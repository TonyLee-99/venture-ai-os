"""The committed backtest numbers recompute exactly from the frozen table, and the walk-forward split
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


def test_seed_relevant_population_is_reported_first():
    pops = BT["populations"]
    nr = pops["never_raised"]
    assert nr["n_positive_rows"] < BT["n_positives_test"] and nr["n_positive_protocols"] <= nr["n_positive_rows"]
    assert BT["scores"] == pops["all"]["scores"]
    for key in ("all_owner_clustered", "never_raised_owner_clustered", "all_gh_found_only", "never_raised_gh_found_only"):
        assert key in pops
    assert "b_prior_funding" in nr["scores"] and nr["scores"]["b_prior_funding"]["auc"] == 0.5  # constant there


def test_round_mix_lead_time_and_selection_reported():
    rm = BT["round_mix_all"]
    assert rm["distinct_protocols"] == BT["n_positive_protocols_test"] and rm["distinct_raises"] >= rm["distinct_protocols"]
    assert sum(rm["by_round"].values()) == rm["distinct_raises"]
    lt = BT["lead_time"]
    assert {"github_first_repo", "defillama_listing", "earliest_public_signal"} <= set(lt)
    assert 0 <= BT["selection"]["gh_found_rate_positives"] <= 1
