"""`make freeze`: export the small tables that offline tests and backtests recompute from (committed).

The warehouse itself (data/warehouse.duckdb) is gitignored and rebuilt from raw pulls; these Parquet files
are the frozen, reviewable inputs of every number in results/.
"""

from __future__ import annotations

import json
from collections import defaultdict

import pandas as pd

from vaios.config import FROZEN, RAW, RESULTS
from vaios.dakr.warehouse import connect

BACKTEST_SQL = """
SELECT f.*, l.raised, l.n_raises, l.amount_musd, l.first_raise_at, l.leads,
       a.outcome_end, COALESCE(s.stars_now, 0) AS leaky_stars_now
FROM features_pit f
JOIN labels_pit l USING (t0, slug)
JOIN asof_dates a USING (t0)
LEFT JOIN leaky_reference s ON s.owner = f.github_owner
ORDER BY t0, slug
"""


def run() -> None:
    FROZEN.mkdir(parents=True, exist_ok=True)
    con = connect()
    exports = {
        "backtest_table": BACKTEST_SQL,
        "x402_daily": "SELECT * FROM stg_x402_daily ORDER BY chain, day",
        "x402_facilitator_daily": "SELECT * FROM stg_x402_facilitator_daily WHERE txs > 0 ORDER BY facilitator, day",
        "commits_weekly": "SELECT * FROM commits_weekly ORDER BY repo, week",
        "hn_stories": "SELECT objectID, title, url, points, num_comments, created_at, query FROM stg_hn ORDER BY created_at",
        "raises": "SELECT slug, raise_date, round, amount_musd, lead_investors, other_investors FROM raises ORDER BY slug, raise_date",
        "top_repos": "SELECT DISTINCT owner, repo, repo_created_at FROM stg_gh_windows ORDER BY owner, repo",
        # first public signals per protocol, for the lead-time analysis (repo dates reflect TODAY's repos)
        "protocol_dates": """SELECT p.slug, p.name, p.github_owner, p.listed_at_eff,
                                    (SELECT MIN(repo_created_at) FROM stg_gh_repos r WHERE r.owner = p.github_owner) AS first_repo_at,
                                    (SELECT MIN(raise_date) FROM raises x WHERE x.slug = p.slug) AS first_raise_at
                             FROM protocols p WHERE p.github_owner IS NOT NULL ORDER BY p.slug""",
    }
    for name, sql in exports.items():
        out = FROZEN / f"{name}.parquet"
        con.execute(f"COPY ({sql}) TO '{out}' (FORMAT parquet, COMPRESSION zstd)")
        n = con.execute(f"SELECT COUNT(*) FROM ({sql})").fetchone()[0]
        print(f"  {out.relative_to(RESULTS.parent)}  {n:,} rows")
    con.close()
    summarize_manifest()


def summarize_manifest() -> None:
    """Committed summary of the gitignored raw manifest: per source files, records, bytes, fetch window."""
    rows = [json.loads(x) for x in (RAW / "_manifest.jsonl").read_text().splitlines()]
    latest = {}
    for r in rows:  # a re-pull of the same path supersedes the older row
        latest[r["path"]] = r
    agg: dict[str, dict] = defaultdict(lambda: {"files": 0, "bytes": 0, "records": 0, "first_fetch": None,
                                                 "last_fetch": None, "example_urls": []})
    for r in latest.values():
        a = agg[r["source"]]
        a["files"] += 1
        a["bytes"] += r["bytes"]
        a["records"] += r["n_records"] or 0
        a["first_fetch"] = min(filter(None, [a["first_fetch"], r["fetched_at"]]))
        a["last_fetch"] = max(filter(None, [a["last_fetch"], r["fetched_at"]]))
        if len(a["example_urls"]) < 3:
            a["example_urls"].append(r["url"])
    out = {"n_sources": len(agg), "n_files": len(latest), "sources": dict(sorted(agg.items()))}
    files = pd.DataFrame(sorted(latest.values(), key=lambda r: r["path"]))
    files[["source", "url", "fetched_at", "sha256", "bytes", "path", "n_records"]].to_csv(
        RESULTS / "data_manifest_files.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    (RESULTS / "data_manifest.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"  results/data_manifest.json  {len(agg)} sources, {len(latest)} files")
