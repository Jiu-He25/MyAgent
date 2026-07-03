"""LLM profile router."""

from __future__ import annotations

from research_agent.core.config import LLMProfilesConfig
from research_agent.core.errors import ConfigError
from research_agent.llm.base import FakeLLMClient, LLMClient
from research_agent.llm.openai_compatible import OpenAICompatibleClient


class LLMRouter:
    def __init__(self, config: LLMProfilesConfig, *, fake: bool = False) -> None:
        self.config = config
        self.fake = fake

    def client_for(self, profile_name: str) -> LLMClient:
        if profile_name not in self.config.llm_profiles:
            raise ConfigError(f"Unknown LLM profile: {profile_name}")
        if self.fake:
            return FakeLLMClient(profile_name)
        profile = self.config.llm_profiles[profile_name]
        if profile.provider == "openai_compatible":
            return OpenAICompatibleClient(profile)
        raise ConfigError(f"Unsupported LLM provider: {profile.provider}")
