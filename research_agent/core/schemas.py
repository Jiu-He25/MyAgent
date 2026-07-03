"""Shared lightweight schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    command: str
    cwd: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0


class ExperimentRecord(BaseModel):
    method: str
    seed: int | None = None
    command: str
    exit_code: int
    status: Literal["completed", "failed", "skipped"] = "completed"
    metrics: dict[str, Any] = Field(default_factory=dict)
    stdout_path: str | None = None
    stderr_path: str | None = None


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
