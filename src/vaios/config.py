"""Paths and the few fixed parameters every module shares."""

from __future__ import annotations

from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
WAREHOUSE = DATA / "warehouse.duckdb"
RESULTS = ROOT / "results"
FROZEN = RESULTS / "frozen"          # small point-in-time tables committed so offline tests can recompute
STORE = ROOT / "store"               # DAKR document store (committed snapshots that memos cite)
CASSETTES = ROOT / "cassettes"       # gateway cache = recorded LLM responses (committed)
SKILLS = ROOT / "skills"
JOBS = ROOT / "jobs"
SYNTHETIC = ROOT / "synthetic"

USER_AGENT = "venture-ai-os/0.1 (portfolio research project; github.com/TonyLee-99)"

# Walk-forward backtest origins. Each T0 has a 12-month outcome window that closes before today (2026-11-02).
BACKTEST_T0S = [date(2022, 7, 1), date(2023, 1, 1), date(2023, 7, 1), date(2024, 1, 1),
                date(2024, 7, 1), date(2025, 1, 1), date(2025, 7, 1)]
OUTCOME_MONTHS = 12

# LLM-judgment eval: features frozen at this date, outcomes counted only after the assumed model cutoff.
ASSUMED_MODEL_CUTOFF = date(2026, 6, 30)
LLM_EVAL_T0 = ASSUMED_MODEL_CUTOFF
LLM_EVAL_OUTCOME_END = date(2026, 11, 1)

# "As of now" for live screening/monitoring (data pulled 2026-11-02).
AS_OF = date(2026, 11, 1)

# Every as-of date the GitHub activity query computes windows for (backtest + llm eval + live).
ALL_ASOF = BACKTEST_T0S + [LLM_EVAL_T0, AS_OF]
