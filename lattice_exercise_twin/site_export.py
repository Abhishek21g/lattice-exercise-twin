"""Export CLI manifests to static site data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def _golden_bundle(plan: dict[str, Any]) -> dict[str, Any]:
    golden_path = plan.get("golden_scenario")
    if not golden_path:
        raise ValueError("plan missing golden_scenario")
    probe = simulate_exercise(plan=plan, scenario=load_scenario(Path(golden_path)))
    bundle = _scenario_bundle(
        scenario_id="ci-golden-mesh",
        plan=plan,
        probe=probe,
        manifest={"mode": "mock", "doctor": {"verdict": "deploy", "findings": []}},
    )
    bundle["verdict"] = "deploy"
    return bundle


def export_site(manifest: dict[str, Any], site_dir: Path | None = None) -> list[Path]:
    """Write site/data JSON from a doctored manifest. Returns paths written."""
    if not manifest.get("doctor"):
        raise ValueError("manifest must include doctor results — run doctor first")

    root = site_dir or default_site_dir()
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    plan = manifest["plan"]
    probe = manifest["probe"]
    written: list[Path] = []

    failure = _scenario_bundle(
        scenario_id="relay-death-t14",
        plan=plan,
        probe=probe,
        manifest=manifest,
    )
    failure_path = data_dir / "relay-death-t14.json"
    failure_path.write_text(json.dumps(failure, indent=2) + "\n")
    written.append(failure_path)

    golden = _golden_bundle(plan)
    golden_path = data_dir / "ci-golden-mesh.json"
    golden_path.write_text(json.dumps(golden, indent=2) + "\n")
    written.append(golden_path)

    latest = {
        "run_id": manifest.get("run_id"),
        "generated_at": manifest.get("generated_at"),
        "verdict": manifest["doctor"].get("verdict"),
        "failure_hour": probe.get("first_block_hour"),
        "scenarios": {
            "relay-death-t14": "data/relay-death-t14.json",
            "ci-golden-mesh": "data/ci-golden-mesh.json",
        },
    }
    latest_path = data_dir / "latest.json"
    latest_path.write_text(json.dumps(latest, indent=2) + "\n")
    written.append(latest_path)

    return written
