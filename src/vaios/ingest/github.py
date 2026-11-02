"""GitHub: point-in-time activity per org (GraphQL), niche repo search, commit timestamps, READMEs.

Star timestamps are not available any more (REST 404 / GraphQL empty, ADR 0001), so point-in-time signals
are commit counts in windows before each as-of date (GraphQL `history(since, until)`) and repo creation
dates. One GraphQL query per org returns every window for every as-of date at a cost of 1 point.
"""

from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from vaios.config import ALL_ASOF, RAW
from vaios.ingest.http import gh_api, record, write_json

OUT = RAW / "github"
TOP_REPOS = 5

NICHE_QUERIES = [
    "x402", "x402 payments", "agentic payments", "agent payments", "agent commerce", "agentic commerce",
    "ai agent wallet", "mcp payments", "mcp monetization", "pay per call api agents", "AP2 agent payments",
    "stablecoin ai agents", "machine payments protocol", "agent payment protocol",
]


def _iso(d: date) -> str:
    return f"{d.isoformat()}T00:00:00Z"


def _windows() -> str:
    # u = all commits before the date, r = last 90 days, p = the 90 days before that (growth denominator)
    parts = []
    for i, d in enumerate(ALL_ASOF):
        parts.append(f'u{i}: history(until:"{_iso(d)}"){{totalCount}}')
        parts.append(f'r{i}: history(since:"{_iso(d - timedelta(days=90))}", until:"{_iso(d)}"){{totalCount}}')
        parts.append(f'p{i}: history(since:"{_iso(d - timedelta(days=180))}", '
                     f'until:"{_iso(d - timedelta(days=90))}"){{totalCount}}')
    return " ".join(parts)


def activity_query(login: str) -> str:
    return f"""query {{
  repositoryOwner(login: "{login}") {{
    login __typename
    ... on Organization {{ createdAt }}
    ... on User {{ createdAt }}
    top: repositories(first: {TOP_REPOS}, orderBy: {{field: STARGAZERS, direction: DESC}}, isFork: false) {{
      nodes {{ name createdAt pushedAt stargazerCount forkCount isArchived
        defaultBranchRef {{ target {{ ... on Commit {{ {_windows()} }} }} }} }}
    }}
    all: repositories(first: 100, isFork: false) {{ totalCount nodes {{ name createdAt stargazerCount }} }}
  }}
}}"""


def pull_org_activity(login: str) -> Path | None:
    path = OUT / "activity" / f"{login.lower()}.json.gz"
    if path.exists():
        return path
    try:
        data = gh_api("graphql", graphql=activity_query(login))
    except RuntimeError as e:
        data = {"error": str(e)[:300]}
    payload = {"login": login, "asof_dates": [d.isoformat() for d in ALL_ASOF], "response": data}
    path = write_json(path.with_suffix(""), payload, compress=True)
    record("github", f"graphql:repositoryOwner({login})", path)
    return path


def pull_many_orgs(logins: list[str], workers: int = 4) -> None:
    logins = sorted({x.strip().lower() for x in logins if x and x.strip()})
    print(f"github: activity for {len(logins)} owners")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(pull_org_activity, logins))


def search_niche() -> None:
    for q in NICHE_QUERIES:
        slug = q.replace(" ", "_")
        path = OUT / "search" / f"{slug}.json"
        if path.exists():
            continue
        api = f"search/repositories?q={q.replace(' ', '+')}&sort=stars&order=desc&per_page=100"
        data = gh_api(api)
        write_json(path, data)
        record("github", f"https://api.github.com/{api}", path, len(data.get("items", [])))


def pull_commit_timestamps(full_name: str, since: str = "2025-01-01T00:00:00Z", max_pages: int = 40) -> Path:
    path = OUT / "commits" / f"{full_name.replace('/', '__')}.json"
    if path.exists():
        return path
    stamps: list[str] = []
    for page in range(1, max_pages + 1):
        api = f"repos/{full_name}/commits?since={since}&per_page=100&page={page}"
        try:
            batch = gh_api(api)
        except RuntimeError:
            break
        stamps += [c["commit"]["committer"]["date"] for c in batch]
        if len(batch) < 100:
            break
    write_json(path, {"repo": full_name, "since": since, "commit_dates": stamps})
    record("github", f"https://api.github.com/repos/{full_name}/commits?since={since}", path, len(stamps))
    return path


def fetch_readme(full_name: str) -> str:
    data = gh_api(f"repos/{full_name}/readme")
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def fetch_repo(full_name: str) -> dict:
    return gh_api(f"repos/{full_name}")
