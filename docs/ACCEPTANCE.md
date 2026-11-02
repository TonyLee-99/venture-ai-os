# Acceptance criteria

Written 2026-11-02 **before** the main build (commit 38188de); targets unchanged since. Marked at the end of
session 1 with the command and an output excerpt. A missed target is reported with its real number.

| # | Criterion (measurable) | Target | Status | Evidence |
|---|---|---|---|---|
| A1 | Live public sources pulled with a provenance manifest (url, fetched_at, sha256) | >= 6 sources | PASS | `results/data_manifest.json`: 8 sources, 4,031 files (arxiv, coingecko, defillama, github, hn_algolia, x402_foundation_feed, x402scan, yc_directory); `tests/test_manifest.py` |
| A2 | Backtest sample size pooled over walk-forward test T0s | >= 1,000 rows and >= 50 positives | PASS | `backtest.json`: n_rows_test 4,655, n_positives_test 80, 5 test T0s |
| A3 | Point-in-time: features unchanged when rows dated >= T0 are injected | test passes | PASS | `tests/test_point_in_time.py::test_poisoned_future_rows_change_nothing` |
| A4 | Score AUC vs best naive baseline, 95% protocol-clustered bootstrap CI | score AUC > best baseline AUC | **FAIL** (all protocols: higher point estimate, not significant; never-raised: below the best baseline, see A17) | logit_full 0.810 (0.725-0.886) vs "raised before" 0.773; paired diff +0.036, CI -0.022 to +0.100 includes 0. Per ADR 0004 reported as not distinguishable |
| A5 | Precision@20 per test T0 vs base rate | lift > 1.5x | PASS | logit_full precision@20 per T0: 0.15, 0.20, 0.20, 0.20, 0.15 vs base rates 1.1%-3.0% (lift 5x-15x); lift@50 9.0x averaged |
| A6 | LLM judgment only where it cannot know the outcome; leakage-exposed items flagged | anonymized arm or probed post-cutoff only | PASS (revised) | Round 1 cited a hard-coded flag and a wrong "4 of 8" count; both removed. Now: anonymized walk-forward set (400 items, 80 positives) + post-cutoff set whose window starts after the PROBED cutoffs (Claude 2025-12-11, GPT 2025-09-29; `cutoff_probe.json`); raise mentions by explicit rule: 1 of 8 positives, 2 of 112 negatives |
| A7 | Claim-level citation precision of shipped memos | >= 0.95 after the gate; raw reported | **Withdrawn as a metric** | "After the gate" is 1.0 by construction. Reported instead: first-draft verifier pass 57.3% (stricter verifier v2) and critic-entailed 31.1% of 103 claims (68 tagged partial, 3 withheld) |
| A8 | Verifier catches injected corruptions; no false rejects on gold | >= 95% caught, 0 false rejects | PASS but demoted | `verifier_eval.json` passes (0 false rejects, all corruptions caught), but its claim text is a placeholder, so it only tests citation mechanics. Replaced as evidence by A18 |
| A9 | Memos critiqued by a different model family; disagreements -> decision cards | 100% | PASS | 8/8 memos drafted by claude-sonnet-5-5, critiqued by gpt-6.1-sol; 8 decision cards; `tests/test_critique.py` |
| A10 | Changepoint event hit rate within +/-7 days | >= 0.5 and above null, p < 0.05 | **FAIL** | headline series: hit rate 0.42 vs null 0.36, p = 0.44 (12 changepoints, 12 events). Sensitivity: 0.5x penalty 0.42 (p 0.59), 2x penalty 0.17 (p 0.87) |
| A11 | Changepoint false-alarm rate lower than naive z-score detector | lower | **FAIL** | PELT 0.67 vs z-score 0.57 |
| A12 | Weekly brief: every shipped inflection claim passes the verifier | 100% | PASS | `results/briefs/2026-11-01.json`: 16 drafted, 81.2% first pass, 16 shipped after repair; all 8 inflections flagged `needs human` (low confidence, no explaining event) |
| A13 | Strict replay reproduces all committed LLM outputs with zero model calls | `make replay` exits 0 | PASS | `make replay`: sourcing-run 0 real / 23 cached, llm-eval 0 real, brief 0 real / 2 cached; `git diff --exit-code -- results` clean. Also passes in a fresh clone with VAIOS_STRICT_REPLAY=1 VAIOS_MAX_CALLS=0 |
| A14 | Budget: LLM calls / disk | < 400 calls / < 3 GB | PASS | ledger 131 calls in total (52 in round 0, 79 in round 1) + 6 untracked setup probes; repo about 0.7 GB, of which .venv is 579 MB |
| A15 | `make check` runtime offline | < 120 s | PASS | ~22 s locally (58 tests + 17 feature verifications) |
| A16 | README headline numbers equal committed results | drift test passes | PASS | `tests/test_readme_numbers.py` (every string from `vaios.report.headline_numbers()` appears verbatim) |

## Second-iteration additions (written before the re-runs)

| # | Criterion | Target | Status | Evidence |
|---|---|---|---|---|
| A17 | Seed-relevant screening: never-raised population reported first, with round mix and lead time | reported; target: a score beats the best naive baseline | **FAIL** | never-raised: 28 positive rows / 18 protocols / 22 raises (5 seed-type); heuristic 0.688 (0.57-0.83), logistic 0.605, best baseline "newest listing" 0.697; heuristic minus baseline CI -0.072 to +0.058 |
| A18 | Claim-level eval on real memo claims with labelled perturbations | recall reported per type for verifier and critic | PASS | `claim_eval.json`: 60 originals + 109 perturbations; verifier 100% on number/date changes, 0% on entity/qualifier; critic 100% on all four; critic flags 82% of originals (precision pending human labels) |
| A19 | Investability: known late-stage names excluded with stored evidence | Tempo, Merit, Kite excluded | PASS | `stage_checks.json`: 40 checked, 4 excluded (Tempo, Merit Systems, Kite, QuickNode) with snapshot doc_ids |
| A20 | Calibrated committee: advance budget and cards only on real disagreement | <= 2 advance; cards only on rec diff or 2+ gap | PASS | 0 advance / 6 watch / 2 pass; 3 cards |
| A21 | Human verdicts and flag labels | tooling ready; none fabricated | PASS (tooling) / **PENDING** (labels) | `vaios.decide status`: 3 cards, 0 human decisions; 17-row flag sample, 0 labelled |
| A22 | Harness fails closed | verify exits non-zero on any open feature; pipeline fails on any company failure | PASS | `tests/test_harness.py::test_verify_fails_closed_on_open_features`; `VAIOS_MAX_JOB_FAILURES` default 0 |

Exploratory monitoring diagnostics (ADR 0009, no targets): 8 of 12 events needed for p < 0.05 (power 72% at a
true 70% hit rate); median real-time detection delay 1 week, 3 alarms later dropped; at matched alarm count
PELT's false-alarm rate is 67% vs 75% for the z-score detector; event list v2 with 51 token launches: hit rate
44% vs 32% (p = 0.03), post hoc.

Summary: 17 PASS (A7 withdrawn, A8 demoted), 4 FAIL (A4, A10, A11, A17), and 1 pending human step (A21 labels).
The failures are real results, documented in the README. None was fixed by changing a target or method after the fact.
