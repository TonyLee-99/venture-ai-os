# PayAI Network: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | PAYAI (FDV $7.1M) | none | 26 (triage only, not evidence) |

**PayAI operates a production x402 facilitator (verify and settle stablecoin payments, Solana-first plus EVM chains) and SDKs so merchants selling API calls, MCP tools, inference or data to AI agents can charge per request.**

Thesis fit: Direct fit: infrastructure for agents paying per API call over x402. The open question is whether its very high transaction count reflects real agent commerce or low-value, possibly inorganic traffic, given roughly $0.03 per payment.

Recommendation after critique and committee: **watch** (first draft: watch; critic: watch)  
Receipts: 14 claims drafted, 36% passed the verifier on the first pass, 14 verified after one repair; the critic labelled 8 as entailed, 6 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 3 | 4 | 4 |
| EXECUTION | 3 | 4 | 3 |

## Team
- notorious-d-e-v is the top contributor to the x402-solana repo with 55 commits. [^c8] _(partial support: The quoted line supports the contributor's commit count but does not itself establish the repository or top-contributor ranking.)_
- PayAI Network, LLC is registered in Delaware and the team works remotely. No founders are named in the sources, and no funding evidence was found. [^c13] _(partial support: The receipt supports registration and remote work, but does not establish the absence of founder names or funding evidence across the sources.)_

## Why Now
- Users start with 1,000 free credits, after which $1 buys 1,000 credits. [^c12]

## Competition
- PayAI settled 462,019 payments (12.3% of payments) but only 16,089 USD (1.1% of volume). [^c2]
- Fluxa captures 56.2% of volume on 9.4% of payments, which shows that value-weighted share sits with other facilitators. [^c3]

## PMF
- PayAI has settled 53,090,708 x402 transactions and 6,762,431 USD in total volume. [^c1]
- Average value per payment over the last 30 days is about $0.0348, a very low figure that is an inorganic-traffic risk. [^c4] _(partial support: The metric supports the average payment value, but does not establish inorganic traffic or distinguish it from legitimate micropayments.)_
- Payments per peak daily buyer were 3397.2, meaning a small number of buyers account for a large share of payment volume. [^c5] _(partial support: The ratio is correct, but dividing monthly payments by peak daily buyers does not establish monthly buyer concentration or concentration of dollar volume.)_
- Developer adoption of the main SDK is modest: x402-solana has 36 stars and 15 forks. [^c11] _(partial support: The quote supports the star and fork counts, but does not identify the repository, establish it as the main SDK or prove substantive developer adoption.)_

## Execution
- Commits across the owner's top repos in the latest window were 29. [^c9]
- PayAI publishes a protocol-agnostic agentic payments SDK to accept x402 and MPP payments through a single integration. [^c10]

## Risk
- Third-party customer evidence on the website is limited to two ecosystem testimonials (WURK.FUN and Predict), with no revenue or customer counts disclosed. [^c14] _(partial support: The quote supports Predict's reported listing experience, but not the total testimonial count, WURK.FUN's involvement or the absence of revenue and customer disclosures.)_

## Scores (final, after the support review)

- **PMF 2/5**: Settlement is real and cumulative volume is sizable [c1], but PayAI's 462,019 payments yield only 16,089 USD, a 1.1% volume share [c2]. Average value per payment is about $0.0348 over 30 days, an inorganic-traffic risk [c4, partial]. Payments per peak daily buyer of 3397.2 suggests concentration in few buyers [c5, partial]. Weekly transaction medians swing by orders of magnitude [c6][c7]. Developer adoption is modest at 36 stars and 15 forks [c11, partial], and customer evidence is limited to two testimonials with no revenue or customer counts [c14, partial]. Payments exist, but organic demand from independent users is not demonstrated.
- **NARRATIVE 3/5**: The story is timely and clear: an x402 facilitator with a protocol-agnostic SDK covering x402 and MPP through one integration [c10], and a free-credit start [c12]. Lowered from 4 because the remaining claims no longer support a Solana-first or Anthropic Commerce edge, and the field is crowded: other facilitators hold the value-weighted share [c3], and PayAI has only 1.1% of volume [c2]. Monetization looks hard at about $0.0348 per payment [c4, partial]. The wedge is plausible but undifferentiated on the evidence.
- **EXECUTION 3/5**: There is a shipped, protocol-agnostic SDK [c10] and 29 commits across the owner's top repos in the latest window [c9]. However, the team evidence is thin: one named top contributor with 55 commits on x402-solana [c8, partial], no named founders and no funding evidence [c13, partial]. The earlier claim of several contributors and sustained multi-person velocity is not supported, and the commit trend is unverified in the remaining claims. Steady but concentrated shipping fits a 3.

Re-score note: Narrative lowered from 4 to 3 and Execution from 4 to 3 because the review removed support for the Solana-first and Anthropic Commerce edge, for multiple contributors, and for the halving of commit volume cited in the first draft. PMF stays at 2. The total is 8, below the advance threshold of 11, and PMF is below 3, so the recommendation stays watch.

## Risks

- Inorganic traffic: 462,019 payments at about $0.03 each and about 136 peak daily buyers suggest volume driven by a few bots or incentives, and the swings from 4.5M to 49K weekly transactions support this.
- Weak monetization: 12.3% of payments but 1.1% of volume, with credits priced at $1 per 1,000, so facilitator revenue may be negligible versus infrastructure costs.
- Commoditization: Coinbase holds 69.7% of payments and the facilitator role is easy to replicate, as the 12 facilitators listed show; the free tier and no-key onboarding limit pricing power.
- Opaque team and funding: no founders named, no round evidence, and a token (PAYAI, FDV $7.1M) that complicates equity-style investment.

## Questions for the founder call

- What share of the 462K monthly payments comes from the top 5 buyers or wallets, and what explains the August 2026 spike to 4.5M weekly transactions?
- Who are the founders, and what is the cap table and token structure (PAYAI FDV $7.1M) relative to the LLC?
- What is actual revenue: how many paying merchants are above the 1,000 free credits, and what is monthly credit revenue?
- Which merchants drive real dollar volume, and what is the path from the facilitator to higher-value products such as batch settlement, Payment Splitting or the Token Gateway?
- Why did commits fall from 56 to 29 quarter over quarter, and where is engineering time going?

## Receipts

[^c1]: "Total x402 transactions settled: 53,090,708. Total volume: 6,762,431 USD." (x402scan, https://www.x402scan.com, snapshot `d_f07008e5d5f69b82`, fetched 2026-11-02)
[^c2]: "payAI: 462,019 payments (12.3% of payments), 16,089 USD (1.1% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c3]: "fluxa: 353,469 payments (9.4% of payments), 846,830 USD (56.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c4]: warehouse metric `x402.usd_per_tx_30d` = 0.0348 (as of 2026-11-01)
[^c5]: warehouse metric `x402.txs_per_peak_daily_buyer_30d` = 3397.2 (as of 2026-11-01)
[^c6]: "Week of 2026-09-14: weekly median transactions 4,485,090 -> 49,368 (down, ratio 0.011)" (monitor_findings, results/monitoring/changepoints.json, snapshot `d_95b38e673e4b0e38`, fetched 2026-11-02)
[^c7]: "Week of 2026-01-26: weekly median transactions 2,988,322 -> 577,642 (down, ratio 0.193)" (monitor_findings, results/monitoring/changepoints.json, snapshot `d_95b38e673e4b0e38`, fetched 2026-11-02)
[^c8]: "notorious-d-e-v (User): 55 commits" (github_contributors, https://github.com/PayAINetwork/x402-solana/graphs/contributors, snapshot `d_1d9989bd19a2b6ca`, fetched 2026-11-02)
[^c9]: warehouse metric `gh.commits_90d` = 29.0 (as of 2026-11-01)
[^c10]: "Protocol-agnostic agentic payments SDK — accept x402 and MPP payments through a single integration" (github_profile, https://github.com/payainetwork, snapshot `d_50189362d7ac28de`, fetched 2026-11-02)
[^c11]: "Stars: 36. Forks: 15. Language: TypeScript." (github_profile, https://github.com/payainetwork, snapshot `d_50189362d7ac28de`, fetched 2026-11-02)
[^c12]: "You start with 1,000 free credits. After that, $1 buys 1,000 credits." (website, https://payai.network, snapshot `d_97739bfb70f0047f`, fetched 2026-11-02)
[^c13]: "PayAI Network, LLC is registered in Delaware, United States. The team works remotely." (website_about, https://payai.network/about, snapshot `d_bf4860a8b3f2429b`, fetched 2026-11-02)
[^c14]: "PayAI has enabled us to list our Prediction Market agent on their platform" (website, https://payai.network, snapshot `d_97739bfb70f0047f`, fetched 2026-11-02)
