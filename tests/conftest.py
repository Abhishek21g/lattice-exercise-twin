"""Pytest fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    for name in ("relay-death-t14", "ci-golden-mesh"):
        dst = tmp_path / "examples" / "scenarios" / name
        dst.mkdir(parents=True)
        src = EXAMPLES / "scenarios" / name / "scenario.json"
        (dst / "scenario.json").write_text(src.read_text())
    plan_src = EXAMPLES / "platoon-mesh-3node.yaml"
    (tmp_path / "examples" / "platoon-mesh-3node.yaml").write_text(plan_src.read_text())
    return tmp_path


@pytest.fixture
def relay_scenario() -> dict:
    return json.loads((EXAMPLES / "scenarios" / "relay-death-t14" / "scenario.json").read_text())


@pytest.fixture
def golden_scenario() -> dict:
    return json.loads((EXAMPLES / "scenarios" / "ci-golden-mesh" / "scenario.json").read_text())


@pytest.fixture
def base_plan() -> dict:
    return {
        "name": "test-plan",
        "duration_hours": 72,
        "mesh": {
            "nodes": [
                {"id": "relay-3", "role": "relay"},
                {"id": "uav-orin-07", "role": "edge"},
                {"id": "tower-12", "role": "sensor"},
            ],
            "links": [["relay-3", "uav-orin-07"], ["relay-3", "tower-12"]],
        },
        "golden_scenario": "examples/scenarios/ci-golden-mesh",
        "max_entity_gap_hours": 0.05,
    }
