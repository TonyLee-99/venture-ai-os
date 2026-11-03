# venture-ai-os: one-command targets.
# Offline targets (check, acceptance, replay, sourcing-run, dashboard) run from committed caches/cassettes.
# Network targets (ingest, reproduce) pull live public data and may call the LLMs (cached).
UV ?= uv
PY = $(UV) run python
CLI = $(PY) -m vaios.cli

.PHONY: init lint test check acceptance verifier-eval export-skills live-run claim-eval monitor-diagnostics company-brief readme ingest warehouse freeze backtest llm-eval sourcing-run memos \
        monitor brief dashboard screenshots extracts replay reproduce clean

init:           ## fresh clone -> ready (deps + headless browser for screenshots)
	bash scripts/init.sh

lint:
	$(UV) run ruff check .

test:
	$(UV) run pytest -q

check: lint test acceptance ## fast, offline: lint + tests + regeneration checks

acceptance:     ## committed results must recompute unchanged from frozen tables and cassettes (strict replay)
	bash scripts/regen_check.sh "$(CLI) backtest" results/backtest/backtest.json
	bash scripts/regen_check.sh "$(CLI) verifier-eval" results/receipts/verifier_eval.json
	bash scripts/regen_check.sh "VAIOS_STRICT_REPLAY=1 $(CLI) sourcing-run" results/memos results/sourcing

# ---------- network: live public data ----------
ingest:         ## pull raw data from all sources into data/raw (+ manifest)
	$(CLI) ingest

warehouse:      ## build data/warehouse.duckdb from data/raw with SQL
	$(CLI) warehouse

freeze:         ## export the small point-in-time tables that offline tests/backtests need (committed)
	$(CLI) freeze

# ---------- jobs ----------
backtest:       ## point-in-time screening backtest (deterministic; from frozen tables)
	$(CLI) backtest

llm-eval:       ## LLM screening judgment on post-cutoff outcomes only (gateway, cached)
	$(CLI) llm-eval

sourcing-run:   ## pre-investment job: source -> stage check -> memo -> critique -> committee -> decision cards
	$(CLI) sourcing-run

live-run:       ## LOCAL live mode: fresh pulls + warehouse, then a new shortlist with budgeted, cached LLM calls
	$(CLI) ingest
	$(CLI) warehouse
	$(CLI) freeze
	rm -f results/sourcing/shortlist.json
	VAIOS_MAX_CALLS=$${VAIOS_MAX_CALLS:-400} $(CLI) sourcing-run

claim-eval:     ## verifier + critic on real memo claims and labelled perturbations
	$(CLI) claim-eval

monitor-diagnostics: ## exploratory monitoring diagnostics (ADR 0009)
	$(CLI) monitor-diagnostics

company-brief:  ## KPI brief for one named comparable (Daydreams)
	$(CLI) company-brief

readme:         ## re-render anchored numbers in README.md from results/
	$(PY) -m vaios.report render

monitor:        ## post-investment job: series -> changepoints -> event validation
	$(CLI) monitor

brief:          ## weekly brief with receipts
	$(CLI) brief

dashboard:      ## static HTML dashboard from committed results
	$(CLI) dashboard

extracts:       ## Tableau-ready CSV extracts
	$(CLI) extracts

screenshots:    ## headless screenshot of the dashboard into docs/img
	$(UV) run --group screenshot python scripts/screenshot.py

verifier-eval:  ## test the receipts verifier on gold spans + programmatic corruptions
	$(CLI) verifier-eval

export-skills:  ## founder bundle: skills + output schemas -> dist/founder-skills-bundle
	$(CLI) export-skills

replay:         ## re-run every LLM job in strict replay (no model calls) and diff against committed outputs
	VAIOS_STRICT_REPLAY=1 $(CLI) sourcing-run
	VAIOS_STRICT_REPLAY=1 $(CLI) llm-eval
	VAIOS_STRICT_REPLAY=1 $(CLI) brief
	VAIOS_STRICT_REPLAY=1 $(CLI) company-brief
	VAIOS_STRICT_REPLAY=1 $(CLI) claim-eval
	git diff --stat --exit-code -- results

reproduce: ingest warehouse freeze backtest llm-eval monitor monitor-diagnostics sourcing-run brief company-brief claim-eval verifier-eval extracts dashboard screenshots readme check

clean:          ## delete the rebuilt warehouse (NOT raw pulls, NOT cassettes)
	rm -f data/warehouse.duckdb
