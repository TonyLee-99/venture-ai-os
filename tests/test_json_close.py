"""Regeneration checks tolerate last-digit float rounding across OS, and nothing else."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("json_close", Path(__file__).resolve().parents[1] / "scripts/json_close.py")
jc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jc)


def test_rounding_flip_passes_but_real_changes_fail():
    assert jc.close({"spearman": 0.121}, {"spearman": 0.1211}) == []
    assert jc.close({"auc": 0.7496}, {"auc": 0.7596})
    assert jc.close({"n": 801}, {"n": 802})
    assert jc.close({"label": "seed"}, {"label": "angel"})
    assert jc.close({"a": [1, 2]}, {"a": [1, 2, 3]})
