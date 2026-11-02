"""Skills = plain SKILL.md folders (YAML frontmatter + markdown body). They are the prompt library: an agent's
system prompt is its skill body plus the bodies of the skills it `includes`. Vendor-neutral on purpose: the
same folder works as a Claude Code skill, a Codex AGENTS-style instruction file, or a plain prompt.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from vaios.config import ROOT, SKILLS


def load(name: str, root: Path = SKILLS) -> tuple[dict, str]:
    text = (root / name / "SKILL.md").read_text()
    _, front, body = text.split("---", 2)
    return yaml.safe_load(front), body.strip()


def system_prompt(name: str, root: Path = SKILLS) -> str:
    meta, body = load(name, root)
    parts = [body]
    for inc in meta.get("includes", []):
        parts.append(load(inc, root)[1])
    return "\n\n".join(parts)


def all_skills(root: Path = SKILLS) -> list[str]:
    return sorted(p.parent.name for p in root.glob("*/SKILL.md"))


def schema_hint(model_cls) -> str:
    """Compact JSON schema to paste into prompts so both model families see the same contract."""
    return json.dumps(model_cls.model_json_schema(), separators=(",", ":"))


def export_bundle(dest: Path | None = None) -> Path:
    """Package the skills for a portfolio founder: SKILL.md folders + output schemas + a one-page README."""
    from vaios.agents import schemas

    dest = dest or ROOT / "dist" / "founder-skills-bundle"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(SKILLS, dest / "skills")
    contracts = {name: getattr(schemas, name).model_json_schema()
                 for name in ("Memo", "Critique", "WeeklyBrief", "JudgmentBatch")}
    (dest / "schemas.json").write_text(json.dumps(contracts, indent=1))
    (dest / "README.md").write_text(
        "# Founder skills bundle\n\nDrop `skills/` into `.claude/skills/` (Claude Code) or reference the SKILL.md "
        "files from AGENTS.md (Codex). Each skill states its output schema (see schemas.json) and the receipts "
        "rule: every factual claim carries a quote from a stored source or a metric key.\n\n"
        f"Skills: {', '.join(all_skills())}\n")
    print(f"exported {len(all_skills())} skills -> {dest}")
    return dest
