# Decision card: aibtcdev

The two agents disagree. A human decides; log the decision in `ledger/human_feedback.jsonl` (schema: `vaios.agents.schemas.HumanDecision`).

## Where they disagree

- recommendation: drafter 'advance' vs critic 'watch'
- critic flags 3 claim(s) as unsupported by their quote

| | Drafter | Critic |
|---|---|---|
| Model | claude_cli:claude-sonnet-5-5 | codex_cli:gpt-6.1-sol |
| Recommendation | advance | watch |
| PMF | 3 | 2 |
| NARRATIVE | 4 | 3 |
| EXECUTION | 4 | 3 |

## Critic's strongest counterargument

Against advancing, the memo treats unvalidated forks and aggregate commit activity as stronger evidence of adoption and shipping quality than the supplied sources establish [c3-c6]. I recommend watch until independent integrations, meaningful releases, and safe transaction execution can be verified.

## Claims the critic says the quote does not support

- `c6`: The quote supports the fork and star counts, but not the inference that independent developers are building on the software. Fork ownership, activity, and integration evidence are unknown.
- `c8`: The quoted span establishes deprecation only; it does not identify the replacement architectures. The surrounding source supplies those architectures, but replacing a repository with separate frontend and backend repositories does not establish a change in product direction.
- `c10`: The metric establishes the number of public non-fork repositories, not that they are actively maintained. The characterization as a pre-seed team is also unverified.

## Risks the critic says are missing

- Custody and transaction-authorization risk: require evidence of key isolation, spending limits, approval controls, and recovery procedures before treating agent wallet capabilities as production-ready.
- Security assurance is unknown: request audits, transaction-failure handling, and defenses against prompt injection or malicious tool instructions.
- Evidence continuity risk: the detailed README concerns a deprecated repository, while the MCP server is represented only by profile metadata; current functionality and operational maturity remain unverified.
- Maintainer concentration and project ownership are unknown; establish contributor independence, succession coverage, and which legal entity controls the code and any commercial offering.
- Screening-selection risk: a GitHub-only rank should not substitute for independent evidence of customer demand or investment quality [c12].

## Decision

- [ ] advance  - [ ] watch  - [ ] pass   reviewer: ____   reason: ____
