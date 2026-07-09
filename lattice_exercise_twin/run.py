"""Run mock or live exercise probes."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from lattice_exercise_twin import __version__
from lattice_exercise_twin.paths import new_run_id, save_manifest, set_latest
from lattice_exercise_twin.plan import load_plan_by_name
from lattice_exercise_twin.schema import MANIFEST_VERSION
from lattice_exercise_twin.simulate import load_scenario, simulate_exercise


def run_exercise(
    *,
    plan_name: str | None = None,
    plan: dict[str, Any] | None = None,
    scenario: Path | None = None,
    mock: bool = True,
    run_id: str | None = None,
) -> tuple[str, dict[str, Any]]:
    if plan is None:
        if not plan_name:
            raise ValueError("plan_name or plan required")
        plan = load_plan_by_name(plan_name)

    if mock:
        if scenario is None:
            scenario = Path(plan.get("failure_scenario", "examples/scenarios/relay-death-t14"))
        scen = load_scenario(Path(scenario))
        probe = simulate_exercise(plan=plan, scenario=scen)
        probe["scenario_path"] = str(scenario)
    else:
        probe = _live_probe(plan)

    rid = run_id or new_run_id()
    manifest: dict[str, Any] = {
        "manifest_version": MANIFEST_VERSION,
        "tool_version": __version__,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_id": rid,
        "mode": "mock" if mock else "live",
        "plan": plan,
        "probe": probe,
        "doctor": None,
        "disclaimer": (
            "Mock simulation models sample-app-auto-reconnaissance entity/task flow — "
            "not a live Lattice sandbox unless --live with credentials."
        ),
    }
    save_manifest(rid, manifest)
    set_latest(rid)
    return rid, manifest


def _live_probe(plan: dict[str, Any]) -> dict[str, Any]:
    from lattice_exercise_twin.live import check_lattice_env, ping_sandbox

    env = check_lattice_env()
    ping = ping_sandbox(env)
    return {
        "live_ping": ping,
        "note": "live probe partial — use --mock for full exercise fate demo",
        "plan_name": plan.get("name"),
    }
