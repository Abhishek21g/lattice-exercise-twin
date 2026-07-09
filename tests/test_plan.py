from pathlib import Path

import pytest

from lattice_exercise_twin.plan import load_plan, save_plan


def test_load_plan(workspace: Path):
    plan = load_plan(workspace / "examples" / "platoon-mesh-3node.yaml")
    assert plan["name"] == "platoon-mesh-3node"


def test_invalid_plan(tmp_path: Path):
    bad = tmp_path / "x.yaml"
    bad.write_text("name: only\n")
    with pytest.raises(ValueError):
        load_plan(bad)


def test_save_plan(workspace: Path):
    plan = load_plan(workspace / "examples" / "platoon-mesh-3node.yaml")
    path = save_plan(plan)
    assert path.name == "platoon-mesh-3node.json"
