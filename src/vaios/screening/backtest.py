"""`make backtest`: walk-forward, point-in-time evaluation of the screening score against revealed VC decisions.

Input: results/frozen/backtest_table.parquet (features as of each T0 + the raise outcome in [T0, T0+12m)).
Output: results/backtest/backtest.json (+ per-T0 CSV). Spec: docs/decisions/0004.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from vaios.config import BACKTEST_T0S, FROZEN, RESULTS
from vaios.screening import score as sc
from vaios.screening.metrics import averaged, cluster_bootstrap, per_t0_metrics, pooled_auc

OUT = RESULTS / "backtest"

SCORERS = {  # column -> (label, leakage-exposed?)
    "s_logit_full": ("Logistic, all point-in-time features (walk-forward)", False),
    "s_logit_github": ("Logistic, GitHub-only features (walk-forward; live niche score)", False),
    "s_heuristic": ("Pre-specified heuristic (no fitting)", False),
    "s_heuristic_github": ("Heuristic, GitHub signals only (post-hoc variant, ADR 0010)", False),
    "b_random": ("Baseline: random", False),
    "b_tvl": ("Baseline: TVL size", False),
    "b_commits": ("Baseline: commits in last 90 days (live triage order, ADR 0010)", False),
    "b_newest": ("Baseline: newest listing first", False),
    "b_prior_funding": ("Baseline: raised before (most recent first)", False),
    "leaky_stars_now": ("Reference: today's GitHub stars (LEAKAGE-EXPOSED, not a fair baseline)", True),
}
MODELS = ["s_logit_full", "s_logit_github", "s_heuristic", "s_heuristic_github"]


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
    df["s_heuristic_github"] = sc.heuristic_github(df)
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


def evaluate_block(test: pd.DataFrame, n_boot: int, cluster: str = "slug") -> dict:
    """All metrics for one evaluation population: point estimates (mean over test T0s), pooled AUC,
    protocol-clustered CIs, and the paired AUC difference of each model vs the best naive baseline."""
    cols = list(SCORERS)
    point = averaged(test, cols)
    best_base = max([c for c in cols if c.startswith("b_")], key=lambda c: point[c]["auc"])

    def stat(sample: pd.DataFrame) -> dict[str, float]:
        a = averaged(sample, cols)
        flat = {f"{c}|{m}": v for c, d in a.items() for m, v in d.items()}
        for m in MODELS:  # paired difference vs the best naive baseline, on the same resample
            flat[f"{m}|auc_minus_best_baseline"] = a[m]["auc"] - a[best_base]["auc"]
        return flat

    cis = cluster_bootstrap(test, stat, n_boot=n_boot, cluster=cluster)
    scores = {}
    for c, (label, leaky) in SCORERS.items():
        scores[c] = {"label": label, "leakage_exposed": leaky, "pooled_auc": round(pooled_auc(test, c), 4)}
        for m in ("auc", "p@20", "p@50", "lift@50"):
            scores[c][m] = round(point[c][m], 4)
            scores[c][f"{m}_ci95"] = [round(x, 4) for x in cis[f"{c}|{m}"]]
    paired = {m: {"best_baseline": best_base,
                  "auc_diff": round(point[m]["auc"] - point[best_base]["auc"], 4),
                  "ci95": [round(x, 4) for x in cis[f"{m}|auc_minus_best_baseline"]]} for m in MODELS}
    pos = test[test["raised"] == 1]
    return {"n_rows": int(len(test)), "n_positive_rows": int(len(pos)),
            "n_positive_protocols": int(pos["slug"].nunique()), "n_protocols": int(test["slug"].nunique()),
            "base_rate": round(float(test["raised"].mean()), 4), "cluster": cluster,
            "scores": scores, "paired_vs_best_baseline": paired}


def round_mix(test: pd.DataFrame) -> dict:
    """Which distinct raises sit behind the positive rows (overlapping windows count one raise twice)."""
    raises = pd.read_parquet(FROZEN / "raises.parquet")
    rows = []
    for r in test[test["raised"] == 1].itertuples():
        end = r.outcome_end
        hit = raises[(raises["slug"] == r.slug) & (raises["raise_date"] >= r.t0) & (raises["raise_date"] < end)]
        rows.append(hit)
    hits = pd.concat(rows).drop_duplicates(["slug", "raise_date", "round"])
    rnd = hits["round"].fillna("unspecified").str.strip()
    seedish = rnd.str.contains("seed|angel", case=False)
    return {"distinct_raises": int(len(hits)), "distinct_protocols": int(hits["slug"].nunique()),
            "seed_preseed_angel": int(seedish.sum()),
            "by_round": {k: int(v) for k, v in rnd.value_counts().sort_index().items()},
            "protocols_positive_at_2plus_t0s": int((test[test["raised"] == 1].groupby("slug").size() >= 2).sum())}


def lead_time() -> dict:
    """For protocols with a recorded first raise: when could a public-data system first have seen them?
    Signals: first public GitHub repo of today's owner (retrospective: deleted repos are invisible) and the
    DefiLlama listing date (when the backtest universe can include it). Real dates only."""
    d = pd.read_parquet(FROZEN / "protocol_dates.parquet").dropna(subset=["first_raise_at"])
    months = lambda a, b: (a - b).dt.days / 30.44  # noqa: E731
    gh = months(d["first_raise_at"], d["first_repo_at"]).dropna()
    dl = months(d["first_raise_at"], d["listed_at_eff"]).dropna()
    first_signal = d[["first_repo_at", "listed_at_eff"]].min(axis=1)
    fs = months(d["first_raise_at"], first_signal).dropna()
    q = lambda x: {"n": int(len(x)), "median_months": round(float(x.median()), 1),  # noqa: E731
                   "share_signal_before_raise": round(float((x > 0).mean()), 3)}
    top = pd.read_parquet(FROZEN / "top_repos.parquet").merge(d[["github_owner", "first_raise_at"]],
                                                              left_on="owner", right_on="github_owner")
    after = float((top["repo_created_at"] > top["first_raise_at"]).mean())
    years = d["first_raise_at"].dt.year
    return {"github_first_repo": q(gh), "defillama_listing": q(dl), "earliest_public_signal": q(fs),
            "share_of_todays_top5_repos_created_after_first_raise": round(after, 3),
            "share_first_raises_2020_2022": round(float(years.between(2020, 2022).mean()), 3),
            "note": "positive months = a public GitHub signal (today's repos) or listing existed BEFORE the first "
                    "raise. Repo creation is not when a repo went public, nor when a system would have surfaced "
                    "the company; deleted repos are invisible; about half of these first raises are 2020-22 DeFi."}


def run(n_boot: int = 1000) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    df, test_t0s, coefs = add_scores(load())
    test = df[df["t0"].isin(test_t0s)].reset_index(drop=True)
    cols = list(SCORERS)
    never = test[test["prior_raises"] == 0].reset_index(drop=True)
    blocks = {
        "never_raised": evaluate_block(never, n_boot),          # the seed-relevant population: headline
        "all": evaluate_block(test, n_boot),
        "all_owner_clustered": evaluate_block(test, n_boot, cluster="github_owner"),
        "never_raised_owner_clustered": evaluate_block(never, n_boot, cluster="github_owner"),
        # selection sensitivity: rows whose GitHub owner no longer resolves (deleted/renamed) look inactive
        "all_gh_found_only": evaluate_block(test[test["gh_found"]].reset_index(drop=True), n_boot),
        "never_raised_gh_found_only": evaluate_block(never[never["gh_found"]].reset_index(drop=True), n_boot),
    }
    per_t0 = {c: [] for c in cols}
    for t0, g in test.groupby("t0"):
        for c in cols:
            m = per_t0_metrics(g["raised"].to_numpy(int), g[c].to_numpy(float))
            per_t0[c].append({"t0": str(t0.date()), **{k: round(v, 4) for k, v in m.items()}})
    allb = blocks["all"]
    last = test[test["t0"] == max(test_t0s)].sort_values("s_logit_full", ascending=False).head(20)
    result = {
        "description": "Walk-forward point-in-time backtest (retrospective reconstruction, see ADR 0003): does "
                       "the screening score rank protocols that announce a raise within 12 months of T0 above "
                       "those that do not? Headline population: protocols that had never raised before T0.",
        "outcome": "any DefiLlama raise dated in [T0, T0+12 months); for never-raised protocols this is their "
                   "first recorded raise",
        "metric_definitions": "auc / p@k / lift@50 = mean over test T0s of the per-T0 value; pooled_auc = one "
                              "AUC over all rows; CIs: 1,000 bootstrap resamples clustered by protocol (or owner)",
        "all_t0s": [str(t.date()) for t in sorted(df["t0"].unique())],
        "test_t0s": [str(t.date()) for t in test_t0s],
        "n_rows_test": allb["n_rows"], "n_positives_test": allb["n_positive_rows"],
        "n_positive_protocols_test": allb["n_positive_protocols"],
        "n_protocols_test": allb["n_protocols"], "base_rate_test": allb["base_rate"],
        "n_bootstrap": n_boot,
        "scores": allb["scores"], "paired_vs_best_baseline": allb["paired_vs_best_baseline"],
        "populations": blocks,
        "round_mix_all": round_mix(test), "round_mix_never_raised": round_mix(never),
        "lead_time": lead_time(),
        "selection": {
            "note": "retrospective reconstruction: universe membership, GitHub owner and top-5 repos are TODAY's; "
                    "owners that no longer resolve contribute zero commits (ADR 0003)",
            "gh_found_rate_positives": round(float(test.loc[test["raised"] == 1, "gh_found"].mean()), 4),
            "gh_found_rate_negatives": round(float(test.loc[test["raised"] == 0, "gh_found"].mean()), 4)},
        "per_t0": per_t0, "coefficients_all_t0": coefs,
        "top20_last_test_t0": [{"name": r.name, "category": r.category, "score": round(r.s_logit_full, 4),
                                "raised_within_12m": bool(r.raised), "prior_raises": int(r.prior_raises),
                                "leads": r.leads if isinstance(r.leads, str) else None}
                               for r in last.itertuples()],
    }
    (OUT / "backtest.json").write_text(json.dumps(result, indent=2) + "\n")
    test[["t0", "slug", "name", "raised", "prior_raises"] + cols].to_csv(OUT / "scores_test.csv", index=False)
    for name, b in blocks.items():
        print(name, b["n_rows"], b["n_positive_rows"], b["n_positive_protocols"],
              {c: (b["scores"][c]["auc"], b["scores"][c]["auc_ci95"]) for c in cols})
    print(json.dumps({k: result[k] for k in ("round_mix_all", "round_mix_never_raised", "lead_time")}, indent=1))
    return result
