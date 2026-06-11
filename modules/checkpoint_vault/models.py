"""Checkpoint Vault — Pydantic v2 models.

Defines the data structures for ethical checkpoint records.

DLP: checkpoint_vault_models_v1
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CheckpointTrigger(str, Enum):
    """What caused this checkpoint to be created."""

    MANUAL = "manual"
    PRE_ACTION = "pre_action"
    POST_ACTION = "post_action"
    SCHEDULED = "scheduled"
    VIOLATION_DETECTED = "violation_detected"
    ROLLBACK_POINT = "rollback_point"


class CheckpointStatus(str, Enum):
    """Lifecycle state of a checkpoint."""

    ACTIVE = "active"
    ROLLED_BACK = "rolled_back"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class CheckpointRecord(BaseModel):
    """A single ethical checkpoint snapshot.

    Represents the captured state of an agent at a specific moment,
    along with the ethics compliance profile at the time of capture.

    DLP: checkpoint_vault_models_v1
    """

    model_config = ConfigDict(use_enum_values=True)

    checkpoint_id: str = Field(..., description="Unique CHKP-* identifier")
    agent_id: str = Field(..., description="ID of the agent whose state was captured")
    version: int = Field(..., ge=1, description="Monotonically increasing version per agent")
    trigger: CheckpointTrigger = Field(..., description="What caused this checkpoint")
    status: CheckpointStatus = Field(default=CheckpointStatus.ACTIVE)
    timestamp: str = Field(..., description="ISO-8601 UTC timestamp of capture")
    state_snapshot: Dict[str, Any] = Field(
        default_factory=dict,
        description="Serializable snapshot of the agent state at checkpoint time",
    )
    ethics_profile: Dict[str, Any] = Field(
        default_factory=dict,
        description="Ethics compliance data at checkpoint time",
    )
    parent_checkpoint_id: Optional[str] = Field(
        default=None, description="ID of the checkpoint this was spawned from"
    )
    tags: List[str] = Field(default_factory=list, description="Searchable labels")
    context_tag: str = Field(
        default="checkpoint_vault_v1", description="DLP context tag"
    )
    meta: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class CreateCheckpointRequest(BaseModel):
    """Request body for POST /checkpoint/create."""

    agent_id: str
    trigger: CheckpointTrigger = CheckpointTrigger.MANUAL
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    ethics_profile: Dict[str, Any] = Field(default_factory=dict)
    parent_checkpoint_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    context_tag: str = "checkpoint_vault_v1"
    meta: Dict[str, Any] = Field(default_factory=dict)


class RollbackRequest(BaseModel):
    """Request body for POST /checkpoint/{id}/rollback."""

    reason: str = Field(..., description="Why this rollback is being performed")
    performed_by: str = Field(default="system", description="Actor performing the rollback")


class CheckpointSummary(BaseModel):
    """Lightweight listing item for GET /checkpoint."""

    checkpoint_id: str
    agent_id: str
    version: int
    trigger: str
    status: str
    timestamp: str
    tag_count: int
    context_tag: str = "checkpoint_vault_v1"


class VaultHealthResponse(BaseModel):
    """GET /checkpoint/health response."""

    status: str
    total_checkpoints: int
    active_checkpoints: int
    agents_tracked: int
    timestamp: str
    context_tag: str = "checkpoint_vault_v1"
