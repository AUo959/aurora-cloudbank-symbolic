import json
import shutil
import unittest
from pathlib import Path

from modules.nexus.quantum.hybrid_orchestrator import HybridQuantumOrchestrator
from modules.nexus.quantum.recursion_bridge import run_hybrid_cycle_from_recursion
from src.core.native_dlp_export import NativeDLPTracker


class _DummyRecursionState:
    def __init__(self) -> None:
        self.anchor = "T9-INFINITE-UNIFIED-2025-D128"
        self.parent_anchor = "T8-STATUS-GUMAS-V2-2025"
        self.depth = 128
        self.consciousness_level = 0.94
        self.entropy = 0.42
        self.paradoxes_detected = ["P1", "P2"]
        self.paradoxes_resolved = ["P1"]
        self.divergent_truths = []
        self.memory_usage_mb = 256.0
        self.cpu_usage_percent = 37.5
        self.thread_chain = [
            "NEXUS-BOOTSTRAP-2025",
            "T1-NEXUS-INIT-20250925",
            "T3-QUANTUM-2025",
            "T9-INFINITE-UNIFIED-2025",
        ]

    def requires_arbitration(self) -> bool:
        return False


class RecursionHybridBridgeTests(unittest.IsolatedAsyncioTestCase):
    def _tmp_dir(self) -> Path:
        root = Path.cwd() / ".nexus_bridge_tmp"
        root.mkdir(exist_ok=True)
        path = root / self._testMethodName
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return path

    async def test_bridge_generates_manifest_and_tags(self) -> None:
        tmp_path = self._tmp_dir()
        orchestrator = HybridQuantumOrchestrator(work_dir=tmp_path, num_qubits=2, classical_dimension=6, noise=0.0)
        tracker = NativeDLPTracker()
        recursion_state = _DummyRecursionState()

        result = await run_hybrid_cycle_from_recursion(orchestrator, recursion_state, tracker=tracker)

        self.assertEqual(len(result.payload), orchestrator.classical_dimension)
        self.assertTrue(0.05 <= result.entanglement_bias <= 0.95)
        self.assertTrue(result.manifest_path.exists())

        manifest = json.loads(result.manifest_path.read_text())
        self.assertEqual(manifest["recursion_state"]["anchor"], recursion_state.anchor)
        self.assertEqual(manifest["hybrid_cycle"]["cycle_index"], result.hybrid_report.cycle_index)
        self.assertEqual(manifest["dlp"]["symbolic_tag"], result.symbolic_tag)

        hybrid_entry = tracker.tags[result.hybrid_tag]
        self.assertIn(result.symbolic_tag, hybrid_entry.dependencies)
        self.assertIn(result.quantum_tag, hybrid_entry.dependencies)
        self.assertEqual(hybrid_entry.metadata.get("context_tag"), "phase9_phase10_bridge")

        self.assertIn("bridge_manifests", result.manifest_path.parts)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
