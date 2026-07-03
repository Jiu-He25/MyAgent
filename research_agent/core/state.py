"""Workflow state model."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


WorkflowStatus = Literal["created", "running", "completed", "failed", "cancelled"]


class ResearchState(BaseModel):
    run_id: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-")
        + uuid4().hex[:8]
    )
    task_name: str
    idea: str
    repo_path: str
    run_dir: str
    plan: dict[str, Any] | None = None
    plan_markdown: str = ""
    code_changes: dict[str, Any] | None = None
    experiments: list[dict[str, Any]] = Field(default_factory=list)
    analysis: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    report_path: str | None = None
    status: WorkflowStatus = "created"
    step: str = "INIT"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def run_path(self) -> Path:
        return Path(self.run_dir)
