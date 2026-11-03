# 0003. The screening backtest runs on DefiLlama-listed crypto protocols, not only on agentic payments

Status: accepted (2026-11-02).

## Context
The fund-relevant niche is agentic payments (x402, agent wallets, MCP monetisation). It is young: x402 went
live in May 2025 and its on-chain series starts 2025-05-09. A point-in-time backtest needs (a) many entities
visible at several past dates T0, (b) a dated, free outcome that reflects an investor decision, and (c) a
12-month outcome window that has already closed. The niche alone gives a handful of entities and almost no
closed windows.

## Decision
- Backtest universe: every DefiLlama protocol with a GitHub owner and a known listing date before T0
  (about 500 to 1,200 per T0). Outcome: any raise in DefiLlama's per-protocol `raises` dated in [T0, T0+12m).
- Seven T0s every six months, 2022-07-01 to 2025-07-01. Walk-forward: a model tested at T0 is trained only on
  T0s whose outcome window closed on or before that T0.
- The live niche screen uses the **GitHub-only** variant of the score, because most niche candidates are not
  DefiLlama protocols. That variant is backtested separately so the live score is never an untested one.

## Consequences and honest limits
- The backtest measures "does public traction anticipate a VC raise for crypto protocols", which is close to,
  but not the same as, "for agentic-payments startups". Stated in the README limitations.
- DefiLlama raises cover protocols that are listed; raises before listing are invisible to the universe.
- DefiLlama backfills TVL history when it lists a protocol, so listing date (not first TVL day) defines when a
  protocol becomes visible. Protocols with no listing date and TVL starting after 2021-10-14 are dropped.
- Survivorship: DefiLlama keeps dead protocols with zero TVL, which limits but does not remove this bias.
- The top-5 repos per owner are chosen by today's stars (residual selection leakage). Commit counts inside
  them are still timestamped, and repos created after T0 contribute zero commits before T0.

## Amendment (round 1): label and sensitivity
This backtest is a **retrospective reconstruction**: universe membership, GitHub owner and the top-5 repos are
today's, and an owner that no longer resolves contributes zero commits. Owners resolve for 96% of positive
rows vs 90% of negative rows, so deleted/renamed repos make negatives look less active (bias in the model's
favour). `backtest.json` reports the never-raised and full populations again with unresolved owners dropped
(`*_gh_found_only`). Lead-time analysis: DefiLlama listing comes AFTER the first raise for most protocols, so
the listed universe is post-raise by construction; first public GitHub repos usually come before it.
