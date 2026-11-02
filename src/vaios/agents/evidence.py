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
    f["screen.score"] = round(float(cand["screen_score"]), 4)
    f["screen.rank"] = int(cand["rank"])
    f["screen.n_candidates"] = int(n_candidates)
    desc["screen.score"] = "GitHub-only screening model probability (backtested, see results/backtest)"
    desc["screen.rank"] = "rank among all sourced candidates"
    x = con.execute("""SELECT SUM(txs), SUM(volume_usd), MAX(buyers) FROM stg_x402_facilitator_daily
                       WHERE facilitator = ? AND day >= ?::TIMESTAMP - INTERVAL 30 DAY""",
                    [cand.get("facilitator") or "", str(AS_OF)]).fetchone()
    if x and x[0]:
        f["x402.txs_30d"], f["x402.volume_usd_30d"], f["x402.peak_daily_buyers_30d"] = int(x[0]), round(x[1], 2), int(x[2])
        desc["x402.txs_30d"] = "x402 transactions settled by this facilitator in the 30 days to the as-of date"
    h = con.execute("SELECT COUNT(*), COALESCE(SUM(points),0) FROM stg_hn WHERE title ILIKE ?",
                    [f"%{cand['name']}%"]).fetchone() if len(cand["name"]) >= 4 else (0, 0)
    f["hn.stories"], f["hn.points_total"] = int(h[0]), int(h[1])
    desc["hn.stories"] = "Hacker News stories with the company name in the title"
    return {"entity": cand["entity"], "as_of": str(AS_OF), "facts": f, "descriptions": desc}


def save_facts(sheet: dict) -> None:
    FACTS.mkdir(parents=True, exist_ok=True)
    (FACTS / f"{sheet['entity']}.json").write_text(json.dumps(sheet, indent=1) + "\n")


def load_facts(entity: str) -> dict:
    return json.loads((FACTS / f"{entity}.json").read_text())
