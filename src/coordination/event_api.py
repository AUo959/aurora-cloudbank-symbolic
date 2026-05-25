"""
FastAPI Endpoints for Multi-Agent Event Coordination Registry

Provides REST API for event publishing, subscription, discovery,
conflict detection, and workflow orchestration.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from src.middleware.exception_handler import processing_handler, integration_handler
from src.middleware.fastapi_security import require_csrf_token

from src.coordination.event_models import (
    ConflictReport,
    Event,
    EventFilter,
    EventPriority,
    EventType,
    WorkflowDefinition,
)
from src.coordination.event_registry import get_event_registry

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/coordination", tags=["Event Coordination"])


# Request/Response models
class PublishEventRequest(BaseModel):
    """Request to publish an event"""

    event_type: EventType
    priority: EventPriority = EventPriority.NORMAL
    source_agent_id: str
    target_agent_ids: Optional[List[str]] = None
    payload: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    context_tag: str = "COORD_EVENT"
    t1_anchor: Optional[str] = None
    srb_anchor: Optional[str] = None


class SubscribeRequest(BaseModel):
    """Request to subscribe to events"""

    agent_id: str
    event_types: Optional[List[EventType]] = None
    priorities: Optional[List[EventPriority]] = None
    source_agent_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    context_tags: Optional[List[str]] = None


class LockRequest(BaseModel):
    """Request to acquire resource lock"""

    agent_id: str
    resource_id: str
    resource_type: str = "generic"
    ttl_seconds: int = 300


class ConflictDetectionRequest(BaseModel):
    """Request to detect conflicts"""

    agent_id: str
    resource_id: str
    resource_type: str
    operation: str


class ConflictResolutionRequest(BaseModel):
    """Request to resolve conflict"""

    conflict_id: str
    strategy: str
    resolved_by: str


# Event Publishing Endpoints
@router.post("/events/publish", dependencies=[Depends(require_csrf_token)])
async def publish_event(request: PublishEventRequest) -> Dict[str, Any]:
    """
    Publish event to coordination registry

    **Example:**
    ```json
    {
        "event_type": "task.created",
        "priority": "normal",
        "source_agent_id": "r2-agent-001",
        "payload": {
            "task_id": "task-123",
            "description": "Process data"
        }
    }
    ```
    """
    try:
        registry = get_event_registry()

        # Create event
        event = Event(
            event_type=request.event_type,
            priority=request.priority,
            source_agent_id=request.source_agent_id,
            target_agent_ids=request.target_agent_ids,
            payload=request.payload,
            metadata=request.metadata,
            context_tag=request.context_tag,
            t1_anchor=request.t1_anchor,
            srb_anchor=request.srb_anchor,
        )

        # Publish
        result = await registry.publish_event(event)

        return {
            "success": True,
            "event_id": result["event_id"],
            "delivered_count": result["delivered_count"],
            "delivered_to": result["delivered_to"],
        }

    except Exception as e:
        logger.error(f"Error publishing event: {e}")
        raise HTTPException(status_code=500, detail="Event publication failed")


# Subscription Endpoints
@router.post("/subscriptions/subscribe", dependencies=[Depends(require_csrf_token)])
async def subscribe_to_events(request: SubscribeRequest) -> Dict[str, Any]:
    """
    Subscribe to events matching filter criteria

    **Example:**
    ```json
    {
        "agent_id": "r2-agent-001",
        "event_types": ["task.created", "task.assigned"],
        "priorities": ["high", "critical"]
    }
    ```
    """
    try:
        registry = get_event_registry()

        # Create filter
        event_filter = EventFilter(
            event_types=request.event_types,
            priorities=request.priorities,
            source_agent_ids=request.source_agent_ids,
            tags=request.tags,
            context_tags=request.context_tags,
        )

        # Subscribe
        result = await registry.subscribe(agent_id=request.agent_id, event_filter=event_filter)

        return {
            "success": True,
            "subscription_id": result["subscription_id"],
            "agent_id": result["agent_id"],
            "filter": result["filter"],
        }

    except Exception as e:
        logger.error(f"Error subscribing to events: {e}")
        raise HTTPException(status_code=500, detail="Subscription failed")


@router.delete("/subscriptions/{subscription_id}", dependencies=[Depends(require_csrf_token)])
async def unsubscribe_from_events(subscription_id: str) -> Dict[str, Any]:
    """
    Unsubscribe from events

    **Example:** DELETE /api/coordination/subscriptions/abc-123
    """
    try:
        registry = get_event_registry()
        result = await registry.unsubscribe(subscription_id)

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Subscription not found"))

        return {"success": True, "subscription_id": subscription_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing: {e}")
        raise HTTPException(status_code=500, detail="Unsubscribe failed")


@router.get("/subscriptions/{agent_id}")
async def get_agent_subscriptions(agent_id: str) -> Dict[str, Any]:
    """
    Get all active subscriptions for an agent

    **Example:** GET /api/coordination/subscriptions/r2-agent-001
    """
    try:
        registry = get_event_registry()
        subscriptions = await registry.get_subscriptions(agent_id)

        return {"success": True, "agent_id": agent_id, "subscriptions": subscriptions, "count": len(subscriptions)}

    except Exception as e:
        logger.error(f"Error retrieving subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve subscriptions")


# Event Discovery and Replay
@router.get("/events/discover")
async def discover_events(
    event_types: Optional[List[EventType]] = Query(None),
    priorities: Optional[List[EventPriority]] = Query(None),
    source_agent_ids: Optional[List[str]] = Query(None),
) -> Dict[str, Any]:
    """
    Discover available events based on filter criteria

    **Example:** GET /api/coordination/events/discover?event_types=task.created&priorities=high
    """
    try:
        registry = get_event_registry()

        # Create optional filter
        event_filter = None
        if event_types or priorities or source_agent_ids:
            event_filter = EventFilter(
                event_types=event_types, priorities=priorities, source_agent_ids=source_agent_ids
            )

        events = await registry.discover_events(filter=event_filter)

        return {"success": True, "events": events, "count": len(events)}

    except Exception as e:
        logger.error(f"Error discovering events: {e}")
        raise HTTPException(status_code=500, detail="Event discovery failed")


@router.get("/events/replay/{agent_id}")
async def replay_events(
    agent_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Replay historical events for audit or recovery

    **Example:** GET /api/coordination/events/replay/r2-agent-001?start_time=2024-01-01T00:00:00Z
    """
    try:
        registry = get_event_registry()

        # Parse datetime filters
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00")) if start_time else None
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00")) if end_time else None

        events = await registry.replay_events(agent_id, start_time=start_dt, end_time=end_dt)

        return {"success": True, "agent_id": agent_id, "events": events, "count": len(events)}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime format")
    except Exception as e:
        logger.error(f"Error replaying events: {e}")
        raise HTTPException(status_code=500, detail="Event replay failed")


# Conflict Detection and Resolution
@router.post("/conflicts/detect", dependencies=[Depends(require_csrf_token)])
async def detect_conflict(request: ConflictDetectionRequest) -> Dict[str, Any]:
    """
    Detect potential conflicts with other agents

    **Example:**
    ```json
    {
        "agent_id": "r2-agent-001",
        "resource_id": "dataset-123",
        "resource_type": "dataset",
        "operation": "write"
    }
    ```
    """
    try:
        registry = get_event_registry()

        conflict = await registry.detect_conflict(
            agent_id=request.agent_id,
            resource_id=request.resource_id,
            resource_type=request.resource_type,
            operation=request.operation,
        )

        if conflict:
            return {
                "success": True,
                "conflict_detected": True,
                "conflict": conflict.model_dump(),
            }
        else:
            return {"success": True, "conflict_detected": False}

    except Exception as e:
        logger.error(f"Error detecting conflict: {e}")
        raise HTTPException(status_code=500, detail="Conflict detection failed")


@router.post("/conflicts/resolve", dependencies=[Depends(require_csrf_token)])
async def resolve_conflict(request: ConflictResolutionRequest) -> Dict[str, Any]:
    """
    Mark conflict as resolved

    **Example:**
    ```json
    {
        "conflict_id": "conflict-123",
        "strategy": "priority_based",
        "resolved_by": "r2-agent-001"
    }
    ```
    """
    try:
        registry = get_event_registry()

        result = await registry.resolve_conflict(
            conflict_id=request.conflict_id, strategy=request.strategy, resolved_by=request.resolved_by
        )

        if not result["success"]:
            raise HTTPException(status_code=404, detail=result.get("error", "Conflict not found"))

        return {"success": True, "conflict_id": request.conflict_id, "strategy": request.strategy}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving conflict: {e}")
        raise HTTPException(status_code=500, detail="Conflict resolution failed")


# Resource Locking
@router.post("/locks/acquire", dependencies=[Depends(require_csrf_token)])
async def acquire_lock(request: LockRequest) -> Dict[str, Any]:
    """
    Acquire exclusive lock on resource

    **Example:**
    ```json
    {
        "agent_id": "r2-agent-001",
        "resource_id": "dataset-123",
        "resource_type": "dataset",
        "ttl_seconds": 300
    }
    ```
    """
    try:
        registry = get_event_registry()

        result = await registry.acquire_lock(
            agent_id=request.agent_id, resource_id=request.resource_id, ttl_seconds=request.ttl_seconds
        )

        if not result["success"]:
            raise HTTPException(status_code=409, detail=result.get("error", "Lock acquisition failed"))

        return {"success": True, "resource_id": request.resource_id, "expires_in": result["expires_in"]}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acquiring lock: {e}")
        raise HTTPException(status_code=500, detail="Lock acquisition failed")


@router.delete("/locks/{resource_id}", dependencies=[Depends(require_csrf_token)])
async def release_lock(resource_id: str, agent_id: str = Query(...)) -> Dict[str, Any]:
    """
    Release lock on resource

    **Example:** DELETE /api/coordination/locks/dataset-123?agent_id=r2-agent-001
    """
    try:
        registry = get_event_registry()

        result = await registry.release_lock(agent_id=agent_id, resource_id=resource_id)

        if not result["success"]:
            error = result.get("error", "Lock release failed")
            if error == "lock_not_found":
                raise HTTPException(status_code=404, detail="Lock not found")
            elif error == "lock_not_owned":
                raise HTTPException(status_code=403, detail="Lock not owned by this agent")
            else:
                raise HTTPException(status_code=400, detail=error)

        return {"success": True, "resource_id": resource_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error releasing lock: {e}")
        raise HTTPException(status_code=500, detail="Lock release failed")


# Workflow Orchestration
@router.post("/workflows/create", dependencies=[Depends(require_csrf_token)])
async def create_workflow(workflow: WorkflowDefinition) -> Dict[str, Any]:
    """
    Create multi-agent workflow

    **Example:**
    ```json
    {
        "name": "Data Processing Pipeline",
        "description": "Multi-stage data processing",
        "steps": [
            {"step_id": "step1", "action": "fetch_data"},
            {"step_id": "step2", "action": "process_data"}
        ],
        "agent_assignments": {
            "step1": "r2-agent-001",
            "step2": "r2-agent-002"
        },
        "created_by": "orchestrator"
    }
    ```
    """
    try:
        registry = get_event_registry()

        result = await registry.create_workflow(workflow)

        return {"success": True, "workflow_id": result["workflow_id"]}

    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail="Workflow creation failed")


@router.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """
    Get workflow status

    **Example:** GET /api/coordination/workflows/workflow-123
    """
    try:
        registry = get_event_registry()

        workflow = await registry.get_workflow_status(workflow_id)

        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return {"success": True, "workflow": workflow}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving workflow status: {e}")
        raise HTTPException(status_code=500, detail="Workflow status retrieval failed")


# Monitoring and Metrics
@router.get("/metrics")
async def get_registry_metrics() -> Dict[str, Any]:
    """
    Get coordination registry metrics and statistics

    **Example:** GET /api/coordination/metrics
    """
    try:
        registry = get_event_registry()
        metrics = await registry.get_metrics()

        return {"success": True, "metrics": metrics}

    except Exception as e:
        logger.error(f"Error retrieving metrics: {e}")
        raise HTTPException(status_code=500, detail="Metrics retrieval failed")


@router.get("/status")
async def get_registry_status() -> Dict[str, Any]:
    """
    Get coordination registry health status

    **Example:** GET /api/coordination/status
    """
    try:
        registry = get_event_registry()
        status = await registry.get_status()

        return {"success": True, "status": status}

    except Exception as e:
        logger.error(f"Error retrieving status: {e}")
        raise HTTPException(status_code=500, detail="Status retrieval failed")


# Event type discovery endpoint
@router.get("/event-types")
async def get_event_types() -> Dict[str, Any]:
    """
    Get list of available event types

    **Example:** GET /api/coordination/event-types
    """
    try:
        event_types = [
            {
                "type": event_type.value,
                "category": event_type.value.split(".")[0],
                "description": _get_event_type_description(event_type),
            }
            for event_type in EventType
        ]

        return {"success": True, "event_types": event_types, "count": len(event_types)}

    except Exception as e:
        logger.error(f"Error retrieving event types: {e}")
        raise HTTPException(status_code=500, detail="Event types retrieval failed")


def _get_event_type_description(event_type: EventType) -> str:
    """Get description for event type"""
    descriptions = {
        EventType.AGENT_STARTED: "Agent has started and is ready",
        EventType.AGENT_STOPPED: "Agent has stopped",
        EventType.AGENT_HEARTBEAT: "Agent heartbeat signal",
        EventType.TASK_CREATED: "New task has been created",
        EventType.TASK_ASSIGNED: "Task has been assigned to an agent",
        EventType.TASK_COMPLETED: "Task has been completed successfully",
        EventType.TASK_FAILED: "Task has failed",
        EventType.WORKFLOW_STARTED: "Multi-agent workflow has started",
        EventType.WORKFLOW_COMPLETED: "Multi-agent workflow has completed",
        EventType.CONFLICT_DETECTED: "Conflict detected between agents",
        EventType.CONFLICT_RESOLVED: "Conflict has been resolved",
        EventType.LOCK_ACQUIRED: "Resource lock has been acquired",
        EventType.LOCK_RELEASED: "Resource lock has been released",
        EventType.SYSTEM_ALERT: "System alert or notification",
        EventType.METRIC_REPORTED: "Metric or telemetry data reported",
        EventType.AUDIT_LOG: "Audit log entry",
        EventType.CUSTOM: "Custom event type",
    }
    return descriptions.get(event_type, "No description available")
