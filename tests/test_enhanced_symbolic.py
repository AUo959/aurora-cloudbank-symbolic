"""Tests for Enhanced Aurora Cloudbank Symbolic Engine"""
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_entropy_tracking():
    """Test entropy-state awareness module"""
    from aurora.core.symbolic_engine import T1Anchor, SRBAnchor
    
    # Test T1 entropy tracking
    t1 = T1Anchor()
    initial_entropy = t1.entropy
    
    # Advance with data and check entropy changes
    t1.advance("test_data_for_entropy")
    assert t1.entropy != initial_entropy
    assert len(t1.entropy_history) > 0
    
    # Check entropy status
    entropy_status = t1.get_entropy_status()
    assert "current_entropy" in entropy_status
    assert "warning" in entropy_status
    assert isinstance(entropy_status["warning"], bool)
    
    # Test SRB entropy tracking
    srb = SRBAnchor()
    initial_srb_entropy = srb.entropy
    
    srb.resolve("test_boundary_for_entropy")
    assert srb.entropy != initial_srb_entropy
    assert len(srb.entropy_history) > 0
    
    srb_status = srb.get_entropy_status()
    assert "current_entropy" in srb_status
    assert "warning" in srb_status
    
    # Add a second operation to test drift detection
    srb.resolve("another_boundary_for_entropy_testing")
    srb_status_2 = srb.get_entropy_status()
    assert "spatial_drift_detected" in srb_status_2


def test_memory_sealing():
    """Test memory sealing protocols"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Test thread sealing
    thread_data = {"test": "data", "values": [1, 2, 3], "nested": {"key": "value"}}
    sealed = engine.seal_thread("test_thread_001", thread_data)
    
    assert sealed["thread_id"] == "test_thread_001"
    assert "seal_timestamp" in sealed
    assert "integrity_hash" in sealed
    assert "test_thread_001" in engine.sealed_threads
    
    # Test thread rehydration
    rehydrated = engine.rehydrate_thread("test_thread_001")
    assert rehydrated is not None
    assert rehydrated["thread_id"] == "test_thread_001"
    assert rehydrated["data"] == thread_data
    
    # Test non-existent thread
    non_existent = engine.rehydrate_thread("non_existent")
    assert non_existent is None


def test_enhanced_export_system():
    """Test enhanced export system with metadata and DLP tagging"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Add DLP tags
    engine.add_dlp_tag("sensitive_data", "reference_001")
    engine.add_dlp_tag("classified", "reference_002")
    
    # Update reliquary index
    engine.update_reliquary_index("thread_001", {"type": "temporal", "priority": "high"})
    
    # Test enhanced manifest export
    manifest = engine.export_manifest()
    
    assert manifest["version"] == "2.0.0"
    assert "export_timestamp" in manifest
    assert "entropy_summary" in manifest
    assert len(manifest["dlp_tags"]) == 2
    assert "sensitive_data" in manifest["dlp_tags"]
    assert "classified" in manifest["dlp_tags"]
    assert "thread_001" in manifest["reliquary_index"]


def test_chain_branching():
    """Test enhanced chain notation with branching"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Test basic chain execution
    result1 = engine.execute_chain(1, 5)
    assert len(result1) == 5
    assert "001//005//" in engine.chains
    
    # Test branched chain execution
    result2 = engine.execute_chain(1, 5, "alpha")
    assert len(result2) == 5
    assert "001//005//alpha//" in engine.chains
    
    # Test different branch
    result3 = engine.execute_chain(10, 15, "beta")
    assert len(result3) == 6
    assert "010//015//beta//" in engine.chains
    
    # Ensure all chains are stored separately
    assert len(engine.chains) == 3


def test_snapshot_functionality():
    """Test simulation snapshot logic"""
    from aurora.core.symbolic_engine import SymbolicEngine
    
    engine = SymbolicEngine()
    
    # Execute some operations to create state
    engine.execute_chain(1, 3)
    engine.seal_thread("snapshot_test", {"data": "initial"})
    
    # Create first snapshot
    snapshot1 = engine.create_snapshot("snapshot_001")
    assert snapshot1["snapshot_id"] == "snapshot_001"
    assert "timestamp" in snapshot1
    assert "t1_anchor" in snapshot1
    assert "srb_anchor" in snapshot1
    
    # Modify state
    time.sleep(0.1)  # Ensure timestamp difference
    engine.execute_chain(5, 7)
    engine.seal_thread("snapshot_test_2", {"data": "modified"})
    
    # Create second snapshot
    snapshot2 = engine.create_snapshot("snapshot_002")
    
    # Compare snapshots
    comparison = engine.compare_snapshots("snapshot_001", "snapshot_002")
    assert "timestamp_diff" in comparison
    assert comparison["timestamp_diff"] > 0
    assert "t1_state_diff" in comparison
    assert "sealed_threads_diff" in comparison


def test_cli_checkpoint_system():
    """Test CLI checkpoint and rollback system"""
    from aurora.cli.symbolic_cli import SymbolicCLI
    
    cli = SymbolicCLI()
    
    # Execute initial chain
    cli.execute_chain(1, 5)
    initial_state = cli.engine.t1.state
    
    # Create checkpoint
    checkpoint_name = cli.create_checkpoint("test_checkpoint")
    assert checkpoint_name in cli.checkpoints
    
    # Modify state
    cli.execute_chain(10, 15)
    modified_state = cli.engine.t1.state
    assert modified_state != initial_state
    
    # Rollback to checkpoint
    success = cli.rollback_to_checkpoint("test_checkpoint")
    assert success is True
    assert cli.engine.t1.state == initial_state
    
    # Test rollback to non-existent checkpoint
    fail_rollback = cli.rollback_to_checkpoint("non_existent")
    assert fail_rollback is False


def test_parallel_chain_execution():
    """Test parallel chain execution via CLI"""
    from aurora.cli.symbolic_cli import SymbolicCLI
    
    cli = SymbolicCLI()
    
    # Define parallel chain specifications
    chain_specs = [
        [1, 5, "alpha"],
        [6, 10, "beta"],
        [11, 15, "gamma"]
    ]
    
    # Execute parallel chains
    results = cli.execute_parallel_chains(chain_specs)
    
    assert len(results) == 3
    assert "001//005//alpha//" in results
    assert "006//010//beta//" in results
    assert "011//015//gamma//" in results
    
    # Verify all chains are stored in engine
    assert len(cli.engine.chains) == 3


def test_symbolic_helpers():
    """Test automated symbolic helpers"""
    from aurora.core.symbolic_engine import SymbolicEngine
    from aurora.utils.symbolic_helpers import SymbolicHelpers
    
    engine = SymbolicEngine()
    
    # Create two different states for comparison
    engine.execute_chain(1, 3)
    state1 = engine.export_manifest()
    
    engine.execute_chain(5, 7)
    state2 = engine.export_manifest()
    
    # Test state comparison
    comparison = SymbolicHelpers.compare_symbolic_states(state1, state2)
    assert "comparison_timestamp" in comparison
    assert "summary" in comparison
    assert comparison["summary"]["total_changes"] > 0
    
    # Test glyphcard generation
    thread_data = {"type": "test", "values": [1, 2, 3]}
    glyphcard = SymbolicHelpers.generate_glyphcard("test_thread", thread_data)
    assert glyphcard["thread_id"] == "test_thread"
    assert "generation_timestamp" in glyphcard
    assert "complexity_analysis" in glyphcard
    
    # Test operation helpers export
    helpers = SymbolicHelpers.export_operation_helpers("chain_execution")
    assert helpers["operation_type"] == "chain_execution"
    assert "recommended_ranges" in helpers["helpers"]
    
    # Test integrity validation
    validation = SymbolicHelpers.validate_symbolic_integrity(state2)
    assert "overall_status" in validation
    assert validation["overall_status"] in ["healthy", "warning", "critical"]


def test_automated_snapshot_scheduling():
    """Test automated snapshot scheduling"""
    from aurora.core.symbolic_engine import SymbolicEngine
    from aurora.utils.symbolic_helpers import SymbolicHelpers
    
    engine = SymbolicEngine()
    
    # Test snapshot scheduling configuration
    schedule = SymbolicHelpers.schedule_automated_snapshots(engine, interval_minutes=15)
    assert schedule["interval_minutes"] == 15
    assert "next_snapshot_time" in schedule
    assert "retention_policy" in schedule
    assert schedule["retention_policy"]["max_snapshots"] == 24


def test_comprehensive_integration():
    """Test comprehensive integration of all enhanced features"""
    from aurora.core.symbolic_engine import SymbolicEngine
    from aurora.cli.symbolic_cli import SymbolicCLI
    from aurora.utils.symbolic_helpers import SymbolicHelpers
    
    # Create engine and CLI
    engine = SymbolicEngine()
    cli = SymbolicCLI()
    
    # Execute complex workflow
    # 1. Execute branched chains
    engine.execute_chain(1, 10, "main")
    engine.execute_chain(1, 10, "experimental")
    
    # 2. Seal important threads
    thread_data = {"experiment": "alpha", "results": [0.1, 0.2, 0.3]}
    engine.seal_thread("experiment_alpha", thread_data)
    
    # 3. Add DLP tagging
    engine.add_dlp_tag("experimental", "experiment_alpha")
    
    # 4. Create snapshot
    snapshot = engine.create_snapshot("integration_test")
    
    # 5. Create checkpoint via CLI
    cli.create_checkpoint("integration_checkpoint")
    
    # 6. Generate glyphcard
    glyphcard = SymbolicHelpers.generate_glyphcard("experiment_alpha", thread_data)
    
    # 7. Export comprehensive manifest
    manifest = engine.export_manifest()
    
    # Verify integration
    assert len(engine.chains) == 2  # main and experimental branches
    assert "experiment_alpha" in engine.sealed_threads
    assert "experimental" in engine.dlp_tags
    assert "integration_test" in engine.thread_snapshots
    assert "integration_checkpoint" in cli.checkpoints
    assert glyphcard["thread_id"] == "experiment_alpha"
    assert manifest["version"] == "2.0.0"
    assert manifest["entropy_summary"]["t1_current"] > 0
    assert manifest["entropy_summary"]["srb_current"] > 0


# Test runner function
def run_all_tests():
    """Run all enhanced functionality tests"""
    test_functions = [
        test_entropy_tracking,
        test_memory_sealing,
        test_enhanced_export_system,
        test_chain_branching,
        test_snapshot_functionality,
        test_cli_checkpoint_system,
        test_parallel_chain_execution,
        test_symbolic_helpers,
        test_automated_snapshot_scheduling,
        test_comprehensive_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__} - PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} - FAILED: {str(e)}")
            failed += 1
    
    print(f"\n🎯 Test Results: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)