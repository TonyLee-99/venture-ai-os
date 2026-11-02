"""Model backends behind the gateway. No API keys exist on this machine, so both run the vendors' headless
CLIs on a local subscription. In production each class is swapped for an API client with the same
`call(system, prompt) -> RawResult` interface; nothing above the gateway changes.
"""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from vaios.config import ROOT

SANDBOX = ROOT / ".llm_sandbox"  # empty cwd: the CLIs pick up no project instruction files or settings


@dataclass
class RawResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float | None = None
    latency_s: float = 0.0


class BackendError(RuntimeError):
    pass


class ClaudeCLI:
    family = "anthropic"

    def __init__(self, model: str = "claude-sonnet-5-5", timeout_s: float = 300):
        self.name, self.model, self.timeout_s = "claude_cli", model, timeout_s

    def call(self, system: str, prompt: str) -> RawResult:
        cmd = ["claude", "-p", prompt, "--model", self.model, "--output-format", "json",
               "--system-prompt", system, "--tools", "", "--strict-mcp-config", "--setting-sources", "",
               "--no-session-persistence", "--disable-slash-commands"]
        SANDBOX.mkdir(exist_ok=True)
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=SANDBOX, capture_output=True, text=True, timeout=self.timeout_s,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired as e:
            raise BackendError(f"claude: timeout after {self.timeout_s}s") from e
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError as e:
            raise BackendError(f"claude: non-JSON output exit={proc.returncode} {proc.stderr[:300]}") from e
        if out.get("is_error") or out.get("subtype") != "success":
            raise BackendError(f"claude: {str(out.get('result'))[:300]}")
        u = out.get("usage", {})
        return RawResult(
            text=out.get("result", ""),
            input_tokens=u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0)
            + u.get("cache_creation_input_tokens", 0),
            output_tokens=u.get("output_tokens", 0),
            cost_usd=float(out.get("total_cost_usd", 0.0)),
            latency_s=round(time.time() - t0, 2),
        )


class CodexCLI:
    family = "openai"

    def __init__(self, model: str = "gpt-6.1-sol", timeout_s: float = 600, effort: str = "medium"):
        self.name, self.model, self.timeout_s, self.effort = "codex_cli", model, timeout_s, effort

    def call(self, system: str, prompt: str) -> RawResult:
        SANDBOX.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            last = Path(tmp) / "last.txt"
            # -s read-only is mandatory: the critic may read nothing it could change.
            # The prompt goes in on stdin ("-"): with an inherited open stdin, codex waits for more input.
            cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--ephemeral",
                   "-m", self.model, "-c", f"model_reasoning_effort={self.effort}", "-C", str(SANDBOX),
                   "-o", str(last), "-"]
            t0 = time.time()
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout_s,
                                      input=f"{system}\n\n---\n\n{prompt}")
            except subprocess.TimeoutExpired as e:
                raise BackendError(f"codex: timeout after {self.timeout_s}s") from e
            latency = time.time() - t0
            if proc.returncode != 0 or not last.exists():
                raise BackendError(f"codex: exit={proc.returncode} {proc.stderr[-300:]}")
            text = last.read_text()
        # codex prints "tokens used\n12,345" at the end; it reports no dollar cost on a subscription
        m = re.search(r"tokens used\s*\n\s*([\d,]+)", proc.stdout + proc.stderr)
        total = int(m.group(1).replace(",", "")) if m else 0
        return RawResult(text=text, input_tokens=total, output_tokens=0, cost_usd=None,
                         latency_s=round(latency, 2))
