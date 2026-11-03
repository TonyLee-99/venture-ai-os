"""Dashboard is built from committed results, screenshot exists, Tableau extracts + doc exist."""

import pandas as pd

from vaios.config import ROOT
from vaios.report import headline_numbers


def test_dashboard_shows_committed_numbers():
    page = (ROOT / "dashboard" / "index.html").read_text()
    n = headline_numbers()
    assert f"heuristic {float(n['auc_nr_heuristic']):.2f}" in page and f"AUC {float(n['auc_full']):.2f}" in page
    assert f"{n['cp_n']} changepoints, {n['cp_events']} events" in page
    assert "SYNTHETIC" in page and "pending" in page


def test_screenshot_and_extracts():
    assert (ROOT / "docs" / "img" / "dashboard.png").stat().st_size > 50_000
    assert (ROOT / "docs" / "tableau.md").exists()
    for f in ("backtest_by_t0.csv", "x402_daily_by_chain.csv", "changepoints.csv", "memos.csv",
              "sourcing_candidates.csv"):
        df = pd.read_csv(ROOT / "extracts" / f)
        assert len(df) > 0, f
