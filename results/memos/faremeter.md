# faremeter: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 4 (triage only, not evidence) |

**Open-source TypeScript framework (client library, middleware, facilitator, gateway, wallet integrations) that lets agents and existing APIs make and accept HTTP 402 machine payments over x402 and MPP on Solana and EVM chains. Built by ABK Labs.**

Thesis fit: Direct fit: it is infrastructure for agents paying per API call, and it spans both the x402 and MPP standards. It sits at the developer-tooling layer rather than the facilitator layer, so the open question is how it captures value beyond being open-source plumbing.

Recommendation after critique and committee: **watch** (first draft: advance; critic: watch)  
Receipts: 12 claims drafted, 67% passed the verifier on the first pass, 12 verified after one repair; the critic labelled 5 as entailed, 6 as partial (tagged below) and withheld 1.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 3 | 3 |
| NARRATIVE | 3 | 4 | 3 |
| EXECUTION | 3 | 4 | 3 |

## Team
- Development is concentrated in one engineer: alexanderguy has 550 commits, far ahead of the other listed contributors. [^c1] _(partial support: The quote establishes alexanderguy's commit count but contains no other contributors' counts to establish concentration or the comparison.)_
- Faremeter is sponsored and built by the engineers at ABK Labs, plus open-source contributors. The founders are not named in the sources. [^c2] _(partial support: The quote supports ABK Labs sponsorship and engineering participation but does not establish that founders are unnamed throughout the sources.)_

## Why Now
- The README says it supports both v1 and v2 of Coinbase's x402, negotiated automatically, so it has tracked the standard's upgrade. [^c3] _(partial support: The quote supports automatic negotiation between protocol versions but does not itself identify Coinbase's x402 or establish the history of upgrade implementation.)_
- It also ships the `charge` intent of the emerging MPP (Machine Payments Protocol) on Solana, while noting that the spec is still evolving. This hedges across competing agent-payment standards. [^c4] _(partial support: The quote supports shipping the charge intent on Solana under an evolving specification, but neither identifies MPP nor establishes a hedge across competing standards.)_

## Competition
- Fluxa carries 56.2% of x402 dollar volume on only 9.4% of payments, which shows value is concentrated in a few facilitators. [^c6]

## PMF
- The main repo has 70 stars and 25 forks. This is real but modest developer interest, and it is not proof of payments. [^c7]
- There is no Hacker News traction: 0 points across stories with the company name in the title. [^c8] _(partial support: The metric establishes zero points for the specified title-based search, which does not establish an absence of all Hacker News traction.)_

## Execution
- There were 1,180 commits across the owner's top 5 repos in the last 90 days. [^c9]
- The warehouse shows 1156 commits in the earlier of the two most recent 90-day windows. [^c10]
- The README lists broad network coverage for EVM payments, including Base, Polygon, Monad and Skale. [^c11]

## Risk
- The GitHub profile shows the main repo's last push as 2026-07-06, about four months before the fetch date. That sits oddly with the recent commit counts, which may come from other repos or default branches. [^c12] _(partial support: The quote establishes the last-push date but contains neither the fetch date nor recent commit counts needed to support the comparison or proposed explanation.)_

## Scores (final, after the support review)

- **PMF 2/5**: Evidence is limited to modest developer interest: 70 stars and 25 forks [c7]. There is no evidence of payments, customers or on-chain volume attributable to Faremeter, and no Hacker News traction [c8]. The withheld c5 offered nothing on Faremeter's own share, so market-structure context [c6] does not help it. The 25 forks are weak evidence of real adoption, and the earlier claim of outside contributors [c1] is only partial and actually shows concentration in one engineer. This sits between the 1 level (repo with no outside usage evidence) and the 3 level (real developer adoption), so 2.
- **NARRATIVE 3/5**: The wedge, standard-agnostic agent payment middleware supporting x402 v1/v2 and MPP, is timely [c3][c4], and the broad network coverage [c11] suggests a plausible platform path. However, c3 and c4 are only partial support. The market is concentrated in a few facilitators [c6], no founders or monetization edge are named [c2], and no funding or stage evidence exists. This reads as in the right space with a decent but unproven edge, so 3.
- **EXECUTION 3/5**: Commit counts are high: 1,180 commits across the owner's top 5 repos in 90 days [c9], and 1156 in the prior window [c10], which indicates sustained activity. However, development is concentrated in one engineer with 550 commits [c1], the team is not named [c2], and the main repo's last push is dated about four months before the fetch date, which conflicts with the recent commit figures [c12]. The commit counts are across multiple repos, not the main one. Steady but single-maintainer-heavy, so 3.

Re-score note: Lowered PMF from 3 to 2 (only stars/forks; no payment or customer evidence; contributor claim c1 shows concentration, not outside adoption), Narrative from 4 to 3 (c3/c4 only partial, no named founders or monetization edge, crowded market), and Execution from 4 to 3 (single-engineer concentration [c1], multi-repo commit counts, and the unexplained stale push on the main repo [c12]). The total is now 8, below the advance threshold of 11, and PMF is below 3, so the recommendation moves from advance to watch. Re-check in a quarter for payment evidence or named founders.

## Risks

- No evidence of paid usage: Faremeter does not appear among the measured x402 facilitators, and no customer or volume data is provided. The framework could be widely forked without producing revenue.
- Open-source infrastructure with an unclear business model. It is sponsored by ABK Labs, an engineering services shop, and it is unclear whether Faremeter is the company or a side project.
- Key-person concentration: one contributor accounts for about 83% of the roughly 660 commits among the top four contributors.
- x402 volume is concentrated in Coinbase and Fluxa, and standards (x402, MPP, AP2, L402) are still shifting, so a framework layer can be commoditized or bypassed.
- Data inconsistency between the main repo's last push in July 2026 and the 90-day commit activity. The activity may come from other repos, so shipping on the core product is unverified.

## Questions for the founder call

- What is the entity and ownership structure: is Faremeter a standalone company or an ABK Labs project, and who are the founders? Is there any funding?
- What is the monetization plan (hosted facilitator, gateway, enterprise support), and are there paying or pilot customers today?
- How much real x402 or MPP traffic flows through Faremeter-based deployments, and what is the average dollar value per payment (x402 usd_per_tx_30d was not provided)?
- Why does the main repo show a last push of 2026-07-06 while 90-day commits are high? Where is the current work happening?
- How do you plan to stay differentiated if Coinbase's SDKs and facilitators absorb middleware features, and how do you decide between x402 and MPP?
- What is the plan to reduce dependence on one lead engineer?

## Withheld: real quote, but the critic says it does not support the claim

- ~~x402 facilitator volume is dominated by Coinbase, which has 69.7% of payments. Faremeter does not appear by name among the listed facilitators, so its own facilitator share is unknown or negligible.~~ (contradicts: The receipt distinguishes Coinbase's majority payment count from its minority dollar-volume share and provides no evidence about Faremeter's absence or share.)

## Receipts

[^c1]: "alexanderguy (User): 550 commits" (github_contributors, https://github.com/faremeter/faremeter/graphs/contributors, snapshot `d_2bf293576b4555c8`, fetched 2026-11-02)
[^c2]: "Faremeter is sponsored and built by the engineers at [ABK Labs](https://abklabs.com) along with other open-source contributors." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c3]: "both v1 and v2 of the protocol, negotiated automatically." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c4]: "the spec is still evolving; we currently ship the `charge` intent on Solana." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c6]: "fluxa: 353,469 payments (9.4% of payments), 846,830 USD (56.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_d654ae3bd333bd8e`, fetched 2026-11-02)
[^c7]: "Stars: 70. Forks: 25. Language: TypeScript." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
[^c8]: warehouse metric `hn.points_total` = 0.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_90d` = 1180.0 (as of 2026-11-01)
[^c10]: warehouse metric `gh.commits_prev_90d` = 1156.0 (as of 2026-11-01)
[^c11]: "network coverage including Base, Polygon, Monad, and Skale (mainnet and testnets)" (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c12]: "Created: 2025-06-11. Last push: 2026-07-06." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
