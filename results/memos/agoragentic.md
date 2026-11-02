# agoragentic: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 7 (triage only, not evidence) |

**Agoragentic sells Triptych OS (Agent OS), a governed runtime giving autonomous agents mandates, wallet budgets, approvals and receipts, plus an open-source integration/governance layer and a Router/Marketplace for agent-to-agent purchases, aimed at developers and platform teams that already run AI agents.**

Thesis fit: Adjacent to the agents x payments thesis: the pitch is governance, evidence and receipts for agents, with x402 monetization and a marketplace as optional layers. However paid purchasing is currently frozen and no real transaction volume is shown, so the commerce side is unproven.

Recommendation (score policy + committee): **watch**; evidence status: **sufficient** (first draft: pass; critic by policy: watch, critic stated: pass)  
Receipts: 13 claims drafted, 54% passed the verifier on the first pass, 13 verified after one repair; the critic labelled 4 as entailed, 9 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 2 | 2 | 2 |
| NARRATIVE | 3 | 3 | 3 |
| EXECUTION | 4 | 4 | 3 |

## Team
- The company names a single founder, Jeremy Borden. [^c1] _(partial support: The quote establishes Jeremy Borden's name but neither his founder role nor that he is the sole named founder.)_
- A second human contributor, jmborden1112-beep, has 34 commits in the main integrations repo. [^c2] _(partial support: The receipt supports the account's commit count, but a GitHub User account does not establish a distinct second human.)_

## Why Now
- The product is built on agent protocols now emerging: it connects via MCP, A2A, x402 or direct REST. [^c10] _(partial support: The quote supports the listed connection options but does not establish that these protocols are now emerging.)_

## Competition
- In the x402scan facilitator data, Coinbase handles 68.2% of payments; Agoragentic is not among the listed facilitators, so it has no visible share of x402 settlement. [^c11] _(partial support: The quote supports Coinbase's payment share but cannot establish Agoragentic's absence or its settlement share.)_

## PMF
- Outside developer interest is modest: 41 stars and 10 forks on the integrations repo. [^c6] _(partial support: The quote supports the star and fork counts but does not establish that they represent outside developers.)_
- The site reports 1,463 successful public listing calls across browse-visible listings. [^c7]
- Hacker News shows 0 stories with the company name in the title. [^c13]

## Narrative
- The story has broadened to many surfaces: the repo catalog lists 112 integration surfaces and many product layers (Agent OS, Router/Marketplace, Interchange, Harness Core, ECF, Risk Fork), which dilutes the wedge. [^c9] _(partial support: The quote supports the surface count but neither the named product layers nor historical broadening or wedge dilution.)_

## Execution
- The owner's top repos show 766 commits in the latest 90-day window. [^c3]
- The prior-90-day commit count was 279, showing the acceleration is from a lower base. [^c4] _(partial support: The metric establishes the prior period's count, but acceleration requires comparison with another receipt.)_
- The integrations repo was last pushed on 2026-10-28, days before the snapshot, and the org has 2 public non-fork repos. [^c5] _(partial support: The quote supports the last-push date but contains neither the snapshot date nor the organization's repository count.)_

## Risk
- Paid purchasing on the marketplace is currently unavailable because platform custody policy is frozen. [^c8]
- The GitHub organization account was created 2026-10-23, so its public track record is very short. [^c12] _(partial support: The quote establishes the organization account's creation date but does not establish the age of the company's public work.)_

## Scores (final, after the support review)

- **PMF 2/5**: Evidence of real usage is thin. The 1,463 successful public listing calls [c7] are free or browse-level calls, not paid volume, and paid purchasing is currently unavailable because custody policy is frozen [c8]. Outside developer interest is modest at 41 stars and 10 forks [c6], and there is no Hacker News traction [c13].
- **NARRATIVE 3/5**: The space is timely: the product connects via MCP, A2A, x402 or REST [c10]. But the story has spread across many product layers and 112 integration surfaces [c9], which dilutes the wedge. There is no visible x402 settlement share against Coinbase's 68.2% [c11]. The GitHub org is also very new [c12].
- **EXECUTION 4/5**: Commit volume was 766 in the latest 90 days versus 279 in the prior 90 [c3][c4], and the integrations repo was pushed days before the snapshot [c5]. Against that, the work looks concentrated in a single named founder [c1] with one other visible contributor at 34 commits [c2], and the org is new [c12].

Re-score note: Dropping the withheld claims changed nothing because none were withheld, and the partial claims were treated as weak evidence. I added [c12] and [c13] to the rationales as further caution on track record and outside traction. Recommendation stays pass; shipping velocity is strong, so re-checking if paid purchasing reopens and non-team paid usage appears would be reasonable.

## Risks

- Marketplace commerce is the thesis-relevant part, yet paid purchasing is frozen and priced usage is tiny, so the agent-payments wedge is unproven.
- Scope sprawl across Agent OS, Marketplace, Interchange, Harness, ECF and Risk Fork may mean no product reaches depth; high commit counts may reflect generated or churned code.
- Call counts on listings may be team-seeded (free echo/demo tools), so they may not indicate organic demand.

## Questions for the founder call

- Why is paid purchasing frozen, what is the platform custody issue, and when does it reopen?
- Who are the paying or transacting users outside the team, and what is real USDC settlement volume to date?
- Which single product (Agent OS, Harness Core, or Marketplace) is the wedge, and how do you monetize it?
- How are rhein1 and jmborden1112-beep related to the founder, and who else is on the team?
- What share of the 1,463 listing calls came from the team or its own agents?
- How do you differentiate from existing x402 facilitators and agent governance tooling?

_7 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: "Jeremy Borden" (website_about, https://agoragentic.com/about, snapshot `d_25ae1a0ad41ac6ad`, fetched 2026-11-02)
[^c2]: "jmborden1112-beep (User): 34 commits" (github_contributors, https://github.com/Agoragentic/agoragentic-integrations/graphs/contributors, snapshot `d_b7d34711deeb9013`, fetched 2026-11-02)
[^c3]: warehouse metric `gh.commits_90d` = 766.0 (as of 2026-11-01)
[^c4]: warehouse metric `gh.commits_prev_90d` = 279.0 (as of 2026-11-01)
[^c5]: "Created: 2026-02-27. Last push: 2026-10-28." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c6]: "Stars: 41. Forks: 10." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c7]: "1,463
successful public listing calls are counted from browse-visible listings." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c8]: "Purchasing is currently unavailable while the platform custody policy is frozen." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c9]: "contains **112** surfaces" (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c10]: "Connect via MCP, A2A, x402, or direct REST API." (website_about, https://agoragentic.com/about, snapshot `d_25ae1a0ad41ac6ad`, fetched 2026-11-02)
[^c11]: "coinbase: 2,342,973 payments (68.2% of payments)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c12]: "Account created: 2026-10-23." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c13]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
