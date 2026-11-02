"""F23: the decision and flag-adjudication tools record only what a human passes in."""

import json

import pytest

from vaios import decide
from vaios.config import RESULTS


@pytest.mark.skipif(not list((RESULTS / "memos").glob("*.json")), reason="no memos yet")
def test_record_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr(decide, "LEDGER", tmp_path / "h.jsonl")
    monkeypatch.setattr(decide, "FLAG_LEDGER", tmp_path / "f.jsonl")
    before = decide.status()
    assert before["human_decisions_recorded"] == 0
    card = decide.memos()[0]
    decide.record(card["entity"], "pass", "test-only row in a temp ledger", "pytest")
    row = json.loads((tmp_path / "h.jsonl").read_text())
    assert row["decision"] == "pass" and row["example"] is False
    assert decide.status()["human_decisions_recorded"] == 1


def test_flag_sample_has_blank_human_labels():
    import csv
    rows = list(csv.DictReader((RESULTS / "adjudication" / "flag_sample.csv").open()))
    assert rows and all(r["human_label"] == "" for r in rows)
