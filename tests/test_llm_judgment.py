"""F08/F22: LLM judgment is evaluated where it cannot know the answer (anonymized walk-forward set; post-cutoff set
with probed cutoffs), leakage-exposed arms are flagged, and the eval replays offline with identical results."""

import json

from vaios.config import RESULTS

OUT = RESULTS / "backtest" / "llm_judgment.json"


def test_structure_and_flags():
    lj = json.loads(OUT.read_text())
    wf, pc = lj["walk_forward_anonymized"], lj["post_cutoff"]
    assert wf["n_positives"] == 80 and all(not v["leakage_exposed"] for v in wf["all"].values())
    for k, v in pc["results"].items():
        assert v["leakage_exposed"] == k.startswith("named"), k
    probe = json.loads((RESULTS / "backtest" / "cutoff_probe.json").read_text())
    for model, ok in pc["probed_knowledge_ends_before_window"].items():
        latest = probe["models"][model]["latest_correct_event"] or "0000"
        assert ok == (latest < pc["t0"])  # computed from the probe, not hard-coded


def test_no_bootstrap_drops():
    lj = json.loads(OUT.read_text())
    for v in lj["walk_forward_anonymized"]["all"].values():
        assert v["auc_ci95"][0] <= v["auc"] <= v["auc_ci95"][1]


def test_strict_replay_reproduces(monkeypatch):
    from vaios.screening import llm_judgment

    before = OUT.read_text()
    monkeypatch.setenv("VAIOS_STRICT_REPLAY", "1")
    monkeypatch.setattr("vaios.config.WAREHOUSE", RESULTS / "does-not-exist.duckdb")
    llm_judgment.run()
    assert OUT.read_text() == before
