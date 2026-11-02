"""Dated public events for changepoint validation, built by the mechanical rule in ADR 0005.

Each event is also stored as a source snapshot (DAKR doc store) so the weekly brief can cite it.
Network is needed only to (re)build; the result is committed as results/monitoring/events.csv.
"""

from __future__ import annotations

import re
from email.utils import parsedate_to_datetime

import pandas as pd

from vaios.agents.evidence import FETCHED, MAX_CHARS, fetch_website, html_to_text
from vaios.config import FROZEN, RAW, RESULTS
from vaios.dakr.docstore import DocStore
from vaios.ingest.http import get_text

EVENTS_CSV = RESULTS / "monitoring" / "events.csv"
CURATED = [  # third-party launches; kept only if the fetched page shows the date (verified below)
    ("2025-09-16", "Google announces the Agent Payments Protocol (AP2)",
     "https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol",
     "September 16, 2025"),
    ("2025-09-23", "Cloudflare and Coinbase announce the x402 Foundation", "https://blog.cloudflare.com/x402/",
     "September 23, 2025"),
    ("2026-07-01", "Cloudflare Monetization Gateway: charge for any resource via x402",
     "https://blog.cloudflare.com/monetization-gateway/", "July 1, 2026"),
]
HN_PATTERN = r"x402|\bAP2\b|agentic payments?|agentic commerce"
HN_MIN_POINTS = 15
MERGE_DAYS = 3


def feed_events(store: DocStore) -> list[dict]:
    xml = (RAW / "x402org" / "feed.xml").read_text()
    out = []
    for title, link, pub, body in re.findall(
            r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>(.*?)</item>", xml, re.S):
        day = parsedate_to_datetime(pub).date().isoformat()
        title = re.sub(r"<!\[CDATA\[|\]\]>", "", title).strip()
        desc = html_to_text(re.sub(r"<!\[CDATA\[|\]\]>", "", body))[:2000]
        text = f"x402 Foundation announcement feed (https://x402.org/feed/), fetched {FETCHED}.\n" \
               f"Title: {title}\nPublished: {pub.strip()}\nLink: {link.strip()}\n\n{desc}"
        doc = store.put(text[:MAX_CHARS], entity="x402-events", kind="event_source", url=link.strip(),
                        fetched_at=FETCHED, title=title)
        out.append({"date": day, "title": title, "url": link.strip(), "source": "x402_foundation_feed", "doc_id": doc})
    return out


def curated_events(store: DocStore) -> tuple[list[dict], list[str]]:
    out, rejected = [], []
    for day, title, url, date_str in CURATED:
        try:
            text = html_to_text(get_text(url))
        except Exception:  # noqa: BLE001 - an unreachable page simply fails verification
            text = fetch_website(url.split("/")[2]) or ""
        pos = text.find(date_str)
        if pos < 0:
            rejected.append(f"{url}: date '{date_str}' not found on page")
            continue
        snippet = f"Fetched {FETCHED} from {url}\n\n" + text[max(0, pos - 1500):pos + 6000]
        doc = store.put(snippet[:MAX_CHARS], entity="x402-events", kind="event_source", url=url,
                        fetched_at=FETCHED, title=title)
        out.append({"date": day, "title": title, "url": url, "source": "curated_verified", "doc_id": doc})
    return out, rejected


def hn_events(store: DocStore) -> list[dict]:
    hn = pd.read_parquet(FROZEN / "hn_stories.parquet").drop_duplicates("objectID")
    hits = hn[hn["title"].str.contains(HN_PATTERN, case=False, regex=True) & (hn["points"] >= HN_MIN_POINTS)]
    out = []
    for r in hits.sort_values("created_at").itertuples():
        text = (f"Hacker News story (HN Algolia API, fetched {FETCHED})\nTitle: {r.title}\n"
                f"Posted: {r.created_at:%Y-%m-%d}\nPoints: {r.points}\nComments: {r.num_comments}\n"
                f"Link: {r.url}\nDiscussion: https://news.ycombinator.com/item?id={r.objectID}")
        doc = store.put(text, entity="x402-events", kind="event_source",
                        url=f"https://news.ycombinator.com/item?id={r.objectID}", fetched_at=FETCHED, title=r.title)
        out.append({"date": f"{r.created_at:%Y-%m-%d}", "title": r.title, "url": r.url or "", "source": "hn",
                    "doc_id": doc})
    return out


def build(store: DocStore | None = None) -> pd.DataFrame:
    store = store or DocStore()
    cur, rejected = curated_events(store)
    ev = pd.DataFrame(feed_events(store) + cur + hn_events(store))
    ev["date"] = pd.to_datetime(ev["date"])
    ev = ev.sort_values(["date", "source"]).reset_index(drop=True)
    # merge events within MERGE_DAYS of the previous kept event (same news, several sources)
    group, last = [], None
    for d in ev["date"]:
        if last is None or (d - last).days > MERGE_DAYS:
            group.append((group[-1] + 1) if group else 0)
            last = d
        else:
            group.append(group[-1])
    ev["event_group"] = group
    EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    ev.to_csv(EVENTS_CSV, index=False)
    for r in rejected:
        print("  event rejected:", r)
    return ev


def load() -> pd.DataFrame:
    ev = pd.read_csv(EVENTS_CSV, parse_dates=["date"])
    return ev


def grouped(ev: pd.DataFrame) -> pd.DataFrame:
    """One row per merged event: earliest date, all titles and doc_ids."""
    return ev.groupby("event_group").agg(date=("date", "min"), titles=("title", " | ".join),
                                         sources=("source", lambda s: ",".join(sorted(set(s)))),
                                         doc_ids=("doc_id", lambda s: ",".join(s))).reset_index()
