-- Outcome labels: did the protocol announce a raise in [t0, t0 + window)?
-- A revealed investor decision (DefiLlama raises: date, round, lead investors). Kept apart from features.
CREATE OR REPLACE TABLE labels_pit AS
SELECT f.t0, f.slug,
       COUNT(r.slug) > 0 AS raised,
       COUNT(r.slug) AS n_raises,
       COALESCE(SUM(r.amount_musd), 0) AS amount_musd,
       MIN(r.raise_date) AS first_raise_at,
       string_agg(DISTINCT r.lead_investors, '; ') FILTER (WHERE r.lead_investors <> '') AS leads
FROM features_pit f
JOIN asof_dates a ON a.t0 = f.t0
LEFT JOIN raises r ON r.slug = f.slug AND r.raise_date >= f.t0 AND r.raise_date < a.outcome_end
GROUP BY 1, 2;
