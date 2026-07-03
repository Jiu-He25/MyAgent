"""Reviewer agent."""

from __future__ import annotations

from research_agent.agents.base import AgentBase
from research_agent.core.state import ResearchState


class ReviewerAgent(AgentBase):
    prompt_name = "reviewer.md"

    def review(self, state: ResearchState) -> dict:
        return self.complete_json(state)
