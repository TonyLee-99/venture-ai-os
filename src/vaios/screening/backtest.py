"""`make backtest`: walk-forward, point-in-time evaluation of the screening score against revealed VC decisions.

Input: results/frozen/backtest_table.parquet (features as of each T0 + the raise outcome in [T0, T0+12m)).
Output: results/backtest/backtest.json (+ per-T0 CSV). Pre-registration: docs/decisions/0004.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from vaios.config import BACKTEST_T0S, FROZEN, RESULTS
from vaios.screening import score as sc
from vaios.screening.metrics import averaged, cluster_bootstrap, per_t0_metrics

OUT = RESULTS / "backtest"

SCORERS = {  # column -> (label, leakage-exposed?)
    "s_logit_full": ("Logistic, all point-in-time features (walk-forward)", False),
    "s_logit_github": ("Logistic, GitHub-only features (walk-forward; live niche score)", False),
    "s_heuristic": ("Pre-registered heuristic (no fitting)", False),
    "b_random": ("Baseline: random", False),
    "b_tvl": ("Baseline: TVL size", False),
    "b_commits": ("Baseline: commits in last 90 days", False),
    "b_newest": ("Baseline: newest listing first", False),
    "b_prior_funding": ("Baseline: raised before (most recent first)", False),
    "leaky_stars_now": ("Reference: today's GitHub stars (LEAKAGE-EXPOSED, not a fair baseline)", True),
}
MODELS = ["s_logit_full", "s_logit_github", "s_heuristic"]


def load() -> pd.DataFrame:
    df = pd.read_parquet(FROZEN / "backtest_table.parquet")
    df = df[df["t0"].dt.date.isin(BACKTEST_T0S)].copy()
    df["raised"] = df["raised"].astype(int)
    return df.reset_index(drop=True)


def stable_random(slug: str, t0) -> float:
    # hash-based so the random baseline is identical on every run and machine
    return int(hashlib.sha256(f"{slug}|{t0}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF


def add_scores(df: pd.DataFrame) -> tuple[pd.DataFrame, list, dict]:
    df = df.copy()
    df["s_heuristic"] = sc.heuristic(df)
    df["b_random"] = [stable_random(s, t) for s, t in zip(df["slug"], df["t0"], strict=True)]
    df["b_tvl"] = df["tvl_t0"]
    df["b_commits"] = df["commits_90d"] + 1e-6 * df["commits_before"]  # tie-break by history
    df["b_newest"] = -df["listing_age_days"]
    df["b_prior_funding"] = (df["prior_raises"] > 0) + 1 / (1 + df["days_since_last_raise"].fillna(1e6) / 365)
    df["s_logit_full"] = np.nan
    df["s_logit_github"] = np.nan
    test_t0s = []
    for t0 in sorted(df["t0"].unique()):
        train = df[df["outcome_end"] <= t0]  # only windows that had fully closed by this T0
        if train["t0"].nunique() == 0 or train["raised"].sum() < 5:
            continue
        test_t0s.append(pd.Timestamp(t0))
        mask = df["t0"] == t0
        for col, feats in (("s_logit_full", sc.FULL_FEATURES), ("s_logit_github", sc.GITHUB_FEATURES)):
            df.loc[mask, col] = sc.predict(sc.fit_logit(train, feats), df[mask], feats)
    # final models on every backtest T0: the coefficients are reported and the GitHub one is used live
    coefs = {name: sc.coefficients(sc.fit_logit(df, feats), feats)
             for name, feats in (("logit_full", sc.FULL_FEATURES), ("logit_github", sc.GITHUB_FEATURES))}
    return df, test_t0s, coefs


def run(n_boot: int = 1000) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    df, test_t0s, coefs = add_scores(load())
    test = df[df["t0"].isin(test_t0s)].reset_index(drop=True)
    cols = list(SCORERS)

    point = averaged(test, cols)
    non_leaky_baselines = [c for c in cols if c.startswith("b_")]
    best_base = max(non_leaky_baselines, key=lambda c: point[c]["auc"])

    def stat(sample: pd.DataFrame) -> dict[str, float]:
        a = averaged(sample, cols)
        flat = {f"{c}|{m}": v for c, d in a.items() for m, v in d.items()}
        for m in MODELS:  # paired difference vs the best naive baseline, on the same resample
            flat[f"{m}|auc_minus_best_baseline"] = a[m]["auc"] - a[best_base]["auc"]
        return flat

    cis = cluster_bootstrap(test, stat, n_boot=n_boot)
    per_t0 = {c: [] for c in cols}
    for t0, g in test.groupby("t0"):
        for c in cols:
            m = per_t0_metrics(g["raised"].to_numpy(int), g[c].to_numpy(float))
            per_t0[c].append({"t0": str(t0.date()), **{k: round(v, 4) for k, v in m.items()}})

    scores = {}
    for c, (label, leaky) in SCORERS.items():
        scores[c] = {"label": label, "leakage_exposed": leaky}
        for m in ("auc", "p@20", "p@50", "lift@50"):
            scores[c][m] = round(point[c][m], 4)
            scores[c][f"{m}_ci95"] = [round(x, 4) for x in cis[f"{c}|{m}"]]
    paired = {m: {"best_baseline": best_base,
                  "auc_diff": round(point[m]["auc"] - point[best_base]["auc"], 4),
                  "ci95": [round(x, 4) for x in cis[f"{m}|auc_minus_best_baseline"]]} for m in MODELS}

    last = test[test["t0"] == max(test_t0s)].sort_values("s_logit_full", ascending=False).head(20)
    result = {
        "description": "Walk-forward point-in-time backtest: does the screening score rank protocols that "
                       "announce a VC raise within 12 months of T0 above those that do not?",
        "outcome": "any DefiLlama raise dated in [T0, T0+12 months)",
        "all_t0s": [str(t.date()) for t in sorted(df["t0"].unique())],
        "test_t0s": [str(t.date()) for t in test_t0s],
        "n_rows_test": int(len(test)), "n_positives_test": int(test["raised"].sum()),
        "n_protocols_test": int(test["slug"].nunique()),
        "base_rate_test": round(float(test["raised"].mean()), 4),
        "n_bootstrap": n_boot, "bootstrap": "clustered by protocol",
        "scores": scores, "paired_vs_best_baseline": paired, "per_t0": per_t0,
        "coefficients_all_t0": coefs,
        "top20_last_test_t0": [{"name": r.name, "category": r.category, "score": round(r.s_logit_full, 4),
                                "raised_within_12m": bool(r.raised), "leads": r.leads if isinstance(r.leads, str) else None}
                               for r in last.itertuples()],
    }
    (OUT / "backtest.json").write_text(json.dumps(result, indent=2) + "\n")
    test[["t0", "slug", "name", "raised"] + cols].to_csv(OUT / "scores_test.csv", index=False)
    print(json.dumps({c: {k: scores[c][k] for k in ("auc", "auc_ci95", "p@50", "lift@50")} for c in cols},
                     indent=1))
    print("paired:", json.dumps(paired))
    return result
