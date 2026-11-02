# sera-cx: baseline diligence memo (AI first pass, not a decision)

**Open-source MCP server (TypeScript) that lets AI agents discover currencies, quote, route and execute stablecoin FX swaps on Sera Protocol, aimed at agent builders and ops engineers.**

Thesis fit: Direct fit with agents x payments: a standard tool layer for multi-currency stablecoin settlement, with x402 services mentioned in the companion repo. The sources show no evidence yet of paying or transacting usage.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 13 claims shipped, 0 withheld by the verifier (raw citation precision 0.85, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 2 | 2 |
| NARRATIVE | 3 | 3 |
| EXECUTION | 3 | 3 |

## Market
- The product exposes Sera Protocol's stablecoin FX settlement to agents as one standard tool layer. [^c1]
- The recommended 'standard' policy preset covers USDC, USDT, XSGD, JPYC, MYRT, TGBP and EURC, with a $5,000 per-transaction cap, a $50,000 daily cap and 10 bps slippage, which indicates a non-USD, Asia-heavy stablecoin focus. [^c10]

## PMF
- The sera-mcp repo has 22 stars and 34 forks, a sign of some developer interest but not of payment or transaction usage. [^c4]

## Narrative
- The README advertises compatibility with several agent hosts (Claude Code, Claude Desktop, Cursor, OpenAI Agents SDK, OpenClaw, Hermes, NanoClaw). [^c8]
- A companion repo is described as holding templates, examples, x402 services and host integrations built on the MCP, pointing toward an agent-commerce platform path. [^c9]

## Execution
- The README states the server ships 56 tools across 11 categories, covering discovery, pricing, quoting, treasury, execution and maker order tools. [^c2]
- The owner's top repos had 94 commits on default branches in the most recent quarter. [^c5]
- In the preceding quarter the same repos had 126 commits, so commit velocity has fallen. [^c6]
- sera-mcp was created 2026-05-13 and last pushed 2026-09-01. [^c7]
- The GitHub organization was created 2025-12-15, so the team is young. [^c12]

## Risk
- The GitHub repo description lists 32 tools for sera-mcp. [^c3]
- The streamable HTTP transport has no built-in authentication, so any party that can reach the port can call every registered tool, including execution tools if enabled. [^c11]

## Scores

- **PMF 2/5**: There is some developer interest (22 stars and 34 forks, [c4]) and a broad host-compatibility list [c8]. Nothing in the sources shows payments, volume, customers or named outside users. The forks may be mostly installs by people trying the tool, since contributor identity is unknown. There is no on-chain or revenue evidence.
- **NARRATIVE 3/5**: The wedge is clear: give agents multi-currency stablecoin FX through MCP [c1], with x402 services as an expansion path [c9] and a differentiated non-USD currency set [c10]. It depends heavily on Sera Protocol, and the relationship between sera-cx and the protocol is not stated. Demand for agent FX is asserted, not evidenced.
- **EXECUTION 3/5**: The team shipped a large tool surface [c2] and made 94 commits in the latest quarter [c5], but that is down from 126 in the prior quarter [c6]. The last push was 2026-09-01 [c7]. The README and repo description disagree on tool count [c3]. The sources do not show how many people are shipping.

## Risks

- Dependence on Sera Protocol liquidity and a single settlement venue: the sources give no evidence of FX volume or depth, and the stablecoin FX niche may stay small.
- No evidence of paying or transacting users; stars and forks [c4] may reflect curiosity rather than usage.
- Commit velocity is declining [c5][c6] and the last push was two months before the fetch [c7], with possible bus-factor risk.
- Security posture for agent-controlled funds: no built-in auth on HTTP transport [c11], plus a local-signer mode that holds private keys. A single incident could damage trust.
- Documentation inconsistency (32 vs 56 tools) [c3] suggests fast, loosely maintained releases.

## Questions for the founder call

- What is the relationship between sera-cx and Sera Protocol (same team, a partner, or a third-party wrapper), and who captures the revenue?
- Is there any real transaction volume via the MCP or x402 services today? Who are the first users, and are any of them outside the team?
- Who are the 34 forkers and any outside contributors, and what are they building?
- What is the business model (fees on swaps, SaaS, protocol incentives), and what is the path from the MCP wedge to a platform?
- Why did commit velocity drop, and how many engineers work on this full-time?
- How deep is liquidity in the non-USD pairs (XSGD, JPYC, MYRT, TGBP, EURC) for realistic agent-sized trades?

## Receipts

[^c1]: "Turns any agent into a multi-currency agent by exposing [Sera Protocol](https://docs.sera.cx) — stablecoin FX settlement — as one standard tool layer." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c2]: "56 tools across 11 categories" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c3]: "Multi-currency settlement MCP for AI agents. 32 tools over Sera Protocol's stablecoin FX rails." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c4]: "Stars: 22. Forks: 34. Language: TypeScript." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c5]: warehouse metric `gh.commits_90d` = 94.0 (as of 2026-11-01)
[^c6]: warehouse metric `gh.commits_prev_90d` = 126.0 (as of 2026-11-01)
[^c7]: "Created: 2026-05-13. Last push: 2026-09-01." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c8]: "Works with Claude Code, Claude Desktop, Cursor, OpenAI Agents SDK, **OpenClaw**, **Hermes**, **NanoClaw**, and any other MCP-compatible host." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c9]: "templates, examples, x402 services, and host integrations built on top of this MCP" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c10]: "| `standard` (recommended) | USDC, USDT, XSGD, JPYC, MYRT, TGBP, EURC | $5,000 | $50,000 | 10 bps |" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c11]: "Anyone who can reach the bound port can call every registered Sera tool." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c12]: "Account created: 2025-12-15." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c13]: warehouse metric `screen.rank` = 20.0 (as of 2026-11-01)
