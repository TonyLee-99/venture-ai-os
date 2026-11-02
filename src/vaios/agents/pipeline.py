"""The two end-to-end jobs.

`make sourcing-run` (nightly): sourcing -> screening -> evidence -> memo -> receipts gate -> critique -> cards.
`make brief` (weekly): changepoints -> evidence -> brief with receipts.

Offline behaviour: without the warehouse (CI, fresh clone) or under VAIOS_STRICT_REPLAY=1, the evidence
steps are skipped and the committed shortlist, snapshots and facts are used; LLM steps replay from cassettes.
"""

from __future__ import annotations

import json

from vaios.agents import diligence, evidence, sourcing
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
            "incumbent", "crm_stage", "screen_score", "commits_90d", "commit_growth", "top_repo", "domain", "evidence"]
    cands[cols].to_csv(SRC / "candidates.csv", index=False)
    counts = sourcing.source_counts(cands)
    trace.step("source_and_resolve", entities=len(cands), by_source=counts,
               multi_source=int((cands["n_sources"] > 1).sum()))
    short = sourcing.shortlist(cands)
    trace.step("screen", relevant=int(cands["relevant"].sum()),
               relevant_investable=int((cands["relevant"] & cands["investable"]).sum()),
               already_in_crm=int(cands["crm_stage"].notna().sum()), shortlisted=list(short["entity"]))
    rows = []
    for cand in short.to_dict("records"):
        doc_ids = evidence.gather(con, store, cand)
        evidence.save_facts(evidence.facts_sheet(con, cand, len(cands)))
        rows.append({k: cand[k] for k in ("entity", "name", "github_owner", "top_repo", "domain", "facilitator",
                                          "rank", "screen_score", "sources")} | {"doc_ids": doc_ids})
    payload = {"as_of": str(AS_OF), "n_candidates": len(cands), "by_source": counts, "shortlist": rows}
    (SRC / "shortlist.json").write_text(json.dumps(payload, indent=1, default=str) + "\n")
    artifacts.save("candidates", "agentic-payments", {"by_source": counts, "shortlist": [r["entity"] for r in rows],
                                                      "n_candidates": len(cands)},
                   as_of=str(AS_OF), provenance={"run_id": trace.run_id, "job": "sourcing"})
    trace.save("ok", {"candidates": "results/sourcing/candidates.csv", "shortlist": [r["entity"] for r in rows]})
    con.close()
    return rows


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
    summary = summarize(results, failures)
    (SRC / "run_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "memos"}, indent=1))
    print(f"  gateway this run: {gw.session_calls}")
    return summary


def summarize(results: list[dict], failures: list[dict]) -> dict:
    drafted = sum(r["receipts"]["claims_drafted"] for r in results)
    raw_ok = sum(round(r["receipts"]["raw_precision"] * r["receipts"]["claims_drafted"]) for r in results)
    shipped = sum(r["receipts"]["shipped"] for r in results)
    withheld = sum(r["receipts"]["withheld"] for r in results)
    flagged = sum(len(r["critique"]["unsupported_claims"]) for r in results)
    return {
        "as_of": str(AS_OF), "n_memos": len(results), "failed": failures,
        "claims_drafted": drafted, "claims_verified_first_pass": raw_ok,
        "raw_citation_precision": round(raw_ok / drafted, 4) if drafted else None,
        "post_repair_citation_precision": round(shipped / (shipped + withheld), 4) if shipped + withheld else None,
        "claims_shipped": shipped, "claims_withheld": withheld,
        "critic_unsupported_flags": flagged,
        "critic_support_rate": round(1 - flagged / shipped, 4) if shipped else None,
        "memos_with_disagreement": sum(bool(r["disagreements"]) for r in results),
        "recommendation_agreement": sum(r["memo"]["recommendation"] == r["critique"]["recommendation"] for r in results),
        "memos": [{"entity": r["entity"], "name": r["name"], "drafter": r["memo"]["recommendation"],
                   "critic": r["critique"]["recommendation"], **r["receipts"],
                   "scores_drafter": {d: r["memo"]["scores"][d]["score"] for d in ("pmf", "narrative", "execution")},
                   "scores_critic": {d: r["critique"]["scores"][d]["score"] for d in ("pmf", "narrative", "execution")},
                   "disagreements": r["disagreements"]} for r in results],
    }


def brief_run() -> dict:
    from vaios.agents import brief

    return brief.run(Gateway(), DocStore())
