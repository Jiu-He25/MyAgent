"""Command deny-list checks."""

from __future__ import annotations

import shlex

from research_agent.core.errors import SafetyError


class CommandFilter:
    def __init__(self, denied_commands: list[str]) -> None:
        self.denied_commands = [item.lower() for item in denied_commands]

    def validate(self, command: str) -> None:
        normalized = " ".join(command.lower().split())
        try:
            parts = [part.lower() for part in shlex.split(command, posix=False)]
        except ValueError:
            parts = normalized.split()
        for denied in self.denied_commands:
            if denied in normalized or (parts and parts[0] == denied):
                raise SafetyError(f"Command denied by safety policy: {denied}")
