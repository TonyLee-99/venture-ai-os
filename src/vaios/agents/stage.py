"""Stage / investability for a $1-2M pre-seed or seed check, from sourced evidence only.

Evidence sources (each stored as a DAKR snapshot so a memo header can cite it):
- the company's own homepage and /about page: funding sentences ("$10M seed round led by a16z", "incubated
  by Stripe and Paradigm") and investor-logo alt text ("PayPal Ventures");
- DefiLlama per-protocol raises (when the company is a listed protocol);
- the YC directory (batch);
- CoinGecko market data (liquid token and FDV).
Rules (heuristic, documented in ADR 0008): a stated Series A+, a seed of $5M or more, incubation by an
incumbent, or tier-1 institutional backers on the homepage => past the fund's entry stage. A liquid token with
FDV above $100M => not a seed-stage equity deal. Anything not sourced is "unknown", never assumed.
"""

from __future__ import annotations

import json
import re
from html import unescape

import httpx

from vaios.agents.evidence import FETCHED, MAX_CHARS, html_to_text
from vaios.config import RAW, USER_AGENT
from vaios.dakr.docstore import DocStore

FUNDING = re.compile(r"[^.\n]{0,120}(\$\s?\d+(?:\.\d+)?\s?(?:m|million|b|billion)\b[^.\n]{0,80}(?:round|raise|seed|series)|"
                     r"\braised\b|\bseed round\b|\bpre-seed\b|\bseries [a-d]\b|\bincubated by\b|\bbacked by\b)[^.\n]{0,160}",
                     re.I)
TIER1 = ["a16z", "andreessen", "paradigm", "sequoia", "paypal ventures", "general catalyst", "coinbase ventures",
         "pantera", "polychain", "multicoin", "dragonfly", "electric capital", "founders fund", "lightspeed",
         "accel", "greylock", "benchmark", "union square", "variant", "haun", "framework ventures", "jump crypto"]
INCUMBENT_INCUBATORS = ["stripe", "coinbase", "google", "visa", "paypal", "binance", "okx", "circle"]


def _fetch(url: str) -> tuple[str, list[str]] | None:
    try:
        r = httpx.get(url, timeout=20, follow_redirects=True, headers={"User-Agent": USER_AGENT})
    except httpx.HTTPError:
        return None
    if r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
        return None
    alts = sorted({unescape(a).strip() for a in re.findall(r'alt="([^"]{3,60})"', r.text)})
    return html_to_text(r.text), alts


def parse(quotes: list[str], alts: list[str]) -> dict:
    blob = " ".join(quotes).lower()
    rounds = re.findall(r"pre-seed|seed|series [a-d]", blob)
    amounts = [float(a) * (1000 if u.lower().startswith("b") else 1)
               for a, u in re.findall(r"\$\s?(\d+(?:\.\d+)?)\s?(m|million|b|billion)\b", blob)]
    backers = sorted({t for t in TIER1 if t in blob or any(t in a.lower() for a in alts)})
    incub = sorted({i for i in INCUMBENT_INCUBATORS if re.search(rf"incubated by[^.]*\b{i}\b", blob)})
    return {"rounds": sorted(set(rounds)), "amounts_musd": amounts, "tier1_backers": backers,
            "incubated_by_incumbent": incub}


def gather(store: DocStore, entity: str, domain: str | None) -> dict:
    """Fetch homepage + /about, snapshot the funding evidence, return parsed signals + doc ids."""
    quotes, alts, doc_ids = [], [], []
    for path in ("", "/about"):
        if not domain:
            break
        got = _fetch(f"https://{domain}{path}")
        if not got:
            continue
        text, page_alts = got
        hits = [m.group(0).strip() for m in FUNDING.finditer(text)]
        investor_alts = [a for a in page_alts if any(t in a.lower() for t in TIER1)]
        if hits or investor_alts:
            body = (f"Funding evidence from https://{domain}{path} (fetched {FETCHED}).\n"
                    + "\n".join(f"Page text: {h}" for h in dict.fromkeys(hits))
                    + ("\nInvestor logos (image alt text): " + ", ".join(investor_alts) if investor_alts else ""))
            doc_ids.append(store.put(body[:MAX_CHARS], entity=entity, kind="funding_evidence",
                                     url=f"https://{domain}{path}", fetched_at=FETCHED, title=f"funding {entity}"))
            quotes += hits
            alts += investor_alts
    return {"quotes": list(dict.fromkeys(quotes))[:6], "investor_logos": sorted(set(alts)), "doc_ids": doc_ids,
            **parse(quotes, alts)}


def token_info(con, name: str, owner: str | None) -> dict | None:
    """Liquid token from the CoinGecko market lists already pulled (name match on the normalised name)."""
    from vaios.agents.sourcing import norm_name

    keys = {norm_name(name), norm_name(owner or "")} - {""}
    for path in sorted((RAW / "coingecko").glob("markets_*.json")):
        for m in json.loads(path.read_text()):
            if norm_name(m["name"]) in keys:
                return {"ticker": m["symbol"].upper(), "coingecko_id": m["id"], "fdv_usd": m.get("fully_diluted_valuation"),
                        "market_cap_usd": m.get("market_cap"), "source": f"https://www.coingecko.com/en/coins/{m['id']}"}
    return None


def classify(signals: dict, yc_batch: str | None, token: dict | None, prior_raises: list[dict]) -> dict:
    reasons = []
    r = signals.get("rounds", []) + [x["round"].lower() for x in prior_raises if x.get("round")]
    if any(x.startswith("series") for x in r):
        reasons.append("stated Series A or later")
    if any(a >= 5 for a in signals.get("amounts_musd", [])):
        reasons.append(f"stated raise of ${max(signals['amounts_musd']):g}M")
    if signals.get("incubated_by_incumbent"):
        reasons.append("incubated by " + ", ".join(signals["incubated_by_incumbent"]))
    if signals.get("tier1_backers"):
        reasons.append("institutional backers on homepage: " + ", ".join(signals["tier1_backers"]))
    if token and (token.get("fdv_usd") or 0) > 100e6:
        reasons.append(f"liquid token {token['ticker']} with FDV ${token['fdv_usd'] / 1e6:,.0f}M")
    if reasons:
        stage = "past entry stage"
    elif yc_batch:
        stage = f"YC {yc_batch} (pre-seed/seed)"
    elif signals.get("rounds") or prior_raises:
        stage = "early, round details partial"
    else:
        stage = "unknown (no funding evidence found)"
    return {"stage": stage, "seed_eligible": not reasons, "ineligible_reasons": reasons}
