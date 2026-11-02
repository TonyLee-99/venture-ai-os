"""`make claim-eval`: claim-level evaluation of the two support checks on REAL memo claims.

Gold pairs = verified claim/quote pairs from the committed memos. Perturbations of those pairs have labels
known by construction:
  swapped_number  -> contradicts   (a number in the claim changed)
  wrong_entity    -> contradicts   (the claim now names another company)
  wrong_date      -> contradicts   (a year in the claim shifted)
  added_qualifier -> partial       (an unsupported superlative appended)
Each pair goes through the deterministic verifier and through the cross-family critic (entailment label against
the quote). We report recall per perturbation type for each check and for both combined. Precision on the
unperturbed claims needs human labels: their flag rate is reported as an upper bound and a sample is exported
for the owner to label (python -m vaios.decide flags). Nothing here fabricates a human label.
"""

from __future__ import annotations

import hashlib
import json
import re

from vaios.agents import schemas
from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.gateway import Gateway
from vaios.receipts.verify import check_claim

OUT = RESULTS / "receipts" / "claim_eval.json"
MAX_ORIGINALS = 60
BATCH = 30
QUALIFIER = ", making it the clear market leader with proven paying customers"
SYSTEM = ("You check citations. For each pair, judge ONLY whether the quote supports the claim text: entails "
          "(fully supported), partial (part supported, part inference or embellishment), contradicts (quote says "
          "something different: number, entity, date or meaning) or unsupported (quote unrelated). Be strict.")


def originals() -> list[dict]:
    pairs = []
    for p in sorted((RESULTS / "memos").glob("*.json")):
        m = json.loads(p.read_text())
        others = [json.loads(q.read_text())["name"] for q in sorted((RESULTS / "memos").glob("*.json")) if q != p]
        for c in m["memo"]["claims"] + [w["claim"] for w in m["withheld_by_critic"]]:
            if c.get("doc_id") and c.get("quote"):
                pairs.append({"entity": m["entity"], "name": m["name"], "other": others[0] if others else "Acme",
                              "claim": {k: c.get(k) for k in ("id", "text", "doc_id", "quote", "metric", "value")}})
    pairs.sort(key=lambda x: hashlib.sha256(f"{x['entity']}{x['claim']['id']}".encode()).hexdigest())
    return pairs[:MAX_ORIGINALS]


def perturb(o: dict) -> list[dict]:
    c, text, out = o["claim"], o["claim"]["text"], []
    nums = re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", text)
    if nums:
        n = nums[0]
        v = float(n.replace(",", ""))
        out.append(("swapped_number", "contradicts", text.replace(n, f"{v * 3 + 7:,.0f}", 1)))
    if re.search(re.escape(o["name"]), text, re.I):
        out.append(("wrong_entity", "contradicts", re.sub(re.escape(o["name"]), o["other"], text, flags=re.I)))
    years = re.findall(r"\b20[12]\d\b", text)
    if years:
        out.append(("wrong_date", "contradicts", text.replace(years[0], str(int(years[0]) - 2), 1)))
    out.append(("added_qualifier", "partial", text.rstrip(".") + QUALIFIER + "."))
    return [{**o, "kind": k, "expected": e, "claim": {**c, "id": f"{c['id']}~{k}", "text": t}} for k, e, t in out]


def run() -> dict:
    gw, store = Gateway(), DocStore()
    orig = originals()
    pairs = [{**o, "kind": "original", "expected": None} for o in orig]
    for o in orig:
        pairs += perturb(o)
    for i, p in enumerate(pairs):
        p["pair_id"] = f"q{i:03d}"
        facts = {}
        p["verifier_ok"] = check_claim(p["claim"], store, facts).ok
    labels: dict[str, str] = {}
    for i in range(0, len(pairs), BATCH):
        chunk = pairs[i:i + BATCH]
        body = "\n".join(json.dumps({"claim_id": p["pair_id"], "claim": p["claim"]["text"],
                                     "quote": p["claim"]["quote"]}, ensure_ascii=False) for p in chunk)
        prompt = (f"Pairs:\n{body}\n\nReturn ONLY JSON: {{\"labels\": [{{\"claim_id\", \"label\", \"reason\"}}]}} "
                  f"with one label per pair; reason under 12 words.")
        res = gw.complete("critique", SYSTEM, prompt, tag=f"claim_eval:{i // BATCH}", schema=schemas.EntailmentBatch)
        labels |= {x["claim_id"]: x["label"] for x in res.parsed["labels"]}
    for p in pairs:
        p["critic_label"] = labels.get(p["pair_id"], "missing")
        p["critic_flags"] = p["critic_label"] != "entails"
    kinds = sorted({p["kind"] for p in pairs if p["kind"] != "original"})
    orig_label = {(p["entity"], p["claim"]["id"]): p["critic_label"] for p in pairs if p["kind"] == "original"}
    hard = ("contradicts", "unsupported")
    recall = {}
    for k in kinds:
        g = [p for p in pairs if p["kind"] == k]
        # conditional: only perturbations of claims whose ORIGINAL the critic called "entails" -- otherwise a
        # "partial" on the perturbed copy may just repeat the critic's view of the original
        cond = [p for p in g if orig_label.get((p["entity"], p["claim"]["id"].split("~")[0])) == "entails"]
        recall[k] = {"n": len(g), "expected": g[0]["expected"],
                     "verifier_recall": round(sum(not p["verifier_ok"] for p in g) / len(g), 4),
                     # lenient: any label other than "entails" counts as caught (partial ships, tagged)
                     "critic_recall_lenient": round(sum(p["critic_flags"] for p in g) / len(g), 4),
                     # strict: only labels that WITHHOLD the claim (contradicts / unsupported)
                     "critic_recall_strict": round(sum(p["critic_label"] in hard for p in g) / len(g), 4),
                     "n_conditional_on_original_entails": len(cond),
                     "critic_recall_lenient_conditional": round(sum(p["critic_flags"] for p in cond) / len(cond), 4) if cond else None,
                     "critic_recall_strict_conditional": round(sum(p["critic_label"] in hard for p in cond) / len(cond), 4) if cond else None,
                     "either_recall": round(sum((not p["verifier_ok"]) or p["critic_flags"] for p in g) / len(g), 4),
                     "labelled_partial_so_shipped_tagged": sum(p["critic_label"] == "partial" for p in g)}
        recall[k]["critic_recall"] = recall[k]["critic_recall_lenient"]
    og = [p for p in pairs if p["kind"] == "original"]
    out = {"n_original_pairs": len(og), "n_perturbed_pairs": len(pairs) - len(og), "recall_by_perturbation": recall,
           "originals": {"verifier_pass_rate": round(sum(p["verifier_ok"] for p in og) / len(og), 4),
                         "critic_flag_rate_upper_bound_on_false_positives": round(sum(p["critic_flags"] for p in og) / len(og), 4),
                         "critic_labels": {lab: sum(p["critic_label"] == lab for p in og)
                                           for lab in ("entails", "partial", "contradicts", "unsupported", "missing")}},
           "precision": "pending human labels (results/adjudication/flag_sample.csv)",
           "notes": ["'partial' ships with a visible tag, so a perturbation labelled partial (e.g. some wrong-entity "
                     "swaps) still ships; strict recall counts only labels that withhold the claim",
                     "the entailed share partly measures quote scope: a claim bundling several facts behind one quote "
                     "is rarely fully entailed; splitting claims into one fact each before verification is the "
                     "next step (not done: it needs new drafter calls)",
                     "no inter-rater agreement (kappa) is reported: the critic was not re-run on the same pairs"],
           "pairs": [{k: p[k] for k in ("pair_id", "entity", "kind", "expected", "verifier_ok", "critic_label")}
                     | {"text": p["claim"]["text"], "quote": p["claim"]["quote"]} for p in pairs]}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "pairs"}, indent=1))
    return out
