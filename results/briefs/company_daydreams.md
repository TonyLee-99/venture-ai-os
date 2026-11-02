# Daydreams: weekly KPI brief, week of 2026-11-01

_Public comparable (x402 facilitator + open-source agent framework); portfolio-style monitor. Every claim passed the receipts verifier (7 shipped of 10)._

| Week | Payments | USD volume | Peak daily buyers | USD / payment | Share of x402 | Commits |
|---|---|---|---|---|---|---|
| 2026-08-10 | 163 | 394 | 8 | 2.4147 | 0.01% | 0.0 |
| 2026-08-17 | 176 | 277 | 7 | 1.5722 | 0.00% | 0.0 |
| 2026-08-24 | 276 | 83 | 12 | 0.3023 | 0.00% | 0.0 |
| 2026-08-31 | 84 | 11 | 5 | 0.132 | 0.00% | 0.0 |
| 2026-09-07 | 135 | 39 | 5 | 0.2871 | 0.01% | 0.0 |
| 2026-09-14 | 77 | 237 | 6 | 3.0797 | 0.01% | 0.0 |
| 2026-09-21 | 67 | 343 | 5 | 5.1241 | 0.01% | 0.0 |
| 2026-09-28 | 155 | 74 | 33 | 0.4773 | 0.03% | 0.0 |
| 2026-10-05 | 191 | 127 | 5 | 0.6641 | 0.03% | 2.0 |
| 2026-10-12 | 76 | 67 | 8 | 0.8797 | 0.01% | 0.0 |
| 2026-10-19 | 99 | 28 | 8 | 0.2847 | 0.01% | 0.0 |
| 2026-10-26 | 343 | 623 | 53 | 1.8165 | 0.03% | 0.0 |

Daydreams' latest week (starting 2026-10-26) was its biggest in the recent window: 343 transactions, $623.06 volume and 53 peak daily buyers, versus 99 transactions and $28.188 the prior week. The buyer spike looks like a one-off, similar to the 33-buyer spike in the week of 2026-09-28, and no source documents were provided, so none of these moves can be tied to a public event. The long-run changepoints in the series swing across several orders of magnitude, and the unit of that series is not stated in the facts, so they should be read with caution.

## 2026-10-26 | Weekly volume jumps to $623 from $28 with no explanation in evidence **[needs human]**

- Weekly volume was 623.06 USD in the week of 2026-10-26. (`daydreams.2026-10-26.volume_usd` = 623.06)

## 2026-10-26 | Peak daily buyers hit 53, the highest in the window, from 8 **[needs human]**

- Peak daily buyers reached 53 in the week of 2026-10-26. (`daydreams.2026-10-26.peak_daily_buyers` = 53.0)
- The prior week's peak was 8 buyers. (`daydreams.2026-10-19.peak_daily_buyers` = 8.0)

## 2026-10-26 | Transactions rise to 343 from 99, a window high **[needs human]**

- Weekly transactions were 343 in the week of 2026-10-26. (`daydreams.2026-10-26.txs` = 343.0)
- Transactions were 99 the week before. (`daydreams.2026-10-19.txs` = 99.0)

## 2026-06-01 | Latest detected changepoint: median level rose about 21x from 7 to 149 **[needs human]**

- The median level shifted from 7 before to 149 after, a ratio of 21.286. (`daydreams.changepoint.2026-06-01.ratio` = 21.286)
- The median level after the shift was 149. (`daydreams.changepoint.2026-06-01.median_after` = 149.0)

## Watchlist

- daydreams.peak_daily_buyers: check whether the 53-buyer spike persists or reverts to about 5 to 8 as the 33-buyer spike did.
- daydreams.volume_usd: check whether weekly volume stays above the recent range after 623.06 USD, or falls back toward the 28 to 127 USD range of recent weeks.
- daydreams.commits: commit activity is near zero in nearly every week of the window, so check whether development activity resumes and whether it matters for usage.
- daydreams.share_of_x402_txs: it stays near 0.0001 to 0.0003, so confirm whether the latest week's 0.0003 holds.
