"""Validated data contracts for the Narrative River Adapter."""

from __future__ import annotations

import json
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SUPPORTED_SCHEMA_VERSION = "0.1.0"
SupportedSchemaVersion = Literal["0.1.0"]
UnitInterval = Annotated[float, Field(ge=0.0, le=1.0)]


class StrictModel(BaseModel):
    """Base model that rejects undeclared state and validates assignment."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )


class PersistenceClass(str, Enum):
    EPHEMERAL = "ephemeral"
    DRAFT = "draft_persistent"
    PROJECT = "project_persistent"
    CANON_LINKED = "canon_linked"


class AuthorityStatus(str, Enum):
    CANON = "canon"
    STAGING = "staging"
    DRAFT = "draft"
    MIXED = "mixed"


class NarrativeState(str, Enum):
    OUTLINE = "outline"
    DRAFT = "draft"
    REVISED = "revised"
    CANON_CANDIDATE = "canon_candidate"
    CANON = "canon"


class EvidenceStatus(str, Enum):
    CONFIRMED = "confirmed"
    OBSERVED = "observed"
    INSTRUMENT_OUTPUT = "instrument_output"
    TESTIMONY = "testimony"
    HYPOTHESIS = "hypothesis"
    RUMOR = "rumor"
    CONTRADICTED = "contradicted"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ProvenanceRef(StrictModel):
    source_type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    authority_status: AuthorityStatus
    commit_sha: str | None = None
    confidence: UnitInterval = 1.0


class CanonSnapshot(StrictModel):
    repository: str | None = None
    commit_sha: str | None = None
    source_files: list[str] = Field(default_factory=list)
    authority_status: AuthorityStatus = AuthorityStatus.DRAFT


class NarrativeStatus(StrictModel):
    current_state: NarrativeState = NarrativeState.DRAFT
    persistence_class: PersistenceClass = PersistenceClass.EPHEMERAL
    previous_scene_id: str | None = None
    next_scene_hint: str | None = None
    storage_receipt: str | None = None

    @model_validator(mode="after")
    def require_storage_for_persistence(self) -> "NarrativeStatus":
        if self.persistence_class != PersistenceClass.EPHEMERAL and not self.storage_receipt:
            raise ValueError("persistent narrative state requires a storage_receipt")
        return self


class Viewpoint(StrictModel):
    mode: str = Field(min_length=1)
    focal_character_ids: list[str] = Field(default_factory=list)
    prohibited_omniscience: bool = True


class SceneObjective(StrictModel):
    operational_goal: str = Field(min_length=1)
    dramatic_goal: str = Field(min_length=1)
    required_state_change: str = Field(min_length=1)


class IncomingFlow(StrictModel):
    flow_id: str = Field(min_length=1)
    flow_type: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    carrier: str = Field(min_length=1)
    strength: UnitInterval
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    confidence: UnitInterval = 1.0


class NarrativeSediment(StrictModel):
    sediment_id: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    affected_actor_ids: list[str] = Field(default_factory=list)
    current_effect: str = ""
    resolution_status: str = "active"


class NarrativeReservoir(StrictModel):
    reservoir_id: str = Field(min_length=1)
    reservoir_type: str = Field(min_length=1)
    capacity: UnitInterval
    absorbs: list[str] = Field(default_factory=list)
    failure_condition: str = ""


class ChannelCondition(StrictModel):
    channel_id: str = Field(min_length=1)
    channel_type: str = Field(min_length=1)
    state: str = Field(min_length=1)
    turbulence: UnitInterval = 0.0
    notes: str = ""


class EvidenceClaim(StrictModel):
    claim_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    status: EvidenceStatus
    support: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    confidence: UnitInterval = 0.0


class ActorInterpretation(StrictModel):
    actor_id: str = Field(min_length=1)
    interpretation: str = Field(min_length=1)
    preferred_response: str = Field(min_length=1)
    blind_spot: str = Field(min_length=1)
    authority_limit: str = ""


class RelationshipState(StrictModel):
    relation_id: str = Field(min_length=1)
    actor_ids: list[str] = Field(min_length=2)
    trust: UnitInterval
    operational_reliance: UnitInterval
    current_strain: UnitInterval
    required_change: str = ""


class InstitutionalConstraint(StrictModel):
    constraint_id: str = Field(min_length=1)
    authority: str = Field(min_length=1)
    effect: str = Field(min_length=1)
    appears_in_prose_as: list[str] = Field(default_factory=list)
    must_not_appear_as: list[str] = Field(default_factory=list)


class EquipmentState(StrictModel):
    asset_id: str = Field(min_length=1)
    state: str = Field(min_length=1)
    quantity: int | None = Field(default=None, ge=0)
    constraints: list[str] = Field(default_factory=list)
    narrative_function: str = ""


class ScarcityState(StrictModel):
    scarce_asset: str = Field(min_length=1)
    current_quantity: int | None = Field(default=None, ge=0)
    consequence: str = Field(min_length=1)


class NarrativeRiverFrame(StrictModel):
    """Scene-level causal contract supplied to a prose generator."""

    frame_id: str = Field(min_length=1)
    schema_version: SupportedSchemaVersion = SUPPORTED_SCHEMA_VERSION
    scene_id: str = Field(min_length=1)
    chapter_id: str | None = None
    generated_at_utc: str = Field(min_length=1)
    canon_snapshot: CanonSnapshot
    narrative_status: NarrativeStatus
    viewpoint: Viewpoint
    scene_objective: SceneObjective
    incoming_flows: list[IncomingFlow] = Field(default_factory=list)
    active_pressures: dict[str, UnitInterval] = Field(default_factory=dict)
    sediment: list[NarrativeSediment] = Field(default_factory=list)
    reservoirs: list[NarrativeReservoir] = Field(default_factory=list)
    channel_conditions: list[ChannelCondition] = Field(default_factory=list)
    evidence_state: list[EvidenceClaim] = Field(default_factory=list)
    actor_interpretations: list[ActorInterpretation] = Field(default_factory=list)
    relationship_state: list[RelationshipState] = Field(default_factory=list)
    institutional_constraints: list[InstitutionalConstraint] = Field(default_factory=list)
    equipment_state: list[EquipmentState] = Field(default_factory=list)
    scarcity_state: list[ScarcityState] = Field(default_factory=list)
    required_downstream_effects: list[str] = Field(default_factory=list)
    prohibited_shortcuts: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
    exit_conditions: list[str] = Field(default_factory=list)
    axiom_checks: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_collection_ids(self) -> "NarrativeRiverFrame":
        collections = {
            "incoming_flows": [item.flow_id for item in self.incoming_flows],
            "sediment": [item.sediment_id for item in self.sediment],
            "reservoirs": [item.reservoir_id for item in self.reservoirs],
            "channel_conditions": [item.channel_id for item in self.channel_conditions],
            "evidence_state": [item.claim_id for item in self.evidence_state],
            "actor_interpretations": [item.actor_id for item in self.actor_interpretations],
            "relationship_state": [item.relation_id for item in self.relationship_state],
            "institutional_constraints": [item.constraint_id for item in self.institutional_constraints],
            "equipment_state": [item.asset_id for item in self.equipment_state],
        }
        for name, identifiers in collections.items():
            if len(identifiers) != len(set(identifiers)):
                raise ValueError(f"{name} contains duplicate identifiers")
        return self

    def canonical_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)


class SceneRiverDelta(StrictModel):
    """Approved state changes exported after a scene."""

    schema_version: SupportedSchemaVersion = SUPPORTED_SCHEMA_VERSION
    scene_id: str = Field(min_length=1)
    completed_at_utc: str | None = None
    storage_receipt: str | None = None
    state_changes: list[str] = Field(default_factory=list)
    new_sediment: list[NarrativeSediment] = Field(default_factory=list)
    resolved_sediment_ids: list[str] = Field(default_factory=list)
    pressure_changes: dict[str, float] = Field(default_factory=dict)
    relationship_changes: list[dict[str, Any]] = Field(default_factory=list)
    evidence_changes: list[dict[str, Any]] = Field(default_factory=list)
    new_questions: list[str] = Field(default_factory=list)
    closed_questions: list[str] = Field(default_factory=list)
    equipment_changes: list[dict[str, Any]] = Field(default_factory=list)
    institutional_changes: list[dict[str, Any]] = Field(default_factory=list)
    canon_candidates: list[str] = Field(default_factory=list)
    next_scene_requirements: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_delta_sets(self) -> "SceneRiverDelta":
        if len(self.resolved_sediment_ids) != len(set(self.resolved_sediment_ids)):
            raise ValueError("resolved_sediment_ids contains duplicates")
        if len(self.closed_questions) != len(set(self.closed_questions)):
            raise ValueError("closed_questions contains duplicates")
        return self

    def canonical_json(self) -> str:
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, indent=2, sort_keys=True)


class ValidationFinding(StrictModel):
    rule_id: str = Field(min_length=1)
    severity: ValidationSeverity
    message: str = Field(min_length=1)
    passage: str = ""
    line_number: int | None = Field(default=None, ge=1)


class ValidationReport(StrictModel):
    schema_version: SupportedSchemaVersion = SUPPORTED_SCHEMA_VERSION
    frame_id: str = Field(min_length=1)
    findings: list[ValidationFinding] = Field(default_factory=list)
    storage_receipt: str | None = None

    @property
    def has_errors(self) -> bool:
        return any(item.severity == ValidationSeverity.ERROR.value for item in self.findings)
