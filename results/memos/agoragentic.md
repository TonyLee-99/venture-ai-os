# agoragentic: baseline diligence memo (AI first pass, not a decision)

**Agoragentic sells Triptych OS (Agent OS), a governance and evidence layer for deployed AI agents (policy, approvals, budgets, receipts), with open-source local controls for existing frameworks plus an optional hosted Router/Marketplace and Interchange for agent commerce.**

Thesis fit: Adjacent to AI agents x payments: the receipts, mandates and budgets layer is relevant to agent commerce, and the repo is tagged x402/USDC. But the stated core is governance, and paid purchasing is currently frozen, so the payments wedge is not live.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **watch**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 14 claims shipped, 0 withheld by the verifier (raw citation precision 0.86, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 2 | 2 |
| NARRATIVE | 3 | 3 |
| EXECUTION | 4 | 3 |

## Market
- The product is positioned as a control-and-proof layer for autonomous agents, not an orchestration framework requiring a rewrite. [^c1]
- The marketplace has 79 public live services browse-visible in the curated catalog. [^c6]

## PMF
- The largest featured listing, Agent Echo, is priced free per call and has 1,094 successful calls. [^c3]
- Only one featured listing shows a non-zero price (Text Summarizer, 0.01 USDC per call, 55 successful calls), so paid usage evidence is thin. [^c4]

## Narrative
- The company describes Agent OS as a runtime with mandates, budgets, approvals and stop controls, which ties to agent spending authority. [^c2]
- The company separates the hosted Router/Marketplace and Interchange from the governed runtime, giving a stated path from local governance to commerce. [^c13]

## Execution
- Commits on the owner's top repos totaled 766 in the last 90 days before 2026-11-01. [^c7]
- The prior-90-day commit count was 279, so recent activity is roughly 2.7x higher. [^c8]
- The integrations repo has 41 stars and 10 forks, which is modest outside interest. [^c9]
- Live in-path enforcement exists only for Claude Code (a PreToolUse hook); OpenCode is experimental and other frameworks are mapping examples only. [^c10]
- The integration catalog lists 112 surfaces, but the README warns a catalog entry does not imply live enforcement or payment readiness. [^c11]

## Risk
- Paid purchasing is currently unavailable because the platform custody policy is frozen. [^c5]
- The GitHub organization was created on 2026-10-23, with only 2 public non-fork repositories. [^c12]
- The company has no Hacker News presence (0 stories), so there is no external community validation from that channel. [^c14]

## Scores

- **PMF 2/5**: There is some outside developer interest (41 stars, 10 forks [c9]) and 1,463 marketplace calls [c3], but most of the volume is a free listing, paid evidence is thin [c4], and paid purchasing is frozen [c5]. No customer or revenue proof.
- **NARRATIVE 3/5**: The governance, receipts and mandates framing is timely for agent spending [c2] and has a stated path to commerce [c13]. But the story is broad: many product layers, a 112-surface catalog [c11], and a frozen payments leg [c5] dilute the wedge.
- **EXECUTION 4/5**: Commit velocity is strong and accelerating [c7][c8], with SDKs, a hook for Claude Code and a large catalog. Held back by enforcement being real for only one host [c10], an unclear team size, and commit counts that may include automated or generated work.

## Risks

- Payments leg is frozen: paid purchasing is unavailable under a platform custody freeze, so the agent-commerce thesis is unproven in production [c5].
- Marketplace traffic is dominated by a free listing (Agent Echo), so the usage numbers may reflect self-generated or test traffic rather than real buyers [c3][c4].
- Scope sprawl: Agent OS, Router, Interchange, Harness, ECF, Risk Fork and 112 catalog surfaces for what looks like a small team; the README itself repeatedly disclaims enforcement and readiness [c10][c11].
- Governance layers are likely to be absorbed by agent framework vendors and platform hosts, and real enforcement exists for only one host today [c10].
- Very young public footprint (org created 2026-10-23) and no external press or community signals [c12][c14]; the high commit count may include bulk or generated commits.

## Questions for the founder call

- Who is on the team, and who authors the commits? How much of the 766 recent commits is human versus agent-generated?
- Why is the custody policy frozen, what is the timeline to unfreeze paid purchasing, and is the custody model non-custodial in the future?
- How much of the 1,463 marketplace calls come from outside buyers versus the team's own tests? Is there any revenue or paying customer today?
- Which design partners or teams run Harness Core or Agent OS in production, and which host integrations do they use?
- Is the wedge governance for coding agents, or agent commerce via x402/USDC? Which one is the first product to focus on?
- What is the funding history, and what does the org created in 2026-10-23 mean for earlier repos or prior entities (the repo itself dates from 2026-02-27)?

## Receipts

[^c1]: "Agoragentic is not another orchestration framework that requires a rewrite." (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c2]: "Mandates, budgets, approvals, stop controls, runtime state, receipts, and reconciliation" (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c3]: "Configured price: free (per call), verified, 1,094 successful calls." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c4]: "Text Summarizer
- devtools. Configured price: 0.01 USDC (per call), verified, 55 successful calls." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c5]: "Purchasing is currently unavailable while the platform custody policy is frozen." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c6]: "79
public live services are browse-visible in the curated catalog." (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c7]: warehouse metric `gh.commits_90d` = 766.0 (as of 2026-11-01)
[^c8]: warehouse metric `gh.commits_prev_90d` = 279.0 (as of 2026-11-01)
[^c9]: "Stars: 41. Forks: 10." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c10]: "Mapping or example support is not the same as in-path enforcement." (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c11]: "contains **112** surfaces." (github_readme, https://github.com/Agoragentic/agoragentic-integrations, snapshot `d_56dbcafcb8f38ffa`, fetched 2026-11-02)
[^c12]: "Account created: 2026-10-23. Public non-fork repositories: 2.0." (github_profile, https://github.com/agoragentic, snapshot `d_5a4cd6a19a1a9d5f`, fetched 2026-11-02)
[^c13]: "Router / Marketplace and Agoragentic Interchange are transaction and discovery" (website, https://agoragentic.com, snapshot `d_58548c9e5cdbdfd3`, fetched 2026-11-02)
[^c14]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
