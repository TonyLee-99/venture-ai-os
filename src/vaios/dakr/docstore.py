"""DAKR document store: content-addressed source snapshots that agent outputs cite.

A snapshot is the exact text an agent saw (a README, a web page, an API record rendered as text). Its id is
derived from its content, so a citation can never silently point at a changed page: re-fetching a page that
changed creates a new doc_id, and the old one stays.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from vaios.config import STORE


@dataclass
class DocMeta:
    doc_id: str
    entity: str
    kind: str        # github_readme | github_repo | website | hn | yc | defillama | x402scan | event_source ...
    url: str
    fetched_at: str  # date the source was fetched (YYYY-MM-DD)
    sha256: str
    chars: int
    title: str = ""


class DocStore:
    def __init__(self, root: Path = STORE):
        self.root = Path(root)
        self.snap_dir = self.root / "snapshots"
        self.index_path = self.root / "index.jsonl"
        self._index: dict[str, DocMeta] | None = None

    @property
    def index(self) -> dict[str, DocMeta]:
        if self._index is None:
            self._index = {}
            if self.index_path.exists():
                for line in self.index_path.read_text().splitlines():
                    m = DocMeta(**json.loads(line))
                    self._index[m.doc_id] = m
        return self._index

    @staticmethod
    def make_id(text: str) -> str:
        return "d_" + hashlib.sha256(text.encode()).hexdigest()[:16]

    def put(self, text: str, *, entity: str, kind: str, url: str, fetched_at: str, title: str = "") -> str:
        doc_id = self.make_id(text)
        if doc_id in self.index:  # idempotent: same content, same id, no new row
            return doc_id
        self.snap_dir.mkdir(parents=True, exist_ok=True)
        (self.snap_dir / f"{doc_id}.txt").write_text(text)
        meta = DocMeta(doc_id, entity, kind, url, fetched_at, hashlib.sha256(text.encode()).hexdigest(),
                       len(text), title)
        self.index[doc_id] = meta
        with self.index_path.open("a") as f:
            f.write(json.dumps(asdict(meta), ensure_ascii=False) + "\n")
        return doc_id

    def get(self, doc_id: str) -> str | None:
        p = self.snap_dir / f"{doc_id}.txt"
        return p.read_text() if p.exists() else None

    def meta(self, doc_id: str) -> DocMeta | None:
        return self.index.get(doc_id)

    def for_entity(self, entity: str) -> list[DocMeta]:
        return [m for m in self.index.values() if m.entity == entity]

    def integrity_errors(self) -> list[str]:
        """Every indexed snapshot exists and still hashes to its recorded sha256."""
        errs = []
        for m in self.index.values():
            text = self.get(m.doc_id)
            if text is None:
                errs.append(f"{m.doc_id}: missing file")
            elif hashlib.sha256(text.encode()).hexdigest() != m.sha256:
                errs.append(f"{m.doc_id}: content changed")
        return errs
