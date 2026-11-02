# faremeter: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 5 (triage only, not evidence) |

**It is aimed at API providers and agent developers, and is sponsored by ABK Labs.**

Thesis fit: Direct fit with agents paying per API call over x402. It is a multi-standard, wallet- and chain-agnostic plumbing layer rather than an end-user product. The sources show no evidence of paid usage or customers.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: watch; critic by policy: watch, critic stated: watch)  
Receipts: 13 claims drafted, 69% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 4 as entailed, 9 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 4 | 4 | 3 |
| EXECUTION | 4 | 4 | 3 |

## Team
- One engineer dominates the repo: alexanderguy has 550 commits. [^c1] _(partial support: The receipt confirms alexanderguy's commit count but contains no comparison establishing dominance or evidence that the account represents an engineer.)_
- The project is sponsored and built by the engineers at ABK Labs, an existing company, plus open-source contributors. The founders' identities and the corporate structure of any spinout are not stated in the sources. [^c2] _(partial support: The receipt establishes ABK Labs sponsorship and engineering involvement but does not establish its corporate status or document the absence of founder and spinout information.)_

## Why Now
- Faremeter supports both v1 and v2 of Coinbase's x402, negotiated automatically. This shows it is following the standard as it moves. [^c3] _(partial support: The quote supports automatic negotiation between protocol versions but does not identify the protocol or establish responsiveness to standards changes.)_
- It also ships the MPP (Machine Payments Protocol) charge intent on Solana, while noting that the MPP spec is still evolving. This hedges across competing agent-payment standards. [^c4] _(partial support: The quote supports shipping a charge intent on Solana but does not identify MPP, describe its evolving specification, or establish a strategy of hedging competing standards.)_

## Competition
- Coinbase's facilitator dominates x402, with 68.2% of payments and 35.2% of volume. [^c5]
- Fluxa holds 56.7% of x402 volume on 9.7% of payments, so volume is concentrated in a few facilitators. Faremeter is not named among the facilitators in the market-share table, so its live x402 share is unmeasured here. [^c6] _(partial support: The receipt supports Fluxa's shares but cannot establish concentration across multiple facilitators or Faremeter's absence from the complete table.)_

## PMF
- Developer interest is modest: the main repo has 70 stars and 25 forks. This is adoption interest, not payment evidence. [^c7] _(partial support: The receipt confirms stars and forks, while characterizing interest as modest and interpreting these counts as adoption interest require judgment.)_
- There is no Hacker News traction: 0 stories with the company name in the title. [^c8] _(partial support: The metric establishes no matching company-name titles, which does not exclude other Hacker News coverage or engagement.)_

## Narrative
- The product breadth is wide for a young project, covering Solana and EVM wallet integrations alongside middleware, a facilitator and a gateway. The pitch is wallet- and chain-agnostic plumbing. [^c9] _(partial support: The quote supports Solana and EVM wallet integrations but not project age, middleware, facilitator, gateway, or wallet and chain agnosticism.)_

## Execution
- Commit velocity is high: 1180 commits in the last 90 days across the owner's top 5 repos. [^c10]
- The owner's top repos logged 1180 commits in the latest window. [^c11]

## Risk
- The GitHub profile lists the main repo's last push as 2026-07-06. [^c12]
- Outside contribution is thin. Partner-linked accounts such as the Crossmint one have a single commit each, so there is no evidence of deep third-party engagement. [^c13] _(partial support: One account's commit count does not establish partner affiliation, contribution counts for other accounts, or the overall depth of outside engagement.)_

## Scores (final, after the support review)

- **PMF 2/5**: Evidence is developer interest only: 70 stars and 25 forks [c7], no Hacker News presence [c8], and thin outside contribution with single-commit partner accounts [c13]. There is no evidence of payments, customers or facilitator share; Faremeter is absent from the market-share table [c6] while Coinbase dominates x402 [c5].
- **NARRATIVE 4/5**: The wedge is timely: x402 middleware and facilitator plumbing for agents and APIs, tracking x402 v1 and v2 [c3] and hedging with MPP on Solana [c4]. Wallet- and chain-agnostic breadth across Solana and EVM is a plausible platform path [c9]. The space is concentrated, with Coinbase leading payments and volume [c5] and Fluxa holding most volume [c6], and the founders and corporate structure are unclear [c2], so the edge is not yet stated.
- **EXECUTION 4/5**: Commit velocity is high at 1180 commits in 90 days across the owner's top 5 repos [c10][c11], and the project follows standards changes [c3][c4]. It is backed by an existing engineering company, ABK Labs [c2]. Caveats: one engineer holds 550 commits [c1], the 1180 figure spans several repos rather than the main one, and the last-push date of 2026-07-06 on the main repo [c12] is about four months old as of today, which tempers the velocity. c11 only restates c10 and gives no trend.

Re-score note: Changes to the rationale: removed the claim of a 'flat trend against the prior period', since c11 only restates the latest window and does not support a trend. Partial support on c1-c4, c6-c9 and c13 is treated as weak evidence.

## Risks

- No evidence of paid or transacting usage: faremeter does not appear in x402 facilitator market share, and the repo shows only modest forks and stars with thin outside contribution.
- Incumbent concentration: Coinbase holds most x402 payments and fluxa most volume, so a framework or facilitator layer must show an edge over default tooling.
- Key-person and structure risk: a single engineer accounts for most commits, and the project is sponsored by ABK Labs with no stated spinout, cap table or round.
- Standards risk: MPP is still evolving and AP2, Pay-Per-Crawl and L402 are only tracked, so the multi-standard bet could dilute focus or become obsolete.
- Data inconsistency: the last-push date of 2026-07-06 versus 1180 commits in 90 days needs verification before relying on the execution score.

## Questions for the founder call

- Is faremeter a standalone company or an ABK Labs project? Who would be the founders, and what is the intended entity, round and use of funds?
- How many production services or agents use Faremeter's middleware or facilitator today, and what are their payment counts and volume? Is the usd_per_tx figure organic?
- What is the business model: hosted facilitator fees, gateway SaaS, or enterprise support? What is the wedge against Coinbase's default facilitator and tools?
- Where is the 1180-commit activity happening if the main repo's last push was 2026-07-06? Which repos are active?
- What do the Crossmint and other wallet and chain partnerships involve (co-marketing, integrations, grants)?
- How do you weigh x402 against MPP, AP2 and Pay-Per-Crawl, and what would make you drop or add a standard?

_6 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: "alexanderguy (User): 550 commits" (github_contributors, https://github.com/faremeter/faremeter/graphs/contributors, snapshot `d_2bf293576b4555c8`, fetched 2026-11-02)
[^c2]: "Faremeter is sponsored and built by the engineers at [ABK Labs](https://abklabs.com) along with other open-source contributors." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c3]: "both v1 and v2 of the protocol, negotiated automatically." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c4]: "we currently ship the `charge` intent on Solana" (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c5]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c6]: "fluxa: 332,013 payments (9.7% of payments), 846,277 USD (56.7% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c7]: "Stars: 70. Forks: 25. Language: TypeScript." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
[^c8]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
[^c9]: "Wallet integrations for [Solana](./packages/wallet-solana), [EVM](./packages/wallet-evm)" (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c10]: warehouse metric `gh.commits_90d` = 1180.0 (as of 2026-11-01)
[^c11]: warehouse metric `gh.commits_90d` = 1180.0 (as of 2026-11-01)
[^c12]: "Created: 2025-06-11. Last push: 2026-07-06." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
[^c13]: "alberto-crossmint (User): 1 commits" (github_contributors, https://github.com/faremeter/faremeter/graphs/contributors, snapshot `d_2bf293576b4555c8`, fetched 2026-11-02)
