# 0001. Data sources: what actually works keyless today (probed 2026-11-02)

Status: accepted. Probed before designing the pipeline, so the design follows the data, not the reverse.

## Probe results

| Source | Endpoint probed | Result | Used for |
|---|---|---|---|
| GitHub REST (`gh api`) | `search/repositories`, `repos/*`, `commits?until=`, `forks`, `issues` | Works (5,000 req/h) | Sourcing, repo metadata, README snapshots |
| GitHub REST stargazers with `starred_at` | `repos/*/stargazers` + `star+json` | **404 for every repo** (also `cli/cli`) | Not available |
| GitHub GraphQL `stargazers(orderBy: STARRED_AT)` | GraphQL | **Returns an empty list** | Not available |
| GitHub GraphQL commit `history(since, until){totalCount}` | GraphQL | Works, cost 1 point per org query | Point-in-time activity features |
| GitHub `stats/commit_activity` | REST | Returns empty (not computed on demand) | Not used |
| DefiLlama `/protocols`, `/protocol/{slug}`, `/v2/chains`, stablecoins | `api.llama.fi` | Works | Universe, TVL history, **per-protocol `raises`** |
| DefiLlama `/raises` (all raises) | `api.llama.fi/raises` | **HTTP 402, paid plan** | Not used directly |
| DefiLlama raises page | `defillama.com/raises` | 403 to scripts | Not used |
| CoinGecko public | `coins/markets`, `coins/{id}/market_chart?days=365` | Works (365-day cap) | Token price/volume series |
| x402scan public tRPC (Merit Systems, open source) | `public.stats.bucketed`, `public.facilitators.bucketedStatistics` | Works: daily x402 transfers since 2025-05-09, per chain and per facilitator | Agentic-payments traction series |
| HN Algolia | `search_by_date?query=x402` | Works | Narrative signal, dated events |
| arXiv API | `export.arxiv.org/api/query` (https) | Works (http 301 -> https) | Technical-research context only |
| YC company directory (yc-oss mirror) | `yc-oss.github.io/api/companies/all.json` | Works, 6,362 companies with batch dates | Sourcing; YC acceptance = dated investor decision |
| SEC EDGAR full-text search | `efts.sec.gov/LATEST/search-index` | Works (needs User-Agent) | Not used in v1 (name matching to Form D is noisy) |
| LLM backends | `claude -p` (claude-sonnet-5-5), `codex exec -s read-only` (gpt-6.1-sol) | Both work headless | Gateway backends |

## Consequences for the design

1. **No point-in-time star history.** The usual "stars at T0" baseline cannot be built honestly. The backtest uses
   point-in-time signals that do carry timestamps: commit counts in windows before T0 (GraphQL `history`),
   repo creation dates, DefiLlama listing date and TVL history. Current star count is reported only as a
   **leakage-exposed** reference baseline, clearly labelled.
2. **No bulk raises feed.** Funding outcomes come from DefiLlama's per-protocol `raises` field (free, dated,
   with lead investors). That restricts the backtest universe to DefiLlama-listed protocols with a GitHub org
   (about 1,600 of 8,900). See ADR 0003 for why the backtest universe is broader than the agentic-payments niche.
3. **Agentic-payments traction is measurable.** x402scan gives a daily series of x402 transactions, volume,
   buyers and sellers, split by chain and by facilitator. This is the main series for inflection detection.
4. Paid sources (PitchBook, Crunchbase, Messari, Dune, DefiLlama Pro) are not used. `src/vaios/ingest/` has one
   module per source with the same `fetch -> raw file + manifest row` contract, so a paid connector plugs in as
   one more module.
