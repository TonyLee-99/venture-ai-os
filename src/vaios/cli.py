"""Single entrypoint behind the Makefile: `uv run python -m vaios.cli <command>`."""

from __future__ import annotations

import argparse
import importlib

# command -> "module:function"; imported lazily so offline commands never import network code
COMMANDS = {
    "ingest": "vaios.ingest.run:run",
    "warehouse": "vaios.dakr.warehouse:build",
    "freeze": "vaios.dakr.freeze:run",
    "backtest": "vaios.screening.backtest:run",
    "llm-eval": "vaios.screening.llm_judgment:run",
    "sourcing-run": "vaios.agents.pipeline:sourcing_run",
    "monitor": "vaios.monitoring.run:run",
    "brief": "vaios.agents.pipeline:brief_run",
    "dashboard": "vaios.dashboard.build:run",
    "extracts": "vaios.dashboard.extracts:run",
    "manifest": "vaios.dakr.freeze:summarize_manifest",
    "export-skills": "vaios.agents.skills:export_bundle",
    "verifier-eval": "vaios.receipts.evaluate:run",
    "claim-eval": "vaios.receipts.claim_eval:run",
    "monitor-diagnostics": "vaios.monitoring.diagnostics:run",
    "readme": "vaios.report:render_readme",
    "company-brief": "vaios.agents.company_brief:run",
}


def main() -> None:
    ap = argparse.ArgumentParser(prog="vaios")
    ap.add_argument("command", choices=sorted(COMMANDS))
    ap.add_argument("--only", help="ingest: run a single stage")
    args = ap.parse_args()
    module, func = COMMANDS[args.command].split(":")
    fn = getattr(importlib.import_module(module), func)
    fn(only=args.only) if args.command == "ingest" else fn()


if __name__ == "__main__":
    main()
