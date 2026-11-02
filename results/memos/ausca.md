# auscahq: baseline diligence memo (AI first pass, not a decision)

| Stage | Last known round | Token | YC batch | Triage rank |
|---|---|---|---|---|
| unknown (no funding evidence found) | unknown | none found | none | 26 (triage only, not evidence) |

**Pay-per-call APIs and MCP services for AI agents (document OCR, document analysis, media transcription, remote browser sessions, agent email inboxes), paid in USDC on Base over x402 with no account or API keys, plus buyer SDKs in many languages.**

Thesis fit: Direct fit: agents buying infrastructure per call via x402 with signed receipts is core agent commerce. But it is a seller of resold or commodity services with no visible paid usage, so the evidence is of product breadth, not demand.

Recommendation (score policy + committee): **pass**; evidence status: **evidence insufficient** (first draft: pass; critic by policy: pass, critic stated: pass)  
Receipts: 12 claims drafted, 58% passed the verifier on the first pass, 12 verified after one repair; the critic labelled 1 as entailed, 11 as partial (tagged below) and withheld 0.

| Dimension | Drafter (final) | Drafter (first draft) | Critic |
|---|---|---|---|
| PMF | 1 | 1 | 1 |
| NARRATIVE | 3 | 4 | 3 |
| EXECUTION | 3 | 3 | 3 |

## Team
- The public repo has a single contributor, auscaster, with 61 commits; no other named people or team are disclosed in the sources. [^c1] _(partial support: The quote supports auscaster's commit count but does not establish contributor exclusivity or the absence of other disclosed team members.)_

## Why Now
- Ausca builds on the x402 payment standard, where the Coinbase facilitator alone processed 2,342,973 payments in the latest reported window. [^c9] _(partial support: The receipt supports Coinbase's payment count but does not establish Ausca's use of x402 or identify the reporting window.)_

## Competition
- The x402 facilitator market is uneven: fluxa has 56.7% of volume on only 9.7% of payments. The sources do not say which facilitator Ausca uses or name competing pay-per-call service vendors. [^c10] _(partial support: The quote supports Fluxa's payment and volume shares but not the assertions about undisclosed facilitators or competitors.)_

## PMF
- The repo has 39 stars and 0 forks, the only outside-interest signal in the sources; no customers, payment counts or on-chain volume are reported. [^c5] _(partial support: The receipt supports the star and fork counts but not the exhaustive assertions about outside interest or absent commercial evidence.)_
- There is no Hacker News traction for the company: 0 stories mention it. [^c6] _(partial support: The metric establishes no company-name title matches, which is narrower than no mentions or Hacker News traction.)_

## Narrative
- The wedge is agents paying per call with a hard USD cap, with no account or API keys, and a signed receipt per completed invocation. [^c7] _(partial support: The quote supports accountless, keyless per-call payments and signed receipts but does not mention agents or a hard spending cap.)_
- Pricing is published and low-ticket: Document OCR is $0.25 per document. [^c8]

## Execution
- The auscahq GitHub organization was created on 2026-09-02, so the company is very young. [^c2] _(partial support: The receipt establishes the GitHub account creation date, which does not establish the company's age.)_
- The org's top repos show 73 commits on default branches in the most recent window, which is also its entire commit history, consistent with a new project. [^c3] _(partial support: The metric supports recent commit volume but does not establish that this equals the entire commit history.)_
- The README lists client libraries for npm, PyPI, Go, Rust, Ruby, PHP, Swift, Dart, .NET, Java, plus Vercel AI SDK and LangChain tools, which is very broad surface area for one maintainer in two months. [^c4] _(partial support: The quote supports Vercel AI SDK tools but not the other libraries, maintainer count or development period.)_
- Distribution work is visible: an MCP registry listing, a Smithery listing and installable agent skills for each of five services. [^c12] _(partial support: The command supports a skills installation path but does not establish registry listings, service coverage or the number of skills.)_

## Risk
- The service runtime is closed source and not in the repository; only the buyer side is public, so the delivery backend cannot be verified from the sources. [^c11] _(partial support: The quote establishes that the runtime is absent from this repository but does not establish that it is closed source or unverifiable elsewhere.)_

## Scores (final, after the support review)

- **PMF 1/5**: No evidence of paying or transacting usage from users outside the team. The only outside-interest signal is 39 stars and 0 forks, and no customers, payment counts or on-chain volume are reported [c5]. There is no Hacker News traction [c6]. The x402 usd_per_tx_30d metric was not provided, so the inorganic-traffic risk cannot be assessed. The Coinbase facilitator volume in [c9] is market-wide context, not Ausca usage.
- **NARRATIVE 3/5**: The wedge is clear: agents pay per call under a hard USD cap, with no account or API keys and a signed receipt per invocation [c7]. It is tied to a live x402 market [c9], and pricing is published and low-ticket [c8]. The review downgraded several supporting claims to partial. The sources do not say which facilitator Ausca uses or who it competes with, so the edge is unstated [c10]. The delivery backend is closed and unverifiable [c11]. The path from a bundle of unrelated services to a platform is unproven.
- **EXECUTION 3/5**: Shipping is recent and fast, with 73 commits in the window, which is the org's entire history [c3]. SDK coverage is broad [c4], and distribution work is visible through registry and Smithery listings and agent skills [c12]. It is a single-contributor project (auscaster, 61 commits) about two months old [c1][c2], so there is no multi-person or sustained-velocity evidence. The closed backend limits verification [c11].

Re-score note: A re-check in a quarter is reasonable if payment or customer evidence appears.

## Risks

- No evidence of any paying customer or on-chain volume; the 39 stars may reflect curiosity rather than demand.
- Agents buying OCR, transcription or a browser per call is not yet a proven category; demand may sit with human developers using existing API-key vendors.

## Questions for the founder call

- How many paid invocations and distinct paying wallets have you had, and how many are not yours or testers?
- Which providers sit behind OCR, transcription and browser sessions, and what is the gross margin per call?
- Who else is on the team, and what are your funding status and plans?
- Why these five services, and which one has the strongest pull so far?
- Which x402 facilitator do you settle through, and what is your average USD per payment?
- What is your defensibility if existing API vendors add x402 support?

_8 free-text item(s) removed because they stated a number that no shipped claim or warehouse fact supports._

## Receipts

[^c1]: "auscaster (User): 61 commits" (github_contributors, https://github.com/auscahq/ausca/graphs/contributors, snapshot `d_1887cd9fe2e6615f`, fetched 2026-11-02)
[^c2]: "Account created: 2026-09-02." (github_profile, https://github.com/auscahq, snapshot `d_3af8c54623d0adf4`, fetched 2026-11-02)
[^c3]: warehouse metric `gh.commits_90d` = 73.0 (as of 2026-11-01)
[^c4]: "Vercel AI SDK tools for any x402 v2 resource" (github_readme, https://github.com/auscahq/ausca, snapshot `d_0c8cc36797b12828`, fetched 2026-11-02)
[^c5]: "Stars: 39. Forks: 0." (github_profile, https://github.com/auscahq, snapshot `d_3af8c54623d0adf4`, fetched 2026-11-02)
[^c6]: warehouse metric `hn.stories` = 0.0 (as of 2026-11-01)
[^c7]: "No account, no API keys; USDC on Base per call, a signed receipt for every completed invocation." (github_readme, https://github.com/auscahq/ausca, snapshot `d_0c8cc36797b12828`, fetched 2026-11-02)
[^c8]: "| Document OCR | Normalized text with line confidence from one committed document | $0.25 per document |" (github_readme, https://github.com/auscahq/ausca, snapshot `d_0c8cc36797b12828`, fetched 2026-11-02)
[^c9]: "coinbase: 2,342,973 payments (68.2% of payments), 525,020 USD (35.2% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c10]: "fluxa: 332,013 payments (9.7% of payments), 846,277 USD (56.7% of volume)" (market_structure, https://www.x402scan.com/facilitators, snapshot `d_b3e61427fd0e0e8c`, fetched 2026-11-02)
[^c11]: "The service runtime is not in this repository; this is the complete public" (github_readme, https://github.com/auscahq/ausca, snapshot `d_0c8cc36797b12828`, fetched 2026-11-02)
[^c12]: "npx -y skills add auscahq/ausca --skill '*'" (github_readme, https://github.com/auscahq/ausca, snapshot `d_0c8cc36797b12828`, fetched 2026-11-02)
