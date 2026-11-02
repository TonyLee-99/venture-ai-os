"""F16: skills are valid SKILL.md folders, are the prompt source for agents, and export as a founder bundle."""

import json

from vaios.agents import skills


def test_every_skill_has_frontmatter_matching_folder():
    names = skills.all_skills()
    assert len(names) >= 5
    for n in names:
        meta, body = skills.load(n)
        assert meta["name"] == n and meta["description"] and meta["version"] >= 1 and len(body) > 200
        for inc in meta.get("includes", []):
            assert inc in names


def test_system_prompt_includes_receipts_rules():
    sp = skills.system_prompt("diligence-memo")
    assert "Receipts" in sp and "Product-Market Fit" in sp


def test_export_bundle(tmp_path):
    dest = skills.export_bundle(tmp_path / "bundle")
    assert sorted(p.parent.name for p in (dest / "skills").glob("*/SKILL.md")) == skills.all_skills()
    contracts = json.loads((dest / "schemas.json").read_text())
    assert {"Memo", "Critique", "WeeklyBrief", "JudgmentBatch"} <= set(contracts)
