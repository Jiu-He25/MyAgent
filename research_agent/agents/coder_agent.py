"""Coder agent."""

from __future__ import annotations

from research_agent.agents.base import AgentBase
from research_agent.core.state import ResearchState


class CoderAgent(AgentBase):
    prompt_name = "coder.md"

    def implement(self, state: ResearchState) -> dict:
        return self.complete_json(state)
