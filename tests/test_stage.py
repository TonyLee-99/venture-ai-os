"""F19: seed-stage eligibility comes only from sourced evidence, and every memo carries the stage header."""

import json

from vaios.agents import stage
from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore

CHECKS = json.loads((RESULTS / "sourcing" / "stage_checks.json").read_text())


def test_classify_rules():
    sig = stage.parse(["We raised a $10M seed round led by a16z"], [])
    assert not stage.classify(sig, None, None, [])["seed_eligible"]
    sig = stage.parse(["Tempo is incubated by Stripe and Paradigm"], [])
    assert "incubated by stripe" in stage.classify(sig, None, None, [])["ineligible_reasons"]
    assert stage.classify(stage.parse([], []), "Fall 2026", None, [])["stage"].startswith("YC")
    assert stage.classify(stage.parse([], []), None, None, [])["stage"].startswith("unknown")


def test_known_late_stage_names_are_excluded_with_stored_evidence():
    by = {c["entity"]: c for c in CHECKS}
    store = DocStore()
    for e in ("tempo", "meritsystems", "gokite"):
        assert by[e]["seed_eligible"] is False and by[e]["ineligible_reasons"], e
        assert by[e]["doc_ids"] and all(store.get(d) for d in by[e]["doc_ids"]), e


def test_memo_queue_is_seed_eligible_and_headed():
    short = json.loads((RESULTS / "sourcing" / "shortlist.json").read_text())["shortlist"]
    for r in short:
        assert r["stage"]["seed_eligible"] is True
        md = (RESULTS / "memos" / f"{r['entity']}.md").read_text()
        assert "| Stage | Last known round | Token | YC batch | Triage rank |" in md
