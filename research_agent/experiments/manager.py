"""Experiment manager facade."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from research_agent.executors.local_executor import LocalExecutor
from research_agent.experiments.runner import ExperimentRunner


class ExperimentManager:
    def __init__(self, executor: LocalExecutor, run_dir: Path) -> None:
        self.runner = ExperimentRunner(executor, run_dir)

    def run(self, experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return self.runner.run_many(experiments)
