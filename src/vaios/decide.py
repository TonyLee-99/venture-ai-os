"""Human-in-the-loop tooling. A human records decisions; nothing here ever writes a verdict by itself.

  uv run python -m vaios.decide status
  uv run python -m vaios.decide record <entity> --verdict watch --reason "..." --reviewer tony
  uv run python -m vaios.decide flags                      # write the flag-adjudication sample (blank labels)
  uv run python -m vaios.decide label <entity>:<claim_id> --label entails|partial|contradicts --reviewer tony
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import date

from vaios.agents.schemas import HumanDecision
from vaios.config import RESULTS, ROOT

LEDGER = ROOT / "ledger" / "human_feedback.jsonl"
FLAG_LEDGER = ROOT / "ledger" / "flag_adjudication.jsonl"
SAMPLE = RESULTS / "adjudication" / "flag_sample.csv"


def _rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []


def memos() -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((RESULTS / "memos").glob("*.json"))]


def status() -> dict:
    decided = {r["entity"]: r for r in _rows(LEDGER) if not r.get("example")}
    cards = [m for m in memos() if m["disagreements"]]
    # every memo, not only decision cards, gets a human verdict: agreement is measured on all of them
    agree_drafter = sum(decided[m["entity"]]["decision"] == m["memo"]["recommendation"] for m in memos() if m["entity"] in decided)
    agree_critic = sum(decided[m["entity"]]["decision"] == m["critique"]["recommendation"] for m in memos() if m["entity"] in decided)
    labelled = {r["claim"] for r in _rows(FLAG_LEDGER)}
    sample = list(csv.DictReader(SAMPLE.open())) if SAMPLE.exists() else []
    all_m = memos()
    out = {"decision_cards": len(cards), "memos_awaiting_human_verdict": sum(m["entity"] not in decided for m in all_m),
           "human_decisions_recorded": sum(m["entity"] in decided for m in all_m),
           "human_agrees_with_drafter": agree_drafter, "human_agrees_with_critic": agree_critic,
           "flag_sample_size": len(sample), "flag_sample_labelled": sum(f"{r['entity']}:{r['claim_id']}" in labelled for r in sample)}
    print(json.dumps(out, indent=1))
    return out


def record(entity: str, verdict: str, reason: str, reviewer: str) -> None:
    m = next(x for x in memos() if x["entity"] == entity)
    from vaios.dakr.artifacts import latest

    row = HumanDecision(date=str(date.today()), entity=entity, memo_version=latest("memo", entity)[0],
                        decision=verdict, agreed_with=("both" if verdict == m["memo"]["recommendation"] == m["critique"]["recommendation"]
                                                       else "drafter" if verdict == m["memo"]["recommendation"]
                                                       else "critic" if verdict == m["critique"]["recommendation"] else "neither"),
                        reviewer=reviewer, reason=reason, example=False)
    with LEDGER.open("a") as f:
        f.write(row.model_dump_json() + "\n")
    print(f"recorded {entity}: {verdict}")


def write_flag_sample(n: int = 30, seed: int = 1) -> int:
    """Stratified sample of claims for HUMAN labelling: critic-withheld, critic-partial and critic-entailed."""
    rows = []
    for m in memos():
        for w in m["withheld_by_critic"]:
            rows.append((m, w["claim"], w["critic_label"], w["reason"]))
        for c in m["memo"]["claims"]:
            rows.append((m, c, c.get("support"), c.get("support_note", "")))
    rng = random.Random(seed)
    by = {}
    for r in rows:
        by.setdefault(r[2], []).append(r)
    pick = []
    for _label, group in sorted(by.items(), key=lambda kv: str(kv[0])):
        pick += rng.sample(group, min(len(group), max(1, n // len(by))))
    SAMPLE.parent.mkdir(parents=True, exist_ok=True)
    with SAMPLE.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity", "claim_id", "claim_text", "quote_or_metric", "critic_label", "critic_reason",
                    "human_label", "human_note"])
        for m, c, lab, why in pick:
            receipt = c.get("quote") or f"{c.get('metric')} = {c.get('value')}"
            w.writerow([m["entity"], c["id"], c["text"], receipt, lab, why, "", ""])
    print(f"wrote {len(pick)} rows to {SAMPLE.relative_to(ROOT)} (human_label left blank on purpose)")
    return len(pick)


def label(claim: str, lab: str, reviewer: str, note: str) -> None:
    with FLAG_LEDGER.open("a") as f:
        f.write(json.dumps({"date": str(date.today()), "claim": claim, "label": lab, "reviewer": reviewer,
                            "note": note}) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser(prog="vaios.decide")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    r = sub.add_parser("record")
    r.add_argument("entity")
    r.add_argument("--verdict", choices=["advance", "watch", "pass"], required=True)
    r.add_argument("--reason", required=True)
    r.add_argument("--reviewer", required=True)
    sub.add_parser("flags")
    lb = sub.add_parser("label")
    lb.add_argument("claim", help="entity:claim_id")
    lb.add_argument("--label", choices=["entails", "partial", "contradicts"], required=True)
    lb.add_argument("--reviewer", required=True)
    lb.add_argument("--note", default="")
    a = ap.parse_args()
    if a.cmd == "status":
        status()
    elif a.cmd == "record":
        record(a.entity, a.verdict, a.reason, a.reviewer)
    elif a.cmd == "flags":
        write_flag_sample()
    else:
        label(a.claim, a.label, a.reviewer, a.note)


if __name__ == "__main__":
    main()
