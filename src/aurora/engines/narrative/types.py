from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TaskKind(str, Enum):
    CHARACTER_ACTION_AUDIT = "character_action_audit"
    NEXT_EVENT_CONTINUITY_CHECK = "next_event_continuity_check"
    HISTORICAL_PLAUSIBILITY_CHECK = "historical_plausibility_check"
    EXPANSION = "expansion"
    TRANSLATION = "translation"
    UNSUPPORTED = "unsupported"


class Strictness(str, Enum):
    LENIENT = "lenient"
    DEFAULT = "default"
    STRICT = "strict"


class Verdict(str, Enum):
    SUPPORTED = "supported"
    PLAUSIBLE = "plausible"
    POSSIBLE_WITH_SETUP = "possible_with_setup"
    STRAINED = "strained"
    CONTRADICTORY = "contradictory"


@dataclass(frozen=True)
class LayerRecord:
    name: str
    origin: str
    confidence: float
    status: str = "available"
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EntityRecord:
    name: str
    entity_type: str = "character"
    role: str = ""
    traits: list[str] = field(default_factory=list)
    source: str = "declared"
    confidence: float = 1.0


@dataclass(frozen=True)
class PressureRecord:
    actor: str
    label: str
    direction: str = "toward"
    strength: float = 0.5
    source: str = "declared"
    confidence: float = 1.0


@dataclass(frozen=True)
class ConstraintRecord:
    label: str
    constraint_type: str
    severity: str = "soft"
    details: str = ""
    source: str = "declared"
    confidence: float = 1.0


@dataclass(frozen=True)
class MotiveRecord:
    actor: str
    label: str
    strength: float = 0.5
    source: str = "declared"
    confidence: float = 1.0
    inferred: bool = False


@dataclass(frozen=True)
class EventRecord:
    label: str
    status: str = "established"
    timing: str = ""
    participants: list[str] = field(default_factory=list)
    source: str = "declared"
    confidence: float = 1.0
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class KnowledgeStateRecord:
    holder: str
    fact: str
    status: str = "knows"
    source: str = "declared"
    confidence: float = 1.0


@dataclass(frozen=True)
class UncertaintyRecord:
    label: str
    reason: str
    source: str = "declared"
    confidence: float = 1.0


@dataclass(frozen=True)
class NormalizedTaskRequest:
    task_kind: TaskKind
    proposal_present: bool
    strictness: Strictness
    task_type: str = "validate"
    desired_output_form: str = "audit"
    input_kind: str = "mapping"
    user_query: str = ""
    supported_in_phase_one: bool = True
    unsupported_reason: str | None = None


@dataclass
class CanonicalState:
    state_id: str
    input_profile: dict[str, Any] = field(default_factory=dict)
    layers: list[LayerRecord] = field(default_factory=list)
    entities: list[EntityRecord] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    pressures: list[PressureRecord] = field(default_factory=list)
    constraints: list[ConstraintRecord] = field(default_factory=list)
    motives: list[MotiveRecord] = field(default_factory=list)
    events: list[EventRecord] = field(default_factory=list)
    knowledge_states: list[KnowledgeStateRecord] = field(default_factory=list)
    uncertainties: list[UncertaintyRecord] = field(default_factory=list)
    continuity: dict[str, Any] = field(default_factory=dict)
    narrative_context: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationPacket:
    active_layers: list[str] = field(default_factory=list)
    missing_layers: list[str] = field(default_factory=list)
    selected_operators: list[str] = field(default_factory=list)
    supports: list[str] = field(default_factory=list)
    blocks: list[str] = field(default_factory=list)
    missing_bridges: list[str] = field(default_factory=list)
    hard_blocks: list[str] = field(default_factory=list)
    soft_blocks: list[str] = field(default_factory=list)
    confidence_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResponsePayload:
    summary: str
    verdict: Verdict | None
    main_supports: list[str]
    main_blockers: list[str]
    missing_bridges: list[str]
    smallest_fix: list[str]
    confidence: float
    supported_in_phase_one: bool = True
    unsupported_reason: str | None = None


@dataclass(frozen=True)
class NarrativeValidationRun:
    request: NormalizedTaskRequest
    state: CanonicalState
    evaluation: EvaluationPacket
    response: ResponsePayload

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
