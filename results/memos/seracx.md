# sera-cx: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 20 (triage only, not evidence) |

**Open-source MCP server that exposes Sera Protocol's stablecoin FX settlement (quote, route, swap, treasury, maker tools) to AI agents, aimed at agent builders and ops engineers who need multi-currency payments.**

Thesis fit: Direct fit with agents x payments: a tool layer that lets agents quote and settle non-USD stablecoin FX (XSGD, JPYC, EURC, etc.). It is a wedge on cross-currency agent commerce, but the evidence shows developer interest only, not paid usage, and it depends on Sera Protocol's own liquidity.

Recommendation after critique and committee: **pass** (first draft: pass; critic: watch)  
Receipts: 13 claims drafted, 54% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 4 as entailed, 9 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- Josh-sera is the top contributor to sera-mcp with 11 commits. [^c4] _(partial support: The quote establishes Josh-sera's commit count but does not establish their ranking among contributors.)_
- Outside contributors appear, e.g. mashharuki with 5 commits, suggesting some non-team code contributions. Founder identities and backgrounds are not in the sources. [^c5] _(partial support: The quote establishes mashharuki's contributions but neither their independence from the team nor the absence of founder information.)_

## Why Now
- Coinbase's x402 facilitator processed 2,610,865 payments in the latest reported window, showing agent-payment rails are live. [^c6] _(partial support: The quote supports Coinbase's payment count but does not identify the reporting window or establish that agents initiated those payments.)_

## Competition
- The x402 facilitator market is concentrated: Coinbase has 69.7% of payments. [^c7]

## PMF
- The README describes a product exposing 56 tools across 11 categories for stablecoin FX settlement to MCP-compatible agent hosts. [^c1] _(partial support: The quote supports the tool and category counts but does not establish stablecoin FX functionality or compatibility with agent hosts.)_
- The GitHub repository description for sera-mcp says it has 32 tools. [^c2]
- sera-mcp has 22 stars and 34 forks; forks exceeding stars suggests some hands-on developer experimentation, though no payment or customer usage is evidenced. [^c3] _(partial support: The quote establishes the stars and forks counts, but experimentation and the absence of customer or payment evidence are not established by those counts.)_
- There is no Hacker News presence (0 points), and no x402 usage metrics (such as usd_per_tx_30d) were provided for sera-cx. [^c13] _(partial support: Zero recorded Hacker News points does not establish no presence, and the metric says nothing about whether company-specific x402 usage metrics were provided.)_

## Narrative
- The README ties the product to a companion repo of templates, examples and x402 services, which points to an intended path from tool layer to agent-commerce platform. [^c12] _(partial support: The quote supports the listed extensions built on the MCP but does not establish a companion repository relationship or an intended platform strategy.)_

## Execution
- Commits across the owner's top repos totaled 94 in the most recent three-month window. [^c8]
- The org has 264 total commits on its top repos. [^c9]
- The last push to sera-mcp was 2026-09-01, about two months before the fetch date, and the repo was created 2026-05-13. [^c10] _(partial support: The quote supports both repository dates but does not include the fetch date needed to establish the elapsed time.)_

## Risk
- Streamable HTTP transport has no built-in authentication; anyone who can reach the port can call every registered tool. [^c11] _(partial support: The quote establishes that reachable callers can invoke every registered tool but does not itself identify the transport or explicitly state the absence of built-in authentication.)_

## Scores (final, after the support review)

- **PMF 2/5**: Evidence is limited to developer interest: 22 stars and 34 forks, plus an outside contributor with 5 commits [c3][c5]. Both claims are only partially supported. There is no payment, volume or customer evidence, and no x402 usage metrics were provided [c13]. Tool counts are inconsistent between the README (56) and the repo description (32) [c1][c2], so the product's actual scope is unclear. This is below the level for real adoption such as integrations or paying users.
- **NARRATIVE 3/5**: The wedge is stablecoin FX settlement for MCP-compatible agents, with a stated path to templates and x402 services [c1][c12]. Agent payment rails are live [c6], though Coinbase holds 69.7% of x402 payments, so the market is concentrated [c7]. The story is in the right space but generic. Scope claims are inconsistent [c1][c2], demand for non-USD agent settlement is unproven, and the unauthenticated HTTP transport is a credibility gap for a payments product [c11].
- **EXECUTION 3/5**: There is meaningful output: 264 total commits across top repos and 94 commits in the latest three-month window [c9][c8], with a contributor base that includes at least one outsider [c5]. Against that, the core work is concentrated in one top committer [c4], and the last push to sera-mcp was 2026-09-01, about two months before the fetch date [c10]. Steady but not sustained or fast-following.

Re-score note: Scores are unchanged (PMF 2, Narrative 3, Execution 3; total 8). The remaining claims are mostly partial, so they count as weak evidence, which does not justify raising any dimension. PMF stays below 3 because no payment, volume or customer usage is evidenced. The total is under the advance threshold of 11, and PMF is below the minimum of 3, so the recommendation remains pass. I dropped the draft's reference to a roughly 25% drop in 90-day commits because no remaining claim supports it; the execution rationale now relies on the 94-commit window [c8]. I also added the inconsistent tool counts [c1][c2] and the unauthenticated transport [c11] as caveats.

## Risks

- No evidence of paid or transacting usage; demand for agent-driven non-USD stablecoin FX is unproven and may be a small niche relative to USD x402 flows.
- Dependency on Sera Protocol (API, liquidity, FX depth); unclear whether sera-cx is the protocol team or a thin integration layer, and what the business model is.
- Slowing velocity: commits fell from 126 to 94 and the last push was 2026-09-01, with a single core committer.
- Security surface: execution and signing tools in an MCP, with an unauthenticated HTTP transport, create fund-loss risk if misdeployed, which can chill adoption.

## Questions for the founder call

- Who are the founders, and what is the relationship between sera-cx and Sera Protocol (same team, token, funding)?
- How many agents or developers actually run sera-mcp in production, and what swap volume has flowed through it?
- Where does revenue come from: protocol fees, x402 services, or SaaS? Is there a token?
- Why did commit velocity drop and why was there no push since 2026-09-01? What is the roadmap?
- What real use cases need agents to hold or convert non-USD stablecoins, and who are the first customers?
- Which is correct: 32 or 56 tools, and what is the real maturity of the maker and withdraw tooling?

## Receipts

[^c1]: "**56 tools across 11 categories**" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c2]: "Multi-currency settlement MCP for AI agents. 32 tools over Sera Protocol's stablecoin FX rails. Open source." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c3]: "Stars: 22. Forks: 34. Language: TypeScript." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c4]: "Josh-sera (User): 11 commits" (github_contributors, https://github.com/sera-cx/sera-mcp/graphs/contributors, snapshot `d_8bbbff9536997d14`, fetched 2026-11-02)
[^c5]: "mashharuki (User): 5 commits" (github_contributors, https://github.com/sera-cx/sera-mcp/graphs/contributors, snapshot `d_8bbbff9536997d14`, fetched 2026-11-02)
[^c6]: "coinbase: 2,610,865 payments (69.7% of payments), 534,034 USD (35.4% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c7]: "coinbase: 2,610,865 payments (69.7% of payments), 534,034 USD (35.4% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c8]: warehouse metric `gh.commits_90d` = 94.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_total` = 264.0 (as of 2026-11-01)
[^c10]: "Created: 2026-05-13. Last push: 2026-09-01." (github_profile, https://github.com/sera-cx, snapshot `d_4a064986e41fcdc9`, fetched 2026-11-02)
[^c11]: "Anyone who can reach the bound port can call every registered Sera tool." (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c12]: "templates, examples, x402 services, and host integrations built on top of this MCP" (github_readme, https://github.com/sera-cx/sera-mcp, snapshot `d_3d48a837c89cc67a`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.points_total` = 0.0 (as of 2026-11-01)
