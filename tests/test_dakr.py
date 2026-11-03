"""Warehouse SQL builds the marts, the doc store is content-addressed, artifacts are versioned + idempotent."""

import json

from sql_fixture import build

from vaios.dakr import artifacts
from vaios.dakr.docstore import DocStore
from vaios.dakr.warehouse import SQL_DIR


def test_sql_models_build_expected_tables():
    con = build()
    tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
    assert {"protocols", "raises", "features_pit", "labels_pit", "x402_weekly", "commits_weekly",
            "leaky_reference"} <= tables
    assert len(list(SQL_DIR.glob("*.sql"))) >= 3


def test_docstore_is_content_addressed_and_idempotent(tmp_path):
    s = DocStore(tmp_path)
    a = s.put("hello world", entity="e", kind="k", url="u", fetched_at="2026-11-02")
    b = s.put("hello world", entity="e", kind="k", url="u", fetched_at="2026-11-02")
    c = s.put("hello world!", entity="e", kind="k", url="u", fetched_at="2026-11-02")
    assert a == b != c and len(s.index_path.read_text().splitlines()) == 2
    assert s.integrity_errors() == []
    (s.snap_dir / f"{a}.txt").write_text("tampered")
    assert s.integrity_errors()


def test_artifacts_version_only_on_change(tmp_path):
    prov = {"run_id": "r1", "job": "t"}
    assert artifacts.save("memo", "x", {"a": 1}, provenance=prov, as_of="d", root=tmp_path)["version"] == 1
    assert artifacts.save("memo", "x", {"a": 1}, provenance=prov, as_of="d", root=tmp_path)["changed"] is False
    v2 = artifacts.save("memo", "x", {"a": 2, "b": 3}, provenance=prov, as_of="d", root=tmp_path)
    assert v2 == {"version": 2, "changed": True}
    log = [json.loads(x) for x in (tmp_path / "changelog.jsonl").read_text().splitlines()]
    assert len(log) == 2 and log[1]["changed_fields"] == ["a", "b"]
    _, rec = artifacts.latest("memo", "x", tmp_path)
    assert rec["parent_version"] == 1 and rec["provenance"]["run_id"] == "r1"


def test_committed_store_integrity():
    assert DocStore().integrity_errors() == []
