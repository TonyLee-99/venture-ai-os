"""Monitoring diagnostics added later (written after the pre-specified test missed; all
EXPLORATORY except the power analysis, which only re-describes the pre-specified test).

1. power: how many of the 12 events would have to be hit for p < 0.05, and the power at plausible true rates;
2. real-time replay: PELT re-run on expanding windows -> detection delay and how often past alarms get revised;
3. matched-count comparison: PELT vs the z-score detector at the SAME number of alarms;
4. event-leads window: a changepoint counts only from 3 days before to 14 days after an event (cause first);
5. event list v2: v1 plus crypto-native catalysts (first DEX pool of every CoinGecko "x402 Ecosystem" token,
   dated by GeckoTerminal); post-hoc by construction, so never the headline;
6. artifact check of the September 2026 drop: daily shape by chain and facilitator around the break, plus
   x402scan indexer commits in that window (if pulled).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.stats import binom

from vaios.config import FROZEN, RAW, RESULTS
from vaios.dakr.docstore import DocStore
from vaios.monitoring import events as ev_mod
from vaios.monitoring import run as mon

OUT = RESULTS / "monitoring" / "diagnostics.json"
TOKEN_EVENTS = RESULTS / "monitoring" / "events_token_launches.csv"


def null_rates(weeks: pd.DatetimeIndex, n_cps: int, events: list, tol_before: int = 7, tol_after: int = 7,
               n_perm: int = 5000) -> np.ndarray:
    rng = np.random.default_rng(11)
    out = np.empty(n_perm)
    for i in range(n_perm):
        pick = [weeks[j] for j in rng.choice(np.arange(2, len(weeks) - 1), size=n_cps, replace=False)]
        out[i] = hit_rate(pick, events, tol_before, tol_after)
    return out


def hit_rate(cps: list, events: list, before: int, after: int) -> float:
    """Share of events with a changepoint in [event - before, event + after] days."""
    if not events:
        return float("nan")
    return float(np.mean([any(-before <= (c - e).days <= after for c in cps) for e in events]))


def false_alarm(cps: list, events: list, before: int, after: int) -> float:
    if not cps:
        return float("nan")
    return float(np.mean([not any(-before <= (c - e).days <= after for e in events) for c in cps]))


def power(n_events: int, null: np.ndarray, true_rates=(0.5, 0.6, 0.7, 0.8)) -> dict:
    need = next(h for h in range(n_events + 1) if (np.sum(null >= h / n_events) + 1) / (len(null) + 1) < 0.05)
    return {"events": n_events, "hits_needed_for_p_lt_0.05": int(need),
            "power_at_true_hit_rate": {str(p): round(float(binom.sf(need - 1, n_events, p)), 3) for p in true_rates}}


def realtime_replay(s: pd.Series, min_weeks: int = 20) -> dict:
    y = np.log1p(s.to_numpy(float))
    final = mon.weekly_pelt(y)
    first_seen: dict[int, int] = {}
    alarms_seen, revised = set(), 0
    prev: set[int] = set()
    for w in range(min_weeks, len(y) + 1):
        now = set(mon.weekly_pelt(y[:w]))
        settled = {c for c in prev if c < w - 5}
        revised += len(settled - now)  # an alarm older than 5 weeks that disappeared = a revision
        for c in final:
            if c not in first_seen and any(abs(c - x) <= 1 for x in now):
                first_seen[c] = w - 1
        alarms_seen |= now
        prev = now
    delays = [first_seen[c] - c for c in final if c in first_seen and c >= min_weeks]
    spurious = [a for a in alarms_seen if not any(abs(a - c) <= 1 for c in final)]
    return {"final_changepoints": len(final), "detected_in_real_time": len([c for c in final if c in first_seen]),
            "median_detection_delay_weeks": float(np.median(delays)) if delays else None,
            "detection_delays_weeks": delays, "revisions_of_settled_alarms": int(revised),
            "real_time_alarms_later_dropped": len(spurious), "min_weeks_before_first_run": min_weeks}


def matched_count(s: pd.Series, events: list) -> dict:
    y = np.log1p(s.to_numpy(float))
    weeks = s.index
    pelt_cps = [weeks[i] for i in mon.weekly_pelt(y)]
    d = pd.Series(np.diff(y, prepend=y[0]))
    z = ((d - d.rolling(8, min_periods=4).mean().shift(1)) / d.rolling(8, min_periods=4).std().shift(1)).abs()
    order = [i for i in z.sort_values(ascending=False).index if np.isfinite(z[i])]
    picked: list[int] = []
    for i in order:  # top-|z| weeks with a 2-week refractory, until the same count as PELT
        if all(abs(i - j) >= 2 for j in picked):
            picked.append(i)
        if len(picked) == len(pelt_cps):
            break
    z_cps = [weeks[i] for i in sorted(picked)]
    return {"k": len(pelt_cps),
            "pelt": {"hit_rate": hit_rate(pelt_cps, events, 7, 7), "false_alarm_rate": false_alarm(pelt_cps, events, 7, 7)},
            "zscore_top_k": {"hit_rate": hit_rate(z_cps, events, 7, 7), "false_alarm_rate": false_alarm(z_cps, events, 7, 7)}}


def token_launch_events(store: DocStore) -> pd.DataFrame:
    """Earliest DEX pool per x402-ecosystem token, kept if inside the x402 series range."""
    rows = []
    for path in sorted((RAW / "token_launches").glob("*.json")):
        rec = json.loads(path.read_text())
        dates = [p["pool_created_at"] for p in rec["pools"] if p.get("pool_created_at")]
        if not dates:
            continue
        first = min(dates)[:10]
        if first < "2025-05-09":
            continue
        text = (f"GeckoTerminal pools for {rec['name']} ({rec['symbol'].upper()}), a token in CoinGecko's 'x402 Ecosystem' "
                f"category (fetched 2026-11-02).\nEarliest pool created: {first}\n"
                + "\n".join(f"{p['network']} {p['name']}: created {p['pool_created_at']}" for p in rec["pools"][:10]))
        doc = store.put(text, entity="x402-events", kind="event_source", url=rec["pools"][0]["source"],
                        fetched_at="2026-11-02", title=f"{rec['symbol'].upper()} first DEX pool")
        rows.append({"date": first, "title": f"{rec['name']} ({rec['symbol'].upper()}) first DEX pool",
                     "url": rec["pools"][0]["source"], "source": "token_launch", "doc_id": doc})
    df = pd.DataFrame(rows, columns=["date", "title", "url", "source", "doc_id"])
    if (RAW / "token_launches").exists():
        df.to_csv(TOKEN_EVENTS, index=False)
    return pd.read_csv(TOKEN_EVENTS) if TOKEN_EVENTS.exists() else df


def artifact_check() -> dict:
    x = pd.read_parquet(FROZEN / "x402_daily.parquet")
    f = pd.read_parquet(FROZEN / "x402_facilitator_daily.parquet")
    win = (x["day"] >= "2026-08-31") & (x["day"] <= "2026-09-27")
    daily = x[win].pivot(index="day", columns="chain", values="txs")
    before = f[(f["day"] >= "2026-08-17") & (f["day"] < "2026-09-14")].groupby("facilitator")["txs"].sum()
    after = f[(f["day"] >= "2026-09-14") & (f["day"] < "2026-10-12")].groupby("facilitator")["txs"].sum()
    chg = pd.concat([before, after], axis=1, keys=["4w_before", "4w_after"]).fillna(0).sort_values("4w_before", ascending=False).head(8)
    zero_days = int((x[(x["chain"] == "all") & (x["day"] >= "2025-06-01")]["txs"] == 0).sum())
    out = {"daily_txs_by_chain_2026-08-31_to_09-27": {str(k.date()): {c: int(v) for c, v in r.items()} for k, r in daily.iterrows()},
           "top_facilitators_4w_before_vs_after_2026-09-14": {k: {c: int(v) for c, v in r.items()} for k, r in chg.iterrows()},
           "zero_txs_days_since_2025-06": zero_days}
    raw_commits, kept = RAW / "github" / "x402scan_commits_2026-09.json", RESULTS / "monitoring" / "x402scan_commits_2026-09.json"
    if raw_commits.exists():  # keep a committed copy so the check recomputes offline
        kept.write_text(raw_commits.read_text())
    if kept.exists():
        out["x402scan_commits_2026-09-01_to_09-21"] = json.loads(kept.read_text())
    return out


def run() -> dict:
    store = DocStore()
    v1 = ev_mod.grouped(ev_mod.load())
    series = mon.build_series()
    s = series[mon.MAIN]
    weeks = s.index
    in_range = lambda evs: [e for e in evs if weeks[0] <= e <= weeks[-1] + pd.Timedelta(days=6)]  # noqa: E731
    ev1 = in_range(list(v1["date"]))
    cps = [weeks[i] for i in mon.weekly_pelt(np.log1p(s.to_numpy(float)))]
    null_sym = null_rates(weeks, len(cps), ev1)
    null_lead = null_rates(weeks, len(cps), ev1, 3, 14)
    lead_hit = hit_rate(cps, ev1, 3, 14)
    tok = token_launch_events(store)
    v2_dates = sorted(set(ev1) | set(pd.to_datetime(tok["date"])))
    v2_dates = in_range(v2_dates)
    null_v2 = null_rates(weeks, len(cps), v2_dates)
    v2_hit = hit_rate(cps, v2_dates, 7, 7)
    out = {
        "status": "exploratory diagnostics written after the pre-specified test (ADR 0005) missed; ADR 0009",
        "power_preregistered_test": power(len(ev1), null_sym),
        "realtime_replay_headline_series": realtime_replay(s),
        "matched_count_vs_zscore": matched_count(s, ev1),
        "event_leads_window_3d_before_14d_after": {
            "hit_rate": round(lead_hit, 4), "null_mean": round(float(null_lead.mean()), 4),
            "p_value": round(float((np.sum(null_lead >= lead_hit) + 1) / (len(null_lead) + 1)), 4),
            "false_alarm_rate": round(false_alarm(cps, ev1, 3, 14), 4)},
        "event_list_v2_with_token_launches": {
            "n_token_launch_events": int(len(tok)), "n_events": len(v2_dates), "hit_rate": round(v2_hit, 4),
            "null_mean": round(float(null_v2.mean()), 4),
            "p_value": round(float((np.sum(null_v2 >= v2_hit) + 1) / (len(null_v2) + 1)), 4),
            "false_alarm_rate": round(false_alarm(cps, v2_dates, 7, 7), 4),
            "token_events": tok.to_dict("records")},
        "september_2026_drop_artifact_check": artifact_check(),
    }
    OUT.write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("september_2026_drop_artifact_check",)}, indent=1,
                     default=str)[:3000])
    return out
