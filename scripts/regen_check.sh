#!/usr/bin/env bash
# Regeneration check used by feature verifications: run a command and fail if it changes the given files.
# Works on uncommitted trees (compares against a temp copy, not git), so `make check` stays usable mid-work.
set -euo pipefail
cmd="$1"; shift
tmp=$(mktemp -d)
for f in "$@"; do mkdir -p "$tmp/$(dirname "$f")"; cp -R "$f" "$tmp/$f"; done
eval "$cmd" >/dev/null
status=0
for f in "$@"; do diff -r -q "$tmp/$f" "$f" || status=1; done
rm -rf "$tmp"
exit $status
