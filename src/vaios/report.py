"""Headline numbers as the exact strings the README prints. tests/test_readme_numbers.py asserts that every
one of them appears verbatim in README.md, so README and results/ can never drift apart."""

from __future__ import annotations

import json
import re

from vaios.config import RESULTS, ROOT


def _j(path: str) -> dict:
    return json.loads((RESULTS / path).read_text())


def headline_numbers() -> dict[str, str]:
    bt, cp, rs = _j("backtest/backtest.json"), _j("monitoring/changepoints.json"), _j("sourcing/run_summary.json")
    allp, nr = bt["populations"]["all"], bt["populations"]["never_raised"]
    pair, pair_nr = allp["paired_vs_best_baseline"]["s_logit_full"], nr["paired_vs_best_baseline"]
    base, base_nr = allp["scores"][pair["best_baseline"]], nr["scores"][pair_nr["s_heuristic"]["best_baseline"]]
    s, snr = allp["scores"], nr["scores"]
    h = cp["headline"]
    rm, lt = bt["round_mix_all"], bt["lead_time"]
    n = {
        # screening, seed-relevant population first
        "nr_rows": f"{nr['n_rows']:,}", "nr_pos": f"{nr['n_positive_rows']}", "nr_pos_protocols": f"{nr['n_positive_protocols']}",
        "nr_raises": f"{bt['round_mix_never_raised']['distinct_raises']}",
        "nr_seed": f"{bt['round_mix_never_raised']['seed_preseed_angel']}",
        "auc_nr_full": f"{snr['s_logit_full']['auc']:.3f}",
        "auc_nr_full_ci": f"{snr['s_logit_full']['auc_ci95'][0]:.2f}-{snr['s_logit_full']['auc_ci95'][1]:.2f}",
        "auc_nr_github": f"{snr['s_logit_github']['auc']:.3f}",
        "auc_nr_heuristic": f"{snr['s_heuristic']['auc']:.3f}",
        "auc_nr_heuristic_ci": f"{snr['s_heuristic']['auc_ci95'][0]:.2f}-{snr['s_heuristic']['auc_ci95'][1]:.2f}",
        "auc_nr_commits": f"{snr['b_commits']['auc']:.3f}", "auc_nr_random": f"{snr['b_random']['auc']:.3f}",
        "auc_nr_heur_gh": f"{snr['s_heuristic_github']['auc']:.3f}",
        "auc_nr_best_base": f"{base_nr['auc']:.3f}",
        "auc_nr_heur_diff_ci": f"{pair_nr['s_heuristic']['ci95'][0]:+.3f} to {pair_nr['s_heuristic']['ci95'][1]:+.3f}",
        # full population
        "bt_rows": f"{bt['n_rows_test']:,}", "bt_pos": f"{bt['n_positives_test']}",
        "bt_pos_protocols": f"{bt['n_positive_protocols_test']}", "bt_protocols": f"{bt['n_protocols_test']:,}",
        "bt_raises": f"{rm['distinct_raises']}", "bt_seed": f"{rm['seed_preseed_angel']}",
        "bt_base_rate": f"{bt['base_rate_test']:.1%}",
        "auc_full": f"{s['s_logit_full']['auc']:.3f}",
        "auc_full_ci": f"{s['s_logit_full']['auc_ci95'][0]:.3f}-{s['s_logit_full']['auc_ci95'][1]:.3f}",
        "auc_full_pooled": f"{s['s_logit_full']['pooled_auc']:.3f}",
        "auc_heuristic": f"{s['s_heuristic']['auc']:.3f}", "auc_github": f"{s['s_logit_github']['auc']:.3f}",
        "auc_best_base": f"{base['auc']:.3f}", "auc_diff": f"{pair['auc_diff']:+.3f}",
        "auc_diff_ci": f"{pair['ci95'][0]:+.3f} to {pair['ci95'][1]:+.3f}",
        "lift50_full": f"{s['s_logit_full']['lift@50']:.1f}x", "lift50_base": f"{base['lift@50']:.1f}x",
        "p50_full": f"{s['s_logit_full']['p@50']:.3f}",
        "lead_gh_median": f"{lt['github_first_repo']['median_months']:.1f}",
        "lead_gh_share": f"{lt['github_first_repo']['share_signal_before_raise']:.0%}",
        "lead_dl_median": f"{lt['defillama_listing']['median_months']:.1f}",
        "lead_dl_share": f"{lt['defillama_listing']['share_signal_before_raise']:.0%}",
        "lead_after_share": f"{lt['share_of_todays_top5_repos_created_after_first_raise']:.0%}",
        "lead_2020_22": f"{lt['share_first_raises_2020_2022']:.0%}",
        # sourcing + memos
        "n_entities": f"{_j('sourcing/shortlist.json')['n_candidates']:,}",
        "memos": f"{rs['n_memos']}", "claims_drafted": f"{rs['claims_drafted']}",
        "raw_precision": f"{rs['raw_citation_precision']:.1%}",
        "critic_entailed": f"{rs['critic_entailed_over_verified']:.1%}",
        "claims_partial": f"{rs['claims_shipped_partial_tagged']}", "claims_withheld_critic": f"{rs['claims_withheld_by_critic']}",
        "recs": f"{rs['recommendations']['advance']} advance / {rs['recommendations']['watch']} watch / {rs['recommendations']['pass']} pass",
        "rec_agreement": f"{rs['recommendation_agreement']} of {rs['n_memos']}",
        "cards": f"{rs['memos_with_decision_card']}",
        # monitoring
        "cp_hit": f"{h['event_hit_rate']:.0%}", "cp_null": f"{h['null_mean_hit_rate']:.0%}", "cp_p": f"{h['p_value']:.2f}",
        "cp_fa": f"{h['false_alarm_rate']:.0%}", "cp_n": f"{h['n_changepoints']}", "cp_events": f"{h['n_events']}",
        "cp_oct_ratio": f"~{round(next(g['ratio'] for g in cp['series'][cp['headline_series']]['segments'] if g['date'] == '2025-10-20')):,}x",
    }
    n["llm_calls"] = f"{len((RESULTS / 'llm_ledger.jsonl').read_text().splitlines())}"
    stage_checks = _j_list("sourcing/stage_checks.json")
    n["stage_checked"] = f"{len(stage_checks)}"
    n["stage_excluded"] = f"{sum(not c['seed_eligible'] for c in stage_checks)}"
    ce = RESULTS / "receipts" / "claim_eval.json"
    if ce.exists():
        c = json.loads(ce.read_text())
        n["ce_orig"], n["ce_pert"] = f"{c['n_original_pairs']}", f"{c['n_perturbed_pairs']}"
        n["ce_critic_flag_orig"] = f"{c['originals']['critic_flag_rate_upper_bound_on_false_positives']:.0%}"
        for k, v in c["recall_by_perturbation"].items():
            n[f"ce_ver|{k}"], n[f"ce_cri|{k}"] = f"{v['verifier_recall']:.0%}", f"{v['critic_recall_lenient']:.0%}"
            n[f"ce_cri_strict|{k}"] = f"{v['critic_recall_strict']:.0%}"
            cond = v["critic_recall_lenient_conditional"]
            n[f"ce_cri_cond|{k}"] = f"{cond:.0%}" if cond is not None else "n/a"
            n[f"ce_cond_n|{k}"] = f"{v['n_conditional_on_original_entails']}"
        n["ce_strict_entity"] = n.get("ce_cri_strict|wrong_entity", "n/a")
    lj = RESULTS / "backtest" / "llm_judgment.json"
    if lj.exists():
        d = json.loads(lj.read_text())
        wf, pc = d["walk_forward_anonymized"], d["post_cutoff"]
        n["wf_items"], n["wf_pos"] = f"{wf['n_items']}", f"{wf['n_positives']}"
        for k, v in wf["all"].items():
            n[f"wf_auc|{k}"] = f"{v['auc']:.2f}"
        for k, v in wf["never_raised"].items():
            if isinstance(v, dict):
                n[f"wf_nr_auc|{k}"] = f"{v['auc']:.2f}"
        n["pc_items"], n["pc_pos"] = f"{pc['n_items']}", f"{pc['n_positives']}"
        m = pc["raise_mentions_in_current_description"]
        n["pc_mention_pos"], n["pc_mention_neg"] = f"{m['positives']} of {m['positives_total']}", f"{m['negatives']} of {m['negatives_total']}"
        for k, v in pc["results"].items():
            n[f"pc_auc|{k}"] = f"{v['auc']:.2f}"
        probe = _j("backtest/cutoff_probe.json")["models"]
        for k, v in probe.items():
            n[f"probe|{k}"] = v["latest_correct_event"] or "none"
    dg = RESULTS / "monitoring" / "diagnostics.json"
    if dg.exists():
        g = json.loads(dg.read_text())
        n["pw_needed"] = f"{g['power_preregistered_test']['hits_needed_for_p_lt_0.05']}"
        n["pw_07"] = f"{g['power_preregistered_test']['power_at_true_hit_rate']['0.7']:.0%}"
        rt = g["realtime_replay_headline_series"]
        n["rt_delay"] = f"{rt['median_detection_delay_weeks']:g}"
        n["rt_dropped"] = f"{rt['real_time_alarms_later_dropped']}"
        v2 = g["event_list_v2_with_token_launches"]
        n["v2_events"], n["v2_hit"], n["v2_null"], n["v2_p"] = (f"{v2['n_events']}", f"{v2['hit_rate']:.0%}",
                                                               f"{v2['null_mean']:.0%}", f"{v2['p_value']:.2f}")
        n["payai_fixed"] = f"{g['payai_30d_window_fix']['fixed_window_txs']:,}"
        n["payai_old"] = f"{g['payai_30d_window_fix']['round1_window_txs']:,}"
        mc = g["matched_count_vs_zscore"]
        n["mc_k"], n["mc_pelt_fa"], n["mc_z_fa"] = (f"{mc['k']}", f"{mc['pelt']['false_alarm_rate']:.0%}",
                                                    f"{mc['zscore_top_k']['false_alarm_rate']:.0%}")
    return n


def _j_list(path: str) -> list:
    return json.loads((RESULTS / path).read_text())


# ---------- anchored README numbers ----------
# Every headline number in README.md is written as <!--n:key-->value<!--/n-->. `make readme` re-renders the
# values from results/; the test fails if any anchored value differs from results/ or a required key is missing.
TOKEN = re.compile(r"<!--n:([\w|.\-]+)-->(.*?)<!--/n-->")


def render_readme(path=None) -> int:
    path = path or ROOT / "README.md"
    nums = headline_numbers()
    text = path.read_text()
    new = TOKEN.sub(lambda m: f"<!--n:{m.group(1)}-->{nums[m.group(1)]}<!--/n-->", text)
    path.write_text(new)
    return len(TOKEN.findall(new))


def check_readme(text: str, required: set[str] | None = None) -> list[str]:
    nums = headline_numbers()
    problems = [f"{k}: README says {v!r}, results say {nums.get(k)!r}" for k, v in TOKEN.findall(text)
                if nums.get(k) != v]
    present = {k for k, _ in TOKEN.findall(text)}
    problems += [f"{k}: required number not anchored in README" for k in (required or set()) - present]
    return problems


if __name__ == "__main__":
    import sys

    if sys.argv[1:] == ["render"]:
        print(f"rendered {render_readme()} anchored numbers into README.md")
    else:
        for k, v in headline_numbers().items():
            print(f"{k:<40} {v}")
