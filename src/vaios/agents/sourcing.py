"""Sourcing agent (deterministic, no LLM): gather niche candidates from independent public sources,
resolve them into entities, filter for relevance and investability, dedupe against the (SYNTHETIC) CRM,
and score them with the backtested GitHub-only screening model.
"""

from __future__ import annotations

import re
from collections import defaultdict
from urllib.parse import urlparse

import numpy as np
import pandas as pd

from vaios.config import AS_OF, BACKTEST_T0S, FROZEN, SYNTHETIC
from vaios.screening import score as sc

STRONG = ["x402", "agentic payment", "agent payment", "agentic commerce", "agent commerce", "ap2",
          "payments for ai agents", "agent wallet", "wallets for ai agents", "mcp monetiz", "pay-per-call",
          "pay per call", "pay-per-request", "machine payment", "agent-to-agent payment", "a2a payment",
          "agents to pay", "agents pay", "paid mcp", "monetize mcp", "payment infrastructure for ai agents"]
MEDIUM = ["stablecoin", "usdc", "micropayment", "wallet", "payment", "paywall", "billing"]
AI_CONTEXT = ["agent", " ai ", "ai-", "llm", "mcp", "autonomous"]

# Incumbents and standards bodies: relevant to the niche but not pre-seed/seed investable.
INCUMBENTS = {"coinbase", "stripe", "google", "google-agentic-commerce", "visa", "mastercard", "paypal",
              "cloudflare", "anthropics", "openai", "microsoft", "aws", "awslabs", "amazon", "shopify",
              "apify", "medusajs", "solana-foundation", "ethereum", "base", "circlefin", "x402-foundation",
              "agentic-commerce-protocol", "worldliberty", "moov-io", "thirdweb-dev", "alchemyplatform",
              "metamask", "consensys", "vercel", "supabase", "langchain-ai", "huggingface", "modelcontextprotocol"}
SHARED_DOMAINS = {"github.com", "x.com", "twitter.com", "docs.google.com", "npmjs.com", "www.npmjs.com", "t.me",
                  "docs.rs", "pypi.org", "medium.com", "linktr.ee", "discord.gg", "youtube.com", "x402.org",
                  "vercel.app", "netlify.app", "gitbook.io", "notion.site", "huggingface.co", "crates.io"}
# Company accounts of large firms: in the niche, but never a pre-seed/seed deal.
BIG_COMPANY_TOKENS = ["nvidia", "microsoft", "google", "amazon", "aws", "ibm", "oracle", "salesforce", "meta-",
                      "bnb-chain", "binance", "okx", "bitget", "bybit", "coinbase", "circle", "stripe", "visa",
                      "paypal", "alibaba", "tencent", "cloudflare", "skalenetwork", "lightninglabs", "chainlink",
                      "solana-labs", "near", "polygon", "avalanche", "ava-labs", "aptos", "sui-foundation",
                      "mysten", "starknet", "base-org", "ethereum", "openai", "anthropic", "shopify"]
STOP_SUFFIX = re.compile(r"(labs?|hq|inc|ai|protocol|network|finance|xyz|io|app|dev|org|official)$")


def norm_name(name: str) -> str:
    n = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    stripped = STOP_SUFFIX.sub("", n)
    return stripped if len(stripped) >= 3 else n


def domain(url: str | None) -> str:
    if not isinstance(url, str) or not url:
        return ""
    host = urlparse(url if "//" in url else f"https://{url}").netloc.lower()
    return host.removeprefix("www.")


def relevance(text: str) -> int:
    t = f" {text.lower()} "
    s = 2 * sum(k in t for k in STRONG)
    if any(k in t for k in AI_CONTEXT):
        s += sum(k in t for k in MEDIUM)
    return s


def mentions(con) -> pd.DataFrame:
    """One row per (source, raw candidate) with whatever identifiers that source gives."""
    rows = []
    gh = con.execute("""
        SELECT owner, any_value(owner_type) AS owner_type, string_agg(DISTINCT full_name, ', ') AS repos,
               string_agg(DISTINCT description || ' ' || topics, ' | ') AS text, max(stars_now) AS top_repo_stars,
               arg_max(homepage, stars_now) AS homepage, arg_max(full_name, stars_now) AS top_repo
        FROM stg_gh_search GROUP BY owner""").df()
    for r in gh.itertuples():
        rows.append({"source": "github_search", "name": r.owner, "github_owner": r.owner,
                     "owner_type": r.owner_type, "domain": domain(r.homepage), "text": r.text,
                     "evidence": f"https://github.com/{r.top_repo}", "top_repo": r.top_repo})
    dl = con.execute("""SELECT name, slug, category, github_owner, url, description FROM stg_protocols
                        WHERE category IN ('Payments','AI Agents','Wallets','Developer Tools','Decentralized AI',
                                           'Crypto Card Issuer','Telegram Bot','Interface')""").df()
    for r in dl.itertuples():
        rows.append({"source": "defillama", "name": r.name, "github_owner": r.github_owner, "domain": domain(r.url),
                     "text": f"{r.category}: {r.description}", "evidence": f"https://defillama.com/protocol/{r.slug}"})
    yc = con.execute("SELECT name, website, one_liner, long_description, batch, url FROM stg_yc").df()
    for r in yc.itertuples():
        text = f"{r.one_liner} {r.long_description}"
        if relevance(text) >= 2:
            rows.append({"source": "yc_directory", "name": r.name, "github_owner": None, "domain": domain(r.website),
                         "text": f"YC {r.batch}: {text}", "evidence": r.url})
    fac = con.execute("""SELECT facilitator, SUM(txs) AS txs FROM stg_x402_facilitator_daily
                         GROUP BY 1 HAVING SUM(txs) >= 1000""").df()
    for r in fac.itertuples():
        rows.append({"source": "x402scan", "name": r.facilitator, "github_owner": None, "domain": "",
                     "text": f"x402 facilitator with {int(r.txs):,} transactions",
                     "evidence": "https://www.x402scan.com/facilitators"})
    hn = con.execute("""SELECT title, url, objectID FROM stg_hn
                        WHERE title ILIKE 'Show HN%' OR title ILIKE 'Launch HN%'""").df()
    for r in hn.itertuples():
        m = re.match(r"(?:show|launch) hn:\s*([^\s–\-:,(]+(?:\s[A-Z][\w.]*)?)", r.title, re.I)
        if m and relevance(r.title) >= 2:
            rows.append({"source": "hn", "name": m.group(1), "github_owner": None, "domain": domain(r.url),
                         "text": r.title, "evidence": f"https://news.ycombinator.com/item?id={r.objectID}"})
    cg = con.execute("SELECT name, id FROM stg_cg_markets WHERE category = 'x402-ecosystem'").df()
    for r in cg.itertuples():
        rows.append({"source": "coingecko", "name": r.name, "github_owner": None, "domain": "",
                     "text": "token in CoinGecko 'x402 Ecosystem' category",
                     "evidence": f"https://www.coingecko.com/en/coins/{r.id}"})
    return pd.DataFrame(rows)


def resolve(m: pd.DataFrame) -> pd.DataFrame:
    """Union-find over shared keys (normalised name, GitHub owner, web domain) -> entity ids."""
    parent = list(range(len(m)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    first_seen: dict[str, int] = {}
    for i, r in enumerate(m.itertuples()):
        name_key = norm_name(r.name)
        keys = [f"n:{name_key}"] if len(name_key) >= 3 else []
        if isinstance(r.github_owner, str) and r.github_owner:  # NaN is truthy: check the type
            keys.append(f"g:{r.github_owner.lower()}")
        if r.domain and r.domain not in SHARED_DOMAINS:
            keys.append(f"d:{r.domain}")
        for k in keys:
            if k in first_seen:
                parent[find(i)] = find(first_seen[k])
            else:
                first_seen[k] = i
    m = m.copy()
    m["entity_idx"] = [find(i) for i in range(len(m))]
    return m


def github_scores(con) -> pd.DataFrame:
    """Apply the GitHub-only model, trained on every backtest T0, to features as of today."""
    table = pd.read_parquet(FROZEN / "backtest_table.parquet")
    train = table[table["t0"].dt.date.isin(BACKTEST_T0S)]
    model = sc.fit_logit(train.assign(raised=train["raised"].astype(int)), sc.GITHUB_FEATURES)
    now = con.execute("""
        WITH w AS (SELECT owner, SUM(commits_before) commits_before, SUM(commits_90d) commits_90d,
                          SUM(commits_prev90d) commits_prev90d FROM stg_gh_windows WHERE as_of = ? GROUP BY 1),
             r AS (SELECT owner, COUNT(*) n_repos, MIN(repo_created_at) first_repo FROM stg_gh_repos GROUP BY 1)
        SELECT w.owner, w.commits_before, w.commits_90d, w.commits_prev90d,
               ln(1 + w.commits_90d) - ln(1 + w.commits_prev90d) AS commit_growth,
               r.n_repos, datediff('day', r.first_repo, ?::TIMESTAMP) AS gh_age_days,
               o.owner_type, o.owner_created_at
        FROM w JOIN r USING (owner) LEFT JOIN stg_gh_owners o USING (owner)""",
                      [str(AS_OF), str(AS_OF)]).df()
    for col in ("tvl_t0", "tvl_growth_90d", "listing_age_days", "prior_raises", "days_since_last_raise"):
        now[col] = 0  # not used by the GitHub-only model; model_matrix needs the columns to exist
    now["screen_score"] = sc.predict(model, now, sc.GITHUB_FEATURES)
    return now


def is_incumbent(owners: list[str], name: str) -> bool:
    if set(owners) & INCUMBENTS or norm_name(name) in {norm_name(x) for x in INCUMBENTS}:
        return True
    return any(tok in o for o in owners + [name.lower()] for tok in BIG_COMPANY_TOKENS)


def owner_type(s, g: pd.DataFrame) -> str | None:
    if s is not None and isinstance(s["owner_type"], str):
        return s["owner_type"]
    known = g["owner_type"].dropna()
    return known.iloc[0] if len(known) else None


def run(con) -> pd.DataFrame:
    m = resolve(mentions(con))
    crm = pd.read_csv(SYNTHETIC / "crm_pipeline.csv")
    crm_keys = {norm_name(c): stage for c, stage in zip(crm["company"], crm["stage"], strict=True)}
    scores = github_scores(con).set_index("owner")
    ents = []
    for idx, g in m.groupby("entity_idx"):
        owners = sorted({str(o).lower() for o in g["github_owner"].dropna()})
        name = (g[g["source"] != "github_search"]["name"].tolist() or g["name"].tolist())[0]
        text = " | ".join(g["text"].fillna("").tolist())
        owner = next((o for o in owners if o in scores.index), owners[0] if owners else None)
        s = scores.loc[owner] if owner in scores.index else None
        ent = {
            "entity": norm_name(name) or f"e{idx}", "name": name, "github_owner": owner,
            "sources": ",".join(sorted(set(g["source"]))), "n_sources": g["source"].nunique(),
            "relevance": relevance(text),
            "owner_type": owner_type(s, g),
            "incumbent": is_incumbent(owners, name),
            "crm_stage": crm_keys.get(norm_name(name)),
            "screen_score": float(s["screen_score"]) if s is not None else np.nan,
            "commits_90d": int(s["commits_90d"]) if s is not None else None,
            "commit_growth": round(float(s["commit_growth"]), 3) if s is not None else None,
            "evidence": " ".join(g["evidence"].dropna().unique()[:3]),
            "top_repo": next(iter(g["top_repo"].dropna()), None),
            "facilitator": next(iter(g.loc[g["source"] == "x402scan", "name"]), None),
            "domain": next((d for d in g["domain"] if d and d != "github.com"), ""),
            "text": text[:600],
        }
        ents.append(ent)
    df = pd.DataFrame(ents)
    # second pass: a facilitator id that prefixes a GitHub owner (payAI -> payainetwork) is the same company
    facs = [f for f in m.loc[m["source"] == "x402scan", "name"] if len(f) >= 5]
    for i, r in df[df["facilitator"].isna() & df["github_owner"].notna()].iterrows():
        hit = next((f for f in facs if r["github_owner"].startswith(f.lower())), None)
        if hit:
            df.loc[i, "facilitator"] = hit
            df.loc[i, "sources"] = ",".join(sorted(set(r["sources"].split(",")) | {"x402scan"}))
    df["relevant"] = df["relevance"] >= 2
    df["investable"] = ~df["incumbent"] & (df["owner_type"].fillna("Organization") != "User")
    df["new_to_crm"] = df["crm_stage"].isna()
    df = df.sort_values(["relevant", "investable", "screen_score"], ascending=False, na_position="last")
    df["rank"] = range(1, len(df) + 1)
    return df.reset_index(drop=True)


CORE_RELEVANCE = 4  # at least two strong niche terms: the memo queue is for core agentic-payments companies


def shortlist(df: pd.DataFrame, n: int | None = 8) -> pd.DataFrame:
    """Memo queue: core-niche, investable, NOT already in the CRM, scored, with a repo to read."""
    ok = df[df["investable"] & df["new_to_crm"] & (df["relevance"] >= CORE_RELEVANCE)
            & df["screen_score"].notna() & df["top_repo"].notna()]
    return ok if n is None else ok.head(n)


def source_counts(df: pd.DataFrame) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for s in df["sources"]:
        for x in s.split(","):
            counts[x] += 1
    return dict(sorted(counts.items()))
