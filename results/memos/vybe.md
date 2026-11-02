# vybenetwork: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 18 (triage only, not evidence) |

**Vybe Network sells Solana wallet/portfolio analytics, smart-money tracking and a data API to traders and developers, and has added a pay-per-call x402 (USDC) API and SDK aimed at AI agents.**

Thesis fit: Partial fit: an established Solana data provider that has bolted on x402 pay-per-call access for agents, so the agent-payments angle is a new distribution channel rather than the core company. No evidence yet of actual x402 payment volume from Vybe.

Recommendation after critique and committee: **watch** (first draft: watch; critic: watch)  
Receipts: 13 claims drafted, 62% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 3 as entailed, 9 as partial (tagged below) and withheld 1.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 3 | 3 | 3 |
| NARRATIVE | 3 | 3 | 4 |
| EXECUTION | 3 | 3 | 3 |

## Team
- No named founders or team members appear in the sources; the GitHub org has existed since 2022 with 18 public non-fork repos. Team size is unknown. [^c9] _(partial support: The quote supports account age and repository count but cannot establish the absence of named team members across the sources or determine team size.)_

## Why Now
- The x402 SDK is positioned for AI agents: pay-per-call USDC over HTTP plus prepaid-credit WebSocket streaming for Solana analytics. [^c4]

## Competition
- In the x402 facilitator market over the trailing window, Coinbase holds 69.7% of payments. Vybe does not appear in the list of facilitators; it is a seller/API, so this is context rather than direct competition. [^c10] _(partial support: The quote supports Coinbase's payment share but does not establish Vybe's absence from the full list, its business role or its competitive relationship.)_

## PMF
- The core product is a Solana wallet tracker and portfolio analytics app, with API access offered alongside it. [^c1] _(partial support: The quote establishes the wallet tracker and portfolio analytics product but does not mention API access.)_
- The website claims 10,000+ traders use the product (self-reported, unverified). [^c2] _(partial support: The website claims trader trust, but the quoted wording does not establish actual product use.)_
- The x402 API charges per call in USDC with no API keys, starting at $0.001 per call, and is described as a beta discount that will rise at general availability. [^c3] _(partial support: The quote supports discounted default pricing but does not establish USDC settlement, per-call billing, keyless access or future price increases.)_
- The x402-client repo has 160 stars and 64 forks, suggesting developer interest, though forks are high relative to stars and there is no payment-volume evidence. [^c5] _(partial support: The receipt supports the repository counts, while developer interest is an inference and the absence of payment-volume evidence is not established by this quote.)_

## Narrative
- Hacker News traction is nil: the count of stories with the company name in the title is 0. [^c13] _(partial support: The metric establishes no matching title stories but does not establish the absence of all Hacker News traction.)_

## Execution
- The x402-client repo was created 2026-05-11 and last pushed 2026-05-13. [^c6]
- Commits on the default branches of the owner's top repos totaled 89 in the most recent quarter-length window. [^c7]
- Prior-90-day commit count was 609, showing earlier bursts of activity. [^c8] _(partial support: The metric supports the prior-window commit count but does not reveal whether activity occurred in bursts.)_

## Risk
- The SDK README states the service is in beta, and the API, shapes and pricing can change. [^c12] _(partial support: The quote establishes beta status but does not explicitly support changes to the API, response shapes or pricing.)_

## Scores (final, after the support review)

- **PMF 3/5**: Self-reported 10,000+ traders [c2] and an analytics app with API access [c1] are weak, unverified signals. The x402-client repo has 160 stars and 64 forks [c5], which is developer interest but not payment evidence. The x402 API is priced from $0.001 per call [c3], but no payment or x402 volume from Vybe is evidenced in the remaining claims. This is the top of what the evidence supports, so it holds at 3 rather than moving up.
- **NARRATIVE 3/5**: The agent-pays-per-call angle for Solana analytics [c4] with a low entry price [c3] is timely and fits the thesis. However, the core story is a trader-facing analytics app [c1], the x402 channel is a beta add-on whose API and pricing can change [c12], and Vybe sits as a seller next to a facilitator market dominated by Coinbase [c10]. No stated edge against other Solana data APIs, and no HN traction [c13]. Generic-to-timely, so 3.
- **EXECUTION 3/5**: Commit volume dropped from 609 in the prior 90 days [c8] to 89 in the most recent window [c7], a sharp slowdown. The x402-client repo was last pushed 2026-05-13 [c6], months before today. The org has 18 public non-fork repos since 2022 [c9], but team size and named contributors are unknown. Prior velocity was strong, but the recent trend is weak. 3 is generous; a 2 is arguable if the slowdown is confirmed as a real stall and not a repo-selection artifact.

Re-score note: Scores unchanged at 3/3/3 (total 9, below the advance threshold of 11), so the recommendation stays watch. The withheld claim c11 is removed, so the draft's statement that x402 volume is unverified is now simply an absence of evidence, not a documented finding; PMF stays at 3 on developer interest alone. Several remaining claims are only partially supported, so the rationales lean on them as weak evidence. Execution is the dimension most at risk of a downgrade given the commit drop and the stale x402 repo.

## Risks

- Company is an established Solana analytics business, not an agent-payments company; x402 may be a side channel with little revenue, and the stage is unclear for a pre-seed/seed check.
- No evidence of x402 payment volume or customers; the 64 forks and 160 stars may not translate to paying agents.
- Shipping velocity dropped about 85% quarter over quarter, and the x402 SDK repo appears dormant since May 2026.
- Pay-per-call prices are a beta discount ($0.001) that will rise, so unit economics and demand at GA price are untested; data-provider competition on Solana is crowded.

## Questions for the founder call

- Who are the founders and how many engineers work on Vybe? Is there any funding or investors to date?
- How many x402 payments and how much USD volume has the Vybe x402 API processed, and how many distinct paying wallets are outside the team?
- What explains the drop in commits from 609 to 89, and is the x402 SDK still actively maintained?
- What is revenue today by channel (subscriptions vs x402) and what is the plan for GA pricing?
- Why would agents choose Vybe over other Solana data providers or RPC-based indexing, and what is the moat in the data?

## Withheld: real quote, but the critic says it does not support the claim

- ~~The market-structure source shows no Vybe-specific x402 payment or revenue data, so x402 usage by Vybe is unmeasured. The warehouse facts also contain no x402.usd_per_tx_30d value, so inorganic-traffic risk cannot be assessed.~~ (unsupported: The quoted heading identifies the market dataset's scope and period but does not establish missing company metrics, warehouse contents or whether inorganic traffic can be assessed.)

## Receipts

[^c1]: "The Ultimate Solana Wallet Tracker and Portfolio Analytics App" (website, https://vybenetwork.com, snapshot `d_79209d156af52c70`, fetched 2026-11-02)
[^c2]: "Trusted by 10,000+ Traders" (website, https://vybenetwork.com, snapshot `d_79209d156af52c70`, fetched 2026-11-02)
[^c3]: "Pricing is currently a beta discount.** $0.001 default" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c4]: "Pay-per-call USDC over HTTP and prepaid-credit WebSocket streaming for Vybe's Solana analytics API. Built for AI agents." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c5]: "Stars: 160. Forks: 64. Language: TypeScript." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c6]: "Created: 2026-05-11. Last push: 2026-05-13." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.commits_90d` = 89.0 (as of 2026-11-01)
[^c8]: warehouse metric `gh.commits_prev_90d` = 609.0 (as of 2026-11-01)
[^c9]: "Account created: 2022-01-25. Public non-fork repositories: 18.0." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c10]: "coinbase: 2,610,865 payments (69.7% of payments), 534,034 USD (35.4% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c12]: "**The service is in beta.**" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
