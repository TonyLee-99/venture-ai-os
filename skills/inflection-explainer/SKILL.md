---
name: inflection-explainer
description: Explain detected changepoints in traction series for a weekly post-investment brief, with receipts, without inventing causes.
version: 1
includes: [receipts]
output_schema: vaios.agents.schemas.WeeklyBrief
route: draft
---
# Weekly monitoring brief: explain inflections

You get detected changepoints (series, date, level before/after) and, for each, candidate evidence: dated
public events and Hacker News stories within +/- 14 days, each as a source document with a doc_id, plus a
FACTS sheet with the numbers.

For each inflection write a one-line headline and 1 to 3 claims with receipts: the size of the shift (cite
the metric) and the dated public event that coincides with it (cite the document) if there is one.
Coincidence is not cause: say "coincides with", never "caused by", unless a source says so.
If nothing in the evidence explains a shift, say so and set confidence to low. Those are the ones a human
should look at.

`summary`: 3 sentences for a partner. `watchlist`: series to re-check next week and why.
Return ONLY one JSON object matching the schema shown in the prompt.
