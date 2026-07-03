"""Base agent helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_agent.core.schemas import LLMMessage
from research_agent.core.state import ResearchState
from research_agent.llm.base import LLMClient


class AgentBase:
    prompt_name = ""

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def prompt(self) -> str:
        path = Path(__file__).parents[1] / "llm" / "prompts" / self.prompt_name
        return path.read_text(encoding="utf-8")

    def messages(self, state: ResearchState, extra: dict[str, Any] | None = None) -> list[LLMMessage]:
        payload = state.model_dump(mode="json")
        if extra:
            payload.update(extra)
        return [
            LLMMessage(role="system", content=self.prompt()),
            LLMMessage(role="user", content=json.dumps(payload, ensure_ascii=False)),
        ]

    def complete_json(self, state: ResearchState, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        text = self.llm.complete(self.messages(state, extra), response_format="json")
        try:
            loaded = json.loads(text)
        except json.JSONDecodeError:
            loaded = {"summary": text}
        return loaded if isinstance(loaded, dict) else {"value": loaded}
