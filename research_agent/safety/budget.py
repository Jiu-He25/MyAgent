"""Runtime budget checks."""

from __future__ import annotations

from research_agent.core.config import SafetyBudgetConfig
from research_agent.core.errors import SafetyError


class Budget:
    def __init__(self, config: SafetyBudgetConfig) -> None:
        self.config = config

    def validate_timeout(self, timeout_seconds: int) -> None:
        if timeout_seconds > self.config.max_command_timeout_seconds:
            raise SafetyError(
                f"Timeout {timeout_seconds}s exceeds budget "
                f"{self.config.max_command_timeout_seconds}s"
            )

    def validate_experiment_count(self, count: int) -> None:
        if count > self.config.max_experiments:
            raise SafetyError(f"Experiment count {count} exceeds budget {self.config.max_experiments}")
