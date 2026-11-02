"""`make llm-eval`: does LLM screening judgment add anything, measured where it cannot have seen the answer?

Two evaluation sets (ADR 0007)
1. Walk-forward set, ANONYMIZED only: all 80 positive rows of the backtest test T0s plus a hash-seeded random
   sample of 320 negative rows (case-control: AUC is unaffected by sampling within class; precision and
   probabilities are not deployment-prevalence numbers). Items carry an opaque id and point-in-time features
   only, so there is no memorisation channel even though the T0s predate the model cutoffs.
2. Post-cutoff set: features at T0 = 2026-06-30, outcomes to 2026-11-01 (a 4-month, right-censored window),
   anonymized arm plus a "named" arm (name, category, today's DefiLlama description). Whether the window is
   really after each model's knowledge is PROBED (cutoff_probe.json), not assumed.
Deterministic scores are evaluated on exactly the same items. Bootstraps resample within class, so no resample
is ever dropped for lacking positives.
"""

from __future__ import annotations

import hashlib
import json
import re

import numpy as np
import pandas as pd

from vaios.agents import schemas, skills
from vaios.agents.runner import Trace
from vaios.config import BACKTEST_T0S, FROZEN, LLM_EVAL_OUTCOME_END, LLM_EVAL_T0, RESULTS
from vaios.gateway import Gateway
from vaios.screening import backtest
from vaios.screening import score as sc
from vaios.screening.metrics import auc, precision_at_k

OUT = RESULTS / "backtest" / "llm_judgment.json"
DESC_FILE = RESULTS / "backtest" / "llm_eval_descriptions.json"
SAMPLE_SIZE = 120
WF_NEGATIVES = 320
BATCH = 30
WF_BATCH = 40
FEATURES = ["commits_90d", "commit_growth", "commits_before", "n_repos", "gh_age_days", "tvl_t0", "tvl_growth_90d",
            "listing_age_days", "prior_raises", "days_since_last_raise"]
# A description "mentions a raise" only with explicit fundraising language. Round 1 matched "fund" (money-market
# funds); the round-1 fix still matched "backed by" alone ("backed by the first DAO", "backed by institutional-grade
# security"). Now "backed by" counts only when an investor-type word follows within 40 characters.
INVESTOR = r"(ventures|capital|labs|vc|investors|partners|a16z|paradigm|sequoia|polychain|pantera|multicoin)"
RAISE_RULE = re.compile(r"\braised\s+\$|\braises\s+\$|\bfunding round\b|\b(pre-)?seed round\b|"
                        r"\bseries [a-d] (round|funding)\b|\bbacked by\b[^.]{0,40}\b" + INVESTOR + r"\b|"
                        r"\bled by\b[^.]{0,40}\b" + INVESTOR + r"\b|\bstrategic (round|investment)\b", re.I)
DESC_CHARS_SHOWN = 300  # the named arm sees description[:300]; leakage is counted only inside that text


def item_id(key: str) -> str:
    return "p" + hashlib.sha256(key.encode()).hexdigest()[:8]  # opaque id: the anonymized arm never sees names


def features_of(r) -> dict:
    d = {}
    for f in FEATURES:
        v = getattr(r, f)
        d[f] = None if pd.isna(v) else (round(float(v), 3) if isinstance(v, float) else int(v))
    return d


def judge(gw: Gateway, route: str, items: list[dict], header: str, tag: str, trace: Trace, batch: int) -> dict:
    out = {}
    system = skills.system_prompt("screening-judgment")
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        prompt = (f"{header}\nItems ({len(chunk)}):\n" + "\n".join(json.dumps(x) for x in chunk) +
                  f"\n\nOutput JSON schema:\n{skills.schema_hint(schemas.JudgmentBatch)}")
        res = gw.complete(route, system, prompt, tag=f"{tag}:{i // batch}", schema=schemas.JudgmentBatch)
        trace.llm(f"{tag}_batch{i // batch}", res, prompt)
        out |= {x["item_id"]: x["probability"] for x in res.parsed["items"]}
    return out


def strat_boot_auc(y: np.ndarray, s: np.ndarray, n: int = 2000, seed: int = 3) -> list[float]:
    """Bootstrap that resamples positives and negatives separately: every resample has both classes."""
    rng = np.random.default_rng(seed)
    pos, neg = np.where(y == 1)[0], np.where(y == 0)[0]
    vals = []
    for _ in range(n):
        idx = np.concatenate([rng.choice(pos, len(pos)), rng.choice(neg, len(neg))])
        vals.append(auc(y[idx], s[idx]))
    return [round(float(x), 4) for x in np.percentile(vals, [2.5, 97.5])]


def summarize(y: np.ndarray, scores: dict[str, np.ndarray], leaky: set[str]) -> dict:
    out = {}
    for name, score in scores.items():
        ok = ~np.isnan(score)
        out[name] = {"auc": round(auc(y[ok], score[ok]), 4), "auc_ci95": strat_boot_auc(y[ok], score[ok]),
                     "p@10": precision_at_k(y[ok], score[ok], 10), "missing": int((~ok).sum()),
                     "leakage_exposed": name in leaky}
    return out


# ---------- set 1: walk-forward, anonymized ----------
def walk_forward_sample() -> pd.DataFrame:
    df, test_t0s, _ = backtest.add_scores(backtest.load())
    test = df[df["t0"].isin(test_t0s)].copy()
    test["key"] = test["slug"] + "|" + test["t0"].dt.date.astype(str)
    test["item_id"] = test["key"].map(item_id)
    pos = test[test["raised"] == 1]
    neg = test[test["raised"] == 0].sort_values("item_id").head(WF_NEGATIVES)
    return pd.concat([pos, neg]).sort_values("item_id").reset_index(drop=True)


def run_walk_forward(gw: Gateway, trace: Trace) -> dict:
    s = walk_forward_sample()
    items = [{"item_id": r.item_id, "as_of": str(r.t0.date()), "window_months": 12, **features_of(r)}
             for r in s.itertuples()]
    header = "Each item has its own as_of date; the window is the 12 months after that date."
    y = s["raised"].to_numpy(int)
    scores = {f"deterministic|{c}": s[c].to_numpy(float) for c in ("s_logit_full", "s_heuristic", "b_prior_funding",
                                                                   "b_newest")}
    for route in ("judge", "judge_alt"):
        probs = judge(gw, route, items, header, f"wf_anonymized:{route}", trace, WF_BATCH)
        scores[f"anonymized|{gw.routes[route][1]}"] = np.array([probs.get(i, np.nan) for i in s["item_id"]], float)
    never = (s["prior_raises"] == 0).to_numpy()
    return {"n_items": int(len(s)), "n_positives": int(y.sum()), "n_negatives_sampled": int((y == 0).sum()),
            "sampling": "case-control: all positive rows + hash-seeded random negatives from the walk-forward test set",
            "all": summarize(y, scores, set()),
            "never_raised": {"n_items": int(never.sum()), "n_positives": int(y[never].sum()),
                             **summarize(y[never], {k: v[never] for k, v in scores.items()}, set())}}


# ---------- set 2: post-cutoff ----------
def post_cutoff_sample() -> pd.DataFrame:
    df = pd.read_parquet(FROZEN / "backtest_table.parquet")
    df = df[df["t0"].dt.date == LLM_EVAL_T0].copy()
    df["raised"] = df["raised"].astype(int)
    pos, neg = df[df["raised"] == 1], df[df["raised"] == 0]
    neg = neg.assign(h=neg["slug"].map(item_id)).sort_values("h").head(SAMPLE_SIZE - len(pos))
    s = pd.concat([pos, neg.drop(columns="h")]).assign(item_id=lambda d: d["slug"].map(item_id))
    return s.sort_values("item_id").reset_index(drop=True)


def load_descriptions(slugs: set[str]) -> dict:
    from vaios.config import WAREHOUSE

    if WAREHOUSE.exists():  # snapshot the descriptions the named arm sees, so replay is offline
        import duckdb

        con = duckdb.connect(str(WAREHOUSE), read_only=True)
        rows = con.execute("SELECT slug, description FROM stg_protocols").fetchall()
        d = {k: v for k, v in rows if k in slugs}
        DESC_FILE.write_text(json.dumps(dict(sorted(d.items())), indent=1) + "\n")
        return d
    return json.loads(DESC_FILE.read_text())


def run_post_cutoff(gw: Gateway, trace: Trace, probe: dict) -> dict:
    s = post_cutoff_sample()
    desc = load_descriptions(set(s["slug"]))
    full = pd.read_parquet(FROZEN / "backtest_table.parquet")
    train = full[full["t0"].dt.date.isin(BACKTEST_T0S) & (full["outcome_end"].dt.date <= LLM_EVAL_T0)]
    train = train.assign(raised=train["raised"].astype(int))
    scores = {
        "deterministic|logit_full": sc.predict(sc.fit_logit(train, sc.FULL_FEATURES), s, sc.FULL_FEATURES),
        "deterministic|logit_github": sc.predict(sc.fit_logit(train, sc.GITHUB_FEATURES), s, sc.GITHUB_FEATURES),
        "deterministic|prior_funding": ((s["prior_raises"] > 0) + 1 / (1 + s["days_since_last_raise"].fillna(1e6) / 365)).to_numpy(),
    }
    header = f"Features are measured as of {LLM_EVAL_T0}. Window: {LLM_EVAL_T0} to {LLM_EVAL_OUTCOME_END}."
    for arm, named in (("anonymized", False), ("named", True)):
        items = []
        for r in s.itertuples():
            d = {"item_id": r.item_id}
            if named:
                d |= {"name": r.name, "category": r.category, "description": (desc.get(r.slug) or "")[:DESC_CHARS_SHOWN]}
            items.append(d | features_of(r))
        for route in ("judge", "judge_alt"):
            probs = judge(gw, route, items, header, f"{arm}:{route}", trace, BATCH)
            scores[f"{arm}|{gw.routes[route][1]}"] = np.array([probs.get(i, np.nan) for i in s["item_id"]], float)
    y = s["raised"].to_numpy(int)
    shown = s["slug"].map(lambda sl: (desc.get(sl) or "")[:DESC_CHARS_SHOWN])
    mention = shown.map(lambda t: bool(RAISE_RULE.search(t)))
    mention_full = s["slug"].map(lambda sl: bool(RAISE_RULE.search(desc.get(sl) or "")))
    window_start = str(LLM_EVAL_T0)
    after = {m: (v["latest_correct_event"] or "0000") < window_start for m, v in probe["models"].items()}
    return {
        "t0": str(LLM_EVAL_T0), "outcome_window_end": str(LLM_EVAL_OUTCOME_END),
        "window": "4 months, right-censored: raises announced after 2026-11-01 count as negatives",
        "n_items": int(len(s)), "n_positives": int(y.sum()),
        "sampling": "case-control: all positives + hash-seeded random negatives",
        "probed_knowledge_ends_before_window": after,
        "post_cutoff_status": "assumed, with supporting evidence: the latest correctly dated event is a lower bound "
                              "on each model's cutoff (cutoff_probe.json); not proven",
        "missing_predictions_reported_per_scorer": True,
        "raise_mentions_in_current_description": {
            "rule": RAISE_RULE.pattern,
            "counted_within": f"the first {DESC_CHARS_SHOWN} characters (what the named arm saw)",
            "positives": int(mention[s["raised"] == 1].sum()), "positives_total": int(y.sum()),
            "negatives": int(mention[s["raised"] == 0].sum()), "negatives_total": int((y == 0).sum()),
            "positives_full_description": int(mention_full[s["raised"] == 1].sum()),
            "negatives_full_description": int(mention_full[s["raised"] == 0].sum()),
            "matched_descriptions": {sl: (desc.get(sl) or "")[:400] for sl in s.loc[mention_full, "slug"]},
        },
        "results": summarize(y, scores, {k for k in scores if k.startswith("named")}),
    }


def run() -> dict:
    from vaios.screening.cutoff_probe import load_or_run

    gw = Gateway()
    probe = load_or_run(gw)
    trace = Trace("llm_judgment_eval", "all_sets", {"wf_negatives": WF_NEGATIVES, "post_cutoff_t0": str(LLM_EVAL_T0)},
                  as_of=str(LLM_EVAL_T0))
    wf = run_walk_forward(gw, trace)
    pc = run_post_cutoff(gw, trace, probe)
    out = {"walk_forward_anonymized": wf, "post_cutoff": pc, "cutoff_probe": "results/backtest/cutoff_probe.json",
           "note": "Post-cutoff set has 8 positives: CIs are wide; read it as a harness check, not a verdict."}
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    trace.save("ok", {"results": "results/backtest/llm_judgment.json"})
    print(json.dumps({k: (v["auc"], v["auc_ci95"]) for k, v in wf["all"].items()}, indent=1))
    print(json.dumps({k: (v["auc"], v["auc_ci95"]) for k, v in pc["results"].items()}, indent=1))
    print("raise mentions:", {k: v for k, v in pc["raise_mentions_in_current_description"].items() if k != "matched_descriptions"})
    print(f"  gateway this run: {gw.session_calls}")
    return out
