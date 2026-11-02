---
name: receipts
description: Citation rules every research agent follows so a machine can verify each factual claim.
version: 1
used_by: [diligence-memo, inflection-explainer, memo-critic]
---
# Receipts

Every factual claim is one JSON object with a receipt. A claim without a valid receipt is deleted before
the output ships, so an uncited claim is wasted work.

Two kinds of receipt (a claim may carry both):
1. **Snapshot quote**: `doc_id` of a provided source document plus `quote`, a span copied character for
   character from that document (10 to 300 characters). Do not paraphrase, translate, fix typos or join two
   separate sentences inside `quote`.
2. **Warehouse metric**: `metric` = a key from the provided FACTS sheet, `value` = its number exactly as given.

Rules
- Any number you write in `text` must appear in your `quote` or equal the cited metric `value`.
- Only cite documents and metric keys that were provided. Never invent a doc_id, URL or metric.
- Opinions, judgments and recommendations are not claims; put them in rationales, risks or questions.
- If the sources do not support something you believe, say it is unknown and add it to open questions.
