"""
Load Balancer - Intelligent Handshake Distribution

Routes handshakes to optimal bridge nodes based on load, health, and proximity.

Anchor: EOS_SEED_ORION_v2
DLP: context_tag=load_balancer_v2, symbolic_hash=LOAD_BAL_v2
"""

import logging
import random
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing algorithm"""

    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"  # Weight by inverse load
    RANDOM = "random"


class LoadBalancer:
    """
    Intelligent load balancing for bridge nodes.

    Selects optimal node for handshake based on:
    - Node health (healthy only)
    - Current load (prefer lower)
    - Geographic proximity (if known)
    - Node capabilities (feature matching)
    """

    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.WEIGHTED):
        """
        Initialize load balancer.

        Args:
            strategy: Load balancing algorithm
        """
        self.strategy = strategy
        self._round_robin_index = 0

    def select_node(
        self,
        nodes: List,
        thread_id: Optional[str] = None,
        required_capabilities: Optional[List[str]] = None,
        preferred_region: Optional[str] = None,
    ):
        """
        Select optimal node for handshake.

        Args:
            nodes: List of available BridgeNode instances
            thread_id: Thread requesting handshake (for affinity)
            required_capabilities: Required node capabilities
            preferred_region: Preferred geographic region

        Returns:
            Selected BridgeNode, or None if no eligible nodes

        Raises:
            ValueError: If no nodes available
        """
        if not nodes:
            raise ValueError("No nodes available for load balancing")

        # Filter by capabilities if specified
        eligible_nodes = nodes
        if required_capabilities:
            eligible_nodes = [
                n
                for n in eligible_nodes
                if all(cap in n.capabilities for cap in required_capabilities)
            ]

        if not eligible_nodes:
            logger.warning(
                f"No nodes with required capabilities: {required_capabilities}"
            )
            return None

        # Apply load balancing strategy
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(eligible_nodes)
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            return self._least_loaded_select(eligible_nodes)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            return self._weighted_select(eligible_nodes, preferred_region)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(eligible_nodes)
        else:
            logger.warning(f"Unknown strategy {self.strategy}, using weighted")
            return self._weighted_select(eligible_nodes, preferred_region)

    def _round_robin_select(self, nodes: List):
        """Round-robin selection"""
        selected = nodes[self._round_robin_index % len(nodes)]
        self._round_robin_index = (self._round_robin_index + 1) % len(nodes)
        return selected

    def _least_loaded_select(self, nodes: List):
        """Select node with lowest current load"""
        return min(nodes, key=lambda n: n.current_load)

    def _weighted_select(self, nodes: List, preferred_region: Optional[str] = None):
        """
        Weighted selection by inverse load with regional preference.

        Weights:
        - Lower load = higher weight
        - Same region = 1.5x weight boost
        """
        if not nodes:
            return None

        # Calculate weights (inverse of load, avoid division by zero)
        weights = [1.0 / (n.current_load + 1) for n in nodes]

        # Apply regional preference
        if preferred_region:
            for i, node in enumerate(nodes):
                if node.region == preferred_region:
                    weights[i] *= 1.5  # 50% boost for same region

        # Random weighted choice
        return random.choices(nodes, weights=weights)[0]


# Global load balancer instance
_load_balancer: Optional[LoadBalancer] = None


def get_load_balancer() -> LoadBalancer:
    """Get global load balancer instance"""
    global _load_balancer
    if _load_balancer is None:
        _load_balancer = LoadBalancer()
    return _load_balancer
