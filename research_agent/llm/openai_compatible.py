"""OpenAI-compatible LLM client."""

from __future__ import annotations

import os

from research_agent.core.config import LLMProfile
from research_agent.core.errors import ConfigError, LLMError
from research_agent.core.schemas import LLMMessage
from research_agent.llm.base import LLMClient


class OpenAICompatibleClient(LLMClient):
    def __init__(self, profile: LLMProfile) -> None:
        if not profile.api_key_env:
            raise ConfigError("LLM profile must define api_key_env")
        api_key = os.environ.get(profile.api_key_env)
        if not api_key:
            raise ConfigError(
                f"Missing API key environment variable: {profile.api_key_env}. "
                "Set it in your shell or use --fake-llm for local tests."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ConfigError(
                "The openai package is not installed. Run scripts/setup_env.sh or scripts\\setup_env.ps1 first."
            ) from exc
        self.profile = profile
        self.client = OpenAI(api_key=api_key, base_url=profile.base_url)

    def complete(self, messages: list[LLMMessage], *, response_format: str = "text") -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.profile.model,
                messages=[message.model_dump() for message in messages],
                temperature=self.profile.temperature,
                max_tokens=self.profile.max_tokens,
            )
        except Exception as exc:  # pragma: no cover - provider/network dependent
            raise LLMError(str(exc)) from exc
        content = response.choices[0].message.content
        return content or ""
