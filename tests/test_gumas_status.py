#!/usr/bin/env python3
"""
Test Suite for GUMAS/Orion Status Module
Anchor: T8-TEST-STATUS-2025
"""

import unittest
import asyncio
from datetime import datetime, UTC
from pathlib import Path

from modules.nexus.gumas.gumas_orion_status_enhanced import (
    GUMASOrionStatusModule,
    EntropyState,
    StatusSnapshot,
    SYMBOLIC_ANCHORS,
    THREAD_CHAIN
)

class TestGUMASStatus(unittest.TestCase):
    """Test suite for GUMAS status module"""
    
    def setUp(self):
        """Initialize test environment"""
        self.status = GUMASOrionStatusModule()
    
    def test_symbolic_anchoring(self):
        """Test proper anchor initialization"""
        self.assertEqual(self.status.anchor, "T8-STATUS-GUMAS-2025")
        self.assertEqual(self.status.seed, "EOS_SEED_ORION")
        self.assertEqual(len(self.status.thread_chain), 10)
    
    def test_entropy_drift_detection(self):
        """Test entropy drift calculation"""
        self.status.entropy_state.current = 0.65
        drift = self.status.entropy_state.calculate_drift()
        
        self.assertAlmostEqual(drift, 0.15, places=2)  # |0.65 - 0.5|
        self.assertEqual(self.status.entropy_state.trend, "STABLE")
    
    def test_thread_continuity(self):
        """Test thread continuity verification"""
        verification = self.status.verify_thread_continuity()
        
        self.assertTrue(verification["continuity_intact"])
        self.assertEqual(len(verification["anchors_verified"]), 10)
    
    def test_snapshot_creation(self):
        """Test snapshot creation and sealing"""
        snapshot = StatusSnapshot(
            snapshot_id="TEST-SNAP",
            timestamp=datetime.now(UTC),
            anchor_chain=THREAD_CHAIN,
            system_metrics={},
            entropy_state=EntropyState(),
            agent_states={},
            station_status={},
            simulation_layers={},
            consciousness_level=0.92
        )
        
        self.assertIsNotNone(snapshot.seal)
        self.assertTrue(snapshot.verify_integrity())
    
    def test_status_generation(self):
        """Test comprehensive status generation"""
        status = asyncio.run(self.status.get_comprehensive_status())
        
        self.assertIn("manifest_version", status)
        self.assertIn("seal", status)
        self.assertEqual(status["manifest_version"], "8.1.0")
    
    def test_glyphcard_generation(self):
        """Test visual glyphcard generation"""
        glyphcard = self.status.generate_status_glyphcard()
        
        self.assertIn("GUMAS/ORION STATUS", glyphcard)
        self.assertIn(self.status.anchor, glyphcard)

if __name__ == "__main__":
    print(f"Testing anchor: {SYMBOLIC_ANCHORS['primary']}")
    unittest.main(verbosity=2)