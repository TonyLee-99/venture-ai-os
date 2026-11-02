# aibtcdev: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 23 (triage only, not evidence) |

**AIBTC is an agent network on Bitcoin where AI agents register a wallet and identity, message each other for 100 sats via x402, and earn BTC rewards, with an MCP server giving agents BTC/STX wallets, DeFi and x402 payments.**

Thesis fit: Strong topical fit: agents holding Bitcoin wallets and paying each other over x402 is agent commerce. The evidence is of registration and tooling, not of paying usage, and no x402 volume is attributed to the company.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: watch; critic by policy: watch, critic stated: watch)  
Receipts: 12 claims drafted, 50% passed the verifier on the first pass, 12 verified after one repair; the critic labelled 4 as entailed, 8 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 3 | 4 | 3 |
| EXECUTION | 4 | 4 | 3 |

## Team
- In the earlier ai-agent-crew repo, whoabuddy has 262 commits, the most of any listed contributor. Only handles are given, not names. [^c7] _(partial support: The quote supports whoabuddy's commit count but contains neither contributor comparisons nor evidence about the other contributors' names.)_

## Why Now
- The site links to the x402 protocol and ERC-8004 under protocols and tools, and builds its paid messaging on x402, which is the standard agents use to pay per call. [^c9] _(partial support: The quote lists the protocol names but does not establish paid messaging implementation or x402's asserted standard status.)_

## Competition
- In the x402 facilitator market, Coinbase holds 68.2% of payments, and aibtcdev does not appear among the listed facilitators. [^c10] _(partial support: The quote supports Coinbase's payment share but cannot establish aibtcdev's absence from the full facilitator list.)_

## PMF
- The AIBTC site reports 1,361 agents registered on the network. [^c1]
- Agents can send paid messages to any agent for 100 sats via x402, the only payment feature described on the site; no payment volume or count is given. [^c2] _(partial support: The quote supports paid messaging at 100 sats via x402 but establishes neither feature exclusivity nor the absence of payment statistics.)_
- The MCP server has 49 forks against 12 stars, a sign of developer adoption or experimentation; the sources do not say who the forkers are. [^c4] _(partial support: The quote supports the fork and star counts, but adoption or experimentation is an inference and forker identities are not established.)_
- Stars across all the owner's repos total 120. [^c12]

## Execution
- The aibtc-mcp-server repo was created 2026-01-09 and last pushed 2026-11-01. [^c3]
- The owner's top repositories recorded 102 commits in the most recent window. [^c5]
- The owner has 4473 total commits across its top repos, which points to a long-running build. [^c6] _(partial support: The metric supports the cumulative commit count but does not establish how long or consistently development occurred.)_

## Risk
- The ai-agent-crew repo is marked deprecated in favor of a separate Next.js frontend and a CrewAI backend. [^c8] _(partial support: The quote establishes deprecation in favor of replacements but does not identify their architecture or technologies.)_
- The company has no stage or funding evidence, and the warehouse shows 0 Hacker News points, so external validation is thin. [^c11] _(partial support: The metric supports zero Hacker News points but does not establish funding evidence, company stage, or external validation more broadly.)_

## Scores (final, after the support review)

- **PMF 2/5**: 1,361 registered agents [c1] and 49 forks against 12 stars [c4] show developer interest, but registrations and forks are not payments. The only payment feature is 100-sat paid messages via x402, with no volume or count given [c2]. aibtcdev does not appear among listed x402 facilitators [c10]. Owner-wide stars are modest at 120 [c12]. Who the forkers and registered agents are is unknown, and there is no evidence of non-team paying usage.
- **NARRATIVE 3/5**: The story is timely: Bitcoin-native agents that pay each other over x402 [c2][c9]. But the sources show only a narrow paid-messaging feature, the path from agent registry to a defensible business is unstated, and the earlier ai-agent-crew repo was deprecated, which signals a pivot [c8]. There is no funding or external validation [c11], and the x402 market is dominated by Coinbase at 68.2% [c10].
- **EXECUTION 4/5**: Shipping is recent and sustained: the MCP server was last pushed 2026-11-01 [c3], the owner's top repos recorded 102 commits in the latest window [c5], and cumulative commits total 4473 [c6].

## Risks

- Registrations may be inflated by operators or scripts, and the reward incentive could attract farming, so the 1,361 figure may not reflect real demand.
- No evidence of paying x402 usage or revenue: the 100 sat message price is tiny, and no volume is attributed to AIBTC.
- Key-person dependence on a single maintainer, and a prior pivot away from the CrewAI product.
- Unclear business model and funding status: the network is incentive-driven, and it is unknown who funds the BTC rewards and whether a token is planned.

## Questions for the founder call

- Who funds the BTC rewards and bounties, and what is the long-run revenue model beyond the 100 sat message fee?
- Who is on the team full-time, how are they structured, and how dependent is the project on whoabuddy?
- What drove the 49 forks of aibtc-mcp-server, and are they external developers or operators?
- What is the funding history, and is there any token or treasury plan?
- What is the relationship to Stacks and sBTC, and what is the plan if x402 settlement stays dominated by Coinbase and EVM chains?

_8 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: "1,361
agents
registered" (website, https://aibtc.com, snapshot `d_76ba5cffbf5b0186`, fetched 2026-11-02)
[^c2]: "Send messages to any agent for 100 sats via x402" (website, https://aibtc.com, snapshot `d_76ba5cffbf5b0186`, fetched 2026-11-02)
[^c3]: "Created: 2026-01-09. Last push: 2026-11-01." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c4]: "Stars: 12. Forks: 49. Language: TypeScript." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c5]: warehouse metric `gh.commits_90d` = 102.0 (as of 2026-11-01)
[^c6]: warehouse metric `gh.commits_total` = 4473.0 (as of 2026-11-01)
[^c7]: "whoabuddy (User): 262 commits" (github_contributors, https://github.com/aibtcdev/ai-agent-crew/graphs/contributors, snapshot `d_ce78c495614d3efb`, fetched 2026-11-02)
[^c8]: "This repo is now deprecated in favor of:" (github_readme, https://github.com/aibtcdev/ai-agent-crew, snapshot `d_4198603fbe742f78`, fetched 2026-11-02)
[^c9]: "x402 Protocol
ERC-8004
Moltbook" (website, https://aibtc.com, snapshot `d_76ba5cffbf5b0186`, fetched 2026-11-02)
[^c10]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c11]: warehouse metric `hn.points_total` = 0.0 (as of 2026-11-01)
[^c12]: warehouse metric `gh.stars_total_now` = 120.0 (as of 2026-11-01)
