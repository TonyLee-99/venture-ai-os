# Acceptance criteria

Written 2026-11-02 **before** the main build (commit 38188de); targets unchanged since. Marked at the end of
session 1 with the command and an output excerpt. A missed target is reported with its real number.

| # | Criterion (measurable) | Target | Status | Evidence |
|---|---|---|---|---|
| A1 | Live public sources pulled with a provenance manifest (url, fetched_at, sha256) | >= 6 sources | PASS | `results/data_manifest.json`: 8 sources, 4,031 files (arxiv, coingecko, defillama, github, hn_algolia, x402_foundation_feed, x402scan, yc_directory); `tests/test_manifest.py` |
| A2 | Backtest sample size pooled over walk-forward test T0s | >= 1,000 rows and >= 50 positives | PASS | `backtest.json`: n_rows_test 4,655, n_positives_test 80, 5 test T0s |
| A3 | Point-in-time: features unchanged when rows dated >= T0 are injected | test passes | PASS | `tests/test_point_in_time.py::test_poisoned_future_rows_change_nothing` |
| A4 | Score AUC vs best naive baseline, 95% protocol-clustered bootstrap CI | score AUC > best baseline AUC | **FAIL (point estimate higher, not significant)** | logit_full 0.810 (0.725-0.886) vs "raised before" 0.773; paired diff +0.036, CI -0.022 to +0.100 includes 0. Per ADR 0004 reported as not distinguishable |
| A5 | Precision@20 per test T0 vs base rate | lift > 1.5x | PASS | logit_full precision@20 per T0: 0.15, 0.20, 0.20, 0.20, 0.15 vs base rates 1.1%-3.0% (lift 5x-15x); lift@50 9.0x averaged |
| A6 | LLM judgment only on outcomes after the assumed cutoff; leakage-exposed items flagged | 100% post-cutoff | PASS | `llm_judgment.json`: t0 2026-06-30, window to 2026-11-01, `all_outcomes_after_cutoff: true`, named arms `leakage_exposed: true`; 4 of 8 positives' current descriptions mention funding (reported) |
| A7 | Claim-level citation precision of shipped memos | >= 0.95 after the gate; raw reported | PASS | `run_summary.json`: raw (first draft) 0.887, after one repair round 1.000 (106/106 claims, 0 dropped, 0 withheld). Caveat: the critic flags 32 shipped claims as overreaching (ADR 0006) |
| A8 | Verifier catches injected corruptions; no false rejects on gold | >= 95% caught, 0 false rejects | PASS | `results/receipts/verifier_eval.json`: 266 gold spans, 0 false rejects; 500/500 corruptions caught (first run 498/500; fix disclosed in README) |
| A9 | Memos critiqued by a different model family; disagreements -> decision cards | 100% | PASS | 8/8 memos drafted by claude-sonnet-5-5, critiqued by gpt-6.1-sol; 8 decision cards; `tests/test_critique.py` |
| A10 | Changepoint event hit rate within +/-7 days | >= 0.5 and above null, p < 0.05 | **FAIL** | headline series: hit rate 0.42 vs null 0.36, p = 0.44 (12 changepoints, 12 events). Sensitivity: 0.5x penalty 0.42 (p 0.59), 2x penalty 0.17 (p 0.87) |
| A11 | Changepoint false-alarm rate lower than naive z-score detector | lower | **FAIL** | PELT 0.67 vs z-score 0.57 |
| A12 | Weekly brief: every shipped inflection claim passes the verifier | 100% | PASS | `results/briefs/2026-11-01.json`: 16 drafted, 81.2% first pass, 16 shipped after repair; all 8 inflections flagged `needs human` (low confidence, no explaining event) |
| A13 | Strict replay reproduces all committed LLM outputs with zero model calls | `make replay` exits 0 | PASS | `make replay`: sourcing-run 0 real / 23 cached, llm-eval 0 real, brief 0 real / 2 cached; `git diff --exit-code -- results` clean. Also passes in a fresh clone with VAIOS_STRICT_REPLAY=1 VAIOS_MAX_CALLS=0 |
| A14 | Budget: LLM calls / disk | < 400 calls / < 3 GB | PASS | ledger 52 calls (30 Claude, 22 GPT; Claude cost $1.29) + 6 untracked probe calls during setup; repo 695 MB of which .venv 579 MB, data 104 MB |
| A15 | `make check` runtime offline | < 120 s | PASS | ~22 s locally (58 tests + 17 feature verifications) |
| A16 | README headline numbers equal committed results | drift test passes | PASS | `tests/test_readme_numbers.py` (every string from `vaios.report.headline_numbers()` appears verbatim) |

Summary: 13 PASS, 3 FAIL (A4 not significant; A10 and A11 changepoint validation). The failures are real
results, documented in the README, not fixed by changing targets or methods after the fact.
