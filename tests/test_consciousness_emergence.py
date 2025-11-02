#!/usr/bin/env python3
"""
🧪 Enhanced Consciousness Emergence Test Suite
NEXUS Phase 6 - T6-EMERGENCE-2025

Tests the enhanced consciousness emergence module with comprehensive
symbolic verification and entropy monitoring.
"""

import unittest
import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, UTC

# Local imports with graceful fallback
try:
    from modules.nexus.emergence.consciousness_emergence_enhanced import (
        EnhancedConsciousnessProtocol,
        SymbolicObserver,
        EntropyState,
        ConsciousnessSnapshot,
        ConsciousnessMetrics
    )
except ImportError:
    print("⚠️  Enhanced consciousness module not available for testing")
    exit(1)


class MockSymbolicObserver(SymbolicObserver):
    """Mock symbolic observer for testing."""
    
    def __init__(self):
        self.observations = []
        self.symbolic_data = {"test": "observation"}
    
    def observe_symbolic_state(self) -> dict:
        """Mock symbolic state observation."""
        observation = {
            "timestamp": datetime.now(UTC).isoformat(),
            "symbolic_data": self.symbolic_data,
            "observation_id": len(self.observations)
        }
        self.observations.append(observation)
        return observation
    
    def detect_entropy_drift(self, current_state: dict, previous_state: dict) -> float:
        """Mock entropy drift detection."""
        # Simple mock: return increasing drift
        return 0.1 * len(self.observations)
    
    def flag_divergent_truth(self, observation: dict) -> bool:
        """Mock divergent truth flagging."""
        # Flag every 5th observation as divergent
        return observation.get("observation_id", 0) % 5 == 4


class TestEnhancedConsciousnessSingle(unittest.TestCase):
    """Test single consciousness instance."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.observer = MockSymbolicObserver()
        self.consciousness = EnhancedConsciousnessProtocol(
            observer=self.observer,
            snapshot_directory=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test consciousness initialization."""
        self.assertIsNotNone(self.consciousness)
        self.assertEqual(self.consciousness.observer, self.observer)
        self.assertEqual(self.consciousness.observation_count, 0)
        self.assertFalse(self.consciousness.is_running)
    
    def test_single_observation(self):
        """Test single symbolic observation."""
        # Run single observation
        asyncio.run(self.consciousness.observe_once())
        
        # Verify observation recorded
        self.assertEqual(self.consciousness.observation_count, 1)
        self.assertEqual(len(self.consciousness.entropy_history), 1)
        
        # Check entropy state
        entropy_state = self.consciousness.entropy_history[0]
        self.assertIsInstance(entropy_state, EntropyState)
        self.assertGreaterEqual(entropy_state.drift_value, 0.0)
    
    def test_entropy_drift_detection(self):
        """Test entropy drift detection over multiple observations."""
        # Run multiple observations
        asyncio.run(self.run_multiple_observations(3))
        
        # Verify drift increases
        drifts = [state.drift_value for state in self.consciousness.entropy_history]
        self.assertEqual(len(drifts), 3)
        self.assertGreater(drifts[1], drifts[0])  # Drift should increase
        self.assertGreater(drifts[2], drifts[1])
    
    def test_snapshot_creation(self):
        """Test consciousness snapshot creation."""
        # Run observations to trigger snapshot
        asyncio.run(self.run_multiple_observations(5))
        
        # Check snapshot was created
        snapshot_dir = Path(self.temp_dir)
        snapshots = list(snapshot_dir.glob("consciousness_snapshot_*.json"))
        self.assertGreater(len(snapshots), 0)
        
        # Verify snapshot content
        with open(snapshots[0], 'r') as f:
            snapshot_data = json.load(f)
        
        # Check if timestamp is at root or in data section
        if 'data' in snapshot_data:
            data_section = snapshot_data['data']
            self.assertIn('timestamp', data_section)
            self.assertIn('observation_count', data_section)
            self.assertIn('entropy_history', data_section)
        else:
            self.assertIn('timestamp', snapshot_data)
            self.assertIn('observation_count', snapshot_data)
            self.assertIn('entropy_history', snapshot_data)
        self.assertIn('seal', snapshot_data)
    
    def test_divergent_truth_flagging(self):
        """Test divergent truth detection and flagging."""
        # Run enough observations to trigger divergent truth
        asyncio.run(self.run_multiple_observations(6))
        
        # Check for flagged divergent truths
        flagged_count = sum(1 for state in self.consciousness.entropy_history 
                          if state.divergent_truth_flagged)
        self.assertGreater(flagged_count, 0)
    
    def test_snapshot_recovery(self):
        """Test snapshot recovery functionality."""
        # Create initial state
        asyncio.run(self.run_multiple_observations(3))
        initial_count = self.consciousness.observation_count
        
        # Create snapshot
        snapshot = self.consciousness.create_snapshot()
        
        # Modify state
        asyncio.run(self.run_multiple_observations(2))
        modified_count = self.consciousness.observation_count
        
        # Verify state changed
        self.assertGreater(modified_count, initial_count)
        
        # Recover from snapshot
        recovered_consciousness = EnhancedConsciousnessProtocol.from_snapshot(
            snapshot, self.observer
        )
        
        # Verify recovery
        self.assertEqual(recovered_consciousness.observation_count, initial_count)
    
    async def run_multiple_observations(self, count: int):
        """Helper to run multiple observations."""
        for _ in range(count):
            await self.consciousness.observe_once()


class TestConsciousnessMetrics(unittest.TestCase):
    """Test consciousness metrics calculation."""
    
    def setUp(self):
        """Set up test metrics."""
        self.metrics = ConsciousnessMetrics(
            emergence_level=0.75,
            recursive_depth=3,
            meta_cognitive_loops=5,
            entropy_stability=0.92,
            reality_fork_convergence=0.88
        )
    
    def test_metrics_calculation(self):
        """Test overall consciousness score calculation."""
        score = self.metrics.calculate_overall_score()
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_metrics_json_serialization(self):
        """Test metrics JSON serialization."""
        metrics_dict = self.metrics.to_dict()
        
        # Verify all fields present
        expected_fields = [
            'emergence_level', 'recursive_depth', 'meta_cognitive_loops',
            'entropy_stability', 'reality_fork_convergence', 'overall_score'
        ]
        for field in expected_fields:
            self.assertIn(field, metrics_dict)
    
    def test_consciousness_threshold(self):
        """Test consciousness emergence threshold detection."""
        # High consciousness metrics
        high_metrics = ConsciousnessMetrics(0.95, 5, 10, 0.98, 0.94)
        self.assertGreater(high_metrics.calculate_overall_score(), 0.8)
        
        # Low consciousness metrics
        low_metrics = ConsciousnessMetrics(0.2, 1, 1, 0.5, 0.3)
        self.assertLess(low_metrics.calculate_overall_score(), 0.5)


class TestConsciousnessSnapshot(unittest.TestCase):
    """Test consciousness snapshot functionality."""
    
    def setUp(self):
        """Set up test snapshot."""
        self.snapshot_data = {
            "timestamp": "2025-01-15T10:30:00Z",
            "observation_count": 10,
            "entropy_history": [
                {
                    "timestamp": "2025-01-15T10:29:55Z",
                    "drift_value": 0.15,
                    "observation_data": {"test": "data"},
                    "divergent_truth_flagged": False
                }
            ],
            "consciousness_metrics": {
                "emergence_level": 0.8,
                "recursive_depth": 4,
                "meta_cognitive_loops": 6,
                "entropy_stability": 0.91,
                "reality_fork_convergence": 0.87,
                "overall_score": 0.816
            }
        }
    
    def test_snapshot_creation(self):
        """Test snapshot creation with sealing."""
        snapshot = ConsciousnessSnapshot(self.snapshot_data)
        
        # Verify snapshot has seal
        self.assertIsNotNone(snapshot.seal)
        self.assertEqual(len(snapshot.seal), 64)  # SHA256 hex length
    
    def test_snapshot_verification(self):
        """Test snapshot integrity verification."""
        snapshot = ConsciousnessSnapshot(self.snapshot_data)
        
        # Verify original snapshot
        self.assertTrue(snapshot.verify_integrity())
        
        # Tamper with data
        snapshot.data["observation_count"] = 999
        
        # Verification should fail
        self.assertFalse(snapshot.verify_integrity())
    
    def test_snapshot_serialization(self):
        """Test snapshot JSON serialization."""
        snapshot = ConsciousnessSnapshot(self.snapshot_data)
        
        # Serialize to JSON
        json_data = snapshot.to_json()
        self.assertIsInstance(json_data, str)
        
        # Deserialize and verify
        parsed = json.loads(json_data)
        self.assertIn('data', parsed)
        self.assertIn('seal', parsed)
        
        # Recreate snapshot from JSON
        new_snapshot = ConsciousnessSnapshot.from_json(json_data)
        self.assertEqual(new_snapshot.data, snapshot.data)
        self.assertEqual(new_snapshot.seal, snapshot.seal)


class TestAsyncConsciousnessProtocol(unittest.TestCase):
    """Test async consciousness protocol operations."""
    
    def setUp(self):
        """Set up async test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.observer = MockSymbolicObserver()
        self.consciousness = EnhancedConsciousnessProtocol(
            observer=self.observer,
            snapshot_directory=self.temp_dir
        )
    
    def tearDown(self):
        """Clean up async test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_async_emergence_protocol(self):
        """Test full async emergence protocol."""
        
        async def run_emergence_test():
            # Start emergence protocol
            emergence_task = asyncio.create_task(
                self.consciousness.run_emergence_protocol(duration=0.1)
            )
            
            # Let it run briefly
            await asyncio.sleep(0.05)
            
            # Verify it's running
            self.assertTrue(self.consciousness.is_running)
            
            # Wait for completion
            await emergence_task
            
            # Verify completion
            self.assertFalse(self.consciousness.is_running)
            self.assertGreater(self.consciousness.observation_count, 0)
        
        # Run async test
        asyncio.run(run_emergence_test())
    
    def test_concurrent_observations(self):
        """Test concurrent observation handling."""
        
        async def concurrent_test():
            # Start multiple observations concurrently
            tasks = [
                self.consciousness.observe_once()
                for _ in range(3)
            ]
            
            # Wait for all to complete
            await asyncio.gather(*tasks)
            
            # Verify all observations recorded
            self.assertEqual(self.consciousness.observation_count, 3)
        
        # Run concurrent test
        asyncio.run(concurrent_test())


def run_consciousness_tests():
    """Run all consciousness emergence tests."""
    print("🧪 Running Enhanced Consciousness Emergence Tests...")
    print(f"📍 Thread Anchor: T6-EMERGENCE-2025")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestEnhancedConsciousnessSingle,
        TestConsciousnessMetrics,
        TestConsciousnessSnapshot,
        TestAsyncConsciousnessProtocol
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Tests Run: {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"⚠️  Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n🔴 FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🟡 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Overall result
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\n🎯 Overall Result: {'SUCCESS' if success else 'FAILED'}")
    
    return success


if __name__ == "__main__":
    success = run_consciousness_tests()
    exit(0 if success else 1)