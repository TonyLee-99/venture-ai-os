"""`make llm-eval`: does LLM screening judgment add anything, measured only where it cannot have seen the answer?

Leakage handling
- Features are frozen at T0 = 2026-06-30 (the assumed knowledge cutoff of both models, config.py), and the
  outcome is a raise announced after that date (to 2026-11-01). A model cannot have memorised these raises
  unless its true cutoff is later than assumed; that residual risk is stated in the README.
- Arm "anonymized": no name, no description, only point-in-time features -> no memorisation channel at all.
- Arm "named": name, category and today's DefiLlama description added. The description is a CURRENT snapshot
  that can mention post-T0 news, so this arm is flagged leakage-exposed; we also count descriptions of
  positives that mention funding.
The deterministic scores are evaluated on exactly the same items.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from vaios.agents import schemas, skills
from vaios.agents.runner import Trace
from vaios.config import (
    ASSUMED_MODEL_CUTOFF,
    BACKTEST_T0S,
    FROZEN,
    LLM_EVAL_OUTCOME_END,
    LLM_EVAL_T0,
    RESULTS,
)
from vaios.gateway import Gateway
from vaios.screening import score as sc
from vaios.screening.metrics import auc, precision_at_k

OUT = RESULTS / "backtest" / "llm_judgment.json"
SAMPLE_SIZE = 120
BATCH = 30
FEATURES = ["commits_90d", "commit_growth", "commits_before", "n_repos", "gh_age_days", "tvl_t0", "tvl_growth_90d",
            "listing_age_days", "prior_raises", "days_since_last_raise"]
FUNDING_WORDS = r"rais|fund|backed|investor|seed|series a"


def item_id(slug: str) -> str:
    return "p" + hashlib.sha256(slug.encode()).hexdigest()[:8]  # opaque id: the anonymized arm never sees names


def sample() -> pd.DataFrame:
    df = pd.read_parquet(FROZEN / "backtest_table.parquet")
    df = df[df["t0"].dt.date == LLM_EVAL_T0].copy()
    df["raised"] = df["raised"].astype(int)
    pos, neg = df[df["raised"] == 1], df[df["raised"] == 0]
    neg = neg.assign(h=neg["slug"].map(item_id)).sort_values("h").head(SAMPLE_SIZE - len(pos))  # seeded by hash
    s = pd.concat([pos, neg.drop(columns="h")]).assign(item_id=lambda d: d["slug"].map(item_id))
    return s.sort_values("item_id").reset_index(drop=True)


def describe(r, named: bool, descriptions: dict) -> dict:
    d = {"item_id": r.item_id}
    if named:
        d |= {"name": r.name, "category": r.category, "description": (descriptions.get(r.slug) or "")[:300]}
    for f in FEATURES:
        v = getattr(r, f)
        d[f] = None if pd.isna(v) else (round(float(v), 3) if isinstance(v, float) else int(v))
    return d


def judge(gw: Gateway, route: str, items: list[dict], tag: str, trace: Trace) -> dict[str, int]:
    out = {}
    system = skills.system_prompt("screening-judgment")
    for i in range(0, len(items), BATCH):
        chunk = items[i:i + BATCH]
        prompt = (f"Features are measured as of {LLM_EVAL_T0}. Window: {LLM_EVAL_T0} to {LLM_EVAL_OUTCOME_END}.\n"
                  f"Items ({len(chunk)}):\n" + "\n".join(json.dumps(x) for x in chunk) +
                  f"\n\nOutput JSON schema:\n{skills.schema_hint(schemas.JudgmentBatch)}")
        res = gw.complete(route, system, prompt, tag=f"{tag}:{i // BATCH}", schema=schemas.JudgmentBatch)
        trace.llm(f"{tag}_batch{i // BATCH}", res, prompt)
        out |= {x["item_id"]: x["probability"] for x in res.parsed["items"]}
    return out


def boot_auc(y: np.ndarray, s: np.ndarray, n: int = 2000, seed: int = 3) -> list[float]:
    rng = np.random.default_rng(seed)
    vals = [auc(y[idx], s[idx]) for idx in (rng.integers(0, len(y), len(y)) for _ in range(n))]
    return [round(float(x), 4) for x in np.nanpercentile(vals, [2.5, 97.5])]


def run() -> dict:
    gw = Gateway()
    s = sample()
    import duckdb

    from vaios.config import WAREHOUSE
    descriptions = {}
    desc_file = RESULTS / "backtest" / "llm_eval_descriptions.json"
    if WAREHOUSE.exists():  # snapshot the descriptions the named arm sees, so replay is offline
        con = duckdb.connect(str(WAREHOUSE), read_only=True)
        rows = con.execute("SELECT slug, description FROM stg_protocols").fetchall()
        descriptions = {k: v for k, v in rows if k in set(s["slug"])}
        desc_file.write_text(json.dumps(dict(sorted(descriptions.items())), indent=1) + "\n")
    else:
        descriptions = json.loads(desc_file.read_text())

    full = pd.read_parquet(FROZEN / "backtest_table.parquet")
    train = full[full["t0"].dt.date.isin(BACKTEST_T0S) & (full["outcome_end"].dt.date <= LLM_EVAL_T0)]
    train = train.assign(raised=train["raised"].astype(int))
    det = {
        "logit_full": sc.predict(sc.fit_logit(train, sc.FULL_FEATURES), s, sc.FULL_FEATURES),
        "logit_github": sc.predict(sc.fit_logit(train, sc.GITHUB_FEATURES), s, sc.GITHUB_FEATURES),
        "prior_funding": ((s["prior_raises"] > 0) + 1 / (1 + s["days_since_last_raise"].fillna(1e6) / 365)).to_numpy(),
    }
    trace = Trace("llm_judgment_eval", "t0_" + str(LLM_EVAL_T0), {"items": list(s["item_id"])}, as_of=str(LLM_EVAL_T0))
    arms = {}
    for arm, named in (("anonymized", False), ("named", True)):
        items = [describe(r, named, descriptions) for r in s.itertuples()]
        for route in ("judge", "judge_alt"):
            probs = judge(gw, route, items, f"{arm}:{route}", trace)
            arms[f"{arm}|{gw.routes[route][1]}"] = np.array([probs.get(i, np.nan) for i in s["item_id"]], float)
    y = s["raised"].to_numpy(int)
    results = {}
    for name, score in {**{f"deterministic|{k}": v for k, v in det.items()}, **arms}.items():
        ok = ~np.isnan(score)
        results[name] = {"auc": round(auc(y[ok], score[ok]), 4), "auc_ci95": boot_auc(y[ok], score[ok]),
                         "p@10": precision_at_k(y[ok], score[ok], 10), "missing": int((~ok).sum()),
                         "leakage_exposed": name.startswith("named")}
    pos_desc = [descriptions.get(sl, "") or "" for sl in s.loc[s["raised"] == 1, "slug"]]
    out = {
        "t0": str(LLM_EVAL_T0), "outcome_window_end": str(LLM_EVAL_OUTCOME_END),
        "assumed_model_cutoff": str(ASSUMED_MODEL_CUTOFF),
        "all_outcomes_after_cutoff": True,
        "n_items": int(len(s)), "n_positives": int(y.sum()),
        "positives_with_funding_words_in_current_description": int(pd.Series(pos_desc).str.contains(
            FUNDING_WORDS, case=False, regex=True).sum()),
        "results": results,
        "note": "Tiny positive count: CIs are wide; read as a sanity check of the harness, not a verdict.",
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    trace.save("ok", {"results": "results/backtest/llm_judgment.json"})
    print(json.dumps({k: (v["auc"], v["auc_ci95"]) for k, v in results.items()}, indent=1))
    print(f"  gateway this run: {gw.session_calls}")
    return out
