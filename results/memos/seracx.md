# sera-cx: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 24 (triage only, not evidence) |

**Open-source MCP server (plus CLI) that lets AI agents discover currencies, quote, route and execute stablecoin FX swaps on Sera Protocol, aimed at agent builders and ops engineers who need multi-currency settlement.**

Thesis fit: Direct fit with agent commerce: it is a tool layer for agents that move money across currencies, with x402 services in a companion repo. The wedge is stablecoin FX for agents, but there is no evidence yet of paying usage or of Sera Protocol volume driven through the MCP.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: watch; critic by policy: watch, critic stated: watch)  
Receipts: 13 claims drafted, 62% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 6 as entailed, 7 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- Josh-sera is the top contributor to sera-mcp with 11 commits. Five other contributors are listed after him, so there is some outside contribution, but the build looks concentrated in one person. [^c1] _(partial support: The quote supports Josh-sera's commit count but does not establish contributor ranking, other contributors, outside affiliation or concentration of work.)_
- The second-largest contributor, mashharuki, has 5 commits. No founders or titles are named in the sources, so team identity is unknown. [^c2] _(partial support: The quote supports mashharuki's commit count but establishes neither contributor ranking nor the absence of founder identities or titles.)_

## Why Now
- MCP is now supported by many agent hosts, so one server can reach Claude Code, Claude Desktop, Cursor and the OpenAI Agents SDK without custom integrations. [^c5] _(partial support: The quote asserts compatibility with the named hosts but does not establish a recent adoption shift or eliminate the need for custom integration work.)_

## Competition
- In x402 market structure, Coinbase handles 68.2% of payments. Sera does not appear as a facilitator in the market-structure data, so any x402 exposure is via services in the companion repo, not facilitation. [^c11] _(partial support: The quote supports Coinbase's payment share but establishes neither Sera's absence from the broader market nor an exclusive channel for its x402 exposure.)_

## PMF
- The product is a broad tool surface: the README claims 56 tools, 5 resources and 4 slash-prompt templates. [^c3]
- Developer interest is modest: sera-mcp has 22 stars and 34 forks. Forks well above stars is unusual and may reflect templating or hackathon-style copying rather than production use. [^c6] _(partial support: The quote supports the star and fork counts but provides no comparative benchmark or evidence of templating, hackathon copying or production use.)_
- Hacker News traction is 0 points in total. [^c7]

## Narrative
- A companion repo holds templates, examples and x402 services built on the MCP, suggesting a path from tool layer to agent-facing services. [^c13] _(partial support: The quote supports templates, examples, services and integrations built on the MCP, while the proposed expansion path is an inference.)_

## Execution
- The owner's top repos saw 94 commits in the last 90 days. [^c8]
- Commits in the prior 90 days window were 126. [^c9]
- The repo was created 2026-05-13 and last pushed 2026-09-01. [^c10]

## Risk
- The GitHub repo description says 32 tools. [^c4]
- The streamable HTTP transport has no built-in auth. Anyone who can reach the port can call every registered tool, including execution tools unless disabled. The README documents mitigations, but this matters for a product that moves money. [^c12] _(partial support: The quote supports reachability granting access to every registered tool but does not itself describe the transport, execution defaults or documented mitigations.)_

## Scores (final, after the support review)

- **PMF 2/5**: Evidence is developer interest only: 22 stars and 34 forks, with outside contributors listed [c1][c2][c6]. The fork/star ratio may reflect templating or hackathon copying rather than production use [c6]. Hacker News traction is 0 points [c7], and nothing shows payments, FX volume or customers. The tool surface is broad [c3], but breadth is not usage. Team identity is unknown [c2].
- **NARRATIVE 3/5**: A clear niche: stablecoin FX tooling for agents delivered over MCP, which many hosts now support [c5], with a possible path to agent-facing x402 services via the companion repo [c13]. But Coinbase handles 68.2% of x402 payments and Sera is not a facilitator [c11], so the edge against incumbents is not stated, and demand for agent FX is unproven. Inconsistent tool counts (56 in README vs 32 in the repo description) [c3][c4] and the unauthenticated HTTP transport on a money-moving product [c12] weaken credibility.
- **EXECUTION 3/5**: 94 commits in the last 90 days [c8] is real activity, but it is down from 126 in the prior 90-day window [c9]. The repo was created 2026-05-13 and last pushed 2026-09-01 [c10], roughly two months before today, so it looks stalled. Work is concentrated in one main author with 11 commits versus 5 for the next contributor [c1][c2].

Re-score note: Remaining partial claims are weak evidence, but nothing moved a score. I added citations to the tool-count inconsistency and auth risk in the narrative rationale and flagged that team identity is unknown. Watch rather than pass because the niche is clear and there are some outside contributors; re-check for payment or FX usage evidence and renewed shipping.

## Risks

- No evidence that agents actually transact through the MCP. Value to Sera Protocol and to the company is unproven, and the business model (fees, token, SaaS) is unclear.
- Dependence on a single underlying protocol (Sera Protocol) for liquidity and settlement. It is unclear whether sera-cx is the protocol team or a separate integrator, and how much stablecoin FX liquidity exists beyond USD pairs.
- Security and trust: unauthenticated HTTP transport and local-signer mode [c12] raise liability concerns for agents that hold funds.
- Shipping has slowed [c9] and the last push is two months old [c10]. Stale or inconsistent docs [c4] suggest limited maintenance bandwidth.
- A thin tool wrapper is easy to copy. Other MCP and x402 builders or the protocol itself can ship an equivalent.

## Questions for the founder call

- Who are the founders, and what is the relationship between sera-cx and Sera Protocol? Is this the protocol's own team, a spin-out, or a third-party integrator?
- What is the business model, and who pays? Per-swap fees, protocol revenue share, or hosted services?
- Why 34 forks against 22 stars? Who is forking, and are any forks production deployments?
- What caused the slowdown in commits and the gap since the last push in September?

_7 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: "Josh-sera (User): 11 commits" (github_contributors, https://github.com/sera-cx/sera-mcp/graphs/contributors, snapshot `d_8bbbff9536997d14`, fetched 2026-11-02)
[^c2]: "mashharuki (User): 5 commits" (github_contributors, https://github.com/sera-cx/sera-mcp/graphs/contributors, snapshot `d_8bbbff9536997d14`, fetched 2026-11-02)
[^c3]: "**56 tools**, 5 resources, 4 slash-prompt templates." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c4]: "Multi-currency settlement MCP for AI agents. 32 tools over Sera Protocol's stablecoin FX rails." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c5]: "Works with Claude Code, Claude Desktop, Cursor, OpenAI Agents SDK" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c6]: "Stars: 22. Forks: 34. Language: TypeScript." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c7]: warehouse metric `hn.points_total` = 0.0 (as of 2026-11-01)
[^c8]: warehouse metric `gh.commits_90d` = 94.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_prev_90d` = 126.0 (as of 2026-11-01)
[^c10]: "Created: 2026-05-13. Last push: 2026-09-01." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c11]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c12]: "Anyone who can reach the bound port can call every registered Sera tool." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c13]: "templates, examples, x402 services, and host integrations built on top of this MCP" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
