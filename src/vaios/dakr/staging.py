"""Staging: flatten raw JSON files into tidy DataFrames (one per source table), no business logic.

Everything that *means* something (features, labels, marts) is SQL in src/vaios/sql/, run by warehouse.py.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime

import pandas as pd

from vaios.config import RAW
from vaios.ingest.http import read_json


def _ts(sec: float | int | None):
    return None if sec is None else datetime.fromtimestamp(int(sec), UTC).replace(tzinfo=None)


def defillama() -> dict[str, pd.DataFrame]:
    protos, raises, tvl, hallmarks = [], [], [], []
    for path in sorted((RAW / "defillama" / "protocol").glob("*.json.gz")):
        d = read_json(path)
        d["slug"] = path.name.removesuffix(".json.gz")  # the detail endpoint does not echo the slug
        gh = [g.split("/")[0].lower() for g in (d.get("github") or [])]
        protos.append({"slug": d["slug"], "name": d["name"], "category": d.get("category"),
                       "github_owner": gh[0] if gh else None, "github_owners": ",".join(gh),
                       "listed_at": _ts(d.get("listedAt")), "url": d.get("url"),
                       "twitter": d.get("twitter"), "description": d.get("description"),
                       "gecko_id": d.get("gecko_id"), "chains": ",".join(d.get("chains") or [])})
        for r in d.get("raises") or []:
            raises.append({"slug": d["slug"], "raise_date": _ts(r["date"]), "round": r.get("round"),
                           "amount_musd": r.get("amount"), "lead_investors": ", ".join(r.get("leadInvestors") or []),
                           "other_investors": ", ".join(r.get("otherInvestors") or []),
                           "source": r.get("source") or ""})
        for day, value in d.get("tvl") or []:
            tvl.append((d["slug"], _ts(day), float(value or 0)))
        for h in d.get("hallmarks") or []:
            if isinstance(h, list) and len(h) == 2 and isinstance(h[0], int | float):
                hallmarks.append({"slug": d["slug"], "day": _ts(h[0]), "text": str(h[1])})
    return {"stg_protocols": pd.DataFrame(protos), "stg_raises": pd.DataFrame(raises),
            "stg_tvl_daily": pd.DataFrame(tvl, columns=["slug", "day", "tvl_usd"]),
            "stg_hallmarks": pd.DataFrame(hallmarks)}


def github_activity() -> dict[str, pd.DataFrame]:
    """One row per (owner, repo, asof) with commit counts in windows before asof, plus a repo-list table."""
    windows, repos, owners = [], [], []
    for path in sorted((RAW / "github" / "activity").glob("*.json.gz")):
        payload = read_json(path)
        node = (payload["response"].get("data") or {}).get("repositoryOwner") if "response" in payload else None
        if not node:
            owners.append({"owner": payload["login"], "owner_type": None, "owner_created_at": None, "found": False})
            continue
        owners.append({"owner": payload["login"], "owner_type": node["__typename"],
                       "owner_created_at": node.get("createdAt"), "found": True,
                       "repo_total_now": node["all"]["totalCount"]})
        for r in node["all"]["nodes"]:
            repos.append({"owner": payload["login"], "repo": r["name"], "repo_created_at": r["createdAt"],
                          "stars_now": r["stargazerCount"]})
        for r in node["top"]["nodes"]:
            hist = ((r.get("defaultBranchRef") or {}).get("target") or {})
            for i, asof in enumerate(payload["asof_dates"]):
                if f"u{i}" not in hist:
                    continue
                windows.append({"owner": payload["login"], "repo": r["name"], "as_of": asof,
                                "repo_created_at": r["createdAt"], "stars_now": r["stargazerCount"],
                                "forks_now": r["forkCount"], "archived": r["isArchived"],
                                "commits_before": hist[f"u{i}"]["totalCount"],
                                "commits_90d": hist[f"r{i}"]["totalCount"],
                                "commits_prev90d": hist[f"p{i}"]["totalCount"]})
    df_w = pd.DataFrame(windows)
    if len(df_w):
        df_w["as_of"] = pd.to_datetime(df_w["as_of"])
        df_w["repo_created_at"] = pd.to_datetime(df_w["repo_created_at"]).dt.tz_localize(None)
    df_r = pd.DataFrame(repos)
    if len(df_r):
        df_r["repo_created_at"] = pd.to_datetime(df_r["repo_created_at"]).dt.tz_localize(None)
    df_o = pd.DataFrame(owners)
    df_o["owner_created_at"] = pd.to_datetime(df_o["owner_created_at"]).dt.tz_localize(None)
    return {"stg_gh_windows": df_w, "stg_gh_repos": df_r, "stg_gh_owners": df_o}


def github_search() -> pd.DataFrame:
    rows = []
    for path in sorted((RAW / "github" / "search").glob("*.json")):
        q = path.stem.replace("_", " ")
        for it in json.loads(path.read_text()).get("items", []):
            rows.append({"query": q, "full_name": it["full_name"], "owner": it["owner"]["login"].lower(),
                         "owner_type": it["owner"]["type"], "description": it.get("description") or "",
                         "topics": ",".join(it.get("topics") or []), "stars_now": it["stargazers_count"],
                         "forks_now": it["forks_count"], "created_at": it["created_at"],
                         "pushed_at": it["pushed_at"], "homepage": it.get("homepage") or "",
                         "language": it.get("language")})
    df = pd.DataFrame(rows)
    for c in ("created_at", "pushed_at"):
        df[c] = pd.to_datetime(df[c]).dt.tz_localize(None)
    return df


def github_commits() -> pd.DataFrame:
    rows = []
    for path in sorted((RAW / "github" / "commits").glob("*.json")):
        d = json.loads(path.read_text())
        rows += [{"repo": d["repo"], "committed_at": t} for t in d["commit_dates"]]
    df = pd.DataFrame(rows, columns=["repo", "committed_at"])
    df["committed_at"] = pd.to_datetime(df["committed_at"]).dt.tz_localize(None)
    return df


def x402scan() -> dict[str, pd.DataFrame]:
    out = RAW / "x402scan"
    daily = []
    for chain, fname in (("all", "daily_all"), ("base", "daily_base"), ("solana", "daily_solana")):
        for b in json.loads((out / f"{fname}.json").read_text()):
            daily.append({"day": b["bucket_start"][:10], "chain": chain, "txs": b["total_transactions"],
                          "volume_usd": b["total_amount"] / 1e6,  # USDC has 6 decimals
                          "buyers": b["unique_buyers"], "sellers": b["unique_sellers"]})
    fac = []
    for b in json.loads((out / "daily_by_facilitator.json").read_text()):
        for name, s in b["facilitators"].items():
            fac.append({"day": b["bucket_start"][:10], "facilitator": name, "txs": s["total_transactions"],
                        "volume_usd": s["total_amount"] / 1e6, "buyers": s["unique_buyers"],
                        "sellers": s["unique_sellers"]})
    d1, d2 = pd.DataFrame(daily), pd.DataFrame(fac)
    d1["day"], d2["day"] = pd.to_datetime(d1["day"]), pd.to_datetime(d2["day"])
    return {"stg_x402_daily": d1, "stg_x402_facilitator_daily": d2}


def coingecko() -> dict[str, pd.DataFrame]:
    out = RAW / "coingecko"
    prices, markets = [], []
    for path in sorted(out.glob("chart_*.json")):
        d = json.loads(path.read_text())
        tok = path.stem.removeprefix("chart_")
        vols = {int(t): v for t, v in d.get("total_volumes", [])}
        caps = {int(t): v for t, v in d.get("market_caps", [])}
        for t, p in d.get("prices", []):
            prices.append({"token": tok, "day": _ts(t / 1000), "price_usd": p, "volume_usd": vols.get(int(t)),
                           "mcap_usd": caps.get(int(t))})
    for path in sorted(out.glob("markets_*.json")):
        for m in json.loads(path.read_text()):
            markets.append({"category": path.stem.removeprefix("markets_"), "id": m["id"], "symbol": m["symbol"],
                            "name": m["name"], "market_cap": m.get("market_cap"),
                            "total_volume": m.get("total_volume"), "price_change_30d": None})
    return {"stg_cg_prices": pd.DataFrame(prices), "stg_cg_markets": pd.DataFrame(markets)}


def hn() -> pd.DataFrame:
    rows = {}
    for path in sorted((RAW / "hn").glob("*.json")):
        d = json.loads(path.read_text())
        for h in d["hits"]:
            rows.setdefault(h["objectID"], {**h, "query": d["query"]})
    df = pd.DataFrame(rows.values())
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None)
    return df


def arxiv() -> pd.DataFrame:
    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring((RAW / "arxiv" / "agent_payments.xml").read_text())
    rows = []
    for e in root.findall("a:entry", ns):
        rows.append({"arxiv_id": e.findtext("a:id", namespaces=ns).rsplit("/", 1)[-1],
                     "title": re.sub(r"\s+", " ", e.findtext("a:title", namespaces=ns) or "").strip(),
                     "published": e.findtext("a:published", namespaces=ns),
                     "summary": re.sub(r"\s+", " ", e.findtext("a:summary", namespaces=ns) or "").strip()})
    df = pd.DataFrame(rows)
    df["published"] = pd.to_datetime(df["published"]).dt.tz_localize(None)
    return df


def yc() -> pd.DataFrame:
    data = read_json(RAW / "yc" / "companies.json.gz")
    keep = ["id", "name", "slug", "website", "one_liner", "long_description", "batch", "status", "launched_at",
            "team_size", "industry", "subindustry", "url"]
    df = pd.DataFrame([{k: c.get(k) for k in keep} | {"tags": ",".join(c.get("tags") or [])} for c in data])
    df["launched_at"] = pd.to_datetime(df["launched_at"], unit="s")
    return df
