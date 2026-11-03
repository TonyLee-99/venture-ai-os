"""Blind cross-family critique with per-claim entailment; flagged claims withheld or tagged; scores
re-derived; advance budget; decision cards only on real disagreement; human verdicts never pre-filled."""

import json

import pytest

from vaios.agents import diligence
from vaios.agents.schemas import HumanDecision
from vaios.config import CASSETTES, RESULTS, ROOT

MEMOS = [json.loads(p.read_text()) for p in sorted((RESULTS / "memos").glob("*.json"))]


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_cross_family_blind_critique():
    for m in MEMOS:
        assert m["models"]["drafter"].split(":")[0] != m["models"]["critic"].split(":")[0]
        trace = json.loads((RESULTS / "traces" / "diligence_memo" / f"{m['entity']}.json").read_text())
        key = next(s["cache_key"] for s in trace["steps"] if s.get("step") == "critique")
        prompt = json.loads((CASSETTES / key[:2] / f"{key}.json").read_text())["request"]["prompt"]
        claims_part = prompt.split("DRAFTER CLAIMS:")[1].split("Output JSON schema")[0]
        assert '"recommendation"' not in claims_part and '"scores"' not in claims_part, m["entity"]


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_reconciliation_and_cards():
    advances = 0
    for m in MEMOS:
        labels = {x["claim_id"]: x["label"] for x in m["critique"]["claim_labels"]}
        shipped = {c["id"] for c in m["memo"]["claims"]}
        for w in m["withheld_by_critic"]:
            assert w["claim"]["id"] not in shipped and w["critic_label"] in ("contradicts", "unsupported")
        for c in m["memo"]["claims"]:
            assert c["support"] == labels.get(c["id"], "unlabelled")
        assert m["disagreements"] == diligence.disagreement(m["memo"], m["critique"])
        card = RESULTS / "decision_cards" / f"{m['entity']}.md"
        assert card.exists() == bool(m["disagreements"])
        assert m["memo"]["recommendation"] == diligence.policy(m["memo"]["scores"], m["memo"]["recommendation"]) or \
            m["memo"].get("committee_note")
        advances += m["memo"]["recommendation"] == "advance"
    assert advances <= diligence.ADVANCE_BUDGET


def test_policy_and_budget():
    s = lambda p, n, e: {d: {"score": v, "rationale": ""} for d, v in zip(("pmf", "narrative", "execution"), (p, n, e), strict=True)}  # noqa: E731
    assert diligence.policy(s(2, 2, 3), "advance") == "pass"
    assert diligence.policy(s(3, 4, 3), "advance") == "watch"
    assert diligence.policy(s(4, 4, 4), "advance") == "advance"


def test_human_ledgers_are_empty_until_the_owner_fills_them():
    for name in ("human_feedback.jsonl", "flag_adjudication.jsonl"):
        rows = [json.loads(x) for x in (ROOT / "ledger" / name).read_text().splitlines() if x.strip()]
        assert all(r.get("reviewer") != "EXAMPLE" for r in rows)
        for r in rows:
            if name == "human_feedback.jsonl":
                HumanDecision.model_validate(r)
    for r in (ROOT / "ledger" / "human_feedback.example.jsonl").read_text().splitlines():
        assert json.loads(r)["example"] is True


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_recommendations_follow_the_score_policy():
    seen = {}
    for m in MEMOS:
        key = tuple(m["memo"]["scores"][d]["score"] for d in ("pmf", "narrative", "execution"))
        rec = m["memo"]["recommendation"]
        if not m["memo"].get("committee_note"):
            assert rec == diligence.policy(m["memo"]["scores"]), m["entity"]
            assert seen.setdefault(key, rec) == rec  # same scores, same call
        assert m["critique"]["recommendation"] == diligence.policy(m["critique"]["scores"])
        if m["receipts"]["critic_entailed_share"] < diligence.EVIDENCE_MIN_ENTAILED:
            assert m["memo"]["evidence_status"] == "evidence insufficient" and rec != "advance"


def test_unlabelled_claims_fail_closed():
    shipped, withheld, counts = diligence.reconcile([{"id": "c1", "text": "x"}], [])
    assert not shipped and withheld[0]["critic_label"] == "unlabelled"


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_free_text_numbers_are_supported():
    from vaios.receipts.verify import _matches, numbers_in, written_numbers
    for m in MEMOS:
        allowed = [n for c in m["memo"]["claims"] for n in numbers_in(c["text"] + " " + (c.get("quote") or ""))]
        allowed += [float(v) for v in m["facts"].values() if isinstance(v, int | float)]
        texts = m["memo"]["risks"] + m["memo"]["open_questions"] + [m["memo"]["one_liner"], m["memo"]["thesis_fit"]]
        texts += [m["memo"]["scores"][d]["rationale"] for d in ("pmf", "narrative", "execution")]
        for t in texts:
            for w in written_numbers(t):
                assert any(_matches(w, a) for a in allowed), (m["entity"], t)
