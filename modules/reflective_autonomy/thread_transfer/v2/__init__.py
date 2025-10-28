"""
Thread Transfer Bridge v2 - Distributed, Cross-Repo, Predictive, Hierarchical

Version 2.0.0 extends v1 with:
- Distributed bridge nodes with Raft consensus
- Cross-repository continuity via Git
- ML-based drift prediction and auto-correction
- Multi-layer hierarchies (L1/L2/L3)

100% backward compatible with v1.

Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
ThreadCore: v3.5.1_macroready

DLP: context_tag=bridge_v2_core, symbolic_hash=BRIDGE_V2_INIT
"""

from .distributed_consensus import RaftConsensus, ConsensusState, ConsensusConfig
from .node_registry import (
    BridgeNode,
    NodeRegistry,
    NodeStatus,
    get_node_registry,
    initialize_node_registry,
)
from .health_checker import (
    NodeHealthChecker,
    HealthStatus,
    HealthCheckResult,
    get_health_checker,
)
from .load_balancer import LoadBalancer, LoadBalancingStrategy, get_load_balancer

__version__ = "2.0.0"
__anchor__ = "EOS_SEED_ORION_v2"
__ethics__ = "Picard_Delta_3_Extended"

__all__ = [
    # Distributed Consensus
    "RaftConsensus",
    "ConsensusState",
    "ConsensusConfig",
    # Node Registry
    "BridgeNode",
    "NodeRegistry",
    "NodeStatus",
    "get_node_registry",
    "initialize_node_registry",
    # Health Checking
    "NodeHealthChecker",
    "HealthStatus",
    "HealthCheckResult",
    "get_health_checker",
    # Load Balancing
    "LoadBalancer",
    "LoadBalancingStrategy",
    "get_load_balancer",
]
