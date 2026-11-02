# vybenetwork: baseline diligence memo (AI first pass, not a decision)

**Vybe Network sells a Solana analytics API (token, wallet, holder data and WebSocket streams) to developers and AI agents, now also payable per call in USDC over x402 with no API keys, via an open-source TypeScript client SDK.**

Thesis fit: Direct fit: an established Solana data provider has added an x402 pay-per-call channel explicitly aimed at AI agents. It is a data vendor adding agent payments, not a payments-native startup, so the question is whether agent-paid revenue becomes material.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 13 claims shipped, 0 withheld by the verifier (raw citation precision 0.85, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 3 |
| NARRATIVE | 4 | 4 |
| EXECUTION | 3 | 3 |

## Market
- The x402 client SDK is built for AI agents and offers pay-per-call USDC over HTTP plus prepaid-credit WebSocket streaming for Vybe's Solana analytics API. [^c1]
- The org has 6298 stars across its repos in total, indicating an established developer presence beyond the x402 SDK. [^c12]
- Hacker News shows zero stories with the company name in the title. [^c13]

## PMF
- The SDK repo has 160 stars, a lightweight signal of developer interest. [^c2]
- The SDK has 64 forks, which is high relative to its stars, but the sources show no paid-call volume or customer counts. [^c3]

## Narrative
- The pitch is no signup and no API keys: a funded Solana wallet is all an agent needs. [^c4]
- The beta pricing has a default of $0.001 per call, with $0.003, $0.005, $0.008 and $0.010 on heavier endpoints. [^c5]
- A traditional flat-fee subscription alternative exists, so x402 is one of two monetization channels. [^c6]

## Execution
- Commits on the top repos' default branches in the latest quarter-length window totaled 89. [^c7]
- The x402 client repo was created 2026-05-11 and last pushed 2026-05-13, so the repo shows no pushes in roughly five and a half months before the fetch date. [^c8]
- The organization has existed since 2022 and has 18 public non-fork repositories. [^c9]

## Risk
- The SDK is pre-release and the service is in beta, so the API, pricing and protocol may change. [^c10]
- Each wallet is limited to 600 paid HTTP requests per minute. [^c11]

## Scores

- **PMF 3/5**: Real developer interest: 160 stars and 64 forks on the SDK [c2][c3] and a large org-wide star count [c12]. However, there is no evidence of paid x402 calls, wallet counts or revenue, so it does not reach the transacting-usage bar.
- **NARRATIVE 4/5**: Clear wedge: agents pay per call for Solana data with no keys [c1][c4]. It is tied to the x402 shift, with a subscription fallback [c6]. Pricing is a temporary beta discount [c5], and the path from a data API to an agent-commerce platform is not stated.
- **EXECUTION 3/5**: The team shipped an SDK and has a multi-year, multi-repo track record [c9], but commits dropped from 609 to 89 quarter over quarter [c7] and the SDK repo shows only two days of pushes in its history [c8]. Recent velocity is unclear and the product is still beta [c10].

## Risks

- Agent-paid x402 revenue may be negligible next to the existing subscription business; there is no usage or revenue evidence in the sources.
- Shipping velocity fell sharply (89 commits in 90 days vs 609 previously) and the SDK repo has no pushes after May 2026, which may signal deprioritization or work moving to private repos.
- Beta discount pricing ($0.001 default) will rise at GA, so current demand may not reflect willingness to pay at real prices.
- Commodity data risk: Solana analytics has many competitors, and the sources name none and state no moat beyond keyless payment.

## Questions for the founder call

- How many distinct wallets have paid for x402 calls, how many calls per day, and what is the monthly USDC volume, and how is it trending?
- What share of API revenue comes from subscriptions versus x402, and what is the expected mix in 12 months?
- Why did commit activity drop from 609 to 89 over the last two quarters, and is development happening in private repos?
- What are the target GA prices and what retention do you expect from early integrators once the beta discount ends?
- Who are the main competitors for agent-paid Solana data, and what is Vybe's defensible edge?
- Are any named AI agent frameworks or companies integrated or using the SDK in production?

## Receipts

[^c1]: "Pay-per-call USDC over HTTP and prepaid-credit WebSocket streaming for Vybe's Solana analytics API. Built for AI agents." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c2]: "Stars: 160. Forks: 64. Language: TypeScript." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c3]: "Stars: 160. Forks: 64. Language: TypeScript." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c4]: "**No signup, no keys.** A funded Solana wallet is all you need." (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c5]: "$0.001 default, $0.003 / $0.005 / $0.008 / $0.010 on heavier endpoints" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c6]: "If you'd rather a traditional flat-fee subscription instead of pay-per-call" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.commits_90d` = 89.0 (as of 2026-11-01)
[^c8]: "Created: 2026-05-11. Last push: 2026-05-13." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c9]: "Account created: 2022-01-25. Public non-fork repositories: 18.0." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c10]: "**The SDK is pre-release (0.1.x)** — the public API may change before 1.0." (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c11]: "600 paid HTTP requests per minute per wallet (sliding window)." (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c12]: warehouse metric `gh.stars_total_now` = 6298.0 (as of 2026-11-01)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
