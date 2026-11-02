"""DefiLlama: protocol universe, TVL history, dated raises and hallmarks (all free endpoints).

`/raises` is paid (HTTP 402, see ADR 0001), but each `/protocol/{slug}` response carries that protocol's
own `raises` list with dates, round names and lead investors. We pull details for every protocol that has a
GitHub org (the backtest universe) plus every protocol in the niche categories (sourcing).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from vaios.config import RAW
from vaios.ingest.http import get_json, record, write_json

BASE = "https://api.llama.fi"
OUT = RAW / "defillama"
NICHE_CATEGORIES = {"Payments", "AI Agents", "Wallets", "Developer Tools", "Crypto Card Issuer",
                    "Decentralized AI", "Telegram Bot", "Interface"}
# Keep only what the warehouse uses; the full response is mostly per-chain/per-token TVL duplicates.
KEEP = ["id", "name", "slug", "category", "github", "listedAt", "url", "twitter", "description", "gecko_id",
        "chains", "raises", "hallmarks"]


def pull_protocols() -> list[dict]:
    url = f"{BASE}/protocols"
    protocols = get_json(url)
    path = write_json(OUT / "protocols.json", protocols, compress=True)
    record("defillama", url, path, len(protocols))
    return protocols


def _detail(slug: str) -> None:
    path = OUT / "protocol" / f"{slug}.json.gz"
    if path.exists():  # idempotent: re-running ingest only fetches what is missing
        return
    url = f"{BASE}/protocol/{slug}"
    try:
        d = get_json(url)
    except RuntimeError as e:
        print(f"  skip {slug}: {e}")
        return
    slim = {k: d.get(k) for k in KEEP}
    slim["tvl"] = [[p["date"], p["totalLiquidityUSD"]] for p in (d.get("tvl") or [])]
    path = write_json(path.with_suffix(""), slim, compress=True)
    record("defillama", url, path, len(slim["tvl"]))


def pull_details(protocols: list[dict]) -> int:
    slugs = sorted({p["slug"] for p in protocols
                    if p.get("github") or p.get("category") in NICHE_CATEGORIES})
    print(f"defillama: {len(slugs)} protocol details")
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(_detail, slugs))
    return len(slugs)


def run() -> None:
    pull_details(pull_protocols())
