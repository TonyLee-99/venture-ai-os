#!/usr/bin/env bash
# Fresh clone -> ready to run `make check` (offline) and `make reproduce` (network).
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || { echo "install uv first: https://docs.astral.sh/uv/"; exit 1; }
uv sync --locked --all-groups
# headless browser only needed for `make screenshots`
uv run --group screenshot playwright install chromium >/dev/null 2>&1 || echo "playwright browser not installed (screenshots only)"
mkdir -p data/raw
echo "ready: run 'make check' (offline) or 'make reproduce' (pulls live data, uses cached LLM calls)"
