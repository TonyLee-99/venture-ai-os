"""Headline numbers as the exact strings the README prints. tests/test_readme_numbers.py asserts that every
one of them appears verbatim in README.md, so README and results/ can never drift apart."""

from __future__ import annotations

import json

from vaios.config import RESULTS


def _j(path: str) -> dict:
    return json.loads((RESULTS / path).read_text())


def headline_numbers() -> dict[str, str]:
    bt, cp, rs = _j("backtest/backtest.json"), _j("monitoring/changepoints.json"), _j("sourcing/run_summary.json")
    full, gh, heur = bt["scores"]["s_logit_full"], bt["scores"]["s_logit_github"], bt["scores"]["s_heuristic"]
    pair = bt["paired_vs_best_baseline"]["s_logit_full"]
    base = bt["scores"][pair["best_baseline"]]
    h = cp["headline"]
    n = {
        "bt_rows": f"{bt['n_rows_test']:,}",
        "bt_pos": f"{bt['n_positives_test']}",
        "bt_protocols": f"{bt['n_protocols_test']:,}",
        "bt_base_rate": f"{bt['base_rate_test']:.1%}",
        "auc_full": f"{full['auc']:.3f}",
        "auc_full_ci": f"{full['auc_ci95'][0]:.3f}-{full['auc_ci95'][1]:.3f}",
        "auc_github": f"{gh['auc']:.3f}",
        "auc_heuristic": f"{heur['auc']:.3f}",
        "auc_best_base": f"{base['auc']:.3f}",
        "auc_diff": f"{pair['auc_diff']:+.3f}",
        "auc_diff_ci": f"{pair['ci95'][0]:+.3f} to {pair['ci95'][1]:+.3f}",
        "auc_leaky": f"{bt['scores']['leaky_stars_now']['auc']:.3f}",
        "lift50_full": f"{full['lift@50']:.1f}x",
        "lift50_base": f"{base['lift@50']:.1f}x",
        "p50_full": f"{full['p@50']:.3f}",
        "memos": f"{rs['n_memos']}",
        "claims_drafted": f"{rs['claims_drafted']}",
        "raw_precision": f"{rs['raw_citation_precision']:.1%}",
        "post_precision": f"{rs['post_repair_citation_precision']:.1%}",
        "claims_shipped": f"{rs['claims_shipped']}",
        "critic_flags": f"{rs['critic_unsupported_flags']}",
        "disagreements": f"{rs['memos_with_disagreement']}",
        "cp_hit": f"{h['event_hit_rate']:.0%}",
        "cp_null": f"{h['null_mean_hit_rate']:.0%}",
        "cp_p": f"{h['p_value']:.2f}",
        "cp_fa": f"{h['false_alarm_rate']:.0%}",
        "cp_fa_z": f"{h['baseline_zscore']['false_alarm_rate']:.0%}",
        "cp_n": f"{h['n_changepoints']}",
        "cp_events": f"{h['n_events']}",
    }
    llm = RESULTS / "backtest" / "llm_judgment.json"
    if llm.exists():
        lj = json.loads(llm.read_text())
        n["llm_n"], n["llm_pos"] = f"{lj['n_items']}", f"{lj['n_positives']}"
        for k, v in lj["results"].items():
            n[f"llm_auc|{k}"] = f"{v['auc']:.2f}"
    return n


if __name__ == "__main__":
    for k, v in headline_numbers().items():
        print(f"{k:<40} {v}")
