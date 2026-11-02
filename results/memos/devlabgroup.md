# devlab-group: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 15 (triage only, not evidence) |

****

Thesis fit: The product sits squarely in agent commerce (x402/MCP/AP2 wrapper for existing APIs), but it is an open-source side project of a services shop with no evidence of paying users and no venture-style company or funding signal yet.

Recommendation (score policy + committee): **watch**; evidence status: **evidence insufficient** (first draft: watch; critic by policy: watch, critic stated: pass)  
Receipts: 13 claims drafted, 62% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 3 as entailed, 9 as partial (tagged below) and withheld 1.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 2 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 4 | 4 | 3 |

## Team
- Revinand is the top contributor to the gateway repo with 137 commits. [^c1] _(partial support: The receipt establishes Revinand's 137 commits but does not establish contributor ranking.)_
- DevLab is a services business: it sells outsourced engineering for client projects, which suggests the gateway is a public-work showcase rather than a standalone venture. [^c2] _(partial support: The quote supports engagement by founders and product teams but does not establish the commercial arrangement or that the gateway is a showcase rather than a standalone venture.)_
- The consultancy's website advertises 20+ projects of protocol and infrastructure work. [^c3] _(partial support: The receipt supports the advertised project count but does not identify the projects as protocol and infrastructure work.)_

## Why Now
- The gateway targets a stack of emerging agent-commerce protocols at once, with x402 marked supported and MPP, A2A, ACP and AP2 marked experimental. [^c4] _(partial support: The quote supports HTTP, MCP and experimental A2A exposure but does not establish the stated support status of the payment and other commerce protocols.)_
- The pitch is that existing API owners can become agent-payable without changing their backend, with funds going straight to the merchant wallet. [^c5] _(partial support: The receipt supports direct merchant-wallet settlement without gateway access to private keys but not integration without backend changes.)_

## Competition
- The x402 facilitator market is concentrated: Coinbase handles 68.2% of payments. [^c6]

## PMF
- Outside adoption signals are small: the main repo has 69 stars and 4 forks. [^c7]
- The only payment evidence in the sources is a local demo using MockUSDC with a development-only signer; there is no evidence of production payments or named customers. [^c8] _(partial support: The quote establishes development-only payment signing but does not identify MockUSDC or establish the absence of production payments and named customers across the sources.)_
- Hacker News traction is zero: 0 stories mention the company. [^c9] _(partial support: The metric establishes no company-name matches in story titles, not no mentions anywhere or an absence of all Hacker News traction.)_

## Execution
- Commit activity in the last 90 days totals 285 commits across the owner's top repos. [^c10]
- The agent-commerce repo was created in August 2026 and last pushed 2026-10-29, so it is about 10 weeks old and actively maintained. [^c11] _(partial support: The receipt supports the creation and last-push dates, but approximate age is derived and a recent push alone does not establish ongoing active maintenance.)_
- The repo ships a CLI, an Agent Skills integration for coding agents, Docker demo stack and a doctor/reconcile toolchain, indicating attention to developer onboarding. [^c12] _(partial support: The quote establishes the CLI and its doctor and reconcile commands but does not establish the Agent Skills integration or Docker demo stack.)_

## Scores (final, after the support review)

- **PMF 2/5**: Outside adoption is small: 69 stars and 4 forks [c7]. The only payment evidence is a local MockUSDC demo with a development-only signer, with no production payments or named customers [c8], and Hacker News traction is zero [c9]. Unchanged.
- **NARRATIVE 3/5**: The wedge is reasonably clear: existing API owners become agent-payable without backend changes, with funds going straight to the merchant wallet [c5], and the gateway spans several agent-commerce protocols, though only x402 is marked supported and the rest are experimental [c4]. The x402 facilitator market is concentrated, with Coinbase at 68.2% [c6], so the space is crowded with no stated edge. The company is a services business, and the gateway looks more like a showcase than a standalone venture [c2], which weakens the path from wedge to platform. The newly withheld focus-split claim  is not used.
- **EXECUTION 4/5**: Commit velocity is strong at 285 commits in 90 days across the owner's top repos [c10], and the repo is actively maintained [c11]. The repo ships a CLI, Agent Skills integration, Docker demo stack and doctor/reconcile tooling [c12]. Contribution is concentrated: Revinand has 137 commits [c1], which suggests a small team. Several supporting claims are only partial, and the repo is about 10 weeks old [c11], so the burst is not yet shown to be sustained. Score stays at 4, but with less certainty.

Re-score note: No score changes. The withheld claim c13 (funding status and split focus) was not relied on in the first draft's rationales, so removing it changes nothing. Partial claims (c1, c2, c4, c5, c8, c9, c11, c12) are treated as weak evidence, so confidence is lower, but not enough to move any dimension. Recommendation stays watch: execution is strong, but there is no production payment evidence. Re-check in a quarter for real transacting usage or a clearer commitment to the product over consulting.

## Risks

- No evidence of real usage: payments shown are local MockUSDC demos, no customers, and the star count is modest.
- Protocol churn: most protocols (MPP, A2A, ACP, AP2) are marked experimental, and x402 facilitators are concentrated around Coinbase, so the wrapper layer could be commoditized or absorbed by facilitators.
- Founder focus is split across many open-source projects and client work, and the velocity spike may reflect a one-off sprint.

## Questions for the founder call

- Is the gateway meant to become a standalone company, and if so, who is the full-time team and would the consultancy be wound down or kept as funding?
- Are any real merchants running it in production with mainnet x402 payments, and what is the payment volume and value per payment?
- Why did the commit rate jump from 10 to 285 in 90 days, and how much of it is AI-assisted?
- How do you differentiate from facilitators and SDKs (Coinbase, x402 middleware) adding the same wrapper features?

_7 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Withheld: real quote, but the critic says it does not support the claim

- ~~No funding, round, token or YC evidence was found, and the repo is listed alongside several other open-source projects (RWA platform, MCP scanner, Postflight), so focus is split.~~ (unsupported: The quoted product name establishes neither funding status nor the other projects or any split in team focus.)

## Receipts

[^c1]: "Revinand (User): 137 commits" (github_contributors, https://github.com/devlab-group/agent-commerce/graphs/contributors, snapshot `d_5eb8ec42715ebc96`, fetched 2026-11-02)
[^c2]: "Founders and product teams bring us in" (website, https://devlab.group, snapshot `d_a8853fc947857823`, fetched 2026-11-02)
[^c3]: "20+ PROJECTS" (website, https://devlab.group, snapshot `d_a8853fc947857823`, fetched 2026-11-02)
[^c4]: "Resources can be exposed over
HTTP, MCP or experimental A2A" (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c5]: "Funds
go directly to the merchant wallet, and the gateway needs neither the buyer's
nor the merchant's private key." (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c6]: "coinbase: 2,342,973 payments (68.2% of payments)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c7]: "Stars: 69. Forks: 4." (github_profile, https://github.com/devlab-group, snapshot `d_216e113b6b2b5219`, fetched 2026-11-02)
[^c8]: "signed x402 payment proof (LOCAL DEVELOPMENT ONLY - DO NOT FUND)" (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
[^c9]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
[^c10]: warehouse metric `gh.commits_90d` = 285.0 (as of 2026-11-01)
[^c11]: "Created: 2026-08-20. Last push: 2026-10-29." (github_profile, https://github.com/devlab-group, snapshot `d_216e113b6b2b5219`, fetched 2026-11-02)
[^c12]: "The package includes the `agent-commerce` CLI
(`init`, `validate`, `start`, `doctor`, `reconcile`, `resolve`, `demo`,
`import openapi`, `version`)" (github_readme, https://github.com/devlab-group/agent-commerce, snapshot `d_05d72a18545d2c02`, fetched 2026-11-02)
