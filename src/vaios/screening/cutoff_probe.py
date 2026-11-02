"""Probe each model's knowledge cutoff instead of assuming it.

Each model gets the titles (no dates) of dated public events from results/monitoring/events.csv, which all have
stored source snapshots, and must give the year-month or "unknown". The latest correctly dated event is only a
LOWER bound on the cutoff: both models also missed some 2025 events, and answering "unknown" to niche 2026
events does not prove they are after the cutoff. So the post-cutoff window is ASSUMED, with supporting evidence
from this probe, not proven. Guessing from a title is possible; the full answer table is reported.
"""

from __future__ import annotations

import json

import pandas as pd
from pydantic import BaseModel

from vaios.config import RESULTS
from vaios.gateway import Gateway
from vaios.monitoring import events as ev_mod

OUT = RESULTS / "backtest" / "cutoff_probe.json"
SYSTEM = ("You are being tested on what you know from training data. Do not guess. For each event, give the "
          "year and month it happened as YYYY-MM if you actually know it, otherwise exactly 'unknown'.")


class ProbeAnswer(BaseModel):
    event_id: str
    month: str


class ProbeBatch(BaseModel):
    answers: list[ProbeAnswer]


def probe_events() -> pd.DataFrame:
    ev = ev_mod.load().drop_duplicates("title").sort_values("date").reset_index(drop=True)
    ev["event_id"] = [f"e{i:02d}" for i in range(len(ev))]
    return ev


def months_apart(a: str, b: pd.Timestamp) -> int | None:
    try:
        y, m = (int(x) for x in a.split("-")[:2])
    except ValueError:
        return None
    return abs((y * 12 + m) - (b.year * 12 + b.month))


def run(gw: Gateway) -> dict:
    ev = probe_events()
    listing = "\n".join(f"{r.event_id}: {r.title}" for r in ev.itertuples())
    prompt = (f"Events:\n{listing}\n\nReturn ONLY JSON: {{\"answers\": [{{\"event_id\": \"e00\", \"month\": "
              f"\"YYYY-MM or unknown\"}}, ...]}} with one answer per event.")
    models = {}
    for route in ("judge", "judge_alt"):
        res = gw.complete(route, SYSTEM, prompt, tag=f"cutoff_probe:{route}", schema=ProbeBatch)
        ans = {a["event_id"]: a["month"] for a in res.parsed["answers"]}
        rows, latest = [], None
        for r in ev.itertuples():
            gap = months_apart(ans.get(r.event_id, "unknown"), r.date)
            ok = gap is not None and gap <= 1
            rows.append({"event_id": r.event_id, "true_date": str(r.date.date()), "title": r.title,
                         "answer": ans.get(r.event_id, "unknown"), "correct": ok})
            if ok:
                latest = str(r.date.date())
        models[gw.routes[route][1]] = {"latest_correct_event": latest,
                                       "n_correct": sum(x["correct"] for x in rows),
                                       "n_unknown": sum(x["answer"] == "unknown" for x in rows), "answers": rows}
    out = {"method": " ".join(__doc__.split()), "n_events": int(len(ev)), "models": models}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    for m, v in models.items():
        print(f"  {m}: latest correctly dated event {v['latest_correct_event']}, correct {v['n_correct']}/{len(ev)}")
    return out


def load_or_run(gw: Gateway) -> dict:
    return run(gw)  # cached through the gateway, so re-running is free and replays offline
