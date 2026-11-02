"""Versioned artifacts with provenance and a change log (memos, briefs, candidate lists, facts).

`save()` writes a new version only when the content changed, so re-running a job on the same inputs is a
no-op (idempotent). Each version records what it was built from: snapshot doc_ids, LLM cache keys,
warehouse metric keys, and the run id.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from vaios.config import RESULTS

ROOT = RESULTS / "artifacts"
CHANGELOG = ROOT / "changelog.jsonl"


def _sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def latest(kind: str, entity: str, root: Path = ROOT) -> tuple[int, dict | None]:
    d = root / kind / entity
    versions = sorted((int(p.stem[1:]), p) for p in d.glob("v*.json")) if d.exists() else []
    if not versions:
        return 0, None
    n, p = versions[-1]
    return n, json.loads(p.read_text())


def save(kind: str, entity: str, content: dict, *, provenance: dict, as_of: str, root: Path = ROOT) -> dict:
    """Returns {"version": n, "changed": bool}. Provenance: {run_id, doc_ids, cache_keys, metrics, job}."""
    n, prev = latest(kind, entity, root)
    sha = _sha(content)
    if prev is not None and prev["content_sha256"] == sha:
        return {"version": n, "changed": False}
    record = {"kind": kind, "entity": entity, "version": n + 1, "parent_version": n or None, "as_of": as_of,
              "content_sha256": sha, "provenance": provenance, "content": content}
    path = root / kind / entity / f"v{n + 1}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    changed_keys = sorted(k for k in content if prev is None or prev["content"].get(k) != content.get(k))
    with (root / "changelog.jsonl").open("a") as f:
        f.write(json.dumps({"kind": kind, "entity": entity, "version": n + 1, "as_of": as_of,
                            "run_id": provenance.get("run_id"), "content_sha256": sha,
                            "changed_fields": changed_keys}) + "\n")
    return {"version": n + 1, "changed": True}
