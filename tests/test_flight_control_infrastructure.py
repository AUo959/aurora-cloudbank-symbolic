"""Integration tests for Flight Control Infrastructure modules.

Tests DLP manifest generation, maintenance orchestration, and enhanced docking sequences.
"""
import json
import subprocess
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.flightcontrol
class TestFlightControlInfrastructure:
    """Integration tests for flight control infrastructure."""
    
    @pytest.fixture(scope="class")
    def flight_control_path(self):
        """Path to flight_control module."""
        path = Path(__file__).parent.parent / "modules" / "flight_control"
        assert path.exists(), f"Flight control module not found at {path}"
        return path
    
    @pytest.fixture(scope="class")
    def demo_script(self, flight_control_path):
        """Path to infrastructure demo script."""
        demo = flight_control_path / "demo_infrastructure.js"
        assert demo.exists(), f"Demo script not found at {demo}"
        return demo
    
    def test_infrastructure_demo_execution(self, demo_script):
        """Test that infrastructure demo executes without errors."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        # Demo should complete successfully
        assert result.returncode == 0, f"Demo failed: {result.stderr}"
        
        # Check for key milestone messages
        output = result.stdout
        assert "Flight Control Infrastructure Demo" in output
        assert "DLP Manifest Generation" in output
        assert "Maintenance Orchestration" in output
        assert "Enhanced Docking Sequence" in output
        assert "Infrastructure demo complete" in output
    
    def test_dlp_manifest_generation(self, demo_script, tmp_path):
        """Test DLP manifest file generation and structure."""
        # Run demo (manifests saved to ./station_manifests)
        manifest_dir = tmp_path / "station_manifests"
        manifest_dir.mkdir()
        
        # Note: Demo creates manifests in default location, check there
        demo_manifest_dir = Path("./station_manifests")
        
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        # Check manifests were created (files named {timestamp}_{context}_MANIFEST-*.json)
        manifests = list(demo_manifest_dir.glob("*_MANIFEST-*.json"))
        assert len(manifests) >= 2, f"Expected at least 2 manifests (init + final), found {len(manifests)}"
        
        # Validate manifest structure
        with open(manifests[0], "r") as f:
            manifest = json.load(f)
        
        # Required fields
        assert "manifestId" in manifest
        assert "timestamp" in manifest
        assert "snapshot" in manifest  # Changed from stationState
        assert "stateHash" in manifest
        assert "contextTag" in manifest
        assert "chainNotation" in manifest
        assert "anchors" in manifest
        
        # Anchors structure
        anchors = manifest["anchors"]
        assert "t1State" in anchors
        assert "srbResolution" in anchors
        
        # Metadata
        assert "metadata" in manifest
        assert "craftCount" in manifest["metadata"]
        assert "dockCount" in manifest["metadata"]
        assert "trafficSlotCount" in manifest["metadata"]  # Changed from trafficSlots
        
        # Cleanup
        for m in manifests:
            m.unlink()
        demo_manifest_dir.rmdir()
    
    def test_maintenance_orchestration_workflow(self, demo_script):
        """Test maintenance task scheduling and completion flow."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        output = result.stdout
        
        # Verify maintenance workflow stages
        assert "Scheduled: POST_FLIGHT_INSPECT" in output
        assert "Task ID:" in output
        assert "Task started" in output
        assert "Task completed" in output
        
        # Verify maintenance summary
        assert "Maintenance Summary" in output
        assert "scheduled" in output or "completed" in output
    
    def test_docking_sequence_phases(self, demo_script):
        """Test enhanced docking sequence phase progression."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        output = result.stdout
        
        # Expected phases in order
        expected_phases = [
            "APPROACH",
            "CORRIDOR_ENTRY",
            "SAFETY_HOLD",
            "FINAL_APPROACH",
            "DOCKING",
            "LOCKED",
            "UMBILICAL",
            "COMPLETE",
        ]
        
        # Find phase progression in output
        phase_count = 0
        for phase in expected_phases:
            if f"Phase: {phase}" in output:
                phase_count += 1
        
        # Should see most phases (at least 5 of 8)
        assert phase_count >= 5, f"Only saw {phase_count}/8 docking phases"
        
        # Verify safety checks
        assert "Safety checks:" in output
        assert "Docking sequence complete" in output
    
    def test_system_integration(self, demo_script):
        """Test all systems working together in sequence."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        output = result.stdout
        
        # Verify complete flow
        flow_steps = [
            "Station initialized",
            "Manifest generated",
            "Scheduled: POST_FLIGHT_INSPECT",
            "Docking sequence initiated",
            "Docking sequence complete",
            "Final manifest",
            "System Summary",
        ]
        
        for step in flow_steps:
            assert step in output, f"Missing flow step: {step}"
        
        # Verify final state reporting
        assert "Station State:" in output
        assert "Docks:" in output
        assert "Craft:" in output
        assert "Fuel:" in output
    
    def test_dlp_manifest_validation(self, demo_script):
        """Test that manifests pass internal validation."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        output = result.stdout
        
        # Demo includes validation checks
        assert "Validation: ✅ VALID" in output
        assert "❌ INVALID" not in output
    
    def test_telemetry_bus_integration(self, demo_script):
        """Test EventEmitter telemetry bus emissions."""
        result = subprocess.run(
            ["node", str(demo_script)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0
        
        output = result.stdout
        
        # Check for telemetry events
        telemetry_events = [
            "docking:phase-advanced",
            "docking:safety-checks",
        ]
        
        event_count = 0
        for event in telemetry_events:
            # Events logged with emoji markers
            if "🚀 Phase:" in output or "🛡️  Safety checks:" in output:
                event_count += 1
        
        assert event_count >= 1, "No telemetry events observed"


@pytest.mark.unit
@pytest.mark.flightcontrol
class TestModuleExports:
    """Unit tests for module exports and structure."""
    
    def test_dlp_manifest_generator_exports(self):
        """Test DLPManifestGenerator module exports correctly."""
        result = subprocess.run(
            [
                "node",
                "-e",
                "import('./modules/flight_control/dlp_manifest_generator.js').then(m => "
                "console.log(m.DLPManifestGenerator ? 'OK' : 'FAIL'))",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OK" in result.stdout
    
    def test_maintenance_orchestrator_exports(self):
        """Test MaintenanceOrchestrator module exports correctly."""
        result = subprocess.run(
            [
                "node",
                "-e",
                "import('./modules/flight_control/maintenance_orchestrator.js').then(m => "
                "console.log(m.MaintenanceOrchestrator ? 'OK' : 'FAIL'))",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OK" in result.stdout
    
    def test_docking_sequence_manager_exports(self):
        """Test DockingSequenceManager module exports correctly."""
        result = subprocess.run(
            [
                "node",
                "-e",
                "import('./modules/flight_control/docking_sequence_manager.js').then(m => "
                "console.log(m.DockingSequenceManager ? 'OK' : 'FAIL'))",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        assert "OK" in result.stdout
