"""Agents own jobs: a job spec (jobs/*.yaml) + a trace per run.

A trace records everything needed to replay a run: inputs, each step, for LLM steps the route, model,
cache key, prompt hash and cited doc_ids, and the output hash. It has no wall-clock timestamps on purpose,
so re-running on the same inputs (from cassettes) reproduces the trace byte for byte (`make replay`).
Latency and cost live in the gateway ledger instead.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import yaml

from vaios.config import JOBS, RESULTS
from vaios.gateway.gateway import LLMResult

TRACES = RESULTS / "traces"


def load_spec(job: str) -> dict:
    return yaml.safe_load((JOBS / f"{job}.yaml").read_text())


def sha(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()


class Trace:
    def __init__(self, job: str, entity: str, inputs: dict, as_of: str, root: Path = TRACES):
        self.spec = load_spec(job)
        self.job, self.entity, self.as_of, self.root = job, entity, as_of, root
        self.inputs = inputs
        self.run_id = sha({"job": job, "entity": entity, "inputs": inputs, "as_of": as_of})[:16]
        self.steps: list[dict] = []
        self.status = "running"

    def step(self, name: str, **info) -> None:
        self.steps.append({"step": name, **info})

    def llm(self, name: str, res: LLMResult, prompt: str, doc_ids: list[str] | None = None) -> None:
        self.steps.append({"step": name, "kind": "llm", "backend": res.backend, "model": res.model,
                           "cache_key": res.cache_key, "prompt_sha256": sha(prompt), "doc_ids": doc_ids or [],
                           "output_sha256": sha(res.text)})

    @property
    def cache_keys(self) -> list[str]:
        return [s["cache_key"] for s in self.steps if s.get("kind") == "llm"]

    def sla_violations(self) -> list[str]:
        out = []
        max_calls = self.spec.get("sla", {}).get("max_llm_calls")
        n = len(self.cache_keys)
        if max_calls is not None and n > max_calls:
            out.append(f"llm calls {n} > SLA {max_calls}")
        return out

    def save(self, status: str, outputs: dict | None = None, error: str | None = None) -> Path:
        self.status = status
        record = {"job": self.job, "agent": self.spec.get("agent"), "entity": self.entity, "run_id": self.run_id,
                  "as_of": self.as_of, "status": status, "inputs": self.inputs, "steps": self.steps,
                  "outputs": outputs or {}, "error": error, "sla_violations": self.sla_violations()}
        path = self.root / self.job / f"{self.entity}.json"  # one file per (job, entity): reruns overwrite
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=1, ensure_ascii=False, default=str) + "\n")
        return path
