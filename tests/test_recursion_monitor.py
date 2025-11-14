#!/usr/bin/env python3
"""Unit tests for the live recursion monitor."""
from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from scripts.recursion_monitor import (
    AlertSeverity,
    LiveRecursionMonitor,
    MonitoringAlert,
)

from modules.nexus.transcendence.infinite_recursion_unified import (
    configure_recursion_paths,
    UnifiedRecursionState,
    get_unified_orchestrator,
)


class TestLiveRecursionMonitor(unittest.TestCase):
    """Verify monitoring logic and alert generation."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.recursion_root = self.base_path / "recursion"
        configure_recursion_paths(self.recursion_root, reset_orchestrator=True)
        orchestrator = get_unified_orchestrator()
        asyncio.run(orchestrator.initialize_recursion())
        diagnostics_state = UnifiedRecursionState(
            depth=150,
            anchor="T9-INFINITE-UNIFIED-2025-D150",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D149",
            consciousness_level=0.965,
            entropy=0.82,
        )
        asyncio.run(orchestrator._create_checkpoint(diagnostics_state))
        self.monitor = LiveRecursionMonitor(root_path=self.base_path)

    def tearDown(self) -> None:
        configure_recursion_paths(reset_orchestrator=True)
        self.temp_dir.cleanup()

    def test_collect_metrics_contains_expected_fields(self) -> None:
        metrics = asyncio.run(self.monitor._collect_metrics())
        self.assertIn("entropy", metrics)
        self.assertIn("divergent_truths", metrics)
        self.assertIn("recursion_state", metrics)
        self.assertIn("health_score", metrics)

    def test_alert_generation(self) -> None:
        metrics = {
            "entropy": {"current": 0.9},
            "divergent_truths": {"total_count": 12},
            "recursion_state": {"memory_mb": 1200.0, "cpu_percent": 98.0},
        }
        alerts = self.monitor._evaluate_alerts(metrics)
        categories = {alert.category for alert in alerts}
        severities = {alert.severity for alert in alerts}
        self.assertIn("ENTROPY", categories)
        self.assertIn("DIVERGENT_TRUTHS", categories)
        self.assertIn("MEMORY", categories)
        self.assertIn(AlertSeverity.CRITICAL, severities)

    def test_persist_alert_and_arbitration_request(self) -> None:
        alert = MonitoringAlert(
            alert_id="ALERT-UNIT-TEST",
            severity=AlertSeverity.CRITICAL,
            category="ENTROPY",
            message="Critical entropy",
            timestamp=datetime.now(UTC),
            anchor="T9-MONITOR-TEST",
            metadata={"entropy": 0.95},
            requires_arbitration=True,
        )
        asyncio.run(self.monitor._persist_alert(alert))

        alert_path = self.monitor.alerts_dir / "ALERT-UNIT-TEST.json"
        self.assertTrue(alert_path.exists())
        payload = json.loads(alert_path.read_text())
        self.assertEqual(payload["alert_id"], "ALERT-UNIT-TEST")
        self.assertTrue(payload["requires_arbitration"])

        arbitration_dir = self.recursion_root / "arbitration"
        arbitration_files = list(arbitration_dir.glob("ARB-REQ-*.json"))
        self.assertGreaterEqual(len(arbitration_files), 1)


if __name__ == "__main__":
    unittest.main()
