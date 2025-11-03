"""
Multi-Agent Event Coordination Registry

Implements a centralized event coordination system enabling R-2 agents to:
- Publish and subscribe to events
- Discover available event streams
- Coordinate workflows across multiple agents
- Detect and resolve conflicts
- Replay events for audit and recovery

Architecture:
- In-memory pub-sub for fast event delivery (<100ms latency)
- Async/await for non-blocking event processing
- Thread-safe operations with asyncio locks
- Event persistence for replay and audit
- Optional Redis/Kafka backends can be added for distributed deployments
"""

import asyncio
import hashlib
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

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

logger = logging.getLogger(__name__)


class EventCoordinationRegistry:
    """
    Multi-agent event coordination registry with pub-sub architecture

    Key features:
    - Fast in-memory event delivery with async/await
    - Priority-based event routing
    - Event filtering and transformation
    - Conflict detection and resolution
    - Event replay and audit trails
    - DLP tracking and symbolic anchors (Aurora patterns)
    """

    def __init__(self, max_history: int = 10000):
        """
        Initialize event coordination registry

        Args:
            max_history: Maximum number of events to keep in history for replay
        """
        # Event storage
        self._events: Dict[str, Event] = {}  # event_id -> Event
        self._event_history: List[Event] = []  # Ordered list for replay
        self._max_history = max_history

        # Subscription management
        self._subscriptions: Dict[str, Subscription] = {}  # subscription_id -> Subscription
        self._agent_subscriptions: Dict[str, List[str]] = defaultdict(list)  # agent_id -> [subscription_ids]

        # Event handlers (async callbacks)
        self._event_handlers: Dict[str, List[Callable]] = defaultdict(list)  # subscription_id -> [handlers]

        # Conflict tracking
        self._conflicts: Dict[str, ConflictReport] = {}  # conflict_id -> ConflictReport
        self._resource_locks: Dict[str, str] = {}  # resource_id -> agent_id

        # Workflow orchestration
        self._workflows: Dict[str, WorkflowDefinition] = {}  # workflow_id -> WorkflowDefinition

        # Metrics and monitoring
        self._metrics = {
            "events_published": 0,
            "events_delivered": 0,
            "events_failed": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
        }

        # Thread safety
        self._lock = asyncio.Lock()

        # Registry status
        self._status = "initializing"
        self._initialized_at = datetime.utcnow()

        logger.info("Event Coordination Registry initialized")
        self._status = "ready"

    async def publish_event(self, event: Event) -> Dict[str, Any]:
        """
        Publish event to coordination registry

        Args:
            event: Event to publish

        Returns:
            Publication result with delivery statistics
        """
        async with self._lock:
            # Validate event hasn't expired
            if event.is_expired():
                logger.warning(f"Event {event.event_id} has expired, not publishing")
                return {"success": False, "error": "event_expired", "event_id": event.event_id}

            # Store event
            self._events[event.event_id] = event
            self._event_history.append(event)

            # Maintain history limit
            if len(self._event_history) > self._max_history:
                oldest = self._event_history.pop(0)
                if oldest.event_id in self._events:
                    del self._events[oldest.event_id]

            # Update metrics
            self._metrics["events_published"] += 1

            # Update event status
            event.status = EventStatus.PROCESSING

            logger.info(
                f"Event published: {event.event_type} from {event.source_agent_id} (priority: {event.priority})"
            )

        # Deliver to subscribers (outside lock for better concurrency)
        delivery_results = await self._deliver_event(event)

        async with self._lock:
            # Update event status based on delivery
            if delivery_results["delivered_count"] > 0:
                event.status = EventStatus.DELIVERED
                self._metrics["events_delivered"] += 1
            elif delivery_results["failed_count"] > 0:
                event.status = EventStatus.FAILED
                self._metrics["events_failed"] += 1

        return {
            "success": True,
            "event_id": event.event_id,
            "delivered_to": delivery_results["delivered_to"],
            "delivered_count": delivery_results["delivered_count"],
            "failed_count": delivery_results["failed_count"],
        }

    async def _deliver_event(self, event: Event) -> Dict[str, Any]:
        """
        Deliver event to matching subscribers

        Args:
            event: Event to deliver

        Returns:
            Delivery statistics
        """
        delivered_to = []
        failed = []

        # Find matching subscriptions
        matching_subscriptions = []
        async with self._lock:
            for sub_id, subscription in self._subscriptions.items():
                if not subscription.active:
                    continue

                # Check if subscription filter matches
                if subscription.filter.matches(event):
                    # Check if target filtering applies
                    if event.target_agent_ids is None or subscription.agent_id in event.target_agent_ids:
                        matching_subscriptions.append((sub_id, subscription.agent_id))

        # Deliver to handlers (outside lock for concurrency)
        delivery_tasks = []
        for sub_id, agent_id in matching_subscriptions:
            handlers = self._event_handlers.get(sub_id, [])
            for handler in handlers:
                task = asyncio.create_task(self._invoke_handler(handler, event, agent_id))
                delivery_tasks.append((task, agent_id))

        # Wait for all deliveries with timeout based on priority
        timeout = self._get_delivery_timeout(event.priority)
        for task, agent_id in delivery_tasks:
            try:
                await asyncio.wait_for(task, timeout=timeout)
                delivered_to.append(agent_id)
            except asyncio.TimeoutError:
                logger.warning(f"Handler timeout for agent {agent_id}")
                failed.append(agent_id)
            except Exception as e:
                logger.error(f"Handler error for agent {agent_id}: {e}")
                failed.append(agent_id)

        # Update event delivery tracking
        async with self._lock:
            event.delivered_to.extend(delivered_to)
            event.delivery_attempts += 1
            event.last_delivery_attempt = datetime.utcnow()

        return {
            "delivered_to": delivered_to,
            "delivered_count": len(delivered_to),
            "failed_count": len(failed),
        }

    @staticmethod
    def _get_delivery_timeout(priority: EventPriority) -> float:
        """Get delivery timeout based on event priority"""
        timeouts = {
            EventPriority.CRITICAL: 0.01,  # 10ms
            EventPriority.HIGH: 0.05,  # 50ms
            EventPriority.NORMAL: 0.1,  # 100ms
            EventPriority.LOW: 1.0,  # 1s
        }
        return timeouts.get(priority, 0.1)

    async def _invoke_handler(self, handler: Callable, event: Event, agent_id: str):
        """Invoke event handler safely"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Handler invocation failed for agent {agent_id}: {e}")
            raise

    async def subscribe(
        self, agent_id: str, event_filter: EventFilter, handler: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Subscribe to events matching filter

        Args:
            agent_id: Subscribing agent ID
            event_filter: Event filter criteria
            handler: Optional async callback for event delivery

        Returns:
            Subscription details
        """
        async with self._lock:
            subscription = Subscription(agent_id=agent_id, filter=event_filter)

            self._subscriptions[subscription.subscription_id] = subscription
            self._agent_subscriptions[agent_id].append(subscription.subscription_id)

            if handler:
                self._event_handlers[subscription.subscription_id].append(handler)

            logger.info(f"Agent {agent_id} subscribed with filter: {event_filter}")

            return {
                "success": True,
                "subscription_id": subscription.subscription_id,
                "agent_id": agent_id,
                "filter": event_filter.model_dump(),
            }

    async def unsubscribe(self, subscription_id: str) -> Dict[str, Any]:
        """
        Unsubscribe from events

        Args:
            subscription_id: Subscription ID to cancel

        Returns:
            Unsubscription result
        """
        async with self._lock:
            if subscription_id not in self._subscriptions:
                return {"success": False, "error": "subscription_not_found"}

            subscription = self._subscriptions[subscription_id]
            subscription.active = False

            # Clean up handlers
            if subscription_id in self._event_handlers:
                del self._event_handlers[subscription_id]

            logger.info(f"Subscription {subscription_id} cancelled")

            return {"success": True, "subscription_id": subscription_id}

    async def get_subscriptions(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all subscriptions for an agent"""
        async with self._lock:
            subscription_ids = self._agent_subscriptions.get(agent_id, [])
            subscriptions = []
            for sub_id in subscription_ids:
                if sub_id in self._subscriptions:
                    subscription = self._subscriptions[sub_id]
                    if subscription.active:
                        subscriptions.append(subscription.model_dump())
            return subscriptions

    async def discover_events(self, filter: Optional[EventFilter] = None) -> List[Dict[str, Any]]:
        """
        Discover available events

        Args:
            filter: Optional filter to narrow discovery

        Returns:
            List of matching events
        """
        async with self._lock:
            events = []
            for event in self._event_history:
                if filter is None or filter.matches(event):
                    events.append(event.to_dict())
            return events

    async def replay_events(
        self, agent_id: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Replay historical events for audit or recovery

        Args:
            agent_id: Agent requesting replay
            start_time: Optional start time filter
            end_time: Optional end time filter

        Returns:
            List of historical events
        """
        async with self._lock:
            events = []
            for event in self._event_history:
                # Time filter
                if start_time and event.timestamp < start_time:
                    continue
                if end_time and event.timestamp > end_time:
                    continue

                events.append(event.to_dict())

            logger.info(f"Replayed {len(events)} events for agent {agent_id}")
            return events

    async def detect_conflict(
        self, agent_id: str, resource_id: str, resource_type: str, operation: str
    ) -> Optional[ConflictReport]:
        """
        Detect potential conflict with other agents

        Args:
            agent_id: Agent attempting operation
            resource_id: Resource being accessed
            resource_type: Type of resource
            operation: Operation being attempted

        Returns:
            ConflictReport if conflict detected, None otherwise
        """
        async with self._lock:
            # Check if resource is locked by another agent
            if resource_id in self._resource_locks:
                locking_agent = self._resource_locks[resource_id]
                if locking_agent != agent_id:
                    # Conflict detected
                    conflict = ConflictReport(
                        conflict_type="resource_lock",
                        agent_ids=[agent_id, locking_agent],
                        resource_id=resource_id,
                        resource_type=resource_type,
                        description=f"Agent {agent_id} attempted {operation} on {resource_type}:{resource_id} "
                        f"locked by {locking_agent}",
                        severity="medium",
                    )

                    self._conflicts[conflict.conflict_id] = conflict
                    self._metrics["conflicts_detected"] += 1

                    logger.warning(f"Conflict detected: {conflict.description}")

                    # Publish conflict event
                    conflict_event = Event(
                        event_type=EventType.CONFLICT_DETECTED,
                        priority=EventPriority.HIGH,
                        source_agent_id="coordination_registry",
                        payload=conflict.model_dump(),
                        context_tag="COORD_CONFLICT",
                    )
                    await self.publish_event(conflict_event)

                    return conflict

            return None

    async def acquire_lock(self, agent_id: str, resource_id: str, ttl_seconds: int = 300) -> Dict[str, Any]:
        """
        Acquire exclusive lock on resource

        Args:
            agent_id: Agent requesting lock
            resource_id: Resource to lock
            ttl_seconds: Lock time-to-live in seconds

        Returns:
            Lock acquisition result
        """
        async with self._lock:
            if resource_id in self._resource_locks:
                current_holder = self._resource_locks[resource_id]
                return {"success": False, "error": "resource_locked", "locked_by": current_holder}

            self._resource_locks[resource_id] = agent_id

            # Publish lock event
            lock_event = Event(
                event_type=EventType.LOCK_ACQUIRED,
                priority=EventPriority.HIGH,
                source_agent_id=agent_id,
                payload={"resource_id": resource_id, "ttl_seconds": ttl_seconds},
                context_tag="COORD_LOCK",
            )
            await self.publish_event(lock_event)

            # Schedule lock release
            asyncio.create_task(self._auto_release_lock(resource_id, agent_id, ttl_seconds))

            logger.info(f"Lock acquired by {agent_id} on {resource_id}")

            return {"success": True, "resource_id": resource_id, "expires_in": ttl_seconds}

    async def release_lock(self, agent_id: str, resource_id: str) -> Dict[str, Any]:
        """
        Release lock on resource

        Args:
            agent_id: Agent releasing lock
            resource_id: Resource to unlock

        Returns:
            Lock release result
        """
        async with self._lock:
            if resource_id not in self._resource_locks:
                return {"success": False, "error": "lock_not_found"}

            if self._resource_locks[resource_id] != agent_id:
                return {"success": False, "error": "lock_not_owned"}

            del self._resource_locks[resource_id]

            # Publish unlock event
            unlock_event = Event(
                event_type=EventType.LOCK_RELEASED,
                priority=EventPriority.HIGH,
                source_agent_id=agent_id,
                payload={"resource_id": resource_id},
                context_tag="COORD_LOCK",
            )
            await self.publish_event(unlock_event)

            logger.info(f"Lock released by {agent_id} on {resource_id}")

            return {"success": True, "resource_id": resource_id}

    async def _auto_release_lock(self, resource_id: str, agent_id: str, ttl_seconds: int):
        """Automatically release lock after TTL"""
        await asyncio.sleep(ttl_seconds)
        async with self._lock:
            if resource_id in self._resource_locks and self._resource_locks[resource_id] == agent_id:
                del self._resource_locks[resource_id]
                logger.info(f"Lock auto-released on {resource_id} after {ttl_seconds}s TTL")

    async def resolve_conflict(self, conflict_id: str, strategy: str, resolved_by: str) -> Dict[str, Any]:
        """
        Mark conflict as resolved

        Args:
            conflict_id: Conflict to resolve
            strategy: Resolution strategy used
            resolved_by: Agent that resolved conflict

        Returns:
            Resolution result
        """
        async with self._lock:
            if conflict_id not in self._conflicts:
                return {"success": False, "error": "conflict_not_found"}

            conflict = self._conflicts[conflict_id]
            conflict.resolution_status = "resolved"
            conflict.resolution_strategy = strategy
            conflict.resolved_at = datetime.utcnow()
            conflict.resolved_by = resolved_by

            self._metrics["conflicts_resolved"] += 1

            # Publish resolution event
            resolution_event = Event(
                event_type=EventType.CONFLICT_RESOLVED,
                priority=EventPriority.HIGH,
                source_agent_id=resolved_by,
                payload=conflict.model_dump(),
                context_tag="COORD_CONFLICT",
            )
            await self.publish_event(resolution_event)

            logger.info(f"Conflict {conflict_id} resolved using strategy: {strategy}")

            return {"success": True, "conflict_id": conflict_id, "strategy": strategy}

    async def create_workflow(self, workflow: WorkflowDefinition) -> Dict[str, Any]:
        """
        Create multi-agent workflow

        Args:
            workflow: Workflow definition

        Returns:
            Workflow creation result
        """
        async with self._lock:
            self._workflows[workflow.workflow_id] = workflow

            # Publish workflow creation event
            workflow_event = Event(
                event_type=EventType.WORKFLOW_STARTED,
                priority=EventPriority.NORMAL,
                source_agent_id=workflow.created_by,
                payload=workflow.model_dump(),
                context_tag="COORD_WORKFLOW",
            )
            await self.publish_event(workflow_event)

            logger.info(f"Workflow {workflow.name} created by {workflow.created_by}")

            return {"success": True, "workflow_id": workflow.workflow_id}

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        async with self._lock:
            if workflow_id in self._workflows:
                return self._workflows[workflow_id].model_dump()
            return None

    async def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics and statistics"""
        async with self._lock:
            return {
                "status": self._status,
                "initialized_at": self._initialized_at.isoformat(),
                "uptime_seconds": (datetime.utcnow() - self._initialized_at).total_seconds(),
                "metrics": self._metrics.copy(),
                "counts": {
                    "events_in_history": len(self._event_history),
                    "active_subscriptions": sum(1 for s in self._subscriptions.values() if s.active),
                    "active_locks": len(self._resource_locks),
                    "active_workflows": sum(1 for w in self._workflows.values() if w.status in ["pending", "running"]),
                    "open_conflicts": sum(
                        1 for c in self._conflicts.values() if c.resolution_status == "unresolved"
                    ),
                },
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get detailed registry status"""
        metrics = await self.get_metrics()
        async with self._lock:
            return {
                "registry_status": self._status,
                "initialized_at": self._initialized_at.isoformat(),
                "metrics": metrics,
                "health": "healthy" if self._status == "ready" else "degraded",
            }


# Global registry instance
_registry_instance: Optional[EventCoordinationRegistry] = None


def get_event_registry() -> EventCoordinationRegistry:
    """Get or create global event registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = EventCoordinationRegistry()
    return _registry_instance
