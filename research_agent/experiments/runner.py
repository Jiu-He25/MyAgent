"""Experiment command runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from research_agent.core.schemas import ExperimentRecord
from research_agent.executors.local_executor import LocalExecutor
from research_agent.experiments.parser import parse_metrics


class ExperimentRunner:
    def __init__(self, executor: LocalExecutor, run_dir: Path) -> None:
        self.executor = executor
        self.run_dir = run_dir
        self.logs_dir = run_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def run_many(self, experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.executor.safety.budget.validate_experiment_count(len(experiments))
        return [self.run_one(index, experiment).model_dump() for index, experiment in enumerate(experiments)]

    def run_one(self, index: int, experiment: dict[str, Any]) -> ExperimentRecord:
        command = str(experiment["command"])
        result = self.executor.run(command)
        stem = f"experiment_{index:03d}_{experiment.get('method', 'method')}"
        stdout_path = self.logs_dir / f"{stem}.out.log"
        stderr_path = self.logs_dir / f"{stem}.err.log"
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")
        metrics = parse_metrics(self.executor.repo_path, result.stdout)
        status = "completed" if result.exit_code == 0 else "failed"
        return ExperimentRecord(
            method=str(experiment.get("method", "unknown")),
            seed=experiment.get("seed"),
            command=command,
            exit_code=result.exit_code,
            status=status,
            metrics=metrics,
            stdout_path=str(stdout_path),
            stderr_path=str(stderr_path),
        )
