"""F08: LLM judgment is evaluated only on post-cutoff outcomes, leakage-exposed arms are flagged, and the
whole eval replays offline from cassettes with identical results."""

import json

from vaios.config import ASSUMED_MODEL_CUTOFF, RESULTS

OUT = RESULTS / "backtest" / "llm_judgment.json"


def test_post_cutoff_only_and_flags():
    lj = json.loads(OUT.read_text())
    assert lj["t0"] >= str(ASSUMED_MODEL_CUTOFF) and lj["all_outcomes_after_cutoff"] is True
    for k, v in lj["results"].items():
        assert v["leakage_exposed"] == k.startswith("named"), k
    assert any(k.startswith("anonymized") for k in lj["results"])


def test_strict_replay_reproduces(monkeypatch):
    from vaios.screening import llm_judgment

    before = OUT.read_text()
    monkeypatch.setenv("VAIOS_STRICT_REPLAY", "1")
    monkeypatch.setattr("vaios.config.WAREHOUSE", RESULTS / "does-not-exist.duckdb")
    llm_judgment.run()
    assert OUT.read_text() == before
