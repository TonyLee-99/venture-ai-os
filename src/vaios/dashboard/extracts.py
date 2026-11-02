"""`make extracts`: Tableau-ready flat files (CSV, one grain per file), built from committed results.

See docs/tableau.md for the intended Tableau Public workbook. No .twb is shipped (it would be fake).
"""

from __future__ import annotations

import json

import pandas as pd

from vaios.config import FROZEN, RESULTS, ROOT

OUT = ROOT / "extracts"


def run() -> None:
    OUT.mkdir(exist_ok=True)
    bt = json.loads((RESULTS / "backtest" / "backtest.json").read_text())
    rows = [{"scorer": k, "label": v["label"], "leakage_exposed": v["leakage_exposed"], **p}
            for k, v in bt["scores"].items() for p in bt["per_t0"][k]]
    pd.DataFrame(rows).to_csv(OUT / "backtest_by_t0.csv", index=False)
    pd.read_csv(RESULTS / "backtest" / "scores_test.csv").to_csv(OUT / "backtest_scores_by_protocol.csv", index=False)

    x = pd.read_parquet(FROZEN / "x402_daily.parquet")
    x.to_csv(OUT / "x402_daily_by_chain.csv", index=False)
    pd.read_parquet(FROZEN / "x402_facilitator_daily.parquet").to_csv(OUT / "x402_daily_by_facilitator.csv", index=False)

    cp = json.loads((RESULTS / "monitoring" / "changepoints.json").read_text())
    segs = [{"series": s, **seg} for s, r in cp["series"].items() for seg in r["segments"]]
    pd.DataFrame(segs).to_csv(OUT / "changepoints.csv", index=False)
    pd.read_csv(RESULTS / "monitoring" / "events.csv").to_csv(OUT / "events.csv", index=False)

    pd.read_csv(RESULTS / "sourcing" / "candidates.csv").to_csv(OUT / "sourcing_candidates.csv", index=False)
    run_summary = json.loads((RESULTS / "sourcing" / "run_summary.json").read_text())
    memos = [{k: v for k, v in m.items() if not isinstance(v, dict | list)}
             | {f"drafter_{d}": m["scores_drafter"][d] for d in m["scores_drafter"]}
             | {f"critic_{d}": m["scores_critic"][d] for d in m["scores_critic"]} for m in run_summary["memos"]]
    pd.DataFrame(memos).to_csv(OUT / "memos.csv", index=False)
    print(f"extracts -> {sorted(p.name for p in OUT.glob('*.csv'))}")
