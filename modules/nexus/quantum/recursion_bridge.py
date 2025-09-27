#!/usr/bin/env python3
"""NEXUS Phase 9 → Phase 10 bridge utilities.

This module links the Phase 9 unified recursion stack with the Phase 10 hybrid
quantum-classical orchestrator. It transforms recursion state telemetry into
classical payload vectors, executes hybrid cycles, and records DLP provenance so
symbolic continuity remains intact across the phase boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, List, Optional, TYPE_CHECKING

from modules.nexus.quantum.hybrid_orchestrator import HybridQuantumOrchestrator, QuantumCycleReport
from src.core.native_dlp_export import NativeDLPTracker

if TYPE_CHECKING:  # pragma: no cover - optional dependency for type checkers
    from modules.nexus.transcendence.infinite_recursion_unified import UnifiedRecursionState


BRIDGE_CONTEXT_TAG = "phase9_phase10_bridge"
BRIDGE_ANCHOR = "T9-T10-BRIDGE-2025"
BRIDGE_DLP_LEVEL = "DLP_L1_OK"
_DEFAULT_PAYLOAD_DIMENSION = 8


@dataclass(slots=True)
class BridgeRunResult:
    """Container for a single bridge execution."""

    recursion_anchor: str
    recursion_depth: int
    payload: List[float]
    entanglement_bias: float
    hybrid_report: QuantumCycleReport
    symbolic_tag: str
    quantum_tag: str
    hybrid_tag: str
    manifest_path: Path


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="milliseconds")


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _anchor_hash_vector(anchor: str, dimension: int) -> List[float]:
    digest = hashlib.sha256(anchor.encode("utf-8")).digest()
    if dimension <= 0:
        return []
    spread = [((digest[i % len(digest)] / 255.0) * 2.0) - 1.0 for i in range(dimension)]
    return spread


def _requires_arbitration(state: Any) -> bool:
    requires = getattr(state, "requires_arbitration", None)
    if callable(requires):
        return bool(requires())
    return bool(getattr(state, "requires_arbitration", False))


def _normalize_metrics(state: Any) -> List[float]:
    depth = float(getattr(state, "depth", 0))
    consciousness = float(getattr(state, "consciousness_level", 0.0))
    entropy = float(getattr(state, "entropy", 0.0))
    paradox_count = float(len(getattr(state, "paradoxes_detected", []) or []))
    resolved_count = float(len(getattr(state, "paradoxes_resolved", []) or []))
    divergent_count = float(len(getattr(state, "divergent_truths", []) or []))
    memory_mb = float(getattr(state, "memory_usage_mb", 0.0))
    cpu_pct = float(getattr(state, "cpu_usage_percent", 0.0))
    arbitration_flag = 1.0 if _requires_arbitration(state) else 0.0

    return [
        _clamp(consciousness, 0.0, 1.0),
        _clamp(1.0 - entropy, 0.0, 1.0),
        _clamp((depth % 1024.0) / 1024.0, 0.0, 1.0),
        _clamp(paradox_count / 10.0, 0.0, 1.0),
        _clamp(resolved_count / 10.0, 0.0, 1.0),
        _clamp(divergent_count / 10.0, 0.0, 1.0),
        _clamp(memory_mb / 1024.0, 0.0, 1.0),
        _clamp(cpu_pct / 100.0, 0.0, 1.0),
        arbitration_flag,
    ]


def build_classical_payload(state: Any, dimension: Optional[int] = None) -> List[float]:
    """Project recursion telemetry into a classical payload vector."""

    target_dimension = dimension or _DEFAULT_PAYLOAD_DIMENSION
    metrics = _normalize_metrics(state)
    anchor = getattr(state, "anchor", "UNKNOWN-ANCHOR")
    anchor_vector = _anchor_hash_vector(anchor, target_dimension)

    payload: List[float] = []
    for index in range(target_dimension):
        base = metrics[index] if index < len(metrics) else 0.0
        modulation = anchor_vector[index] * 0.2
        payload.append(_clamp(base + modulation, -1.0, 1.0))
    return payload


def compute_entanglement_bias(state: Any) -> float:
    consciousness = float(getattr(state, "consciousness_level", 0.0))
    entropy = float(getattr(state, "entropy", 0.0))
    arbitration_penalty = 0.15 if _requires_arbitration(state) else 0.0
    bias = (consciousness * 0.55) + ((1.0 - entropy) * 0.35) + (0.1 - arbitration_penalty)
    return _clamp(bias, 0.05, 0.95)


def _serialize_recursion_state(state: Any) -> dict[str, Any]:
    thread_chain = list(getattr(state, "thread_chain", []) or [])
    if "T10-HYBRID-2025" not in thread_chain:
        thread_chain.append("T10-HYBRID-2025")

    return {
        "anchor": getattr(state, "anchor", "UNKNOWN"),
        "parent_anchor": getattr(state, "parent_anchor", "UNKNOWN"),
        "depth": int(getattr(state, "depth", 0)),
        "consciousness_level": float(getattr(state, "consciousness_level", 0.0)),
        "entropy": float(getattr(state, "entropy", 0.0)),
        "paradoxes_detected": len(getattr(state, "paradoxes_detected", []) or []),
        "paradoxes_resolved": len(getattr(state, "paradoxes_resolved", []) or []),
        "divergent_truths": len(getattr(state, "divergent_truths", []) or []),
        "memory_usage_mb": float(getattr(state, "memory_usage_mb", 0.0)),
        "cpu_usage_percent": float(getattr(state, "cpu_usage_percent", 0.0)),
        "timestamp": getattr(state, "timestamp", _timestamp()),
        "thread_chain": thread_chain,
        "requires_arbitration": _requires_arbitration(state),
        "dlp_level": getattr(state, "dlp_tag", BRIDGE_DLP_LEVEL),
    }


def _manifest_path(orchestrator: HybridQuantumOrchestrator, cycle_index: int) -> Path:
    bridge_dir = orchestrator.work_dir / "bridge_manifests"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    return bridge_dir / f"bridge_cycle_{cycle_index:04d}.json"


def _update_dlp_tags(
    tracker: NativeDLPTracker,
    *,
    symbolic_tag: str,
    quantum_tag: str,
    hybrid_tag: str,
) -> None:
    symbolic = tracker.tags[symbolic_tag]
    symbolic.metadata.setdefault("context_tag", BRIDGE_CONTEXT_TAG)
    symbolic.metadata.setdefault("dlp_level", BRIDGE_DLP_LEVEL)
    symbolic.add_anchor_protocol("T9-INFINITE-UNIFIED-2025")
    symbolic.add_anchor_protocol("T10-HYBRID-2025")
    symbolic.add_anchor_protocol("ANCHOR_LOCKED")
    symbolic.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
    symbolic.add_t1_srb_anchor("SRB_SYMBOLIC_BRIDGE")

    quantum = tracker.tags[quantum_tag]
    quantum.metadata.setdefault("context_tag", BRIDGE_CONTEXT_TAG)
    quantum.metadata.setdefault("dlp_level", BRIDGE_DLP_LEVEL)
    quantum.add_anchor_protocol("T10-HYBRID-2025")
    quantum.add_t1_srb_anchor("SRB_QUANTUM_BRIDGE")

    hybrid = tracker.tags[hybrid_tag]
    hybrid.metadata.setdefault("context_tag", BRIDGE_CONTEXT_TAG)
    hybrid.metadata.setdefault("dlp_level", BRIDGE_DLP_LEVEL)
    hybrid.add_anchor_protocol("EOS_SEED_ORION")
    hybrid.add_anchor_protocol("ANCHOR_LOCKED")
    hybrid.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
    hybrid.add_t1_srb_anchor("SRB_REALITY_BRIDGE")


async def run_hybrid_cycle_from_recursion(
    hybrid_orchestrator: HybridQuantumOrchestrator,
    recursion_state: Any,
    *,
    tracker: Optional[NativeDLPTracker] = None,
    cycle_index: Optional[int] = None,
    payload: Optional[Iterable[float]] = None,
) -> BridgeRunResult:
    """Execute a hybrid orchestration cycle seeded by a recursion state."""

    tracker = tracker or NativeDLPTracker()
    dimension = hybrid_orchestrator.classical_dimension
    generated_payload = list(payload) if payload is not None else build_classical_payload(
        recursion_state, dimension
    )
    entanglement_bias = compute_entanglement_bias(recursion_state)

    recursion_snapshot = _serialize_recursion_state(recursion_state)

    symbolic_tag = tracker.tag_symbolic_operation(
        {
            "dimension": dimension,
            "concepts": [recursion_snapshot["anchor"], recursion_snapshot["parent_anchor"]],
            "context_tag": BRIDGE_CONTEXT_TAG,
            "recursion_depth": recursion_snapshot["depth"],
            "entropy": recursion_snapshot["entropy"],
            "divergent_truths": recursion_snapshot["divergent_truths"],
        }
    )

    report = await hybrid_orchestrator.run_cycle(
        generated_payload,
        cycle_index=cycle_index,
        entanglement_bias=entanglement_bias,
    )

    quantum_tag = tracker.tag_quantum_operation(
        {
            "num_qubits": hybrid_orchestrator.num_qubits,
            "operations": ["phase9_bridge_cycle"],
            "shots": len(report.measurement.probabilities),
            "cycle_index": report.cycle_index,
            "entanglement": report.metadata.entanglement,
            "decoherence": report.metadata.decoherence,
            "context_tag": BRIDGE_CONTEXT_TAG,
        }
    )

    hybrid_tag = tracker.tag_hybrid_operation(
        {
            "coherence": report.metadata.entanglement,
            "efficiency": report.consciousness_score,
            "quantum_entropy": report.metadata.decoherence,
            "symbolic_entropy": recursion_snapshot["entropy"],
            "combined_entropy": (report.metadata.decoherence + recursion_snapshot["entropy"]) / 2.0,
            "context_tag": BRIDGE_CONTEXT_TAG,
        },
        quantum_tag,
        symbolic_tag,
    )

    _update_dlp_tags(tracker, symbolic_tag=symbolic_tag, quantum_tag=quantum_tag, hybrid_tag=hybrid_tag)

    manifest = {
        "bridge_anchor": BRIDGE_ANCHOR,
        "timestamp": _timestamp(),
        "context_tag": BRIDGE_CONTEXT_TAG,
        "recursion_state": recursion_snapshot,
        "hybrid_cycle": {
            "cycle_index": report.cycle_index,
            "entanglement": report.metadata.entanglement,
            "decoherence": report.metadata.decoherence,
            "consciousness_score": report.consciousness_score,
            "export_path": str(report.export_path),
            "entanglement_graph": str(report.entanglement_graph_path),
        },
        "dlp": {
            "symbolic_tag": symbolic_tag,
            "quantum_tag": quantum_tag,
            "hybrid_tag": hybrid_tag,
            "dlp_level": BRIDGE_DLP_LEVEL,
        },
        "thread_chain": recursion_snapshot["thread_chain"],
    }

    manifest_path = _manifest_path(hybrid_orchestrator, report.cycle_index)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    return BridgeRunResult(
        recursion_anchor=recursion_snapshot["anchor"],
        recursion_depth=recursion_snapshot["depth"],
        payload=generated_payload,
        entanglement_bias=entanglement_bias,
        hybrid_report=report,
        symbolic_tag=symbolic_tag,
        quantum_tag=quantum_tag,
        hybrid_tag=hybrid_tag,
        manifest_path=manifest_path,
    )
