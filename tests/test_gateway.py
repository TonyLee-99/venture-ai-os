"""F02: gateway routing, cache, ledger, retries, strict replay, schema repair -- with fake backends (offline)."""

import json

import pytest
from pydantic import BaseModel

from vaios.config import CASSETTES
from vaios.gateway.backends import BackendError, RawResult
from vaios.gateway.gateway import ROUTES, BudgetExceeded, Gateway, ReplayMiss, extract_json


class Fake:
    def __init__(self, name, family, replies):
        self.name, self.family, self.replies, self.calls = name, family, list(replies), 0

    def call(self, system, prompt):
        self.calls += 1
        r = self.replies.pop(0)
        if isinstance(r, Exception):
            raise r
        return RawResult(text=r, input_tokens=10, output_tokens=5, cost_usd=0.001, latency_s=0.01)


def make(tmp_path, claude_replies=(), codex_replies=(), **kw):
    fakes = {"claude_cli": Fake("claude_cli", "anthropic", claude_replies),
             "codex_cli": Fake("codex_cli", "openai", codex_replies)}
    gw = Gateway(cache_dir=tmp_path / "cache", ledger=tmp_path / "ledger.jsonl", backends=fakes, **kw)
    return gw, fakes


def test_cache_hit_second_time_and_ledger_counts_only_real_calls(tmp_path):
    gw, fakes = make(tmp_path, claude_replies=["hello"])
    a = gw.complete("draft", "sys", "p1", tag="t")
    b = gw.complete("draft", "sys", "p1", tag="t")
    assert (a.cached, b.cached) == (False, True) and b.text == "hello"
    assert fakes["claude_cli"].calls == 1
    rows = [json.loads(x) for x in (tmp_path / "ledger.jsonl").read_text().splitlines()]
    assert len(rows) == 1 and rows[0]["tag"] == "t" and rows[0]["cost_usd"] == 0.001


def test_routes_use_two_model_families():
    assert ROUTES["draft"][0] != ROUTES["critique"][0]
    gw = Gateway()
    assert gw.family("draft") != gw.family("critique")


def test_strict_replay_raises_on_miss_and_serves_hits(tmp_path, monkeypatch):
    gw, _ = make(tmp_path, claude_replies=["recorded"])
    gw.complete("draft", "s", "known")
    monkeypatch.setenv("VAIOS_STRICT_REPLAY", "1")
    assert gw.complete("draft", "s", "known").text == "recorded"
    with pytest.raises(ReplayMiss):
        gw.complete("draft", "s", "never seen")


def test_retries_then_succeeds(tmp_path, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    gw, fakes = make(tmp_path, codex_replies=[BackendError("overloaded"), "ok"])
    assert gw.complete("critique", "s", "p").text == "ok"
    assert fakes["codex_cli"].calls == 2


def test_budget_guard(tmp_path):
    gw, _ = make(tmp_path, claude_replies=["a", "b"], max_calls=1)
    gw.complete("draft", "s", "p1")
    with pytest.raises(BudgetExceeded):
        gw.complete("draft", "s", "p2")


class Score(BaseModel):
    score: int


def test_schema_validation_with_one_repair_round(tmp_path):
    gw, fakes = make(tmp_path, claude_replies=["not json at all", '```json\n{"score": 4}\n```'])
    res = gw.complete("judge", "s", "p", schema=Score)
    assert res.parsed == {"score": 4} and fakes["claude_cli"].calls == 2


def test_extract_json_handles_prose_and_fences():
    assert extract_json('Sure! {"a": [1, 2]} hope this helps') == {"a": [1, 2]}
    assert extract_json("```json\n[1,2]\n```") == [1, 2]


def test_committed_cassettes_are_well_formed():
    files = list(CASSETTES.rglob("*.json"))
    for f in files[:500]:
        rec = json.loads(f.read_text())
        assert rec["result"]["cache_key"] == f.stem
        assert {"route", "backend", "model", "system", "prompt"} <= set(rec["request"])
