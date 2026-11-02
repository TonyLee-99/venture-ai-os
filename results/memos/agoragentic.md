# agoragentic: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 16 (triage only, not evidence) |

**Agoragentic sells Triptych OS (Agent OS), a governed runtime with mandates, wallet budgets, approvals and receipts for deployed autonomous agents, plus a Router/Marketplace for agents to buy and sell work (optionally via x402), to developers and platform teams with existing agents.**

Thesis fit: Adjacent fit: the agent commerce marketplace with x402 and USDC on Base is on-thesis, but the current pitch leads with governance and control, and paid purchasing is currently frozen, so there is no evidence of agents paying for services yet.

Recommendation after critique and committee: **watch** (first draft: watch; critic: pass)  
Receipts: 13 claims drafted, 62% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 4 as entailed, 9 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 3 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 3 | 4 | 4 |

## Team
- The founder is Jeremy Borden, and the about page names no other team members. [^c1] _(partial support: The quote names Jeremy Borden but establishes neither his founder role nor the absence of other team members.)_
- In the main integrations repo, the account rhein1 has 967 commits, the largest share of contributions. [^c2] _(partial support: The quote supports rhein1's commit count but does not establish its rank relative to other contributors.)_

## Why Now
- The product supports MCP, A2A, x402 and REST, positioned for agents that transact autonomously. [^c11] _(partial support: The quote supports the listed connection protocols but does not establish the autonomous-transaction positioning.)_

## Competition
- The x402 facilitator market is concentrated: Coinbase holds 69.7% of payments, and Agoragentic does not appear among the listed facilitators. [^c10] _(partial support: The quote supports Coinbase's payment share but cannot establish Agoragentic's absence from the facilitator list.)_

## PMF
- Developer adoption is modest: 41 stars and 10 forks on the integrations repo. [^c6]
- The site reports 1,463 successful public listing calls across browse-visible listings. [^c7] _(partial support: The quoted numeral matches the claimed count but is below the minimum quote length and does not identify what was counted.)_
- Paid purchasing is currently unavailable on the platform because the custody policy is frozen. [^c8]
- The marketplace catalog is small: 79 public live services are browse-visible. [^c9] _(partial support: The quoted numeral matches the claimed count but is below the minimum quote length and does not establish that it measures browse-visible services.)_

## Execution
- The owner's top repos had 766 commits on default branches in the 90 days before 2026-11-01. [^c3]
- The GitHub organization was created on 2026-10-23 and has 2 public non-fork repos. [^c4]
- The integrations manifest lists 112 surfaces, and the README states that a catalog entry does not imply live enforcement or payment readiness. [^c5] _(partial support: The quote supports the manifest's surface count but contains no qualification concerning live enforcement or payment readiness.)_

## Risk
- Positioning is broad and shifting across several layers: a governance harness, Agent OS runtime, Router/Marketplace and Interchange. The README says live enforcement is available only for hosts like Claude Code, with others at mapping-example level. [^c12] _(partial support: The receipt supports the distinction between example support and in-path enforcement but establishes neither positioning changes nor host-specific enforcement availability.)_
- There is no external validation on Hacker News: 0 stories carry the company name in the title. [^c13] _(partial support: The metric establishes the absence of company-name title matches, not the absence of all external validation on Hacker News.)_

## Scores (final, after the support review)

- **PMF 2/5**: Developer interest is modest (41 stars, 10 forks [c6]). The 1,463 public listing calls are partial evidence and are mostly free browse-visible usage [c7], with only 79 live services [c9]. Paid purchasing is frozen [c8], so there is no evidence of payments or outside paying customers. Hacker News shows no external validation [c13].
- **NARRATIVE 3/5**: Governance, receipts and budgets for agents handling money is timely, and the product spans MCP, A2A, x402 and REST [c11]. But positioning is spread across several layers (harness, Agent OS, Router/Marketplace, Interchange), and live enforcement exists only for hosts like Claude Code [c12]. The x402 market is concentrated and Agoragentic is not a listed facilitator [c10]. There is no crisp wedge.
- **EXECUTION 3/5**: Commit volume is high (766 in 90 days [c3]) and the integration surface is broad (112 manifest entries [c5]). However, this is a one-primary-committer project (967 commits from rhein1 [c2]) with a single named founder [c1]. The org was created only on 2026-10-23 [c4], so the 90-day commit figure likely includes work from before the org existed or from personal repos. The README states a catalog entry does not imply live enforcement or payment readiness [c5], so breadth overstates shipped capability. With partial support on several of these claims, I lower execution from 4 to 3.

Re-score note: Execution lowered from 4 to 3: the velocity evidence is strong on volume [c3], but the team claims are only partial [c1, c2], it rests on a single maintainer, the org is very new [c4], and the README caveats that catalog breadth does not imply live capability [c5]. PMF stays at 2 and Narrative at 3. Total is 8, below the 11 threshold, and PMF is below 3, so advance is not allowed. Watch remains right rather than pass because there is real shipping activity and a timely governance theme. Re-check once paid purchasing is unfrozen and outside payment evidence exists.

## Risks

- Traffic is likely inorganic or self-generated: top listings are free, and there is no paid transaction evidence while paid purchasing is frozen.
- Key-person dependency: one account made nearly all commits and one named founder, with no visible team.
- Scope sprawl across governance harness, runtime, marketplace and interchange, with enforcement limited to a few hosts, may dilute focus and delay a clear wedge.
- Weak position in x402 flows: Agoragentic is absent from the facilitator market-share data, and Coinbase dominates payment volume.

## Questions for the founder call

- Why is paid purchasing frozen under the custody policy, what is the timeline to unfreeze, and what changes?
- Who are the real users of the marketplace and Agent OS outside the team, and how much of the 1,463 calls came from non-team accounts?
- What is the relationship between rhein1 and Jeremy Borden, and who else works on the company full time?
- Which single wedge do you lead with: governance for existing agents, or the agent commerce marketplace, and how do you monetize it (the 97% seller share)?
- What is the actual paid volume in USDC or x402 to date, and is it routed through any facilitator?
- What is the funding history and runway, given no round has been found?

## Receipts

[^c1]: "Jeremy Borden" (website_about, https://agoragentic.com/about, snapshot `d_25ae1a0ad41ac6ad`, fetched 2026-11-02)
[^c2]: "rhein1 (User): 967 commits" (github_contributors, https://github.com/Agoragentic/agoragentic-integrations/graphs/contributors, snapshot `d_b7d34711deeb9013`, fetched 2026-11-02)
[^c3]: warehouse metric `gh.commits_90d` = 766.0 (as of 2026-11-01)
[^c4]: "Account created: 2026-10-23. Public non-fork repositories: 2.0." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c5]: "the canonical `integrations.json` manifest contains **112** surfaces" (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c6]: "Stars: 41. Forks: 10." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c7]: "1,463" (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c8]: "Purchasing is currently unavailable while the platform custody policy is frozen." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c9]: "79" (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c10]: "coinbase: 2,610,865 payments (69.7% of payments)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c11]: "Connect via MCP, A2A, x402, or direct REST API." (website_about, https://agoragentic.com/about, snapshot `d_25ae1a0ad41ac6ad`, fetched 2026-11-02)
[^c12]: "Mapping or example support is not the same as in-path enforcement." (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
