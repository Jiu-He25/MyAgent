"""Reporter agent."""

from __future__ import annotations

from pathlib import Path

from research_agent.agents.base import AgentBase
from research_agent.core.state import ResearchState


class ReporterAgent(AgentBase):
    prompt_name = "reporter.md"

    def report(self, state: ResearchState) -> str:
        report_dir = Path(state.run_dir) / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "experiment_report.md"
        text = self.llm.complete(self.messages(state), response_format="markdown")
        if not text.strip():
            text = "# Experiment Report\n\nNo report content was generated.\n"
        report_path.write_text(text, encoding="utf-8")
        return str(report_path)
