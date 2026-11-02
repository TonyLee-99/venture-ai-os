"""Ranking metrics and a protocol-clustered bootstrap."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr


def auc(y: np.ndarray, s: np.ndarray) -> float:
    """ROC AUC via the Mann-Whitney rank formula (ties get average ranks); ~50x faster than sklearn in a loop."""
    n_pos = int(y.sum())
    n_neg = len(y) - n_pos
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    r = rankdata(s)
    return float((r[y == 1].sum() - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg))


def precision_at_k(y: np.ndarray, s: np.ndarray, k: int) -> float:
    order = np.argsort(-s, kind="stable")
    return float(np.mean(y[order[:k]]))


def per_t0_metrics(y: np.ndarray, s: np.ndarray) -> dict[str, float]:
    base = float(np.mean(y))
    out = {"n": int(len(y)), "positives": int(y.sum()), "base_rate": base, "auc": auc(y, s)}
    out["spearman"] = float(spearmanr(s, y).statistic) if 0 < y.sum() < len(y) else float("nan")
    for k in (20, 50):
        out[f"p@{k}"] = precision_at_k(y, s, k)
    out["lift@50"] = out["p@50"] / base if base > 0 else float("nan")
    return out


def averaged(df: pd.DataFrame, score_cols: list[str], metrics=("auc", "p@20", "p@50", "lift@50")) -> dict:
    """{score: {metric: mean over T0}} computed on whatever rows `df` holds (used inside the bootstrap)."""
    acc: dict[str, dict[str, list[float]]] = {c: {m: [] for m in metrics} for c in score_cols}
    for _, g in df.groupby("t0"):
        y = g["raised"].to_numpy(int)
        if y.sum() == 0:
            continue
        base = y.mean()
        for c in score_cols:
            s = g[c].to_numpy(float)
            vals = {"auc": auc(y, s), "p@20": precision_at_k(y, s, 20), "p@50": precision_at_k(y, s, 50)}
            vals["lift@50"] = vals["p@50"] / base
            for m in metrics:
                acc[c][m].append(vals[m])
    return {c: {m: float(np.nanmean(v)) for m, v in d.items()} for c, d in acc.items()}


def cluster_bootstrap(df: pd.DataFrame, stat: Callable[[pd.DataFrame], dict[str, float]], n_boot: int = 1000,
                      seed: int = 7) -> dict[str, tuple[float, float]]:
    """95% CIs resampling whole protocols (all their T0 rows together): rows of one protocol are correlated."""
    rng = np.random.default_rng(seed)
    groups = df.groupby("slug").indices
    slugs = np.array(list(groups))
    draws: dict[str, list[float]] = {}
    for _ in range(n_boot):
        pick = rng.choice(slugs, size=len(slugs), replace=True)
        rows = np.concatenate([groups[s] for s in pick])
        for k, v in stat(df.iloc[rows]).items():
            draws.setdefault(k, []).append(v)
    return {k: tuple(float(x) for x in np.nanpercentile(v, [2.5, 97.5])) for k, v in draws.items()}
