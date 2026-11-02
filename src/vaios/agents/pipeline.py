"""The two end-to-end jobs.

`make sourcing-run` (nightly): sourcing -> screening -> evidence -> memo -> receipts gate -> critique -> cards.
`make brief` (weekly): changepoints -> evidence -> brief with receipts.

Offline behaviour: without the warehouse (CI, fresh clone) or under VAIOS_STRICT_REPLAY=1, the evidence
steps are skipped and the committed shortlist, snapshots and facts are used; LLM steps replay from cassettes.
"""

from __future__ import annotations

import json
import math
import os

from vaios.agents import diligence, evidence, sourcing, stage
from vaios.agents.runner import Trace
from vaios.config import AS_OF, RESULTS, WAREHOUSE
from vaios.dakr import artifacts
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway, strict_replay

SRC = RESULTS / "sourcing"


def _refresh_candidates(store: DocStore) -> list[dict]:
    from vaios.dakr.warehouse import connect

    con = connect()
    trace = Trace("sourcing", "all", {"as_of": str(AS_OF)}, as_of=str(AS_OF))
    cands = sourcing.run(con)
    SRC.mkdir(parents=True, exist_ok=True)
    cols = ["rank", "entity", "name", "github_owner", "sources", "n_sources", "relevance", "relevant", "investable",
            "incumbent", "crm_stage", "screen_score", "logit_github_score", "heuristic_github_score", "commits_90d", "commit_growth", "top_repo", "domain", "evidence"]
    cands[cols].to_csv(SRC / "candidates.csv", index=False)
    counts = sourcing.source_counts(cands)
    trace.step("source_and_resolve", entities=len(cands), by_source=counts,
               multi_source=int((cands["n_sources"] > 1).sum()))
    # stage check (sourced evidence only) on the top-scored relevant candidates; the memo queue is the first 8
    # that are core-niche (relevance >= 4) and seed-eligible
    pool = cands[cands["relevant"] & cands["investable"] & cands["screen_score"].notna() & cands["top_repo"].notna()
                 & cands["new_to_crm"]].head(40)
    rows, checked = [], []
    for cand in pool.to_dict("records"):
        cand = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in cand.items()}  # NaN -> None
        st = stage_of(con, store, cand)
        checked.append({"entity": cand["entity"], "name": cand["name"], "relevance": cand["relevance"],
                        "screen_rank": cand["rank"], **st})
        if not st["seed_eligible"] or cand["relevance"] < sourcing.CORE_RELEVANCE or len(rows) >= 8:
            continue
        cand["stage"] = st
        doc_ids = sorted(set(evidence.gather(con, store, cand)) | set(st["doc_ids"]))
        evidence.save_facts(evidence.facts_sheet(con, cand, len(cands)))
        rows.append({k: cand[k] for k in ("entity", "name", "github_owner", "top_repo", "domain", "facilitator",
                                          "rank", "screen_score", "sources", "stage")} | {"doc_ids": doc_ids})
    chk = {c["entity"]: c for c in checked}
    cands["stage"] = cands["entity"].map(lambda e: chk[e]["stage"] if e in chk else "not checked")
    cands["seed_eligible"] = cands["entity"].map(lambda e: chk[e]["seed_eligible"] if e in chk else None)
    cands[cols + ["stage", "seed_eligible"]].to_csv(SRC / "candidates.csv", index=False)
    (SRC / "stage_checks.json").write_text(json.dumps(checked, indent=1, default=str) + "\n")
    trace.step("screen", relevant=int(cands["relevant"].sum()),
               relevant_investable=int((cands["relevant"] & cands["investable"]).sum()),
               already_in_crm=int(cands["crm_stage"].notna().sum()), stage_checked=len(checked),
               stage_ineligible=[c["entity"] for c in checked if not c["seed_eligible"]],
               shortlisted=[r["entity"] for r in rows])
    payload = {"as_of": str(AS_OF), "n_candidates": len(cands), "by_source": counts, "shortlist": rows}
    (SRC / "shortlist.json").write_text(json.dumps(payload, indent=1, default=str) + "\n")
    artifacts.save("candidates", "agentic-payments", {"by_source": counts, "shortlist": [r["entity"] for r in rows],
                                                      "n_candidates": len(cands)},
                   as_of=str(AS_OF), provenance={"run_id": trace.run_id, "job": "sourcing"})
    trace.save("ok", {"candidates": "results/sourcing/candidates.csv", "shortlist": [r["entity"] for r in rows]})
    con.close()
    return rows


def stage_of(con, store: DocStore, cand: dict) -> dict:
    yc = con.execute("SELECT batch FROM stg_yc WHERE lower(name) = lower(?)", [cand["name"]]).fetchone()
    prior = con.execute("""SELECT r.raise_date::DATE::VARCHAR AS date, r.round, r.amount_musd, r.lead_investors
                           FROM raises r JOIN protocols p USING (slug) WHERE p.github_owner = ?
                           ORDER BY r.raise_date""", [cand.get("github_owner") or ""]).df().to_dict("records")
    site = stage.org_website(cand.get("github_owner"))
    if site:
        cand["domain"] = site  # the company's own homepage beats a repo's homepage link (x402scan.com for Merit)
    sig = stage.gather(store, cand["entity"], [cand.get("domain")])
    tok = stage.token_info(con, cand["name"], cand.get("github_owner"))
    cls = stage.classify(sig, yc[0] if yc else None, tok, prior)
    evidence_lines = sig["quotes"][:3] + [f"DefiLlama: {p['date']} {p['round'] or 'round n/a'} "
                                          f"{'$' + format(p['amount_musd'], 'g') + 'M' if p['amount_musd'] else ''}"
                                          for p in prior]
    if sig["investor_logos"]:
        evidence_lines.append("investor logos on homepage: " + ", ".join(sig["investor_logos"]))
    return {**cls, "yc_batch": yc[0] if yc else None, "token": tok, "prior_raises_defillama": prior,
            "round_evidence": evidence_lines, "doc_ids": sig["doc_ids"]}


def sourcing_run() -> dict:
    store, gw = DocStore(), Gateway()
    shortlist_path = SRC / "shortlist.json"
    reuse = shortlist_path.exists() and json.loads(shortlist_path.read_text())["as_of"] == str(AS_OF)
    if WAREHOUSE.exists() and not strict_replay() and not reuse:
        rows = _refresh_candidates(store)
    else:
        rows = json.loads(shortlist_path.read_text())["shortlist"]
    results, failures = [], []
    for cand in rows:
        try:
            results.append(diligence.run_one(gw, store, cand, cand["doc_ids"]))
            print(f"  memo {cand['entity']}: {results[-1]['receipts']}")
        except Exception as e:  # noqa: BLE001 - recorded in the trace; the run continues
            failures.append({"entity": cand["entity"], "error": f"{type(e).__name__}: {str(e)[:300]}"})
            print(f"  memo {cand['entity']} FAILED: {failures[-1]['error']}")
    diligence.committee(results)
    for out in results:
        diligence.finalize(out, store)
    summary = summarize(results, failures)
    (SRC / "run_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "memos"}, indent=1))
    print(f"  gateway this run: {gw.session_calls}")
    max_failures = int(os.environ.get("VAIOS_MAX_JOB_FAILURES", "0"))
    if len(failures) > max_failures:  # fail closed: a partial overnight run must not look like a success
        raise SystemExit(f"{len(failures)} company job(s) failed (allowed {max_failures}): {failures}")
    return summary


def summarize(results: list[dict], failures: list[dict]) -> dict:
    R = lambda k: sum(r["receipts"][k] for r in results)  # noqa: E731
    drafted, verified = R("claims_drafted"), R("verified")
    raw_ok = sum(round(r["receipts"]["raw_precision"] * r["receipts"]["claims_drafted"]) for r in results)
    labels = {k: sum(r["receipts"]["critic_labels"][k] for r in results)
              for k in ("entails", "partial", "contradicts", "unsupported", "unlabelled")}
    recs = [r["memo"]["recommendation"] for r in results]
    return {
        "as_of": str(AS_OF), "n_memos": len(results), "failed": failures,
        "claims_drafted": drafted, "claims_verified_first_pass": raw_ok,
        "raw_citation_precision": round(raw_ok / drafted, 4) if drafted else None,
        "claims_verified_after_repair": verified,
        "verifier_pass_after_repair_over_drafted": round(verified / drafted, 4) if drafted else None,
        "critic_labels": labels,
        # headline support rate: claims a different model family says are fully entailed by their receipt
        "critic_entailed_over_verified": round(labels["entails"] / verified, 4) if verified else None,
        "critic_entailed_over_drafted": round(labels["entails"] / drafted, 4) if drafted else None,
        "claims_shipped": R("shipped"), "claims_shipped_partial_tagged": R("shipped_partial"),
        "claims_withheld_by_critic": R("withheld_by_critic"), "claims_withheld_by_verifier": R("withheld_by_verifier"),
        "recommendations": {k: recs.count(k) for k in ("advance", "watch", "pass")},
        "first_draft_recommendations": {k: [r["memo"]["draft_recommendation"] for r in results].count(k)
                                        for k in ("advance", "watch", "pass")},
        "critic_recommendations": {k: [r["critique"]["recommendation"] for r in results].count(k)
                                   for k in ("advance", "watch", "pass")},
        "recommendation_agreement": sum(r["memo"]["recommendation"] == r["critique"]["recommendation"] for r in results),
        "memos_with_decision_card": sum(bool(r["disagreements"]) for r in results),
        "human_decisions": "pending: recorded by the owner with `python -m vaios.decide record` (none yet)",
        "memos": [{"entity": r["entity"], "name": r["name"], "committee_rank": r["committee_rank"],
                   "stage": (r.get("stage") or {}).get("stage"), "drafter": r["memo"]["recommendation"],
                   "drafter_first_draft": r["memo"]["draft_recommendation"], "critic": r["critique"]["recommendation"],
                   **{k: v for k, v in r["receipts"].items() if k != "critic_labels"},
                   "scores_drafter": {d: r["memo"]["scores"][d]["score"] for d in ("pmf", "narrative", "execution")},
                   "scores_critic": {d: r["critique"]["scores"][d]["score"] for d in ("pmf", "narrative", "execution")},
                   "disagreements": r["disagreements"]} for r in sorted(results, key=lambda r: r["committee_rank"])],
    }


def brief_run() -> dict:
    from vaios.agents import brief

    return brief.run(Gateway(), DocStore())
