"""Stage 1 research workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from research_agent.agents.analyzer_agent import AnalyzerAgent
from research_agent.agents.coder_agent import CoderAgent
from research_agent.agents.planner_agent import PlannerAgent
from research_agent.agents.reporter_agent import ReporterAgent
from research_agent.agents.reviewer_agent import ReviewerAgent
from research_agent.core.config import ExecutionConfig, TaskConfig
from research_agent.core.events import Event, EventLog
from research_agent.core.logger import setup_run_logger
from research_agent.core.state import ResearchState
from research_agent.executors.local_executor import LocalExecutor
from research_agent.experiments.artifact_manager import ArtifactManager
from research_agent.experiments.manager import ExperimentManager
from research_agent.llm.router import LLMRouter


ApprovalCallback = Callable[[dict, str], bool]


class ResearchWorkflow:
    def __init__(
        self,
        *,
        task_config: TaskConfig,
        execution_config: ExecutionConfig,
        llm_router: LLMRouter,
        executor: LocalExecutor,
        base_dir: Path | None = None,
        auto_approve: bool = False,
        approval_callback: ApprovalCallback | None = None,
    ) -> None:
        self.task_config = task_config
        self.execution_config = execution_config
        self.llm_router = llm_router
        self.executor = executor
        self.base_dir = base_dir or Path.cwd()
        self.auto_approve = auto_approve
        self.approval_callback = approval_callback

    def run(self) -> ResearchState:
        run_root = (self.base_dir / self.execution_config.local.workspace_root / "runs").resolve()
        state = ResearchState(
            task_name=self.task_config.task_name,
            idea=self.task_config.idea,
            repo_path=str((self.base_dir / self.task_config.repo_path).resolve()),
            run_dir=str(run_root / ResearchState.model_fields["run_id"].default_factory()),
        )
        run_dir = Path(state.run_dir)
        artifacts = ArtifactManager(run_dir)
        events = EventLog(run_dir / "logs" / "events.jsonl")
        logger = setup_run_logger(run_dir)
        state.status = "running"
        self._save_state(artifacts, state)

        self._step(state, "SCAN_REPO", events, logger)
        self.executor.repo_path.mkdir(parents=True, exist_ok=True)
        repo_summary = {"repo_path": str(self.executor.repo_path), "files": self.executor.list_dir(self.executor.repo_path)}
        artifacts.write_json("artifacts/repo_summary.json", repo_summary)

        self._step(state, "PLAN", events, logger)
        planner = PlannerAgent(self.llm_router.client_for("planner"))
        state.plan = planner.plan(state)
        state.plan_markdown = self._plan_markdown(state.plan)
        artifacts.write_json("plans/plan.json", state.plan)
        artifacts.write_text("plans/plan.md", state.plan_markdown)
        self._save_state(artifacts, state)

        self._step(state, "PLAN_APPROVAL", events, logger)
        if not self._approved(state.plan, state.plan_markdown):
            state.status = "cancelled"
            self._save_state(artifacts, state)
            return state

        self._step(state, "IMPLEMENT", events, logger)
        coder = CoderAgent(self.llm_router.client_for("coder"))
        state.code_changes = coder.implement(state)
        self._apply_code_changes(state.code_changes)
        artifacts.write_json("artifacts/code_changes.json", state.code_changes)
        self._save_state(artifacts, state)

        self._step(state, "RUN_EXPERIMENTS", events, logger)
        experiments = list((state.plan or {}).get("experiments", []))
        state.experiments = ExperimentManager(self.executor, run_dir).run(experiments)
        artifacts.write_json("artifacts/experiments.json", state.experiments)
        self._save_state(artifacts, state)

        self._step(state, "ANALYZE", events, logger)
        state.analysis = AnalyzerAgent(self.llm_router.client_for("analyzer")).analyze(state)
        artifacts.write_json("artifacts/analysis.json", state.analysis)

        self._step(state, "REVIEW", events, logger)
        state.review = ReviewerAgent(self.llm_router.client_for("reviewer")).review(state)
        artifacts.write_json("artifacts/review.json", state.review)

        self._step(state, "REPORT", events, logger)
        state.report_path = ReporterAgent(self.llm_router.client_for("reporter")).report(state)
        state.status = "completed"
        self._save_state(artifacts, state)
        return state

    def _approved(self, plan: dict | None, plan_markdown: str) -> bool:
        if self.auto_approve:
            return True
        if self.approval_callback:
            return self.approval_callback(plan or {}, plan_markdown)
        return False

    def _apply_code_changes(self, changes: dict | None) -> None:
        for file_spec in (changes or {}).get("files", []):
            relative_path = str(file_spec["path"])
            if Path(relative_path).is_absolute():
                target = Path(relative_path)
            else:
                target = self.executor.repo_path / relative_path
            self.executor.write_file(target, str(file_spec.get("content", "")))

    def _plan_markdown(self, plan: dict | None) -> str:
        if not plan:
            return "# Plan\n\nNo plan generated.\n"
        lines = ["# Plan", "", str(plan.get("summary", "Experiment plan")), ""]
        for item in plan.get("experiments", []):
            lines.append(f"- `{item.get('command')}`")
        return "\n".join(lines) + "\n"

    def _step(self, state: ResearchState, step: str, events: EventLog, logger) -> None:
        state.step = step
        logger.info("Entering step %s", step)
        events.append(Event(type="step", message=f"Entering {step}", step=step))

    def _save_state(self, artifacts: ArtifactManager, state: ResearchState) -> None:
        artifacts.write_json("state.json", json.loads(state.model_dump_json()))
