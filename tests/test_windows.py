"""Item 5 (round 2): "the 30 days to AS_OF" is [AS_OF - 30 days, AS_OF): exactly 30 daily rows, no later days."""

import duckdb
import pandas as pd

from vaios.agents.evidence import facilitator_shares, facilitator_window


def test_thirty_day_window_boundaries():
    days = pd.date_range("2026-09-25", "2026-11-02", freq="D")  # data runs past the as-of date, like the real pull
    df = pd.DataFrame({"day": days, "facilitator": "f", "txs": 1, "volume_usd": 1.0, "buyers": 1})
    con = duckdb.connect(":memory:")
    con.register("_d", df)
    con.execute("CREATE TABLE stg_x402_facilitator_daily AS SELECT * FROM _d")
    txs, vol, _ = facilitator_window(con, "f", "2026-11-01")
    assert txs == 30 and vol == 30.0  # Oct 2 .. Oct 31; Nov 1 and Nov 2 excluded
    assert facilitator_shares(con, "2026-11-01")["f"][2] == 30
