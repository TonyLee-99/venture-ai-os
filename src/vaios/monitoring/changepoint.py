"""Changepoint detection on traction series and its validation against dated public events.

Detector: PELT (ruptures) with an L2 (mean-shift) cost on log1p of the daily series. The penalty is fixed in
advance (ADR 0005), never tuned on the events: pen = 2 * sigma^2 * ln(n), with sigma estimated robustly from
first differences (MAD / 0.6745 / sqrt 2), the usual BIC-style choice for a mean-shift model.
Baseline detector: a trailing 28-day z-score of daily log changes, |z| > 3, 7-day refractory period.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import ruptures as rpt

MIN_SIZE = 7          # a regime must last at least a week
TOLERANCE_DAYS = 7    # an event "explains" a changepoint within +/- 7 days


def robust_sigma(y: np.ndarray) -> float:
    d = np.diff(y)
    mad = np.median(np.abs(d - np.median(d)))
    return float(mad / 0.6745 / np.sqrt(2)) or float(np.std(d)) or 1.0


def pelt(y: np.ndarray, pen_mult: float = 1.0) -> list[int]:
    """Indices where a new regime starts (excluding 0 and len(y))."""
    sigma = robust_sigma(y)
    pen = pen_mult * 2 * sigma**2 * np.log(len(y))
    bkps = rpt.Pelt(model="l2", min_size=MIN_SIZE, jump=1).fit(y.reshape(-1, 1)).predict(pen=pen)
    return [b for b in bkps if b < len(y)]


def zscore_detector(y: np.ndarray, window: int = 28, thresh: float = 3.0, refractory: int = 7) -> list[int]:
    d = pd.Series(np.diff(y, prepend=y[0]))
    mu = d.rolling(window, min_periods=window // 2).mean().shift(1)
    sd = d.rolling(window, min_periods=window // 2).std().shift(1)
    z = ((d - mu) / sd).to_numpy()
    out, last = [], -10**9
    for i, v in enumerate(z):
        if np.isfinite(v) and abs(v) > thresh and i - last >= refractory:
            out.append(i)
            last = i
    return out


def match(cp_days: list[pd.Timestamp], event_days: list[pd.Timestamp], tol: int = TOLERANCE_DAYS) -> dict:
    """Event hit rate (events with a changepoint within tol) and false-alarm rate (changepoints with no event)."""
    hits = [e for e in event_days if any(abs((c - e).days) <= tol for c in cp_days)]
    false_alarms = [c for c in cp_days if not any(abs((c - e).days) <= tol for e in event_days)]
    return {"n_events": len(event_days), "n_changepoints": len(cp_days),
            "event_hit_rate": len(hits) / len(event_days) if event_days else float("nan"),
            "false_alarm_rate": len(false_alarms) / len(cp_days) if cp_days else float("nan"),
            "hit_events": [str(e.date()) for e in hits]}


def permutation_p(n_days: int, n_cps: int, event_idx: list[int], observed_hit_rate: float, n_perm: int = 5000,
                  seed: int = 11, tol: int = TOLERANCE_DAYS) -> tuple[float, float]:
    """Null: the same number of changepoints placed uniformly at random. Returns (null mean hit rate, p-value)."""
    rng = np.random.default_rng(seed)
    ev = np.array(event_idx)
    if n_cps == 0 or len(ev) == 0:
        return float("nan"), float("nan")
    rates = np.empty(n_perm)
    for i in range(n_perm):
        cps = rng.choice(np.arange(MIN_SIZE, n_days - 1), size=n_cps, replace=False)
        rates[i] = np.mean([np.any(np.abs(cps - e) <= tol) for e in ev])
    return float(rates.mean()), float((np.sum(rates >= observed_hit_rate) + 1) / (n_perm + 1))


def segments(days: pd.DatetimeIndex, y_raw: np.ndarray, cps: list[int]) -> list[dict]:
    """Level before/after each changepoint (median of the raw series in the adjacent regimes)."""
    bounds = [0] + cps + [len(y_raw)]
    out = []
    for k, c in enumerate(cps):
        before = y_raw[bounds[k]:c]
        after = y_raw[c:bounds[k + 2]]
        b, a = float(np.median(before)), float(np.median(after))
        out.append({"date": str(days[c].date()), "median_before": round(b, 2), "median_after": round(a, 2),
                    "ratio": round(a / b, 3) if b > 0 else None,
                    "direction": "up" if a > b else "down"})
    return out
