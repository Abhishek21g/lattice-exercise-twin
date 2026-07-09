"""Doctor pass."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lattice_exercise_twin.paths import load_manifest, resolve_run_id, save_manifest
from lattice_exercise_twin.simulate import load_scenario, simulate_exercise
from lattice_exercise_twin.rules import run_doctor_rules


def doctor_run(run_id: str | None = None) -> dict[str, Any]:
    rid = resolve_run_id(run_id)
    manifest = load_manifest(rid)
    plan = manifest["plan"]
    probe = manifest["probe"]

    golden_probe: dict[str, Any] | None = None
    golden_path = plan.get("golden_scenario")
    if golden_path:
        golden_scenario = load_scenario(Path(golden_path))
        golden_probe = simulate_exercise(plan=plan, scenario=golden_scenario)

    findings, verdict = run_doctor_rules(
        probe=probe,
        plan=plan,
        golden_probe=golden_probe,
    )
    manifest["doctor"] = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "findings": findings,
        "finding_count": len(findings),
        "golden_tasks": (golden_probe or {}).get("tasks_created"),
    }
    save_manifest(rid, manifest)
    return manifest
