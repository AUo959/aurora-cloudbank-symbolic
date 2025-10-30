"""
Node Registry - Bridge Node Management

Manages registration, discovery, and lifecycle of bridge nodes in distributed constellation.

Anchor: EOS_SEED_ORION_v2
DLP: context_tag=node_registry_v2, symbolic_hash=NODE_REG_v2
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    """Bridge node operational status"""

    ONLINE = "online"  # Fully operational
    DEGRADED = "degraded"  # Partially operational
    OFFLINE = "offline"  # Not operational
    STARTING = "starting"  # Initialization in progress
    STOPPING = "stopping"  # Graceful shutdown in progress


@dataclass
class BridgeNode:
    """Distributed bridge node metadata"""

    node_id: str
    hostname: str
    port: int
    region: str
    capacity: int  # Max concurrent handshakes
    current_load: int  # Active handshakes
    status: NodeStatus
    last_heartbeat: datetime
    anchor_hash: str  # EOS_SEED_ORION_v2 verification
    version: str  # Bridge version
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)

    def is_healthy(self, heartbeat_timeout: int = 30) -> bool:
        """Check if node is healthy based on heartbeat"""
        if self.status == NodeStatus.OFFLINE:
            return False

        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
        return time_since_heartbeat < heartbeat_timeout

    def available_capacity(self) -> int:
        """Calculate available handshake capacity"""
        return max(0, self.capacity - self.current_load)

    def load_percentage(self) -> float:
        """Calculate current load as percentage"""
        if self.capacity == 0:
            return 100.0
        return (self.current_load / self.capacity) * 100.0


class NodeRegistry:
    """
    Registry for distributed bridge nodes.

    Maintains catalog of all bridge nodes in constellation,
    tracks health, and facilitates node discovery.
    """

    def __init__(
        self, anchor_hash: str = "EOS_SEED_ORION_v2", heartbeat_timeout: int = 30
    ):
        """
        Initialize node registry.

        Args:
            anchor_hash: Required anchor for node registration
            heartbeat_timeout: Seconds before node considered unhealthy
        """
        self.nodes: Dict[str, BridgeNode] = {}
        self.anchor_hash = anchor_hash
        self.heartbeat_timeout = heartbeat_timeout
        self._lock = asyncio.Lock()

        logger.info(
            f"Node registry initialized with anchor: {anchor_hash[:12]}..."
        )

    async def register_node(
        self,
        hostname: str,
        port: int,
        region: str,
        capacity: int,
        version: str,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, any]] = None,
        node_id: Optional[str] = None,
    ) -> BridgeNode:
        """
        Register a new bridge node.

        Args:
            hostname: Node hostname/IP
            port: Node API port
            region: Geographic region
            capacity: Max concurrent handshakes
            version: Bridge version
            capabilities: Optional feature list
            metadata: Optional metadata
            node_id: Optional specific node ID (generates UUID if not provided)

        Returns:
            Registered BridgeNode instance

        Raises:
            ValueError: If node already registered or invalid parameters
        """
        async with self._lock:
            # Generate node ID if not provided
            if node_id is None:
                node_id = str(uuid4())

            # Check if already registered
            if node_id in self.nodes:
                raise ValueError(f"Node already registered: {node_id}")

            # Create node
            node = BridgeNode(
                node_id=node_id,
                hostname=hostname,
                port=port,
                region=region,
                capacity=capacity,
                current_load=0,
                status=NodeStatus.STARTING,
                last_heartbeat=datetime.now(),
                anchor_hash=self.anchor_hash,
                version=version,
                capabilities=capabilities or [],
                metadata=metadata or {},
            )

            # Register node
            self.nodes[node_id] = node

            logger.info(
                f"Registered node {node_id[:8]} at {hostname}:{port} "
                f"(region={region}, capacity={capacity})"
            )

            return node

    async def unregister_node(self, node_id: str) -> bool:
        """
        Unregister a bridge node.

        Args:
            node_id: Node identifier

        Returns:
            True if unregistered, False if not found
        """
        async with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.status = NodeStatus.STOPPING

                del self.nodes[node_id]

                logger.info(
                    f"Unregistered node {node_id[:8]} "
                    f"({node.hostname}:{node.port})"
                )
                return True

            return False

    async def update_heartbeat(self, node_id: str) -> bool:
        """
        Update node heartbeat timestamp.

        Args:
            node_id: Node identifier

        Returns:
            True if updated, False if node not found
        """
        async with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].last_heartbeat = datetime.now()

                # Transition to ONLINE if starting
                if self.nodes[node_id].status == NodeStatus.STARTING:
                    self.nodes[node_id].status = NodeStatus.ONLINE
                    logger.info(f"Node {node_id[:8]} is now ONLINE")

                return True

            return False

    async def update_node_status(
        self, node_id: str, status: NodeStatus
    ) -> bool:
        """
        Update node operational status.

        Args:
            node_id: Node identifier
            status: New status

        Returns:
            True if updated, False if node not found
        """
        async with self._lock:
            if node_id in self.nodes:
                old_status = self.nodes[node_id].status
                self.nodes[node_id].status = status

                logger.info(
                    f"Node {node_id[:8]} status: {old_status.value} → {status.value}"
                )
                return True

            return False

    async def update_node_load(
        self, node_id: str, current_load: int
    ) -> bool:
        """
        Update node current load.

        Args:
            node_id: Node identifier
            current_load: Active handshake count

        Returns:
            True if updated, False if node not found
        """
        async with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].current_load = current_load
                return True

            return False

    async def get_node(self, node_id: str) -> Optional[BridgeNode]:
        """
        Get node by ID.

        Args:
            node_id: Node identifier

        Returns:
            BridgeNode if found, None otherwise
        """
        async with self._lock:
            return self.nodes.get(node_id)

    async def list_nodes(
        self,
        status_filter: Optional[NodeStatus] = None,
        region_filter: Optional[str] = None,
        healthy_only: bool = False,
    ) -> List[BridgeNode]:
        """
        List registered nodes with optional filters.

        Args:
            status_filter: Filter by node status
            region_filter: Filter by region
            healthy_only: Only return healthy nodes

        Returns:
            List of matching bridge nodes
        """
        async with self._lock:
            nodes = list(self.nodes.values())

            # Apply filters
            if status_filter:
                nodes = [n for n in nodes if n.status == status_filter]

            if region_filter:
                nodes = [n for n in nodes if n.region == region_filter]

            if healthy_only:
                nodes = [n for n in nodes if n.is_healthy(self.heartbeat_timeout)]

            return nodes

    async def get_online_nodes(self) -> List[BridgeNode]:
        """
        Get all online nodes.

        Returns:
            List of online bridge nodes
        """
        return await self.list_nodes(status_filter=NodeStatus.ONLINE, healthy_only=True)

    async def get_available_nodes(self, min_capacity: int = 1) -> List[BridgeNode]:
        """
        Get nodes with available capacity.

        Args:
            min_capacity: Minimum available capacity required

        Returns:
            List of nodes with sufficient capacity
        """
        online_nodes = await self.get_online_nodes()
        return [n for n in online_nodes if n.available_capacity() >= min_capacity]

    async def cleanup_stale_nodes(self) -> int:
        """
        Remove nodes that haven't sent heartbeat within timeout.

        Returns:
            Number of nodes removed
        """
        async with self._lock:
            stale_nodes = []

            for node_id, node in self.nodes.items():
                if not node.is_healthy(self.heartbeat_timeout * 3):  # 3x timeout grace
                    stale_nodes.append(node_id)

            for node_id in stale_nodes:
                node = self.nodes[node_id]
                logger.warning(
                    f"Removing stale node {node_id[:8]} "
                    f"(last heartbeat: {node.last_heartbeat})"
                )
                del self.nodes[node_id]

            if stale_nodes:
                logger.info(f"Cleaned up {len(stale_nodes)} stale nodes")

            return len(stale_nodes)

    async def get_cluster_health(self) -> Dict[str, any]:
        """
        Get overall cluster health metrics.

        Returns:
            Dictionary with cluster health statistics
        """
        async with self._lock:
            total_nodes = len(self.nodes)
            online_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.ONLINE)
            degraded_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.DEGRADED)
            offline_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.OFFLINE)
            healthy_nodes = sum(1 for n in self.nodes.values() if n.is_healthy(self.heartbeat_timeout))

            total_capacity = sum(n.capacity for n in self.nodes.values())
            total_load = sum(n.current_load for n in self.nodes.values())
            avg_load_pct = (
                (total_load / total_capacity * 100.0) if total_capacity > 0 else 0.0
            )

            return {
                "total_nodes": total_nodes,
                "online_nodes": online_nodes,
                "degraded_nodes": degraded_nodes,
                "offline_nodes": offline_nodes,
                "healthy_nodes": healthy_nodes,
                "total_capacity": total_capacity,
                "total_load": total_load,
                "average_load_percentage": round(avg_load_pct, 2),
                "cluster_health_score": round(
                    (healthy_nodes / total_nodes * 100.0) if total_nodes > 0 else 0.0,
                    2,
                ),
            }


# Global registry instance
_node_registry: Optional[NodeRegistry] = None


def get_node_registry() -> NodeRegistry:
    """Get global node registry instance"""
    global _node_registry
    if _node_registry is None:
        _node_registry = NodeRegistry()
    return _node_registry


def initialize_node_registry(
    anchor_hash: str = "EOS_SEED_ORION_v2", heartbeat_timeout: int = 30
) -> NodeRegistry:
    """Initialize global node registry with configuration"""
    global _node_registry
    _node_registry = NodeRegistry(
        anchor_hash=anchor_hash, heartbeat_timeout=heartbeat_timeout
    )
    return _node_registry
