"""`make ingest`: pull every source in dependency order. Idempotent: existing raw files are kept."""

from __future__ import annotations

import json

from vaios.config import RAW
from vaios.ingest import defillama, github, sources
from vaios.ingest.http import read_json
from vaios.monitoring.universe import MONITORED_REPOS


def defillama_github_owners() -> list[str]:
    owners = []
    for path in (RAW / "defillama" / "protocol").glob("*.json.gz"):
        for gh in read_json(path).get("github") or []:
            owners.append(gh.split("/")[0])  # some entries are "org/repo"
    return owners


def niche_owners(min_stars: int = 20) -> list[str]:
    owners = []
    for path in (RAW / "github" / "search").glob("*.json"):
        for item in json.loads(path.read_text()).get("items", []):
            if item["stargazers_count"] >= min_stars:
                owners.append(item["owner"]["login"])
    return owners


def run(only: str | None = None) -> None:
    stages = {
        "x402scan": sources.pull_x402scan,
        "coingecko": sources.pull_coingecko,
        "hn": sources.pull_hn,
        "arxiv": sources.pull_arxiv,
        "yc": sources.pull_yc,
        "defillama": defillama.run,
        "github_search": github.search_niche,
        "github_activity": lambda: github.pull_many_orgs(defillama_github_owners() + niche_owners()),
        "github_commits": lambda: [github.pull_commit_timestamps(r) for r in MONITORED_REPOS],
    }
    for name, fn in stages.items():
        if only and name != only:
            continue
        print(f"== ingest {name}")
        fn()
