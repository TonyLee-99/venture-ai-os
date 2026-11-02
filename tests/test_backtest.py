"""F07: the committed backtest numbers recompute exactly from the frozen table, and the walk-forward split
never trains on an outcome window that was still open at the test date."""

import json

import pandas as pd
import pytest

from vaios.config import RESULTS
from vaios.screening import backtest
from vaios.screening import score as sc
from vaios.screening.metrics import auc, averaged, precision_at_k

BT = json.loads((RESULTS / "backtest" / "backtest.json").read_text())


@pytest.fixture(scope="module")
def scored():
    df, test_t0s, _ = backtest.add_scores(backtest.load())
    return df[df["t0"].isin(test_t0s)].reset_index(drop=True), test_t0s


def test_point_metrics_recompute_exactly(scored):
    test, _ = scored
    point = averaged(test, list(backtest.SCORERS))
    for col, d in BT["scores"].items():
        for m in ("auc", "p@20", "p@50", "lift@50"):
            assert round(point[col][m], 4) == d[m], (col, m)


def test_sample_size_and_test_t0s(scored):
    test, test_t0s = scored
    assert len(test_t0s) >= 5 and BT["n_rows_test"] == len(test) >= 1000
    assert BT["n_positives_test"] == int(test["raised"].sum()) >= 50


def test_walk_forward_never_trains_on_open_windows(monkeypatch):
    seen = []
    real_fit = sc.fit_logit

    def spy(train, feats):
        seen.append(train["outcome_end"].max())
        return real_fit(train, feats)

    monkeypatch.setattr(sc, "fit_logit", spy)
    df, test_t0s, _ = backtest.add_scores(backtest.load())
    # the first len(test_t0s)*2 fits are the walk-forward ones (two models per test T0), in T0 order
    for i, t0 in enumerate(test_t0s):
        for k in (2 * i, 2 * i + 1):
            assert seen[k] <= t0


def test_bootstrap_ci_brackets_point_estimate():
    for col, d in BT["scores"].items():
        lo, hi = d["auc_ci95"]
        assert lo <= d["auc"] <= hi, col


def test_leaky_reference_is_flagged_and_not_a_baseline():
    assert BT["scores"]["leaky_stars_now"]["leakage_exposed"] is True
    assert all(v["best_baseline"].startswith("b_") for v in BT["paired_vs_best_baseline"].values())


def test_auc_matches_sklearn():
    from sklearn.metrics import roc_auc_score
    y = pd.Series([0, 1, 0, 1, 1, 0, 0]).to_numpy()
    s = pd.Series([0.1, 0.9, 0.3, 0.3, 0.8, 0.2, 0.5]).to_numpy()
    assert abs(auc(y, s) - roc_auc_score(y, s)) < 1e-12
    assert precision_at_k(y, s, 2) == 1.0
