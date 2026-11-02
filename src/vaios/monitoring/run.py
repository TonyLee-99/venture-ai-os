"""`make monitor`: weekly traction series -> PELT changepoints -> validation against dated events (ADR 0005)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from vaios.config import FROZEN, RAW, RESULTS
from vaios.monitoring import changepoint as cp
from vaios.monitoring import events as ev_mod

OUT = RESULTS / "monitoring"
MAIN = "x402_all_txs"
N_FACILITATORS = 6


def weekly(df: pd.DataFrame, value: str, how: str = "sum") -> pd.Series:
    d = df.set_index("day")[value].sort_index()
    counts = d.resample("W-MON", label="left", closed="left").count()
    w = d.resample("W-MON", label="left", closed="left").agg(how)
    return w[counts == 7]  # drop partial first/last weeks


def build_series() -> dict[str, pd.Series]:
    x = pd.read_parquet(FROZEN / "x402_daily.parquet")
    series = {}
    for chain in ("all", "base", "solana"):
        c = x[x["chain"] == chain]
        series[f"x402_{chain}_txs"] = weekly(c, "txs")
    a = x[x["chain"] == "all"]
    series["x402_all_volume_usd"] = weekly(a, "volume_usd")
    series["x402_all_peak_daily_buyers"] = weekly(a, "buyers", "max")
    f = pd.read_parquet(FROZEN / "x402_facilitator_daily.parquet")
    top = f.groupby("facilitator")["txs"].sum().nlargest(N_FACILITATORS).index
    for name in sorted(top):
        g = f[f["facilitator"] == name].set_index("day")["txs"]
        full = g.reindex(pd.date_range(a["day"].min(), a["day"].max(), freq="D"), fill_value=0)
        s = weekly(full.rename_axis("day").reset_index(name="txs"), "txs")
        series[f"facilitator_{name}_txs"] = s[s.cumsum() > 0]  # start at the facilitator's first activity
    return series


def zscore_weekly(y: np.ndarray) -> list[int]:
    return cp.zscore_detector(y, window=8, thresh=2.5, refractory=2)


def weekly_pelt(y: np.ndarray, pen_mult: float = 1.0) -> list[int]:
    sigma = cp.robust_sigma(y)
    import ruptures as rpt

    pen = pen_mult * 2 * sigma**2 * np.log(len(y))
    bkps = rpt.Pelt(model="l2", min_size=2, jump=1).fit(y.reshape(-1, 1)).predict(pen=pen)
    return [b for b in bkps if b < len(y)]


def evaluate(s: pd.Series, event_days: list[pd.Timestamp], pen_mult: float = 1.0) -> dict:
    y = np.log1p(s.to_numpy(float))
    weeks = s.index
    in_range = [e for e in event_days if weeks[0] <= e <= weeks[-1] + pd.Timedelta(days=6)]
    cps = weekly_pelt(y, pen_mult)
    # a changepoint at week index i means the new regime starts the week of weeks[i]
    cp_days = [weeks[i] for i in cps]
    m = cp.match(cp_days, in_range)
    # null: same number of changepoints at random weeks (ADR 0005)
    rng = np.random.default_rng(11)
    rates = []
    for _ in range(5000):
        pick = rng.choice(np.arange(2, len(weeks) - 1), size=min(len(cps), len(weeks) - 3), replace=False)
        rates.append(cp.match([weeks[i] for i in pick], in_range)["event_hit_rate"])
    rates = np.array(rates)
    m["null_mean_hit_rate"] = round(float(np.nanmean(rates)), 4)
    m["p_value"] = round(float((np.sum(rates >= m["event_hit_rate"]) + 1) / (len(rates) + 1)), 4)
    z = [weeks[i] for i in zscore_weekly(y)]
    m["baseline_zscore"] = {k: v for k, v in cp.match(z, in_range).items() if k != "hit_events"}
    m["segments"] = cp.segments(weeks, s.to_numpy(float), cps)
    m["weeks"] = len(weeks)
    return m


def run() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    if (RAW / "x402org" / "feed.xml").exists():
        ev = ev_mod.build()
    else:
        ev = ev_mod.load()
    groups = ev_mod.grouped(ev)
    event_days = list(groups["date"])
    series = build_series()
    results = {}
    for name, s in series.items():
        if len(s) < 8:
            continue
        results[name] = evaluate(s, event_days)
    main = series[MAIN]
    sensitivity = {f"pen_x{m}": {k: v for k, v in evaluate(main, event_days, m).items()
                                 if k in ("n_changepoints", "event_hit_rate", "false_alarm_rate", "p_value",
                                          "null_mean_hit_rate")} for m in (0.5, 2.0)}
    market = [k for k in results if k.startswith("x402_")]
    out = {
        "method": "PELT, L2 cost on log1p weekly series, pen = 2*sigma^2*ln(n) (ADR 0005); tolerance +/-7 days",
        "n_events_total": int(len(groups)),
        "events": [{"date": str(r.date.date()), "titles": r.titles, "sources": r.sources} for r in groups.itertuples()],
        "headline_series": MAIN,
        "headline": {k: results[MAIN][k] for k in ("n_events", "n_changepoints", "event_hit_rate", "false_alarm_rate",
                                                   "null_mean_hit_rate", "p_value", "baseline_zscore")},
        "sensitivity_headline": sensitivity,
        "market_series_mean": {
            k: round(float(np.mean([results[s][k] for s in market])), 4)
            for k in ("event_hit_rate", "false_alarm_rate", "null_mean_hit_rate")},
        "series": results,
    }
    (OUT / "changepoints.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    for name, r in results.items():
        print(f"  {name:<36} weeks={r['weeks']:3d} cps={r['n_changepoints']:2d} hit={r['event_hit_rate']:.2f} "
              f"(null {r['null_mean_hit_rate']:.2f}, p={r['p_value']:.3f}) FA={r['false_alarm_rate']:.2f} | "
              f"z: hit={r['baseline_zscore']['event_hit_rate']:.2f} FA={r['baseline_zscore']['false_alarm_rate']:.2f}")
    return out
