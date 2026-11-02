"""The smaller public sources: x402scan, CoinGecko, HN Algolia, arXiv, YC directory.

Each function writes raw files under data/raw/<source>/ and a manifest row per file.
"""

from __future__ import annotations

import json
import time
import urllib.parse

from vaios.config import RAW
from vaios.ingest.http import get_json, get_text, record, write_json

# ---------- x402scan (Merit Systems, open source; public tRPC endpoints, no key) ----------
X402 = "https://www.x402scan.com/api/trpc/public."


def _trpc(proc: str, payload: dict) -> tuple[str, object]:
    url = X402 + proc + "?input=" + urllib.parse.quote(json.dumps({"json": payload}))
    return url, get_json(url)["result"]["data"]["json"]


def pull_x402scan() -> None:
    out = RAW / "x402scan"
    jobs = {
        "daily_all": ("stats.bucketed", {"timeframe": 0, "numBuckets": 1000}),
        "daily_base": ("stats.bucketed", {"timeframe": 0, "numBuckets": 1000, "chain": "base"}),
        "daily_solana": ("stats.bucketed", {"timeframe": 0, "numBuckets": 1000, "chain": "solana"}),
        "daily_by_facilitator": ("facilitators.bucketedStatistics", {"timeframe": 0, "numBuckets": 1000}),
        "overall": ("stats.overall", {"timeframe": 0}),
    }
    for name, (proc, payload) in jobs.items():
        url, data = _trpc(proc, payload)
        path = write_json(out / f"{name}.json", data)
        record("x402scan", url, path, len(data) if isinstance(data, list) else 1)


# ---------- CoinGecko public API (365-day cap on history) ----------
CG = "https://api.coingecko.com/api/v3"
CG_TOKENS = ["payai-network-2", "virtual-protocol", "opinion", "assisterr-ai", "usd-coin"]
CG_CATEGORIES = ["x402-ecosystem", "ai-agents", "payment-solutions"]


def pull_coingecko() -> None:
    out = RAW / "coingecko"
    for cat in CG_CATEGORIES:
        url = f"{CG}/coins/markets?vs_currency=usd&category={cat}&per_page=100&page=1"
        data = get_json(url)
        record("coingecko", url, write_json(out / f"markets_{cat}.json", data), len(data))
        time.sleep(3)  # public tier is ~5-15 calls/min
    for tok in CG_TOKENS:
        url = f"{CG}/coins/{tok}/market_chart?vs_currency=usd&days=365&interval=daily"
        try:
            data = get_json(url)
        except RuntimeError as e:
            print(f"  coingecko skip {tok}: {e}")
            continue
        record("coingecko", url, write_json(out / f"chart_{tok}.json", data), len(data.get("prices", [])))
        time.sleep(3)


# ---------- HN Algolia ----------
HN_QUERIES = ["x402", "agentic payments", "agent payments", "agentic commerce", "AP2 protocol",
              "stablecoin agents", "pay per crawl", "MCP payments"]


def pull_hn() -> None:
    out = RAW / "hn"
    for q in HN_QUERIES:
        hits, page = [], 0
        while page < 10:
            url = ("https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=200"
                   f"&page={page}&query={urllib.parse.quote(q)}")
            data = get_json(url)
            hits += data["hits"]
            page += 1
            if page >= data.get("nbPages", 0):
                break
        slim = [{k: h.get(k) for k in ("objectID", "title", "url", "points", "num_comments", "created_at",
                                       "author")} for h in hits]
        path = write_json(out / f"{q.replace(' ', '_')}.json", {"query": q, "hits": slim})
        record("hn_algolia", f"https://hn.algolia.com/api/v1/search_by_date?query={q}", path, len(slim))


# ---------- arXiv ----------
ARXIV_QUERY = ('abs:"agent payment" OR abs:"agentic payment" OR abs:"agentic commerce" OR abs:x402 '
               'OR abs:"agent-to-agent payment" OR abs:"machine-to-machine payment"')


def pull_arxiv() -> None:
    url = ("https://export.arxiv.org/api/query?search_query=" + urllib.parse.quote(ARXIV_QUERY)
           + "&start=0&max_results=200&sortBy=submittedDate&sortOrder=descending")
    xml = get_text(url, timeout=90)
    path = RAW / "arxiv" / "agent_payments.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml)
    record("arxiv", url, path, xml.count("<entry>"))


# ---------- x402 Foundation announcements feed (first-party dated events) ----------
def pull_x402_feed() -> None:
    url = "https://x402.org/feed/"
    xml = get_text(url)
    path = RAW / "x402org" / "feed.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(xml)
    record("x402_foundation_feed", url, path, xml.count("<item>"))


# ---------- YC company directory (yc-oss mirror of the public YC directory) ----------
def pull_yc() -> None:
    url = "https://yc-oss.github.io/api/companies/all.json"
    data = get_json(url, timeout=120)
    path = write_json(RAW / "yc" / "companies.json", data, compress=True)
    record("yc_directory", url, path, len(data))


# ---------- token launches in the x402 ecosystem (crypto-native catalysts for the event list) ----------
GT = "https://api.geckoterminal.com/api/v2"
GT_NETWORKS = {"base": "base", "solana": "solana", "binance-smart-chain": "bsc", "ethereum": "eth"}


def pull_token_launches() -> None:
    """CoinGecko 'x402 Ecosystem' tokens -> contract addresses -> GeckoTerminal earliest DEX pool creation date."""
    out = RAW / "token_launches"
    out.mkdir(parents=True, exist_ok=True)
    markets = json.loads((RAW / "coingecko" / "markets_x402-ecosystem.json").read_text())
    for m in markets:
        path = out / f"{m['id']}.json"
        if path.exists():
            continue
        url = f"{CG}/coins/{m['id']}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false"
        try:
            coin = get_json(url)
        except RuntimeError as e:
            print(f"  skip {m['id']}: {e}")
            continue
        time.sleep(2.5)
        pools = []
        for platform, addr in (coin.get("platforms") or {}).items():
            net = GT_NETWORKS.get(platform)
            if not net or not addr:
                continue
            gurl = f"{GT}/networks/{net}/tokens/{addr}/pools?page=1"
            try:
                data = get_json(gurl)
            except RuntimeError:
                continue
            time.sleep(2.2)  # GeckoTerminal public limit is ~30 calls/min
            pools += [{"network": net, "pool": p["id"], "pool_created_at": p["attributes"].get("pool_created_at"),
                       "name": p["attributes"].get("name"), "source": gurl} for p in data.get("data", [])]
        rec = {"id": m["id"], "symbol": m["symbol"], "name": m["name"], "genesis_date": coin.get("genesis_date"),
               "platforms": coin.get("platforms"), "pools": pools, "coingecko_url": url}
        write_json(path, rec)
        record("geckoterminal", f"{GT}/networks/*/tokens/*/pools ({m['id']})", path, len(pools))
