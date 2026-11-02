# 0007. Handling LLM look-ahead leakage in screening evaluation

Status: accepted (2026-11-02).

## Problem
An LLM asked "will this protocol raise?" about a past date may simply remember that it did. Any backtest that
lets an LLM score pre-cutoff history measures memory, not judgment.

## Decision
1. The backtested screening score uses deterministic point-in-time features only (no LLM anywhere in it).
2. LLM judgment is evaluated on a separate set: features frozen at 2026-06-30 (the assumed knowledge cutoff of
   both models) and outcomes counted only from 2026-06-30 to 2026-11-01.
3. Two arms: `anonymized` (opaque id + features: no memorisation channel) and `named` (adds name, category and
   today's DefiLlama description). The description is a current snapshot that can mention post-T0 news, so the
   named arm is flagged leakage-exposed, and we count positives whose description mentions funding.

## Limits
Only 8 raises fall in the post-cutoff window, so every AUC there has a wide CI. If a model's true cutoff is
later than 2026-06-30 the anonymized arm is still clean but the named arm is not.

## Amendment
- Cutoffs are probed, not assumed (`results/backtest/cutoff_probe.json`): each model dates 18 events that have
  stored sources; Claude dated events through 2025-12, GPT through 2025-09, neither dated any 2026 event.
  `probed_knowledge_ends_before_window` is computed from that probe.
- The anonymized arm, which has no memorisation channel, now also runs on the walk-forward set: all 80 positive
  rows plus 320 hash-sampled negatives (case-control; AUC is valid, precision and probabilities are not
  deployment-prevalence numbers).
- The raise-mention check uses an explicit rule (raised / funding round / seed round / series X / backed by...),
  prints every matched description for owner review, and compares positives with negatives. The first version
  matched "fund" and wrongly counted products like money-market funds.
- Bootstraps resample within class, so no resample is dropped. The post-cutoff window is 4 months and
  right-censored.
