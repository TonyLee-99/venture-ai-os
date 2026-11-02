"""AI DD + critic: draft memo (model A) -> verify receipts -> repair round -> cross-family critique (model B)
-> decision card when they disagree. Every step goes through the gateway and is written to the trace.
"""

from __future__ import annotations

import json
import re

from vaios.agents import schemas, skills
from vaios.agents.evidence import load_facts
from vaios.agents.runner import Trace
from vaios.config import RESULTS
from vaios.dakr import artifacts
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway
from vaios.receipts.verify import _matches, check_all, numbers_in, precision, written_numbers

MEMOS = RESULTS / "memos"
CARDS = RESULTS / "decision_cards"
MAX_DOC_CHARS = 9000  # snapshots are stored at most this long, so the verifier sees exactly what the model saw


def render_sources(store: DocStore, doc_ids: list[str]) -> str:
    parts = []
    for d in doc_ids:
        m = store.meta(d)
        parts.append(f"<source doc_id=\"{d}\" kind=\"{m.kind}\" url=\"{m.url}\" fetched=\"{m.fetched_at}\">\n"
                     f"{store.get(d)[:MAX_DOC_CHARS]}\n</source>")
    return "\n\n".join(parts)


def render_facts(sheet: dict) -> str:
    lines = [f"FACTS (warehouse, as of {sheet['as_of']}):"]
    for k, v in sorted(sheet["facts"].items()):
        lines.append(f"- {k} = {v}" + (f"   ({sheet['descriptions'][k]})" if k in sheet["descriptions"] else ""))
    return "\n".join(lines)


def memo_prompt(name: str, sources: str, facts: str) -> str:
    return (f"Company: {name}\n\nSOURCES:\n{sources}\n\n{facts}\n\n"
            f"Output JSON schema (Memo):\n{skills.schema_hint(schemas.Memo)}")


def disagreement(memo: dict, crit: dict) -> list[str]:
    """A decision card fires only on a different recommendation or a score gap of 2+ points (not on any flag)."""
    reasons = []
    for dim in ("pmf", "narrative", "execution"):
        a, b = memo["scores"][dim]["score"], crit["scores"][dim]["score"]
        if abs(a - b) >= 2:
            reasons.append(f"{dim.upper()} score differs by {abs(a - b)} (drafter {a}, critic {b})")
    if memo["recommendation"] != crit["recommendation"]:
        reasons.append(f"recommendation: drafter '{memo['recommendation']}' vs critic '{crit['recommendation']}'")
    return reasons


def stage_header(cand: dict) -> str:
    st = cand.get("stage") or {}
    tok = st.get("token")
    lines = ["STAGE (sourced evidence only; 'unknown' means none found):",
             f"- stage: {st.get('stage', 'unknown')}",
             f"- last known round: {'; '.join(st.get('round_evidence') or []) or 'unknown'}",
             f"- token: {tok['ticker'] + ' (FDV $' + format((tok.get('fdv_usd') or 0) / 1e6, ',.1f') + 'M)' if tok else 'none found'}",
             f"- YC batch: {st.get('yc_batch') or 'none'}"]
    return "\n".join(lines)


def reconcile(claims: list[dict], labels: list[dict]) -> tuple[list[dict], list[dict], dict]:
    """entails -> ship; partial -> ship with a visible tag; contradicts/unsupported -> withhold.
    A claim the critic did not label fails closed: withheld, never shipped unreviewed."""
    by_id = {x["claim_id"]: x for x in labels}
    shipped, withheld, counts = [], [], {"entails": 0, "partial": 0, "contradicts": 0, "unsupported": 0,
                                         "unlabelled": 0}
    for c in claims:
        lab = by_id.get(c["id"])
        kind = lab["label"] if lab else "unlabelled"
        counts[kind] += 1
        if kind in ("contradicts", "unsupported", "unlabelled"):
            withheld.append({"claim": c, "critic_label": kind,
                             "reason": lab["reason"] if lab else "no critic label: withheld (fail closed)"})
        else:
            shipped.append({**c, "support": kind, "support_note": lab["reason"] if lab else "critic gave no label"})
    return shipped, withheld, counts


def run_one(gw: Gateway, store: DocStore, cand: dict, doc_ids: list[str]) -> dict:
    """Draft -> receipts gate (+1 repair) -> blind critique with per-claim entailment -> reconcile -> rescore.
    The committee step (advance budget) and the writing of outputs happen in `finalize`."""
    entity, name = cand["entity"], cand["name"]
    sheet = load_facts(entity)
    facts = sheet["facts"]
    trace = Trace("diligence_memo", entity, {"doc_ids": doc_ids, "facts_sha": json.dumps(facts, sort_keys=True),
                                             "stage": cand.get("stage")}, as_of=sheet["as_of"])
    sources, facts_txt = render_sources(store, doc_ids), render_facts(sheet)
    header = stage_header(cand)
    try:
        # 1. draft (model family A)
        prompt = (f"Company: {name}\n\n{header}\n\nSOURCES:\n{sources}\n\n{facts_txt}\n\n"
                  f"Output JSON schema (Memo):\n{skills.schema_hint(schemas.Memo)}")
        res = gw.complete("draft", skills.system_prompt("diligence-memo"), prompt, tag=f"memo:{entity}",
                          schema=schemas.Memo)
        trace.llm("draft_memo", res, prompt, doc_ids)
        memo = res.parsed
        draft_scores, draft_rec = memo["scores"], memo["recommendation"]
        n_drafted = len(memo["claims"])
        checks = check_all(memo["claims"], store, facts, sheet["descriptions"])
        raw_precision = precision(checks)
        trace.step("verify_receipts", n_claims=len(checks), verified=sum(c.ok for c in checks),
                   failures={c.claim_id: c.status for c in checks if not c.ok})

        # 2. repair round: show the drafter only its failing claims and the verifier's reason
        failing = [c for c in checks if not c.ok]
        if failing:
            bad = {c.claim_id: c for c in failing}
            items = [{"claim": cl, "verifier": f"{bad[cl['id']].status}: {bad[cl['id']].detail}"}
                     for cl in memo["claims"] if cl["id"] in bad]
            rp = (f"{prompt}\n\nThe receipts verifier rejected these claims of your memo:\n"
                  f"{json.dumps(items, ensure_ascii=False, indent=1)}\n\nFor each, either fix the receipt (copy the "
                  f"quote exactly from the source, or use the exact metric value and state it) or drop it. Return "
                  f"JSON: {skills.schema_hint(schemas.ClaimRepair)}")
            rr = gw.complete("draft", skills.system_prompt("receipts"), rp, tag=f"repair:{entity}",
                             schema=schemas.ClaimRepair)
            trace.llm("repair_claims", rr, rp, doc_ids)
            fixed = {c["id"]: c for c in rr.parsed["fixed"]}
            memo["claims"] = [fixed.get(c["id"], c) for c in memo["claims"] if c["id"] not in rr.parsed["dropped"]]
            checks = check_all(memo["claims"], store, facts, sheet["descriptions"])
        verified = [c for c, chk in zip(memo["claims"], checks, strict=True) if chk.ok]
        unverified = [{"claim": c, "status": chk.status, "detail": chk.detail}
                      for c, chk in zip(memo["claims"], checks, strict=True) if not chk.ok]
        trace.step("verifier_gate", raw_precision=raw_precision, verified=len(verified), withheld=len(unverified))

        # 3. blind critique (model family B): claims + one-liner only, no drafter scores/recommendation
        blind = {"company": name, "one_liner": memo["one_liner"],
                 "claims": [{k: c[k] for k in ("id", "section", "text", "doc_id", "quote", "metric", "value")}
                            for c in verified]}
        cp = (f"Company: {name}\n\n{header}\n\nSOURCES:\n{sources}\n\n{facts_txt}\n\nDRAFTER CLAIMS:\n"
              f"{json.dumps(blind, ensure_ascii=False, indent=1)}\n\nOutput JSON schema (Critique):\n"
              f"{skills.schema_hint(schemas.Critique)}")
        cr = gw.complete("critique", skills.system_prompt("memo-critic"), cp, tag=f"critique:{entity}",
                         schema=schemas.Critique)
        trace.llm("critique", cr, cp, doc_ids)
        crit = cr.parsed
        shipped, withheld_by_critic, label_counts = reconcile(verified, crit["claim_labels"])
        trace.step("reconcile", **label_counts)

        # 4. rescore: the drafter sees which claims survived and re-decides (dependent recommendations)
        rs_prompt = (f"Company: {name}\n\n{header}\n\nYour first-draft scores and recommendation were:\n"
                     f"{json.dumps({'scores': draft_scores, 'recommendation': draft_rec}, ensure_ascii=False)}\n\n"
                     f"After an independent support review, these claims remain (support = entails or partial):\n"
                     f"{json.dumps([{k: c[k] for k in ('id', 'section', 'text', 'support')} for c in shipped], ensure_ascii=False, indent=1)}\n\n"
                     f"These were withheld as not supported by their receipts:\n"
                     f"{json.dumps([{'id': w['claim']['id'], 'text': w['claim']['text'], 'why': w['reason']} for w in withheld_by_critic], ensure_ascii=False, indent=1)}\n\n"
                     f"Re-score PMF / Narrative / Execution using only the remaining evidence (partial claims count "
                     f"as weak evidence) and give a recommendation under the same rules. Return JSON: "
                     f"{skills.schema_hint(schemas.Rescore)}")
        rr2 = gw.complete("draft", skills.system_prompt("diligence-memo"), rs_prompt, tag=f"rescore:{entity}",
                          schema=schemas.Rescore)
        trace.llm("rescore", rr2, rs_prompt, doc_ids)
        final = {**memo, "claims": shipped, "scores": rr2.parsed["scores"],
                 "recommendation": rr2.parsed["recommendation"], "rescore_note": rr2.parsed["change_note"],
                 "draft_scores": draft_scores, "draft_recommendation": draft_rec}
        n_ver = len(verified)
        out = {"entity": entity, "name": name, "as_of": sheet["as_of"], "stage": cand.get("stage"),
               "triage": {"rank": cand.get("rank"), "screen_score": cand.get("screen_score"),
                          "note": "triage signal only, not evidence (near chance on never-raised protocols)"},
               "memo": final, "unverified": unverified, "withheld_by_critic": withheld_by_critic,
               "critique": crit, "doc_ids": doc_ids, "facts": facts,
               "receipts": {"claims_drafted": n_drafted, "raw_precision": round(raw_precision, 4),
                            "verified": n_ver, "withheld_by_verifier": len(unverified),
                            "dropped_in_repair": n_drafted - len(memo["claims"]),
                            "critic_labels": label_counts,
                            "critic_entailed_share": round(label_counts["entails"] / n_ver, 4) if n_ver else None,
                            "shipped": len(shipped), "shipped_partial": label_counts["partial"],
                            "withheld_by_critic": len(withheld_by_critic)},
               "models": {"drafter": f"{res.backend}:{res.model}", "critic": f"{cr.backend}:{cr.model}"},
               "_trace": trace}
        return out
    except Exception as e:  # one company failing must not stop the overnight run
        trace.save("failed", error=f"{type(e).__name__}: {str(e)[:500]}")
        raise


ADVANCE_BUDGET = 2  # at most 2 of 8 memos may recommend "advance": forces a ranking, like a partner meeting


EVIDENCE_MIN_ENTAILED = 0.25  # below this share of fully entailed claims the memo is "evidence insufficient"


def policy(scores: dict, rec: str | None = None) -> str:
    """The written policy (skills/diligence-memo): the call is a function of the three scores ONLY.
    total >= 11 and every dimension >= 3 -> advance; total <= 7 or any dimension = 1 -> pass; else watch.
    `rec` (the model's own stated call) is ignored on purpose: same scores, same call."""
    total = sum(scores[d]["score"] for d in ("pmf", "narrative", "execution"))
    low = min(scores[d]["score"] for d in ("pmf", "narrative", "execution"))
    if total <= 7 or low == 1:
        return "pass"
    if total >= 11 and low >= 3:
        return "advance"
    return "watch"


def committee(outs: list[dict]) -> None:
    """Score policy for drafter AND critic, evidence gate, then the advance budget. Tie-break for the budget:
    higher drafter+critic total first, then higher share of entailed claims, then entity name."""
    tot = lambda o, k: sum(o[k]["scores"][d]["score"] for d in ("pmf", "narrative", "execution"))  # noqa: E731
    for o in outs:
        m, c = o["memo"], o["critique"]
        m["recommendation_stated_by_model"] = m["recommendation"]
        m["recommendation"] = policy(m["scores"])
        c["recommendation_stated_by_model"] = c["recommendation"]
        c["recommendation"] = policy(c["scores"])  # resolves stated-verdict vs score conflicts the same way
        c["stated_vs_policy_conflict"] = c["recommendation"] != c["recommendation_stated_by_model"]
        share = o["receipts"]["critic_entailed_share"] or 0.0
        m["evidence_status"] = "sufficient" if share >= EVIDENCE_MIN_ENTAILED else "evidence insufficient"
        if m["evidence_status"] != "sufficient" and m["recommendation"] == "advance":
            m["recommendation"] = "watch"
            m["committee_note"] = "advance blocked: evidence insufficient"
    ranked = sorted(outs, key=lambda o: (-(tot(o, "memo") + tot(o, "critique")),
                                         -(o["receipts"]["critic_entailed_share"] or 0), o["entity"]))
    kept = 0
    for i, o in enumerate(ranked, 1):
        o["committee_rank"] = i
        if o["memo"]["recommendation"] == "advance":
            kept += 1
            if kept > ADVANCE_BUDGET:
                o["memo"]["recommendation"] = "watch"
                o["memo"]["committee_note"] = f"downgraded: advance budget of {ADVANCE_BUDGET} already used"
    for o in outs:
        o["disagreements"] = disagreement(o["memo"], o["critique"])
        scrub_free_text(o)


def scrub_free_text(o: dict) -> None:
    """Free text (one-liner, thesis, risks, founder questions, score rationales) carries no receipt, so any
    number in it must equal a number in a shipped claim or the facts sheet; otherwise the item is removed (lists)
    or the sentence is removed (prose). References to withheld claim ids are removed from rationales."""
    m = o["memo"]
    allowed = [n for c in m["claims"] for n in numbers_in(c["text"] + " " + (c.get("quote") or ""))]
    allowed += [float(v) for v in o["facts"].values() if isinstance(v, int | float)]
    withheld_ids = {w["claim"]["id"] for w in o["withheld_by_critic"]}
    removed = []

    def ok(text: str) -> bool:  # same precision rule as the verifier: "56.6 million" covers 56,580,000
        return all(any(_matches(w, a) for a in allowed) for w in written_numbers(text))

    def clean_prose(text: str) -> str:
        keep = []
        for sent in re.split(r"(?<=[.!?])\s+", text):
            if ok(sent):
                keep.append(sent)
            else:
                removed.append(sent)
        return " ".join(keep)

    for key in ("risks", "open_questions"):
        kept = [x for x in m[key] if ok(x)]
        removed += [x for x in m[key] if not ok(x)]
        m[key] = kept
    for key in ("one_liner", "thesis_fit", "rescore_note"):
        if m.get(key):
            m[key] = clean_prose(m[key])
    for d in ("pmf", "narrative", "execution"):
        r = m["scores"][d]["rationale"]
        for cid in withheld_ids:
            r = r.replace(f"[{cid}]", "")
        m["scores"][d]["rationale"] = clean_prose(r)
    m["free_text_removed"] = removed


def finalize(out: dict, store: DocStore) -> None:
    trace = out.pop("_trace")
    sheet = load_facts(out["entity"])
    write_outputs(out, store, sheet)
    v = artifacts.save("memo", out["entity"], out, as_of=sheet["as_of"],
                       provenance={"run_id": trace.run_id, "job": "diligence_memo", "doc_ids": out["doc_ids"],
                                   "cache_keys": trace.cache_keys, "metrics": sorted(out["facts"])})
    trace.step("committee", rank=out["committee_rank"], recommendation=out["memo"]["recommendation"],
               disagreements=out["disagreements"])
    trace.save("ok", {"memo": f"results/memos/{out['entity']}.md", "artifact_version": v["version"],
                      "decision_card": bool(out["disagreements"])})


def write_outputs(out: dict, store: DocStore, sheet: dict) -> None:
    MEMOS.mkdir(parents=True, exist_ok=True)
    (MEMOS / f"{out['entity']}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    (MEMOS / f"{out['entity']}.md").write_text(render_memo_md(out, store))
    if out["disagreements"]:
        CARDS.mkdir(parents=True, exist_ok=True)
        (CARDS / f"{out['entity']}.md").write_text(render_card(out))


SECTIONS = ("team", "why_now", "market", "competition", "pmf", "narrative", "execution", "inflection", "risk")


def render_memo_md(out: dict, store: DocStore) -> str:
    m, r, st = out["memo"], out["receipts"], out.get("stage") or {}
    tok = st.get("token")
    lines = [f"# {out['name']}: baseline diligence memo (AI first pass, not a decision)", "",
             "| Stage | Last known round | Token | YC batch | Triage rank |", "|---|---|---|---|---|",
             f"| {st.get('stage', 'unknown')} | {'; '.join(st.get('round_evidence') or []) or 'unknown'} | "
             f"{tok['ticker'] + ' (FDV $' + format((tok.get('fdv_usd') or 0) / 1e6, ',.1f') + 'M)' if tok else 'none found'} | "
             f"{st.get('yc_batch') or 'none'} | {out['triage']['rank']} (triage only, not evidence) |", "",
             f"**{m['one_liner']}**", "", f"Thesis fit: {m['thesis_fit']}", "",
             f"Recommendation (score policy + committee): **{m['recommendation']}**; evidence status: "
             f"**{m.get('evidence_status', 'n/a')}** (first draft: {m['draft_recommendation']}; critic by policy: "
             f"{out['critique']['recommendation']}, critic stated: {out['critique'].get('recommendation_stated_by_model')})  ",
             f"Receipts: {r['claims_drafted']} claims drafted, {r['raw_precision']:.0%} passed the verifier on the "
             f"first pass, {r['verified']} verified after one repair; the critic labelled {r['critic_labels']['entails']} "
             f"as entailed, {r['shipped_partial']} as partial (tagged below) and withheld {r['withheld_by_critic']}.", "",
             "| Dimension | Drafter (final) | Drafter (first draft) | Critic |", "|---|---|---|---|"]
    for dim in ("pmf", "narrative", "execution"):
        lines.append(f"| {dim.upper()} | {m['scores'][dim]['score']} | {m['draft_scores'][dim]['score']} | "
                     f"{out['critique']['scores'][dim]['score']} |")
    for sec in SECTIONS:
        cl = [c for c in m["claims"] if c["section"] == sec]
        if cl:
            lines += ["", f"## {sec.replace('_', ' ').upper() if sec == 'pmf' else sec.replace('_', ' ').title()}"]
            lines += [f"- {c['text']} [^{c['id']}]" + (f" _(partial support: {c['support_note']})_"
                                                       if c.get("support") != "entails" else "") for c in cl]
    lines += ["", "## Scores (final, after the support review)", ""]
    lines += [f"- **{d.upper()} {m['scores'][d]['score']}/5**: {m['scores'][d]['rationale']}" for d in
              ("pmf", "narrative", "execution")]
    if m.get("rescore_note"):
        lines += ["", f"Re-score note: {m['rescore_note']}"]
    if m.get("committee_note"):
        lines += ["", f"Committee: {m['committee_note']}"]
    lines += ["", "## Risks", ""] + [f"- {x}" for x in m["risks"]]
    lines += ["", "## Questions for the founder call", ""] + [f"- {x}" for x in m["open_questions"]]
    if m.get("free_text_removed"):
        lines += ["", f"_{len(m['free_text_removed'])} free-text item(s) removed because they stated a number that no "
                  "shipped claim or warehouse fact supports._"]
    if out["withheld_by_critic"]:
        lines += ["", "## Withheld: real quote, but the critic says it does not support the claim", ""]
        lines += [f"- ~~{w['claim']['text']}~~ ({w['critic_label']}: {w['reason']})" for w in out["withheld_by_critic"]]
    lines += ["", "## Receipts", ""]
    for c in m["claims"]:
        if c.get("doc_id"):
            meta = store.meta(c["doc_id"])
            lines.append(f"[^{c['id']}]: \"{c['quote']}\" ({meta.kind}, {meta.url}, snapshot `{c['doc_id']}`, "
                         f"fetched {meta.fetched_at})")
        else:
            lines.append(f"[^{c['id']}]: warehouse metric `{c['metric']}` = {c['value']} (as of {out['as_of']})")
    return "\n".join(lines) + "\n"


def render_card(out: dict) -> str:
    m, c = out["memo"], out["critique"]
    lines = [f"# Decision card: {out['name']}", "",
             "The two agents disagree on the recommendation or by 2+ points on a dimension. A human decides and "
             f"records it with `uv run python -m vaios.decide record {out['entity']} --verdict <advance|watch|pass> "
             "--reason \"...\" --reviewer <name>` (appends to `ledger/human_feedback.jsonl`).", "",
             "## Where they disagree", ""] + [f"- {r}" for r in out["disagreements"]]
    lines += ["", "| | Drafter (final) | Critic |", "|---|---|---|",
              f"| Model | {out['models']['drafter']} | {out['models']['critic']} |",
              f"| Recommendation | {m['recommendation']} | {c['recommendation']} |"]
    for dim in ("pmf", "narrative", "execution"):
        lines.append(f"| {dim.upper()} | {m['scores'][dim]['score']} | {c['scores'][dim]['score']} |")
    lines += ["", "## Critic's strongest counterargument", "", c["strongest_counterargument"]]
    if out["withheld_by_critic"]:
        lines += ["", "## Claims withheld by the critic", ""]
        lines += [f"- `{w['claim']['id']}` {w['critic_label']}: {w['reason']}" for w in out["withheld_by_critic"]]
    if c["missing_risks"]:
        lines += ["", "## Risks the critic says are missing", ""] + [f"- {x}" for x in c["missing_risks"]]
    lines += ["", "## Human decision", "", "Pending: not yet recorded by the owner."]
    return "\n".join(lines) + "\n"
