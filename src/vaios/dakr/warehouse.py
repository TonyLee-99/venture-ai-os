"""`make warehouse`: load staging tables, then run the SQL models in src/vaios/sql/ in file order."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from vaios.config import ALL_ASOF, AS_OF, LLM_EVAL_OUTCOME_END, LLM_EVAL_T0, OUTCOME_MONTHS, WAREHOUSE
from vaios.dakr import staging

SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def asof_table() -> pd.DataFrame:
    rows = []
    for t0 in ALL_ASOF:
        if t0 == LLM_EVAL_T0:
            end = LLM_EVAL_OUTCOME_END
        elif t0 == AS_OF:
            end = AS_OF  # live screening: no outcome window yet
        else:
            end = date(t0.year + (t0.month - 1 + OUTCOME_MONTHS) // 12, (t0.month - 1 + OUTCOME_MONTHS) % 12 + 1, 1)
        rows.append({"t0": pd.Timestamp(t0), "outcome_end": pd.Timestamp(end)})
    return pd.DataFrame(rows)


def run_sql(con: duckdb.DuckDBPyConnection, files: list[Path] | None = None) -> None:
    for path in files or sorted(SQL_DIR.glob("*.sql")):
        con.execute(path.read_text())


def load_staging(con: duckdb.DuckDBPyConnection) -> None:
    tables: dict[str, pd.DataFrame] = {}
    tables |= staging.defillama()
    tables |= staging.github_activity()
    tables |= staging.x402scan()
    tables |= staging.coingecko()
    tables |= {"stg_gh_search": staging.github_search(), "stg_gh_commits": staging.github_commits(),
               "stg_hn": staging.hn(), "stg_arxiv": staging.arxiv(), "stg_yc": staging.yc()}
    tables["asof_dates"] = asof_table()
    for name, df in tables.items():
        con.register("_df", df)
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM _df")
        con.unregister("_df")
        print(f"  {name:<28} {len(df):>9,} rows")


def build(db_path: Path = WAREHOUSE) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    load_staging(con)
    run_sql(con)
    for t in ("protocols", "features_pit", "labels_pit", "x402_weekly", "commits_weekly"):
        print(f"  {t:<28} {con.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]:>9,} rows")
    con.close()


def connect(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(WAREHOUSE), read_only=read_only)
