# merit-systems: baseline diligence memo (AI first pass, not a decision)

**Merit Systems builds open-source infrastructure for agentic commerce on x402: x402scan, an ecosystem explorer for x402 servers, transaction volumes and resources, plus AgentCash tooling (a server framework for x402/MPP-compatible APIs and a pay-per-call GTM agent template) aimed at developers building and consuming paid APIs for agents.**

Thesis fit: Direct fit: the company sits in the x402 / agent-commerce layer, with an explorer that indexes the ecosystem and tooling for pay-per-call APIs. Whether it captures value beyond a public-good explorer is unproven from the sources.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 14 claims shipped, 0 withheld by the verifier (raw citation precision 0.86, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 3 |
| NARRATIVE | 4 | 3 |
| EXECUTION | 4 | 4 |

## Market
- x402scan is an ecosystem explorer for x402, which it describes as a new standard for digital payments. [^c1]
- The GitHub-only screening model ranks merit-systems 7th among all sourced candidates. [^c14]

## PMF
- x402scan lets users explore x402 servers, see their transaction volumes and access their resources through an embedded wallet. [^c2]
- The x402scan repo has 299 forks, a sign of developer interest (stars are 402). [^c3]
- Across the owner's repos there are 1716 stars in total (current snapshot). [^c4]

## Narrative
- The README describes the x402 vision as an internet without ads or centralized intermediaries, with API resources purchasable just-in-time using stablecoins. [^c5]
- The agentcash-router repo is an opinionated server framework for building x402/MPP-compatible APIs. [^c6]
- The company published an AgentCash GTM agent template for sales prospecting, lead enrichment and outreach using pay-per-call APIs. [^c7]

## Execution
- There were 556 commits on default branches of the top 5 repos in the 90 days before 2026-11-01. [^c8]
- The 90 days before the most recent 90-day window saw 790 commits on the default branches of the owner's top repos. [^c9]
- The x402scan repo was last pushed on 2026-10-27, within a week of the fetch date. [^c10]
- The README lists a monorepo with a Next.js web app, a Trigger.dev sync service and shared facilitator configuration, and invites outside contributors to add resources and facilitators. [^c11]

## Risk
- The README notes that local setup is not yet easy. [^c12]
- Hacker News shows no stories with the company name in the title (0 stories). [^c13]

## Scores

- **PMF 3/5**: Real developer adoption signals: 299 forks on x402scan [c3] and 1716 total stars [c4], and the product shows x402 transaction volumes [c2]. But there is no evidence of paying customers or revenue to Merit itself, and the traffic and usage of x402scan.com is not in the sources. Capped at 3.
- **NARRATIVE 4/5**: Clear wedge tied to a live shift: an explorer/index for x402 [c1][c2], extending into server tooling [c6] and agent templates using pay-per-call APIs [c7]. The path from free explorer to a monetizable platform is not stated in the sources, so not 5.
- **EXECUTION 4/5**: High commit volume of 556 in 90 days [c8], though down from 790 in the prior window [c9]; recent push [c10]; contributor-oriented structure [c11]. Contributor count and release cadence are not in the sources, and some repos (GTM template) look one-off.

## Risks

- Monetization is unclear: an open-source Apache-licensed explorer and framework may be a public good without a revenue model.
- Dependence on x402 (and MPP) standards adoption; a larger player or the standards body or facilitators could ship competing explorers or tooling.
- Commit velocity fell about 30% quarter over quarter (556 vs 790), and some repos show little activity (the GTM template had a single push), which may indicate focus shifts.
- Fork counts may overstate real usage: awesome-agentic-commerce has 673 forks against 151 stars, suggesting forks may be inflated by non-organic or incentive-driven behavior.

## Questions for the founder call

- What is the business model: how does Merit make money from x402scan, AgentCash and the router (fees, hosted service, facilitator, data)?
- What are real usage numbers for x402scan.com and AgentCash (MAU, transacting agents, volume routed, paying customers)?
- Why did commits decline from 790 to 556, and how many full-time engineers are on the team? Who are the founders and their backgrounds?
- How is the high fork count on x402scan and awesome-agentic-commerce explained? Are forks tied to contributors, hackathons or incentives?
- What is the relationship with the x402 standard maintainers and facilitators, and how defensible is the position if they build their own explorer?
- What funding has been raised so far and what is the planned use of a new round?

## Receipts

[^c1]: "is an ecosystem explorer for [x402](https://www.x402.org/), a new standard for digital payments." (github_readme, https://github.com/Merit-Systems/x402scan, snapshot `d_dcd4dbd8e9e6ee95`, fetched 2026-11-02)
[^c2]: "lets you explore the ecosystem of x402 servers, see their transaction volumes and directly access their resources through an embedded wallet." (github_readme, https://github.com/Merit-Systems/x402scan, snapshot `d_dcd4dbd8e9e6ee95`, fetched 2026-11-02)
[^c3]: "Stars: 402. Forks: 299. Language: TypeScript." (github_profile, https://github.com/merit-systems, snapshot `d_6fb31a9056596c9d`, fetched 2026-11-02)
[^c4]: warehouse metric `gh.stars_total_now` = 1716.0 (as of 2026-11-01)
[^c5]: "x402 is vision for an internet without ads or centralized intermediaries." (github_readme, https://github.com/Merit-Systems/x402scan, snapshot `d_dcd4dbd8e9e6ee95`, fetched 2026-11-02)
[^c6]: "Opinionated server framework for building x402/MPP-compatible APIs" (github_profile, https://github.com/merit-systems, snapshot `d_6fb31a9056596c9d`, fetched 2026-11-02)
[^c7]: "AgentCash GTM agent template — sales prospecting, lead enrichment, and outreach powered by pay-per-call APIs" (github_profile, https://github.com/merit-systems, snapshot `d_6fb31a9056596c9d`, fetched 2026-11-02)
[^c8]: warehouse metric `gh.commits_90d` = 556.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_prev_90d` = 790.0 (as of 2026-11-01)
[^c10]: "Created: 2025-09-23. Last push: 2026-10-27." (github_profile, https://github.com/merit-systems, snapshot `d_6fb31a9056596c9d`, fetched 2026-11-02)
[^c11]: "We're actively seeking contributors to help build x402scan." (github_readme, https://github.com/Merit-Systems/x402scan, snapshot `d_dcd4dbd8e9e6ee95`, fetched 2026-11-02)
[^c12]: "We're working on making this easier to spin-up." (github_readme, https://github.com/Merit-Systems/x402scan, snapshot `d_dcd4dbd8e9e6ee95`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
[^c14]: warehouse metric `screen.rank` = 7.0 (as of 2026-11-01)
