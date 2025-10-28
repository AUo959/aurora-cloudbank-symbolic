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

# Phase 1: Distributed Bridge Nodes
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

# Phase 2: Cross-Repository Continuity
from .repo_sync import (
    RepositorySynchronizer,
    RepositoryInfo,
    SyncStatus,
    SyncDirection,
    get_repository_synchronizer
)
from .anchor_propagation import (
    AnchorPropagator,
    AnchorRecord,
    get_anchor_propagator
)
from .cross_repo_bridge import (
    CrossRepositoryBridge,
    CrossRepoBridge,
    CrossRepoHandshakeStage,
    CrossRepoBridgeStatus,
    get_cross_repository_bridge
)

# Phase 3: ML Drift Prediction
from .drift_predictor import (
    DriftPredictor,
    DriftPrediction,
    DriftFeatures,
    DriftSeverity,
    PredictionConfidence,
    get_drift_predictor
)
from .pattern_analyzer import (
    PatternAnalyzer,
    DriftPattern,
    PatternType,
    get_pattern_analyzer
)
from .auto_corrector import (
    AutoCorrector,
    CorrectionAction,
    CorrectionStrategy,
    get_auto_corrector
)

# Phase 4: Multi-Layer Hierarchies
from .layer_manager import (
    LayerManager,
    LayerBridge,
    LayerConfiguration,
    BridgeLayer,
    LAYER_CONFIGS,
    get_layer_manager
)
from .hierarchy_validator import (
    HierarchyValidator,
    ValidationReport,
    ValidationIssue,
    ValidationSeverity,
    get_hierarchy_validator
)

__version__ = "2.0.0"
__anchor__ = "EOS_SEED_ORION_v2"
__ethics__ = "Picard_Delta_3_Extended"

__all__ = [
    # Phase 1: Distributed Consensus
    "RaftConsensus",
    "ConsensusState",
    "ConsensusConfig",
    "BridgeNode",
    "NodeRegistry",
    "NodeStatus",
    "get_node_registry",
    "initialize_node_registry",
    "NodeHealthChecker",
    "HealthStatus",
    "HealthCheckResult",
    "get_health_checker",
    "LoadBalancer",
    "LoadBalancingStrategy",
    "get_load_balancer",
    # Phase 2: Cross-Repository Continuity
    "RepositorySynchronizer",
    "RepositoryInfo",
    "SyncStatus",
    "SyncDirection",
    "get_repository_synchronizer",
    "AnchorPropagator",
    "AnchorRecord",
    "get_anchor_propagator",
    "CrossRepositoryBridge",
    "CrossRepoBridge",
    "CrossRepoHandshakeStage",
    "CrossRepoBridgeStatus",
    "get_cross_repository_bridge",
    # Phase 3: ML Drift Prediction
    "DriftPredictor",
    "DriftPrediction",
    "DriftFeatures",
    "DriftSeverity",
    "PredictionConfidence",
    "get_drift_predictor",
    "PatternAnalyzer",
    "DriftPattern",
    "PatternType",
    "get_pattern_analyzer",
    "AutoCorrector",
    "CorrectionAction",
    "CorrectionStrategy",
    "get_auto_corrector",
    # Phase 4: Multi-Layer Hierarchies
    "LayerManager",
    "LayerBridge",
    "LayerConfiguration",
    "BridgeLayer",
    "LAYER_CONFIGS",
    "get_layer_manager",
    "HierarchyValidator",
    "ValidationReport",
    "ValidationIssue",
    "ValidationSeverity",
    "get_hierarchy_validator",
]
