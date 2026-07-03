"""Executor interfaces."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from research_agent.core.schemas import CommandResult


class Executor(ABC):
    @abstractmethod
    def run(self, command: str, *, cwd: str | Path | None = None, timeout_seconds: int | None = None) -> CommandResult:
        """Run a command."""

    @abstractmethod
    def read_file(self, path: str | Path) -> str:
        """Read a file."""

    @abstractmethod
    def write_file(self, path: str | Path, content: str) -> None:
        """Write a file."""

    @abstractmethod
    def exists(self, path: str | Path) -> bool:
        """Return whether path exists."""

    @abstractmethod
    def list_dir(self, path: str | Path) -> list[str]:
        """List directory entries."""
