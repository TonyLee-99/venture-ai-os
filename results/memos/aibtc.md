# aibtcdev: baseline diligence memo (AI first pass, not a decision)

**Open-source tooling that gives AI agents Bitcoin/Stacks wallets and payment capabilities, now centered on a Bitcoin-native MCP server for agents (BTC/STX wallets, DeFi yield, sBTC peg, NFTs, x402 payments), aimed at developers building agents.**

Thesis fit: Direct fit with AI agents x payments: the current flagship repo targets agent wallets and x402 payments on Bitcoin/Stacks via MCP. Evidence of paying users or transacting volume is absent from the sources, so fit is on narrative and shipping, not demonstrated demand.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 12 claims shipped, 0 withheld by the verifier (raw citation precision 0.75, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 2 |
| NARRATIVE | 4 | 3 |
| EXECUTION | 4 | 3 |

## Market
- The org maintains 40 public non-fork repositories, a broad surface for a pre-seed team. [^c10]
- The original ai-agent-crew repo had 47 stars and 17 forks. [^c11]

## PMF
- The aibtc-mcp-server repo has 49 forks, more than its 12 stars, which suggests developers are copying or building on it. [^c6]
- Total stars across the org's repos are 120, a small audience. [^c7]

## Narrative
- The aibtc-mcp-server repo describes itself as a Bitcoin-native MCP server for AI agents covering BTC/STX wallets, DeFi yield, sBTC peg, NFTs, and x402 payments. [^c1]
- The org ranks 24th among sourced candidates on a GitHub-only screening model. [^c12]

## Execution
- The MCP server repo was created 2026-01-09 and last pushed 2026-11-01, one day before the fetch date. [^c2]
- Commits on default branches of the top 5 repos reached 102 in the last 90 days. [^c3]
- The previous quarter had 91 commits on default branches of the owner's top repos. [^c4]
- The org has 4473 total commits on those branches, showing a long working history. [^c5]
- The earlier ai-agent-crew repo is deprecated in favor of a Next.js front-end and a CrewAI Python back-end, showing the team has pivoted product direction at least once. [^c8]

## Risk
- The original crew product was labeled an early experiment where agents act automatically and run at the user's own risk. [^c9]

## Scores

- **PMF 3/5**: Developer adoption signals exist, notably 49 forks on the MCP server [c6], but total stars are small [c7] and nothing in the sources shows payments, transacting agents, or paying customers. That matches the rubric's 3 band at most.
- **NARRATIVE 4/5**: The story is timely and specific: an MCP server giving agents Bitcoin wallets and x402 payments [c1]. It is held back from 5 by the earlier product pivot [c8], a broad feature list (DeFi, NFTs, sBTC) rather than a single wedge [c1], and no stated competitive edge.
- **EXECUTION 4/5**: Shipping is recent and rising [c2][c3][c4], with a deep commit history [c5]. The sources don't show how many people contribute, and the team has already deprecated one product [c8], so I stop short of 5.

## Risks

- No evidence of paid or transacting usage: the sources show forks and commits but no agent payment volume, customers or revenue.
- Narrow ecosystem dependence: the product is built around Bitcoin/Stacks, so growth depends on that ecosystem's agent and x402 adoption, which the sources do not evidence.
- Focus risk: 40 public repos, a prior deprecated product, and a wide feature list (wallets, DeFi, NFTs, sBTC, x402) suggest scope sprawl for a small team.
- Commodity risk: wallet and payment MCP servers can be replicated by larger agent-infra and wallet providers, and the sources name no competitors or moat.

## Questions for the founder call

- Who actually uses the MCP server, and how many agents or wallets transact through it per week? Is there any x402 payment volume?
- How is the 49-fork count distributed: real integrations, hackathon copies, or internal use?
- What is the business model (token, hosted service, fees, grants), and how does the company capture value from open-source tooling?
- How many people contribute to the 102 recent commits, and who are the core maintainers?
- Why was the earlier CrewAI product deprecated, and what did the team learn that shaped the MCP server?
- Which competitors (EVM-based x402 stacks, other wallet MCPs) do customers compare against, and why choose a Bitcoin-native option?

## Receipts

[^c1]: "Bitcoin-native MCP server for AI agents: BTC/STX wallets, DeFi yield, sBTC peg, NFTs, and x402 payments." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c2]: "Created: 2026-01-09. Last push: 2026-11-01." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c3]: warehouse metric `gh.commits_90d` = 102.0 (as of 2026-11-01)
[^c4]: warehouse metric `gh.commits_prev_90d` = 91.0 (as of 2026-11-01)
[^c5]: warehouse metric `gh.commits_total` = 4473.0 (as of 2026-11-01)
[^c6]: "Stars: 12. Forks: 49. Language: TypeScript." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.stars_total_now` = 120.0 (as of 2026-11-01)
[^c8]: "This repo is now deprecated in favor of:" (github_readme, https://github.com/aibtcdev/ai-agent-crew, snapshot `d_4198603fbe742f78`, fetched 2026-11-02)
[^c9]: "This is an early experiment, agents do automatic things, here be dragons, run at your own risk." (github_readme, https://github.com/aibtcdev/ai-agent-crew, snapshot `d_4198603fbe742f78`, fetched 2026-11-02)
[^c10]: warehouse metric `gh.public_repos` = 40.0 (as of 2026-11-01)
[^c11]: "Stars: 47. Forks: 17. Language: Python." (github_profile, https://github.com/aibtcdev, snapshot `d_b8ac0b5cfb3102a8`, fetched 2026-11-02)
[^c12]: warehouse metric `screen.rank` = 24.0 (as of 2026-11-01)
