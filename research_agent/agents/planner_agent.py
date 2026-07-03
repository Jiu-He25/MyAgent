"""Planner agent."""

from __future__ import annotations

from research_agent.agents.base import AgentBase
from research_agent.core.state import ResearchState


class PlannerAgent(AgentBase):
    prompt_name = "planner.md"

    def plan(self, state: ResearchState) -> dict:
        return self.complete_json(state)
