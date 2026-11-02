"""`make dashboard`: one static HTML page (no JS libraries, no network) built only from committed results.

Charts are hand-written SVG so every mark can carry a native tooltip (<title>) and the page works offline.
Colors follow a validated categorical palette (slot 1 blue = our score, slot 2 orange = best naive baseline,
gray = other baselines / leakage-exposed reference).
"""

from __future__ import annotations

import html
import json
import math

import pandas as pd

from vaios.config import FROZEN, RESULTS, ROOT

OUT = ROOT / "dashboard" / "index.html"
SHORT = {"s_logit_full": "Logistic, all PIT features", "s_logit_github": "Logistic, GitHub-only (live score)",
         "s_heuristic": "Pre-registered heuristic", "b_random": "Random", "b_tvl": "TVL size",
         "b_commits": "Commits, last 90 days", "b_newest": "Newest listing first",
         "b_prior_funding": "Raised before (most recent first)", "leaky_stars_now": "Today's stars (leakage-exposed)"}
BLUE, ORANGE, GRAY, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#a3a29c", "#0b0b0b", "#52514e", "#e6e5e0"


def esc(x) -> str:
    return html.escape(str(x))


def load() -> dict:
    j = lambda p: json.loads((RESULTS / p).read_text())  # noqa: E731
    d = {"bt": j("backtest/backtest.json"), "cp": j("monitoring/changepoints.json"),
         "run": j("sourcing/run_summary.json")}
    for opt in ("backtest/llm_judgment.json",):
        p = RESULTS / opt
        d[opt.split("/")[-1].split(".")[0]] = json.loads(p.read_text()) if p.exists() else None
    briefs = sorted((RESULTS / "briefs").glob("*.json"))
    d["brief"] = json.loads(briefs[-1].read_text()) if briefs else None
    ledger = RESULTS / "llm_ledger.jsonl"
    d["llm_calls"] = len(ledger.read_text().splitlines()) if ledger.exists() else 0
    return d


def auc_chart(bt: dict) -> str:
    """Horizontal dot-and-whisker: AUC with 95% CI per scorer, sorted by AUC."""
    rows = sorted(bt["scores"].items(), key=lambda kv: kv[1]["auc"])
    best = bt["paired_vs_best_baseline"]["s_logit_full"]["best_baseline"]
    w, row_h, left, right = 760, 30, 250, 50
    h = row_h * len(rows) + 50
    x = lambda v: left + (v - 0.4) / 0.6 * (w - left - right)  # noqa: E731  axis 0.4..1.0
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Backtest AUC by scorer">']
    for t in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        out.append(f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="10" y2="{h - 30}" stroke="{GRID}"/>'
                   f'<text x="{x(t):.1f}" y="{h - 12}" font-size="11" fill="{MUTED}" text-anchor="middle">{t:.1f}</text>')
    for i, (k, v) in enumerate(rows):
        y = 20 + i * row_h
        color = BLUE if k.startswith("s_") else ORANGE if k == best else GRAY
        lo, hi = v["auc_ci95"]
        dash = ' stroke-dasharray="3 3"' if v["leakage_exposed"] else ""
        tip = f"{v['label']}: AUC {v['auc']:.3f} (95% CI {lo:.3f}-{hi:.3f}), lift@50 {v['lift@50']:.1f}x"
        out.append(f'<g><title>{esc(tip)}</title>'
                   f'<rect x="0" y="{y - 12}" width="{w}" height="{row_h}" fill="transparent"/>'
                   f'<text x="{left - 10}" y="{y + 4}" font-size="12" fill="{INK}" text-anchor="end">{esc(SHORT.get(k, k))}</text>'
                   f'<line x1="{x(lo):.1f}" x2="{x(hi):.1f}" y1="{y}" y2="{y}" stroke="{color}" stroke-width="2"{dash}/>'
                   f'<circle cx="{x(v["auc"]):.1f}" cy="{y}" r="5" fill="{color}" stroke="#fcfcfb" stroke-width="2"/>'
                   f'<text x="{x(hi) + 6:.1f}" y="{y + 4}" font-size="11" fill="{MUTED}">{v["auc"]:.3f}</text></g>')
    out.append("</svg>")
    return "".join(out)


def series_chart(cp: dict) -> str:
    """Weekly x402 transactions (log scale) with detected changepoints and dated events."""
    x402 = pd.read_parquet(FROZEN / "x402_daily.parquet")
    a = x402[x402["chain"] == "all"].set_index("day")["txs"]
    wk = a.resample("W-MON", label="left", closed="left").agg(["sum", "count"])
    wk = wk[wk["count"] == 7]["sum"]
    w, h, pad_l, pad_r, t, b = 760, 280, 60, 20, 20, 40
    xs = lambda d: pad_l + (d - wk.index[0]).days / max(1, (wk.index[-1] - wk.index[0]).days) * (w - pad_l - pad_r)  # noqa: E731
    lo, hi = 0, math.ceil(math.log10(wk.max()))
    ys = lambda v: t + (1 - (math.log10(max(v, 1)) - lo) / (hi - lo)) * (h - t - b)  # noqa: E731
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Weekly x402 transactions with changepoints">']
    for p in range(lo, hi + 1):
        out.append(f'<line x1="{pad_l}" x2="{w - pad_r}" y1="{ys(10**p):.1f}" y2="{ys(10**p):.1f}" stroke="{GRID}"/>'
                   f'<text x="{pad_l - 6}" y="{ys(10**p) + 4:.1f}" font-size="11" fill="{MUTED}" text-anchor="end">1e{p}</text>')
    for e in cp["events"]:
        d = pd.Timestamp(e["date"])
        if wk.index[0] <= d <= wk.index[-1]:
            out.append(f'<g><title>{esc(e["date"] + ": " + e["titles"][:160])}</title>'
                       f'<rect x="{xs(d) - 5:.1f}" y="{h - b + 2}" width="10" height="14" fill="transparent"/>'
                       f'<path d="M{xs(d):.1f},{h - b + 4} l5,9 l-10,0 z" fill="{ORANGE}"/></g>')
    for s in cp["series"][cp["headline_series"]]["segments"]:
        d = pd.Timestamp(s["date"])
        tip = f"changepoint week of {s['date']}: weekly median {s['median_before']:,.0f} -> {s['median_after']:,.0f}"
        out.append(f'<g><title>{esc(tip)}</title>'
                   f'<line x1="{xs(d):.1f}" x2="{xs(d):.1f}" y1="{t}" y2="{h - b}" stroke="{GRAY}" stroke-width="2" '
                   f'stroke-dasharray="4 3"/></g>')
    pts = " ".join(f"{xs(d):.1f},{ys(v):.1f}" for d, v in wk.items())
    out.append(f'<polyline points="{pts}" fill="none" stroke="{BLUE}" stroke-width="2"/>')
    for d, v in wk.items():
        out.append(f'<circle cx="{xs(d):.1f}" cy="{ys(v):.1f}" r="6" fill="transparent"><title>week of {d:%Y-%m-%d}: '
                   f'{v:,.0f} x402 transactions</title></circle>')
    for d in pd.date_range(wk.index[0], wk.index[-1], freq="QS"):
        out.append(f'<text x="{xs(d):.1f}" y="{h - 8}" font-size="11" fill="{MUTED}" text-anchor="middle">{d:%b %Y}</text>')
    out.append("</svg>")
    return "".join(out)


def kpi(label: str, value: str, sub: str) -> str:
    return f'<div class="kpi"><div class="kl">{esc(label)}</div><div class="kv">{esc(value)}</div><div class="ks">{esc(sub)}</div></div>'


def run() -> None:
    d = load()
    bt, cp, rs = d["bt"], d["cp"], d["run"]
    full, pair = bt["scores"]["s_logit_full"], bt["paired_vs_best_baseline"]["s_logit_full"]
    base = bt["scores"][pair["best_baseline"]]
    h = cp["headline"]
    kpis = [
        kpi("Screening AUC (walk-forward)", f"{full['auc']:.2f}",
            f"95% CI {full['auc_ci95'][0]:.2f}-{full['auc_ci95'][1]:.2f}; best naive baseline {base['auc']:.2f}"),
        kpi("Precision@50 lift", f"{full['lift@50']:.1f}x", f"vs {bt['base_rate_test']:.1%} base rate of raising within 12 months"),
        kpi("Memo citation precision", f"{rs['raw_citation_precision']:.0%} -> {rs['post_repair_citation_precision']:.0%}",
            f"first draft -> after one repair round; {rs['claims_shipped']} claims shipped"),
        kpi("Inflection hit rate", f"{h['event_hit_rate']:.0%}",
            f"vs {h['null_mean_hit_rate']:.0%} by chance (p={h['p_value']:.2f}); not significant"),
        kpi("LLM calls (ledger)", f"{d['llm_calls']}", "all cached; CI replays with zero calls"),
    ]
    memo_rows = "".join(
        f"<tr><td><a href='../results/memos/{esc(m['entity'])}.md'>{esc(m['name'])}</a></td>"
        f"<td>{m['scores_drafter']['pmf']}/{m['scores_drafter']['narrative']}/{m['scores_drafter']['execution']}</td>"
        f"<td>{m['scores_critic']['pmf']}/{m['scores_critic']['narrative']}/{m['scores_critic']['execution']}</td>"
        f"<td>{esc(m['drafter'])}</td><td>{esc(m['critic'])}</td><td>{m['shipped']}/{m['claims_drafted']}</td>"
        f"<td>{'<a href=../results/decision_cards/' + esc(m['entity']) + '.md>card</a>' if m['disagreements'] else ''}</td></tr>"
        for m in rs["memos"])
    brief_rows = ""
    if d["brief"]:
        for n in d["brief"]["brief"]["inflections"]:
            brief_rows += (f"<tr><td>{esc(n['date'])}</td><td>{esc(n['series'])}</td><td>{esc(n['headline'])}</td>"
                           f"<td>{esc(n['confidence'])}{' / needs human' if n['needs_human'] else ''}</td></tr>")
    llm = d.get("llm_judgment")
    llm_rows = "".join(f"<tr><td>{esc(k.replace('|', ' / '))}</td><td>{v['auc']:.2f}</td><td>{v['auc_ci95'][0]:.2f}-{v['auc_ci95'][1]:.2f}</td>"
                       f"<td>{'yes' if v['leakage_exposed'] else 'no'}</td></tr>"
                       for k, v in (llm["results"].items() if llm else []))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>venture-ai-os dashboard</title>
<style>
body{{font:14px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;color:{INK};background:#fcfcfb;margin:0;padding:28px 36px;max-width:1180px}}
h1{{font-size:22px;margin:0 0 4px}} h2{{font-size:16px;margin:28px 0 8px}} .sub{{color:{MUTED};margin-bottom:18px}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}} .kpi{{border:1px solid {GRID};border-radius:8px;padding:12px;background:#fff}}
.kl{{color:{MUTED};font-size:12px}} .kv{{font-size:26px;font-weight:600;margin:4px 0}} .ks{{color:{MUTED};font-size:12px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:24px}} svg{{width:100%;height:auto;font-family:inherit}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{text-align:left;padding:5px 8px;border-bottom:1px solid {GRID}}}
th{{color:{MUTED};font-weight:500}} .note{{color:{MUTED};font-size:12px}} .legend span{{margin-right:14px}}
.sw{{display:inline-block;width:10px;height:10px;border-radius:5px;margin-right:4px;vertical-align:middle}}
</style></head><body>
<h1>venture-ai-os: agentic-payments sourcing and monitoring</h1>
<div class="sub">A mini AI OS for a venture fund, built only from public data pulled 2026-11-02. Every number below is read from <code>results/</code>; hover any mark for its value.</div>
<div class="kpis">{''.join(kpis)}</div>
<div class="grid2">
<div><h2>Pre-investment: does the screening score anticipate VC raises? (held-out T0s {bt['test_t0s'][0]} to {bt['test_t0s'][-1]})</h2>
<div class="legend note"><span><i class="sw" style="background:{BLUE}"></i>our scores</span><span><i class="sw" style="background:{ORANGE}"></i>best naive baseline</span><span><i class="sw" style="background:{GRAY}"></i>other baselines (dashed = leakage-exposed)</span></div>
{auc_chart(bt)}
<div class="note">{bt['n_rows_test']:,} protocol x T0 rows, {bt['n_positives_test']} raises. Paired AUC gain over the best baseline: {pair['auc_diff']:+.3f} (95% CI {pair['ci95'][0]:+.3f} to {pair['ci95'][1]:+.3f}), so not distinguishable from it.</div></div>
<div><h2>Post-investment: weekly x402 transactions, detected changepoints, dated events</h2>
<div class="legend note"><span><i class="sw" style="background:{BLUE}"></i>weekly transactions (log)</span><span><i class="sw" style="background:{GRAY}"></i>PELT changepoint</span><span><i class="sw" style="background:{ORANGE}"></i>dated public event</span></div>
{series_chart(cp)}
<div class="note">{h['n_changepoints']} changepoints, {h['n_events']} events in range. Hit rate {h['event_hit_rate']:.0%} vs {h['null_mean_hit_rate']:.0%} expected by chance; false alarms {h['false_alarm_rate']:.0%}. Most inflections are not explained by announcements, which is why the brief flags them for a human.</div></div>
</div>
<h2>Diligence memos (drafter: Claude; critic: GPT; PMF / Narrative / Execution)</h2>
<table><tr><th>Company</th><th>Drafter P/N/E</th><th>Critic P/N/E</th><th>Drafter rec.</th><th>Critic rec.</th><th>Claims shipped / drafted</th><th>Decision card</th></tr>{memo_rows}</table>
<h2>Weekly brief: recent inflections</h2>
<table><tr><th>Week</th><th>Series</th><th>Headline</th><th>Confidence</th></tr>{brief_rows}</table>
<h2>LLM screening judgment, outcomes after the model cutoff only</h2>
<table><tr><th>Scorer</th><th>AUC</th><th>95% CI</th><th>Leakage-exposed input</th></tr>{llm_rows}</table>
<p class="note">Sources: GitHub API, DefiLlama, x402scan, CoinGecko, HN Algolia, arXiv, YC directory, x402 Foundation feed. The fund CRM used for de-duplication is SYNTHETIC. No affiliation with any fund.</p>
</body></html>"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    print(f"dashboard -> {OUT.relative_to(ROOT)}")
