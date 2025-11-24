"""
Event Models for Multi-Agent Coordination Registry

Defines the event schema and taxonomy for the R-2 agent ecosystem,
following Aurora's DLP tracking and symbolic anchor patterns.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from src.core.time_utils import utc_now


class EventPriority(str, Enum):
    """Event priority levels for routing"""

    CRITICAL = "critical"  # <10ms target latency
    HIGH = "high"  # <50ms target latency
    NORMAL = "normal"  # <100ms target latency
    LOW = "low"  # Best effort


class EventType(str, Enum):
    """Taxonomy of R-2 ecosystem events"""

    # Agent lifecycle events
    AGENT_STARTED = "agent.started"
    AGENT_STOPPED = "agent.stopped"
    AGENT_HEARTBEAT = "agent.heartbeat"

    # Task and workflow events
    TASK_CREATED = "task.created"
    TASK_ASSIGNED = "task.assigned"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"

    # Conflict and coordination events
    CONFLICT_DETECTED = "conflict.detected"
    CONFLICT_RESOLVED = "conflict.resolved"
    LOCK_ACQUIRED = "lock.acquired"
    LOCK_RELEASED = "lock.released"

    # System and monitoring events
    SYSTEM_ALERT = "system.alert"
    METRIC_REPORTED = "metric.reported"
    AUDIT_LOG = "audit.log"

    # Custom events
    CUSTOM = "custom"


class EventStatus(str, Enum):
    """Event processing status"""

    PENDING = "pending"
    PROCESSING = "processing"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


class Event(BaseModel):
    """
    Core event model with DLP tracking and symbolic anchors

    Following Aurora canonical patterns:
    - DLP tracking with context_tag and symbolic_hash_validation
    - T1/SRB anchors for temporal and symbolic reference
    - Memory seals for quantum memory integrity
    """

    # Event identification
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    priority: EventPriority = EventPriority.NORMAL
    status: EventStatus = EventStatus.PENDING

    # Event metadata
    source_agent_id: str
    target_agent_ids: Optional[List[str]] = None  # None = broadcast to all subscribers
    timestamp: datetime = Field(default_factory=utc_now)
    expiry: Optional[datetime] = None

    # Event payload
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # DLP tracking (Aurora canonical pattern)
    context_tag: str = Field(default="COORD_EVENT")
    symbolic_hash_validation: bool = Field(default=True)
    dlp_level: str = Field(default="DLP_L1_OK")

    # T1/SRB anchors (Aurora canonical pattern)
    t1_anchor: Optional[str] = None
    srb_anchor: Optional[str] = None

    # Memory seal (Aurora canonical pattern)
    memory_seal: Optional[str] = None

    # Routing and delivery tracking
    delivery_attempts: int = Field(default=0)
    last_delivery_attempt: Optional[datetime] = None
    delivered_to: List[str] = Field(default_factory=list)

    model_config = ConfigDict()

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return self.model_dump()

    def is_expired(self) -> bool:
        """Check if event has expired"""
        if self.expiry is None:
            return False
        return datetime.now(timezone.utc) > self.expiry


class EventFilter(BaseModel):
    """Filter criteria for event subscription"""

    event_types: Optional[List[EventType]] = None
    priorities: Optional[List[EventPriority]] = None
    source_agent_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    context_tags: Optional[List[str]] = None

    def matches(self, event: Event) -> bool:
        """Check if event matches filter criteria"""
        if self.event_types and event.event_type not in self.event_types:
            return False
        if self.priorities and event.priority not in self.priorities:
            return False
        if self.source_agent_ids and event.source_agent_id not in self.source_agent_ids:
            return False
        if self.context_tags and event.context_tag not in self.context_tags:
            return False
        if self.tags:
            event_tags = event.metadata.get("tags", [])
            if not any(tag in event_tags for tag in self.tags):
                return False
        return True


class Subscription(BaseModel):
    """Event subscription model"""

    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    filter: EventFilter
    created_at: datetime = Field(default_factory=utc_now)
    active: bool = Field(default=True)

    # Subscription metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConflictReport(BaseModel):
    """Report of detected conflict between agents"""

    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: str
    detected_at: datetime = Field(default_factory=utc_now)

    # Conflicting agents and resources
    agent_ids: List[str]
    resource_id: str
    resource_type: str

    # Conflict details
    description: str
    severity: str = "medium"  # low, medium, high, critical

    # Resolution tracking
    resolution_status: str = "unresolved"  # unresolved, resolving, resolved
    resolution_strategy: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None

    # DLP tracking
    context_tag: str = Field(default="COORD_CONFLICT")


class WorkflowDefinition(BaseModel):
    """Multi-agent workflow definition"""

    workflow_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str

    # Workflow steps
    steps: List[Dict[str, Any]]

    # Agent assignments
    agent_assignments: Dict[str, str]  # step_id -> agent_id

    # Workflow metadata
    created_at: datetime = Field(default_factory=utc_now)
    created_by: str
    status: str = "pending"  # pending, running, completed, failed

    # DLP tracking
    context_tag: str = Field(default="COORD_WORKFLOW")
