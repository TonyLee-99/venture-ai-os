-- Core tables on top of staging. Pure SQL; staging tables (stg_*) are loaded by dakr/warehouse.py.

-- DefiLlama started recording listedAt on 2021-10-14. A protocol with no listedAt whose TVL history starts
-- before that date was listed before tracking began; we date its listing conservatively at 2021-10-14.
-- A protocol with no listedAt and later TVL has an unknown listing date and is left out of the backtest
-- (DefiLlama backfills TVL history on listing, so first-TVL-day would leak future visibility).
CREATE OR REPLACE TABLE protocols AS
WITH first_tvl AS (
    SELECT slug, MIN(day) AS first_tvl_day FROM stg_tvl_daily WHERE tvl_usd > 0 GROUP BY slug
)
SELECT p.*,
       f.first_tvl_day,
       CASE
           WHEN p.listed_at IS NOT NULL THEN p.listed_at
           WHEN f.first_tvl_day < TIMESTAMP '2021-10-14' THEN TIMESTAMP '2021-10-14'
       END AS listed_at_eff
FROM stg_protocols p
LEFT JOIN first_tvl f USING (slug);

CREATE OR REPLACE TABLE raises AS SELECT * FROM stg_raises;

-- Weekly x402 traction (all chains + per chain), the main inflection series.
CREATE OR REPLACE TABLE x402_weekly AS
SELECT chain, date_trunc('week', day) AS week, SUM(txs) AS txs, SUM(volume_usd) AS volume_usd,
       MAX(buyers) AS peak_daily_buyers, MAX(sellers) AS peak_daily_sellers, COUNT(*) AS days
FROM stg_x402_daily GROUP BY 1, 2;

CREATE OR REPLACE TABLE commits_weekly AS
SELECT repo, date_trunc('week', committed_at) AS week, COUNT(*) AS commits
FROM stg_gh_commits GROUP BY 1, 2;
