# 0004. Screening score, baselines and metrics: spec committed before the first backtest run

Status: accepted 2026-11-02. Committed before `make backtest` was first run (git log order), but AFTER the raw
data had been pulled and its shape inspected, so this is a committed spec, not a pre-registration in the
clinical-trial sense. Amended in round 1 (see "Amendment" below).

## Scores (all deterministic, point-in-time)
1. `heuristic` (no fitting, specified before any result was seen): mean within-T0 percentile rank of commits in the last 90 days, commit growth
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

## Amendment (round 1, 2026-11-02)
- Headline population changed to protocols that had **never raised before T0** (the seed-relevant case); on the
  full population, "raised before" dominates. Both are reported; no model is picked as headline because it won:
  all three scores and all baselines are shown side by side.
- Units: "80 positive protocol x T0 rows from 44 protocols (58 distinct raises)"; AUC and lift are means of
  per-T0 values, pooled AUC is reported next to them. CIs: protocol-clustered, with an owner-clustered
  sensitivity check; predictions are held fixed inside the bootstrap.
