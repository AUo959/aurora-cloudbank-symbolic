#!/usr/bin/env python3
"""Authority-safe fleet projection and deterministic L1 world process."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List

from l1_runtime_support import GovernanceError
from l1_runtime_types import (
    FleetEntityProvenance,
    FleetEntityState,
    FleetRunState,
    GovernanceReceipt,
    L1RunState,
)
from modules.ord.ord_policy_engine import DispatchOrder, DroneType


DRONE_ID_BY_POLICY_TYPE = {
    DroneType.GAMMA_SWARM: "ORD-1",
    DroneType.DELTA_SCOUT: "ORD-2",
    DroneType.WISP: "ORD-4",
}
SHADOWFAX_FLEET_ID = "ORD-3"
ORD_ADAPTER_ID = "ord_to_l1_physical_mission_v1"
ORD_POLICY_DOMAIN = "mcp_validation"
ORD_PHYSICAL_LOCATIONS = {
    "station_proximity",
    "external_operating_area",
    "assigned_host_vessel",
}


def build_initial_fleet_state(receipt: Dict[str, Any]) -> FleetRunState:
    """Build identity-only genesis state without importing dated mission truth."""
    if not isinstance(receipt, dict):
        raise ValueError("fleet receipt must be an object")
    projection = receipt.get("cloudbank_projection")
    if not isinstance(projection, dict):
        raise ValueError("fleet receipt projection must be an object")
    receipt_id = receipt.get("receipt_id")
    if projection.get("role") != "runtime_projection_non_authoritative":
        raise ValueError("fleet receipt does not define a non-authoritative projection")
    if not isinstance(receipt_id, str) or not receipt_id:
        raise ValueError("fleet receipt_id must be a non-empty string")
    if (
        projection.get("historical_mission_policy")
        != "provenance_only_never_current_run_truth"
    ):
        raise ValueError("fleet receipt does not quarantine historical mission state")

    entities: Dict[str, FleetEntityState] = {}
    for entry in _receipt_entities(receipt):
        entity = _entity_from_receipt(entry, receipt_id, projection["role"])
        if entity.fleet_id in entities:
            raise ValueError(f"duplicate fleet identity: {entity.fleet_id}")
        entities[entity.fleet_id] = entity
    if not entities:
        raise ValueError("fleet receipt contains no projected entities")

    fleet = FleetRunState(
        provider_status="bound",
        authority_receipt_id=receipt_id,
        projection_role=projection["role"],
        process_position=0,
        elapsed_minutes=0,
        entities=entities,
    )
    fleet.validate()
    validate_fleet_identity_projection(fleet, receipt)
    return fleet


def _receipt_entities(receipt: Dict[str, Any]) -> list[Dict[str, Any]]:
    entries = receipt.get("entities")
    if not isinstance(entries, list) or not all(
        isinstance(entry, dict) for entry in entries
    ):
        raise ValueError("fleet receipt entities must be a list of objects")
    return entries


def expected_fleet_ids(receipt: Dict[str, Any]) -> frozenset[str]:
    """Return the exact identity set projected by the authority receipt."""
    identifiers = []
    for entry in _receipt_entities(receipt):
        fleet_id = entry.get("fleet_id")
        if not isinstance(fleet_id, str) or not fleet_id:
            raise ValueError("fleet receipt identity must be a non-empty string")
        identifiers.append(fleet_id)
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("fleet receipt identities are duplicated")
    return frozenset(identifiers)


def validate_fleet_identity_projection(
    fleet: FleetRunState,
    receipt: Dict[str, Any],
) -> None:
    """Fail closed if bound run state omits or invents projected fleet identities."""
    if fleet.provider_status != "bound":
        raise ValueError("fleet identity projection requires a bound provider")
    expected = expected_fleet_ids(receipt)
    actual = frozenset(fleet.entities)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            "bound fleet identities do not match authority receipt "
            f"(missing={missing}, extra={extra})"
        )


def _entity_from_receipt(
    entry: Dict[str, Any],
    receipt_id: str,
    projection_role: str,
) -> FleetEntityState:
    if not isinstance(entry, dict):
        raise ValueError("fleet receipt entity must be an object")
    required = (
        "fleet_id",
        "display_name",
        "asset_class",
        "autonomy_class",
        "design_source_path",
        "implementation_source_path",
        "routine_mission_class",
        "operating_location_class",
        "standby_location_class",
    )
    if any(
        not isinstance(entry.get(field), str) or not entry[field]
        for field in required
    ):
        raise ValueError("fleet receipt entity fields must be non-empty strings")
    entity = FleetEntityState(
        fleet_id=entry["fleet_id"],
        display_name=entry["display_name"],
        asset_class=entry["asset_class"],
        autonomy_class=entry["autonomy_class"],
        status="identity_projected",
        mission_state_class="unassigned",
        docking_location_class="unresolved",
        provenance=FleetEntityProvenance(
            authority_receipt_id=receipt_id,
            projection_role=projection_role,
            identity_source_path=entry["implementation_source_path"],
            design_source_path=entry["design_source_path"],
            historical_snapshot_role="provenance_only",
            current_state_source="deterministic_l1_run_state",
        ),
        routine_mission_class=entry["routine_mission_class"],
        operating_location_class=entry["operating_location_class"],
        standby_location_class=entry["standby_location_class"],
    )
    entity.validate()
    return entity


def advance_fleet_world_process(
    fleet: FleetRunState,
    *,
    seed: int,
    tick: int,
    elapsed_minutes: int,
) -> List[Dict[str, Any]]:
    """Advance fleet state from seed/tick only; observation is never consulted."""
    fleet.validate()
    if fleet.provider_status != "bound":
        raise RuntimeError("fleet world process provider is unbound")
    if tick != fleet.process_position + 1:
        raise RuntimeError("fleet replay position is not contiguous with run tick")
    if elapsed_minutes <= 0:
        raise ValueError("fleet elapsed_minutes must be positive")

    transitions: List[Dict[str, Any]] = []
    for fleet_id in sorted(fleet.entities):
        entity = fleet.entities[fleet_id]
        transition = _advance_entity(entity, seed, tick, elapsed_minutes)
        if transition is not None:
            fleet.transitions.append(transition)
            transitions.append(transition)
    fleet.process_position = tick
    fleet.elapsed_minutes += elapsed_minutes
    fleet.validate()
    return transitions


def _advance_entity(
    entity: FleetEntityState,
    seed: int,
    tick: int,
    elapsed_minutes: int,
) -> Dict[str, Any] | None:
    if entity.fleet_id == SHADOWFAX_FLEET_ID:
        # Custody/promotion gates are incomplete. Keep ORD-3 observable as a
        # projected identity, but grant it no physical runtime authority.
        return None

    roll = _deterministic_roll(seed, entity.fleet_id, tick, "fleet-world-process")
    if entity.mission_state_class in {"active_routine", "active_explicit_adapter"}:
        entity.mission_elapsed_minutes += elapsed_minutes
        if entity.mission_elapsed_minutes < 30 or roll >= 0.22:
            return None
        return _complete_mission(entity, tick)

    threshold = _activation_threshold(entity.autonomy_class)
    if entity.status != "identity_projected":
        threshold *= 0.35
    if roll < threshold:
        return _start_routine_mission(entity, seed, tick)
    if entity.status in {"identity_projected", "mission_complete"}:
        return _set_standing_by(entity, tick)
    return None


def _activation_threshold(autonomy_class: str) -> float:
    return {
        "supervised_autonomous": 0.28,
        "fully_autonomous": 0.58,
        "swarm_autonomous": 0.62,
    }[autonomy_class]


def _start_routine_mission(
    entity: FleetEntityState,
    seed: int,
    tick: int,
) -> Dict[str, Any]:
    before = _state_marker(entity)
    digest = hashlib.sha256(
        f"{seed}:{entity.fleet_id}:{tick}:{entity.routine_mission_class}".encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    entity.status = "operating"
    entity.mission_state_class = "active_routine"
    entity.docking_location_class = entity.operating_location_class
    entity.mission_id = f"L1-{entity.fleet_id}-{tick}-{digest}"
    entity.mission_class = entity.routine_mission_class
    entity.mission_elapsed_minutes = 0
    entity.last_transition_tick = tick
    return _transition(entity, tick, "deterministic_fleet_world_process", before)


def _set_standing_by(entity: FleetEntityState, tick: int) -> Dict[str, Any]:
    before = _state_marker(entity)
    entity.status = "standing_by"
    entity.mission_state_class = "unassigned"
    entity.docking_location_class = entity.standby_location_class
    entity.mission_id = None
    entity.mission_class = None
    entity.mission_elapsed_minutes = 0
    entity.last_transition_tick = tick
    return _transition(entity, tick, "deterministic_fleet_world_process", before)


def _complete_mission(entity: FleetEntityState, tick: int) -> Dict[str, Any]:
    before = _state_marker(entity)
    entity.status = "mission_complete"
    entity.mission_state_class = "completed"
    entity.docking_location_class = entity.standby_location_class
    entity.last_transition_tick = tick
    return _transition(entity, tick, "deterministic_fleet_world_process", before)


def _transition(
    entity: FleetEntityState,
    tick: int,
    cause: str,
    before: Dict[str, Any],
    *,
    governance_receipt_id: str | None = None,
) -> Dict[str, Any]:
    return {
        "transition_id": _transition_id(entity.fleet_id, tick, cause, entity.mission_id),
        "fleet_id": entity.fleet_id,
        "tick": tick,
        "cause": cause,
        "before": before,
        "after": _state_marker(entity),
        "governance_receipt_id": governance_receipt_id,
        "pilot_attention_influenced_probability": False,
        "canon_status": "run_state",
    }


def _transition_id(
    fleet_id: str,
    tick: int,
    cause: str,
    mission_id: str | None,
) -> str:
    payload = f"{fleet_id}:{tick}:{cause}:{mission_id or 'none'}".encode("utf-8")
    return f"fleet-transition-{hashlib.sha256(payload).hexdigest()[:16]}"


def _state_marker(entity: FleetEntityState) -> Dict[str, Any]:
    return {
        "status": entity.status,
        "mission_state_class": entity.mission_state_class,
        "docking_location_class": entity.docking_location_class,
        "mission_id": entity.mission_id,
        "mission_class": entity.mission_class,
        "mission_elapsed_minutes": entity.mission_elapsed_minutes,
    }


def _deterministic_roll(seed: int, fleet_id: str, tick: int, namespace: str) -> float:
    payload = f"{namespace}:{seed}:{fleet_id}:{tick}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def fleet_observation(state: L1RunState) -> Dict[str, Any]:
    """Project all bound fleet records without exact navigation claims."""
    unavailable = _unavailable_provider(state, "fleet")
    if unavailable is not None:
        return unavailable
    return _available_provider(
        state,
        "fleet",
        [_entity_observation(entity) for entity in _entities(state)],
    )


def proximity_observation(state: L1RunState) -> Dict[str, Any]:
    """Project qualitative proximity classes; exact range remains quarantined."""
    unavailable = _unavailable_provider(state, "proximity")
    if unavailable is not None:
        return unavailable
    records = [
        {
            "fleet_id": entity.fleet_id,
            "display_name": entity.display_name,
            "proximity_class": entity.docking_location_class,
            "exact_range_available": False,
        }
        for entity in _entities(state)
    ]
    return _available_provider(state, "proximity", records)


def docking_observation(state: L1RunState) -> Dict[str, Any]:
    """Project docking classes without inventing bays, ports, or trajectories."""
    unavailable = _unavailable_provider(state, "docking")
    if unavailable is not None:
        return unavailable
    docked_classes = {"docked_at_orion", "orion_hangar"}
    records = [
        {
            "fleet_id": entity.fleet_id,
            "display_name": entity.display_name,
            "docking_location_class": entity.docking_location_class,
            "docked": entity.docking_location_class in docked_classes,
            "exact_bay_available": False,
            "trajectory_available": False,
        }
        for entity in _entities(state)
    ]
    return _available_provider(state, "docking", records)


def drone_observation(state: L1RunState) -> Dict[str, Any]:
    """Project physical ORD run state, not MCP-policy dispatch decisions."""
    unavailable = _unavailable_provider(state, "drone")
    if unavailable is not None:
        return unavailable
    records = [
        {
            **_entity_observation(entity),
            "physical_state_source": "l1_run_fleet_state",
            "mcp_policy_dispatch_implies_flight": False,
            "physical_activation_authorized": entity.fleet_id != SHADOWFAX_FLEET_ID,
        }
        for entity in _entities(state)
        if entity.fleet_id.startswith("ORD-")
    ]
    return _available_provider(state, "drone", records)


def observation_for_focus(state: L1RunState, focus: str) -> Dict[str, Any] | None:
    normalized = focus.strip().lower()
    providers = {
        "fleet": fleet_observation,
        "fleet systems": fleet_observation,
        "proximity": proximity_observation,
        "proximity systems": proximity_observation,
        "docking": docking_observation,
        "docking systems": docking_observation,
        "drone": drone_observation,
        "drones": drone_observation,
        "autonomous craft": drone_observation,
    }
    provider = providers.get(normalized)
    return provider(state) if provider is not None else None


def _entities(state: L1RunState) -> Iterable[FleetEntityState]:
    return (state.fleet.entities[fleet_id] for fleet_id in sorted(state.fleet.entities))


def _entity_observation(entity: FleetEntityState) -> Dict[str, Any]:
    return {
        "fleet_id": entity.fleet_id,
        "display_name": entity.display_name,
        "asset_class": entity.asset_class,
        "autonomy_class": entity.autonomy_class,
        "status": entity.status,
        "mission_state_class": entity.mission_state_class,
        "mission_id": entity.mission_id,
        "mission_class": entity.mission_class,
        "mission_elapsed_minutes": entity.mission_elapsed_minutes,
        "docking_location_class": entity.docking_location_class,
        "provenance": asdict(entity.provenance),
    }


def _unavailable_provider(
    state: L1RunState,
    channel: str,
) -> Dict[str, Any] | None:
    if state.fleet.provider_status == "bound":
        return None
    return {
        "channel": channel,
        "status": "unavailable",
        "reason": "provider_unbound",
        "provider": None,
        "tick": state.manifest.tick,
        "records": [],
    }


def _available_provider(
    state: L1RunState,
    channel: str,
    records: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return {
        "channel": channel,
        "status": "available",
        "reason": None,
        "provider": "l1_run_fleet_state",
        "tick": state.manifest.tick,
        "authority_receipt_id": state.fleet.authority_receipt_id,
        "projection_role": state.fleet.projection_role,
        "exact_navigation_available": False,
        "records": records,
    }


@dataclass(frozen=True)
class OrdPhysicalMissionProposal:
    """Explicit bridge object between MCP policy and a physical L1 mission."""

    proposal_id: str
    policy_mission_id: str
    drone_ids: List[str]
    physical_mission_class: str
    docking_location_class: str
    status: str = "proposal_only"
    physical_execution: bool = False
    policy_domain: str = ORD_POLICY_DOMAIN
    adapter: str = ORD_ADAPTER_ID


class OrdPhysicalMissionAdapter:
    """Require an explicit proposal and Triplex receipt before ORD flight state."""

    def propose(
        self,
        order: DispatchOrder,
        *,
        physical_mission_class: str,
        docking_location_class: str,
    ) -> OrdPhysicalMissionProposal:
        self._validate_mission_fields(
            physical_mission_class,
            docking_location_class,
        )
        drone_ids = []
        for item in order.drones_required:
            drone_id = DRONE_ID_BY_POLICY_TYPE.get(item)
            if drone_id is None:
                if item == DroneType.SHADOWFAX:
                    raise GovernanceError(
                        "SHADOWFAX custody/promotion gates are incomplete; "
                        "physical activation rejected"
                    )
                raise ValueError(f"ORD policy drone type is unsupported: {item}")
            drone_ids.append(drone_id)
        if not drone_ids:
            raise ValueError("ORD policy order contains no drone requirements")
        proposal_id = self._proposal_id(
            order.mission_id,
            physical_mission_class,
            docking_location_class,
            drone_ids,
        )
        return OrdPhysicalMissionProposal(
            proposal_id=proposal_id,
            policy_mission_id=order.mission_id,
            drone_ids=drone_ids,
            physical_mission_class=physical_mission_class,
            docking_location_class=docking_location_class,
        )

    def activate(
        self,
        fleet: FleetRunState,
        proposal: OrdPhysicalMissionProposal,
        *,
        receipt: GovernanceReceipt,
        tick: int,
    ) -> List[Dict[str, Any]]:
        self._validate_activation(fleet, proposal, receipt, tick)
        entities = self._resolve_entities(fleet, proposal)
        transitions = [
            self._activate_entity(entity, fleet, proposal, receipt, tick)
            for entity in entities
        ]
        fleet.validate()
        return transitions

    @classmethod
    def _validate_activation(
        cls,
        fleet: FleetRunState,
        proposal: OrdPhysicalMissionProposal,
        receipt: GovernanceReceipt,
        tick: int,
    ) -> None:
        if not receipt.complete:
            raise GovernanceError(
                "Triplex authorization incomplete; ORD physical mission rejected"
            )
        cls._validate_proposal(proposal)
        if fleet.provider_status != "bound":
            raise RuntimeError("fleet physical-state provider is unbound")
        if tick != fleet.process_position:
            raise RuntimeError("ORD activation tick does not match fleet replay position")

    @classmethod
    def _validate_proposal(cls, proposal: OrdPhysicalMissionProposal) -> None:
        if not isinstance(proposal, OrdPhysicalMissionProposal):
            raise ValueError("ORD physical mission proposal type is unsupported")
        if proposal.status != "proposal_only" or proposal.physical_execution:
            raise ValueError("ORD adapter accepts proposal-only policy bridges")
        if proposal.policy_domain != ORD_POLICY_DOMAIN or proposal.adapter != ORD_ADAPTER_ID:
            raise ValueError("ORD physical mission proposal provenance is unsupported")
        if not isinstance(proposal.policy_mission_id, str) or not proposal.policy_mission_id:
            raise ValueError("ORD policy mission ID must be a non-empty string")
        cls._validate_mission_fields(
            proposal.physical_mission_class,
            proposal.docking_location_class,
        )
        if not proposal.drone_ids or not all(
            isinstance(drone_id, str) and drone_id for drone_id in proposal.drone_ids
        ):
            raise ValueError("ORD physical mission proposal requires drone identities")
        if len(set(proposal.drone_ids)) != len(proposal.drone_ids):
            raise ValueError("ORD physical mission proposal contains duplicate drones")
        allowed_ids = frozenset(DRONE_ID_BY_POLICY_TYPE.values())
        if any(drone_id not in allowed_ids for drone_id in proposal.drone_ids):
            raise GovernanceError(
                "ORD physical mission proposal contains an unpromoted or unsupported drone"
            )
        expected_id = cls._proposal_id(
            proposal.policy_mission_id,
            proposal.physical_mission_class,
            proposal.docking_location_class,
            proposal.drone_ids,
        )
        if proposal.proposal_id != expected_id:
            raise ValueError("ORD physical mission proposal integrity check failed")

    @staticmethod
    def _validate_mission_fields(
        physical_mission_class: str,
        docking_location_class: str,
    ) -> None:
        if not isinstance(physical_mission_class, str) or not physical_mission_class.startswith(
            "physical_"
        ):
            raise ValueError("ORD physical mission class must start with 'physical_'")
        if docking_location_class not in ORD_PHYSICAL_LOCATIONS:
            raise ValueError("ORD physical mission location class is unsupported")

    @staticmethod
    def _proposal_id(
        policy_mission_id: str,
        physical_mission_class: str,
        docking_location_class: str,
        drone_ids: List[str],
    ) -> str:
        payload = ":".join(
            [
                policy_mission_id,
                physical_mission_class,
                docking_location_class,
                *drone_ids,
            ]
        )
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
        return f"ord-physical-{digest}"

    @staticmethod
    def _resolve_entities(
        fleet: FleetRunState,
        proposal: OrdPhysicalMissionProposal,
    ) -> List[FleetEntityState]:
        entities: List[FleetEntityState] = []
        for drone_id in proposal.drone_ids:
            entity = fleet.entities.get(drone_id)
            if entity is None or not drone_id.startswith("ORD-"):
                raise ValueError(f"ORD physical entity is not projected: {drone_id}")
            if drone_id == SHADOWFAX_FLEET_ID:
                raise GovernanceError(
                    "SHADOWFAX custody/promotion gates are incomplete; "
                    "physical activation rejected"
                )
            entities.append(entity)
        return entities

    @staticmethod
    def _activate_entity(
        entity: FleetEntityState,
        fleet: FleetRunState,
        proposal: OrdPhysicalMissionProposal,
        receipt: GovernanceReceipt,
        tick: int,
    ) -> Dict[str, Any]:
        before = _state_marker(entity)
        entity.status = "operating"
        entity.mission_state_class = "active_explicit_adapter"
        entity.docking_location_class = proposal.docking_location_class
        entity.mission_id = proposal.proposal_id
        entity.mission_class = proposal.physical_mission_class
        entity.mission_elapsed_minutes = 0
        entity.last_transition_tick = tick
        transition = _transition(
            entity,
            tick,
            "explicit_ord_physical_mission_adapter",
            before,
            governance_receipt_id=receipt.receipt_id,
        )
        fleet.transitions.append(transition)
        return transition


__all__ = [
    "OrdPhysicalMissionAdapter",
    "OrdPhysicalMissionProposal",
    "advance_fleet_world_process",
    "build_initial_fleet_state",
    "docking_observation",
    "drone_observation",
    "expected_fleet_ids",
    "fleet_observation",
    "observation_for_focus",
    "proximity_observation",
    "validate_fleet_identity_projection",
]
