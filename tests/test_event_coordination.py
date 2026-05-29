"""
Tests for Multi-Agent Event Coordination Registry

Validates event publishing, subscription, conflict detection,
workflow orchestration, and all coordination features.
"""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from src.coordination.event_models import (
    ConflictReport,
    Event,
    EventFilter,
    EventPriority,
    EventType,
    Subscription,
    WorkflowDefinition,
)
from src.coordination.event_registry import EventCoordinationRegistry


class TestEventModels:
    """Test event data models"""

    def test_event_creation(self):
        """Test basic event creation"""
        event = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-001", payload={"task_id": "task-123"})

        assert event.event_id is not None
        assert event.event_type == EventType.TASK_CREATED
        assert event.source_agent_id == "agent-001"
        assert event.priority == EventPriority.NORMAL
        assert event.context_tag == "COORD_EVENT"
        assert event.symbolic_hash_validation is True

    def test_event_expiry(self):
        """Test event expiry checking"""
        # Event with no expiry
        event = Event(event_type=EventType.AGENT_HEARTBEAT, source_agent_id="agent-001")
        assert not event.is_expired()

        # Event with future expiry
        event.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        assert not event.is_expired()

        # Event with past expiry
        event.expiry = datetime.now(timezone.utc) - timedelta(hours=1)
        assert event.is_expired()

    def test_event_filter_matching(self):
        """Test event filter matching"""
        event = Event(
            event_type=EventType.TASK_CREATED,
            priority=EventPriority.HIGH,
            source_agent_id="agent-001",
            payload={},
            context_tag="COORD_TASK",
        )

        # Filter matches event type
        filter1 = EventFilter(event_types=[EventType.TASK_CREATED])
        assert filter1.matches(event)

        # Filter matches priority
        filter2 = EventFilter(priorities=[EventPriority.HIGH])
        assert filter2.matches(event)

        # Filter matches source agent
        filter3 = EventFilter(source_agent_ids=["agent-001"])
        assert filter3.matches(event)

        # Filter matches context tag
        filter4 = EventFilter(context_tags=["COORD_TASK"])
        assert filter4.matches(event)

        # Filter doesn't match event type
        filter5 = EventFilter(event_types=[EventType.AGENT_STARTED])
        assert not filter5.matches(event)

    def test_subscription_model(self):
        """Test subscription model"""
        filter = EventFilter(event_types=[EventType.TASK_CREATED])
        subscription = Subscription(agent_id="agent-001", filter=filter)

        assert subscription.subscription_id is not None
        assert subscription.agent_id == "agent-001"
        assert subscription.active is True
        assert subscription.created_at is not None

    def test_conflict_report_model(self):
        """Test conflict report model"""
        conflict = ConflictReport(
            conflict_type="resource_lock",
            agent_ids=["agent-001", "agent-002"],
            resource_id="resource-123",
            resource_type="dataset",
            description="Lock conflict",
        )

        assert conflict.conflict_id is not None
        assert len(conflict.agent_ids) == 2
        assert conflict.resolution_status == "unresolved"
        assert conflict.context_tag == "COORD_CONFLICT"

    def test_workflow_definition_model(self):
        """Test workflow definition model"""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            description="Test workflow description",
            steps=[{"step_id": "step1", "action": "process"}],
            agent_assignments={"step1": "agent-001"},
            created_by="orchestrator",
        )

        assert workflow.workflow_id is not None
        assert workflow.name == "Test Workflow"
        assert workflow.status == "pending"
        assert workflow.context_tag == "COORD_WORKFLOW"


class TestEventCoordinationRegistry:
    """Test event coordination registry"""

    @pytest.fixture
    def registry(self):
        """Create fresh registry for each test"""
        return EventCoordinationRegistry(max_history=100)

    @pytest.mark.asyncio
    async def test_registry_initialization(self, registry):
        """Test registry initialization"""
        assert registry._status == "ready"
        assert registry._metrics["events_published"] == 0
        assert len(registry._events) == 0

        status = await registry.get_status()
        assert status["registry_status"] == "ready"
        assert status["health"] == "healthy"

    @pytest.mark.asyncio
    async def test_publish_event(self, registry):
        """Test event publishing"""
        event = Event(
            event_type=EventType.TASK_CREATED, source_agent_id="agent-001", payload={"task_id": "task-123"}
        )

        result = await registry.publish_event(event)

        assert result["success"] is True
        assert result["event_id"] == event.event_id
        assert result["delivered_count"] >= 0

        # Verify event stored
        assert event.event_id in registry._events
        assert len(registry._event_history) == 1

        # Verify metrics updated
        assert registry._metrics["events_published"] == 1

    @pytest.mark.asyncio
    async def test_publish_expired_event(self, registry):
        """Test publishing expired event"""
        event = Event(
            event_type=EventType.TASK_CREATED,
            source_agent_id="agent-001",
            expiry=datetime.now(timezone.utc) - timedelta(hours=1),
        )

        result = await registry.publish_event(event)

        assert result["success"] is False
        assert result["error"] == "event_expired"

    @pytest.mark.asyncio
    async def test_subscribe_and_deliver(self, registry):
        """Test subscription and event delivery"""
        received_events = []

        async def handler(event: Event):
            received_events.append(event)

        # Subscribe
        filter = EventFilter(event_types=[EventType.TASK_CREATED])
        subscription = await registry.subscribe(agent_id="agent-001", event_filter=filter, handler=handler)

        assert subscription["success"] is True
        assert subscription["agent_id"] == "agent-001"

        # Publish matching event
        event = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-002")
        await registry.publish_event(event)

        # Give time for async delivery
        await asyncio.sleep(0.1)

        # Verify delivery
        assert len(received_events) == 1
        assert received_events[0].event_id == event.event_id

    @pytest.mark.asyncio
    async def test_subscribe_with_filter(self, registry):
        """Test subscription filtering"""
        received_events = []

        async def handler(event: Event):
            received_events.append(event)

        # Subscribe to high priority only
        filter = EventFilter(priorities=[EventPriority.HIGH])
        await registry.subscribe(agent_id="agent-001", event_filter=filter, handler=handler)

        # Publish high priority event
        event1 = Event(
            event_type=EventType.TASK_CREATED, priority=EventPriority.HIGH, source_agent_id="agent-002"
        )
        await registry.publish_event(event1)

        # Publish normal priority event
        event2 = Event(
            event_type=EventType.TASK_CREATED, priority=EventPriority.NORMAL, source_agent_id="agent-002"
        )
        await registry.publish_event(event2)

        await asyncio.sleep(0.1)

        # Only high priority event should be received
        assert len(received_events) == 1
        assert received_events[0].priority == EventPriority.HIGH

    @pytest.mark.asyncio
    async def test_unsubscribe(self, registry):
        """Test unsubscribing from events"""
        received_events = []

        async def handler(event: Event):
            received_events.append(event)

        # Subscribe
        filter = EventFilter(event_types=[EventType.TASK_CREATED])
        subscription = await registry.subscribe(agent_id="agent-001", event_filter=filter, handler=handler)

        # Unsubscribe
        result = await registry.unsubscribe(subscription["subscription_id"])
        assert result["success"] is True

        # Publish event after unsubscribe
        event = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-002")
        await registry.publish_event(event)

        await asyncio.sleep(0.1)

        # No events should be received
        assert len(received_events) == 0

    @pytest.mark.asyncio
    async def test_get_subscriptions(self, registry):
        """Test getting agent subscriptions"""
        # Create multiple subscriptions
        filter1 = EventFilter(event_types=[EventType.TASK_CREATED])
        await registry.subscribe(agent_id="agent-001", event_filter=filter1)

        filter2 = EventFilter(priorities=[EventPriority.HIGH])
        await registry.subscribe(agent_id="agent-001", event_filter=filter2)

        # Get subscriptions
        subscriptions = await registry.get_subscriptions("agent-001")

        assert len(subscriptions) == 2

    @pytest.mark.asyncio
    async def test_discover_events(self, registry):
        """Test event discovery"""
        # Publish several events
        event1 = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-001")
        event2 = Event(event_type=EventType.TASK_COMPLETED, source_agent_id="agent-001")
        event3 = Event(event_type=EventType.AGENT_STARTED, source_agent_id="agent-002")

        await registry.publish_event(event1)
        await registry.publish_event(event2)
        await registry.publish_event(event3)

        # Discover all events
        all_events = await registry.discover_events()
        assert len(all_events) == 3

        # Discover with filter
        filter = EventFilter(event_types=[EventType.TASK_CREATED])
        filtered_events = await registry.discover_events(filter=filter)
        assert len(filtered_events) == 1
        assert filtered_events[0]["event_type"] == EventType.TASK_CREATED.value

    @pytest.mark.asyncio
    async def test_replay_events(self, registry):
        """Test event replay"""
        # Publish events
        event1 = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-001")
        event2 = Event(event_type=EventType.TASK_COMPLETED, source_agent_id="agent-001")

        await registry.publish_event(event1)
        await asyncio.sleep(0.1)
        await registry.publish_event(event2)

        # Replay all events
        replayed = await registry.replay_events("agent-001")
        assert len(replayed) == 2

        # Replay with time filter
        mid_time = datetime.now(timezone.utc)
        event3 = Event(event_type=EventType.AGENT_HEARTBEAT, source_agent_id="agent-001")
        await registry.publish_event(event3)

        replayed_after = await registry.replay_events("agent-001", start_time=mid_time)
        assert len(replayed_after) >= 1

    @pytest.mark.asyncio
    async def test_conflict_detection(self, registry):
        """Test conflict detection"""
        # First agent acquires lock
        await registry.acquire_lock("agent-001", "resource-123")

        # Second agent tries to access same resource
        conflict = await registry.detect_conflict(
            agent_id="agent-002", resource_id="resource-123", resource_type="dataset", operation="write"
        )

        assert conflict is not None
        assert conflict.conflict_type == "resource_lock"
        assert "agent-001" in conflict.agent_ids
        assert "agent-002" in conflict.agent_ids
        assert registry._metrics["conflicts_detected"] == 1

    @pytest.mark.asyncio
    async def test_no_conflict_when_resource_free(self, registry):
        """Test no conflict when resource is free"""
        conflict = await registry.detect_conflict(
            agent_id="agent-001", resource_id="resource-123", resource_type="dataset", operation="read"
        )

        assert conflict is None

    @pytest.mark.asyncio
    async def test_acquire_and_release_lock(self, registry):
        """Test lock acquisition and release"""
        # Acquire lock
        result = await registry.acquire_lock("agent-001", "resource-123")
        assert result["success"] is True
        assert result["resource_id"] == "resource-123"

        # Try to acquire same lock
        result2 = await registry.acquire_lock("agent-002", "resource-123")
        assert result2["success"] is False
        assert result2["error"] == "resource_locked"

        # Release lock
        result3 = await registry.release_lock("agent-001", "resource-123")
        assert result3["success"] is True

        # Now lock can be acquired
        result4 = await registry.acquire_lock("agent-002", "resource-123")
        assert result4["success"] is True

    @pytest.mark.asyncio
    @pytest.mark.slow  # #792: TTL test sleeps 1.5s
    async def test_lock_auto_release(self, registry):
        """Test automatic lock release after TTL"""
        # Acquire lock with short TTL
        await registry.acquire_lock("agent-001", "resource-123", ttl_seconds=1)

        # Lock should be held immediately
        result = await registry.acquire_lock("agent-002", "resource-123")
        assert result["success"] is False

        # Wait for TTL to expire
        await asyncio.sleep(1.5)

        # Lock should now be available
        result2 = await registry.acquire_lock("agent-002", "resource-123")
        assert result2["success"] is True

    @pytest.mark.asyncio
    async def test_resolve_conflict(self, registry):
        """Test conflict resolution"""
        # Create a conflict
        await registry.acquire_lock("agent-001", "resource-123")
        conflict = await registry.detect_conflict(
            agent_id="agent-002", resource_id="resource-123", resource_type="dataset", operation="write"
        )

        assert conflict is not None

        # Resolve conflict
        result = await registry.resolve_conflict(
            conflict_id=conflict.conflict_id, strategy="priority_based", resolved_by="agent-001"
        )

        assert result["success"] is True
        assert registry._metrics["conflicts_resolved"] == 1

        # Check conflict status
        resolved_conflict = registry._conflicts[conflict.conflict_id]
        assert resolved_conflict.resolution_status == "resolved"
        assert resolved_conflict.resolution_strategy == "priority_based"

    @pytest.mark.asyncio
    async def test_create_workflow(self, registry):
        """Test workflow creation"""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            description="Test workflow",
            steps=[{"step_id": "step1", "action": "process"}],
            agent_assignments={"step1": "agent-001"},
            created_by="orchestrator",
        )

        result = await registry.create_workflow(workflow)

        assert result["success"] is True
        assert result["workflow_id"] == workflow.workflow_id

        # Verify workflow stored
        assert workflow.workflow_id in registry._workflows

    @pytest.mark.asyncio
    async def test_get_workflow_status(self, registry):
        """Test getting workflow status"""
        workflow = WorkflowDefinition(
            name="Test Workflow",
            description="Test workflow",
            steps=[],
            agent_assignments={},
            created_by="orchestrator",
        )

        await registry.create_workflow(workflow)

        status = await registry.get_workflow_status(workflow.workflow_id)

        assert status is not None
        assert status["name"] == "Test Workflow"
        assert status["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_metrics(self, registry):
        """Test getting registry metrics"""
        # Publish some events
        event = Event(event_type=EventType.TASK_CREATED, source_agent_id="agent-001")
        await registry.publish_event(event)

        metrics = await registry.get_metrics()

        assert metrics["status"] == "ready"
        assert "metrics" in metrics
        assert metrics["metrics"]["events_published"] == 1
        assert "counts" in metrics
        assert metrics["counts"]["events_in_history"] == 1

    @pytest.mark.asyncio
    async def test_priority_based_delivery(self, registry):
        """Test priority-based event delivery timing"""
        critical_received = []
        low_received = []

        async def critical_handler(event: Event):
            critical_received.append(datetime.now(timezone.utc))

        async def low_handler(event: Event):
            low_received.append(datetime.now(timezone.utc))

        # Subscribe to critical events
        filter_critical = EventFilter(priorities=[EventPriority.CRITICAL])
        await registry.subscribe(agent_id="agent-001", event_filter=filter_critical, handler=critical_handler)

        # Subscribe to low priority events
        filter_low = EventFilter(priorities=[EventPriority.LOW])
        await registry.subscribe(agent_id="agent-002", event_filter=filter_low, handler=low_handler)

        # Publish critical event
        critical_event = Event(
            event_type=EventType.SYSTEM_ALERT, priority=EventPriority.CRITICAL, source_agent_id="system"
        )
        await registry.publish_event(critical_event)

        # Publish low priority event
        low_event = Event(
            event_type=EventType.METRIC_REPORTED, priority=EventPriority.LOW, source_agent_id="system"
        )
        await registry.publish_event(low_event)

        await asyncio.sleep(0.2)

        # Both should be delivered
        assert len(critical_received) == 1
        assert len(low_received) == 1

    @pytest.mark.asyncio
    async def test_targeted_event_delivery(self, registry):
        """Test targeted event delivery to specific agents"""
        agent1_received = []
        agent2_received = []

        async def handler1(event: Event):
            agent1_received.append(event)

        async def handler2(event: Event):
            agent2_received.append(event)

        # Both agents subscribe
        filter = EventFilter(event_types=[EventType.TASK_ASSIGNED])
        await registry.subscribe(agent_id="agent-001", event_filter=filter, handler=handler1)
        await registry.subscribe(agent_id="agent-002", event_filter=filter, handler=handler2)

        # Publish event targeted to agent-001 only
        event = Event(
            event_type=EventType.TASK_ASSIGNED,
            source_agent_id="orchestrator",
            target_agent_ids=["agent-001"],
        )
        await registry.publish_event(event)

        await asyncio.sleep(0.1)

        # Only agent-001 should receive
        assert len(agent1_received) == 1
        assert len(agent2_received) == 0

    @pytest.mark.asyncio
    async def test_history_limit(self, registry):
        """Test event history size limit"""
        max_history = registry._max_history

        # Publish more events than max history
        for i in range(max_history + 50):
            event = Event(event_type=EventType.AGENT_HEARTBEAT, source_agent_id=f"agent-{i}")
            await registry.publish_event(event)

        # Verify history doesn't exceed limit
        assert len(registry._event_history) <= max_history
        assert len(registry._events) <= max_history


@pytest.mark.unit
class TestEventRegistryUnit:
    """Unit tests for event registry"""

    @pytest.mark.asyncio
    async def test_get_event_registry_singleton(self):
        """Test global registry singleton"""
        from src.coordination.event_registry import get_event_registry

        registry1 = get_event_registry()
        registry2 = get_event_registry()

        # Should return same instance
        assert registry1 is registry2
