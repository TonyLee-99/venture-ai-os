"""The AI gateway: every LLM call in the repo goes through `Gateway.complete`.

What it adds on top of a raw model call
- routing: a job asks for a *route* ("draft", "critique", ...), config maps routes to backends;
- content-addressed cache: key = sha256(backend, model, system, prompt, sample, PIPELINE_VERSION). The cache
  directory `cassettes/` is committed, so it doubles as recorded responses for offline replay;
- strict replay (VAIOS_STRICT_REPLAY=1): a cache miss raises ReplayMiss instead of calling a model (CI);
- retries with exponential backoff; a hard call budget (VAIOS_MAX_CALLS);
- a ledger row per real call (latency, tokens, cost) in results/llm_ledger.jsonl;
- structured output: optional pydantic schema; one repair round if the JSON does not validate.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from vaios.config import CASSETTES, RESULTS
from vaios.gateway.backends import BackendError, ClaudeCLI, CodexCLI, RawResult

PIPELINE_VERSION = "v1"  # bump when something that changes a response's meaning (not prompt text) changes
LEDGER = RESULTS / "llm_ledger.jsonl"

ROUTES = {
    "draft": ("claude_cli", "claude-sonnet-5-5"),     # memo drafting, brief writing
    "critique": ("codex_cli", "gpt-6.1-sol"),         # cross-family critic (RLEN-style)
    "judge": ("claude_cli", "claude-sonnet-5-5"),     # screening judgment in the held-out eval
    "judge_alt": ("codex_cli", "gpt-6.1-sol"),        # same judgment, other family
}


class ReplayMiss(RuntimeError):
    """Strict replay is on and this exact request was never recorded."""


class BudgetExceeded(RuntimeError):
    pass


def strict_replay() -> bool:
    return os.environ.get("VAIOS_STRICT_REPLAY", "") not in ("", "0", "false")


def cache_key(**parts: Any) -> str:
    blob = json.dumps({**parts, "pipeline": PIPELINE_VERSION}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode()).hexdigest()


@dataclass
class LLMResult:
    text: str
    backend: str
    model: str
    cache_key: str
    cached: bool
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float | None = None
    parsed: dict | None = field(default=None, repr=False)


def extract_json(text: str) -> Any:
    """Models wrap JSON in prose or ``` fences; take the outermost {...} or [...] block."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    body = fenced.group(1) if fenced else text
    start = min([i for i in (body.find("{"), body.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("no JSON object in model output")
    end = max(body.rfind("}"), body.rfind("]"))
    return json.loads(body[start:end + 1])


class Gateway:
    def __init__(self, cache_dir: Path = CASSETTES, ledger: Path = LEDGER, backends: dict | None = None,
                 routes: dict | None = None, max_calls: int | None = None):
        self.cache_dir = Path(cache_dir)
        self.ledger = Path(ledger)
        self.routes = routes or ROUTES
        self._backends = backends  # tests inject fakes here
        self.max_calls = max_calls if max_calls is not None else int(os.environ.get("VAIOS_MAX_CALLS", "400"))
        self.session_calls = {"real": 0, "cached": 0}

    # ---------- plumbing ----------
    def backend(self, name: str, model: str):
        if self._backends is not None:
            return self._backends[name]
        return ClaudeCLI(model) if name == "claude_cli" else CodexCLI(model)

    def family(self, route: str) -> str:
        name, model = self.routes[route]
        return self.backend(name, model).family

    def _path(self, key: str) -> Path:
        return self.cache_dir / key[:2] / f"{key}.json"

    def real_calls_so_far(self) -> int:
        return sum(1 for _ in self.ledger.open()) if self.ledger.exists() else 0

    def _log(self, row: dict) -> None:
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger.open("a") as f:
            f.write(json.dumps(row) + "\n")

    # ---------- the one public call ----------
    def complete(self, route: str, system: str, prompt: str, *, tag: str = "", sample: int = 0,
                 schema: type[BaseModel] | None = None, retries: int = 3) -> LLMResult:
        name, model = self.routes[route]
        key = cache_key(backend=name, model=model, system=system, prompt=prompt, sample=sample)
        path = self._path(key)
        if path.exists():
            rec = json.loads(path.read_text())
            self.session_calls["cached"] += 1
            res = LLMResult(**{**rec["result"], "cached": True})
        else:
            if strict_replay():
                raise ReplayMiss(f"{route}/{model}: request {key[:12]} not recorded (VAIOS_STRICT_REPLAY=1)")
            if self.real_calls_so_far() >= self.max_calls:
                raise BudgetExceeded(f"LLM call budget {self.max_calls} reached (see {self.ledger})")
            raw = self._call_with_retries(self.backend(name, model), system, prompt, retries)
            res = LLMResult(text=raw.text, backend=name, model=model, cache_key=key, cached=False,
                            latency_s=raw.latency_s, input_tokens=raw.input_tokens,
                            output_tokens=raw.output_tokens, cost_usd=raw.cost_usd)
            path.parent.mkdir(parents=True, exist_ok=True)
            rec = {"request": {"route": route, "backend": name, "model": model, "system": system,
                               "prompt": prompt, "sample": sample, "tag": tag},
                   "result": {k: v for k, v in asdict(res).items() if k not in ("cached", "parsed")}}
            path.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
            self.session_calls["real"] += 1
            self._log({"ts": datetime.now(UTC).isoformat(timespec="seconds"), "route": route, "backend": name,
                       "model": model, "tag": tag, "cache_key": key, "latency_s": res.latency_s,
                       "input_tokens": res.input_tokens, "output_tokens": res.output_tokens,
                       "cost_usd": res.cost_usd})
        if schema is not None:
            res.parsed = self._validate(res, schema, route, system, prompt, tag, sample)
        return res

    def _call_with_retries(self, backend, system: str, prompt: str, retries: int) -> RawResult:
        last = ""
        for attempt in range(retries + 1):
            try:
                return backend.call(system, prompt)
            except (BackendError, OSError, TimeoutError) as e:
                last = str(e)
                time.sleep(min(120, 2 ** attempt * 5) + random.random())  # backoff with jitter
        raise BackendError(f"{backend.name} failed after {retries + 1} attempts: {last}")

    def _validate(self, res: LLMResult, schema: type[BaseModel], route: str, system: str, prompt: str,
                  tag: str, sample: int) -> dict:
        try:
            return schema.model_validate(extract_json(res.text)).model_dump()
        except (ValueError, ValidationError) as e:
            # one repair round (a second failure raises: invalid output is a job failure, not a pass): the error is shown to the model; the repair is cached like any call
            repair = (f"{prompt}\n\nYour previous answer did not validate:\n{str(e)[:800]}\n\n"
                      f"Previous answer:\n{res.text[:6000]}\n\nReturn ONLY the corrected JSON.")
            fixed = self.complete(route, system, repair, tag=f"{tag}:repair", sample=100 + sample)
            res.text, res.cache_key = fixed.text, fixed.cache_key
            return schema.model_validate(extract_json(fixed.text)).model_dump()
