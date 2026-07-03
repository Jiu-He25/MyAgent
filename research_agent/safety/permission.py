"""Aggregate safety policy."""

from __future__ import annotations

from pathlib import Path

from research_agent.core.config import SafetyConfig
from research_agent.safety.budget import Budget
from research_agent.safety.command_filter import CommandFilter
from research_agent.safety.path_guard import PathGuard


class SafetyPolicy:
    def __init__(self, config: SafetyConfig, *, base_dir: Path | None = None) -> None:
        base = base_dir or Path.cwd()
        roots = [base / root for root in config.allowed_roots]
        self.path_guard = PathGuard(roots)
        self.command_filter = CommandFilter(config.denied_commands)
        self.budget = Budget(config.budgets)

    def validate_path(self, path: str | Path) -> Path:
        return self.path_guard.resolve_allowed(path)

    def validate_command(self, command: str, *, cwd: str | Path, timeout_seconds: int) -> None:
        self.validate_path(cwd)
        self.command_filter.validate(command)
        self.budget.validate_timeout(timeout_seconds)
