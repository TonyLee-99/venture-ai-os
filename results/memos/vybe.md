# vybenetwork: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 25 (triage only, not evidence) |

**Vybe Network sells Solana wallet and token analytics (portfolio tracker, smart-money signals, real-time and historical API) to traders and developers, and has added a pay-per-call USDC x402 API and SDK aimed at AI agents.**

Thesis fit: Partial fit. Vybe is an established Solana data provider whose x402 pay-per-call API and SDK for agents are a recent, beta-stage extension, not the core business. There is no sourced evidence yet of agent-driven x402 payment volume.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: watch; critic by policy: watch, critic stated: watch)  
Receipts: 13 claims drafted, 85% passed the verifier on the first pass, 11 verified after one repair; the critic labelled 3 as entailed, 8 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 3 | 3 | 3 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- The Vybe GitHub org has 18 public non-fork repos. The sources name no founders or contributor counts, so team size and composition are unknown. [^c1] _(partial support: The metric supports the repository count but cannot establish whether the sources identify founders or contributors.)_

## Why Now
- The SDK lets an agent pay per request in USDC, starting at $0.001 per call, with no API keys or signup. This is the agent-commerce wedge. [^c8] _(partial support: The quote establishes per-request USDC payments and starting pricing but does not establish agent integration or the absence of signup and API keys.)_

## Competition
- The x402 facilitator market is concentrated: Coinbase handles 68.2% of payments. Vybe does not appear in the facilitator table, so its x402 volume is not visible in this source. [^c9] _(partial support: The quote establishes Coinbase's payment share but cannot establish Vybe's absence from the complete table or the visibility of its volume.)_

## PMF
- The x402-client SDK repo has 160 stars and 64 forks, which is developer interest but not payment evidence. [^c2]
- The website self-reports 10,000+ traders as users. This is unaudited marketing copy and is not specific to x402. [^c3] _(partial support: The quote reports trader trust but does not establish that those traders are users or specify their relationship to x402.)_
- A testimonial attributed to Superteam Canada says it used the Vybe API for historical wallet and token data. This is a named but unverified API user. [^c4] _(partial support: The quote supports reported use of historical wallet and token data but contains no attribution to Superteam Canada.)_
- The org's repos have 6298 stars in total today, a current snapshot rather than point-in-time growth. [^c13]

## Narrative
- The core public product is a Solana wallet tracker and portfolio analytics app. The agent x402 offering is secondary on the website. [^c12] _(partial support: The quote supports the wallet-tracking and portfolio-analytics positioning but does not establish the relative prominence of the agent offering.)_

## Execution
- The top 5 repos had 89 commits in the 90 days before 2026-11-01. [^c5]

## Risk
- The SDK is pre-release, and the README says the endpoint, protocol and pricing may change. [^c10] _(partial support: The quote establishes pre-release status but says nothing about changes to the endpoint, protocol or pricing.)_
- Beta pricing is a discount that the README says will rise at general availability, so current per-call economics are not representative. [^c11] _(partial support: The quote establishes a future price increase but does not establish a beta discount or how representative current unit economics are.)_

## Scores (final, after the support review)

- **PMF 3/5**: Developer adoption is real: the x402-client SDK has 160 stars and 64 forks [c2], and the org has 6298 total stars [c13], though that is a current snapshot and not growth. Usage evidence is weak and partial: the 10,000+ traders figure is unaudited marketing copy not specific to x402 [c3], and the Superteam Canada testimonial is a named but unverified API user [c4]. There is no payment evidence, and Vybe does not appear in the facilitator table [c9].
- **NARRATIVE 3/5**: The agent pay-per-call wedge (USDC, from $0.001 per call, no API keys) is timely [c8], but it is secondary to a Solana wallet tracker and analytics app [c12]. The SDK is pre-release with endpoint, protocol and pricing subject to change [c10], and beta discount pricing will rise at GA, so current economics are not representative [c11]. The facilitator market is concentrated around Coinbase [c9], and no edge against it is stated. The story is in the right space but generic, with no clear path from wedge to platform.
- **EXECUTION 3/5**: Commit volume is substantial: 89 commits across the top 5 repos in the 90 days before 2026-11-01 [c5], and the org has 18 public non-fork repos [c1]. Team size and composition are unknown [c1], so multi-person shipping cannot be confirmed. The earlier draft cited a sharp commit drop [c6] and no SDK pushes since May [c7]. Those claims did not survive review, so they are not used here.

Re-score note: The execution rationale no longer relies on the commit decline [c6] or the stale SDK [c7], since neither claim survived review. The PMF and narrative rationales now flag the partial claims as weak evidence. Priority questions for the founder call are x402 payment volume, the team, and the SDK's maintenance status.

## Risks

- No evidence of actual x402 transaction volume or agent customers. The x402 line is a beta SDK, and the facilitator market data does not show Vybe.
- Commit velocity is down sharply, and the x402-client repo has been idle since mid-May 2026, which may signal deprioritization of the agent product.
- Beta discount pricing and pre-release SDK make any current usage a weak guide to future revenue.
- Solana data and analytics is a crowded category, and the sources state no differentiated edge beyond the website's claims of data quality and latency.
- The x402 usd_per_tx_30d metric was not provided, so inorganic-traffic risk cannot be assessed.

## Questions for the founder call

- Who are the founders and how large is the engineering team? What is the funding history?
- How many paid x402 calls and how much USDC volume have there been, and from how many distinct wallets? What share comes from AI agents rather than testing or the team?
- Why has the x402-client repo had no pushes since May, and is the agent product still a priority?
- What are the post-beta prices, and how do x402 revenues compare with subscription API revenue?
- Which facilitator settles Vybe's payments, and what is the average value per payment?

_5 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: warehouse metric `gh.public_repos` = 18.0 (as of 2026-11-01)
[^c2]: "Stars: 160. Forks: 64. Language: TypeScript." (github_profile, https://github.com/vybenetwork, snapshot `d_26e65d0b8d435a48`, fetched 2026-11-02)
[^c3]: "Trusted by 10,000+ Traders" (website, https://vybenetwork.com, snapshot `d_79209d156af52c70`, fetched 2026-11-02)
[^c4]: "Vybe gave us complete historical data for wallets and tokens we couldn't find anywhere else." (website, https://vybenetwork.com, snapshot `d_79209d156af52c70`, fetched 2026-11-02)
[^c5]: warehouse metric `gh.commits_90d` = 89.0 (as of 2026-11-01)
[^c8]: "Each request settles a USDC micropayment ($0.001 and up)." (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c9]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c10]: "The SDK is pre-release (0.1.x)" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c11]: "These rates will go up at general availability" (github_readme, https://github.com/vybenetwork/x402-client, snapshot `d_d2e39ad11bd7a4d2`, fetched 2026-11-02)
[^c12]: "The Ultimate Solana Wallet Tracker and Portfolio Analytics App" (website, https://vybenetwork.com, snapshot `d_79209d156af52c70`, fetched 2026-11-02)
[^c13]: warehouse metric `gh.stars_total_now` = 6298.0 (as of 2026-11-01)
