# faremeter: baseline diligence memo (AI first pass, not a decision)

**Open-source TypeScript framework (client library, middleware, facilitator, gateway, wallet integrations) that lets AI agents and other software make blockchain payments over HTTP 402, supporting x402 and MPP on Solana and EVM, sponsored by ABK Labs.**

Thesis fit: Direct fit: it is infrastructure for agents paying per request over HTTP 402 (x402 v1/v2, MPP), with wallet and chain-agnostic plugins on both Solana and EVM. The sources show developer adoption signals but no evidence of paid or transacting usage.

Recommendation (drafter, claude_cli:claude-sonnet-5-5): **advance**  
Critic (codex_cli:gpt-6.1-sol): **watch**  
Receipts: 12 claims shipped, 0 withheld by the verifier (raw citation precision 0.92, after repair 1.00)

| Dimension | Drafter | Critic |
|---|---|---|
| PMF | 3 | 2 |
| NARRATIVE | 4 | 4 |
| EXECUTION | 4 | 3 |

## Market
- Faremeter describes itself as a framework for agents and other utilities to transparently make machine payments using web infrastructure. [^c1]
- AP2, Cloudflare Pay-Per-Crawl and L402 are tracked for future support but not yet shipped. [^c5]
- Faremeter ranks 4 among all sourced candidates in the GitHub-only screening model. [^c11]

## PMF
- The main repo has 25 forks, a sign of developer interest but not of payment volume. [^c7]

## Narrative
- The approach is built on HTTP 402 Payment Required with a standard-, wallet- and blockchain-agnostic plugin system. [^c2]
- The project is sponsored and built by ABK Labs engineers along with open-source contributors. [^c10]

## Execution
- It supports both v1 and v2 of Coinbase's x402, negotiated automatically. [^c3]
- It ships the MPP charge intent on Solana, while noting the MPP spec is still evolving. [^c4]
- EVM support covers gasless USDC via EIP-3009 on networks including Base, Polygon, Monad and Skale. [^c6]
- Commits across the owner's top 5 repos were 1180 in the last 90 days, versus 1156 in the prior 90 days, so velocity is sustained and flat. [^c8]
- Total commits across those repos stand at 3635 since the org was created in 2025. [^c9]

## Risk
- There is no Hacker News presence: 0 stories with the company name in the title. [^c12]

## Scores

- **PMF 3/5**: Forks and stars [c7] show real developer interest, and the framework covers wallets, chains and standards, but the sources show no customers, transaction volume or pricing evidence. That puts it at the developer-adoption tier, not the paying tier.
- **NARRATIVE 4/5**: The story is a clear wedge on HTTP 402 and x402/MPP [c2][c3][c4], with a path to a platform via the facilitator, gateway and wallet plugins. Standards are still moving [c4][c5], and the sources do not state a commercial model or an edge over Coinbase's own x402 tooling. ABK Labs sponsorship [c10] leaves the company/product relationship unclear.
- **EXECUTION 4/5**: Commit velocity is high and steady [c8][c9], and the team has shipped x402 v2, MPP charge and multiple EVM chains [c3][c4][c6]. The sources do not show contributor counts, so the multi-person claim is unverified, and the commit totals cover the top 5 repos, not only the main framework.

## Risks

- Commercial model unclear: it is an open-source sponsored project of ABK Labs, with no pricing, customers or revenue shown, so a venture-scale business is unproven.
- Standards risk: MPP is still evolving and x402 is controlled by Coinbase, which could absorb or commoditize the facilitator, middleware and client layers.
- No evidence of transacting usage: forks and stars are the only adoption signals, with no volume, customers or production deployments cited.
- Entity and dependency risk: the project is built by ABK Labs engineers, so it is unclear whether Faremeter is a separate fundable entity, who owns the IP, and how much team time is dedicated to it.

## Questions for the founder call

- Is Faremeter a standalone company or an ABK Labs project, and who owns the IP and would take the investment?
- Who is using it in production, and what are the transaction counts or volume through Faremeter facilitators or gateways?
- What is the business model: hosted facilitator fees, managed gateway, enterprise support, or something else?
- How many distinct people commit regularly, and how many are not ABK Labs employees?
- How does Faremeter differentiate from Coinbase's x402 reference SDKs and other facilitators, and what happens if MPP and x402 converge?
- Which of the 1180 recent commits are in the core framework versus the other 15 repos?

## Receipts

[^c1]: "A universal framework designed to allow agents and other utilities to transparently make machine payments using web infrastructure." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
[^c2]: "Using HTTP and the existing `402 Payment Required` concepts." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c3]: "both v1 and v2 of the protocol, negotiated automatically." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c4]: "the spec is still evolving; we currently ship the `charge` intent on Solana." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c5]: "We're tracking these for future support:" (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c6]: "EVM `exact` over EIP-3009 gasless USDC in [@faremeter/payment-evm](./packages/payment-evm), with network coverage including Base, Polygon, Monad, and Skale" (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c7]: "Stars: 70. Forks: 25." (github_profile, https://github.com/faremeter, snapshot `d_748e85e901fac822`, fetched 2026-11-02)
[^c8]: warehouse metric `gh.commits_90d` = 1180.0 (as of 2026-11-01)
[^c9]: warehouse metric `gh.commits_total` = 3635.0 (as of 2026-11-01)
[^c10]: "Faremeter is sponsored and built by the engineers at [ABK Labs](https://abklabs.com) along with other open-source contributors." (github_readme, https://github.com/faremeter/faremeter, snapshot `d_d7f80babf38c9414`, fetched 2026-11-02)
[^c11]: warehouse metric `screen.rank` = 4.0 (as of 2026-11-01)
[^c12]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
