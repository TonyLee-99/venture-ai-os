"""F09: the receipts verifier accepts true spans, rejects corruptions, and every shipped memo claim verifies."""

import json
import random
import re

import pytest

from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.receipts.verify import check_claim, numbers_in

STORE = DocStore()
MEMOS = sorted((RESULTS / "memos").glob("*.json"))


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


@pytest.mark.skipif(len(STORE.index) < 5, reason="needs committed snapshots")
def test_verifier_catches_corruptions_and_accepts_gold():
    gold, corrupt = gold_and_corrupt()
    facts = {"m": 120.0}
    false_rejects = [g for g in gold if not check_claim(g, STORE, facts).ok]
    caught = [c for c in corrupt if not check_claim(c["claim"], STORE, facts).ok]
    assert len(gold) >= 50 and len(corrupt) >= 50
    assert not false_rejects, false_rejects[:3]
    assert len(caught) / len(corrupt) >= 0.95, [c["kind"] for c in corrupt if c not in caught][:10]


def test_number_rules():
    facts = {"gh.commits_90d": 556}
    ok = {"id": "a", "text": "556 commits in 90 days", "metric": "gh.commits_90d", "value": 556}
    bad = {"id": "b", "text": "5,560 commits in 90 days", "metric": "gh.commits_90d", "value": 556}
    assert check_claim(ok, STORE, facts).ok
    assert check_claim(bad, STORE, facts).status == "number_unsupported"


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_every_shipped_memo_claim_verifies_offline():
    for path in MEMOS:
        out = json.loads(path.read_text())
        desc = json.loads((RESULTS / "facts" / f"{out['entity']}.json").read_text())["descriptions"]
        for c in out["memo"]["claims"]:
            chk = check_claim(c, STORE, out["facts"], desc)
            assert chk.ok, (path.name, c["id"], chk.status, chk.detail)


@pytest.mark.skipif(not MEMOS, reason="no memos yet")
def test_run_summary_matches_memos():
    s = json.loads((RESULTS / "sourcing" / "run_summary.json").read_text())
    outs = [json.loads(p.read_text()) for p in MEMOS]
    assert s["n_memos"] == len(outs)
    assert s["claims_shipped"] == sum(len(o["memo"]["claims"]) for o in outs)
    assert s["claims_withheld"] == sum(len(o["unverified"]) for o in outs)


def test_snapshot_integrity():
    assert STORE.integrity_errors() == []
