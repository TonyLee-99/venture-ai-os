"""F03: every raw pull has provenance (url, fetched_at, sha256, bytes); >= 6 live sources."""

import json
import re

import pandas as pd

from vaios.config import RESULTS


def test_at_least_six_sources_with_files():
    m = json.loads((RESULTS / "data_manifest.json").read_text())
    assert m["n_sources"] >= 6
    for name, s in m["sources"].items():
        assert s["files"] > 0 and s["bytes"] > 0, name


def test_every_file_has_provenance():
    files = pd.read_csv(RESULTS / "data_manifest_files.csv.gz")
    assert len(files) == json.loads((RESULTS / "data_manifest.json").read_text())["n_files"]
    assert files["sha256"].str.fullmatch(r"[0-9a-f]{64}").all()
    assert files["url"].str.len().gt(0).all()
    assert files["fetched_at"].map(lambda x: bool(re.match(r"2026-\d\d-\d\dT", x))).all()
    assert files["path"].str.startswith("data/raw/").all()
