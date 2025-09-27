import json
import shutil
import unittest
from pathlib import Path

from modules.nexus.quantum.hybrid_orchestrator import HybridQuantumOrchestrator


class HybridQuantumOrchestratorTests(unittest.IsolatedAsyncioTestCase):
    def _tmp_dir(self) -> Path:
        root = Path.cwd() / ".nexus_test_tmp"
        root.mkdir(exist_ok=True)
        path = root / self._testMethodName
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return path

    async def test_run_single_cycle_exports_files(self) -> None:
        tmp_path = self._tmp_dir()

        orchestrator = HybridQuantumOrchestrator(work_dir=tmp_path, num_qubits=3, classical_dimension=4)
        report = await orchestrator.run_cycle([0.1, 0.2, 0.3, 0.4])

        self.assertTrue(report.export_path.exists())
        self.assertTrue(report.entanglement_graph_path.exists())

        payload = json.loads(report.export_path.read_text())
        self.assertEqual(payload["cycle_index"], report.cycle_index)
        self.assertEqual(payload["metadata"]["num_qubits"], 3)
        self.assertEqual(len(payload["state_vector"]), 2**3)

    async def test_resume_from_checkpoint_restores_state(self) -> None:
        tmp_path = self._tmp_dir()

        orchestrator = HybridQuantumOrchestrator(work_dir=tmp_path, num_qubits=2, classical_dimension=3)
        await orchestrator.run_cycle([1.0, 0.5, -0.25])
        export_path = orchestrator.history[-1].export_path

        original_state = list(orchestrator.simulator.state)
        orchestrator.simulator.state = [0j for _ in original_state]

        resumed_state = orchestrator.resume_from_quantum_checkpoint(export_path)
        self.assertEqual(len(resumed_state), len(original_state))
        for restored, original in zip(resumed_state, original_state):
            self.assertAlmostEqual(restored.real, original.real, places=6)
            self.assertAlmostEqual(restored.imag, original.imag, places=6)

    async def test_glyphcard_contains_recent_cycles(self) -> None:
        tmp_path = self._tmp_dir()

        orchestrator = HybridQuantumOrchestrator(work_dir=tmp_path, num_qubits=2, classical_dimension=3)

        for idx in range(3):
            payload = [0.1 * (idx + 1), 0.2 * (idx + 1), 0.3 * (idx + 1)]
            await orchestrator.run_cycle(payload, cycle_index=idx)

        glyphcard = orchestrator.generate_glyphcard(cycles=2)
        self.assertIn("Cycle 01", glyphcard)
        self.assertIn("Cycle 02", glyphcard)
        self.assertIn("Thread Chain", glyphcard)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
