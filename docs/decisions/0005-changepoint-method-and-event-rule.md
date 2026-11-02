# 0005. Changepoint method and the dated-event rule (fixed before computing any hit rate)

Status: accepted 2026-11-02, committed before the first event-validation run.

## Series
x402 market traction from x402scan (all chains, Base, Solana): weekly transactions, weekly volume (USD),
peak daily buyers; plus weekly transactions of the largest facilitators. Weeks start Monday. Log1p transform.
Weekly, not daily: daily x402 counts have weekday effects and bursty noise; on daily data PELT with a
BIC-style penalty fires every ~18 days, so almost any event would be "hit" by chance.

## Detector (no tuning on events)
PELT, L2 cost (shift in mean of log level), minimum regime 2 weeks, penalty 2 * sigma^2 * ln(n) with sigma
from the MAD of first differences. Sensitivity rows at 0.5x and 2x the penalty are reported, not selected.
Baseline: trailing z-score of weekly log changes (|z| > 2.5, 8-week window, 2-week refractory).

## Events (mechanical rule)
1. Every post in the x402 Foundation's own feed (https://x402.org/feed/), dated by `pubDate`.
2. Three third-party launches whose pages were fetched and show the date: Google AP2 (2025-09-16),
   Cloudflare x402 Foundation announcement (2025-09-23), Cloudflare Monetization Gateway (2026-07-01).
3. Every Hacker News story with >= 15 points whose title mentions x402, AP2, agentic payments or agentic
   commerce (HN Algolia), dated by the story.
Events within 3 days of each other are merged. Only events inside the series range count.
Each event is stored as a source snapshot so the weekly brief can cite it.

## Metrics
Event hit rate: share of events with a changepoint within +/- 7 days. False-alarm rate: share of
changepoints with no event within +/- 7 days. Null: 5,000 placements of the same number of changepoints at
random weeks; p = share of placements with a hit rate >= observed. Some events (e.g. a protocol launch by
another company) need not move x402 volume at all, so a hit rate well below 1 is expected and is reported.
