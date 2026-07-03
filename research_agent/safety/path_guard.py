"""Path safety checks."""

from __future__ import annotations

from pathlib import Path

from research_agent.core.errors import SafetyError


class PathGuard:
    def __init__(self, allowed_roots: list[str | Path]) -> None:
        self.allowed_roots = [Path(root).resolve() for root in allowed_roots]

    def resolve_allowed(self, path: str | Path) -> Path:
        resolved = Path(path).resolve()
        if not any(resolved == root or root in resolved.parents for root in self.allowed_roots):
            roots = ", ".join(str(root) for root in self.allowed_roots)
            raise SafetyError(f"Path outside allowed roots: {resolved}. Allowed roots: {roots}")
        return resolved
