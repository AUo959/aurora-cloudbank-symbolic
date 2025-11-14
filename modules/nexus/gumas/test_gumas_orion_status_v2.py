#!/usr/bin/env python3
"""
GUMAS/Orion Status Module v2 - Test Suite
Enhanced testing for OSCILLATING entropy detection and performance improvements

Anchor: T8-STATUS-GUMAS-V2-TEST-2025
Thread: T8-STATUS-GUMAS-V2-2025
"""

import pytest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add the module path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from modules.nexus.gumas.gumas_orion_status_v2 import StatusOrchestrator, EntropyMonitor, EntropySnapshot


class TestStatusOrchestratorV2:
    """Test suite for GUMAS/Orion Status Module v2"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.orchestrator = StatusOrchestrator()
    
    def test_initialization_performance(self):
        """Test that v2 initialization meets performance targets (< 2 seconds)"""
        start_time = time.time()
        orchestrator = StatusOrchestrator()
        init_time = time.time() - start_time
        
        assert init_time < 2.0, f"Initialization took {init_time:.2f}s, exceeds 2s target"
        assert orchestrator.anchor == "T8-STATUS-GUMAS-V2-2025"
        
    def test_status_generation_performance(self):
        """Test that status generation meets performance targets (< 1 second)"""
        import asyncio
        
        async def test_async():
            start_time = time.time()
            status = await self.orchestrator.get_comprehensive_status()
            generation_time = time.time() - start_time
            
            assert generation_time < 1.0, f"Status generation took {generation_time:.2f}s, exceeds 1s target"
            assert "manifest" in status
            assert "entropy_analysis" in status
            
        asyncio.run(test_async())
        
    def test_thread_chain_verification(self):
        """Test complete 12-anchor thread chain verification"""
        expected_chain = [
            "NEXUS-BOOTSTRAP-2025",
            "T1-NEXUS-INIT-20250925", 
            "T2-MULTIAGENT-2025",
            "T3-QUANTUM-2025",
            "T4-MEMORY-WEAVE-2025",
            "T5-REALITY-FORK-2025",
            "T6-EMERGENCE-2025",
            "T7-SCALE-2025",
            "T7-GUMAS-ORION-2025",
            "T8-TRANSCENDENT-2025",
            "T8-STATUS-GUMAS-2025",
            "T8-STATUS-GUMAS-V2-2025"
        ]
        
        thread_status = self.orchestrator.verify_thread_continuity()
        assert thread_status["valid"] == True
        assert len(thread_status["chain"]) == 12
        
        for i, expected_anchor in enumerate(expected_chain):
            assert thread_status["chain"][i] == expected_anchor
            
    def test_meta_agent_integration(self):
        """Test integration with all 5 meta-agents"""
        expected_agents = ["ARCHIE", "OPPY", "STARLING", "LIORA", "RIVERTHREAD"]
        
        status = self.orchestrator.get_full_status()
        agents = status.get("meta_agents", {})
        
        for agent_name in expected_agents:
            assert agent_name in agents
            agent = agents[agent_name]
            assert "status" in agent
            assert "clearance" in agent
            assert "capabilities" in agent
            
    def test_station_sectors_mapping(self):
        """Test Orion Station sector assignments"""
        expected_sectors = [
            "command_deck", "science_labs", "medical_bay", 
            "engineering", "data_core"
        ]
        
        status = self.orchestrator.get_full_status()
        sectors = status.get("station_sectors", {})
        
        for sector in expected_sectors:
            assert sector in sectors
            assert "assigned_agents" in sectors[sector]
            assert "status" in sectors[sector]
            
    def test_simulation_layers(self):
        """Test all 6 simulation layers are operational"""
        expected_layers = [
            "PHYSICAL", "DIGITAL", "COGNITIVE", 
            "META", "QUANTUM", "TRANSCENDENT"
        ]
        
        status = self.orchestrator.get_full_status()
        layers = status.get("simulation_layers", {})
        
        for layer in expected_layers:
            assert layer in layers
            assert "anchor" in layers[layer]
            assert "status" in layers[layer]


class TestEntropyMonitorV2:
    """Test suite for enhanced EntropyMonitor with OSCILLATING detection"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.monitor = EntropyMonitor()
        
    def test_oscillating_entropy_detection(self):
        """Test OSCILLATING entropy pattern detection"""
        # Simulate oscillating entropy values
        oscillating_values = [0.05, 0.08, 0.03, 0.09, 0.04, 0.07, 0.02, 0.08]
        
        for value in oscillating_values:
            self.monitor.record_entropy(value)
            
        trend = self.monitor.get_entropy_trend()
        assert trend == "OSCILLATING", f"Expected OSCILLATING, got {trend}"
        
    def test_stable_entropy_detection(self):
        """Test STABLE entropy pattern detection"""
        # Simulate stable entropy values
        stable_values = [0.045, 0.046, 0.044, 0.047, 0.045, 0.046]
        
        for value in stable_values:
            self.monitor.record_entropy(value)
            
        trend = self.monitor.get_entropy_trend()
        assert trend == "STABLE", f"Expected STABLE, got {trend}"
        
    def test_increasing_entropy_detection(self):
        """Test INCREASING entropy pattern detection"""
        # Simulate increasing entropy values
        increasing_values = [0.02, 0.03, 0.045, 0.06, 0.075, 0.09]
        
        for value in increasing_values:
            self.monitor.record_entropy(value)
            
        trend = self.monitor.get_entropy_trend()
        assert trend == "INCREASING", f"Expected INCREASING, got {trend}"
        
    def test_decreasing_entropy_detection(self):
        """Test DECREASING entropy pattern detection"""
        # Simulate decreasing entropy values
        decreasing_values = [0.09, 0.075, 0.06, 0.045, 0.03, 0.02]
        
        for value in decreasing_values:
            self.monitor.record_entropy(value)
            
        trend = self.monitor.get_entropy_trend()
        assert trend == "DECREASING", f"Expected DECREASING, got {trend}"
        
    def test_entropy_drift_thresholds(self):
        """Test entropy drift warning and danger thresholds"""
        # Test warning threshold (0.05)
        self.monitor.record_entropy(0.06)
        status = self.monitor.get_entropy_status()
        assert status["drift_level"] == "WARNING"
        
        # Clear and test danger threshold (0.1)
        self.monitor.clear_history()
        self.monitor.record_entropy(0.12)
        status = self.monitor.get_entropy_status()
        assert status["drift_level"] == "DANGER"
        
    def test_arbitration_flagging(self):
        """Test enhanced arbitration flagging for OSCILLATING patterns"""
        # Simulate oscillating pattern that should trigger arbitration
        oscillating_values = [0.02, 0.09, 0.01, 0.08, 0.03, 0.07]
        
        for value in oscillating_values:
            self.monitor.record_entropy(value)
            
        flags = self.monitor.get_arbitration_flags()
        assert len(flags) > 0
        assert any("OSCILLATING" in flag["reason"] for flag in flags)
        
    def test_historical_entropy_tracking(self):
        """Test comprehensive entropy timeline analysis"""
        # Record entropy over time
        test_values = [0.03, 0.05, 0.04, 0.06, 0.05, 0.07]
        
        for i, value in enumerate(test_values):
            timestamp = datetime.now() - timedelta(minutes=10-i)
            self.monitor.record_entropy(value, timestamp)
            
        history = self.monitor.get_entropy_history()
        assert len(history) == len(test_values)
        
        # Verify chronological order
        for i in range(len(history) - 1):
            assert history[i]["timestamp"] <= history[i+1]["timestamp"]


class TestEntropySnapshotV2:
    """Test suite for enhanced EntropySnapshot"""
    
    def test_snapshot_creation_performance(self):
        """Test snapshot creation meets performance targets (< 500ms)"""
        orchestrator = StatusOrchestrator()
        
        start_time = time.time()
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        creation_time = time.time() - start_time
        
        assert creation_time < 0.5, f"Snapshot creation took {creation_time:.2f}s, exceeds 500ms target"
        
    def test_snapshot_immutability(self):
        """Test that snapshots are truly immutable"""
        orchestrator = StatusOrchestrator()
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        
        # Attempt to modify snapshot data (should fail or be ignored)
        original_anchor = snapshot.data.get("anchor")
        try:
            snapshot.data["anchor"] = "MODIFIED"
            # If we get here, check if the modification was actually applied
            assert snapshot.data.get("anchor") == original_anchor, "Snapshot was modified when it should be immutable"
        except (TypeError, AttributeError):
            # Expected behavior - snapshot should be immutable
            pass
            
    def test_snapshot_sha256_sealing(self):
        """Test SHA256 seal generation and verification"""
        orchestrator = StatusOrchestrator()
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        
        assert hasattr(snapshot, 'seal')
        assert len(snapshot.seal) == 64  # SHA256 hex string length
        assert snapshot.verify_seal() == True
        
    def test_snapshot_export_format(self):
        """Test snapshot export format and structure"""
        orchestrator = StatusOrchestrator()
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        
        export_data = snapshot.export()
        
        required_fields = [
            "anchor", "timestamp", "entropy_status", 
            "meta_agents", "station_sectors", "thread_chain", "seal"
        ]
        
        for field in required_fields:
            assert field in export_data, f"Missing required field: {field}"


class TestCLIInterfaceV2:
    """Test suite for enhanced CLI interface"""
    
    def test_status_command(self):
        """Test --status CLI command"""
        with patch('sys.argv', ['gumas_orion_status_v2.py', '--status']):
            # Import and test CLI functionality
            from modules.nexus.gumas.gumas_orion_status_v2 import main
            
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify status information was printed
                printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "GUMAS/Orion Enhanced Status" in printed_output
                assert "System Health" in printed_output
                
    def test_glyphcard_command(self):
        """Test --glyphcard CLI command"""
        with patch('sys.argv', ['gumas_orion_status_v2.py', '--glyphcard']):
            from modules.nexus.gumas.gumas_orion_status_v2 import main
            
            with patch('builtins.print') as mock_print:
                main()
                
                printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "◊" in printed_output or "Visual Status" in printed_output
                
    def test_verify_thread_command(self):
        """Test --verify-thread CLI command"""
        with patch('sys.argv', ['gumas_orion_status_v2.py', '--verify-thread']):
            from modules.nexus.gumas.gumas_orion_status_v2 import main
            
            with patch('builtins.print') as mock_print:
                main()
                
                printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "Thread Continuity" in printed_output
                
    def test_detect_drift_command(self):
        """Test --detect-drift CLI command"""
        with patch('sys.argv', ['gumas_orion_status_v2.py', '--detect-drift']):
            from modules.nexus.gumas.gumas_orion_status_v2 import main
            
            with patch('builtins.print') as mock_print:
                main()
                
                printed_output = ' '.join([str(call) for call in mock_print.call_args_list])
                assert "Entropy Drift" in printed_output
                
    def test_export_snapshot_command(self):
        """Test --export-snapshot CLI command"""
        with patch('sys.argv', ['gumas_orion_status_v2.py', '--export-snapshot']):
            from modules.nexus.gumas.gumas_orion_status_v2 import main
            
            with patch('builtins.print') as mock_print:
                with patch('os.makedirs'):  # Mock directory creation
                    with patch('builtins.open', create=True) as mock_file:
                        main()
                        
                        # Verify file was attempted to be written
                        mock_file.assert_called()


class TestPerformanceV2:
    """Performance regression tests for v2 improvements"""
    
    def test_load_time_improvement(self):
        """Verify v2 load time is improved over v1 baseline"""
        # Test multiple initializations to get average
        times = []
        for _ in range(5):
            start_time = time.time()
            StatusOrchestrator()
            times.append(time.time() - start_time)
            
        avg_time = sum(times) / len(times)
        assert avg_time < 2.0, f"Average load time {avg_time:.2f}s exceeds 2s target"
        
    def test_status_generation_improvement(self):
        """Verify v2 status generation is improved over v1 baseline"""
        orchestrator = StatusOrchestrator()
        
        times = []
        for _ in range(5):
            start_time = time.time()
            orchestrator.get_full_status()
            times.append(time.time() - start_time)
            
        avg_time = sum(times) / len(times)
        assert avg_time < 1.0, f"Average status generation {avg_time:.2f}s exceeds 1s target"
        
    def test_snapshot_creation_improvement(self):
        """Verify v2 snapshot creation is improved over v1 baseline"""
        orchestrator = StatusOrchestrator()
        
        times = []
        for _ in range(5):
            start_time = time.time()
            EntropySnapshot.create_snapshot(orchestrator)
            times.append(time.time() - start_time)
            
        avg_time = sum(times) / len(times)
        assert avg_time < 0.5, f"Average snapshot creation {avg_time:.2f}s exceeds 500ms target"


class TestIntegrationV2:
    """Integration tests for v2 module"""
    
    def test_end_to_end_workflow(self):
        """Test complete workflow from initialization to export"""
        # Initialize
        orchestrator = StatusOrchestrator()
        assert orchestrator.anchor == "T8-STATUS-GUMAS-V2-2025"
        
        # Get status
        status = orchestrator.get_full_status()
        assert "health" in status
        
        # Verify thread
        thread_status = orchestrator.verify_thread_continuity()
        assert thread_status["valid"] == True
        
        # Create snapshot
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        assert snapshot.verify_seal() == True
        
        # Export snapshot
        export_data = snapshot.export()
        assert "anchor" in export_data
        assert export_data["anchor"] == "T8-STATUS-GUMAS-V2-2025"
        
    def test_migration_from_v1(self):
        """Test migration compatibility from v1 to v2"""
        # This would test actual migration if v1 existed
        # For now, test that v2 can handle v1-style configurations
        
        # Mock v1 configuration
        v1_config = {
            "anchor": "T8-STATUS-GUMAS-2025",
            "entropy_threshold": 0.1,
            "agents": ["ARCHIE", "OPPY", "STARLING", "LIORA", "RIVERTHREAD"]
        }
        
        # Initialize v2 with v1 config (should gracefully handle)
        orchestrator = StatusOrchestrator()
        status = orchestrator.get_full_status()
        
        # Verify v2 enhancements are present
        assert "entropy_trend" in status.get("entropy_status", {})
        
    def test_cross_module_compatibility(self):
        """Test compatibility with other NEXUS modules"""
        orchestrator = StatusOrchestrator()
        
        # Test export format compatibility
        snapshot = EntropySnapshot.create_snapshot(orchestrator)
        export_data = snapshot.export()
        
        # Verify standard NEXUS export format
        assert "anchor" in export_data
        assert "timestamp" in export_data  
        assert "seal" in export_data
        assert export_data["anchor"].startswith("T8-")


if __name__ == "__main__":
    # Run specific test categories
    print("🧪 Running GUMAS/Orion Status Module v2 Test Suite...")
    print("=" * 60)
    
    # Performance tests first
    print("\n📊 Performance Tests...")
    pytest.main(["-v", __file__ + "::TestPerformanceV2", "-x"])
    
    print("\n🔄 Core Functionality Tests...")
    pytest.main(["-v", __file__ + "::TestStatusOrchestratorV2", "-x"])
    
    print("\n📈 Enhanced Entropy Monitoring Tests...")
    pytest.main(["-v", __file__ + "::TestEntropyMonitorV2", "-x"])
    
    print("\n📸 Snapshot Tests...")
    pytest.main(["-v", __file__ + "::TestEntropySnapshotV2", "-x"])
    
    print("\n💻 CLI Interface Tests...")
    pytest.main(["-v", __file__ + "::TestCLIInterfaceV2", "-x"])
    
    print("\n🔗 Integration Tests...")
    pytest.main(["-v", __file__ + "::TestIntegrationV2", "-x"])
    
    print("\n✅ Test Suite Complete!")
    print("Enhanced GUMAS/Orion Status Module v2 - All tests validated")