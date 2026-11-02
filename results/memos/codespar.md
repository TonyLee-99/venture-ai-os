# codespar: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 14 (triage only, not evidence) |

**CodeSpar sells a hosted MCP/SDK account for AI agents to pay and get paid in Latin America, with spending mandates, human approval rules and signed receipts across Pix, boleto, card and USDC, plus an open-source catalog of LATAM commerce MCP servers.**

Thesis fit: Strong thematic fit: agent commerce with a governance layer (mandates, approvals, audit trail) on LATAM rails, with x402/USDC as one of several rails. Paying usage is not evidenced, and the x402 leg looks secondary and partly deprecated.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: watch; critic by policy: watch, critic stated: watch)  
Receipts: 13 claims drafted, 46% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 5 as entailed, 7 as partial (tagged below) and withheld 1.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 4 | 4 | 4 |
| EXECUTION | 4 | 4 | 3 |

## Team
- One person dominates the main repo: fabianocruz has 244 commits. [^c1] _(partial support: The quote establishes fabianocruz's commit count but provides no comparison supporting dominance of the repository.)_
- The about page says the company was built in New York and Rio de Janeiro by the team behind Zoop (a prior LATAM payments company); individual founders are not named in the sources. [^c2] _(partial support: The quote supports the stated locations and Zoop affiliation, but not Zoop's business description or the absence of named founders throughout the sources.)_

## Why Now
- The repo README argues four agentic payment protocols (Stripe ACP, Google UCP, AP2, x402) are shipping in parallel and do not compose cleanly with each other or with regional rails. [^c3] _(partial support: The quote supports parallel protocol shipping but does not identify the protocols or establish the claimed interoperability problems.)_

## Competition
- In the x402 market, Coinbase's facilitator handles 68.2% of payments; no CodeSpar facilitator appears in the list, so CodeSpar is not a visible x402 facilitator. [^c9] _(partial support: The quote supports Coinbase's payment share but contains no evidence about CodeSpar's inclusion or visibility.)_

## PMF
- Developer interest in the open-source MCP catalog is real but modest: mcp-dev-latam has 277 stars and 52 forks, and the owner's repos total 313 stars. [^c4]
- The website's payment history, mandate, receipt counters and settled-today figures are labeled sandbox/demo data, so no customer or payment volume is evidenced. [^c5] _(partial support: The quote identifies sandbox demonstration data but alone does not establish which displays it covers or the absence of customer and payment evidence.)_

## Narrative
- The wedge is control over agent spend: the about page says moving money is solved and the work is deciding whether an agent may move it and proving what happened. [^c10]

## Execution
- The team committed 380 times to the default branches of its top repos in the last 90 days. [^c6]
- The top repos hold 1096 commits in total. [^c7]
- The team measured its own catalog and deprecated the UCP, AP2 and x402 servers because they have no live endpoint. [^c8] _(partial support: The quote supports the packages' deprecation and stated endpoint issue but does not establish that the team measured its catalog.)_
- The team publishes standards work: an agentic-payments-standards repo covers KYA verifiable agent mandates, a Pix push-rail for ACP, an OAC proposal and an AP2 mapping. [^c11]

## Risk
- No funding, stage, or token evidence was found, and there is no Hacker News presence (0 stories). [^c13] _(partial support: The metric establishes no matching company-title Hacker News stories, but supports neither the funding assertions nor the broader absence of Hacker News presence.)_

## Scores (final, after the support review)

- **PMF 2/5**: Outside developer interest in the free MCP catalog is real but modest (277 stars, 52 forks) [c4]. The only payment, mandate and receipt figures are labeled sandbox/demo, so no customer or payment volume is evidenced [c5]. Adoption of a free catalog is not adoption of the paid product, and there is no funding or traction signal elsewhere [c13].
- **NARRATIVE 4/5**: The wedge is clear: control over agent spend, deciding whether an agent may move money and proving what happened [c10]. It is credibly backed by a team with prior LATAM payments experience, though the founders are not named in the sources [c2]. It is timely given fragmented agentic payment protocols [c3]. It is held back because the x402 leg is deprecated and CodeSpar is not a visible x402 facilitator [c8][c9], and because the paid product has no evidenced demand [c5].
- **EXECUTION 4/5**: Shipping velocity is strong: 380 commits to default branches in the last 90 days across 1096 total [c6][c7]. The team publishes standards work covering KYA mandates, a Pix push-rail for ACP, an OAC proposal and an AP2 mapping [c11], and it audited its own catalog and deprecated servers with no live endpoint [c8]. Held back by commit concentration in one person, with fabianocruz at 244 commits [c1]. The claim about features still rolling out was withheld, so it no longer counts against this score.

Re-score note: The rolling-out claim (c12) was withheld, so the rationale no longer relies on it for Execution; the score still holds on velocity, standards work and the self-audit. Partial claims (c1, c2, c3, c5, c8, c9, c13) are treated as weak evidence. PMF is the gap: no payment or customer evidence beyond sandbox data. Re-check when there is evidence of real transacting customers.

## Risks

- No evidence of real paying customers or transaction volume; every payment figure on the site is labeled demo data.
- Regulatory and partner dependency: moving BRL via Pix, boleto and card relies on licensed providers (e.g. Celcoin) and local compliance, with no evidence of how this is structured.
- Platform-vs-catalog confusion: much of the traction is stars on a free open-source MCP catalog, many of whose servers are deprecated or contract-gated, which may not convert to revenue.

## Questions for the founder call

- Who are the founders, and what is the Zoop connection (roles, exit, relationships with LATAM payment providers)?
- Are there any live (non-sandbox) customers or paid volume today? What is the pricing model?
- Who holds the licenses and custody for BRL flows: CodeSpar, Celcoin, or another partner?
- How much of the 380 recent commits is product versus catalog maintenance, and who besides fabianocruz ships?
- Is x402/USDC strategic or incidental, given the deprecated x402 server and no facilitator presence?
- How is the company funded today, and what is the planned raise?

_4 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Withheld: real quote, but the critic says it does not support the claim

- ~~Some product features are not yet shipped: the website marks verified approver, audit trail CSV export and reconciliation as rolling out.~~ (unsupported: The feature label alone establishes neither rollout status nor the shipping status of any listed capability.)

## Receipts

[^c1]: "fabianocruz (User): 244 commits" (github_contributors, https://github.com/codespar/mcp-dev-latam/graphs/contributors, snapshot `d_08316a3bcaac9992`, fetched 2026-11-02)
[^c2]: "Built in New York and Rio de Janeiro by the team behind Zoop" (website_about, https://codespar.dev/about, snapshot `d_d9bf981ecb401c3d`, fetched 2026-11-02)
[^c3]: "four agentic payment protocols are shipping in parallel" (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c4]: "Stars: 277. Forks: 52. Language: TypeScript." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c5]: "Sandbox run · demo data" (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c6]: warehouse metric `gh.commits_90d` = 380.0 (as of 2026-11-01)
[^c7]: warehouse metric `gh.commits_total` = 1096.0 (as of 2026-11-01)
[^c8]: "UCP, AP2 and x402 are deprecated: no live endpoint." (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c9]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c10]: "Moving money is solved. Deciding whether an agent may move it, and proving what happened, is the work." (website_about, https://codespar.dev/about, snapshot `d_d9bf981ecb401c3d`, fetched 2026-11-02)
[^c11]: "Open CodeSpar contributions to agentic payment standards: KYA verifiable agent mandates, Pix push-rail for ACP, OAC proposal (Agentic Commerce Consortium), AP2 mapping." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
