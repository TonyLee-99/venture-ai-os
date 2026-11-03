#!/usr/bin/env bash
# Regeneration check used by `make acceptance`: run a command and fail if it changes the given files.
# Works on uncommitted trees (compares against a temp copy, not git), so `make check` stays usable mid-work.
set -euo pipefail
cmd="$1"; shift
tmp=$(mktemp -d)
for f in "$@"; do mkdir -p "$tmp/$(dirname "$f")"; cp -R "$f" "$tmp/$f"; done
eval "$cmd" >/dev/null
status=0
for f in "$@"; do
  if [[ "$f" == *.json && -f "$f" ]]; then  # floats within 1e-3: rounding can differ across OS (scripts/json_close.py)
    uv run python scripts/json_close.py "$tmp/$f" "$f" || status=1
  else
    diff -r -q "$tmp/$f" "$f" || status=1
  fi
done
rm -rf "$tmp"
exit $status
