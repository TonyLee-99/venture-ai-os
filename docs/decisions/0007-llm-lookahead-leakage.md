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
