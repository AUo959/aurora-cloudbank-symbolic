#!/usr/bin/env python3
"""
Demo script for Multi-Agent Event Coordination Registry

Demonstrates key features:
- Event publishing and subscription
- Conflict detection and resolution
- Resource locking
- Workflow orchestration
"""

import logging

logger = logging.getLogger(__name__)

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports - use relative path detection
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.coordination.event_models import (
    Event,
    EventFilter,
    EventPriority,
    EventType,
    WorkflowDefinition,
)
from src.coordination.event_registry import get_event_registry


async def demo_basic_pubsub():
    """Demo 1: Basic publish-subscribe"""
    print("\n" + "=" * 60)
    print("Demo 1: Basic Event Publishing and Subscription")
    print("=" * 60)

    registry = get_event_registry()

    # Track received events
    received_events = []

    async def task_handler(event: Event):
        print(f"  📩 Agent received event: {event.event_type.value}")
        print(f"     Payload: {event.payload}")
        received_events.append(event)

    # Agent subscribes to task events
    print("\n1. Agent subscribing to task events...")
    event_filter = EventFilter(event_types=[EventType.TASK_CREATED, EventType.TASK_ASSIGNED])

    subscription = await registry.subscribe(agent_id="r2-agent-001", event_filter=event_filter, handler=task_handler)

    print(f"   ✓ Subscribed with ID: {subscription['subscription_id']}")

    # Publish task created event
    print("\n2. Publishing TASK_CREATED event...")
    event1 = Event(
        event_type=EventType.TASK_CREATED,
        priority=EventPriority.HIGH,
        source_agent_id="orchestrator",
        payload={"task_id": "task-001", "description": "Process dataset", "deadline": "2024-01-15T12:00:00Z"},
        context_tag="COORD_DEMO",
    )

    result1 = await registry.publish_event(event1)
    await asyncio.sleep(0.1)  # Give time for async delivery

    print(f"   ✓ Event published: {result1['event_id']}")
    print(f"   ✓ Delivered to {result1['delivered_count']} subscriber(s)")

    # Publish task assigned event
    print("\n3. Publishing TASK_ASSIGNED event...")
    event2 = Event(
        event_type=EventType.TASK_ASSIGNED,
        priority=EventPriority.NORMAL,
        source_agent_id="orchestrator",
        target_agent_ids=["r2-agent-001"],
        payload={"task_id": "task-001", "assigned_to": "r2-agent-001"},
        context_tag="COORD_DEMO",
    )

    result2 = await registry.publish_event(event2)
    await asyncio.sleep(0.1)

    print(f"   ✓ Event published: {result2['event_id']}")
    print(f"   ✓ Delivered to {result2['delivered_count']} subscriber(s)")

    print(f"\n✓ Total events received by handler: {len(received_events)}")


async def demo_conflict_detection():
    """Demo 2: Conflict detection and resource locking"""
    print("\n" + "=" * 60)
    print("Demo 2: Conflict Detection and Resource Locking")
    print("=" * 60)

    registry = get_event_registry()

    # Agent 1 acquires lock
    print("\n1. Agent-001 acquiring lock on dataset-123...")
    lock_result = await registry.acquire_lock(agent_id="r2-agent-001", resource_id="dataset-123", ttl_seconds=300)

    if lock_result["success"]:
        print(f"   ✓ Lock acquired by r2-agent-001")
        print(f"   ✓ Lock expires in {lock_result['expires_in']} seconds")
    else:
        print(f"   ✗ Lock acquisition failed: {lock_result['error']}")

    # Agent 2 tries to access same resource
    print("\n2. Agent-002 attempting to access dataset-123...")
    conflict = await registry.detect_conflict(
        agent_id="r2-agent-002", resource_id="dataset-123", resource_type="dataset", operation="write"
    )

    if conflict:
        print(f"   ⚠️  Conflict detected!")
        print(f"     Type: {conflict.conflict_type}")
        print(f"     Agents: {', '.join(conflict.agent_ids)}")
        print(f"     Description: {conflict.description}")

        # Resolve conflict
        print("\n3. Resolving conflict...")
        resolution = await registry.resolve_conflict(
            conflict_id=conflict.conflict_id, strategy="priority_based", resolved_by="r2-agent-001"
        )

        if resolution["success"]:
            print(f"   ✓ Conflict resolved using strategy: {resolution['strategy']}")
    else:
        print("   ✓ No conflict detected")

    # Release lock
    print("\n4. Agent-001 releasing lock...")
    release_result = await registry.release_lock(agent_id="r2-agent-001", resource_id="dataset-123")

    if release_result["success"]:
        print(f"   ✓ Lock released")

    # Now agent 2 can acquire lock
    print("\n5. Agent-002 acquiring lock...")
    lock_result2 = await registry.acquire_lock(agent_id="r2-agent-002", resource_id="dataset-123")

    if lock_result2["success"]:
        print(f"   ✓ Lock acquired by r2-agent-002")


async def demo_workflow_orchestration():
    """Demo 3: Multi-agent workflow orchestration"""
    print("\n" + "=" * 60)
    print("Demo 3: Multi-Agent Workflow Orchestration")
    print("=" * 60)

    registry = get_event_registry()

    # Define workflow
    print("\n1. Creating data processing workflow...")
    workflow = WorkflowDefinition(
        name="Data Processing Pipeline",
        description="Multi-stage data processing with validation",
        steps=[
            {"step_id": "fetch", "action": "fetch_data", "timeout": 60},
            {"step_id": "process", "action": "process_data", "timeout": 300},
            {"step_id": "validate", "action": "validate_results", "timeout": 30},
        ],
        agent_assignments={"fetch": "r2-agent-001", "process": "r2-agent-002", "validate": "r2-agent-003"},
        created_by="orchestrator",
    )

    result = await registry.create_workflow(workflow)

    if result["success"]:
        print(f"   ✓ Workflow created: {result['workflow_id']}")
        print(f"     Name: {workflow.name}")
        print(f"     Steps: {len(workflow.steps)}")
        print(f"     Agents: {len(workflow.agent_assignments)}")

        # Check workflow status
        print("\n2. Checking workflow status...")
        status = await registry.get_workflow_status(workflow.workflow_id)

        if status:
            print(f"   ✓ Status: {status['status']}")
            print(f"     Created: {status['created_at']}")
            print(f"     Created by: {status['created_by']}")


async def demo_event_discovery():
    """Demo 4: Event discovery and replay"""
    print("\n" + "=" * 60)
    print("Demo 4: Event Discovery and Replay")
    print("=" * 60)

    registry = get_event_registry()

    # Publish several events
    print("\n1. Publishing test events...")
    events = [
        Event(event_type=EventType.AGENT_STARTED, source_agent_id="r2-agent-001"),
        Event(event_type=EventType.TASK_CREATED, source_agent_id="orchestrator", priority=EventPriority.HIGH),
        Event(event_type=EventType.TASK_COMPLETED, source_agent_id="r2-agent-001"),
    ]

    for event in events:
        await registry.publish_event(event)
        print(f"   ✓ Published: {event.event_type.value}")

    await asyncio.sleep(0.1)

    # Discover all events
    print("\n2. Discovering all events...")
    all_events = await registry.discover_events()
    print(f"   ✓ Found {len(all_events)} total events")

    # Discover high priority events
    print("\n3. Discovering high priority events...")
    high_priority_filter = EventFilter(priorities=[EventPriority.HIGH])
    high_priority_events = await registry.discover_events(filter=high_priority_filter)
    print(f"   ✓ Found {len(high_priority_events)} high priority events")

    # Replay events
    print("\n4. Replaying events for r2-agent-001...")
    replayed_events = await registry.replay_events(agent_id="r2-agent-001")
    print(f"   ✓ Replayed {len(replayed_events)} events")

    if replayed_events:
        print("\n   Recent events:")
        for event in replayed_events[-3:]:
            print(f"     - {event['event_type']} from {event['source_agent_id']}")


async def demo_metrics():
    """Demo 5: Registry metrics and monitoring"""
    print("\n" + "=" * 60)
    print("Demo 5: Registry Metrics and Monitoring")
    print("=" * 60)

    registry = get_event_registry()

    print("\n1. Fetching registry metrics...")
    metrics = await registry.get_metrics()

    print(f"\n   Registry Status: {metrics['status']}")
    print(f"   Uptime: {metrics['uptime_seconds']:.2f} seconds")

    print("\n   Event Metrics:")
    print(f"     - Events published: {metrics['metrics']['events_published']}")
    print(f"     - Events delivered: {metrics['metrics']['events_delivered']}")
    print(f"     - Events failed: {metrics['metrics']['events_failed']}")

    print("\n   Coordination Metrics:")
    print(f"     - Conflicts detected: {metrics['metrics']['conflicts_detected']}")
    print(f"     - Conflicts resolved: {metrics['metrics']['conflicts_resolved']}")

    print("\n   Current State:")
    print(f"     - Events in history: {metrics['counts']['events_in_history']}")
    print(f"     - Active subscriptions: {metrics['counts']['active_subscriptions']}")
    print(f"     - Active locks: {metrics['counts']['active_locks']}")
    print(f"     - Active workflows: {metrics['counts']['active_workflows']}")
    print(f"     - Open conflicts: {metrics['counts']['open_conflicts']}")


async def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("🚀 Multi-Agent Event Coordination Registry Demo")
    print("=" * 60)

    try:
        # Run demos
        await demo_basic_pubsub()
        await demo_conflict_detection()
        await demo_workflow_orchestration()
        await demo_event_discovery()
        await demo_metrics()

        print("\n" + "=" * 60)
        logger.info("All demos completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
