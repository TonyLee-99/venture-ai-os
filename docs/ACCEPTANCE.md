# Acceptance criteria

Written 2026-11-02 **before** the main build. Targets are fixed here; at the end each line is marked PASS or
FAIL with the command and an output excerpt. A missed target is reported with its real number.

| # | Criterion (measurable) | Target | Status | Evidence |
|---|---|---|---|---|
| A1 | Live public sources pulled with a provenance manifest (url, fetched_at, sha256) | >= 6 sources | pending | |
| A2 | Backtest sample size (entity x T0 rows / positive outcomes, pooled over walk-forward test T0s) | >= 1,000 rows and >= 50 positives | pending | |
| A3 | Point-in-time correctness: features at T0 unchanged when rows dated >= T0 are injected | test passes | pending | |
| A4 | Screening score vs best naive baseline on held-out T0s: AUC with 95% entity-clustered bootstrap CI | report; target: score AUC > best baseline AUC | pending | |
| A5 | Screening precision@20 per test T0 vs base rate | report; target: lift > 1.5x base rate | pending | |
| A6 | LLM judgment evaluated only on outcomes after the assumed model cutoff (2026-06-30); leakage-exposed items flagged | 100% of evaluated items post-cutoff | pending | |
| A7 | Claim-level citation precision of shipped memos (claims whose quoted span is found in the cited snapshot and whose numbers match the warehouse) | >= 0.95 after the verification gate; raw pre-gate precision reported | pending | |
| A8 | Receipt verifier catches injected corruptions (fake quote, wrong number, wrong source) | >= 95% caught, 0 false rejects on the gold set | pending | |
| A9 | Cross-critique coverage: memos critiqued by a different model family; disagreements become decision cards | 100% of memos | pending | |
| A10 | Changepoint event hit rate within +/-7 days on pre-registered dated events | >= 0.5 and above permutation null (p < 0.05) | pending | |
| A11 | Changepoint false-alarm rate (changepoints with no event within +/-7 days) | report; lower than naive z-score detector | pending | |
| A12 | Weekly brief: every inflection has receipts that pass the verifier | 100% | pending | |
| A13 | Strict replay reproduces all committed LLM outputs with zero model calls | `make replay` exits 0 | pending | |
| A14 | Budget: total real LLM calls (ledger) / disk used by the project | < 400 calls / < 3 GB | pending | |
| A15 | `make check` runtime offline | < 120 s | pending | |
| A16 | README headline numbers equal committed results | drift test passes | pending | |
