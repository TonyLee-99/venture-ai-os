"""F17: README headline numbers are anchored tokens rendered from results/; any drift fails."""

from vaios.config import ROOT
from vaios.report import TOKEN, check_readme, headline_numbers

REQUIRED = {"bt_rows", "bt_pos", "bt_pos_protocols", "nr_pos", "nr_pos_protocols", "auc_nr_full", "auc_nr_heuristic",
            "auc_nr_best_base", "auc_full", "auc_best_base", "n_entities", "rec_agreement", "cp_oct_ratio",
            "p50_full", "raw_precision", "critic_entailed", "cp_hit", "cp_null"}


def test_readme_anchored_numbers_match_results():
    assert check_readme((ROOT / "README.md").read_text(), REQUIRED) == []


def test_mutation_is_caught():
    text = (ROOT / "README.md").read_text()
    n = headline_numbers()
    tok = f"<!--n:bt_pos-->{n['bt_pos']}<!--/n-->"
    assert tok in text
    assert check_readme(text.replace(tok, "<!--n:bt_pos-->18<!--/n-->"), REQUIRED)  # 80 -> 18 must fail
    assert check_readme(text.replace(tok, ""), REQUIRED)                            # removing it must fail too


def test_tokens_parse():
    assert TOKEN.findall("a <!--n:x-->1.0<!--/n--> b") == [("x", "1.0")]
