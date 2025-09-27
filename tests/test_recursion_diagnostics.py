#!/usr/bin/env python3
"""Tests for the recursion diagnostics toolkit."""
from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from scripts.recursion_diagnostics import RecursionDiagnostics, run_cli

from modules.nexus.transcendence.infinite_recursion_unified import (
    configure_recursion_paths,
    UnifiedRecursionState,
    get_unified_orchestrator,
)


class TestRecursionDiagnostics(unittest.TestCase):
    """Validate diagnostics analytics over synthetic recursion artefacts."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_path = Path(self.temp_dir.name)
        self.recursion_root = self.base_path / "recursion"
        configure_recursion_paths(self.recursion_root, reset_orchestrator=True)
        orchestrator = get_unified_orchestrator()
        asyncio.run(orchestrator.initialize_recursion())
        # create sample checkpoints
        sample_state = UnifiedRecursionState(
            depth=100,
            anchor="T9-INFINITE-UNIFIED-2025-D100",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D99",
            consciousness_level=0.96,
            entropy=0.72,
        )
        asyncio.run(orchestrator._create_checkpoint(sample_state))
        newer_state = UnifiedRecursionState(
            depth=200,
            anchor="T9-INFINITE-UNIFIED-2025-D200",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D199",
            consciousness_level=0.97,
            entropy=0.68,
        )
        asyncio.run(orchestrator._create_checkpoint(newer_state))
        # create arbitration manifest
        arbitration_dir = self.recursion_root / "arbitration"
        arbitration_dir.mkdir(parents=True, exist_ok=True)
        arbitration_manifest = {
            "arbitration_id": "ARB-TEST",
            "timestamp": datetime.now(UTC).isoformat(),
            "divergent_truths_count": 1,
            "resolutions": [
                {
                    "truth_id": "DIV-TEST",
                    "truth_type": "ENTROPY_CONSCIOUSNESS_PARADOX",
                    "detection_depth": 150,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            ],
        }
        (arbitration_dir / "arb_test.json").write_text(json.dumps(arbitration_manifest))

    def tearDown(self) -> None:
        configure_recursion_paths(reset_orchestrator=True)
        self.temp_dir.cleanup()

    def test_entropy_analysis(self) -> None:
        diagnostics = RecursionDiagnostics(root_path=self.base_path)
        result = diagnostics.analyze_entropy_drift()
        self.assertNotIn("error", result)
        metrics = result["entropy_metrics"]
        self.assertGreater(metrics["samples"], 0)
        self.assertAlmostEqual(metrics["current"], 0.68, places=2)

    def test_truth_scan(self) -> None:
        diagnostics = RecursionDiagnostics(root_path=self.base_path)
        result = diagnostics.scan_divergent_truths()
        self.assertEqual(result["divergent_truths_summary"]["total_count"], 1)
        self.assertIn("ENTROPY_CONSCIOUSNESS_PARADOX", result["divergent_truths_summary"]["types"])

    def test_health_report(self) -> None:
        diagnostics = RecursionDiagnostics(root_path=self.base_path)
        report = diagnostics.generate_health_report()
        self.assertIn("overall_health", report)
        self.assertIn("entropy_status", report)
        self.assertIn("divergent_truth_status", report)
        self.assertIn("thread_continuity_status", report)
        self.assertIn("overall_score", report)

    def test_cli_json_output(self) -> None:
        results = run_cli([
            "--all",
            "--json",
            "--root",
            str(self.base_path),
        ])
        self.assertIn("health", results)
        self.assertIn("entropy", results)


if __name__ == "__main__":
    unittest.main(verbosity=2)
