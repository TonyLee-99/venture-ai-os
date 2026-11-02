"""F11: PELT finds planted shifts, the event matching is correct, and the committed validation recomputes."""

import json

import numpy as np
import pandas as pd

from vaios.config import RESULTS
from vaios.monitoring import changepoint as cp
from vaios.monitoring import run as mon

CPS = json.loads((RESULTS / "monitoring" / "changepoints.json").read_text())


def test_pelt_recovers_planted_shifts():
    rng = np.random.default_rng(0)
    y = np.concatenate([rng.normal(2, 0.1, 20), rng.normal(4, 0.1, 20), rng.normal(3, 0.1, 20)])
    found = mon.weekly_pelt(y)
    assert any(abs(f - 20) <= 1 for f in found) and any(abs(f - 40) <= 1 for f in found)
    assert len(found) <= 3  # the BIC-style penalty can add one short spurious regime on pure noise


def test_match_hit_and_false_alarm():
    d = pd.Timestamp
    m = cp.match([d("2025-01-06"), d("2025-03-03")], [d("2025-01-10"), d("2025-06-01")])
    assert m["event_hit_rate"] == 0.5 and m["false_alarm_rate"] == 0.5


def test_committed_validation_recomputes_offline():
    groups = mon.ev_mod.grouped(mon.ev_mod.load())
    series = mon.build_series()
    r = mon.evaluate(series[mon.MAIN], list(groups["date"]))
    h = CPS["headline"]
    for k in ("n_events", "n_changepoints", "event_hit_rate", "false_alarm_rate", "p_value"):
        assert r[k] == h[k], k


def test_events_follow_the_preregistered_sources():
    ev = mon.ev_mod.load()
    assert set(ev["source"]) <= {"x402_foundation_feed", "curated_verified", "hn"}
    assert ev["doc_id"].str.startswith("d_").all()
