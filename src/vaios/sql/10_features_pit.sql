-- Point-in-time screening features. For every as-of date t0 in `asof_dates`, every feature reads only rows
-- timestamped strictly before t0. Labels live in a separate table (20_labels.sql) so no feature query can
-- touch the outcome window. tests/test_point_in_time.py injects rows dated >= t0 and asserts nothing changes.

CREATE OR REPLACE TABLE features_pit AS
WITH universe AS (            -- protocols visible on DefiLlama before t0 that have a GitHub owner
    SELECT a.t0, p.slug, p.name, p.category, p.github_owner, p.listed_at_eff
    FROM asof_dates a
    JOIN protocols p ON p.listed_at_eff < a.t0 AND p.github_owner IS NOT NULL
),
gh AS (                        -- commit windows computed by GitHub for exactly this as-of date
    SELECT owner, as_of AS t0,
           SUM(commits_before) AS commits_before,
           SUM(commits_90d) AS commits_90d,
           SUM(commits_prev90d) AS commits_prev90d
    FROM stg_gh_windows
    GROUP BY 1, 2
),
repos AS (
    SELECT u.t0, u.slug, COUNT(r.repo) AS n_repos, MIN(r.repo_created_at) AS first_repo_at
    FROM universe u
    LEFT JOIN stg_gh_repos r ON r.owner = u.github_owner AND r.repo_created_at < u.t0
    GROUP BY 1, 2
),
tvl AS (
    SELECT u.t0, u.slug,
           arg_max(t.tvl_usd, t.day) FILTER (WHERE t.day < u.t0) AS tvl_t0,
           arg_max(t.tvl_usd, t.day) FILTER (WHERE t.day < u.t0 - INTERVAL 90 DAY) AS tvl_t0_90
    FROM universe u
    JOIN stg_tvl_daily t ON t.slug = u.slug AND t.day < u.t0
    GROUP BY 1, 2
),
prior AS (
    SELECT u.t0, u.slug, COUNT(r.slug) AS prior_raises, MAX(r.raise_date) AS last_raise_at
    FROM universe u
    LEFT JOIN raises r ON r.slug = u.slug AND r.raise_date < u.t0
    GROUP BY 1, 2
)
SELECT u.t0, u.slug, u.name, u.category, u.github_owner,
       datediff('day', u.listed_at_eff, u.t0) AS listing_age_days,
       COALESCE(g.commits_before, 0) AS commits_before,
       COALESCE(g.commits_90d, 0) AS commits_90d,
       COALESCE(g.commits_prev90d, 0) AS commits_prev90d,
       ln(1 + COALESCE(g.commits_90d, 0)) - ln(1 + COALESCE(g.commits_prev90d, 0)) AS commit_growth,
       r.n_repos,
       COALESCE(datediff('day', r.first_repo_at, u.t0), 0) AS gh_age_days,
       COALESCE(t.tvl_t0, 0) AS tvl_t0,
       ln(1 + COALESCE(t.tvl_t0, 0)) - ln(1 + COALESCE(t.tvl_t0_90, 0)) AS tvl_growth_90d,
       p.prior_raises,
       CASE WHEN p.last_raise_at IS NULL THEN NULL ELSE datediff('day', p.last_raise_at, u.t0) END
           AS days_since_last_raise,
       g.owner IS NOT NULL AS gh_found
FROM universe u
LEFT JOIN gh g ON g.owner = u.github_owner AND g.t0 = u.t0
LEFT JOIN repos r ON r.t0 = u.t0 AND r.slug = u.slug
LEFT JOIN tvl t ON t.t0 = u.t0 AND t.slug = u.slug
LEFT JOIN prior p ON p.t0 = u.t0 AND p.slug = u.slug;

-- Reference ONLY, never a model input: today's star count is leakage-exposed (GitHub has no star history).
CREATE OR REPLACE TABLE leaky_reference AS
SELECT owner, SUM(stars_now) AS stars_now FROM stg_gh_repos GROUP BY 1;
