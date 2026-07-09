"""Artifact paths."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "out"
PLANS_DIR = OUT / "plans"
RECEIPTS_DIR = OUT / "receipts"
LATEST_FILE = OUT / "latest_run.txt"


def ensure_out() -> None:
    PLANS_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)


def new_run_id() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"run_{ts}"


def run_dir(run_id: str) -> Path:
    return RECEIPTS_DIR / run_id


def resolve_run_id(run_id: str | None) -> str:
    if run_id and run_id != "latest":
        return run_id
    if LATEST_FILE.is_file():
        return LATEST_FILE.read_text().strip()
    runs = sorted(RECEIPTS_DIR.glob("run_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise FileNotFoundError("no runs — run `lattice-exercise-twin run` first")
    return runs[0].name


def set_latest(run_id: str) -> None:
    ensure_out()
    LATEST_FILE.write_text(run_id + "\n")


def load_manifest(run_id: str) -> dict:
    path = run_dir(run_id) / "manifest.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def save_manifest(run_id: str, data: dict) -> Path:
    d = run_dir(run_id)
    d.mkdir(parents=True, exist_ok=True)
    path = d / "manifest.json"
    path.write_text(json.dumps(data, indent=2) + "\n")
    return path
