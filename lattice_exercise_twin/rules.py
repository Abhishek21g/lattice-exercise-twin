"""Doctor rules for mesh exercise fate."""

from __future__ import annotations

from typing import Any, Literal

Severity = Literal["critical", "warning", "info"]
Verdict = Literal["deploy", "review", "block"]


def _finding(
    rule_id: str,
    severity: Severity,
    title: str,
    detail: str,
    remediation: str = "",
) -> dict[str, str]:
    return {
        "id": rule_id,
        "severity": severity,
        "title": title,
        "detail": detail,
        "remediation": remediation,
    }


def check_exercise_block(probe: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    bh = probe.get("first_block_hour")
    if bh is not None:
        out.append(
            _finding(
                "exercise:mission_block",
                "critical",
                f"Exercise mission flow blocked at T+{bh}h",
                probe.get("block_reason", "investigate path failed"),
                "Rehearse mesh failover before live exercise; restore relay path or edge cache policy.",
            )
        )
    return out


def check_stream_gaps(probe: dict[str, Any], max_gap_hours: float) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for gap in probe.get("stream_gaps") or []:
        gh = float(gap.get("gap_hours", 0))
        if gh > max_gap_hours:
            out.append(
                _finding(
                    f"stream:gap:{gap.get('entity_id')}",
                    "critical",
                    f"Entity stream gap {gh:.1f}h on {gap.get('entity_id')}",
                    "Lattice entity long-poll consumers saw stale track/asset — fusion desync risk.",
                    "Add stream gap alerting; block OTA during active Investigate tasks.",
                )
            )
    return out


def check_task_creation(probe: dict[str, Any], golden: dict[str, Any] | None) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    created = int(probe.get("tasks_created", 0))
    if golden:
        expected = int(golden.get("min_investigate_tasks") or golden.get("tasks_created") or 1)
        if created < expected and probe.get("first_block_hour") is not None:
            out.append(
                _finding(
                    "tasks:investigate_missing",
                    "critical",
                    f"Only {created} Investigate tasks (expected ≥{expected})",
                    "Auto-reconnaissance arbiter could not assign Tasks API work.",
                    "Validate entity stream + mesh path to arbiter node before exercise.",
                )
            )
    elif created == 0:
        out.append(
            _finding(
                "tasks:none",
                "warning",
                "No Investigate tasks created during simulation",
                "Check asset/track range and disposition fixtures.",
            )
        )
    return out


def check_timeline_events(probe: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for ev in probe.get("events") or []:
        if ev.get("kind") == "node_loss":
            out.append(
                _finding(
                    f"mesh:node_loss:{ev.get('node_id')}",
                    "warning",
                    f"Node loss at T+{ev.get('hour')}h",
                    ev.get("detail", ""),
                )
            )
    return out


def run_doctor_rules(
    *,
    probe: dict[str, Any],
    plan: dict[str, Any],
    golden_probe: dict[str, Any] | None,
) -> tuple[list[dict[str, str]], Verdict]:
    findings: list[dict[str, str]] = []
    max_gap_h = float(plan.get("max_entity_gap_hours", 0.05))  # ~3 min default
    findings.extend(check_exercise_block(probe))
    findings.extend(check_stream_gaps(probe, max_gap_h))
    findings.extend(check_task_creation(probe, golden_probe))
    findings.extend(check_timeline_events(probe))

    findings = _dedupe(findings)
    if any(f["severity"] == "critical" for f in findings):
        return findings, "block"
    if findings:
        return findings, "review"
    return findings, "deploy"


def _dedupe(findings: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for f in findings:
        if f["id"] in seen:
            continue
        seen.add(f["id"])
        out.append(f)
    return out
