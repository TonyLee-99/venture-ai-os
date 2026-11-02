"""F10: every memo is critiqued by the other model family; disagreements become decision cards; the human
feedback ledger follows its schema and seed rows are marked as examples."""

import json

import pytest

from vaios.agents.schemas import HumanDecision
from vaios.config import RESULTS, ROOT

MEMOS = sorted((RESULTS / "memos").glob("*.json"))


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_cross_family_critique_and_cards():
    for p in MEMOS:
        out = json.loads(p.read_text())
        drafter, critic = out["models"]["drafter"], out["models"]["critic"]
        assert drafter.split(":")[0] != critic.split(":")[0], p.name  # different backend family
        card = RESULTS / "decision_cards" / f"{out['entity']}.md"
        assert card.exists() == bool(out["disagreements"]), p.name
        if card.exists():
            assert "## Decision" in card.read_text()


def test_feedback_ledger_schema_and_example_flags():
    rows = [json.loads(x) for x in (ROOT / "ledger" / "human_feedback.jsonl").read_text().splitlines() if x.strip()]
    assert rows
    for r in rows:
        HumanDecision.model_validate(r)
        if r["reviewer"] == "EXAMPLE":
            assert r["example"] is True and "EXAMPLE" in r["reason"]
