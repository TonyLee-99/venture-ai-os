# venture-ai-os: one-command targets.
# Offline targets (check, verify, replay, sourcing-run, dashboard) run from committed caches/cassettes.
# Network targets (ingest, reproduce) pull live public data and may call the LLMs (cached).
UV ?= uv
PY = $(UV) run python
CLI = $(PY) -m vaios.cli

.PHONY: init lint test check verify ingest warehouse freeze backtest llm-eval sourcing-run memos \
        monitor brief dashboard screenshots extracts replay reproduce clean

init:           ## fresh clone -> ready (deps + headless browser for screenshots)
	bash scripts/init.sh

lint:
	$(UV) run ruff check .

test:
	$(UV) run pytest -q

check: lint test ## fast, offline: lint + tests + feature verification (fails only on regressions)
	$(PY) scripts/verify_features.py --check

verify:         ## run every feature verification and write state/evidence into feature_list.json
	$(PY) scripts/verify_features.py

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

sourcing-run:   ## nightly pre-investment job: source -> screen -> memo -> critique -> decision cards
	$(CLI) sourcing-run

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

replay:         ## re-run every LLM job in strict replay (no model calls) and diff against committed outputs
	VAIOS_STRICT_REPLAY=1 $(CLI) sourcing-run
	VAIOS_STRICT_REPLAY=1 $(CLI) llm-eval
	VAIOS_STRICT_REPLAY=1 $(CLI) brief
	git diff --stat --exit-code -- results

reproduce: ingest warehouse freeze backtest llm-eval sourcing-run monitor brief extracts dashboard screenshots verify

clean:          ## delete the rebuilt warehouse (NOT raw pulls, NOT cassettes)
	rm -f data/warehouse.duckdb
