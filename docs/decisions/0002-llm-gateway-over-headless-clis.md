# 0002. One LLM gateway, two model families, recorded responses as the test fixture

Status: accepted (2026-11-02).

## Context
No API keys exist on the build machine; both vendors' headless CLIs run on a subscription. The fund's real
stack is not public, and it describes an "AI Gateway layer". CI must run with no keys and no network LLM.

## Decision
- Every call goes through `vaios.gateway.Gateway.complete(route, system, prompt, schema=...)`. Jobs ask for a
  route (`draft`, `critique`, `judge`, `judge_alt`), not a vendor. Routes map to `claude -p` (Sonnet) and
  `codex exec -s read-only` (GPT); swapping in API clients changes one file.
- Content-addressed cache: key = sha256 of backend, model, system, prompt, sample and a pipeline version. The
  cache directory `cassettes/` is committed, so it is also the replay fixture. `VAIOS_STRICT_REPLAY=1` turns a
  miss into an error; `make replay`, CI and the nightly workflow run that way.
- Ledger row per real call (latency, tokens, dollar cost when the CLI reports it) in `results/llm_ledger.jsonl`;
  hard budget `VAIOS_MAX_CALLS` (default 400).
- Structured outputs are pydantic models; one repair round on invalid JSON, then the job fails loudly.

## Consequences
- The CLIs expose no temperature or seed; replay determinism comes from the cache, not from sampling settings.
- Codex prints total tokens only and no cost, so the ledger's dollar figure covers the Claude side only.
- Gotcha found in the build: `codex exec` with an inherited open stdin waits for input; the prompt is now
  passed on stdin explicitly.
