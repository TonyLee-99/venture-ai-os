"""F09: the receipts verifier accepts true spans, rejects corruptions, and every shipped memo claim verifies."""

import json

import pytest

from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.receipts import evaluate as verifier_eval
from vaios.receipts.verify import check_claim

STORE = DocStore()
MEMOS = sorted((RESULTS / "memos").glob("*.json"))


@pytest.mark.skipif(len(STORE.index) < 5, reason="needs committed snapshots")
def test_verifier_catches_corruptions_and_accepts_gold():
    committed = json.loads((RESULTS / "receipts" / "verifier_eval.json").read_text())
    assert verifier_eval.run() == committed  # the committed numbers recompute exactly
    gold, corrupt = verifier_eval.gold_and_corrupt()
    facts = {"m": 120.0}
    false_rejects = [g for g in gold if not check_claim(g, STORE, facts).ok]
    caught = [c for c in corrupt if not check_claim(c["claim"], STORE, facts).ok]
    assert len(gold) >= 50 and len(corrupt) >= 50
    assert not false_rejects, false_rejects[:3]
    assert len(caught) / len(corrupt) >= 0.95, [c["kind"] for c in corrupt if c not in caught][:10]


def test_number_rules():
    facts = {"gh.commits_90d": 556}
    ok = {"id": "a", "text": "556 commits in 90 days", "metric": "gh.commits_90d", "value": 556}
    bad = {"id": "b", "text": "5,560 commits in 90 days", "metric": "gh.commits_90d", "value": 556}
    assert check_claim(ok, STORE, facts).ok
    assert check_claim(bad, STORE, facts).status == "number_unsupported"


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_every_shipped_memo_claim_verifies_offline():
    for path in MEMOS:
        out = json.loads(path.read_text())
        desc = json.loads((RESULTS / "facts" / f"{out['entity']}.json").read_text())["descriptions"]
        for c in out["memo"]["claims"]:
            chk = check_claim(c, STORE, out["facts"], desc)
            assert chk.ok, (path.name, c["id"], chk.status, chk.detail)


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_run_summary_matches_memos():
    s = json.loads((RESULTS / "sourcing" / "run_summary.json").read_text())
    outs = [json.loads(p.read_text()) for p in MEMOS]
    assert s["n_memos"] == len(outs)
    assert s["claims_shipped"] == sum(len(o["memo"]["claims"]) for o in outs)
    assert s["claims_withheld_by_critic"] == sum(len(o["withheld_by_critic"]) for o in outs)
    assert s["critic_labels"]["entails"] == sum(c.get("support") == "entails" for o in outs for c in o["memo"]["claims"])


def test_claim_eval_reports_recall_by_type():
    ce = json.loads((RESULTS / "receipts" / "claim_eval.json").read_text())
    assert ce["n_original_pairs"] >= 30
    for k, v in ce["recall_by_perturbation"].items():
        assert v["either_recall"] >= max(v["verifier_recall"], v["critic_recall"]), k
    assert ce["precision"].startswith("pending human labels")


def test_snapshot_integrity():
    assert STORE.integrity_errors() == []


def test_claim_eval_reports_strict_and_conditional_recall():
    ce = json.loads((RESULTS / "receipts" / "claim_eval.json").read_text())
    for v in ce["recall_by_perturbation"].values():
        assert v["critic_recall_strict"] <= v["critic_recall_lenient"]
        assert "critic_recall_lenient_conditional" in v and "labelled_partial_so_shipped_tagged" in v
    assert any("kappa" in n for n in ce["notes"])
