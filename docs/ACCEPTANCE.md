# Acceptance criteria

Written 2026-11-02 **before** the main build; targets unchanged since. Each row is marked with the command
and an output excerpt. A missed target is reported with its real number.

| # | Criterion (measurable) | Target | Status | Evidence |
|---|---|---|---|---|
| A1 | Live public sources pulled with a provenance manifest (url, fetched_at, sha256) | >= 6 sources | PASS | `results/data_manifest.json`: 9 sources, 4,131 files (arxiv, coingecko, defillama, geckoterminal, github, hn_algolia, x402_foundation_feed, x402scan, yc_directory); `tests/test_manifest.py` |
| A2 | Backtest sample size pooled over walk-forward test T0s | >= 1,000 rows and >= 50 positives | PASS | `backtest.json`: n_rows_test 4,655, n_positives_test 80, 5 test T0s |
| A3 | Point-in-time: features unchanged when rows dated >= T0 are injected | test passes | PASS | `tests/test_point_in_time.py::test_poisoned_future_rows_change_nothing` |
| A4 | Score AUC vs best naive baseline, 95% protocol-clustered bootstrap CI | score AUC > best baseline AUC | **FAIL** (all protocols: higher point estimate, not significant; never-raised: below the best baseline, see A17) | logit_full 0.810 (0.725-0.886) vs "raised before" 0.773; paired diff +0.036, CI -0.022 to +0.100 includes 0. Per ADR 0004 reported as not distinguishable |
| A5 | Precision@20 per test T0 vs base rate | lift > 1.5x | PASS | logit_full precision@20 per T0: 0.15, 0.20, 0.20, 0.20, 0.15 vs base rates 1.1%-3.0% (lift 5x-15x); lift@50 9.0x averaged |
| A6 | LLM judgment only where it cannot know the outcome; leakage-exposed items flagged | anonymized arm or probed post-cutoff only | PASS (revised) | Round 1 cited a hard-coded flag and a wrong "4 of 8" count; both removed. Now: anonymized walk-forward set (400 items, 80 positives) + post-cutoff set whose window starts after the PROBED cutoffs (Claude 2025-12-11, GPT 2025-09-29; `cutoff_probe.json`); raise mentions by explicit rule: 1 of 8 positives, 2 of 112 negatives |
| A7 | Claim-level citation precision of shipped memos | >= 0.95 after the gate; raw reported | **Withdrawn as a metric** | "After the gate" is 1.0 by construction. Reported instead: first-draft verifier pass 57.3% (stricter verifier v2) and critic-entailed 31.1% of 103 claims (68 tagged partial, 3 withheld) |
| A8 | Verifier catches injected corruptions; no false rejects on gold | >= 95% caught, 0 false rejects | PASS but demoted | `verifier_eval.json` passes (0 false rejects, all corruptions caught), but its claim text is a placeholder, so it only tests citation mechanics. Replaced as evidence by A18 |
| A9 | Memos critiqued by a different model family; disagreements -> decision cards | 100% critiqued | PASS | 8/8 memos drafted by claude-sonnet-5-5 and critiqued blind by gpt-6.1-sol; decision cards only on a policy-recommendation difference or a 2+ point gap: 0 cards in the final run (the first version fired on every flag: 8/8, since fixed) |
| A10 | Changepoint event hit rate within +/-7 days | >= 0.5 and above null, p < 0.05 | **FAIL** | headline series: hit rate 0.42 vs null 0.36, p = 0.44 (12 changepoints, 12 events). Sensitivity: 0.5x penalty 0.42 (p 0.59), 2x penalty 0.17 (p 0.87) |
| A11 | Changepoint false-alarm rate lower than naive z-score detector | lower | **FAIL** | PELT 0.67 vs z-score 0.57 |
| A12 | Weekly brief: every shipped inflection claim passes the verifier | 100% | PASS | `results/briefs/2026-11-01.json`: 16 drafted, 81.2% first pass, 16 shipped after repair; all 8 inflections flagged `needs human` (low confidence, no explaining event) |
| A13 | Strict replay reproduces all committed LLM outputs with zero model calls | `make replay` exits 0 | PASS | `make replay`: sourcing-run 0 real / 23 cached, llm-eval 0 real, brief 0 real / 2 cached; `git diff --exit-code -- results` clean. Also passes in a fresh clone with VAIOS_STRICT_REPLAY=1 VAIOS_MAX_CALLS=0 |
| A14 | Budget: LLM calls / disk | < 400 calls / < 3 GB | PASS | ledger 131 calls in total (52 in round 0, 79 in round 1) + 6 untracked setup probes; repo about 0.7 GB, of which .venv is 579 MB |
| A15 | `make check` runtime offline | < 120 s | PASS | ~80 s locally (ruff, 78 tests, 3 regeneration checks) |
| A16 | README headline numbers equal committed results | drift test passes | PASS | `tests/test_readme_numbers.py` (every string from `vaios.report.headline_numbers()` appears verbatim) |

## Round-1 additions (written before the re-runs)

| # | Criterion | Target | Status | Evidence |
|---|---|---|---|---|
| A23 | Round-2 correctness: live triage order, 30-day window boundaries, raise rule within shown text, fail-closed labels, free-text numbers | tests pass | PASS | ADR 0010; `tests/test_windows.py` (PayAI 441,602 in [Oct 2, Nov 1) vs 462,019 over 32 days in round 1); raise rule 0 of 8 / 0 of 112 within the 300 characters shown; `tests/test_critique.py`, `tests/test_llm_judgment.py` |
| A17 | Seed-relevant screening: never-raised population reported first, with round mix and lead time | reported; target: a score beats the best naive baseline | **FAIL** | never-raised: 28 positive rows / 18 protocols / 22 raises (5 seed-type); heuristic 0.688 (0.57-0.83), logistic 0.605, best baseline "newest listing" 0.697; heuristic minus baseline CI -0.072 to +0.058 |
| A18 | Claim-level eval on real memo claims with labelled perturbations | recall reported per type for verifier and critic | PASS | `claim_eval.json` (final run): 60 originals + 100 perturbations. Verifier: 100% on number and date changes, 0% on entity and qualifier changes. Critic, lenient (any non-entails): 100% on all four. Critic, strict (withhold only): 100% number, 100% date, 0% entity (all 3 labelled partial, so they ship tagged), 2% qualifier. The critic flags 83% of originals; its precision is pending human labels; no kappa |
| A19 | Investability: known late-stage names excluded with stored evidence | Tempo, Merit, Kite excluded | PASS | `stage_checks.json`: 40 checked, 4 excluded (Tempo, Merit Systems, Kite, QuickNode) with snapshot doc_ids |
| A20 | Calibrated committee: advance budget and cards only on real disagreement | <= 2 advance; cards only on rec diff or 2+ gap | PASS | Round 2: recommendations are a pure function of the scores (same scores give the same call), with an evidence gate (< 25% entailed means "evidence insufficient", which blocks advance) and the critic held to the same policy. Final: 0 advance / 7 watch / 1 pass; 0 cards; `tests/test_critique.py::test_recommendations_follow_the_score_policy` |
| A21 | Human verdicts and flag labels | tooling ready; none fabricated | PASS (tooling) / **PENDING** (labels) | `vaios.decide status`: 8 memos awaiting a human verdict, 0 recorded; 22-row flag sample, 0 labelled |
| A22 | Gates fail closed | `make check` fails if a committed result stops regenerating; pipeline fails on any company failure | PASS | `make acceptance` (`scripts/regen_check.sh` on backtest, verifier eval, sourcing run); `VAIOS_MAX_JOB_FAILURES` default 0 |

Exploratory monitoring diagnostics (ADR 0009, no targets): 8 of 12 events needed for p < 0.05 (power 72% at a
true 70% hit rate); median real-time detection delay 1 week, 3 alarms later dropped; at matched alarm count
PELT's false-alarm rate is 67% vs 75% for the z-score detector; event list v2 with 51 token launches: hit rate
44% vs 32% (p = 0.03), post hoc.

Summary: 18 PASS (A7 withdrawn, A8 demoted), 4 FAIL (A4, A10, A11, A17), and 1 pending human step (A21 labels).
The failures are real results, documented in the README. None was fixed by changing a target or method after the fact.
