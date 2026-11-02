# devlab-group: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 28 (triage only, not evidence) |

**A dev-services consultancy (protocol and financial infrastructure engineering for clients) that also publishes Agent Commerce Gateway, an open-source, self-hosted, non-custodial gateway that lets existing HTTP APIs be discovered, called and paid for by AI agents over MCP, x402 and other protocols.**

Thesis fit: The product sits squarely in agent commerce: it wraps existing APIs with x402 payments, MCP and AP2 mandates. However, it is an open-source project from a services agency with no evidence of customers, payments or a venture-style company around it.

Recommendation after critique and committee: **pass** (first draft: pass; critic: pass)  
Receipts: 13 claims drafted, 62% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 3 as entailed, 9 as partial (tagged below) and withheld 1.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 2 |
| NARRATIVE | 3 | 3 | 4 |
| EXECUTION | 3 | 4 | 3 |

## Team
- The devlab.group website advertises protocol and infrastructure engineering for clients, and cites 20+ projects. [^c1] _(partial support: The quote supports the advertised project count but does not establish the firm's engineering services or client focus.)_
- Revinand is the top contributor to the agent-commerce repo with 137 commits. [^c2] _(partial support: The quote establishes Revinand's commit count but does not establish that this contributor ranks first.)_
- The website names Dmitry Sergeev as the direct contact, consistent with the contributor SergeevDmitry; other team members are not named in the sources. [^c3] _(partial support: The quote names Dmitry Sergeev but does not establish his contact role, connect him to a contributor account, or support the absence of other named team members.)_

## Why Now
- The gateway targets the emerging multi-protocol agent-commerce stack (MCP, x402, plus experimental MPP, A2A, ACP and AP2) behind one backend. [^c4] _(partial support: The quote supports a multi-protocol backend but does not identify the protocols, their maturity labels, or an emerging market shift.)_
- The product claims funds go directly to the merchant wallet and the gateway needs no private keys, a non-custodial positioning. [^c5]

## Competition
- In the x402scan facilitator data, Coinbase handles 69.7% of payments (2,610,865 payments). [^c6]

## PMF
- Outside adoption signals are small: the agent-commerce repo has 69 stars and 4 forks. [^c7] _(partial support: The quote supports the star and fork counts but does not establish that they represent outside users or meaningful adoption.)_
- The only payment evidence is a local demo using MockUSDC marked as local development only; no production payments or customers are shown. [^c8] _(partial support: The quote identifies a local-development payment proof but does not mention MockUSDC or establish the absence of production payments and customers.)_

## Execution
- Commits across the owner's top repos reached 285 in the last 90 days. [^c9]
- The agent-commerce repo was created on 2026-08-20 and last pushed on 2026-10-29, so it is about 10 weeks old and still actively maintained. [^c10] _(partial support: The quote supports the creation and last-push dates, while the approximate age is derived and continued active maintenance is an inference.)_
- Only x402 is marked supported; MPP, A2A, ACP and AP2 are labelled experimental in the README. [^c11] _(partial support: The quote establishes only that MPP is experimental and cannot support the status of the other protocols or the exclusivity asserted for x402.)_

## Risk
- The firm has no Hacker News presence: 0 stories mention the company name in the title. [^c12] _(partial support: The metric establishes zero matching story titles, which does not establish an absence of all Hacker News presence.)_

## Scores (final, after the support review)

- **PMF 2/5**: Outside adoption is small (69 stars, 4 forks) [c7], which is weak developer-interest evidence. The only payment evidence is a local MockUSDC demo, with no production payments or customers shown [c8]. The agency's client work [c1] is not evidence of gateway usage.
- **NARRATIVE 3/5**: The wedge is clear and timely: one backend exposing an existing API across MCP and x402 with non-custodial settlement [c4][c5]. But it is a tool from a services firm [c1], the facilitator market is concentrated around Coinbase at 69.7% [c6], and everything beyond x402 is experimental [c11]. The path from wedge to platform is not shown.
- **EXECUTION 3/5**: Velocity is high: 285 commits in 90 days across the owner's top repos [c9], and the repo was pushed recently after being created about 10 weeks earlier [c10]. But the team is thin, with one top contributor and one named contact [c2][c3], the commit count covers multiple repos rather than just this one, and only x402 is marked supported [c11]. That holds it at 3 rather than 4 given the partial support.

Re-score note: Execution lowered from 4 to 3 because the supporting claims are only partial: the 285 commits are across the owner's top repos, not this product, and the contributor evidence shows a thin team. PMF stays at 2 and Narrative at 3. Total is 8, below the 11 threshold, and PMF is below 3, so the recommendation stays pass.

## Risks

- Services agency, not a venture-scale product company: the gateway may be a lead-generation asset for consulting revenue, with no clear business model or fundable cap table.
- No evidence of real-world usage: only a mock-USDC demo and 69 stars; no production payments, merchants or customer logos.
- Protocol churn: most supported protocols (MPP, A2A, ACP, AP2) are experimental, and x402 traffic is dominated by Coinbase's facilitator, so differentiation as a self-hosted layer may be thin.
- Two-person effective core on the repo, and commit spike is recent (10 to 285), so sustainability is untested.

## Questions for the founder call

- Is the Agent Commerce Gateway intended to be a standalone company, or a showcase for the consulting business? Would the team stop client work?
- Are any merchants running the gateway in production, and what mainnet x402 volume has it settled?
- How do you monetize an Apache-2.0 self-hosted gateway (hosted version, support, facilitator fees)?
- Who is Revinand, and what are the roles of the team beyond Dmitry Sergeev?
- Which of MPP, ACP, AP2 and A2A do you expect real buyers to use, and how does the gateway stay current as the standards change?
- What is the relationship to the ERC-8409 draft and to other open-source projects in the portfolio?

## Withheld: real quote, but the critic says it does not support the claim

- ~~No funding, round or token evidence was found for the company.~~ (unsupported: An invitation to send a project brief is unrelated to whether funding, round, or token evidence exists.)

## Receipts

[^c1]: "20+ PROJECTS" (website, https://devlab.group, snapshot `d_a8853fc947857823`, fetched 2026-11-02)
[^c2]: "Revinand (User): 137 commits" (github_contributors, https://github.com/devlab-group/agent-commerce/graphs/contributors, snapshot `d_5eb8ec42715ebc96`, fetched 2026-11-02)
[^c3]: "Dmitry Sergeev" (website, https://devlab.group, snapshot `d_a8853fc947857823`, fetched 2026-11-02)
[^c4]: "One backend. Multiple agent-commerce protocols. Self-hosted and non-custodial." (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c5]: "Funds
go directly to the merchant wallet, and the gateway needs neither the buyer's
nor the merchant's private key." (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c6]: "coinbase: 2,610,865 payments (69.7% of payments)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c7]: "Stars: 69. Forks: 4." (github_profile, https://github.com/devlab-group, snapshot `d_216e113b6b2b5219`, fetched 2026-11-02)
[^c8]: "signed x402 payment proof (LOCAL DEVELOPMENT ONLY - DO NOT FUND)" (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c9]: warehouse metric `gh.commits_90d` = 285.0 (as of 2026-11-01)
[^c10]: "Created: 2026-08-20. Last push: 2026-10-29." (github_profile, https://github.com/devlab-group, snapshot `d_216e113b6b2b5219`, fetched 2026-11-02)
[^c11]: "<img alt="MPP" src="https://img.shields.io/badge/MPP-experimental-f0a30a">" (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c12]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
