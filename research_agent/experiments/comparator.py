"""Simple result comparison helpers."""

from __future__ import annotations

from typing import Any


def best_by_metric(records: list[dict[str, Any]], metric: str = "val_accuracy") -> dict[str, Any] | None:
    scored = [record for record in records if metric in record.get("metrics", {})]
    if not scored:
        return None
    return max(scored, key=lambda record: float(record["metrics"][metric]))
