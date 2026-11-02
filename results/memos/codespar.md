# codespar: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 17 (triage only, not evidence) |

**CodeSpar sells an account for AI agents to pay and get paid in Latin America: signed spending mandates, approval rules and signed receipts across Pix, boleto, card and USDC, delivered via hosted MCP/SDK, plus an open-source library of LATAM commerce MCP servers.**

Thesis fit: Strong topical fit with agent commerce: governance (mandates, approvals, audit) for agents spending on local rails like Pix and boleto, with x402 as one leg. But x402 is a side feature, the product demos are sandbox data, and there is no evidence yet of real paying usage.

Recommendation after critique and committee: **watch** (first draft: watch; critic: pass)  
Receipts: 13 claims drafted, 69% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 5 as entailed, 8 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 4 | 4 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- One person does nearly all the work in the main repo: fabianocruz has 244 commits. [^c1] _(partial support: The quote establishes fabianocruz's commit count but provides neither a comparison with other contributors nor evidence that commits represent nearly all work.)_
- The about page says the company is built in New York and Rio de Janeiro by the team behind Zoop. Individual founders other than the top committer are not named in the sources. [^c2] _(partial support: The quote supports the stated locations and Zoop affiliation but cannot establish whether individual founders are named elsewhere in the sources.)_

## Why Now
- The README argues that four agentic payment protocols are shipping in parallel and do not compose cleanly with each other or with regional rails. [^c3] _(partial support: The quote supports the README's interoperability argument but does not establish the number of protocols or that they are shipping in parallel.)_

## Competition
- In x402 facilitator share, Coinbase holds 69.7% of payments. [^c4]

## PMF
- The open-source repo mcp-dev-latam has 277 stars and 52 forks, which is developer interest but not payment evidence. [^c5]
- The website's transaction feeds, receipt counters and settled-today figures are labeled sandbox and demo data, so they are not evidence of customers or volume. [^c6] _(partial support: The quote explicitly labels sandbox demo data but does not by itself establish that this label covers every feed, counter and settlement figure named.)_
- The x402 examples repo, the company's direct x402 monetization work, has 3 stars and 1 fork, which is minimal adoption. [^c12] _(partial support: The quote establishes the star and fork counts but does not establish the repository's role or actual adoption beyond those interest indicators.)_

## Narrative
- The company states its thesis as control being the product: deciding whether an agent may move money, and proving what happened. [^c10]

## Execution
- Commits on the owner's top repos were 380 in the latest three-month window. [^c7]
- Total commits on the tracked branches are 1096. [^c8]
- Some governance features are still unshipped: audit trail CSV export, reconciliation and verified approver are marked as rolling out on the product page. [^c11] _(partial support: The quote marks CSV export and reconciliation as rolling out but omits verified approver and does not clearly mark audit trail export itself as unshipped.)_

## Risk
- The company's own README says its x402 server, along with UCP and AP2, is deprecated because the default host has no live endpoint, and that eight more servers were deprecated for the same reason. This is a monitor-style measurement dated 2026-09-27 and shows breadth outrunning maintenance. [^c9] _(partial support: The quote supports the named protocol deprecations and measurement date but omits the additional server deprecations and does not establish that maintenance lag caused them.)_
- No funding, stage, token or YC evidence was found, and Hacker News shows 0 stories mentioning the company. [^c13] _(partial support: The metric supports zero matching Hacker News stories under the defined title search but says nothing about funding, stage, token or YC evidence.)_

## Scores (final, after the support review)

- **PMF 2/5**: Developer interest is real but modest: 277 stars and 52 forks on mcp-dev-latam [c5], which the claim itself says is not payment evidence. The website's transaction feeds and settled figures are sandbox/demo data [c6], and the direct x402 examples repo has 3 stars and 1 fork [c12]. No paying customers or on-chain volume are evidenced, and no funding or outside validation was found [c13]. This is above the rubric's 1 (some outside developer adoption) but below 3 (the adoption is thin and the evidence is partial).
- **NARRATIVE 4/5**: The thesis is clear and timely: control is the product, i.e. deciding whether an agent may move money and proving what happened [c10], against a backdrop of four agentic payment protocols shipping in parallel that do not compose with each other or regional rails [c3]. The Zoop-team pedigree and NY/Rio base [c2] give a plausible LATAM angle, though that claim is only partially supported and no founders besides the top committer are named. Held back from 5 because the product spans many surfaces and several protocol bets are deprecated [c9], and the path from wedge to platform is not yet evidenced.
- **EXECUTION 3/5**: Velocity is high: 380 commits on the owner's top repos in the latest three-month window [c7] and 1096 total commits [c8]. However, work is heavily concentrated in one committer, fabianocruz with 244 commits [c1], the team is otherwise unnamed [c2], governance features such as CSV audit export, reconciliation and verified approver are still rolling out [c11], and the README says the x402, UCP and AP2 servers plus eight more were deprecated because the default host has no live endpoint [c9]. Strong output but single-maintainer concentration and breadth outrunning maintenance keep it at 3.

Re-score note: Scores unchanged from the first draft (PMF 2, Narrative 4, Execution 3; total 9). Partial claims were treated as weak evidence; none changed a score. PMF stays at 2 because demo-labeled transaction data [c6], minimal x402 adoption [c12], and no payment or funding evidence [c13] outweigh the developer interest [c5]. Execution stays at 3 given the single-committer concentration [c1] and deprecations [c9]. The total is below 11 and PMF is below 3, so the advance rule is not met; watch is kept, with a re-check once there is evidence of real paying usage or named co-founders.

## Risks

- No proof of real payments or customers: all product figures are sandbox demos, so demand for governed agent spend in LATAM is unvalidated.
- Single-maintainer concentration (244 of roughly 260 commits in the main repo) and sprawling scope (dozens of provider servers) risk quality decay, as the deprecated servers already show.
- x402 and USDC are a minor part of the offering, and the thin x402 repo adoption means limited exposure to the on-chain agent payments thesis.
- Dependence on third-party rails and providers (e.g. Celcoin) and on LATAM regulatory and licensing requirements for holding or moving funds is not addressed in the sources.

## Questions for the founder call

- Are there any live production customers or real settled volume on the platform, and what share is Pix/boleto versus USDC/x402?
- Who are the founders and the full team beyond the top committer, and what is the Zoop connection?
- Who holds the regulatory licenses for the wallet and payment flows in Brazil, and is a partner bank or Celcoin the licensed party?
- What drove deprecating twelve servers, and how will you decide which integrations to maintain?
- Is the company funded, and what is the planned raise and use of funds?
- What is the pricing model, and what is the wedge: open-source MCP servers, hosted MCP, or the governed wallet?

## Receipts

[^c1]: "fabianocruz (User): 244 commits" (github_contributors, https://github.com/codespar/mcp-dev-latam/graphs/contributors, snapshot `d_08316a3bcaac9992`, fetched 2026-11-02)
[^c2]: "Built in New York and Rio de Janeiro by the team behind Zoop" (website_about, https://codespar.dev/about, snapshot `d_d9bf981ecb401c3d`, fetched 2026-11-02)
[^c3]: "none of them compose cleanly** with each other or with the regional rails businesses actually run on." (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c4]: "coinbase: 2,610,865 payments (69.7% of payments), 534,034 USD (35.4% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c5]: "Stars: 277. Forks: 52. Language: TypeScript." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c6]: "Sandbox run · demo data" (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.commits_90d` = 380.0 (as of 2026-11-01)
[^c8]: warehouse metric `gh.commits_total` = 1096.0 (as of 2026-11-01)
[^c9]: "UCP, AP2 and x402 are deprecated: no live endpoint.** Measured on 2026-09-27:" (github_readme, https://github.com/codespar/mcp-dev-latam, snapshot `d_67cfafef4570ce46`, fetched 2026-11-02)
[^c10]: "Moving money is solved. Deciding whether an agent may move it, and proving what happened, is the work." (website_about, https://codespar.dev/about, snapshot `d_d9bf981ecb401c3d`, fetched 2026-11-02)
[^c11]: "Audit trail export
CSV export
rolling out
Reconciliation
rolling out" (website, https://codespar.dev, snapshot `d_14a53ac7a2c7cac2`, fetched 2026-11-02)
[^c12]: "Stars: 3. Forks: 1. Language: JavaScript." (github_profile, https://github.com/codespar, snapshot `d_0d1fe91274ca5559`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
