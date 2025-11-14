"""
Thread Transfer Bridge v2 - Basic Integration Tests

Simplified test suite validating core v2 functionality.

Thread: T1→BRIDGE_V2→BASIC_TESTS
DLP: context_tag=bridge_v2_basic_tests
Anchor: EOS_SEED_ORION_v2
"""

import pytest
from datetime import datetime

# Phase 1: Distributed Bridge Nodes
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_load_balancer,
    RaftConsensus,
    NodeStatus,
    LoadBalancingStrategy,
    ConsensusState,
)

# Phase 3: ML Drift Prediction
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_drift_predictor,
    get_pattern_analyzer,
    get_auto_corrector,
    DriftFeatures,
    DriftSeverity,
    CorrectionStrategy,
)

# Phase 4: Multi-Layer Hierarchies
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_layer_manager,
    get_hierarchy_validator,
    BridgeLayer,
)


# ============================================================================
# PHASE 1 TESTS: Distributed Bridge Nodes
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_node_registry_basic():
    """Test basic node registry operations."""
    registry = get_node_registry()
    
    # Register node with all required parameters
    node = await registry.register_node(
        hostname="test-node-basic",
        port=8080,
        region="us-east-1",
        capacity=100,
        version="2.0.0"
    )
    
    assert node is not None
    assert node.node_id is not None
    assert node.status == NodeStatus.STARTING
    assert node.capacity == 100
    assert node.version == "2.0.0"
    
    # Verify node can be retrieved
    retrieved = await registry.get_node(node.node_id)
    assert retrieved is not None
    assert retrieved.node_id == node.node_id
    
    # Cleanup
    success = await registry.unregister_node(node.node_id)
    assert success is True


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_load_balancer_basic():
    """Test basic load balancer functionality."""
    registry = get_node_registry()
    load_balancer = get_load_balancer()
    
    # Register two nodes
    node1 = await registry.register_node(
        hostname="lb-node-1",
        port=8080,
        region="us-east-1",
        capacity=100,
        version="2.0.0"
    )
    node2 = await registry.register_node(
        hostname="lb-node-2",
        port=8081,
        region="us-west-1",
        capacity=100,
        version="2.0.0"
    )
    
    # Mark nodes online
    await registry.update_heartbeat(node1.node_id)
    await registry.update_heartbeat(node2.node_id)
    
    # Set different loads
    await registry.update_node_load(node1.node_id, 80)
    await registry.update_node_load(node2.node_id, 20)
    
    # Get all online nodes
    nodes = await registry.get_online_nodes()
    assert len(nodes) >= 2
    
    # Test load balancer selection with explicit node list
    selected = load_balancer.select_node(nodes=nodes)
    assert selected is not None
    assert selected.node_id in [node1.node_id, node2.node_id]
    
    # Cleanup
    await registry.unregister_node(node1.node_id)
    await registry.unregister_node(node2.node_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_raft_consensus_basic():
    """Test basic Raft consensus operations."""
    consensus = RaftConsensus("test-node-consensus")
    
    # Initial state should be FOLLOWER
    assert consensus.state == ConsensusState.FOLLOWER
    assert consensus.current_term == 0
    
    # Become candidate
    await consensus.become_candidate()
    assert consensus.state == ConsensusState.CANDIDATE
    assert consensus.current_term == 1
    
    # Become leader
    await consensus.become_leader()
    assert consensus.state == ConsensusState.LEADER
    assert consensus.is_leader() is True
    
    # Append log entry (only leader can do this)
    log_entry = await consensus.append_log("test_command", {"key": "value"})
    assert log_entry is not None
    assert log_entry.term == 1
    assert log_entry.command == "test_command"


# ============================================================================
# PHASE 3 TESTS: ML Drift Prediction
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_drift_predictor_basic():
    """Test drift prediction with sample features."""
    predictor = get_drift_predictor()
    
    # Create sample features
    features = DriftFeatures(
        drift_velocity=0.001,
        drift_acceleration=0.0001,
        handshake_count=10,
        average_handshake_duration=0.5,
        failed_handshake_ratio=0.05,
        time_of_day=14.0,
        day_of_week=1,
        thread_age_hours=24.0,
        anchor_changes=2,
        sync_frequency=2.0,
        node_count=3
    )
    
    # Predict drift
    prediction = await predictor.predict_drift(
        current_features=features,
        thread_id="test_thread_pred_001"
    )
    
    assert prediction is not None
    assert prediction.predicted_drift >= 0.0
    assert prediction.severity in [
        DriftSeverity.NONE,
        DriftSeverity.LOW,
        DriftSeverity.MEDIUM,
        DriftSeverity.HIGH,
        DriftSeverity.CRITICAL
    ]
    assert len(prediction.recommendations) >= 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_pattern_analyzer_basic():
    """Test pattern analysis for drift trends."""
    analyzer = get_pattern_analyzer()
    
    # Add some observations
    base_time = datetime.now()
    for i in range(10):
        from datetime import timedelta
        timestamp = base_time + timedelta(hours=i)
        drift = 0.001 + (i * 0.0001)
        analyzer.add_observation(timestamp, drift)
    
    # Analyze patterns
    patterns = await analyzer.analyze_patterns()
    
    assert patterns is not None
    assert isinstance(patterns, list)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_auto_corrector_basic():
    """Test auto-correction action evaluation."""
    corrector = get_auto_corrector()
    
    # Test with moderate drift
    actions = await corrector.evaluate_correction(
        predicted_drift=0.003,  # 0.3%
        current_drift=0.001,
        thread_id="test_thread_correct_001",
        metadata={
            "failed_handshake_ratio": 0.05,
            "anchor_changes": 2,
            "node_count": 3
        }
    )
    
    assert actions is not None
    assert isinstance(actions, list)


# ============================================================================
# PHASE 4 TESTS: Multi-Layer Hierarchies
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_layer_manager_l1_bridge():
    """Test L1 (thread-to-thread) bridge creation."""
    layer_manager = get_layer_manager()
    
    # Create L1 bridge
    bridge = await layer_manager.create_bridge(
        bridge_id="l1_basic_001",
        layer=BridgeLayer.L1,
        source_id="thread_a",
        target_id="thread_b",
        thread_id="test_thread_l1_basic"
    )
    
    assert bridge is not None
    assert bridge.layer == BridgeLayer.L1
    assert bridge.bridge_id == "l1_basic_001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_layer_manager_statistics():
    """Test layer statistics gathering."""
    layer_manager = get_layer_manager()
    
    # Get statistics (should work even with no bridges)
    stats = layer_manager.get_layer_statistics()
    
    assert stats is not None
    assert "total_bridges" in stats
    assert "by_layer" in stats
    assert "by_status" in stats
    assert stats["total_bridges"] >= 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_hierarchy_validator_basic():
    """Test hierarchy validator initialization."""
    validator = get_hierarchy_validator()
    
    assert validator is not None
    
    # Test validation with empty bridge list
    report = await validator.validate_hierarchy(
        bridges=[],
        thread_id="test_thread_empty",
        strict_mode=False
    )
    
    assert report is not None


# ============================================================================
# SMOKE TESTS
# ============================================================================

@pytest.mark.smoke
@pytest.mark.bridge_v2
def test_v2_module_imports():
    """Smoke test: Verify all v2 modules can be imported."""
    from modules.reflective_autonomy.thread_transfer import v2
    
    assert hasattr(v2, '__version__')
    assert v2.__version__ == "2.0.0"
    assert v2.__anchor__ == "EOS_SEED_ORION_v2"
    assert v2.__ethics__ == "Picard_Delta_3_Extended"


@pytest.mark.smoke
@pytest.mark.bridge_v2
def test_v2_singletons_initialization():
    """Smoke test: Verify singleton getters work."""
    # Should not raise exceptions
    registry = get_node_registry()
    assert registry is not None
    
    load_balancer = get_load_balancer()
    assert load_balancer is not None
    
    predictor = get_drift_predictor()
    assert predictor is not None
    
    analyzer = get_pattern_analyzer()
    assert analyzer is not None
    
    corrector = get_auto_corrector()
    assert corrector is not None
    
    layer_manager = get_layer_manager()
    assert layer_manager is not None
    
    validator = get_hierarchy_validator()
    assert validator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
