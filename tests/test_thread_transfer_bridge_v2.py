"""
Thread Transfer Bridge v2 - Integration Tests
============================================

Comprehensive test suite for all v2 features:
- Distributed bridge nodes
- Cross-repository continuity
- ML drift prediction
- Multi-layer hierarchies

Thread: T1→BRIDGE_V2→TESTS
DLP: context_tag=bridge_v2_integration_tests
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import pytest
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Phase 1: Distributed Bridge Nodes
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_node_registry,
    get_health_checker,
    get_load_balancer,
    RaftConsensus,
    NodeStatus,
    LoadBalancingStrategy,
    ConsensusState,
)

# Phase 2: Cross-Repository Continuity
from modules.reflective_autonomy.thread_transfer.v2 import (
    get_repository_synchronizer,
    get_anchor_propagator,
    get_cross_repository_bridge,
    SyncDirection,
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
async def test_node_registry_lifecycle():
    """Test complete node lifecycle: register → heartbeat → unregister."""
    registry = get_node_registry()
    
    # Register node
    node = await registry.register_node(
        hostname="test-node-1",
        port=8080,
        region="us-east-1",
        capacity=100
    )
    
    assert node is not None
    assert node.node_id is not None
    assert node.status == NodeStatus.STARTING
    assert node.capacity == 100
    
    # Update heartbeat (should transition to ONLINE)
    await registry.update_heartbeat(node.node_id)
    updated_node = registry.get_node(node.node_id)
    assert updated_node.status == NodeStatus.ONLINE
    
    # Update load
    await registry.update_node_load(node.node_id, 50)
    assert updated_node.current_load == 50
    assert updated_node.available_capacity() == 50
    
    # Unregister
    success = await registry.unregister_node(node.node_id)
    assert success is True
    assert registry.get_node(node.node_id) is None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_health_checker_multi_metric():
    """Test 4-metric health checking system."""
    registry = get_node_registry()
    health_checker = get_health_checker()
    
    # Register test node
    node = await registry.register_node(
        hostname="test-node-health",
        port=8080,
        region="us-west-1"
    )
    await registry.update_heartbeat(node.node_id)
    
    # Check health
    result = await health_checker.check_node_health(
        node.node_id,
        expected_anchor="EOS_SEED_ORION_v2"
    )
    
    assert result is not None
    assert result.node_id == node.node_id
    # Note: Some checks may fail (e.g., API endpoint) in test environment
    assert result.heartbeat_check is True
    
    # Cleanup
    await registry.unregister_node(node.node_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_load_balancer_weighted_selection():
    """Test weighted load balancing with regional preference."""
    registry = get_node_registry()
    load_balancer = get_load_balancer()
    
    # Register multiple nodes
    node1 = await registry.register_node(
        hostname="node-1", port=8080, region="us-east-1", capacity=100
    )
    node2 = await registry.register_node(
        hostname="node-2", port=8081, region="us-west-1", capacity=100
    )
    node3 = await registry.register_node(
        hostname="node-3", port=8082, region="us-east-1", capacity=100
    )
    
    # Mark all online
    for node in [node1, node2, node3]:
        await registry.update_heartbeat(node.node_id)
    
    # Set different loads
    await registry.update_node_load(node1.node_id, 80)  # High load
    await registry.update_node_load(node2.node_id, 20)  # Low load
    await registry.update_node_load(node3.node_id, 50)  # Medium load
    
    # Test LEAST_LOADED strategy
    selected = await load_balancer.select_node(
        strategy=LoadBalancingStrategy.LEAST_LOADED
    )
    assert selected.node_id == node2.node_id  # Should pick lowest load
    
    # Test WEIGHTED with regional preference
    selected_regional = await load_balancer.select_node(
        strategy=LoadBalancingStrategy.WEIGHTED,
        preferred_region="us-east-1"
    )
    # Should prefer us-east-1 nodes (node1 or node3)
    assert selected_regional.region == "us-east-1"
    
    # Cleanup
    await registry.unregister_node(node1.node_id)
    await registry.unregister_node(node2.node_id)
    await registry.unregister_node(node3.node_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_raft_consensus_basic():
    """Test basic Raft consensus operations."""
    consensus = initialize_consensus("test-node-consensus")
    
    # Initial state should be FOLLOWER
    assert consensus.state == ConsensusState.FOLLOWER
    assert consensus.current_term == 0
    
    # Become candidate (would happen on election timeout)
    await consensus.become_candidate()
    assert consensus.state == ConsensusState.CANDIDATE
    assert consensus.current_term == 1
    assert consensus.voted_for == "test-node-consensus"
    
    # Become leader
    await consensus.become_leader()
    assert consensus.state == ConsensusState.LEADER
    assert consensus.is_leader() is True
    
    # Append log entry (only leader can do this)
    log_entry = await consensus.append_log("test_command", {"key": "value"})
    assert log_entry is not None
    assert log_entry.term == 1
    assert log_entry.command == "test_command"
    
    # Get state info
    state_info = await consensus.get_state_info()
    assert state_info["state"] == "LEADER"
    assert state_info["log_length"] == 1


# ============================================================================
# PHASE 2 TESTS: Cross-Repository Continuity
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_anchor_propagation_lifecycle():
    """Test anchor write, read, and propagation."""
    propagator = get_anchor_propagator()
    
    # Create temporary Git repositories for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        source_repo = Path(tmpdir) / "source"
        target_repo = Path(tmpdir) / "target"
        
        # Initialize Git repos
        for repo_path in [source_repo, target_repo]:
            repo_path.mkdir()
            os.system(f"cd {repo_path} && git init && git config user.email 'test@example.com' && git config user.name 'Test' && echo 'test' > README.md && git add . && git commit -m 'Initial'")
        
        # Write anchor to source
        anchor_record = await propagator.write_anchor(
            repo_path=str(source_repo),
            anchor_hash="TEST_ANCHOR_001",
            thread_id="test_thread_001",
            repo_id="source_repo",
            branch="main",
            metadata={"test": "data"}
        )
        
        assert anchor_record is not None
        assert anchor_record.anchor_hash == "TEST_ANCHOR_001"
        assert anchor_record.thread_id == "test_thread_001"
        
        # Read anchor from source
        read_anchor = await propagator.read_anchor(
            repo_path=str(source_repo),
            branch="main"
        )
        
        assert read_anchor is not None
        assert read_anchor.anchor_hash == "TEST_ANCHOR_001"
        assert read_anchor.thread_id == "test_thread_001"
        
        # Propagate to target
        propagation_result = await propagator.propagate_anchor(
            source_repo_path=str(source_repo),
            target_repo_path=str(target_repo),
            thread_id="test_thread_001",
            target_repo_id="target_repo",
            source_branch="main",
            target_branch="main"
        )
        
        assert propagation_result["success"] is True
        assert propagation_result["anchor_hash"] == "TEST_ANCHOR_001"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_repository_synchronizer_registration():
    """Test repository registration and management."""
    synchronizer = get_repository_synchronizer()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test_repo"
        repo_path.mkdir()
        
        # Initialize Git repo
        os.system(f"cd {repo_path} && git init && git config user.email 'test@example.com' && git config user.name 'Test' && echo 'test' > README.md && git add . && git commit -m 'Initial'")
        
        # Register repository
        repo_info = await synchronizer.register_repository(
            repo_id="test_repo_001",
            repo_path=str(repo_path),
            branch="main"
        )
        
        assert repo_info is not None
        assert repo_info.repo_id == "test_repo_001"
        assert repo_info.branch == "main"
        
        # List repositories
        repos = synchronizer.list_repositories()
        assert len(repos) >= 1
        assert any(r.repo_id == "test_repo_001" for r in repos)
        
        # Unregister
        success = await synchronizer.unregister_repository("test_repo_001")
        assert success is True


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
    assert prediction.severity in [DriftSeverity.NONE, DriftSeverity.LOW, DriftSeverity.MEDIUM]
    assert len(prediction.recommendations) > 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_pattern_analyzer_trends():
    """Test pattern analysis for drift trends."""
    analyzer = get_pattern_analyzer()
    
    # Add observations (simulating increasing drift)
    base_time = datetime.now()
    for i in range(30):
        timestamp = base_time + timedelta(hours=i)
        drift = 0.001 + (i * 0.0001)  # Increasing trend
        analyzer.add_observation(timestamp, drift)
    
    # Analyze patterns
    patterns = await analyzer.analyze_patterns()
    
    assert len(patterns) > 0
    # Should detect trending pattern
    assert any(p.pattern_type.value == "trending" for p in patterns)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_auto_corrector_evaluation():
    """Test auto-correction action evaluation."""
    corrector = get_auto_corrector()
    
    # Test with high predicted drift (should trigger corrections)
    actions = await corrector.evaluate_correction(
        predicted_drift=0.006,  # 0.6% - above auto-correct threshold
        current_drift=0.002,
        thread_id="test_thread_correct_001",
        metadata={
            "failed_handshake_ratio": 0.15,
            "anchor_changes": 8,
            "node_count": 2
        }
    )
    
    assert len(actions) > 0
    # Should include resync and frequency increase
    strategies = {a.strategy for a in actions}
    assert CorrectionStrategy.RESYNC_ANCHOR in strategies
    assert CorrectionStrategy.INCREASE_FREQUENCY in strategies


# ============================================================================
# PHASE 4 TESTS: Multi-Layer Hierarchies
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_layer_manager_l1_bridge():
    """Test L1 (thread-to-thread) bridge creation and execution."""
    layer_manager = get_layer_manager()
    
    # Create L1 bridge
    bridge = await layer_manager.create_bridge(
        bridge_id="l1_test_001",
        layer=BridgeLayer.L1,
        source_id="thread_a",
        target_id="thread_b",
        thread_id="test_thread_l1_001"
    )
    
    assert bridge is not None
    assert bridge.layer == BridgeLayer.L1
    assert bridge.status == "idle"
    
    # Execute L1 handshake
    result = await layer_manager.execute_layered_handshake(bridge.bridge_id)
    
    assert result["success"] is True
    assert result["stages_completed"] == 5  # L1 has 5 stages
    assert result["drift_percentage"] <= 0.0  # L1 max drift is 0.0%


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_layer_manager_l2_bridge_requires_l1():
    """Test that L2 bridge requires L1 foundation."""
    layer_manager = get_layer_manager()
    
    # Try to create L2 without L1 (should fail)
    with pytest.raises(Exception):  # Should raise LayerValidationError
        await layer_manager.create_bridge(
            bridge_id="l2_test_001",
            layer=BridgeLayer.L2,
            source_id="repo_a",
            target_id="repo_b",
            thread_id="test_thread_l2_001"
        )
    
    # Create L1 first
    l1_bridge = await layer_manager.create_bridge(
        bridge_id="l1_for_l2_001",
        layer=BridgeLayer.L1,
        source_id="thread_a",
        target_id="thread_b",
        thread_id="test_thread_l2_001"
    )
    await layer_manager.execute_layered_handshake(l1_bridge.bridge_id)
    
    # Now L2 should work
    l2_bridge = await layer_manager.create_bridge(
        bridge_id="l2_test_002",
        layer=BridgeLayer.L2,
        source_id="repo_a",
        target_id="repo_b",
        thread_id="test_thread_l2_001"
    )
    
    assert l2_bridge is not None
    assert l2_bridge.layer == BridgeLayer.L2


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_hierarchy_validator_cascade():
    """Test cascading validation across layers."""
    layer_manager = get_layer_manager()
    validator = get_hierarchy_validator()
    
    thread_id = "test_thread_cascade_001"
    
    # Create complete hierarchy: L1 → L2
    l1_bridge = await layer_manager.create_bridge(
        bridge_id="cascade_l1_001",
        layer=BridgeLayer.L1,
        source_id="thread_a",
        target_id="thread_b",
        thread_id=thread_id
    )
    await layer_manager.execute_layered_handshake(l1_bridge.bridge_id)
    
    l2_bridge = await layer_manager.create_bridge(
        bridge_id="cascade_l2_001",
        layer=BridgeLayer.L2,
        source_id="repo_a",
        target_id="repo_b",
        thread_id=thread_id
    )
    await layer_manager.execute_layered_handshake(l2_bridge.bridge_id)
    
    # Get all bridges for thread
    bridges = layer_manager.list_bridges(thread_id=thread_id)
    
    # Validate hierarchy
    report = await validator.validate_hierarchy(
        bridges=bridges,
        thread_id=thread_id,
        strict_mode=True
    )
    
    assert report is not None
    assert report.valid is True
    assert "L1" in report.layer_status
    assert "L2" in report.layer_status
    assert report.layer_status["L1"] == "valid"
    assert report.layer_status["L2"] == "valid"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_layer_statistics():
    """Test layer statistics gathering."""
    layer_manager = get_layer_manager()
    
    # Create multiple bridges
    for i in range(3):
        await layer_manager.create_bridge(
            bridge_id=f"stats_l1_{i}",
            layer=BridgeLayer.L1,
            source_id=f"source_{i}",
            target_id=f"target_{i}",
            thread_id=f"thread_{i}"
        )
    
    # Get statistics
    stats = layer_manager.get_layer_statistics()
    
    assert stats["total_bridges"] >= 3
    assert "by_layer" in stats
    assert "by_status" in stats
    assert stats["by_layer"]["L1"] >= 3


# ============================================================================
# INTEGRATION TESTS: Cross-Phase Workflows
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
@pytest.mark.slow
async def test_complete_workflow_distributed_l1_bridge():
    """
    Test complete workflow: Register nodes → Create L1 bridge → 
    Predict drift → Validate → Auto-correct if needed.
    """
    # Setup: Register distributed nodes
    registry = get_node_registry()
    node1 = await registry.register_node(
        hostname="workflow-node-1", port=8080, region="us-east-1", capacity=100
    )
    node2 = await registry.register_node(
        hostname="workflow-node-2", port=8081, region="us-east-1", capacity=100
    )
    
    for node in [node1, node2]:
        await registry.update_heartbeat(node.node_id)
    
    # Create L1 bridge
    layer_manager = get_layer_manager()
    bridge = await layer_manager.create_bridge(
        bridge_id="workflow_bridge_001",
        layer=BridgeLayer.L1,
        source_id="thread_source",
        target_id="thread_target",
        thread_id="workflow_thread_001"
    )
    
    # Execute handshake
    handshake_result = await layer_manager.execute_layered_handshake(bridge.bridge_id)
    assert handshake_result["success"] is True
    
    # Predict future drift
    predictor = get_drift_predictor()
    features = DriftFeatures(
        drift_velocity=handshake_result["drift_percentage"] * 0.1,
        drift_acceleration=0.0,
        handshake_count=1,
        average_handshake_duration=0.3,
        failed_handshake_ratio=0.0,
        time_of_day=datetime.now().hour,
        day_of_week=datetime.now().weekday(),
        thread_age_hours=1.0,
        anchor_changes=0,
        sync_frequency=1.0,
        node_count=2
    )
    
    prediction = await predictor.predict_drift(features, "workflow_thread_001")
    assert prediction is not None
    
    # Validate hierarchy
    validator = get_hierarchy_validator()
    bridges = layer_manager.list_bridges(thread_id="workflow_thread_001")
    report = await validator.validate_hierarchy(
        bridges=bridges,
        thread_id="workflow_thread_001",
        strict_mode=False
    )
    
    assert report.valid is True
    
    # Cleanup
    await registry.unregister_node(node1.node_id)
    await registry.unregister_node(node2.node_id)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
async def test_backward_compatibility_with_v1():
    """
    Test that v2 modules can coexist with v1 without breaking changes.
    """
    # Import v1 modules (if available)
    try:
        from modules.reflective_autonomy.thread_transfer.v1 import (
            get_thread_transfer_bridge as get_v1_bridge
        )
        
        # v1 bridge should still work
        v1_bridge = get_v1_bridge()
        assert v1_bridge is not None
        
        # v2 modules should not interfere
        from modules.reflective_autonomy.thread_transfer.v2 import (
            get_layer_manager
        )
        v2_manager = get_layer_manager()
        assert v2_manager is not None
        
    except ImportError:
        # v1 may not be available in test environment
        pytest.skip("v1 modules not available for backward compatibility test")


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.bridge_v2
@pytest.mark.slow
async def test_consensus_performance():
    """Test Raft consensus performance (< 50ms per operation)."""
    consensus = initialize_consensus("perf-test-node")
    await consensus.become_leader()
    
    # Measure log append performance
    start_time = datetime.now()
    iterations = 100
    
    for i in range(iterations):
        await consensus.append_log(f"command_{i}", {"data": i})
    
    end_time = datetime.now()
    duration_ms = (end_time - start_time).total_seconds() * 1000
    avg_ms = duration_ms / iterations
    
    # Should be < 50ms per operation (as per architecture spec)
    assert avg_ms < 50, f"Consensus too slow: {avg_ms:.2f}ms per operation"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
