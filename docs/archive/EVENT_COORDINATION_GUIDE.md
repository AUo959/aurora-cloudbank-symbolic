# Multi-Agent Event Coordination Registry

## Overview

The Event Coordination Registry provides a centralized pub-sub system for multiple R-2 agents to coordinate their activities, share events, detect conflicts, and orchestrate complex workflows.

## Features

- **Event Publishing & Subscription**: Async pub-sub with filter-based routing
- **Priority-Based Delivery**: Critical events delivered within 10ms target latency
- **Conflict Detection**: Automatic detection and resolution of resource conflicts
- **Resource Locking**: Distributed lock management with TTL support
- **Workflow Orchestration**: Multi-agent workflow coordination
- **Event Replay**: Historical event replay for audit and recovery
- **DLP Tracking**: Full DLP compliance with symbolic anchors (Aurora patterns)

## Architecture

### Components

1. **Event Models** (`event_models.py`): Core data models
   - `Event`: Base event with DLP tracking and symbolic anchors
   - `EventFilter`: Subscription filter criteria
   - `Subscription`: Event subscription tracking
   - `ConflictReport`: Conflict detection and resolution
   - `WorkflowDefinition`: Multi-agent workflow orchestration

2. **Event Registry** (`event_registry.py`): Core coordination logic
   - In-memory pub-sub with async/await
   - Thread-safe operations with asyncio locks
   - Priority-based event routing
   - Conflict detection and resource locking

3. **FastAPI Integration** (`event_api.py`): REST API endpoints
   - Event publishing and subscription
   - Conflict detection and resolution
   - Workflow orchestration
   - Monitoring and metrics

## Quick Start

### 1. Publishing Events

```python
from src.coordination.event_models import Event, EventType, EventPriority
from src.coordination.event_registry import get_event_registry

# Get registry instance
registry = get_event_registry()

# Create and publish event
event = Event(
    event_type=EventType.TASK_CREATED,
    priority=EventPriority.HIGH,
    source_agent_id="r2-agent-001",
    payload={
        "task_id": "task-123",
        "description": "Process dataset",
        "deadline": "2024-01-15T12:00:00Z"
    },
    context_tag="COORD_TASK",
    t1_anchor="T1_001",
    srb_anchor="SRB_001"
)

result = await registry.publish_event(event)
print(f"Published event {result['event_id']}, delivered to {result['delivered_count']} subscribers")
```

### 2. Subscribing to Events

```python
from src.coordination.event_models import EventFilter, EventType, EventPriority

# Define event handler
async def handle_task_event(event: Event):
    print(f"Received task event: {event.payload}")
    # Process task...

# Create filter
event_filter = EventFilter(
    event_types=[EventType.TASK_CREATED, EventType.TASK_ASSIGNED],
    priorities=[EventPriority.HIGH, EventPriority.CRITICAL]
)

# Subscribe
subscription = await registry.subscribe(
    agent_id="r2-agent-001",
    event_filter=event_filter,
    handler=handle_task_event
)

print(f"Subscribed with ID: {subscription['subscription_id']}")
```

### 3. Conflict Detection

```python
# Detect potential conflicts before performing operations
conflict = await registry.detect_conflict(
    agent_id="r2-agent-001",
    resource_id="dataset-123",
    resource_type="dataset",
    operation="write"
)

if conflict:
    print(f"Conflict detected: {conflict.description}")
    # Handle conflict...
else:
    # Safe to proceed
    pass
```

### 4. Resource Locking

```python
# Acquire exclusive lock
lock_result = await registry.acquire_lock(
    agent_id="r2-agent-001",
    resource_id="dataset-123",
    ttl_seconds=300  # Lock expires after 5 minutes
)

if lock_result["success"]:
    try:
        # Perform operations on resource
        process_dataset("dataset-123")
    finally:
        # Release lock
        await registry.release_lock(
            agent_id="r2-agent-001",
            resource_id="dataset-123"
        )
else:
    print(f"Could not acquire lock: {lock_result['error']}")
```

### 5. Workflow Orchestration

```python
from src.coordination.event_models import WorkflowDefinition

# Define multi-agent workflow
workflow = WorkflowDefinition(
    name="Data Processing Pipeline",
    description="Multi-stage data processing with validation",
    steps=[
        {"step_id": "fetch", "action": "fetch_data", "timeout": 60},
        {"step_id": "process", "action": "process_data", "timeout": 300},
        {"step_id": "validate", "action": "validate_results", "timeout": 30}
    ],
    agent_assignments={
        "fetch": "r2-agent-001",
        "process": "r2-agent-002",
        "validate": "r2-agent-003"
    },
    created_by="orchestrator"
)

# Create workflow
result = await registry.create_workflow(workflow)
print(f"Created workflow: {result['workflow_id']}")

# Check workflow status
status = await registry.get_workflow_status(workflow.workflow_id)
print(f"Workflow status: {status['status']}")
```

### 6. Event Discovery and Replay

```python
from datetime import datetime, timedelta

# Discover recent events
recent_events = await registry.discover_events(
    filter=EventFilter(
        event_types=[EventType.TASK_COMPLETED, EventType.TASK_FAILED]
    )
)
print(f"Found {len(recent_events)} recent task completion events")

# Replay events for audit
start_time = datetime.utcnow() - timedelta(hours=1)
historical_events = await registry.replay_events(
    agent_id="r2-agent-001",
    start_time=start_time
)
print(f"Replayed {len(historical_events)} events from last hour")
```

## REST API Usage

### Publishing Events via API

```bash
curl -X POST http://localhost:8000/api/coordination/events/publish \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "task.created",
    "priority": "high",
    "source_agent_id": "r2-agent-001",
    "payload": {
      "task_id": "task-123",
      "description": "Process data"
    }
  }'
```

### Subscribing via API

```bash
curl -X POST http://localhost:8000/api/coordination/subscriptions/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "r2-agent-001",
    "event_types": ["task.created", "task.assigned"],
    "priorities": ["high", "critical"]
  }'
```

### Acquiring Lock via API

```bash
curl -X POST http://localhost:8000/api/coordination/locks/acquire \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "r2-agent-001",
    "resource_id": "dataset-123",
    "resource_type": "dataset",
    "ttl_seconds": 300
  }'
```

### Getting Metrics via API

```bash
curl http://localhost:8000/api/coordination/metrics
```

## Event Types

### Agent Lifecycle
- `agent.started` - Agent has started and is ready
- `agent.stopped` - Agent has stopped
- `agent.heartbeat` - Agent heartbeat signal

### Task Management
- `task.created` - New task has been created
- `task.assigned` - Task has been assigned to an agent
- `task.completed` - Task has been completed successfully
- `task.failed` - Task has failed

### Workflow
- `workflow.started` - Multi-agent workflow has started
- `workflow.completed` - Multi-agent workflow has completed

### Conflict and Coordination
- `conflict.detected` - Conflict detected between agents
- `conflict.resolved` - Conflict has been resolved
- `lock.acquired` - Resource lock has been acquired
- `lock.released` - Resource lock has been released

### System
- `system.alert` - System alert or notification
- `metric.reported` - Metric or telemetry data reported
- `audit.log` - Audit log entry
- `custom` - Custom event type

## Event Priorities

Events are routed based on priority with different latency targets:

- **CRITICAL**: <10ms target latency - System alerts, critical failures
- **HIGH**: <50ms target latency - Important task events, conflicts
- **NORMAL**: <100ms target latency - Regular task and workflow events
- **LOW**: Best effort - Metrics, heartbeats, audit logs

## Event Filtering

Event filters support multiple criteria:

```python
EventFilter(
    event_types=[EventType.TASK_CREATED, EventType.TASK_ASSIGNED],
    priorities=[EventPriority.HIGH, EventPriority.CRITICAL],
    source_agent_ids=["r2-agent-001", "r2-agent-002"],
    tags=["production", "data-pipeline"],
    context_tags=["COORD_TASK", "COORD_WORKFLOW"]
)
```

All criteria are combined with AND logic - an event must match all specified criteria.

## Conflict Resolution Strategies

When conflicts are detected, they can be resolved using various strategies:

- **priority_based**: Higher priority agent gets resource
- **first_come_first_served**: First agent to request gets resource
- **round_robin**: Resources distributed evenly across agents
- **custom**: Application-specific resolution logic

## DLP Tracking

All events follow Aurora's DLP tracking patterns:

- **context_tag**: Operation context identifier (e.g., "COORD_EVENT", "COORD_TASK")
- **symbolic_hash_validation**: Data integrity validation flag
- **dlp_level**: DLP compliance level (e.g., "DLP_L1_OK")
- **t1_anchor**: Temporal reference anchor
- **srb_anchor**: Symbolic Reference Base anchor
- **memory_seal**: Quantum memory integrity marker

## Performance Considerations

### In-Memory Implementation

The current implementation uses in-memory data structures for:
- Fast event delivery (<100ms for normal priority)
- Zero external dependencies
- Simple deployment and testing

### Scaling Options

For distributed deployments, consider:

1. **Redis Backend**: Replace in-memory storage with Redis
   - Pub/sub support
   - Persistence and replication
   - Cluster mode for horizontal scaling

2. **RabbitMQ**: For complex routing and guaranteed delivery
   - Exchange/queue topology
   - Message acknowledgments
   - Dead letter queues

3. **Apache Kafka**: For high-throughput event streaming
   - Partition-based scaling
   - Event replay from offset
   - Consumer groups

## Monitoring and Metrics

Monitor registry health with the metrics endpoint:

```python
metrics = await registry.get_metrics()

# Key metrics:
# - events_published: Total events published
# - events_delivered: Successfully delivered events
# - events_failed: Failed delivery attempts
# - conflicts_detected: Total conflicts detected
# - conflicts_resolved: Successfully resolved conflicts
# - active_subscriptions: Current active subscriptions
# - active_locks: Current resource locks
# - open_conflicts: Unresolved conflicts
```

## Best Practices

1. **Use appropriate priorities**: Reserve CRITICAL for actual critical events
2. **Set reasonable TTLs**: Lock TTLs should match operation duration
3. **Handle conflicts gracefully**: Always check for conflicts before critical operations
4. **Clean up subscriptions**: Unsubscribe when no longer needed
5. **Monitor metrics**: Track event delivery success rates
6. **Use targeted delivery**: Specify target_agent_ids when broadcasting isn't needed
7. **Include DLP tracking**: Always set context_tag and symbolic anchors
8. **Test with event replay**: Use replay for debugging and recovery scenarios

## Security Considerations

1. **Authentication**: API endpoints should require authentication (add to aurora_api.py)
2. **Authorization**: Validate agent IDs against authorized agents
3. **Rate Limiting**: Prevent event flooding with rate limits
4. **Input Validation**: Validate all event payloads
5. **Audit Logging**: All events include audit trail via event history

## Integration with Aurora API

To integrate with Aurora's main API server (aurora_api.py):

```python
from src.coordination.event_api import router as coordination_router

# In aurora_api.py, add:
app.include_router(coordination_router)
```

This exposes all coordination endpoints under `/api/coordination/`.

## Testing

Run the comprehensive test suite:

```bash
# Run all coordination tests
pytest tests/test_event_coordination.py -v

# Run specific test class
pytest tests/test_event_coordination.py::TestEventCoordinationRegistry -v

# Run with coverage
pytest tests/test_event_coordination.py --cov=src/coordination
```

## Troubleshooting

### Events not being delivered

1. Check subscription is active: `await registry.get_subscriptions(agent_id)`
2. Verify filter matches event: Test with `filter.matches(event)`
3. Check handler errors in logs
4. Verify event hasn't expired: `event.is_expired()`

### Lock acquisition failing

1. Check if resource already locked: Look for "resource_locked" error
2. Wait for lock TTL to expire
3. Verify lock was released properly
4. Check for conflicts: `await registry.detect_conflict(...)`

### Performance issues

1. Monitor delivery latency with metrics
2. Check for slow event handlers
3. Consider reducing event history size
4. Move to Redis/Kafka for distributed workloads

## Future Enhancements

- [ ] Persistence layer (SQLite/PostgreSQL)
- [ ] Redis pub/sub backend
- [ ] RabbitMQ integration
- [ ] Kafka streaming support
- [ ] Event schema validation
- [ ] Webhook notifications
- [ ] WebSocket event streaming
- [ ] Distributed tracing integration
- [ ] GraphQL subscription API
- [ ] Multi-tenancy support
