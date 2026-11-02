# aibtcdev: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 24 (triage only, not evidence) |

**AIBTC runs an agent network on Bitcoin/Stacks where operators register AI agents with wallets, identity and paid x402 messaging to earn BTC rewards, plus an MCP server giving agents BTC/STX wallets, DeFi, and x402 payments.**

Thesis fit: Direct fit with AI agents x payments: agents hold Bitcoin wallets and pay each other via x402 (100 sats per message). However, the evidence shows registrations rather than paying usage, and x402 market data shows no facilitator attributable to AIBTC.

Recommendation after critique and committee: **watch** (first draft: watch; critic: watch)  
Receipts: 12 claims drafted, 50% passed the verifier on the first pass, 12 verified after one repair; the critic labelled 0 as entailed, 12 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 4 | 4 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- whoabuddy is the top contributor to the legacy ai-agent-crew repo, with 262 commits. [^c3] _(partial support: The quote supports the contributor's identity and commit count but does not establish contributor ranking, repository identity or legacy status.)_
- human058382928 is the second-listed contributor to ai-agent-crew, with 30 commits. [^c4] _(partial support: The quote supports the contributor's identity and commit count but does not establish listing position or repository identity.)_

## Why Now
- The MCP server targets Claude Code and x402 payments, positioning around agents with their own wallets paying for services on Bitcoin. [^c10] _(partial support: The quote supports Bitcoin-native agent wallets and x402 payments but does not mention Claude Code or demonstrate agents paying for services.)_

## Competition
- The x402 facilitator market is concentrated: Coinbase handles 69.7% of payments, and AIBTC does not appear among the listed facilitators. [^c9] _(partial support: The quote supports Coinbase's payment share but cannot establish AIBTC's absence from the facilitator list or concentration across the remaining market.)_

## PMF
- AIBTC's website reports 1,361 registered agents on its network. [^c1] _(partial support: The quote supplies the number but does not identify it as registered agents and falls below the required minimum quote length.)_
- Agents can send paid messages to any other agent for 100 sats via x402, but no payment volume or transaction counts are given in the sources. [^c2] _(partial support: The quote supports the messaging capability and price but cannot establish that payment volume and transaction counts are absent from all sources.)_
- The aibtc-mcp-server has 49 forks against 12 stars, a fork-heavy ratio that suggests developer experimentation (or copying for agent setups) rather than broad interest. [^c7] _(partial support: The quote supports the star and fork counts but does not identify the repository or establish why developers forked it or how broad interest is.)_

## Execution
- Commits across the owner's top repos totaled 102 in the latest window, which indicates ongoing shipping. [^c5] _(partial support: The metric supports the commit count within its defined repository scope, while interpreting commits as shipping requires additional evidence.)_
- The aibtc-mcp-server repo was created 2026-01-09 and last pushed 2026-11-01, indicating active recent work on the x402-capable product. [^c6] _(partial support: The quote supports the dates but does not identify the repository, establish x402 capability or demonstrate substantive product work.)_
- The owner has 4473 total commits across its top repos, which shows long-running sustained output. [^c12] _(partial support: The metric supports the cumulative commit count within its defined scope but does not establish sustained output over time.)_

## Risk
- The original ai-agent-crew product is deprecated in favor of a new frontend and backend, so the company has pivoted at least once. [^c8] _(partial support: The quote establishes repository deprecation but neither identifies its replacements nor demonstrates a company pivot.)_
- There is no outside attention signal on Hacker News: 0 stories mention the company name in the title. [^c11] _(partial support: The metric establishes no matching title stories within the dataset but does not rule out other Hacker News attention.)_

## Scores (final, after the support review)

- **PMF 2/5**: Only weak evidence of outside interest: 1,361 registered agents [c1] and 49 forks against 12 stars [c7]. Both claims are only partially supported, and registrations may be incentive-driven. The paid-message feature via x402 is described, but the sources give no payment volume, transaction counts or paying customers [c2], and no x402 usd_per_tx figure is available. There is no proof of transacting usage, so this stays below 3.
- **NARRATIVE 4/5**: The story is clear and timely: agents with their own Bitcoin wallets that pay and get paid via x402, delivered through MCP tooling for Claude Code [c2][c10]. A path from wallet tooling to an agent network is plausible. Held back by a pivot history [c8], the niche Bitcoin/Stacks ecosystem, Coinbase's 69.7% share of x402 facilitator payments with AIBTC not listed [c9], and no outside attention on Hacker News [c11]. Both [c9] and [c10] are partially supported, so 4 is held with less confidence.
- **EXECUTION 3/5**: Commit activity is ongoing, with 102 commits in the latest window [c5], a recent push on the MCP server [c6], and 4473 cumulative commits across top repos [c12]. Contributor evidence is concentrated: whoabuddy has 262 commits on the legacy repo against 30 for the second contributor [c3][c4]. Contributor data for the current repos is missing, so the team size behind recent shipping is unclear. Claims are partial, so 3 is a ceiling rather than a floor.

Re-score note: Scores are unchanged from the first draft: PMF 2, Narrative 4, Execution 3, total 9. All 12 remaining claims are partially supported, so I treated them as weak evidence and added caveats to the rationales. Narrative confidence is lower and Execution is capped at 3 because current-repo contributors are unknown. The recommendation stays watch: the total is below 11 and PMF is below 3, so advance is ruled out. Pass is not warranted given the clear, timely narrative and active shipping. Re-check when payment volume or transaction data appears.

## Risks

- No evidence of real paid usage: registered agents are a vanity metric if the 100-sat messages and rewards are mostly self-funded or incentive-driven.
- Key-person risk: a single contributor accounts for the large majority of commits on the legacy repo, and the current team is not documented.
- Pivot history (CrewAI Streamlit app to frontend/backend to agent network/MCP) suggests the focus may shift again.
- Ecosystem risk: x402 volume is concentrated in Coinbase and other EVM/Solana-centric facilitators, while AIBTC bets on Bitcoin/Stacks, a small base of agent developers and services.

## Questions for the founder call

- How many x402 payments settle on the AIBTC network per week, at what average value, and what share is between agents not controlled by the team?
- How much of the 1,361 registrations are active (heartbeat, transactions) and how many are driven by BTC reward incentives?
- Who funds the BTC rewards and bounties, and what is the long-term revenue model (fees, sponsor relay, services)?
- Who is on the full-time team now, and what is the legal and funding structure (stage and prior raises are unknown)?
- Why Bitcoin/Stacks rather than building on EVM/Solana where x402 volume is concentrated, and does AIBTC plan to run a facilitator?

## Receipts

[^c1]: "1,361" (website, https://aibtc.com, snapshot `d_76ba5cffbf5b0186`, fetched 2026-11-02)
[^c2]: "Send messages to any agent for 100 sats via x402" (website, https://aibtc.com, snapshot `d_76ba5cffbf5b0186`, fetched 2026-11-02)
[^c3]: "whoabuddy (User): 262 commits" (github_contributors, https://github.com/aibtcdev/ai-agent-crew/graphs/contributors, snapshot `d_ce78c495614d3efb`, fetched 2026-11-02)
[^c4]: "human058382928 (User): 30 commits" (github_contributors, https://github.com/aibtcdev/ai-agent-crew/graphs/contributors, snapshot `d_ce78c495614d3efb`, fetched 2026-11-02)
[^c5]: warehouse metric `gh.commits_90d` = 102.0 (as of 2026-11-01)
[^c6]: "Created: 2026-01-09. Last push: 2026-11-01." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c7]: "Stars: 12. Forks: 49. Language: TypeScript." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c8]: "This repo is now deprecated in favor of:" (github_readme, https://github.com/aibtcdev/ai-agent-crew, snapshot `d_4198603fbe742f78`, fetched 2026-11-02)
[^c9]: "coinbase: 2,610,865 payments (69.7% of payments)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c10]: "Bitcoin-native MCP server for AI agents: BTC/STX wallets, DeFi yield, sBTC peg, NFTs, and x402 payments." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c11]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
[^c12]: warehouse metric `gh.commits_total` = 4473.0 (as of 2026-11-01)
