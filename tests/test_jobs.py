"""F13: job specs are complete; traces point at recorded LLM calls; strict replay reproduces committed memos."""

import json

import pytest

from vaios.agents.runner import load_spec
from vaios.config import CASSETTES, JOBS, RESULTS

REQUIRED = {"job", "agent", "purpose", "inputs", "output", "sla", "eval", "failure"}


def test_job_specs_complete():
    specs = sorted(JOBS.glob("*.yaml"))
    assert len(specs) >= 6
    for p in specs:
        spec = load_spec(p.stem)
        assert REQUIRED <= set(spec), (p.name, REQUIRED - set(spec))
        assert "max_llm_calls" in spec["sla"]


def test_traces_reference_recorded_cassettes_and_meet_sla():
    traces = list((RESULTS / "traces").rglob("*.json"))
    assert traces
    for t in traces:
        rec = json.loads(t.read_text())
        assert rec["status"] == "ok", (t.name, rec.get("error"))
        assert rec["sla_violations"] == [], (t.name, rec["sla_violations"])
        for s in rec["steps"]:
            if s.get("kind") == "llm":
                assert (CASSETTES / s["cache_key"][:2] / f"{s['cache_key']}.json").exists(), (t.name, s["step"])


@pytest.mark.skipif(not list((RESULTS / "memos").glob("*.json")), reason="no memos yet")
def test_strict_replay_reproduces_memos(monkeypatch):
    from vaios.agents import pipeline

    before = {p.name: p.read_text() for p in (RESULTS / "memos").glob("*")}
    changelog = (RESULTS / "artifacts" / "changelog.jsonl").read_text()
    monkeypatch.setenv("VAIOS_STRICT_REPLAY", "1")
    pipeline.sourcing_run()  # any cache miss raises ReplayMiss
    after = {p.name: p.read_text() for p in (RESULTS / "memos").glob("*")}
    assert before == after
    assert (RESULTS / "artifacts" / "changelog.jsonl").read_text() == changelog  # idempotent: no new versions
