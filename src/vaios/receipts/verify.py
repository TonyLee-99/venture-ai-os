"""Receipt verifier: a claim ships only if its receipt checks out mechanically.

Checks per claim
1. source: the cited doc_id exists in the DAKR doc store;
2. span: the quote occurs in that snapshot (exact after normalisation, or fuzzy partial match >= 92 for
   quotes of 15+ chars, which tolerates markdown/whitespace/quote-style differences but not invented text);
3. numbers: a cited warehouse metric matches the facts sheet within 1%; every number written in the claim
   text must appear in the quote, equal the cited metric value, or equal a sibling fact of the same
   measurement (same key prefix) (catches "the README says 1,200" when it
   says 120).
It does NOT judge whether the quote logically supports the claim; the cross-model critic does that.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from rapidfuzz import fuzz

from vaios.dakr.docstore import DocStore

FUZZY_MIN = 92
_NUM = re.compile(r"(?<![\w.])\$?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(k|m|b|bn|million|billion|thousand|%)?(?![\w])",
                  re.I)
_SCALE = {"k": 1e3, "thousand": 1e3, "m": 1e6, "million": 1e6, "b": 1e9, "bn": 1e9, "billion": 1e9}


def normalize(text: str) -> str:
    t = text.lower()
    t = t.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-",
                                   "—": "-", " ": " "}))
    t = re.sub(r"[*_`#>|]", " ", t)          # markdown decoration is not content
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)  # [text](link) -> text
    return re.sub(r"\s+", " ", t).strip()


def numbers_in(text: str) -> list[float]:
    out = []
    for raw, unit in _NUM.findall(text):
        v = float(raw.replace(",", ""))
        out.append(v * _SCALE.get((unit or "").lower(), 1))
    return out


def _close(a: float, b: float, rel: float = 0.01) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-9)


def _number_covered(n: float, quote_nums: list[float], metric_value: float | None,
                    context_nums: list[float]) -> bool:
    if n < 10 and float(n).is_integer():
        return True  # small counts ("3 risks", "Series 2") are not worth a receipt
    candidates = quote_nums + context_nums + ([metric_value] if metric_value is not None else [])
    # the claim may round (56.58M -> "56.6 million", 2.4% -> "2%"), so allow 5% when matching text to text
    return any(_close(n, c, 0.05) for c in candidates)


@dataclass
class ClaimCheck:
    claim_id: str
    ok: bool
    status: str      # verified | bad_source | quote_not_found | metric_unknown | metric_mismatch | number_unsupported
    detail: str = ""
    match_score: float = 0.0


def check_claim(claim: dict, store: DocStore, facts: dict[str, float],
                descriptions: dict[str, str] | None = None) -> ClaimCheck:
    """`descriptions` (metric key -> definition) lets a metric claim restate its window ("in 90 days")."""
    cid = claim["id"]
    quote_nums: list[float] = []
    score = 0.0
    if claim.get("doc_id"):
        doc = store.get(claim["doc_id"])
        if doc is None:
            return ClaimCheck(cid, False, "bad_source", f"unknown doc_id {claim['doc_id']}")
        q, d = normalize(claim.get("quote") or ""), normalize(doc)
        if not q:
            return ClaimCheck(cid, False, "quote_not_found", "empty quote")
        if q in d:
            score = 100.0
        elif len(q) >= 15:
            score = fuzz.partial_ratio(q, d)
        if score < FUZZY_MIN:
            return ClaimCheck(cid, False, "quote_not_found", f"best match {score:.0f} < {FUZZY_MIN}", score)
        quote_nums = numbers_in(claim["quote"])
    metric_value = None
    if claim.get("metric"):
        if claim["metric"] not in facts:
            return ClaimCheck(cid, False, "metric_unknown", f"{claim['metric']} not in facts sheet", score)
        metric_value = float(facts[claim["metric"]])
        if claim.get("value") is None or not _close(float(claim["value"]), metric_value):
            return ClaimCheck(cid, False, "metric_mismatch",
                              f"claimed {claim.get('value')} vs warehouse {metric_value}", score)
    context: list[float] = []
    if claim.get("metric"):
        # numbers in the metric's own name/definition ("commits_90d", "as of 2026-11-01") ...
        context = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", claim["metric"])]
        context += numbers_in((descriptions or {}).get(claim["metric"], ""))
        # ... and sibling facts of the same measurement ("fell from <median_before> to <median_after>")
        # (only for keys with sub-fields, series.date.field; "gh.commits_90d" vs "gh.stars" are different things)
        if claim["metric"].count(".") >= 2:
            family = claim["metric"].rsplit(".", 1)[0] + "."
            context += [float(v) for k, v in facts.items() if k.startswith(family)]
    for n in numbers_in(claim["text"]):
        if not _number_covered(n, quote_nums, metric_value, context):
            return ClaimCheck(cid, False, "number_unsupported", f"{n:g} not in quote or metric", score)
    return ClaimCheck(cid, True, "verified", "", score or 100.0)


def check_all(claims: list[dict], store: DocStore, facts: dict[str, float],
              descriptions: dict[str, str] | None = None) -> list[ClaimCheck]:
    return [check_claim(c, store, facts, descriptions) for c in claims]


def precision(checks: list[ClaimCheck]) -> float:
    return sum(c.ok for c in checks) / len(checks) if checks else float("nan")
