"""Mesh fate simulation engine (mock mode)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lattice_exercise_twin.schema import AUTO_RECON_RANGE_MI, INVESTIGATE_SPEC


@dataclass
class SimEvent:
    hour: float
    kind: str
    detail: str
    node_id: str | None = None


@dataclass
class SimState:
    hour: float = 0.0
    nodes_online: set[str] = field(default_factory=set)
    links_up: set[tuple[str, str]] = field(default_factory=set)
    entity_last_seen: dict[str, float] = field(default_factory=dict)
    entity_positions: dict[str, dict[str, float]] = field(default_factory=dict)
    track_dispositions: dict[str, str] = field(default_factory=dict)
    tasks_created: list[dict[str, Any]] = field(default_factory=list)
    events: list[SimEvent] = field(default_factory=list)
    stream_gaps: list[dict[str, Any]] = field(default_factory=list)


def load_scenario(path: Path) -> dict[str, Any]:
    scenario_file = path / "scenario.json"
    if not scenario_file.is_file():
        raise FileNotFoundError(f"scenario missing scenario.json: {path}")
    return json.loads(scenario_file.read_text())


def haversine_miles(a: dict[str, float], b: dict[str, float]) -> float:
    import math

    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lon"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lon"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 3958.8 * 2 * math.asin(min(1.0, math.sqrt(h)))


def _link_key(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def _path_exists(state: SimState, a: str, b: str) -> bool:
    if a not in state.nodes_online or b not in state.nodes_online:
        return False
    return _link_key(a, b) in state.links_up


def _publisher_reachable(state: SimState, publisher_node: str, consumer_node: str) -> bool:
    if publisher_node not in state.nodes_online or consumer_node not in state.nodes_online:
        return False
    if publisher_node == consumer_node:
        return True
    # BFS on mesh links
    visited = {publisher_node}
    frontier = [publisher_node]
    while frontier:
        cur = frontier.pop(0)
        for other in state.nodes_online:
            if other in visited:
                continue
            if _path_exists(state, cur, other):
                if other == consumer_node:
                    return True
                visited.add(other)
                frontier.append(other)
    return False


def simulate_exercise(
    *,
    plan: dict[str, Any],
    scenario: dict[str, Any],
    step_hours: float = 1.0,
) -> dict[str, Any]:
    mesh = plan.get("mesh") or scenario.get("mesh") or {}
    nodes = {n["id"]: n for n in mesh.get("nodes", [])}
    links = [_link_key(e[0], e[1]) for e in mesh.get("links", [])]

    state = SimState(
        nodes_online=set(nodes),
        links_up=set(links),
    )

    entities = scenario.get("entities") or []
    for ent in entities:
        eid = ent["entity_id"]
        state.entity_last_seen[eid] = 0.0
        state.entity_positions[eid] = ent.get("position", {"lat": 0, "lon": 0})
        if ent.get("template") == "TEMPLATE_TRACK":
            state.track_dispositions[eid] = ent.get("disposition", "DISPOSITION_UNKNOWN")

    timeline = sorted(scenario.get("timeline") or [], key=lambda x: x.get("at_hour", 0))
    duration = float(plan.get("duration_hours", scenario.get("duration_hours", 72)))
    asset_id = scenario.get("asset_entity_id", "asset-alpha")
    track_id = scenario.get("track_entity_id", "track-hostile-1")
    asset_node = nodes.get(scenario.get("asset_node", "uav-orin-07"), {}).get("id", "uav-orin-07")
    track_node = nodes.get(scenario.get("track_node", "tower-12"), {}).get("id", "tower-12")
    arbiter_node = scenario.get("arbiter_node", "relay-3")

    tl_idx = 0
    hour = 0.0
    first_block_hour: float | None = None
    block_reason: str | None = None

    while hour <= duration:
        while tl_idx < len(timeline) and float(timeline[tl_idx].get("at_hour", 0)) <= hour:
            ev = timeline[tl_idx]
            _apply_timeline_event(state, ev, hour)
            tl_idx += 1

        # Entity heartbeats from publishers when mesh path to arbiter exists
        for ent in entities:
            eid = ent["entity_id"]
            pub_node = ent.get("publisher_node", track_node if "track" in eid else asset_node)
            if _publisher_reachable(state, pub_node, arbiter_node):
                state.entity_last_seen[eid] = hour
            else:
                prev = state.entity_last_seen.get(eid, 0.0)
                gap_h = hour - prev
                if prev > 0 and gap_h > float(scenario.get("gap_alert_seconds", 30)) / 3600.0:
                    state.stream_gaps.append(
                        {"entity_id": eid, "gap_hours": gap_h, "at_hour": hour}
                    )

        # Auto-reconnaissance arbiter tick (mirrors sample-app logic, simplified)
        if asset_id in state.entity_positions and track_id in state.entity_positions:
            dist = haversine_miles(
                state.entity_positions[asset_id], state.entity_positions[track_id]
            )
            disp = state.track_dispositions.get(track_id, "DISPOSITION_UNKNOWN")
            hostile = disp not in ("DISPOSITION_FRIENDLY", "DISPOSITION_ASSUMED_FRIENDLY")
            in_range = dist <= float(scenario.get("range_miles", AUTO_RECON_RANGE_MI))

            asset_fresh = (hour - state.entity_last_seen.get(asset_id, 0)) * 3600 <= float(
                scenario.get("entity_stale_seconds", 120)
            )
            track_fresh = (hour - state.entity_last_seen.get(track_id, 0)) * 3600 <= float(
                scenario.get("entity_stale_seconds", 120)
            )
            mesh_ok = _publisher_reachable(state, asset_node, arbiter_node) and _publisher_reachable(
                state, track_node, arbiter_node
            )

            if in_range and hostile and mesh_ok and asset_fresh and track_fresh:
                state.tasks_created.append(
                    {
                        "at_hour": hour,
                        "task_type": INVESTIGATE_SPEC,
                        "asset_id": asset_id,
                        "track_id": track_id,
                        "status": "STATUS_EXECUTING",
                    }
                )
            elif in_range and hostile and (not mesh_ok or not track_fresh or not asset_fresh):
                if first_block_hour is None:
                    first_block_hour = hour
                    if not mesh_ok:
                        block_reason = "mesh_partition_blocks_investigate_task"
                    else:
                        block_reason = "stale_entity_blocks_investigate_task"
                state.events.append(
                    SimEvent(
                        hour=hour,
                        kind="investigate_blocked",
                        detail=block_reason or "investigate_blocked",
                        node_id=arbiter_node,
                    )
                )

        hour += step_hours

    duration_int = int(duration)
    hourly = [0] * (duration_int + 1)
    for task in state.tasks_created:
        hi = int(task["at_hour"])
        if 0 <= hi <= duration_int:
            hourly[hi] += 1

    return {
        "duration_hours": duration,
        "nodes": list(nodes.keys()),
        "timeline_applied": len(timeline),
        "tasks_created": len(state.tasks_created),
        "hourly_investigate_tasks": hourly,
        "min_investigate_tasks": scenario.get("min_investigate_tasks"),
        "stream_gaps": state.stream_gaps,
        "events": [
            {"hour": e.hour, "kind": e.kind, "detail": e.detail, "node_id": e.node_id}
            for e in state.events
        ],
        "first_block_hour": first_block_hour,
        "block_reason": block_reason,
        "final_nodes_online": sorted(state.nodes_online),
        "entity_last_seen_hours": state.entity_last_seen,
    }


def _apply_timeline_event(state: SimState, ev: dict[str, Any], hour: float) -> None:
    kind = ev.get("type", "")
    node = ev.get("node", "")
    if kind == "node_loss":
        state.nodes_online.discard(node)
        state.events.append(
            SimEvent(hour=hour, kind="node_loss", detail=f"{node} offline", node_id=node)
        )
    elif kind == "jamming":
        # drop all links touching node
        drop = {lk for lk in state.links_up if node in lk}
        state.links_up -= drop
        state.events.append(
            SimEvent(hour=hour, kind="jamming", detail=f"links via {node} degraded", node_id=node)
        )
    elif kind == "ota_drift":
        state.events.append(
            SimEvent(
                hour=hour,
                kind="ota_drift",
                detail=ev.get("detail", "plugin OTA"),
                node_id=node,
            )
        )
