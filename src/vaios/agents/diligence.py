"""AI DD + critic: draft memo (model A) -> verify receipts -> repair round -> cross-family critique (model B)
-> decision card when they disagree. Every step goes through the gateway and is written to the trace.
"""

from __future__ import annotations

import json

from vaios.agents import schemas, skills
from vaios.agents.evidence import load_facts
from vaios.agents.runner import Trace
from vaios.config import RESULTS
from vaios.dakr import artifacts
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway
from vaios.receipts.verify import check_all, precision

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
    reasons = []
    for dim in ("pmf", "narrative", "execution"):
        a, b = memo["scores"][dim]["score"], crit["scores"][dim]["score"]
        if abs(a - b) >= 2:
            reasons.append(f"{dim.upper()} score differs by {abs(a - b)} (drafter {a}, critic {b})")
    if memo["recommendation"] != crit["recommendation"]:
        reasons.append(f"recommendation: drafter '{memo['recommendation']}' vs critic '{crit['recommendation']}'")
    if crit["unsupported_claims"]:
        reasons.append(f"critic flags {len(crit['unsupported_claims'])} claim(s) as unsupported by their quote")
    return reasons


def run_one(gw: Gateway, store: DocStore, cand: dict, doc_ids: list[str]) -> dict:
    entity, name = cand["entity"], cand["name"]
    sheet = load_facts(entity)
    facts = sheet["facts"]
    trace = Trace("diligence_memo", entity, {"doc_ids": doc_ids, "facts_sha": json.dumps(facts, sort_keys=True)},
                  as_of=sheet["as_of"])
    sources, facts_txt = render_sources(store, doc_ids), render_facts(sheet)
    try:
        # 1. draft (model family A)
        prompt = memo_prompt(name, sources, facts_txt)
        res = gw.complete("draft", skills.system_prompt("diligence-memo"), prompt, tag=f"memo:{entity}",
                          schema=schemas.Memo)
        trace.llm("draft_memo", res, prompt, doc_ids)
        memo = res.parsed
        n_drafted = len(memo["claims"])
        checks = check_all(memo["claims"], store, facts)
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
                  f"quote exactly from the source, or use the exact metric value) or drop it. Return JSON: "
                  f"{skills.schema_hint(schemas.ClaimRepair)}")
            rr = gw.complete("draft", skills.system_prompt("receipts"), rp, tag=f"repair:{entity}",
                             schema=schemas.ClaimRepair)
            trace.llm("repair_claims", rr, rp, doc_ids)
            fixed = {c["id"]: c for c in rr.parsed["fixed"]}
            memo["claims"] = [fixed.get(c["id"], c) for c in memo["claims"] if c["id"] not in rr.parsed["dropped"]]
            checks = check_all(memo["claims"], store, facts)
        post_precision = precision(checks)
        shipped = [c for c, chk in zip(memo["claims"], checks, strict=True) if chk.ok]
        unverified = [{"claim": c, "status": chk.status, "detail": chk.detail}
                      for c, chk in zip(memo["claims"], checks, strict=True) if not chk.ok]
        trace.step("gate", raw_precision=raw_precision, post_repair_precision=post_precision,
                   shipped=len(shipped), withheld=len(unverified))
        memo_shipped = {**memo, "claims": shipped}

        # 3. critique (model family B), same evidence, never sees the verifier output
        cp = (f"Company: {name}\n\nSOURCES:\n{sources}\n\n{facts_txt}\n\nDRAFTER MEMO:\n"
              f"{json.dumps(memo_shipped, ensure_ascii=False, indent=1)}\n\nOutput JSON schema (Critique):\n"
              f"{skills.schema_hint(schemas.Critique)}")
        cr = gw.complete("critique", skills.system_prompt("memo-critic"), cp, tag=f"critique:{entity}",
                         schema=schemas.Critique)
        trace.llm("critique", cr, cp, doc_ids)
        crit = cr.parsed
        reasons = disagreement(memo_shipped, crit)
        trace.step("disagreement", reasons=reasons, families=[gw.family("draft"), gw.family("critique")])

        out = {"entity": entity, "name": name, "as_of": sheet["as_of"], "memo": memo_shipped, "unverified": unverified,
               "critique": crit, "disagreements": reasons, "doc_ids": doc_ids, "facts": facts,
               "receipts": {"claims_drafted": n_drafted,
                            "raw_precision": round(raw_precision, 4), "post_repair_precision": round(post_precision, 4),
                            "shipped": len(shipped), "withheld": len(unverified)},
               "models": {"drafter": f"{res.backend}:{res.model}", "critic": f"{cr.backend}:{cr.model}"}}
        write_outputs(out, store, sheet)
        v = artifacts.save("memo", entity, out, as_of=sheet["as_of"],
                           provenance={"run_id": trace.run_id, "job": "diligence_memo", "doc_ids": doc_ids,
                                       "cache_keys": trace.cache_keys, "metrics": sorted(facts)})
        trace.save("ok", {"memo": f"results/memos/{entity}.md", "artifact_version": v["version"],
                          "decision_card": bool(reasons)})
        return out
    except Exception as e:  # one company failing must not stop the overnight run
        trace.save("failed", error=f"{type(e).__name__}: {str(e)[:500]}")
        raise


def write_outputs(out: dict, store: DocStore, sheet: dict) -> None:
    MEMOS.mkdir(parents=True, exist_ok=True)
    (MEMOS / f"{out['entity']}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    (MEMOS / f"{out['entity']}.md").write_text(render_memo_md(out, store))
    if out["disagreements"]:
        CARDS.mkdir(parents=True, exist_ok=True)
        (CARDS / f"{out['entity']}.md").write_text(render_card(out))


def render_memo_md(out: dict, store: DocStore) -> str:
    m, r = out["memo"], out["receipts"]
    lines = [f"# {out['name']}: baseline diligence memo (AI first pass, not a decision)", "",
             f"**{m['one_liner']}**", "", f"Thesis fit: {m['thesis_fit']}", "",
             f"Recommendation (drafter, {out['models']['drafter']}): **{m['recommendation']}**  ",
             f"Critic ({out['models']['critic']}): **{out['critique']['recommendation']}**  ",
             f"Receipts: {r['shipped']} claims shipped, {r['withheld']} withheld by the verifier "
             f"(raw citation precision {r['raw_precision']:.2f}, after repair {r['post_repair_precision']:.2f})", "",
             "| Dimension | Drafter | Critic |", "|---|---|---|"]
    for dim in ("pmf", "narrative", "execution"):
        lines.append(f"| {dim.upper()} | {m['scores'][dim]['score']} | {out['critique']['scores'][dim]['score']} |")
    for sec in ("market", "pmf", "narrative", "execution", "risk"):
        cl = [c for c in m["claims"] if c["section"] == sec]
        if cl:
            lines += ["", f"## {sec.upper() if sec == 'pmf' else sec.title()}"]
            lines += [f"- {c['text']} [^{c['id']}]" for c in cl]
    lines += ["", "## Scores", ""]
    lines += [f"- **{d.upper()} {m['scores'][d]['score']}/5**: {m['scores'][d]['rationale']}" for d in
              ("pmf", "narrative", "execution")]
    lines += ["", "## Risks", ""] + [f"- {x}" for x in m["risks"]]
    lines += ["", "## Questions for the founder call", ""] + [f"- {x}" for x in m["open_questions"]]
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
    lines = [f"# Decision card: {out['name']}", "", "The two agents disagree. A human decides; log the decision in "
             "`ledger/human_feedback.jsonl` (schema: `vaios.agents.schemas.HumanDecision`).", "",
             "## Where they disagree", ""] + [f"- {r}" for r in out["disagreements"]]
    lines += ["", "| | Drafter | Critic |", "|---|---|---|",
              f"| Model | {out['models']['drafter']} | {out['models']['critic']} |",
              f"| Recommendation | {m['recommendation']} | {c['recommendation']} |"]
    for dim in ("pmf", "narrative", "execution"):
        lines.append(f"| {dim.upper()} | {m['scores'][dim]['score']} | {c['scores'][dim]['score']} |")
    lines += ["", "## Critic's strongest counterargument", "", c["strongest_counterargument"]]
    if c["unsupported_claims"]:
        lines += ["", "## Claims the critic says the quote does not support", ""]
        lines += [f"- `{u['claim_id']}`: {u['reason']}" for u in c["unsupported_claims"]]
    if c["missing_risks"]:
        lines += ["", "## Risks the critic says are missing", ""] + [f"- {x}" for x in c["missing_risks"]]
    lines += ["", "## Decision", "", "- [ ] advance  - [ ] watch  - [ ] pass   reviewer: ____   reason: ____"]
    return "\n".join(lines) + "\n"
