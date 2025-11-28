# Event Coordination Registry - Quick Reference

## Core Concepts

### Event Types
```python
EventType.AGENT_STARTED      # Agent lifecycle
EventType.AGENT_STOPPED
EventType.AGENT_HEARTBEAT

EventType.TASK_CREATED       # Task management
EventType.TASK_ASSIGNED
EventType.TASK_COMPLETED
EventType.TASK_FAILED

EventType.WORKFLOW_STARTED   # Workflows
EventType.WORKFLOW_COMPLETED

EventType.CONFLICT_DETECTED  # Coordination
EventType.CONFLICT_RESOLVED
EventType.LOCK_ACQUIRED
EventType.LOCK_RELEASED

EventType.SYSTEM_ALERT       # System
EventType.METRIC_REPORTED
EventType.AUDIT_LOG
```

### Event Priorities
```python
EventPriority.CRITICAL  # <10ms target latency
EventPriority.HIGH      # <50ms target latency
EventPriority.NORMAL    # <100ms target latency
EventPriority.LOW       # Best effort (1s)
```

## Common Patterns

### 1. Publish Event
```python
from src.coordination import get_event_registry, Event, EventType, EventPriority

registry = get_event_registry()

event = Event(
    event_type=EventType.TASK_CREATED,
    priority=EventPriority.HIGH,
    source_agent_id="r2-agent-001",
    payload={"task_id": "task-123", "data": "..."},
    context_tag="COORD_TASK"
)

result = await registry.publish_event(event)
# result: {"success": True, "event_id": "...", "delivered_count": N}
```

### 2. Subscribe to Events
```python
from src.coordination import EventFilter

async def my_handler(event: Event):
    print(f"Received: {event.payload}")

filter = EventFilter(
    event_types=[EventType.TASK_CREATED, EventType.TASK_ASSIGNED],
    priorities=[EventPriority.HIGH, EventPriority.CRITICAL]
)

subscription = await registry.subscribe(
    agent_id="r2-agent-001",
    event_filter=filter,
    handler=my_handler
)
# subscription: {"success": True, "subscription_id": "..."}
```

### 3. Acquire Resource Lock
```python
# Acquire lock
lock_result = await registry.acquire_lock(
    agent_id="r2-agent-001",
    resource_id="dataset-123",
    ttl_seconds=300
)

if lock_result["success"]:
    try:
        # Do work with resource
        process_data("dataset-123")
    finally:
        # Always release
        await registry.release_lock(
            agent_id="r2-agent-001",
            resource_id="dataset-123"
        )
```

### 4. Detect Conflicts
```python
conflict = await registry.detect_conflict(
    agent_id="r2-agent-001",
    resource_id="dataset-123",
    resource_type="dataset",
    operation="write"
)

if conflict:
    # Handle conflict
    print(f"Conflict: {conflict.description}")
    # Resolve
    await registry.resolve_conflict(
        conflict_id=conflict.conflict_id,
        strategy="priority_based",
        resolved_by="r2-agent-001"
    )
```

### 5. Create Workflow
```python
from src.coordination import WorkflowDefinition

workflow = WorkflowDefinition(
    name="Data Pipeline",
    description="Multi-stage processing",
    steps=[
        {"step_id": "fetch", "action": "fetch_data"},
        {"step_id": "process", "action": "process_data"}
    ],
    agent_assignments={
        "fetch": "r2-agent-001",
        "process": "r2-agent-002"
    },
    created_by="orchestrator"
)

result = await registry.create_workflow(workflow)
# result: {"success": True, "workflow_id": "..."}
```

### 6. Event Discovery
```python
# Discover all recent events
events = await registry.discover_events()

# Discover with filter
filter = EventFilter(priorities=[EventPriority.HIGH])
high_priority_events = await registry.discover_events(filter=filter)
```

### 7. Event Replay
```python
from datetime import datetime, timedelta

# Replay last hour of events
start_time = datetime.utcnow() - timedelta(hours=1)
events = await registry.replay_events(
    agent_id="r2-agent-001",
    start_time=start_time
)
```

### 8. Get Metrics
```python
metrics = await registry.get_metrics()

print(f"Events published: {metrics['metrics']['events_published']}")
print(f"Conflicts detected: {metrics['metrics']['conflicts_detected']}")
print(f"Active subscriptions: {metrics['counts']['active_subscriptions']}")
```

## REST API Quick Reference

### Publish Event
```bash
POST /api/coordination/events/publish
{
  "event_type": "task.created",
  "priority": "high",
  "source_agent_id": "r2-agent-001",
  "payload": {"task_id": "task-123"}
}
```

### Subscribe
```bash
POST /api/coordination/subscriptions/subscribe
{
  "agent_id": "r2-agent-001",
  "event_types": ["task.created"],
  "priorities": ["high", "critical"]
}
```

### Unsubscribe
```bash
DELETE /api/coordination/subscriptions/{subscription_id}
```

### Get Subscriptions
```bash
GET /api/coordination/subscriptions/{agent_id}
```

### Discover Events
```bash
GET /api/coordination/events/discover?event_types=task.created&priorities=high
```

### Replay Events
```bash
GET /api/coordination/events/replay/{agent_id}?start_time=2024-01-01T00:00:00Z
```

### Detect Conflict
```bash
POST /api/coordination/conflicts/detect
{
  "agent_id": "r2-agent-001",
  "resource_id": "dataset-123",
  "resource_type": "dataset",
  "operation": "write"
}
```

### Resolve Conflict
```bash
POST /api/coordination/conflicts/resolve
{
  "conflict_id": "conflict-123",
  "strategy": "priority_based",
  "resolved_by": "r2-agent-001"
}
```

### Acquire Lock
```bash
POST /api/coordination/locks/acquire
{
  "agent_id": "r2-agent-001",
  "resource_id": "dataset-123",
  "ttl_seconds": 300
}
```

### Release Lock
```bash
DELETE /api/coordination/locks/{resource_id}?agent_id=r2-agent-001
```

### Create Workflow
```bash
POST /api/coordination/workflows/create
{
  "name": "Data Pipeline",
  "description": "Multi-stage processing",
  "steps": [{"step_id": "fetch", "action": "fetch_data"}],
  "agent_assignments": {"fetch": "r2-agent-001"},
  "created_by": "orchestrator"
}
```

### Get Workflow Status
```bash
GET /api/coordination/workflows/{workflow_id}
```

### Get Metrics
```bash
GET /api/coordination/metrics
```

### Get Status
```bash
GET /api/coordination/status
```

### List Event Types
```bash
GET /api/coordination/event-types
```

## Best Practices

### ✅ DO
- Use appropriate priority levels (reserve CRITICAL for actual critical events)
- Set reasonable TTL for locks (match operation duration)
- Always release locks in finally blocks
- Check for conflicts before critical operations
- Unsubscribe when no longer needed
- Include DLP tracking (context_tag, anchors)
- Use targeted delivery when possible (specify target_agent_ids)
- Monitor metrics regularly

### ❌ DON'T
- Don't abuse CRITICAL priority (causes unnecessary load)
- Don't forget to release locks (causes deadlocks)
- Don't create subscriptions without cleanup
- Don't ignore conflict detection results
- Don't publish events without context_tag
- Don't broadcast when targeted delivery suffices
- Don't skip error handling in event handlers

## Troubleshooting

### Events not being delivered?
1. Check subscription is active: `get_subscriptions(agent_id)`
2. Verify filter matches event: `filter.matches(event)`
3. Check for handler exceptions in logs
4. Verify event hasn't expired

### Lock acquisition failing?
1. Check if already locked: Look for "resource_locked" error
2. Wait for TTL expiry
3. Check conflict detection results
4. Verify lock was released properly

### Performance issues?
1. Monitor delivery latency via metrics
2. Check for slow event handlers (add timeouts)
3. Reduce event history size if memory constrained
4. Consider Redis/Kafka for distributed workloads

## Configuration

### History Size
```python
registry = EventCoordinationRegistry(max_history=10000)  # default
```

### Lock TTL
```python
await registry.acquire_lock(
    agent_id="agent-001",
    resource_id="resource-123",
    ttl_seconds=300  # 5 minutes
)
```

## Integration

### Add to Aurora API
Already integrated! Events available at `/api/coordination/*`

### Get Registry Instance
```python
from src.coordination import get_event_registry
registry = get_event_registry()  # Singleton
```

## Resources

- **Full Documentation**: `docs/EVENT_COORDINATION_GUIDE.md`
- **API Docs**: http://localhost:8000/docs (when server running)
- **Demo Script**: `examples/event_coordination_demo.py`
- **Tests**: `tests/test_event_coordination.py`
- **Implementation Summary**: `EVENT_COORDINATION_IMPLEMENTATION_SUMMARY.md`
