"""Format and export simulation results"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .simulate import STAGES
from .teams import Team


def to_sorted_rows(
    results: dict[str, dict[str, float]], teams_by_name: dict[str, Team]
) -> list[dict[str, Any]]:
    """Flatten results into rows sorted by championship probability (descendant)"""
    rows = []
    for name, probs in results.items():
        row: dict[str, Any] = {"team": name, "group": teams_by_name[name].group}
        row.update({stage: round(probs.get(stage, 0.0), 4) for stage in STAGES})
        rows.append(row)

    rows.sort(key=lambda r: r["champion"], reverse=True)
    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    fieldnames = ["team", "group"] + STAGES
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w") as f:
        json.dump(rows, f, indent=2)