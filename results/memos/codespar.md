# codespar: baseline diligence memo (AI first pass, not a decision)

**CodeSpar sells a governed payment layer for AI agents, delivered as a hosted MCP server and SDK. Agents pay and get paid (Pix, boleto, card, USDC) under signed spend mandates, with approvals and signed receipts, aimed at Latin American businesses. It also maintains open-source MCP servers that wrap LATAM commerce APIs.**

Thesis fit: Strong topical fit with AI agents x payments: mandates, approvals and audit trails for agent spend, plus standards work on x402, AP2 and ACP, anchored in a LATAM wedge (Pix, boleto, NF-e). Evidence of paying customers is absent, and the product demos are labeled sandbox data.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 14 claims shipped, 0 withheld by the verifier (raw citation precision 1.00, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 3 |
| NARRATIVE | 4 | 4 |
| EXECUTION | 4 | 3 |

## Market
- CodeSpar positions its product as one account where agents pay and get paid. [^c1]
- The product connects through hosted MCP or an SDK and works with common coding-agent clients. [^c14]

## PMF
- The open-source mcp-dev-latam repo has 277 stars and 52 forks, which shows developer interest. [^c4]
- Stars across the owner's repos total 313 today (current snapshot, not point-in-time). [^c5]
- The site's transaction feeds and receipt counters are labeled sandbox demo data, not customer volume. [^c6]
- The x402 monetization examples repo has only 3 stars, so the x402 side shows little outside traction. [^c13]

## Narrative
- The site says CodeSpar picks the payment method per call from Pix, boleto, card or USDC. [^c2]
- The mandate is described as a signed spend authority with cap, scope and expiry that the model cannot rewrite. [^c3]

## Execution
- Commits on the default branches of the owner's top 5 repos reached 380 in the last 90 days. [^c7]
- The prior 90-day period had 142 commits, so shipping velocity rose substantially. [^c8]
- The GitHub org was created in 2026, so the whole body of work is under a year old. [^c9]
- The company publishes contributions to agentic payment standards (KYA mandates, Pix push-rail for ACP, an OAC proposal, AP2 mapping). [^c10]

## Risk
- The company's own README states that its UCP, AP2 and x402 servers are deprecated because no live endpoint exists. [^c11]
- The README says only Stripe ACP reaches a live service among its agentic protocol servers. [^c12]

## Scores

- **PMF 3/5**: Real developer adoption of the open-source MCP servers (277 stars, 52 forks) [c4][c5], but no evidence of paying or transacting users. Site volumes are explicitly sandbox demo data [c6], and the x402 examples repo has little traction [c13].
- **NARRATIVE 4/5**: Clear wedge: governed agent spend (mandates, approvals, signed receipts) [c1][c3] on LATAM rails like Pix and boleto, with a multi-rail pitch [c2] and standards participation [c10]. The path from open-source tool layer to hosted platform is plausible [c14]. Docked because several protocol servers are deprecated [c11], so the bet is ahead of live usage.
- **EXECUTION 4/5**: Sustained, accelerating shipping: 380 commits in 90 days versus 142 in the prior 90 [c7][c8], plus standards contributions [c10]. The org is under a year old [c9], and team size and contributor count are unknown, so not a 5.

## Risks

- No evidence of paying or transacting customers: all payment feeds and counters on the site are labeled sandbox demo data, so PMF rests on GitHub stars and forks only [c6][c4].
- Protocol bet risk: three of the four agentic-protocol MCP servers are deprecated with no live endpoint, and the x402 examples repo has little traction, so the wedge may be ahead of real usage [c11][c12][c13].
- Regulatory and partner dependence: moving BRL via Pix and boleto for agents relies on licensed providers and bank integrations, and the sources do not show who holds licences or custody.
- Breadth versus depth: a large catalog of MCP servers plus a hosted platform and standards work from a young org may spread a small team thin, and several servers are already deprecated [c9][c11].

## Questions for the founder call

- Are there any live, paying customers or real (non-sandbox) payment volume through the hosted platform? What is the monthly settled amount?
- Who is the licensed party for moving money (Celcoin appears in the demo)? What are the custody, KYC and compliance arrangements, and what are the take rates?
- How many people are on the team, and who writes the commits? Is it one maintainer with AI assistance?
- Who is actually using mcp-dev-latam (npm downloads, registry installs), and does that usage convert to the hosted product?
- Given three protocol servers were deprecated, what is the plan for x402 and AP2, and how do you choose which standards to support?
- What is the pricing model, and what is the funding history so far?

## Receipts

[^c1]: "One account where agents pay and get paid." (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c2]: "One call. CodeSpar picks the payment method that fits: Pix, boleto, card or USDC." (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c3]: "A signed spend authority: cap, scope, expiry. The model can't rewrite it." (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c4]: "Stars: 277. Forks: 52. Language: TypeScript." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c5]: warehouse metric `gh.stars_total_now` = 313.0 (as of 2026-11-01)
[^c6]: "Sandbox run · demo data" (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.commits_90d` = 380.0 (as of 2026-11-01)
[^c8]: warehouse metric `gh.commits_prev_90d` = 142.0 (as of 2026-11-01)
[^c9]: "Account created: 2026-03-18." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c10]: "Open CodeSpar contributions to agentic payment standards: KYA verifiable agent mandates, Pix push-rail for ACP, OAC proposal (Agentic Commerce Consortium), AP2 mapping." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c11]: "UCP, AP2 and x402 are deprecated: no live endpoint." (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c12]: "Only Stripe ACP reaches a live service today; the other three are deprecated" (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c13]: "Stars: 3. Forks: 1. Language: JavaScript." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c14]: "Hosted MCP or SDK. Works with Claude Code, Cursor, Codex CLI and any client that speaks MCP." (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
