"""Passive Narrative River Adapter foundation.

This package validates scene-state frames, renders deterministic prose contracts,
and reports advisory prose findings. It does not write canon, mutate simulation
state, persist memory, or rewrite narrative text.
"""

from .adapter import NarrativeRiverAdapter
from .models import (
    ActorInterpretation,
    AuthorityStatus,
    CanonSnapshot,
    ChannelCondition,
    EquipmentState,
    EvidenceClaim,
    EvidenceStatus,
    IncomingFlow,
    InstitutionalConstraint,
    NarrativeReservoir,
    NarrativeRiverFrame,
    NarrativeSediment,
    NarrativeState,
    NarrativeStatus,
    PersistenceClass,
    ProvenanceRef,
    RelationshipState,
    ScarcityState,
    SceneObjective,
    SceneRiverDelta,
    ValidationFinding,
    ValidationReport,
    ValidationSeverity,
    Viewpoint,
)
from .prompt_contract import render_prompt_contract
from .serialization import dumps_json, dumps_yaml, loads_json, loads_yaml
from .validator import validate_draft

__all__ = [
    "ActorInterpretation",
    "AuthorityStatus",
    "CanonSnapshot",
    "ChannelCondition",
    "EquipmentState",
    "EvidenceClaim",
    "EvidenceStatus",
    "IncomingFlow",
    "InstitutionalConstraint",
    "NarrativeReservoir",
    "NarrativeRiverAdapter",
    "NarrativeRiverFrame",
    "NarrativeSediment",
    "NarrativeState",
    "NarrativeStatus",
    "PersistenceClass",
    "ProvenanceRef",
    "RelationshipState",
    "ScarcityState",
    "SceneObjective",
    "SceneRiverDelta",
    "ValidationFinding",
    "ValidationReport",
    "ValidationSeverity",
    "Viewpoint",
    "dumps_json",
    "dumps_yaml",
    "loads_json",
    "loads_yaml",
    "render_prompt_contract",
    "validate_draft",
]
