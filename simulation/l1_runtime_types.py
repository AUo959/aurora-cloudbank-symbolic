#!/usr/bin/env python3
"""Data contracts for the governed Orion L1 runtime."""

from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from l1_runtime_support import (
    int_mapping,
    optional_int,
    required_bool,
    required_int,
    string_mapping,
)


class DeterministicReplayRNG:
    """Hash/counter replay generator for non-security simulation choices."""

    def __init__(self, seed: int) -> None:
        self._seed = str(seed).encode("ascii")
        self._counter = 0

    def random(self) -> float:
        payload = self._seed + b":" + str(self._counter).encode("ascii")
        digest = hashlib.sha256(payload).digest()
        self._counter += 1
        return int.from_bytes(digest[:8], "big") / float(1 << 64)


@dataclass(frozen=True)
class PopulationSnapshot:
    crew_capacity: Optional[int]
    current_human_crew_complement: Optional[int]
    identified_human_records: int
    persona_resolved_humans: Optional[int]
    missing_named_human_claim: bool
    system_entities: Dict[str, int]
    historical_aggregate_claims: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        self._validate_base_counts()
        self._validate_persona_subset()
        self._validate_human_complement()
        self._validate_system_entities()

    def _validate_base_counts(self) -> None:
        if self.crew_capacity is not None and self.crew_capacity < 0:
            raise ValueError("crew_capacity cannot be negative")
        if self.identified_human_records < 0:
            raise ValueError("identified_human_records cannot be negative")

    def _validate_persona_subset(self) -> None:
        if self.persona_resolved_humans is None:
            return
        if self.persona_resolved_humans < 0:
            raise ValueError("persona_resolved_humans cannot be negative")
        if self.persona_resolved_humans > self.identified_human_records:
            raise ValueError(
                "persona-resolved humans cannot exceed identified human records"
            )

    def _validate_human_complement(self) -> None:
        complement = self.current_human_crew_complement
        if complement is None:
            return
        if complement < self.identified_human_records:
            raise ValueError(
                "human crew complement cannot be smaller than identified human records"
            )
        if self.crew_capacity is not None and complement > self.crew_capacity:
            raise ValueError("human crew complement cannot exceed crew capacity")

    def _validate_system_entities(self) -> None:
        if any(value < 0 for value in self.system_entities.values()):
            raise ValueError("system entity counts cannot be negative")

    @classmethod
    def from_baseline(cls, baseline: Dict[str, Any]) -> "PopulationSnapshot":
        payload = baseline.get("population")
        if not isinstance(payload, dict):
            raise ValueError("population must be a JSON object")

        snapshot = cls(
            crew_capacity=optional_int(payload.get("crew_capacity"), "crew_capacity"),
            current_human_crew_complement=optional_int(
                payload.get("current_human_crew_complement"),
                "current_human_crew_complement",
            ),
            identified_human_records=required_int(
                payload.get("identified_human_records"),
                "identified_human_records",
            ),
            persona_resolved_humans=optional_int(
                payload.get("persona_resolved_humans"),
                "persona_resolved_humans",
            ),
            missing_named_human_claim=required_bool(
                payload.get("missing_named_human_claim"),
                "missing_named_human_claim",
            ),
            system_entities=int_mapping(
                payload.get("system_entities"),
                "system_entities",
            ),
            historical_aggregate_claims=string_mapping(
                payload.get("historical_aggregate_claims", {}),
                "historical_aggregate_claims",
            ),
        )
        snapshot.validate()
        return snapshot


@dataclass(frozen=True)
class EpistemicRecord:
    record_id: str
    subject: str
    value: Any
    epistemic_class: str
    provenance: str
    confidence: float
    tick: int
    canon_status: str = "run_state"

    def __post_init__(self) -> None:
        allowed = {
            "world_fact",
            "character_belief",
            "station_record",
            "runtime_observation",
            "pilot_knowledge",
            "testimony",
            "inference",
        }
        if self.epistemic_class not in allowed:
            raise ValueError(f"unsupported epistemic_class: {self.epistemic_class}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class GovernanceReceipt:
    l3_glyph_arbitration: bool
    continuity_and_relay_verification: bool
    l1_human_consent: bool
    receipt_id: str
    provenance: str

    def __post_init__(self) -> None:
        stages = (
            self.l3_glyph_arbitration,
            self.continuity_and_relay_verification,
            self.l1_human_consent,
        )
        if not all(type(stage) is bool for stage in stages):
            raise ValueError("Triplex authorization stages must be booleans")

    @property
    def complete(self) -> bool:
        return all(
            (
                self.l3_glyph_arbitration,
                self.continuity_and_relay_verification,
                self.l1_human_consent,
            )
        )


@dataclass(frozen=True)
class FleetEntityProvenance:
    """Authority-safe provenance carried by each projected fleet entity."""

    authority_receipt_id: str
    projection_role: str
    identity_source_path: str
    design_source_path: str
    historical_snapshot_role: str
    current_state_source: str

    def validate(self) -> None:
        values = (
            self.authority_receipt_id,
            self.projection_role,
            self.identity_source_path,
            self.design_source_path,
            self.historical_snapshot_role,
            self.current_state_source,
        )
        if not all(isinstance(value, str) and value for value in values):
            raise ValueError("fleet provenance fields must be non-empty strings")
        if self.projection_role != "runtime_projection_non_authoritative":
            raise ValueError("fleet projection must remain non-authoritative")
        if self.historical_snapshot_role != "provenance_only":
            raise ValueError("historical fleet snapshots must remain provenance only")
        if self.current_state_source != "deterministic_l1_run_state":
            raise ValueError("fleet current state source is unsupported")


@dataclass
class FleetEntityState:
    """Typed run-scoped state for one physical fleet asset or asset group."""

    fleet_id: str
    display_name: str
    asset_class: str
    autonomy_class: str
    status: str
    mission_state_class: str
    docking_location_class: str
    provenance: FleetEntityProvenance
    routine_mission_class: str
    operating_location_class: str
    standby_location_class: str
    mission_id: Optional[str] = None
    mission_class: Optional[str] = None
    mission_elapsed_minutes: int = 0
    last_transition_tick: int = 0

    def validate(self) -> None:
        self._validate_identity()
        self._validate_enums()
        self._validate_locations()
        self._validate_mission()
        self._validate_counters()
        self._validate_custody_boundary()
        self.provenance.validate()

    def _validate_identity(self) -> None:
        if not self.fleet_id or not self.display_name or not self.asset_class:
            raise ValueError("fleet identity fields must be non-empty")

    def _validate_enums(self) -> None:
        if self.autonomy_class not in {
            "supervised_autonomous",
            "fully_autonomous",
            "swarm_autonomous",
        }:
            raise ValueError(f"unsupported fleet autonomy class: {self.autonomy_class}")
        if self.status not in {
            "identity_projected",
            "standing_by",
            "operating",
            "mission_complete",
        }:
            raise ValueError(f"unsupported fleet status: {self.status}")
        if self.mission_state_class not in {
            "unassigned",
            "active_routine",
            "active_explicit_adapter",
            "completed",
        }:
            raise ValueError(
                f"unsupported fleet mission state: {self.mission_state_class}"
            )

    def _validate_locations(self) -> None:
        allowed_locations = {
            "unresolved",
            "docked_at_orion",
            "station_proximity",
            "external_operating_area",
            "assigned_host_vessel",
            "orion_hangar",
        }
        locations = (
            self.docking_location_class,
            self.operating_location_class,
            self.standby_location_class,
        )
        if any(location not in allowed_locations for location in locations):
            raise ValueError("unsupported fleet docking/location class")

    def _validate_mission(self) -> None:
        self._validate_mission_identity()
        self._validate_active_mission()
        self._validate_mission_lineage()

    def _validate_mission_identity(self) -> None:
        if self.mission_id is not None and not self.mission_id:
            raise ValueError("fleet mission_id cannot be empty")
        if self.mission_id is not None and not self.mission_id.startswith(
            (f"L1-{self.fleet_id}-", "ord-physical-")
        ):
            raise ValueError("fleet mission_id is not run-derived")
        self._validate_unassigned_mission()

    def _validate_unassigned_mission(self) -> None:
        if self.mission_state_class == "unassigned" and self.mission_id is not None:
            raise ValueError("unassigned fleet entity cannot carry a mission_id")
        if self.mission_state_class == "unassigned" and self.mission_class is not None:
            raise ValueError("unassigned fleet entity cannot carry a mission class")

    def _validate_active_mission(self) -> None:
        if self.mission_state_class.startswith("active_") and (
            self.mission_id is None or self.mission_class is None
        ):
            raise ValueError("active fleet entity requires mission identity and class")

    def _validate_mission_lineage(self) -> None:
        if (
            self.mission_state_class == "active_routine"
            and self.mission_id is not None
            and not self.mission_id.startswith(f"L1-{self.fleet_id}-")
        ):
            raise ValueError("routine fleet mission_id has the wrong lineage")
        if self.mission_state_class == "active_explicit_adapter" and not self.fleet_id.startswith(
            "ORD-"
        ):
            raise ValueError("explicit ORD adapter state is only valid for ORD assets")
        if (
            self.mission_state_class == "active_explicit_adapter"
            and self.mission_id is not None
            and not self.mission_id.startswith("ord-physical-")
        ):
            raise ValueError("ORD adapter mission_id has the wrong lineage")

    def _validate_counters(self) -> None:
        if self.mission_elapsed_minutes < 0 or self.last_transition_tick < 0:
            raise ValueError("fleet mission counters cannot be negative")

    def _validate_custody_boundary(self) -> None:
        if self.fleet_id != "ORD-3":
            return
        identity_only = (
            self.status == "identity_projected"
            and self.mission_state_class == "unassigned"
            and self.docking_location_class == "unresolved"
            and self.mission_id is None
            and self.mission_class is None
            and self.mission_elapsed_minutes == 0
            and self.last_transition_tick == 0
        )
        if not identity_only:
            raise ValueError(
                "ORD-3 Shadowfax is identity/provenance only until custody gates clear"
            )


@dataclass
class FleetRunState:
    """Fleet provider binding and deterministic replay position for one L1 run."""

    provider_status: str
    authority_receipt_id: Optional[str]
    projection_role: str
    process_position: int
    elapsed_minutes: int
    entities: Dict[str, FleetEntityState] = field(default_factory=dict)
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    migrated_from_contract_version: Optional[str] = None

    @classmethod
    def unbound(cls) -> "FleetRunState":
        return cls(
            provider_status="unbound",
            authority_receipt_id=None,
            projection_role="provider_unbound",
            process_position=0,
            elapsed_minutes=0,
        )

    def validate(self) -> None:
        if self.provider_status not in {"bound", "unbound"}:
            raise ValueError("fleet provider status is unsupported")
        if self.process_position < 0 or self.elapsed_minutes < 0:
            raise ValueError("fleet replay counters cannot be negative")
        if self.provider_status == "unbound":
            self._validate_unbound()
            return
        self._validate_bound()

    def _validate_unbound(self) -> None:
        consistent = (
            self.authority_receipt_id is None
            and self.projection_role == "provider_unbound"
            and self.process_position == 0
            and self.elapsed_minutes == 0
            and not self.entities
            and not self.transitions
            and self.migrated_from_contract_version is None
        )
        if not consistent:
            raise ValueError("unbound fleet provider carries bound runtime state")

    def _validate_bound(self) -> None:
        if not self.authority_receipt_id:
            raise ValueError("bound fleet provider requires an authority receipt")
        if self.projection_role != "runtime_projection_non_authoritative":
            raise ValueError("bound fleet state must remain a runtime projection")
        for fleet_id, entity in self.entities.items():
            if fleet_id != entity.fleet_id:
                raise ValueError("fleet entity mapping key does not match identity")
            entity.validate()
        if any(item.get("fleet_id") == "ORD-3" for item in self.transitions):
            raise ValueError("ORD-3 Shadowfax cannot carry physical runtime transitions")


@dataclass(frozen=True)
class EmbodimentState:
    """One evidence-classified architectural component embodied in Orion L1."""

    embodiment_id: str
    component: str
    l1_kind: str
    location: str
    location_certainty: str
    l2_control_surfaces: List[str]
    l3_interfaces: List[str]
    authority_class: str
    evidence_class: str
    source_refs: List[str]
    provider_status: str
    required_for_resume: bool
    causal_use_permitted: bool
    causal_scope: str
    blockers: List[str]

    def validate(self) -> None:
        strings = (
            self.embodiment_id,
            self.component,
            self.l1_kind,
            self.location,
            self.authority_class,
            self.causal_scope,
        )
        if not all(isinstance(value, str) and value for value in strings):
            raise ValueError("embodiment identity and role fields must be non-empty")
        if self.location_certainty not in {"CANON", "STAGING", "UNCONFIRMED"}:
            raise ValueError("embodiment location certainty is unsupported")
        if self.evidence_class not in {
            "explicit_canon",
            "current_implementation",
            "recoverable_historical_implementation",
            "staging",
            "bounded_inference",
            "unresolved",
        }:
            raise ValueError("embodiment evidence class is unsupported")
        if self.provider_status not in {"bound", "partial", "unbound", "blocked"}:
            raise ValueError("embodiment provider status is unsupported")
        if type(self.required_for_resume) is not bool:
            raise ValueError("embodiment resume requirement must be boolean")
        if type(self.causal_use_permitted) is not bool:
            raise ValueError("embodiment causal-use flag must be boolean")
        self._validate_string_lists()
        self._validate_causal_boundary()

    def _validate_string_lists(self) -> None:
        values = (
            self.l2_control_surfaces,
            self.l3_interfaces,
            self.source_refs,
            self.blockers,
        )
        if any(
            not isinstance(items, list)
            or not all(isinstance(item, str) and item for item in items)
            for items in values
        ):
            raise ValueError("embodiment list fields must contain non-empty strings")
        if not self.source_refs:
            raise ValueError("embodiment projection requires provenance references")

    def _validate_causal_boundary(self) -> None:
        if self.causal_use_permitted:
            if self.provider_status not in {"bound", "partial"}:
                raise ValueError("unavailable embodiment provider cannot be causal")
            if self.causal_scope == "none":
                raise ValueError("causal embodiment provider requires a bounded scope")
            return
        if self.causal_scope != "none":
            raise ValueError("non-causal embodiment provider must use scope 'none'")


@dataclass
class EmbodimentRunState:
    """Run-scoped projection of architecture into physical L1 embodiments."""

    registry_status: str
    registry_id: Optional[str]
    registry_sha256: Optional[str]
    projection_role: str
    provider_readiness_status: str
    entities: Dict[str, EmbodimentState] = field(default_factory=dict)
    migrated_from_contract_version: Optional[str] = None

    @classmethod
    def unbound(cls) -> "EmbodimentRunState":
        return cls(
            registry_status="unbound",
            registry_id=None,
            registry_sha256=None,
            projection_role="provider_unbound",
            provider_readiness_status="unavailable",
        )

    def validate(self) -> None:
        if self.registry_status not in {"bound", "unbound"}:
            raise ValueError("embodiment registry status is unsupported")
        if self.registry_status == "unbound":
            self._validate_unbound()
            return
        self._validate_bound()

    def _validate_unbound(self) -> None:
        consistent = (
            self.registry_id is None
            and self.registry_sha256 is None
            and self.projection_role == "provider_unbound"
            and self.provider_readiness_status == "unavailable"
            and not self.entities
            and self.migrated_from_contract_version is None
        )
        if not consistent:
            raise ValueError("unbound embodiment registry carries bound state")

    def _validate_bound(self) -> None:
        if not self.registry_id:
            raise ValueError("bound embodiment registry requires identity")
        if (
            not isinstance(self.registry_sha256, str)
            or len(self.registry_sha256) != 64
            or any(char not in "0123456789abcdef" for char in self.registry_sha256)
        ):
            raise ValueError("bound embodiment registry requires a SHA-256 digest")
        if self.projection_role != "runtime_projection_non_authoritative":
            raise ValueError("bound embodiment state must remain non-authoritative")
        if self.provider_readiness_status not in {"ready", "incomplete"}:
            raise ValueError("embodiment provider readiness is unsupported")
        for embodiment_id, entity in self.entities.items():
            if embodiment_id != entity.embodiment_id:
                raise ValueError("embodiment mapping key does not match identity")
            entity.validate()
        expected_readiness = (
            "ready"
            if all(
                not entity.required_for_resume or entity.provider_status == "bound"
                for entity in self.entities.values()
            )
            else "incomplete"
        )
        if self.provider_readiness_status != expected_readiness:
            raise ValueError("embodiment provider readiness is internally inconsistent")


@dataclass
class RunManifest:
    schema_version: int
    runtime_contract_version: str
    run_id: str
    created_at: str
    cloudbank_revision: str
    canonrec_revision: str
    fleet_authority_receipt_sha256: Optional[str]
    embodiment_registry_sha256: Optional[str]
    seed: int
    station_cycle_length_minutes: int
    station_cycle_minute: int
    tick: int
    status: str
    canon_status: str
    active_quarantines: List[str]
    population: PopulationSnapshot


@dataclass
class L1RunState:
    manifest: RunManifest
    world_state: Dict[str, Any]
    fleet: FleetRunState = field(default_factory=FleetRunState.unbound)
    embodiments: EmbodimentRunState = field(default_factory=EmbodimentRunState.unbound)
    character_knowledge: Dict[str, List[EpistemicRecord]] = field(default_factory=dict)
    character_actions: List[Dict[str, Any]] = field(default_factory=list)
    station_records: List[EpistemicRecord] = field(default_factory=list)
    runtime_observations: List[EpistemicRecord] = field(default_factory=list)
    pilot_knowledge: List[EpistemicRecord] = field(default_factory=list)
    governance_receipts: List[GovernanceReceipt] = field(default_factory=list)
    governed_records: List[EpistemicRecord] = field(default_factory=list)
    communications: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    promotion_candidates: List[Dict[str, Any]] = field(default_factory=list)


def l1_run_state_from_payload(payload: Dict[str, Any]) -> L1RunState:
    """Deserialize a persisted run without weakening the runtime type contract."""
    manifest_payload = _mapping(payload.get("manifest"), "manifest")
    manifest = _manifest_from_payload(manifest_payload)
    if manifest.runtime_contract_version == "1.1.0" and "fleet" in payload:
        raise ValueError("contract 1.1.0 persisted runs cannot supply fleet state")
    if manifest.runtime_contract_version in {"1.1.0", "1.2.0"} and "embodiments" in payload:
        raise ValueError("pre-1.3.0 persisted runs cannot supply embodiment state")
    if (
        manifest.runtime_contract_version not in {"1.1.0", "1.2.0"}
        and "embodiments" not in payload
    ):
        # The mirror of the guard above. A pre-1.3.0 run legitimately has no
        # embodiment state and is migrated on load; a CURRENT-contract run that
        # is missing it has been truncated or tampered with, and must be
        # rejected at parse time rather than silently rebuilt from the registry
        # -- rebuilding would mask the loss and hand back a run whose projection
        # no longer reflects what was persisted.
        raise ValueError("current-contract persisted runs must supply embodiment state")
    return L1RunState(
        manifest=manifest,
        world_state=copy.deepcopy(_mapping(payload.get("world_state"), "world_state")),
        fleet=_fleet_state_from_payload(payload.get("fleet")),
        embodiments=_embodiment_state_from_payload(payload.get("embodiments")),
        character_knowledge=_character_knowledge_from_payload(
            payload.get("character_knowledge", {})
        ),
        character_actions=_mapping_list(
            payload.get("character_actions", []), "character_actions"
        ),
        station_records=_epistemic_records(
            payload.get("station_records", []), "station_records"
        ),
        runtime_observations=_epistemic_records(
            payload.get("runtime_observations", []), "runtime_observations"
        ),
        pilot_knowledge=_epistemic_records(
            payload.get("pilot_knowledge", []), "pilot_knowledge"
        ),
        governance_receipts=_governance_receipts(
            payload.get("governance_receipts", [])
        ),
        governed_records=_epistemic_records(
            payload.get("governed_records", []), "governed_records"
        ),
        communications=_mapping_list(
            payload.get("communications", []), "communications"
        ),
        events=_mapping_list(payload.get("events", []), "events"),
        promotion_candidates=_mapping_list(
            payload.get("promotion_candidates", []), "promotion_candidates"
        ),
    )


def _embodiment_state_from_payload(value: Any) -> EmbodimentRunState:
    if value is None:
        return EmbodimentRunState.unbound()
    payload = _mapping(value, "embodiments")
    entities_payload = _mapping(payload.get("entities", {}), "embodiments.entities")
    state = EmbodimentRunState(
        registry_status=_string(
            payload.get("registry_status"), "embodiments.registry_status"
        ),
        registry_id=_optional_string(
            payload.get("registry_id"), "embodiments.registry_id"
        ),
        registry_sha256=_optional_string(
            payload.get("registry_sha256"), "embodiments.registry_sha256"
        ),
        projection_role=_string(
            payload.get("projection_role"), "embodiments.projection_role"
        ),
        provider_readiness_status=_string(
            payload.get("provider_readiness_status"),
            "embodiments.provider_readiness_status",
        ),
        entities={
            _string(embodiment_id, "embodiment entity key"): _embodiment_entity_from_payload(
                entity,
                f"embodiments.entities.{embodiment_id}",
            )
            for embodiment_id, entity in entities_payload.items()
        },
        migrated_from_contract_version=_optional_string(
            payload.get("migrated_from_contract_version"),
            "embodiments.migrated_from_contract_version",
        ),
    )
    state.validate()
    return state


def _embodiment_entity_from_payload(value: Any, name: str) -> EmbodimentState:
    payload = copy.deepcopy(_mapping(value, name))
    try:
        entity = EmbodimentState(**payload)
    except TypeError as exc:
        raise ValueError(f"{name} has invalid fields") from exc
    entity.validate()
    return entity


def _fleet_state_from_payload(value: Any) -> FleetRunState:
    if value is None:
        return FleetRunState.unbound()
    payload = _mapping(value, "fleet")
    entities_payload = _mapping(payload.get("entities", {}), "fleet.entities")
    fleet = FleetRunState(
        provider_status=_string(
            payload.get("provider_status"), "fleet.provider_status"
        ),
        authority_receipt_id=_optional_string(
            payload.get("authority_receipt_id"), "fleet.authority_receipt_id"
        ),
        projection_role=_string(
            payload.get("projection_role"), "fleet.projection_role"
        ),
        process_position=required_int(
            payload.get("process_position"), "fleet.process_position"
        ),
        elapsed_minutes=required_int(
            payload.get("elapsed_minutes"), "fleet.elapsed_minutes"
        ),
        entities={
            _string(fleet_id, "fleet entity key"): _fleet_entity_from_payload(
                entity, f"fleet.entities.{fleet_id}"
            )
            for fleet_id, entity in entities_payload.items()
        },
        transitions=_mapping_list(
            payload.get("transitions", []), "fleet.transitions"
        ),
        migrated_from_contract_version=_optional_string(
            payload.get("migrated_from_contract_version"),
            "fleet.migrated_from_contract_version",
        ),
    )
    fleet.validate()
    return fleet


def _fleet_entity_from_payload(value: Any, name: str) -> FleetEntityState:
    payload = _mapping(value, name)
    entity = FleetEntityState(
        fleet_id=_string(payload.get("fleet_id"), f"{name}.fleet_id"),
        display_name=_string(payload.get("display_name"), f"{name}.display_name"),
        asset_class=_string(payload.get("asset_class"), f"{name}.asset_class"),
        autonomy_class=_string(
            payload.get("autonomy_class"), f"{name}.autonomy_class"
        ),
        status=_string(payload.get("status"), f"{name}.status"),
        mission_state_class=_string(
            payload.get("mission_state_class"), f"{name}.mission_state_class"
        ),
        docking_location_class=_string(
            payload.get("docking_location_class"),
            f"{name}.docking_location_class",
        ),
        provenance=_fleet_provenance_from_payload(payload, name),
        routine_mission_class=_string(
            payload.get("routine_mission_class"), f"{name}.routine_mission_class"
        ),
        operating_location_class=_string(
            payload.get("operating_location_class"),
            f"{name}.operating_location_class",
        ),
        standby_location_class=_string(
            payload.get("standby_location_class"),
            f"{name}.standby_location_class",
        ),
        mission_id=_optional_string(
            payload.get("mission_id"), f"{name}.mission_id"
        ),
        mission_class=_optional_string(
            payload.get("mission_class"), f"{name}.mission_class"
        ),
        mission_elapsed_minutes=required_int(
            payload.get("mission_elapsed_minutes"),
            f"{name}.mission_elapsed_minutes",
        ),
        last_transition_tick=required_int(
            payload.get("last_transition_tick"), f"{name}.last_transition_tick"
        ),
    )
    entity.validate()
    return entity


def _fleet_provenance_from_payload(
    payload: Dict[str, Any],
    name: str,
) -> FleetEntityProvenance:
    provenance = _mapping(payload.get("provenance"), f"{name}.provenance")
    field_names = (
        "authority_receipt_id",
        "projection_role",
        "identity_source_path",
        "design_source_path",
        "historical_snapshot_role",
        "current_state_source",
    )
    values = {
        field_name: _string(
            provenance.get(field_name),
            f"{name}.provenance.{field_name}",
        )
        for field_name in field_names
    }
    return FleetEntityProvenance(**values)


def _manifest_from_payload(payload: Dict[str, Any]) -> RunManifest:
    population = PopulationSnapshot.from_baseline(
        {"population": _mapping(payload.get("population"), "manifest.population")}
    )
    active_quarantines = _string_list(
        payload.get("active_quarantines"), "manifest.active_quarantines"
    )
    return RunManifest(
        schema_version=required_int(payload.get("schema_version"), "schema_version"),
        runtime_contract_version=_string(
            payload.get("runtime_contract_version"), "runtime_contract_version"
        ),
        run_id=_string(payload.get("run_id"), "run_id"),
        created_at=_string(payload.get("created_at"), "created_at"),
        cloudbank_revision=_string(
            payload.get("cloudbank_revision"), "cloudbank_revision"
        ),
        canonrec_revision=_string(
            payload.get("canonrec_revision"), "canonrec_revision"
        ),
        fleet_authority_receipt_sha256=_optional_string(
            payload.get("fleet_authority_receipt_sha256"),
            "fleet_authority_receipt_sha256",
        ),
        embodiment_registry_sha256=_optional_string(
            payload.get("embodiment_registry_sha256"),
            "embodiment_registry_sha256",
        ),
        seed=required_int(payload.get("seed"), "seed"),
        station_cycle_length_minutes=required_int(
            payload.get("station_cycle_length_minutes"),
            "station_cycle_length_minutes",
        ),
        station_cycle_minute=required_int(
            payload.get("station_cycle_minute"), "station_cycle_minute"
        ),
        tick=required_int(payload.get("tick"), "tick"),
        status=_string(payload.get("status"), "status"),
        canon_status=_string(payload.get("canon_status"), "canon_status"),
        active_quarantines=active_quarantines,
        population=population,
    )


def _character_knowledge_from_payload(value: Any) -> Dict[str, List[EpistemicRecord]]:
    payload = _mapping(value, "character_knowledge")
    return {
        _string(character_id, "character_knowledge key"): _epistemic_records(
            records, f"character_knowledge.{character_id}"
        )
        for character_id, records in payload.items()
    }


def _epistemic_records(value: Any, name: str) -> List[EpistemicRecord]:
    records = _list(value, name)
    return [
        _epistemic_record(item, f"{name}[{index}]")
        for index, item in enumerate(records)
    ]


def _epistemic_record(value: Any, name: str) -> EpistemicRecord:
    payload = _mapping(value, name)
    confidence = payload.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise ValueError(f"{name}.confidence must be numeric")
    return EpistemicRecord(
        record_id=_string(payload.get("record_id"), f"{name}.record_id"),
        subject=_string(payload.get("subject"), f"{name}.subject"),
        value=copy.deepcopy(payload.get("value")),
        epistemic_class=_string(
            payload.get("epistemic_class"), f"{name}.epistemic_class"
        ),
        provenance=_string(payload.get("provenance"), f"{name}.provenance"),
        confidence=float(confidence),
        tick=required_int(payload.get("tick"), f"{name}.tick"),
        canon_status=_string(
            payload.get("canon_status", "run_state"), f"{name}.canon_status"
        ),
    )


def _governance_receipts(value: Any) -> List[GovernanceReceipt]:
    receipts = _list(value, "governance_receipts")
    return [
        GovernanceReceipt(
            **copy.deepcopy(_mapping(item, f"governance_receipts[{index}]"))
        )
        for index, item in enumerate(receipts)
    ]


def _mapping_list(value: Any, name: str) -> List[Dict[str, Any]]:
    items = _list(value, name)
    return [
        copy.deepcopy(_mapping(item, f"{name}[{index}]"))
        for index, item in enumerate(items)
    ]


def _mapping(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")
    return value


def _list(value: Any, name: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return value


def _string_list(value: Any, name: str) -> List[str]:
    items = _list(value, name)
    if not all(isinstance(item, str) for item in items):
        raise ValueError(f"{name} must contain only strings")
    return list(items)


def _string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _optional_string(value: Any, name: str) -> Optional[str]:
    if value is None:
        return None
    return _string(value, name)
