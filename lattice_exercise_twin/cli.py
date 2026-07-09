"""CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from lattice_exercise_twin.doctor import doctor_run
from lattice_exercise_twin.live import check_lattice_env, missing_env
from lattice_exercise_twin.paths import resolve_run_id, run_dir
from lattice_exercise_twin.plan import load_plan, save_plan
from lattice_exercise_twin.report import write_report
from lattice_exercise_twin.run import run_exercise


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lattice-exercise-twin",
        description="Plan, run, doctor, and report Lattice mesh exercise fate.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Load exercise plan YAML")
    plan.add_argument("config", type=Path)
    plan.set_defaults(handler=_cmd_plan)

    run = sub.add_parser("run", help="Simulate exercise (mock default)")
    run.add_argument("--plan", type=str, default="platoon-mesh-3node")
    run.add_argument("--scenario", type=Path, default=None)
    run.add_argument("--live", action="store_true")
    run.set_defaults(handler=_cmd_run)

    doc = sub.add_parser("doctor", help="Evaluate exercise fate rules")
    doc.add_argument("run_id", nargs="?", default="latest")
    doc.add_argument("--json", action="store_true")
    doc.set_defaults(handler=_cmd_doctor)

    rep = sub.add_parser("report", help="Write summary.md and optional HTML")
    rep.add_argument("run_id", nargs="?", default="latest")
    rep.add_argument("--html", action="store_true")
    rep.set_defaults(handler=_cmd_report)

    chk = sub.add_parser("check-env", help="Verify Lattice sandbox env vars")
    chk.set_defaults(handler=_cmd_check_env)

    return p


def _cmd_plan(args: argparse.Namespace) -> int:
    plan = load_plan(args.config)
    path = save_plan(plan)
    print(f"saved plan → {path}")
    print(f"  name: {plan['name']}  duration: {plan['duration_hours']}h")
    print(f"  nodes: {len(plan['mesh']['nodes'])}")
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    rid, manifest = run_exercise(
        plan_name=args.plan,
        scenario=args.scenario,
        mock=not args.live,
    )
    probe = manifest["probe"]
    print(f"run_id: {rid}")
    print(f"mode: {manifest['mode']}")
    if probe.get("first_block_hour") is not None:
        print(f"first_block: T+{probe['first_block_hour']}h ({probe.get('block_reason')})")
    print(f"investigate_tasks: {probe.get('tasks_created', 0)}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    manifest = doctor_run(args.run_id)
    doc = manifest["doctor"]
    print(f"verdict: {doc['verdict']}")
    for f in doc["findings"]:
        mark = {"critical": "✗", "warning": "!", "info": "·"}[f["severity"]]
        print(f"  [{mark}] {f['title']}")
    if args.json:
        print(json.dumps(doc, indent=2))
    return 0 if doc["verdict"] == "deploy" else 1


def _cmd_report(args: argparse.Namespace) -> int:
    rid = resolve_run_id(args.run_id)
    from lattice_exercise_twin.paths import load_manifest

    manifest = load_manifest(rid)
    if not manifest.get("doctor"):
        manifest = doctor_run(rid)
    for path in write_report(manifest, run_dir(rid), html_out=args.html):
        print(f"wrote {path}")
    return 0


def _cmd_check_env(args: argparse.Namespace) -> int:
    env = check_lattice_env()
    miss = missing_env(env)
    if miss:
        print("missing:", ", ".join(miss))
        print("see docs/LATTICE_SANDBOX_SETUP.md")
        return 1
    print(f"LATTICE_ENDPOINT={env['LATTICE_ENDPOINT']}")
    print("sandbox token:", "set" if env.get("SANDBOXES_TOKEN") else "optional/missing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
