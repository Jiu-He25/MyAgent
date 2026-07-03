"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from research_agent.core.errors import ConfigError


class LLMProfile(BaseModel):
    provider: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None
    temperature: float = 0.0
    max_tokens: int = 4096


class LLMProfilesConfig(BaseModel):
    llm_profiles: dict[str, LLMProfile]


class LocalExecutionConfig(BaseModel):
    workspace_root: str = "./workspace"
    repo_path: str
    python_bin: str = "python"


class ExecutionLimits(BaseModel):
    command_timeout_seconds: int = 1800
    max_parallel_jobs: int = 1
    max_total_runtime_seconds: int = 14400


class ExecutionConfig(BaseModel):
    backend: str = "local"
    local: LocalExecutionConfig
    environment: dict[str, str] = Field(default_factory=dict)
    limits: ExecutionLimits = Field(default_factory=ExecutionLimits)


class ExecutionFile(BaseModel):
    execution: ExecutionConfig


class SafetyBudgetConfig(BaseModel):
    max_command_timeout_seconds: int = 1800
    max_experiments: int = 50
    max_total_runtime_seconds: int = 14400


class SafetyConfig(BaseModel):
    allowed_roots: list[str] = Field(default_factory=lambda: ["./workspace"])
    denied_commands: list[str] = Field(default_factory=list)
    budgets: SafetyBudgetConfig = Field(default_factory=SafetyBudgetConfig)


class SafetyFile(BaseModel):
    safety: SafetyConfig


class TaskConfig(BaseModel):
    task: dict[str, Any]
    idea: str
    project: dict[str, Any]
    experiment: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    modes: dict[str, Any] = Field(default_factory=dict)

    @property
    def task_name(self) -> str:
        return str(self.task.get("name", "research_task"))

    @property
    def repo_path(self) -> str:
        return str(self.project["repo_path"])


def load_yaml(path: str | Path) -> dict[str, Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
    except FileNotFoundError as exc:
        raise ConfigError(f"Config file not found: {path}") from exc
    if not isinstance(loaded, dict):
        raise ConfigError(f"Config file must contain a mapping: {path}")
    return loaded


def load_task_config(path: str | Path) -> TaskConfig:
    return TaskConfig.model_validate(load_yaml(path))


def load_llm_profiles(path: str | Path) -> LLMProfilesConfig:
    return LLMProfilesConfig.model_validate(load_yaml(path))


def load_execution_config(path: str | Path) -> ExecutionFile:
    return ExecutionFile.model_validate(load_yaml(path))


def load_safety_config(path: str | Path) -> SafetyFile:
    return SafetyFile.model_validate(load_yaml(path))
