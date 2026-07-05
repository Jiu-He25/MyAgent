"""Local subprocess executor."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from research_agent.core.config import ExecutionConfig
from research_agent.core.schemas import CommandResult
from research_agent.executors.base import Executor
from research_agent.safety.permission import SafetyPolicy


class LocalExecutor(Executor):
    def __init__(self, config: ExecutionConfig, safety: SafetyPolicy, *, base_dir: Path | None = None) -> None:
        self.config = config
        self.safety = safety
        self.base_dir = base_dir or Path.cwd()
        self.workspace_root = (self.base_dir / config.local.workspace_root).resolve()
        self.repo_path = (self.base_dir / config.local.repo_path).resolve()
        self.default_timeout = config.limits.command_timeout_seconds
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def run(self, command: str, *, cwd: str | Path | None = None, timeout_seconds: int | None = None) -> CommandResult:
        run_cwd = Path(cwd).resolve() if cwd else self.repo_path
        timeout = timeout_seconds or self.default_timeout
        self.safety.validate_command(command, cwd=run_cwd, timeout_seconds=timeout)
        env = os.environ.copy()
        env.update(self.config.environment)
        python_dir = str(Path(sys.executable).parent)
        env["PATH"] = os.pathsep.join([python_dir, env.get("PATH", "")])
        env.setdefault("PYTHON_BIN", self.config.local.python_bin)
        started = time.monotonic()
        proc = subprocess.run(
            command,
            cwd=run_cwd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
        )
        return CommandResult(
            command=command,
            cwd=str(run_cwd),
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_seconds=time.monotonic() - started,
        )

    def read_file(self, path: str | Path) -> str:
        allowed = self.safety.validate_path(path)
        return allowed.read_text(encoding="utf-8")

    def write_file(self, path: str | Path, content: str) -> None:
        allowed = self.safety.validate_path(path)
        allowed.parent.mkdir(parents=True, exist_ok=True)
        allowed.write_text(content, encoding="utf-8")

    def exists(self, path: str | Path) -> bool:
        return self.safety.validate_path(path).exists()

    def list_dir(self, path: str | Path) -> list[str]:
        return sorted(item.name for item in self.safety.validate_path(path).iterdir())

    def apply_patch(self, path: str | Path, content: str) -> None:
        self.write_file(path, content)
