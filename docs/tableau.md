# Tableau Public workbook (intended design)

The repo ships Tableau-ready extracts in `extracts/` (built by `make extracts` from committed results). No
`.twb` file is included: a workbook that was never opened in Tableau would be fake. This is the build sheet.

| Extract | Grain | Use |
|---|---|---|
| `backtest_by_t0.csv` | scorer x test T0 | AUC / precision@k / lift by scorer over time |
| `backtest_scores_by_protocol.csv` | protocol x T0 | drill from a T0 into the ranked list and its raises |
| `x402_daily_by_chain.csv` | day x chain | traction lines (log scale), Base vs Solana |
| `x402_daily_by_facilitator.csv` | day x facilitator | comparable-company traction |
| `changepoints.csv`, `events.csv` | changepoint / event | reference lines and event markers on the traction view |
| `sourcing_candidates.csv`, `memos.csv` | entity | pipeline funnel and memo scores (drafter vs critic) |

Sheets
1. **Screening vs baselines**: dot plot of AUC by scorer (color = our score / best baseline / other), filter on T0.
2. **Traction monitor**: weekly x402 transactions (log), reference lines from `changepoints.csv`, shapes from
   `events.csv`; parameter to switch series (all / Base / Solana / facilitator).
3. **Pipeline**: candidates by source -> relevant -> investable -> shortlisted -> memo -> decision card.
4. **Memo review**: drafter vs critic PMF / Narrative / Execution, highlight rows with disagreements.

Dashboard: sheets 1 and 2 side by side with the same KPI row as `dashboard/index.html`.
