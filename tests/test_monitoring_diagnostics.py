"""Monitoring diagnostics exist, are labelled exploratory, and recompute offline; company KPI brief verifies."""

import json

from vaios.config import RESULTS
from vaios.dakr.docstore import DocStore
from vaios.receipts.verify import check_claim

DG = json.loads((RESULTS / "monitoring" / "diagnostics.json").read_text())


def test_sections_present_and_labelled():
    assert DG["status"].startswith("exploratory")
    for k in ("power_preregistered_test", "realtime_replay_headline_series", "matched_count_vs_zscore",
              "event_leads_window_3d_before_14d_after", "event_list_v2_with_token_launches",
              "september_2026_drop_artifact_check"):
        assert k in DG, k
    mc = DG["matched_count_vs_zscore"]
    assert mc["k"] > 0


def test_diagnostics_recompute_offline():
    from vaios.monitoring import diagnostics

    assert json.loads(json.dumps(diagnostics.run(), default=str)) == DG


def test_company_brief_claims_verify():
    out = json.loads((RESULTS / "briefs" / "company_daydreams.json").read_text())
    from vaios.agents.company_brief import kpis
    k = kpis()
    facts = {f"daydreams.{d:%Y-%m-%d}.{c}": round(float(v), 4) for d, r in k.iterrows() for c, v in r.items() if v == v}
    store = DocStore()
    for n in out["brief"]["inflections"]:
        for c in n["claims"]:
            if c["metric"] in facts:
                assert check_claim(c, store, facts).ok, c["id"]
