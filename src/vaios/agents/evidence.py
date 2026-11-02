"""Evidence gathering for one company: source snapshots into the DAKR doc store + a warehouse facts sheet.

Runs only when the warehouse and network are available (`make reproduce`). The results (snapshots in
store/, facts in results/facts/) are committed, so the LLM steps can replay offline.
"""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser

import httpx

from vaios.config import AS_OF, RESULTS, USER_AGENT
from vaios.dakr.docstore import DocStore
from vaios.ingest import github

FACTS = RESULTS / "facts"
MAX_CHARS = 9000
FETCHED = "2026-11-02"  # date of the live pulls this run was built from


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip and data.strip():
            self.parts.append(data.strip())


def html_to_text(html: str) -> str:
    p = _Text()
    p.feed(html)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(p.parts))


def fetch_website(domain: str) -> str | None:
    try:
        r = httpx.get(f"https://{domain}", timeout=20, follow_redirects=True, headers={"User-Agent": USER_AGENT})
        if r.status_code != 200 or "html" not in r.headers.get("content-type", ""):
            return None
        text = html_to_text(r.text)
        return text[:9000] if len(text) >= 300 else None  # JS-only shells have no readable text
    except httpx.HTTPError:
        return None


def github_profile_text(con, owner: str) -> str:
    rows = con.execute("""
        SELECT full_name, any_value(description) d, max(stars_now) s, max(forks_now) f, min(created_at) c,
               max(pushed_at) p, any_value(topics) t, any_value(language) l
        FROM stg_gh_search WHERE owner = ? GROUP BY 1 ORDER BY s DESC LIMIT 8""", [owner]).fetchall()
    o = con.execute("SELECT owner_type, owner_created_at, repo_total_now FROM stg_gh_owners WHERE owner = ?",
                    [owner]).fetchone()
    lines = [f"GitHub owner: {owner}", f"Source: GitHub REST/GraphQL API, fetched {FETCHED}."]
    if o:
        lines.append(f"Account type: {o[0]}. Account created: {str(o[1])[:10]}. Public non-fork repositories: {o[2]}.")
    for full, d, s, f, c, p, t, lang in rows:
        lines.append(f"\nRepository {full}\nDescription: {d}\nStars: {s}. Forks: {f}. Language: {lang}.\n"
                     f"Created: {str(c)[:10]}. Last push: {str(p)[:10]}.\nTopics: {t}")
    return "\n".join(lines)


def hn_text(con, name: str) -> str | None:
    if len(name) < 4:
        return None
    rows = con.execute("""SELECT created_at, title, points, num_comments, objectID FROM stg_hn
                          WHERE title ILIKE ? ORDER BY created_at""", [f"%{name}%"]).fetchall()
    if not rows:
        return None
    lines = [f"Hacker News stories whose title mentions '{name}' (HN Algolia API, fetched {FETCHED}):"]
    lines += [f"{str(c)[:10]} | {t} | {p} points | {n} comments | https://news.ycombinator.com/item?id={i}"
              for c, t, p, n, i in rows]
    return "\n".join(lines)


def yc_text(con, name: str) -> str | None:
    r = con.execute("SELECT name, batch, one_liner, long_description, website, url FROM stg_yc WHERE lower(name) = lower(?)",
                    [name]).fetchone()
    if not r:
        return None
    return (f"Y Combinator company directory entry (yc-oss mirror, fetched {FETCHED})\nName: {r[0]}\nBatch: {r[1]}\n"
            f"One-liner: {r[2]}\nDescription: {r[3]}\nWebsite: {r[4]}\nYC page: {r[5]}")


def x402_text(con, facilitator: str) -> str | None:
    r = con.execute("""SELECT MIN(day), MAX(day), SUM(txs), SUM(volume_usd) FROM stg_x402_facilitator_daily
                       WHERE facilitator = ? AND txs > 0""", [facilitator]).fetchone()
    if not r or r[2] is None:
        return None
    return (f"x402scan public statistics for facilitator '{facilitator}' (fetched {FETCHED}).\n"
            f"First day with transactions: {str(r[0])[:10]}. Last day: {str(r[1])[:10]}.\n"
            f"Total x402 transactions settled: {int(r[2]):,}. Total volume: {r[3]:,.0f} USD.")


def gather(con, store: DocStore, cand: dict) -> list[str]:
    """Snapshot every available source for one candidate; returns doc_ids (sorted for stable prompts)."""
    entity, owner, name = cand["entity"], cand["github_owner"], cand["name"]

    def put(text: str, **kw) -> str:
        return store.put(text[:MAX_CHARS], **kw)  # stored == shown to the model == verified against

    ids = [put(github_profile_text(con, owner), entity=entity, kind="github_profile",
                     url=f"https://github.com/{owner}", fetched_at=FETCHED, title=f"GitHub profile {owner}")]
    if cand.get("top_repo"):
        try:
            readme = github.fetch_readme(cand["top_repo"])[:9000]
            ids.append(put(readme, entity=entity, kind="github_readme",
                                 url=f"https://github.com/{cand['top_repo']}", fetched_at=FETCHED,
                                 title=f"README {cand['top_repo']}"))
        except RuntimeError:
            pass
    if cand.get("domain"):
        site = fetch_website(cand["domain"])
        if site:
            ids.append(put(site, entity=entity, kind="website", url=f"https://{cand['domain']}",
                                 fetched_at=FETCHED, title=f"Homepage {cand['domain']}"))
    if cand.get("domain"):
        about = fetch_website(f"{cand['domain']}/about")
        if about:
            ids.append(put(about, entity=entity, kind="website_about", url=f"https://{cand['domain']}/about",
                           fetched_at=FETCHED, title=f"About page {cand['domain']}"))
    if cand.get("top_repo"):
        team = contributors_text(cand["top_repo"])
        if team:
            ids.append(put(team, entity=entity, kind="github_contributors",
                           url=f"https://github.com/{cand['top_repo']}/graphs/contributors", fetched_at=FETCHED,
                           title=f"Contributors {cand['top_repo']}"))
    ids.append(put(market_structure(con), entity="x402-market", kind="market_structure",
                   url="https://www.x402scan.com/facilitators", fetched_at=FETCHED, title="x402 facilitator shares"))
    mon = monitor_findings(cand)
    if mon:
        ids.append(put(mon, entity=entity, kind="monitor_findings", url="results/monitoring/changepoints.json",
                       fetched_at=FETCHED, title=f"monitor {name}"))
    for kind, text, url in (("hn", hn_text(con, name), "https://hn.algolia.com"),
                            ("yc", yc_text(con, name), "https://www.ycombinator.com/companies"),
                            ("x402scan", x402_text(con, cand.get("facilitator") or ""), "https://www.x402scan.com")):
        if text:
            ids.append(put(text, entity=entity, kind=kind, url=url, fetched_at=FETCHED, title=f"{kind} {name}"))
    return sorted(set(ids))


def facts_sheet(con, cand: dict, n_candidates: int) -> dict:
    owner = cand["github_owner"]
    f: dict[str, float] = {}
    desc: dict[str, str] = {}
    w = con.execute("""SELECT SUM(commits_90d), SUM(commits_prev90d), SUM(commits_before) FROM stg_gh_windows
                       WHERE owner = ? AND as_of = ?""", [owner, str(AS_OF)]).fetchone()
    if w and w[0] is not None:
        f["gh.commits_90d"], f["gh.commits_prev_90d"], f["gh.commits_total"] = map(int, w)
        desc["gh.commits_90d"] = f"commits on default branches of the owner's top 5 repos, 90 days before {AS_OF}"
        desc["gh.commits_prev_90d"] = "same, for the 90 days before that"
        desc["gh.commits_total"] = f"all commits on those branches before {AS_OF}"
    r = con.execute("SELECT COUNT(*), SUM(stars_now), year(MIN(repo_created_at)) FROM stg_gh_repos WHERE owner = ?",
                    [owner]).fetchone()
    if r and r[0]:
        f["gh.public_repos"], f["gh.stars_total_now"], f["gh.first_repo_year"] = int(r[0]), int(r[1] or 0), int(r[2])
        desc["gh.stars_total_now"] = "stars today across the owner's repos (current snapshot, not point-in-time)"
        desc["gh.public_repos"] = "public non-fork repositories (first 100)"
        desc["gh.first_repo_year"] = "year the owner's oldest public repo was created"
    # The screening rank is a triage signal, not evidence: it is shown in the memo header but never offered as a
    # fact a claim could cite (the GitHub-only score is near chance on never-raised protocols, see backtest.json).
    x = facilitator_window(con, cand.get("facilitator") or "")
    if x and x[0]:
        f["x402.txs_30d"], f["x402.volume_usd_30d"], f["x402.peak_daily_buyers_30d"] = int(x[0]), round(x[1], 2), int(x[2])
        desc["x402.txs_30d"] = "x402 transactions settled by this facilitator in the 30 days to the as-of date"
        # inorganic-traffic indicators: tiny value per payment and many payments per buyer suggest bots/mints
        f["x402.usd_per_tx_30d"] = round(x[1] / x[0], 4)
        f["x402.txs_per_peak_daily_buyer_30d"] = round(x[0] / max(x[2], 1), 1)
        desc["x402.usd_per_tx_30d"] = "average USD value per x402 payment, last 30 days"
        desc["x402.txs_per_peak_daily_buyer_30d"] = "30-day payments divided by the peak daily count of distinct buyers"
        share = facilitator_shares(con).get(cand.get("facilitator"))
        if share:
            f["x402.share_of_all_txs_30d"] = round(float(share[0]), 4)
            desc["x402.share_of_all_txs_30d"] = "this facilitator's share of all x402 payments, last 30 days"
    h = con.execute("SELECT COUNT(*), COALESCE(SUM(points),0) FROM stg_hn WHERE title ILIKE ?",
                    [f"%{cand['name']}%"]).fetchone() if len(cand["name"]) >= 4 else (0, 0)
    f["hn.stories"], f["hn.points_total"] = int(h[0]), int(h[1])
    desc["hn.stories"] = "Hacker News stories with the company name in the title"
    return {"entity": cand["entity"], "as_of": str(AS_OF), "facts": f, "descriptions": desc}


def monitor_findings(cand: dict) -> str | None:
    """What the post-investment monitor measured for this company, so the two jobs share one view."""
    path = RESULTS / "monitoring" / "changepoints.json"
    fac = cand.get("facilitator")
    if not fac or not path.exists():
        return None
    series = json.loads(path.read_text())["series"].get(f"facilitator_{fac}_txs")
    if not series:
        return None
    lines = [f"Monitor findings for x402 facilitator '{fac}' (weekly transactions from x402scan, PELT changepoints, "
             f"computed by this system on data fetched {FETCHED}):"]
    lines += [f"Week of {g['date']}: weekly median transactions {g['median_before']:,.0f} -> {g['median_after']:,.0f} "
              f"({g['direction']}, ratio {g['ratio']})" for g in series["segments"]]
    return "\n".join(lines)


# The 30 days TO the as-of date: [AS_OF - 30 days, AS_OF). Round 1 had no upper bound, so data fetched on
# 2026-11-02 leaked Nov 1-2 into "the last 30 days" (32 days). tests/test_windows.py pins the boundaries.
WINDOW = "day >= ?::TIMESTAMP - INTERVAL 30 DAY AND day < ?::TIMESTAMP"


def facilitator_window(con, facilitator: str, as_of=AS_OF):
    return con.execute(f"""SELECT SUM(txs), SUM(volume_usd), MAX(buyers) FROM stg_x402_facilitator_daily
                           WHERE facilitator = ? AND {WINDOW}""", [facilitator, str(as_of), str(as_of)]).fetchone()


def facilitator_shares(con, as_of=AS_OF) -> dict:
    """facilitator -> (share of payments, share of volume, payments, volume) over the 30-day window."""
    rows = con.execute(f"""WITH t AS (SELECT facilitator, SUM(txs) txs, SUM(volume_usd) vol
                                      FROM stg_x402_facilitator_daily WHERE {WINDOW} GROUP BY 1)
                           SELECT facilitator, txs / SUM(txs) OVER (), vol / SUM(vol) OVER (), txs, vol FROM t""",
                       [str(as_of), str(as_of)]).fetchall()
    return {f: (ts, vs, t, v) for f, ts, vs, t, v in rows}


def market_structure(con) -> str:
    """Competitive map from the warehouse: x402 facilitator shares (the comparable set for any facilitator)."""
    rows = sorted(((f, t, v, ts, vs) for f, (ts, vs, t, v) in facilitator_shares(con).items() if t > 0),
                  key=lambda r: -r[1])[:12]
    lines = [f"x402 facilitator market share, 30 days to {AS_OF} (x402scan public data, fetched {FETCHED}):"]
    lines += [f"{f}: {int(t):,} payments ({ts:.1%} of payments), {v:,.0f} USD ({vs:.1%} of volume)"
              for f, t, v, ts, vs in rows]
    return "\n".join(lines)


def contributors_text(top_repo: str) -> str | None:
    """Public team signal: top contributors of the main repo (logins and commit counts only)."""
    try:
        data = github.gh_api(f"repos/{top_repo}/contributors?per_page=8")
    except RuntimeError:
        return None
    if not isinstance(data, list) or not data:
        return None
    lines = [f"Top contributors to github.com/{top_repo} (GitHub API, fetched {FETCHED}):"]
    lines += [f"{c['login']} ({c.get('type', 'User')}): {c['contributions']} commits" for c in data]
    return "\n".join(lines)


def save_facts(sheet: dict) -> None:
    FACTS.mkdir(parents=True, exist_ok=True)
    (FACTS / f"{sheet['entity']}.json").write_text(json.dumps(sheet, indent=1) + "\n")


def load_facts(entity: str) -> dict:
    return json.loads((FACTS / f"{entity}.json").read_text())
