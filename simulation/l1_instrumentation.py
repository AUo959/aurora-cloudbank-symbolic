#!/usr/bin/env python3
"""Evidence-bound sensor and schematic projections for a governed L1 run."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from l1_runtime_support import read_json
from l1_runtime_types import L1RunState
from src.sensors.internal import L1RuntimeSensor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAFF_REGISTRY_PATH = PROJECT_ROOT / "ORION_STATION_CANONICAL_STAFF_REGISTRY.json"


def build_sensor_snapshot(state: L1RunState) -> Dict[str, Any]:
    """Return actual run-ledger telemetry and disclose unavailable channels."""
    reading = L1RuntimeSensor(_provider(state)).read()
    return {
        "source": "persisted_run_ledger",
        "run_id": state.manifest.run_id,
        "live_within_simulation": True,
        "physical_hardware_feed": False,
        "reading": {
            "sensor_id": reading.sensor_id,
            "timestamp": reading.timestamp.isoformat(),
            "layer": reading.layer,
            "category": reading.category,
            "values": reading.values,
            "units": {name: unit.value for name, unit in reading.units.items()},
            "alerts": reading.alerts,
            **reading.metadata,
        },
        "unavailable_physical_channels": [
            "environmental",
            "structural_hull",
            "crew_biometrics",
            "proximity",
            "astronomical",
        ],
        "unavailable_channel_policy": (
            "unbound physical channels remain unavailable; provider metadata "
            "identifies any default-filled metrics in this snapshot"
        ),
    }


def build_logical_schematic(
    state: L1RunState,
    baseline: Dict[str, Any],
) -> Dict[str, Any]:
    """Project only causal-safe topology; quarantine stale physical layouts."""
    command_endpoint = _command_endpoint()
    latency = baseline["orbital_locus"]["communications_latency"]
    return {
        "status": "runtime_projection_non_authoritative",
        "run_id": state.manifest.run_id,
        "station": {
            "name": state.world_state["station"],
            "siting_class": state.world_state["orbital_locus"]["siting_class"],
            "exact_point_resolved": False,
        },
        "pilot": state.world_state["pilot"],
        "command_endpoint": command_endpoint,
        "topology": {
            "nodes": _schematic_nodes(command_endpoint, latency),
            "links": _schematic_links(command_endpoint, latency),
        },
        "physical_deck_layout": {
            "status": "unresolved",
            "reason": (
                "available deck-layout artifacts contain stale locus, population, "
                "or Pilot-embodiment assumptions and are reference-only"
            ),
            "causal_use_permitted": False,
        },
    }


def _schematic_nodes(
    command_endpoint: Dict[str, str],
    latency: Dict[str, Any],
) -> list[Dict[str, Any]]:
    return [
        {"id": "pilot", "location": "Earth", "layer": "control_plane"},
        {
            "id": "earth_orion_link",
            "type": "communications_boundary",
            "latency_certainty": latency["certainty"],
        },
        {
            "id": "orion_station",
            "location": "lagrange_point_exact_point_unresolved",
            "layer": "L1",
        },
        {
            "id": command_endpoint["id"],
            "location": "orion_station_exact_compartment_unresolved",
            "layer": "L1",
        },
        {
            "id": "character_actor:CMD_001",
            "type": "bounded_character_action",
            "policy": "bounded_character_action_v1",
            "knowledge_scope": "station_records_plus_actor_knowledge",
        },
        {
            "id": "internal.l1_runtime",
            "type": "read_only_instrumentation",
            "source": "persisted_run_ledger",
        },
    ]


def _schematic_links(
    command_endpoint: Dict[str, str],
    latency: Dict[str, Any],
) -> list[Dict[str, Any]]:
    return [
        {
            "from": "pilot",
            "to": "orion_station",
            "type": "explicit_communications",
            "modeled_one_way_seconds": latency["modeled_one_way_light_time_seconds"],
            "certainty": latency["certainty"],
        },
        {
            "from": "orion_station",
            "to": command_endpoint["id"],
            "type": "station_routing",
        },
        {
            "from": command_endpoint["id"],
            "to": "character_actor:CMD_001",
            "type": "canon_profile_plus_local_knowledge",
        },
        {
            "from": "orion_station",
            "to": "internal.l1_runtime",
            "type": "one_way_observation",
        },
    ]


def _provider(state: L1RunState):
    def read_state() -> Dict[str, float]:
        communications = state.communications
        return {
            "tick": float(state.manifest.tick),
            "station_cycle_minute": float(state.manifest.station_cycle_minute),
            "event_count": float(len(state.events)),
            "queued_communication_count": float(
                sum(item.get("status") == "queued" for item in communications)
            ),
            "delivered_communication_count": float(
                sum(
                    str(item.get("status", "")).startswith("delivered_")
                    for item in communications
                )
            ),
            "station_response_count": float(
                sum(
                    item.get("direction") == "station_to_earth"
                    for item in communications
                )
            ),
            "character_action_count": float(len(state.character_actions)),
        }

    return read_state


def _command_endpoint() -> Dict[str, str]:
    registry = read_json(STAFF_REGISTRY_PATH)
    matches = [
        item for item in registry.get("human_staff", []) if item.get("id") == "CMD_001"
    ]
    if len(matches) != 1:
        raise RuntimeError("staff registry does not contain one CMD_001 endpoint")
    command = matches[0]
    return {
        "id": command["id"],
        "name": command["name"],
        "role": command["role"],
    }
