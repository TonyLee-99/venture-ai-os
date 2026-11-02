"""One place that touches the network: polite GET with retries, and a provenance manifest row per raw file.

Contract for every source module: fetch -> write one raw file under data/raw/<source>/ -> `record()` a
manifest row (source, url, fetched_at, sha256, bytes, path). A paid connector (PitchBook, Crunchbase...)
would be one more module with the same contract.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx

from vaios.config import RAW, ROOT, USER_AGENT

MANIFEST = RAW / "_manifest.jsonl"
_lock = threading.Lock()  # several fetch threads append to the same manifest


def record(source: str, url: str, path: Path, n_records: int | None = None) -> dict:
    data = path.read_bytes()
    row = {
        "source": source,
        "url": url,
        "fetched_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "path": str(path.relative_to(ROOT)),
        "n_records": n_records,
    }
    with _lock:
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        with MANIFEST.open("a") as f:
            f.write(json.dumps(row) + "\n")
    return row


def get_json(url: str, *, params: dict | None = None, retries: int = 4, timeout: float = 60.0) -> Any:
    last = ""
    for attempt in range(retries + 1):
        try:
            r = httpx.get(url, params=params, timeout=timeout, follow_redirects=True,
                          headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            if r.status_code in (400, 401, 402, 403, 404):
                break  # not retryable
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(min(60, 2 ** attempt * 2))
    raise RuntimeError(f"GET {url} failed: {last}")


def get_text(url: str, *, timeout: float = 30.0) -> str:
    r = httpx.get(url, timeout=timeout, follow_redirects=True, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.text


def gh_api(path: str, *, graphql: str | None = None, retries: int = 4) -> Any:
    """GitHub via the `gh` CLI so the token never lives in this repo or its env files."""
    cmd = ["gh", "api", path] if graphql is None else ["gh", "api", "graphql", "-f", f"query={graphql}"]
    last = ""
    for attempt in range(retries + 1):
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode == 0:
            return json.loads(proc.stdout)
        last = (proc.stderr or proc.stdout)[:300]
        if "Not Found" in last or "Could not resolve" in last:
            break
        time.sleep(min(90, 2 ** attempt * 3))
    raise RuntimeError(f"gh api {path} failed: {last}")


def write_json(path: Path, obj: Any, *, compress: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = json.dumps(obj, ensure_ascii=False).encode()
    if compress:
        path = path.with_suffix(path.suffix + ".gz")
        path.write_bytes(gzip.compress(blob, mtime=0))  # mtime=0 -> same content, same sha256
    else:
        path.write_bytes(blob)
    return path


def read_json(path: Path) -> Any:
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return json.loads(data)
