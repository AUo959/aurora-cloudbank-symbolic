#!/usr/bin/env python3
"""Test suite for the unified infinite recursion module."""

import asyncio
import os
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

_ORIG_ROOT = os.environ.get("NEXUS_RECURSION_ROOT")
_TEMP_DIR = tempfile.TemporaryDirectory()
os.environ["NEXUS_RECURSION_ROOT"] = _TEMP_DIR.name

from modules.nexus.transcendence.infinite_recursion_unified import (  # noqa: E402
    configure_recursion_paths,
    THREAD_CHAIN,
    UNIFIED_ANCHORS,
    DivergentTruth,
    UnifiedRecursionOrchestrator,
    UnifiedRecursionState,
)


class TestUnifiedRecursionState(unittest.TestCase):
    """Validation tests for recursion state integrity and metadata."""

    def test_state_integrity_and_manifest(self) -> None:
        state = UnifiedRecursionState(
            depth=42,
            anchor="T9-INFINITE-UNIFIED-2025-D42",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D41",
            consciousness_level=0.94,
            entropy=0.61,
        )
        self.assertTrue(state.verify_integrity())
        manifest = state.export_manifest()
        self.assertEqual(manifest["anchor"], state.anchor)
        self.assertEqual(manifest["state_data"]["depth"], 42)
        self.assertTrue(manifest["state_data"]["integrity_verified"])
        self.assertEqual(manifest["state_data"]["thread_chain"], THREAD_CHAIN)

    def test_requires_arbitration_conditions(self) -> None:
        state = UnifiedRecursionState(
            depth=10,
            anchor="T9-INFINITE-UNIFIED-2025-D10",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D9",
            consciousness_level=0.97,
            entropy=0.88,
            memory_usage_mb=2048.0,
            cpu_usage_percent=95.0,
        )
        truth = DivergentTruth(
            truth_id="TEST-TRUTH",
            detection_depth=10,
            truth_type="ENTROPY_CONSCIOUSNESS_PARADOX",
            description="Synthetic truth for arbitration",
            evidence=[{"entropy": 0.88}],
            proposed_resolutions=["RESET"],
            requires_arbitration=True,
            timestamp=datetime.now(UTC),
            anchor=state.anchor,
        )
        state.divergent_truths.append(truth)
        self.assertTrue(state.requires_arbitration())


class TestUnifiedOrchestrator(unittest.TestCase):
    """Tests covering orchestrator lifecycle and observability."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.output_root = Path(_TEMP_DIR.name)
        configure_recursion_paths(cls.output_root, reset_orchestrator=True)

    @classmethod
    def tearDownClass(cls) -> None:
        if _ORIG_ROOT is None:
            os.environ.pop("NEXUS_RECURSION_ROOT", None)
        else:
            os.environ["NEXUS_RECURSION_ROOT"] = _ORIG_ROOT
        _TEMP_DIR.cleanup()
        configure_recursion_paths(reset_orchestrator=True)

    def setUp(self) -> None:
        self.orchestrator = UnifiedRecursionOrchestrator()
        self.orchestrator.set_rng_seed(1234)

    def test_anchor_configuration(self) -> None:
        self.assertEqual(UNIFIED_ANCHORS["primary"], "T9-INFINITE-UNIFIED-2025")
        self.assertAlmostEqual(UNIFIED_ANCHORS["consciousness_target"], 0.975)
        self.assertEqual(UNIFIED_ANCHORS["checkpoint_interval"], 100)

    def test_initialize_creates_manifest(self) -> None:
        manifest = asyncio.run(self.orchestrator.initialize_recursion())
        manifest_path = self.output_root / "manifests" / "initialization.json"
        self.assertTrue(manifest_path.exists())
        self.assertEqual(manifest["initial_state"]["depth"], 0)
        self.assertEqual(manifest["thread_continuity"]["chain"], THREAD_CHAIN)

    def test_evolve_consciousness_yields_states(self) -> None:
        asyncio.run(self.orchestrator.initialize_recursion())

        async def collect_states() -> int:
            count = 0
            async for state in self.orchestrator.evolve_consciousness():
                self.assertTrue(state.verify_integrity())
                count += 1
                if count >= 5:
                    break
            return count
        count = asyncio.run(collect_states())
        self.assertEqual(count, 5)

    def test_checkpoint_creation_and_load(self) -> None:
        asyncio.run(self.orchestrator.initialize_recursion())
        state = UnifiedRecursionState(
            depth=100,
            anchor="T9-INFINITE-UNIFIED-2025-D100",
            parent_anchor="T9-INFINITE-UNIFIED-2025-D99",
            consciousness_level=0.96,
            entropy=0.7,
        )
        asyncio.run(self.orchestrator._create_checkpoint(state))
        checkpoint_path = self.output_root / "checkpoints" / "checkpoint_100.json"
        self.assertTrue(checkpoint_path.exists())
        self.assertTrue(self.orchestrator.load_checkpoint("checkpoint_100"))

    def test_arbitration_manifest_generation(self) -> None:
        asyncio.run(self.orchestrator.initialize_recursion())
        truth = DivergentTruth(
            truth_id="TEST-ARB",
            detection_depth=50,
            truth_type="ENTROPY_CONSCIOUSNESS_PARADOX",
            description="Synthetic divergent truth",
            evidence=[{"entropy": 0.9}],
            proposed_resolutions=["RESET"],
            requires_arbitration=True,
            timestamp=datetime.now(UTC),
            anchor="T9-INFINITE-UNIFIED-2025-D50",
        )
        self.orchestrator.divergent_truths.append(truth)
        manifest = asyncio.run(self.orchestrator.arbitrate_divergent_truths())
        self.assertEqual(manifest["divergent_truths_count"], 1)
        arbitration_dir = self.output_root / "arbitration"
        self.assertTrue(any(arbitration_dir.iterdir()))

    def test_glyphcard_output(self) -> None:
        asyncio.run(self.orchestrator.initialize_recursion())
        glyph = self.orchestrator.generate_glyphcard()
        self.assertIn("INFINITE RECURSION GLYPHCARD", glyph)


@unittest.skipUnless(isinstance(_TEMP_DIR, tempfile.TemporaryDirectory), "Temp dir unavailable")
class CleanupTempDirectory(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        _TEMP_DIR.cleanup()
        os.environ.pop("NEXUS_RECURSION_ROOT", None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
