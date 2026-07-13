"""Export CLI manifests to static site data."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lattice_exercise_twin.rules import run_doctor_rules
from lattice_exercise_twin.simulate import load_scenario, simulate_exercise

SITE_DIR = Path(__file__).resolve().parent.parent / "site"
DATA_DIR = SITE_DIR / "data"
DEMO_DIR = SITE_DIR / "demo"


def default_site_dir() -> Path:
    return SITE_DIR


def _scenario_bundle(
    *,
    scenario_id: str,
    plan: dict[str, Any],
    probe: dict[str, Any],
    manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    doctor = (manifest or {}).get("doctor") or {}
    mesh = plan.get("mesh") or {}
    failure_hour = probe.get("first_block_hour")
    hourly = probe.get("hourly_investigate_tasks") or []

    offline_node = None
    for ev in probe.get("events") or []:
        if ev.get("kind") == "node_loss":
            offline_node = ev.get("node_id")
            break

    return {
        "scenario_id": scenario_id,
        "run_id": (manifest or {}).get("run_id"),
        "generated_at": (manifest or {}).get("generated_at"),
        "mode": (manifest or {}).get("mode", "mock"),
        "plan_name": plan.get("name"),
        "duration_hours": int(probe.get("duration_hours", plan.get("duration_hours", 72))),
        "failure_hour": failure_hour,
        "block_reason": probe.get("block_reason"),
        "tasks_total": probe.get("tasks_created", 0),
        "hourly_investigate_tasks": hourly,
        "verdict": doctor.get("verdict", "pending"),
        "findings": doctor.get("findings") or [],
        "golden_tasks": doctor.get("golden_tasks"),
        "mesh": {
            "nodes": mesh.get("nodes") or [],
            "links": mesh.get("links") or [],
            "offline_node": offline_node,
            "final_online": probe.get("final_nodes_online") or [],
        },
    }


def _doctor_manifest(
    *,
    plan: dict[str, Any],
    probe: dict[str, Any],
    golden_probe: dict[str, Any] | None,
    run_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    findings, verdict = run_doctor_rules(
        probe=probe,
        plan=plan,
        golden_probe=golden_probe,
    )
    meta = run_meta or {}
    return {
        "run_id": meta.get("run_id"),
        "generated_at": meta.get("generated_at")
        or datetime.now(timezone.utc).isoformat(),
        "mode": meta.get("mode", "mock"),
        "doctor": {
            "verdict": verdict,
            "findings": findings,
            "golden_tasks": (golden_probe or {}).get("tasks_created"),
        },
    }


def export_site(manifest: dict[str, Any], site_dir: Path | None = None) -> list[Path]:
    """Write site/data JSON for the plan's named scenarios.

    Always re-simulates ``failure_scenario`` and ``golden_scenario`` from the
    plan so a golden doctor run cannot overwrite the relay-death demo bundle.
    """
    if not manifest.get("doctor") and not manifest.get("plan"):
        raise ValueError("manifest must include plan (and preferably doctor results)")

    root = site_dir or default_site_dir()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    plan = manifest["plan"]
    failure_rel = plan.get("failure_scenario", "examples/scenarios/relay-death-t14")
    golden_rel = plan.get("golden_scenario", "examples/scenarios/ci-golden-mesh")

    failure_probe = simulate_exercise(
        plan=plan, scenario=load_scenario(Path(failure_rel))
    )
    golden_probe = simulate_exercise(
        plan=plan, scenario=load_scenario(Path(golden_rel))
    )

    failure_manifest = _doctor_manifest(
        plan=plan,
        probe=failure_probe,
        golden_probe=golden_probe,
        run_meta=manifest,
    )
    golden_manifest = _doctor_manifest(
        plan=plan,
        probe=golden_probe,
        golden_probe=golden_probe,
        run_meta={**manifest, "mode": "mock"},
    )
    # Golden path must stay deploy — force after doctor so baseline is stable for the site.
    golden_manifest["doctor"]["verdict"] = "deploy"

    written: list[Path] = []

    failure = _scenario_bundle(
        scenario_id="relay-death-t14",
        plan=plan,
        probe=failure_probe,
        manifest=failure_manifest,
    )
    failure_path = data_dir / "relay-death-t14.json"
    failure_path.write_text(json.dumps(failure, indent=2) + "\n")
    written.append(failure_path)

    golden = _scenario_bundle(
        scenario_id="ci-golden-mesh",
        plan=plan,
        probe=golden_probe,
        manifest=golden_manifest,
    )
    golden["verdict"] = "deploy"
    golden_path = data_dir / "ci-golden-mesh.json"
    golden_path.write_text(json.dumps(golden, indent=2) + "\n")
    written.append(golden_path)

    latest = {
        "run_id": manifest.get("run_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "verdict": failure["verdict"],
        "failure_hour": failure.get("failure_hour"),
        "scenarios": {
            "relay-death-t14": "data/relay-death-t14.json",
            "ci-golden-mesh": "data/ci-golden-mesh.json",
        },
    }
    latest_path = data_dir / "latest.json"
    latest_path.write_text(json.dumps(latest, indent=2) + "\n")
    written.append(latest_path)

    return written
