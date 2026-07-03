"""Metric parsing utilities."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


def parse_metrics(repo_path: Path, stdout: str = "") -> dict[str, Any]:
    json_path = repo_path / "metrics.json"
    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))
    csv_path = repo_path / "metrics.csv"
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        return rows[-1] if rows else {}
    metrics: dict[str, Any] = {}
    for key, value in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=([-+]?\d+(?:\.\d+)?)", stdout):
        metrics[key] = float(value)
    return metrics
