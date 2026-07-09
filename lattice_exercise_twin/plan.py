"""Exercise plan load/save."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from lattice_exercise_twin.paths import PLANS_DIR, ensure_out


def load_plan(path: Path) -> dict[str, Any]:
    text = path.read_text()
    data = yaml.safe_load(text) if path.suffix != ".json" else json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"plan must be a mapping: {path}")
    _validate(data)
    return data


def _validate(plan: dict[str, Any]) -> None:
    required = ("name", "duration_hours", "mesh")
    missing = [k for k in required if k not in plan]
    if missing:
        raise ValueError(f"plan missing keys: {missing}")
    if not plan.get("mesh", {}).get("nodes"):
        raise ValueError("plan.mesh.nodes required")


def save_plan(plan: dict[str, Any]) -> Path:
    ensure_out()
    path = PLANS_DIR / f"{plan['name']}.json"
    path.write_text(json.dumps(plan, indent=2) + "\n")
    return path


def load_plan_by_name(name: str) -> dict[str, Any]:
    path = PLANS_DIR / f"{name}.json"
    if not path.is_file():
        raise FileNotFoundError(f"plan not found: {path} — run `plan` first")
    return json.loads(path.read_text())
