# 0010. Live triage order: commits in the last 90 days

Status: accepted (2026-11-02).

Round 1 ordered the live queue by the GitHub-only logistic model, which is the weakest scorer on never-raised
protocols (AUC 0.584). The best never-raised scorer, the pre-specified heuristic (0.688), needs DefiLlama TVL and
listing age, and most niche candidates are not DefiLlama protocols. Among the orderings a GitHub-only candidate
can be given, the never-raised backtest AUCs (`results/backtest/backtest.json`, `populations.never_raised`) are:
commits in the last 90 days 0.653; GitHub-only logit 0.584; the heuristic restricted to GitHub signals
(commits, commit growth, newness = minus the age of the oldest repo) 0.551.

Decision: the live queue is ordered by commits in the last 90 days (a baseline pre-specified in ADR 0004),
tie-broken by total commits. Picking it from three backtested options is a mild selection on the same data;
every one of them has a CI that includes 0.5, so the order is a reading list for a human, not a prediction.
The other two scores stay in `candidates.csv` as reference columns.
