"""Weekly post-investment brief: explain recent inflections in comparables' traction, with receipts."""

from __future__ import annotations

import json
import math

import pandas as pd

from vaios.agents import schemas, skills
from vaios.agents.evidence import FETCHED
from vaios.agents.runner import Trace
from vaios.config import AS_OF, FROZEN, RESULTS
from vaios.dakr import artifacts
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway
from vaios.monitoring import events as ev_mod
from vaios.receipts.verify import check_all, precision

BRIEFS = RESULTS / "briefs"
LOOKBACK_WEEKS = 10
WINDOW_DAYS = 14
MAX_INFLECTIONS = 8


def recent_inflections(cps: dict) -> list[dict]:
    cutoff = pd.Timestamp(AS_OF) - pd.Timedelta(weeks=LOOKBACK_WEEKS)
    rows = []
    for series, r in cps["series"].items():
        for seg in r["segments"]:
            if pd.Timestamp(seg["date"]) >= cutoff and seg["ratio"]:
                rows.append({"series": series, **seg})
    # largest relative moves first (|log ratio|), then date
    rows.sort(key=lambda x: (-abs(math.log(x["ratio"])), x["date"]))
    return sorted(rows[:MAX_INFLECTIONS], key=lambda x: (x["date"], x["series"]))


def hn_docs_near(store: DocStore, day: pd.Timestamp) -> list[str]:
    hn = pd.read_parquet(FROZEN / "hn_stories.parquet").drop_duplicates("objectID")
    near = hn[(hn["created_at"] - day).abs() <= pd.Timedelta(days=WINDOW_DAYS)]
    near = near[near["title"].str.contains("x402|agent", case=False)].nlargest(5, "points")
    ids = []
    for r in near.itertuples():
        text = (f"Hacker News story (HN Algolia API, fetched {FETCHED})\nTitle: {r.title}\n"
                f"Posted: {r.created_at:%Y-%m-%d}\nPoints: {r.points}\nLink: {r.url}\n"
                f"Discussion: https://news.ycombinator.com/item?id={r.objectID}")
        ids.append(store.put(text, entity="x402-events", kind="hn", fetched_at=FETCHED, title=r.title,
                             url=f"https://news.ycombinator.com/item?id={r.objectID}"))
    return ids


def run(gw: Gateway, store: DocStore) -> dict:
    cps = json.loads((RESULTS / "monitoring" / "changepoints.json").read_text())
    ev = ev_mod.load()
    infl = recent_inflections(cps)
    facts, doc_ids, blocks = {}, set(), []
    for i, x in enumerate(infl):
        key = f"{x['series']}.{x['date']}"
        facts |= {f"{key}.median_before": x["median_before"], f"{key}.median_after": x["median_after"],
                  f"{key}.ratio": x["ratio"]}
        day = pd.Timestamp(x["date"])
        near_ev = ev[(ev["date"] - day).abs() <= pd.Timedelta(days=WINDOW_DAYS)]
        ids = sorted(set(near_ev["doc_id"]) | set(hn_docs_near(store, day)))
        doc_ids |= set(ids)
        blocks.append(f"Inflection {i + 1}: series={x['series']} week_of={x['date']} direction={x['direction']} "
                      f"(weekly median {x['median_before']} -> {x['median_after']}, ratio {x['ratio']}); "
                      f"evidence doc_ids: {ids or 'none'}")
    doc_ids = sorted(doc_ids)
    sources = "\n\n".join(f"<source doc_id=\"{d}\" kind=\"{store.meta(d).kind}\" url=\"{store.meta(d).url}\">\n"
                          f"{store.get(d)}\n</source>" for d in doc_ids)
    facts_txt = "FACTS (warehouse, weekly series from x402scan):\n" + "\n".join(
        f"- {k} = {v}" for k, v in sorted(facts.items()))
    week = str(AS_OF)
    prompt = (f"Week of {week}. Detected inflections in the last {LOOKBACK_WEEKS} weeks:\n" + "\n".join(blocks) +
              f"\n\nSOURCES:\n{sources}\n\n{facts_txt}\n\nOutput JSON schema (WeeklyBrief):\n"
              f"{skills.schema_hint(schemas.WeeklyBrief)}")
    trace = Trace("weekly_brief", f"week_{week}", {"inflections": infl, "doc_ids": doc_ids}, as_of=week)
    res = gw.complete("draft", skills.system_prompt("inflection-explainer"), prompt, tag=f"brief:{week}",
                      schema=schemas.WeeklyBrief)
    trace.llm("draft_brief", res, prompt, doc_ids)
    brief = res.parsed
    all_claims = [c for n in brief["inflections"] for c in n["claims"]]
    n_drafted = len(all_claims)
    checks = {c.claim_id: c for c in check_all(all_claims, store, facts)}
    raw = precision(list(checks.values()))
    failing = [c for c in all_claims if not checks[c["id"]].ok]
    if failing:  # same repair round as memos: fix the receipt or drop the claim
        items = [{"claim": c, "verifier": f"{checks[c['id']].status}: {checks[c['id']].detail}"} for c in failing]
        rp = (f"{prompt}\n\nThe receipts verifier rejected these claims of your brief:\n"
              f"{json.dumps(items, ensure_ascii=False, indent=1)}\n\nFor each, either fix the receipt (copy the quote "
              f"exactly, or cite the exact metric value) or drop it. Return JSON: "
              f"{skills.schema_hint(schemas.ClaimRepair)}")
        rr = gw.complete("draft", skills.system_prompt("receipts"), rp, tag=f"brief-repair:{week}",
                         schema=schemas.ClaimRepair)
        trace.llm("repair_claims", rr, rp, doc_ids)
        fixed = {c["id"]: c for c in rr.parsed["fixed"]}
        for note in brief["inflections"]:
            note["claims"] = [fixed.get(c["id"], c) for c in note["claims"] if c["id"] not in rr.parsed["dropped"]]
        all_claims = [c for n in brief["inflections"] for c in n["claims"]]
        checks = {c.claim_id: c for c in check_all(all_claims, store, facts)}
    for note in brief["inflections"]:
        kept = [c for c in note["claims"] if checks[c["id"]].ok]
        note["withheld"] = [{"id": c["id"], "status": checks[c["id"]].status} for c in note["claims"]
                            if not checks[c["id"]].ok]
        note["claims"] = kept
        note["needs_human"] = not kept or note["confidence"] == "low"
    shipped = sum(len(n["claims"]) for n in brief["inflections"])
    receipts = {"claims_drafted": n_drafted, "raw_precision": round(raw, 4),
                "post_repair_precision": round(shipped / len(all_claims), 4) if all_claims else None,
                "shipped": shipped, "withheld": len(all_claims) - shipped, "dropped": n_drafted - len(all_claims)}
    trace.step("verify_receipts", **receipts)
    out = {"week_of": week, "brief": brief, "receipts": receipts, "facts": facts, "doc_ids": doc_ids,
           "model": f"{res.backend}:{res.model}"}
    BRIEFS.mkdir(parents=True, exist_ok=True)
    (BRIEFS / f"{week}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    (BRIEFS / f"{week}.md").write_text(render(out, store))
    artifacts.save("brief", week, out, as_of=week, provenance={"run_id": trace.run_id, "job": "weekly_brief",
                                                               "doc_ids": doc_ids, "cache_keys": trace.cache_keys})
    trace.save("ok", {"brief": f"results/briefs/{week}.md"})
    print(json.dumps(receipts), f"gateway: {gw.session_calls}")
    return out


def render(out: dict, store: DocStore) -> str:
    b = out["brief"]
    lines = [f"# Weekly monitoring brief, week of {out['week_of']}", "",
             f"_Comparable companies in agentic payments (x402). AI draft ({out['model']}); every claim below passed "
             f"the receipts verifier ({out['receipts']['shipped']} shipped, {out['receipts']['withheld']} withheld)._",
             "", b["summary"], ""]
    for n in b["inflections"]:
        flag = " **[needs human]**" if n["needs_human"] else ""
        lines += [f"## {n['date']} | {n['series']} | {n['headline']}{flag}", f"Confidence: {n['confidence']}", ""]
        lines += [f"- {c['text']} [^{c['id']}]" for c in n["claims"]]
        lines.append("")
    lines += ["## Watchlist", ""] + [f"- {w}" for w in b["watchlist"]] + ["", "## Receipts", ""]
    for n in b["inflections"]:
        for c in n["claims"]:
            if c.get("doc_id"):
                m = store.meta(c["doc_id"])
                lines.append(f"[^{c['id']}]: \"{c['quote']}\" ({m.kind}, {m.url}, snapshot `{c['doc_id']}`)")
            else:
                lines.append(f"[^{c['id']}]: warehouse metric `{c['metric']}` = {c['value']}")
    return "\n".join(lines) + "\n"
