# 0006. What the receipts verifier proves, and what it does not

Status: accepted (2026-11-02).

## Decision
A claim ships only if a deterministic check passes: the cited snapshot exists in the content-addressed doc
store; the quote is found in it (exact after normalising case, whitespace, quote marks and markdown, or a fuzzy
partial match >= 92 for quotes of 15+ characters); a cited warehouse metric equals the facts sheet within 1%;
and every number in the claim text appears in the quote, equals the cited metric, or is part of that metric's
own definition (or a sibling field of the same series, e.g. a changepoint's before/after medians).
Snapshots are stored truncated to exactly what the model was shown, so a quote can only come from visible text.
Failing claims go back to the drafter once (fix the receipt or drop it); whatever still fails is withheld.

## What it does not prove
Span existence is not support: a real quote can be attached to an overreaching claim. That gap is measured,
not hidden: the cross-family critic flags claims whose quote does not support the text, and that count is
reported next to the verifier's precision. The verifier itself is tested against a gold set of real spans
(must accept all) and programmatic corruptions (fabricated quotes, wrong source, unknown doc, paraphrase,
inflated numbers, wrong metric values; must catch >= 95%).
