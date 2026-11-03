"""Screening scores. All inputs are point-in-time features; nothing here may read an outcome or today's stars.

Three scorers, all deterministic:
- `heuristic`: PRE-SPECIFIED (written before the first backtest run, ADR 0004): mean within-T0 percentile
  rank of five traction signals. No fitting, so it cannot overfit the backtest.
- `logit_full`: L2 logistic regression on all point-in-time features, trained walk-forward.
- `logit_github`: the same on GitHub-only features. This is the score used live on niche candidates, most of
  which are not on DefiLlama (so it must be backtested on its own).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

GITHUB_FEATURES = ["log_commits_90d", "commit_growth", "log_commits_before", "log_n_repos", "log_gh_age"]
FULL_FEATURES = GITHUB_FEATURES + ["log_tvl", "tvl_growth_90d", "log_listing_age", "has_prior_raise",
                                   "log_days_since_raise"]
HEURISTIC_SIGNALS = ["commits_90d", "commit_growth", "tvl_growth_90d", "tvl_t0", "newness"]


def model_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Turn raw point-in-time columns into model features (logs tame heavy tails: TVL spans 9 orders)."""
    x = pd.DataFrame(index=df.index)
    x["log_commits_90d"] = np.log1p(df["commits_90d"])
    x["commit_growth"] = df["commit_growth"].fillna(0)
    x["log_commits_before"] = np.log1p(df["commits_before"])
    x["log_n_repos"] = np.log1p(df["n_repos"].fillna(0))
    x["log_gh_age"] = np.log1p(df["gh_age_days"].fillna(0))
    x["log_tvl"] = np.log1p(df["tvl_t0"].clip(lower=0))
    x["tvl_growth_90d"] = df["tvl_growth_90d"].fillna(0).clip(-10, 10)
    x["log_listing_age"] = np.log1p(df["listing_age_days"].clip(lower=0))
    x["has_prior_raise"] = (df["prior_raises"] > 0).astype(float)
    # never raised -> treat as "very long ago" (10 years) so the feature is monotone
    x["log_days_since_raise"] = np.log1p(df["days_since_last_raise"].fillna(3650))
    return x


def heuristic(df: pd.DataFrame) -> pd.Series:
    sig = df.assign(newness=-df["listing_age_days"])[HEURISTIC_SIGNALS]
    ranks = sig.groupby(df["t0"]).rank(pct=True)
    return ranks.mean(axis=1)


GITHUB_HEURISTIC_SIGNALS = ["commits_90d", "commit_growth", "gh_newness"]


def heuristic_github(df: pd.DataFrame, group: str | None = "t0") -> pd.Series:
    """The pre-specified heuristic restricted to signals a GitHub-only candidate has (ADR 0010): recent commits,
    commit growth, and newness (minus the age of the owner's oldest repo instead of DefiLlama listing age).
    For non-DefiLlama candidates the TVL terms of the full heuristic are constant and would drop out anyway."""
    sig = df.assign(gh_newness=-df["gh_age_days"])[GITHUB_HEURISTIC_SIGNALS]
    ranks = sig.groupby(df[group]).rank(pct=True) if group else sig.rank(pct=True)
    return ranks.mean(axis=1)


def fit_logit(train: pd.DataFrame, features: list[str]):
    model = make_pipeline(StandardScaler(), LogisticRegression(C=0.5, tol=1e-10, max_iter=10000))
    model.fit(model_matrix(train)[features], train["raised"].astype(int))
    return model


def predict(model, df: pd.DataFrame, features: list[str]) -> np.ndarray:
    return model.predict_proba(model_matrix(df)[features])[:, 1]


def coefficients(model, features: list[str]) -> dict[str, float]:
    return {f: round(float(c), 3) for f, c in zip(features, model[-1].coef_[0], strict=True)}
