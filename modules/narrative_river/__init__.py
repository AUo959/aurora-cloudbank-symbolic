"""Narrative River Adapter contracts and explicit workflow trigger.

The package can persist operator-approved scene frames and deltas inside an
explicit workspace. It does not mutate GUMAS simulation state, rewrite prose,
write CanonRec, or promote canon.
"""

from .adapter import NarrativeRiverAdapter
from .models import (
    SUPPORTED_SCHEMA_VERSION,
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
from .storage import NarrativeRiverStore, load_delta_file, load_frame_file
from .validator import validate_draft
from .workflow import NarrativeRiverWorkflow, SceneRunRequest

__all__ = [
    "SUPPORTED_SCHEMA_VERSION",
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
    "NarrativeRiverStore",
    "NarrativeRiverWorkflow",
    "SceneRunRequest",
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
    "load_delta_file",
    "load_frame_file",
    "loads_json",
    "loads_yaml",
    "render_prompt_contract",
    "validate_draft",
]
