"""Analyzer agent."""

from __future__ import annotations

from research_agent.agents.base import AgentBase
from research_agent.core.state import ResearchState


class AnalyzerAgent(AgentBase):
    prompt_name = "analyzer.md"

    def analyze(self, state: ResearchState) -> dict:
        return self.complete_json(state)
