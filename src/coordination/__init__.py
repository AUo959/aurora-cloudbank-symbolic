"""
Multi-Agent Event Coordination System

Provides centralized event coordination, pub-sub messaging, conflict detection,
and workflow orchestration for R-2 agent ecosystem.
"""

from src.coordination.event_models import (
    ConflictReport,
    Event,
    EventFilter,
    EventPriority,
    EventStatus,
    EventType,
    Subscription,
    WorkflowDefinition,
)
from src.coordination.event_registry import EventCoordinationRegistry, get_event_registry

__all__ = [
    # Core models
    "Event",
    "EventType",
    "EventPriority",
    "EventStatus",
    "EventFilter",
    "Subscription",
    "ConflictReport",
    "WorkflowDefinition",
    # Registry
    "EventCoordinationRegistry",
    "get_event_registry",
]

__version__ = "1.0.0"
