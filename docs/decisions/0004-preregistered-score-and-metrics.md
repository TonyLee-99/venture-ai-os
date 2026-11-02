# 0004. Pre-registered screening score, baselines and metrics (fixed before the first backtest run)

Status: accepted 2026-11-02, committed before `make backtest` was ever run (see git log order).

## Scores (all deterministic, point-in-time)
1. `heuristic` (no fitting): mean within-T0 percentile rank of commits in the last 90 days, commit growth
   (last 90 vs prior 90 days, log ratio), TVL growth over 90 days, TVL at T0, and newness (minus listing age).
2. `logit_full`: L2 logistic regression (C=0.5, standardised) on all point-in-time features, walk-forward.
3. `logit_github`: the same on the five GitHub features only (the live niche score).

## Baselines
Random; TVL size; commit activity (last 90 days); newest listing; prior funding (has raised before, most
recent first); and today's total stars, which is **leakage-exposed** (no star history exists) and is shown
only as a reference ceiling-style comparison, never as a fair baseline.

## Metrics
Per test T0, then averaged over test T0s: ROC AUC, precision@20 and @50, lift@50 (precision / base rate),
Spearman rank correlation of score with the outcome. 95% CIs from 1,000 bootstrap resamples **clustered by
protocol** (the same protocol appears at several T0s, so rows are not independent). The headline comparison
is the paired bootstrap CI of (score AUC minus best non-leaky baseline AUC).

## What would count as failure
If the paired CI of the AUC difference includes zero, the README says the score is not distinguishable from
the best naive baseline. No re-weighting of the heuristic after seeing results.
