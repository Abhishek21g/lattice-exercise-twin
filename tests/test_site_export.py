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
