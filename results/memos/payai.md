# PayAI Network: baseline diligence memo (AI first pass, not a decision)

**PayAI Network is an x402 payment facilitator focused on Solana. It publishes open-source TypeScript SDKs (x402-solana and agentic-payments) that let developers and agents pay for and accept HTTP 402 payments, with a newer SDK covering both x402 and MPP.**

Thesis fit: Direct fit with AI agents x payments: it is live infrastructure for agents paying per request over x402, and the agentic-payments SDK extends the wedge toward a protocol-agnostic acceptance layer. The open question is whether the transaction volume is economically meaningful.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 14 claims shipped, 0 withheld by the verifier (raw citation precision 1.00, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 3 |
| NARRATIVE | 4 | 4 |
| EXECUTION | 3 | 3 |

## Market
- A GitHub-only screening model ranks the company 26 among all sourced candidates. [^c13]

## PMF
- x402scan shows the payAI facilitator has settled 53,090,708 x402 transactions in total, with 6,762,431 USD total volume. [^c3]
- The facilitator settled 462019 x402 transactions in the 30 days to the as-of date. [^c4]
- 30-day x402 settlement volume was 16088.59 USD. [^c5]
- Peak daily buyers in the last 30 days was 136. [^c6]

## Narrative
- x402-solana is a framework-agnostic implementation of x402 protocol v2 for Solana clients and servers. [^c1]
- A second SDK, agentic-payments, aims to accept x402 and MPP payments through a single integration, which points to a protocol-agnostic platform play. [^c2]
- The client has a beforePayment policy hook for spend caps, allowlists and reputation checks, and it fails closed, which is relevant for agent safety. [^c12]

## Execution
- The facilitator has been transacting since 2025-05-19, shortly after the GitHub org was created. [^c7]
- Default-branch commits across the top 5 repos were 29 in the latest 90 days. [^c8]
- Commits in the prior 90-day window were 56, so recent commit velocity roughly halved. [^c9]
- x402-solana has 36 stars and 15 forks, which is modest but real developer adoption. [^c10]
- The SDK claims full support for the latest x402 v2 specification, which suggests it tracks standards changes. [^c11]

## Risk
- The company has no Hacker News stories, so it has little public narrative presence there. [^c14]

## Scores

- **PMF 3/5**: Non-team buyers are transacting on-chain: 136 peak daily buyers and 462019 transactions in 30 days [c4][c6], with 53,090,708 lifetime transactions [c3]. Value is small, at 16088.59 USD in 30 days [c5], and the 30-day count is a small fraction of the lifetime total [c3][c4], so growth is not shown. The rubric's 5 requires growing usage, which the sources do not demonstrate.
- **NARRATIVE 4/5**: There is a crisp wedge: Solana x402 facilitation and client SDKs [c1], with agent-safety tooling [c12] and a stated path to a protocol-agnostic acceptance layer covering x402 and MPP [c2]. The edge versus other facilitators is not stated in the sources, and there is little public narrative footprint [c14].
- **EXECUTION 3/5**: They shipped x402 v2 support [c11], run multiple repos, and have been live since 2025-05-19 [c7]. Commits fell from 56 to 29 across the last two 90-day windows [c8][c9], and the sources do not show how many people contribute. Developer pull is modest [c10].

## Risks

- Low value per transaction: roughly 462k transactions for about 16k USD in 30 days suggests micro-payments, possibly including incentive-driven or automated traffic. Real revenue and take rate are unknown.
- The 30-day transaction count is a small fraction of the lifetime total of 53M [c3][c4], which hints at a sharp drop from a peak. This is an inference and needs confirming.
- Commit velocity roughly halved quarter over quarter [c8][c9], and team size and contributor concentration are unverified.
- Facilitation is a commoditizable layer and the sources name no competitors or moat. The company's focus on Solana ties it to one chain's x402 share.
- Monetization is unclear: the sources do not say whether the facilitator charges fees.

## Questions for the founder call

- What is the fee or revenue model, and what has PayAI Network earned in the last 90 days?
- What share of the 462k monthly transactions comes from organic buyers versus automated, incentive-driven or team-controlled wallets?
- What drove the apparent decline from 53M lifetime transactions to 462k in the last 30 days, and what is the trend?
- Who is on the team, how many people commit regularly, and why did commits drop in the last 90 days?
- How does PayAI Network differentiate from other x402 facilitators, and what is its stance on multi-chain and MPP?
- Who are the top 10 sellers or API providers by volume, and are any paying customers or design partners?

## Receipts

[^c1]: "A reusable, framework-agnostic implementation of the x402 payment protocol v2 for Solana clients (browsers) and servers." (github_readme, https://github.com/PayAINetwork/x402-solana, snapshot `d_e25335e7a14a4218`, fetched 2026-11-02)
[^c2]: "Protocol-agnostic agentic payments SDK — accept x402 and MPP payments through a single integration" (github_profile, https://github.com/payainetwork, snapshot `d_50189362d7ac28de`, fetched 2026-11-02)
[^c3]: "Total x402 transactions settled: 53,090,708. Total volume: 6,762,431 USD." (x402scan, https://www.x402scan.com, snapshot `d_f07008e5d5f69b82`, fetched 2026-11-02)
[^c4]: warehouse metric `x402.txs_30d` = 462019.0 (as of 2026-11-01)
[^c5]: warehouse metric `x402.volume_usd_30d` = 16088.59 (as of 2026-11-01)
[^c6]: warehouse metric `x402.peak_daily_buyers_30d` = 136.0 (as of 2026-11-01)
[^c7]: "First day with transactions: 2025-05-19." (x402scan, https://www.x402scan.com, snapshot `d_f07008e5d5f69b82`, fetched 2026-11-02)
[^c8]: warehouse metric `gh.commits_90d` = 29.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_prev_90d` = 56.0 (as of 2026-11-01)
[^c10]: "Stars: 36. Forks: 15. Language: TypeScript." (github_profile, https://github.com/payainetwork, snapshot `d_50189362d7ac28de`, fetched 2026-11-02)
[^c11]: "Full support for the latest x402 v2 specification" (github_readme, https://github.com/PayAINetwork/x402-solana, snapshot `d_e25335e7a14a4218`, fetched 2026-11-02)
[^c12]: "Failure semantics: an unhandled throw inside the hook aborts the payment" (github_readme, https://github.com/PayAINetwork/x402-solana, snapshot `d_e25335e7a14a4218`, fetched 2026-11-02)
[^c13]: warehouse metric `screen.rank` = 26.0 (as of 2026-11-01)
[^c14]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
