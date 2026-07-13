"""Tests for site data export."""

from __future__ import annotations

import json

from lattice_exercise_twin.doctor import doctor_run
from lattice_exercise_twin.run import run_exercise
from lattice_exercise_twin.site_export import export_site


def test_export_site_writes_scenario_json(workspace, tmp_path):
    site = tmp_path / "site"
    (site / "data").mkdir(parents=True)

    _, manifest = run_exercise(plan_name="platoon-mesh-3node", mock=True)
    manifest = doctor_run(manifest["run_id"])

    paths = export_site(manifest, site_dir=site)
    assert len(paths) == 3

    failure = json.loads((site / "data" / "relay-death-t14.json").read_text())
    assert failure["scenario_id"] == "relay-death-t14"
    assert failure["failure_hour"] == 14
    assert failure["verdict"] == "block"
    assert len(failure["hourly_investigate_tasks"]) == 73
    assert failure["hourly_investigate_tasks"][13] == 1
    assert failure["hourly_investigate_tasks"][14] == 0

    golden = json.loads((site / "data" / "ci-golden-mesh.json").read_text())
    assert golden["verdict"] == "deploy"
    assert golden["failure_hour"] is None
    assert sum(golden["hourly_investigate_tasks"]) >= 70


def test_export_site_not_corrupted_by_golden_run(workspace, tmp_path):
    """Regression: syncing after a golden scenario run must keep relay-death BLOCK."""
    site = tmp_path / "site"
    (site / "data").mkdir(parents=True)

    _, golden_manifest = run_exercise(
        plan_name="platoon-mesh-3node",
        scenario=workspace / "examples" / "scenarios" / "ci-golden-mesh",
        mock=True,
    )
    golden_manifest = doctor_run(golden_manifest["run_id"])
    assert golden_manifest["probe"].get("first_block_hour") is None

    export_site(golden_manifest, site_dir=site)
    failure = json.loads((site / "data" / "relay-death-t14.json").read_text())
    assert failure["failure_hour"] == 14
    assert failure["verdict"] == "block"
    assert failure["tasks_total"] == 14
