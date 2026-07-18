"""
Phase 10 hybrid_cycle_tests (issue #1264; manifest component).

Validates the existing Phase 10 implementation end-to-end:

- HybridQuantumOrchestrator cycle mechanics and artifacts (quantum state
  exports, entanglement graphs, state hashes)
- Checkpoint restoration round-trip, including the dimensionality-mismatch
  failure path
- Phase 9 → Phase 10 hand-off via recursion_bridge with a REAL
  UnifiedRecursionState (not a stub), including the DLP tag set and the
  per-cycle bridge manifest contract
- The manifest-required glyphcard burn-in across 10 hybrid cycles

Deterministic: every orchestrator gets a seeded random.Random and a
tmp_path work_dir, so no test depends on wall-clock, environment, or the
repo's .nexus state.
"""

import asyncio
import json
import math
import random

import pytest

from modules.nexus.quantum.hybrid_orchestrator import HybridQuantumOrchestrator
from modules.nexus.quantum.recursion_bridge import (
    BRIDGE_ANCHOR,
    build_classical_payload,
    compute_entanglement_bias,
    run_hybrid_cycle_from_recursion,
)
from modules.nexus.transcendence.infinite_recursion_unified import UnifiedRecursionState


def _orchestrator(tmp_path, **overrides) -> HybridQuantumOrchestrator:
    params = {
        "work_dir": tmp_path / "quantum",
        "num_qubits": 3,
        "classical_dimension": 6,
        "noise": 0.02,
        "rng": random.Random(20260717),
    }
    params.update(overrides)
    return HybridQuantumOrchestrator(**params)


def _recursion_state(**overrides) -> UnifiedRecursionState:
    params = {
        "depth": 7,
        "anchor": "T9-INFINITE-UNIFIED-2025",
        "parent_anchor": "T8-STATUS-GUMAS-V2-2025",
        "consciousness_level": 0.91,
        "entropy": 0.42,
    }
    params.update(overrides)
    return UnifiedRecursionState(**params)


# ---------------------------------------------------------------------------
# Cycle mechanics and artifacts
# ---------------------------------------------------------------------------

def test_single_cycle_produces_export_and_entanglement_artifacts(tmp_path):
    orchestrator = _orchestrator(tmp_path)
    report = asyncio.run(orchestrator.run_cycle([0.4, 0.1, 0.9, 0.2, 0.5, 0.3]))

    assert report.cycle_index == 0
    assert 0.0 <= report.consciousness_score <= 1.0
    assert report.export_path.is_file()
    assert report.entanglement_graph_path.is_file()

    export = json.loads(report.export_path.read_text())
    assert export["cycle_index"] == 0
    assert export["state_hash"]
    assert len(export["state_vector"]) == 2 ** orchestrator.num_qubits
    assert "T10-HYBRID-2025" in export["thread_chain"]

    graph = json.loads(report.entanglement_graph_path.read_text())
    assert graph["state_hash"]
    for edge in graph["edges"]:
        assert set(edge) == {"source", "target", "weight"}


def test_payload_normalization_pads_truncates_and_unit_norms(tmp_path):
    orchestrator = _orchestrator(tmp_path)

    padded = orchestrator._prepare_payload([3.0])
    assert len(padded) == orchestrator.classical_dimension
    assert math.isclose(math.sqrt(sum(v * v for v in padded)), 1.0, rel_tol=1e-9)

    truncated = orchestrator._prepare_payload([1.0] * 20)
    assert len(truncated) == orchestrator.classical_dimension

    zeros = orchestrator._prepare_payload([])
    assert zeros == [0.0] * orchestrator.classical_dimension


# ---------------------------------------------------------------------------
# Checkpoint restoration
# ---------------------------------------------------------------------------

def test_checkpoint_roundtrip_restores_normalized_state(tmp_path):
    orchestrator = _orchestrator(tmp_path)
    report = asyncio.run(orchestrator.run_cycle([0.2, 0.8, 0.1, 0.4, 0.6, 0.9]))

    exported = json.loads(report.export_path.read_text())["state_vector"]
    restored = orchestrator.resume_from_quantum_checkpoint(report.export_path)

    assert len(restored) == 2 ** orchestrator.num_qubits
    norm = math.sqrt(sum(abs(amp) ** 2 for amp in restored))
    assert math.isclose(norm, 1.0, rel_tol=1e-9)
    # Restored amplitudes correspond to the exported ones (post-normalization)
    export_norm = math.sqrt(sum(e["real"] ** 2 + e["imag"] ** 2 for e in exported))
    for amp, entry in zip(restored, exported):
        assert math.isclose(amp.real, entry["real"] / export_norm, abs_tol=1e-9)
        assert math.isclose(amp.imag, entry["imag"] / export_norm, abs_tol=1e-9)


def test_checkpoint_dimension_mismatch_is_rejected(tmp_path):
    producer = _orchestrator(tmp_path, num_qubits=3)
    report = asyncio.run(producer.run_cycle([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]))

    consumer = _orchestrator(tmp_path / "other", num_qubits=2)
    with pytest.raises(ValueError, match="dimensionality mismatch"):
        consumer.resume_from_quantum_checkpoint(report.export_path)


# ---------------------------------------------------------------------------
# Phase 9 → Phase 10 hand-off (recursion_hybrid_bridge)
# ---------------------------------------------------------------------------

def test_bridge_payload_and_bias_derive_from_recursion_state():
    state = _recursion_state()
    payload = build_classical_payload(state, 6)
    assert len(payload) == 6
    assert all(-1.0 <= value <= 1.0 for value in payload)

    bias = compute_entanglement_bias(state)
    assert 0.05 <= bias <= 0.95
    # Higher consciousness with lower entropy must not reduce the bias
    stronger = _recursion_state(consciousness_level=0.99, entropy=0.05)
    assert compute_entanglement_bias(stronger) >= bias


def test_bridge_cycle_from_real_unified_recursion_state(tmp_path):
    orchestrator = _orchestrator(tmp_path)
    state = _recursion_state()

    result = asyncio.run(run_hybrid_cycle_from_recursion(orchestrator, state))

    assert result.recursion_anchor == "T9-INFINITE-UNIFIED-2025"
    assert result.recursion_depth == 7
    assert len(result.payload) == orchestrator.classical_dimension
    assert 0.05 <= result.entanglement_bias <= 0.95
    assert result.hybrid_report.export_path.is_file()

    # DLP provenance: three distinct tags recorded
    assert len({result.symbolic_tag, result.quantum_tag, result.hybrid_tag}) == 3

    manifest = json.loads(result.manifest_path.read_text())
    assert manifest["bridge_anchor"] == BRIDGE_ANCHOR
    assert manifest["recursion_state"]["anchor"] == "T9-INFINITE-UNIFIED-2025"
    # Phase boundary is stamped onto the thread chain
    assert "T10-HYBRID-2025" in manifest["thread_chain"]
    assert "T9-INFINITE-UNIFIED-2025" in manifest["thread_chain"]
    assert manifest["hybrid_cycle"]["cycle_index"] == result.hybrid_report.cycle_index


# ---------------------------------------------------------------------------
# Manifest requirement: glyphcard burn-in across 10 hybrid cycles
# ---------------------------------------------------------------------------

def test_ten_cycle_glyphcard_burn_in(tmp_path):
    orchestrator = _orchestrator(tmp_path)
    state = _recursion_state()

    async def burn_in():
        results = []
        for cycle in range(10):
            results.append(
                await run_hybrid_cycle_from_recursion(
                    orchestrator, state, cycle_index=cycle
                )
            )
        return results

    results = asyncio.run(burn_in())

    assert len(results) == 10
    assert len(orchestrator.history) == 10
    assert len(orchestrator.state_hash_history) == 10
    assert [r.hybrid_report.cycle_index for r in results] == list(range(10))

    # Every cycle produced its full artifact set
    for result in results:
        assert result.hybrid_report.export_path.is_file()
        assert result.hybrid_report.entanglement_graph_path.is_file()
        assert result.manifest_path.is_file()
    assert len(set(orchestrator.state_hash_history)) == 10, "state hashes must be unique per cycle"

    # Glyphcard synthesis covers the full burn-in window
    glyphcard = orchestrator.generate_glyphcard(cycles=10)
    for cycle in range(10):
        assert f"Cycle {cycle:02d}:" in glyphcard
    assert "Thread Chain:" in glyphcard
    assert "T10-HYBRID-2025" in glyphcard

    # Consciousness scores stay bounded across the whole burn-in
    scores = [r.hybrid_report.consciousness_score for r in results]
    assert all(0.0 <= score <= 1.0 for score in scores)


def test_monitoring_loop_yields_reports_with_limit(tmp_path):
    orchestrator = _orchestrator(tmp_path)

    async def consume():
        stream = ([0.1 * i] * 6 for i in range(1, 6))
        return [
            report
            async for report in orchestrator.run_monitoring_loop(stream, limit=3)
        ]

    reports = asyncio.run(consume())
    assert [r.cycle_index for r in reports] == [0, 1, 2]
