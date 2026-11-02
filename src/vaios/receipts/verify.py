"""Receipt verifier: a claim ships only if its receipt checks out mechanically.

Checks per claim
1. source: the cited doc_id exists in the DAKR doc store;
2. span: the quote occurs in that snapshot (exact after normalisation, or fuzzy partial match >= 92 for
   quotes of 15+ chars, which tolerates markdown/whitespace/quote-style differences but not invented text);
3. numbers: a cited warehouse metric matches the facts sheet within 1%; every number written in the claim
   text (small integers included) must appear in the quote, equal the cited metric value, or equal a sibling
   fact of the same series, and it matches only at its own displayed precision ("56.6 million" covers
   56,580,000; "56.7 million" does not);
4. metric receipts must be stated: a claim citing a metric must contain that metric's value in its text, so
   a qualitative sentence cannot borrow credibility from an unrelated number.
It does NOT judge whether the quote logically supports the claim: the cross-family critic labels every claim
entails / partial / contradicts / unsupported, and only "entails" ships untagged (ADR 0006).
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
    return [n for n, _ in written_numbers(text)]


def written_numbers(text: str) -> list[tuple[float, float]]:
    """(value, half-unit of the last displayed digit): '56.6 million' -> (56_600_000, 50_000)."""
    out = []
    for raw, unit in _NUM.findall(text):
        digits = raw.replace(",", "")
        scale = _SCALE.get((unit or "").lower(), 1)
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        out.append((float(digits) * scale, 0.5 * 10 ** (-decimals) * scale))
    return out


def _close(a: float, b: float, rel: float = 0.01) -> bool:
    return abs(a - b) <= rel * max(abs(a), abs(b), 1e-9)


def _matches(written: tuple[float, float], candidate: float) -> bool:
    """A written number covers a source value only if the value rounds to it at the written precision."""
    n, half = written
    return abs(n - candidate) <= max(half, 1e-9 * max(abs(n), 1.0))


def _number_covered(written: tuple[float, float], quote_nums: list[float], metric_value: float | None,
                    context_nums: list[float]) -> bool:
    candidates = quote_nums + context_nums + ([metric_value] if metric_value is not None else [])
    return any(_matches(written, c) for c in candidates)


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
        if score < 100:  # fuzzy match tolerates typos, not different numbers or ids
            doc_nums = numbers_in(doc)
            if any(not any(_close(n, m, 1e-9) for m in doc_nums) for n in numbers_in(claim["quote"])):
                return ClaimCheck(cid, False, "quote_not_found", "fuzzy match but a number in the quote is not "
                                  "in the snapshot", score)
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
    text_nums = written_numbers(claim["text"])
    for w in text_nums:
        if not _number_covered(w, quote_nums, metric_value, context):
            return ClaimCheck(cid, False, "number_unsupported", f"{w[0]:g} not in quote or metric", score)
    if metric_value is not None and not any(_matches(w, metric_value) for w in text_nums):
        return ClaimCheck(cid, False, "metric_not_stated", f"cites {claim['metric']} but never states its value "
                          f"({metric_value:g})", score)
    return ClaimCheck(cid, True, "verified", "", score or 100.0)


def check_all(claims: list[dict], store: DocStore, facts: dict[str, float],
              descriptions: dict[str, str] | None = None) -> list[ClaimCheck]:
    return [check_claim(c, store, facts, descriptions) for c in claims]


def precision(checks: list[ClaimCheck]) -> float:
    return sum(c.ok for c in checks) / len(checks) if checks else float("nan")
