# Decision card: merit-systems

The two agents disagree. A human decides; log the decision in `ledger/human_feedback.jsonl` (schema: `vaios.agents.schemas.HumanDecision`).

## Where they disagree

- recommendation: drafter 'advance' vs critic 'watch'
- critic flags 2 claim(s) as unsupported by their quote

| | Drafter | Critic |
|---|---|---|
| Model | claude_cli:claude-sonnet-5-5 | codex_cli:gpt-6.1-sol |
| Recommendation | advance | watch |
| PMF | 3 | 3 |
| NARRATIVE | 4 | 3 |
| EXECUTION | 4 | 4 |

## Critic's strongest counterargument

The strongest argument against advancing is that developer attention and active shipping have not yet established a customer who repeatedly uses or pays for Merit's offering. Advancing now would rely on an unverified conversion from ecosystem visibility into a differentiated, commercially defensible business.

## Claims the critic says the quote does not support

- `c5`: The quoted span supports the stated vision but does not support the additional assertion about purchasing API resources just-in-time using stablecoins. That assertion appears elsewhere in the provided document and needs its own supporting receipt.
- `c11`: The quote establishes only that the project seeks contributors. It does not substantiate the listed monorepo components or the specific resource and facilitator contribution mechanisms, which require separate supporting spans.

## Risks the critic says are missing

- Ecosystem transaction volume could be mistaken for Merit traction; require attributable usage, repeat users and evidence that transactions reflect independent economic demand.
- Explorer completeness and accuracy are unverified: incomplete facilitator coverage or unreliable resource listings could undermine user trust.
- The embedded-wallet and paid-resource workflow warrants diligence on custody, signing permissions, malicious endpoints and responsibility for failed transactions.
- Commit totals do not reveal maintainer concentration, automated activity, code quality or production readiness; team continuity remains an open diligence issue.
- The memo's fork-ratio speculation does not establish manipulation, and a last-push timestamp does not establish that a repository received only a single push. Treat both as questions rather than adverse findings.

## Decision

- [ ] advance  - [ ] watch  - [ ] pass   reviewer: ____   reason: ____
