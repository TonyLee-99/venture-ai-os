"""`make verifier-eval`: test the receipts verifier itself on a gold set of real spans (must accept) and
programmatic corruptions of the kind a hallucinating model produces (must reject). Deterministic (seeded)."""

from __future__ import annotations

import json
import random
import re
from collections import Counter

from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.receipts.verify import check_claim, numbers_in

STORE = DocStore()


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if 40 <= len(p.strip()) <= 200 and re.search(r"[a-zA-Z]{4}", p)]


def gold_and_corrupt(seed: int = 5, per_doc: int = 3):
    """Gold = real spans from committed snapshots. Corruptions = what a hallucinating model produces."""
    rng = random.Random(seed)
    docs = sorted(STORE.index)
    gold, corrupt = [], []
    for d in docs:
        sents = sentences(STORE.get(d))
        for s in rng.sample(sents, min(per_doc, len(sents))):
            gold.append({"id": "g", "text": "claim", "doc_id": d, "quote": s})
            # light formatting noise a correct citation may carry: case, spacing, curly quotes
            gold.append({"id": "g2", "text": "claim", "doc_id": d, "quote": "  " + s.upper().replace("'", "’")})
            other = rng.choice([x for x in docs if x != d])
            osents = sentences(STORE.get(other)) or ["nothing here at all to quote"]
            corrupt.append({"kind": "fabricated_quote", "claim": {"id": "c", "text": "claim", "doc_id": d,
                            "quote": "The company processes over 4 million agent payments every single day."}})
            o = rng.choice(osents)
            if o not in STORE.get(d):  # a quote from a different document, cited to this one
                corrupt.append({"kind": "wrong_source", "claim": {"id": "c", "text": "claim", "doc_id": d, "quote": o}})
            corrupt.append({"kind": "unknown_doc", "claim": {"id": "c", "text": "claim", "doc_id": "d_0000000000000000",
                                                             "quote": s}})
            words = s.split()
            if len(words) > 8:  # swap in invented words: a paraphrase is not a quote
                w = words[:]
                for i in rng.sample(range(len(w)), k=max(3, len(w) // 3)):
                    w[i] = rng.choice(["revolutionary", "billions", "dominant", "guaranteed", "exclusive"])
                corrupt.append({"kind": "paraphrase", "claim": {"id": "c", "text": "claim", "doc_id": d,
                                                                "quote": " ".join(w)}})
            nums = numbers_in(s)
            if nums:  # a claim that inflates a number its quote states
                corrupt.append({"kind": "inflated_number", "claim": {"id": "c", "doc_id": d, "quote": s,
                                "text": f"It reports {nums[0] * 3 + 17:,.0f} users."}})
    corrupt.append({"kind": "metric_mismatch", "claim": {"id": "c", "text": "Commits 999", "metric": "m", "value": 999}})
    corrupt.append({"kind": "metric_unknown", "claim": {"id": "c", "text": "x", "metric": "nope", "value": 1}})
    return gold, corrupt



def run() -> dict:
    gold, corrupt = gold_and_corrupt()
    facts = {"m": 120.0}
    false_rejects = sum(not check_claim(g, STORE, facts).ok for g in gold)
    missed = [c["kind"] for c in corrupt if check_claim(c["claim"], STORE, facts).ok]
    out = {"gold_spans": len(gold), "false_rejects": false_rejects, "corruptions": len(corrupt),
           "caught": len(corrupt) - len(missed), "catch_rate": round(1 - len(missed) / len(corrupt), 4),
           "by_kind": dict(Counter(c["kind"] for c in corrupt)), "missed_by_kind": dict(Counter(missed))}
    path = RESULTS / "receipts" / "verifier_eval.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out))
    return out
