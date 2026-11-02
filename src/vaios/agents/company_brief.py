"""Portfolio-style KPI brief for ONE named comparable company (Daydreams: x402 facilitator + open-source agent
framework). A public comparable, not a portfolio company of any fund. Same receipts rules as the market brief.

KPIs per week (last 12 complete weeks): x402 payments settled, USD volume, peak daily buyers, USD per payment,
share of all x402 payments, commits to daydreamsai/daydreams. Changepoints come from the monitor.
"""

from __future__ import annotations

import json

import pandas as pd

from vaios.agents import schemas, skills
from vaios.agents.runner import Trace
from vaios.config import AS_OF, FROZEN, RESULTS
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway
from vaios.monitoring.run import weekly
from vaios.receipts.verify import check_all, precision

COMPANY, FACILITATOR, REPO = "Daydreams", "daydreams", "daydreamsai/daydreams"
OUT = RESULTS / "briefs" / "company_daydreams"


def kpis() -> pd.DataFrame:
    f = pd.read_parquet(FROZEN / "x402_facilitator_daily.parquet")
    a = pd.read_parquet(FROZEN / "x402_daily.parquet")
    a = a[a["chain"] == "all"]
    g = f[f["facilitator"] == FACILITATOR].set_index("day")[["txs", "volume_usd", "buyers"]].reindex(pd.date_range(a["day"].min(), a["day"].max()),
                                                                    fill_value=0).rename_axis("day").reset_index()
    df = pd.DataFrame({"txs": weekly(g, "txs"), "volume_usd": weekly(g, "volume_usd"),
                       "peak_daily_buyers": weekly(g, "buyers", "max"), "all_x402_txs": weekly(a, "txs")})
    c = pd.read_parquet(FROZEN / "commits_weekly.parquet")
    c = c[c["repo"] == REPO].set_index("week")["commits"]
    df["commits"] = c.reindex(df.index).fillna(0).astype(int)
    df["usd_per_tx"] = (df["volume_usd"] / df["txs"].where(df["txs"] > 0)).round(4)
    df["share_of_x402_txs"] = (df["txs"] / df["all_x402_txs"]).round(4)
    return df.drop(columns="all_x402_txs").tail(12)


def run(gw: Gateway | None = None, store: DocStore | None = None) -> dict:
    gw, store = gw or Gateway(), store or DocStore()
    k = kpis()
    facts = {f"{COMPANY.lower()}.{d:%Y-%m-%d}.{col}": (round(float(v), 4) if pd.notna(v) else None)
             for d, row in k.iterrows() for col, v in row.items()}
    facts = {kk: v for kk, v in facts.items() if v is not None}
    cps = json.loads((RESULTS / "monitoring" / "changepoints.json").read_text())["series"].get(f"facilitator_{FACILITATOR}_txs", {})
    for seg in cps.get("segments", []):
        for col in ("median_before", "median_after", "ratio"):
            facts[f"{COMPANY.lower()}.changepoint.{seg['date']}.{col}"] = seg[col]
    facts_txt = "FACTS (warehouse; weekly KPIs, weeks start Monday):\n" + "\n".join(f"- {kk} = {v}" for kk, v in sorted(facts.items()))
    prompt = (f"Write the weekly KPI brief for {COMPANY} (x402 facilitator and agent framework), week of {AS_OF}. "
              f"Inflections = the changepoints in the facts plus any large week-on-week move in the last 4 weeks. "
              f"Use only metric receipts from the facts; there are no source documents this time.\n\n{facts_txt}\n\n"
              f"Output JSON schema (WeeklyBrief):\n{skills.schema_hint(schemas.WeeklyBrief)}")
    trace = Trace("weekly_brief", f"company_{COMPANY.lower()}", {"facts_keys": sorted(facts)}, as_of=str(AS_OF))
    res = gw.complete("draft", skills.system_prompt("inflection-explainer"), prompt, tag=f"company_brief:{COMPANY}",
                      schema=schemas.WeeklyBrief)
    trace.llm("draft_company_brief", res, prompt)
    b = res.parsed
    claims = [c for n in b["inflections"] for c in n["claims"]]
    checks = {c.claim_id: c for c in check_all(claims, store, facts)}
    for n in b["inflections"]:
        n["withheld"] = [{"id": c["id"], "status": checks[c["id"]].status} for c in n["claims"] if not checks[c["id"]].ok]
        n["claims"] = [c for c in n["claims"] if checks[c["id"]].ok]
        n["needs_human"] = not n["claims"] or n["confidence"] == "low"
    shipped = sum(len(n["claims"]) for n in b["inflections"])
    out = {"company": COMPANY, "week_of": str(AS_OF), "kpis": {f"{d:%Y-%m-%d}": r.to_dict() for d, r in k.iterrows()},
           "brief": b, "receipts": {"claims_drafted": len(claims), "verified_share": round(precision(list(checks.values())), 4),
                                    "shipped": shipped}, "model": f"{res.backend}:{res.model}"}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.with_suffix(".json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    lines = [f"# {COMPANY}: weekly KPI brief, week of {AS_OF}", "",
             "_Public comparable (x402 facilitator + open-source agent framework); portfolio-style monitor. "
             f"Every claim passed the receipts verifier ({shipped} shipped of {len(claims)})._", "",
             "| Week | Payments | USD volume | Peak daily buyers | USD / payment | Share of x402 | Commits |",
             "|---|---|---|---|---|---|---|"]
    lines += [f"| {d:%Y-%m-%d} | {r.txs:,.0f} | {r.volume_usd:,.0f} | {r.peak_daily_buyers:,.0f} | "
              f"{r.usd_per_tx if pd.notna(r.usd_per_tx) else 'n/a'} | {r.share_of_x402_txs:.2%} | {r.commits} |"
              for d, r in k.iterrows()]
    lines += ["", b["summary"], ""]
    for n in b["inflections"]:
        lines += [f"## {n['date']} | {n['headline']}" + (" **[needs human]**" if n["needs_human"] else ""), ""]
        lines += [f"- {c['text']} (`{c.get('metric')}` = {c.get('value')})" for c in n["claims"]] + [""]
    lines += ["## Watchlist", ""] + [f"- {w}" for w in b["watchlist"]]
    OUT.with_suffix(".md").write_text("\n".join(lines) + "\n")
    trace.save("ok", {"brief": "results/briefs/company_daydreams.md"})
    print(json.dumps(out["receipts"]), gw.session_calls)
    return out
