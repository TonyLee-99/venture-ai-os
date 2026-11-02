"""A tiny hand-made warehouse for SQL tests: two protocols, one as-of date, known answers."""

import duckdb
import pandas as pd

from vaios.dakr.warehouse import SQL_DIR, run_sql

T0 = pd.Timestamp("2024-01-01")


def staging() -> dict[str, pd.DataFrame]:
    ts = pd.Timestamp
    return {
        "stg_protocols": pd.DataFrame([
            {"slug": "alpha", "name": "Alpha", "category": "Payments", "github_owner": "alpha-org", "github_owners": "alpha-org",
             "listed_at": ts("2023-03-01"), "url": "", "twitter": "", "description": "", "gecko_id": None, "chains": ""},
            {"slug": "beta", "name": "Beta", "category": "AI Agents", "github_owner": "beta-org", "github_owners": "beta-org",
             "listed_at": ts("2023-12-15"), "url": "", "twitter": "", "description": "", "gecko_id": None, "chains": ""},
            {"slug": "late", "name": "Late", "category": "AI Agents", "github_owner": "late-org", "github_owners": "late-org",
             "listed_at": ts("2024-02-01"), "url": "", "twitter": "", "description": "", "gecko_id": None, "chains": ""},
        ]),
        "stg_raises": pd.DataFrame([
            {"slug": "alpha", "raise_date": ts("2023-06-01"), "round": "Seed", "amount_musd": 2.0, "lead_investors": "A",
             "other_investors": "", "source": ""},
            {"slug": "beta", "raise_date": ts("2024-05-01"), "round": "Seed", "amount_musd": 3.0, "lead_investors": "B",
             "other_investors": "", "source": ""},
        ]),
        "stg_tvl_daily": pd.DataFrame([
            ("alpha", ts("2023-09-01"), 100.0), ("alpha", ts("2023-12-31"), 400.0), ("beta", ts("2023-12-20"), 50.0),
        ], columns=["slug", "day", "tvl_usd"]),
        "stg_gh_windows": pd.DataFrame([
            {"owner": "alpha-org", "repo": "a", "as_of": T0, "repo_created_at": ts("2023-01-01"), "stars_now": 10,
             "forks_now": 1, "archived": False, "commits_before": 120, "commits_90d": 30, "commits_prev90d": 10},
            {"owner": "beta-org", "repo": "b", "as_of": T0, "repo_created_at": ts("2023-11-01"), "stars_now": 5,
             "forks_now": 0, "archived": False, "commits_before": 40, "commits_90d": 40, "commits_prev90d": 0},
        ]),
        "stg_gh_repos": pd.DataFrame([
            {"owner": "alpha-org", "repo": "a", "repo_created_at": ts("2023-01-01"), "stars_now": 10},
            {"owner": "beta-org", "repo": "b", "repo_created_at": ts("2023-11-01"), "stars_now": 5},
        ]),
        "stg_x402_daily": pd.DataFrame(columns=["day", "chain", "txs", "volume_usd", "buyers", "sellers"]).astype(
            {"day": "datetime64[ns]", "chain": str, "txs": int, "volume_usd": float, "buyers": int, "sellers": int}),
        "stg_gh_commits": pd.DataFrame({"repo": pd.Series(dtype=str), "committed_at": pd.Series(dtype="datetime64[ns]")}),
        "asof_dates": pd.DataFrame([{"t0": T0, "outcome_end": pd.Timestamp("2025-01-01")}]),
    }


def build(extra: dict[str, pd.DataFrame] | None = None) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    tables = staging()
    for name, df in (extra or {}).items():
        tables[name] = pd.concat([tables[name], df], ignore_index=True)
    for name, df in tables.items():
        con.register("_df", df)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM _df")
        con.unregister("_df")
    run_sql(con, sorted(SQL_DIR.glob("*.sql")))
    return con
