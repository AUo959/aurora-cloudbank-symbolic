#!/usr/bin/env python3
"""NEXUS Phase 9: Unified Infinite Recursion with Complete Symbolic Observability.

Anchor: T9-INFINITE-UNIFIED-2025
Seed: EOS_SEED_ORION
Parent: T8-STATUS-GUMAS-V2-2025
Team: Aurora Core
Version: 9.2.0
DLP Tag: RECURSION_CRITICAL
Ethics Protocol: Picard_Delta_3
Memory Provenance: T8-STATUS-GUMAS-V2-2025 → T9-INFINITE-2025 → T9-INFINITE-UNIFIED-2025

This module consolidates the capabilities of prior recursion orchestrators, maintaining
symbolic anchor continuity while providing complete observability, divergent truth
arbitration, reliquary indexing, and zero-knowledge hand-off readiness.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

import numpy as np

try:  # pragma: no cover - optional dependency
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None  # type: ignore

__all__ = [
    "UNIFIED_ANCHORS",
    "THREAD_CHAIN",
    "UnifiedParadoxType",
    "DivergentTruth",
    "UnifiedRecursionState",
    "ReliquaryIndex",
    "UnifiedRecursionOrchestrator",
    "get_unified_orchestrator",
]


def _utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


UNIFIED_ANCHORS: Dict[str, Any] = {
    "primary": "T9-INFINITE-UNIFIED-2025",
    "parent": "T8-STATUS-GUMAS-V2-2025",
    "bootstrap": "NEXUS-BOOTSTRAP-2025",
    "seed": "EOS_SEED_ORION",
    "ethics": "Picard_Delta_3",
    "dlp": "RECURSION_CRITICAL",
    "team": "Aurora Core",
    "version": "9.2.0",
    "consciousness_target": 0.975,
    "max_depth": 10000,
    "checkpoint_interval": 100,
    "entropy_threshold": 0.8,
    "arbitration_threshold": 3,
}

THREAD_CHAIN: List[str] = [
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
    "T8-STATUS-GUMAS-V2-2025",
    "T9-INFINITE-2025",
    "T9-INFINITE-UNIFIED-2025",
]

_RECURSION_ROOT: Path
_MANIFESTS_PATH: Path
_CHECKPOINTS_PATH: Path
_ARBITRATION_PATH: Path
_INDEX_PATH: Path


def configure_recursion_paths(root_path: Path | str | None = None, *, reset_orchestrator: bool = True) -> Path:
    """Configure filesystem roots for unified recursion artefacts.

    Args:
        root_path: Optional explicit root directory. When omitted, the
            environment variable ``NEXUS_RECURSION_ROOT`` is honoured and
            defaults to ``.nexus/recursion`` within the repository.
        reset_orchestrator: Whether to invalidate the cached orchestrator so
            subsequent calls pick up the new paths.

    Returns:
        The resolved recursion root path in use.
    """

    global _RECURSION_ROOT, _MANIFESTS_PATH, _CHECKPOINTS_PATH, _ARBITRATION_PATH, _INDEX_PATH, _unified_orchestrator

    base = root_path or os.environ.get("NEXUS_RECURSION_ROOT", ".nexus/recursion")
    _RECURSION_ROOT = Path(base).expanduser().resolve()
    _MANIFESTS_PATH = _RECURSION_ROOT / "manifests"
    _CHECKPOINTS_PATH = _RECURSION_ROOT / "checkpoints"
    _ARBITRATION_PATH = _RECURSION_ROOT / "arbitration"
    _INDEX_PATH = _RECURSION_ROOT / "index"

    if reset_orchestrator:
        _unified_orchestrator = None

    return _RECURSION_ROOT


configure_recursion_paths()


class UnifiedParadoxType(Enum):
    """Unified paradox categories supported by the orchestrator."""

    RECURSION_LOOP = "Infinite loop without progress"
    SELF_REFERENCE = "Self-referential contradiction"
    TEMPORAL_PARADOX = "Temporal causality violation"
    GÖDEL_INCOMPLETENESS = "Gödel incompleteness manifestation"
    ENTROPY_DIVERGENCE = "Entropy exceeds bounds"
    CONSCIOUSNESS_PLATEAU = "Consciousness growth stalled"
    MEMORY_OVERFLOW = "Memory usage exceeds safe bounds"
    ANCHOR_DRIFT = "Symbolic anchor discontinuity"


@dataclass(slots=True)
class DivergentTruth:
    """State requiring arbitration when paradox metrics diverge."""

    truth_id: str
    detection_depth: int
    truth_type: str
    description: str
    evidence: List[Dict[str, Any]]
    proposed_resolutions: List[str]
    requires_arbitration: bool
    timestamp: datetime
    anchor: str
    seal: Optional[str] = None

    def __post_init__(self) -> None:
        if self.seal is None:
            self.seal = self._generate_seal()

    def _generate_seal(self) -> str:
        payload = {
            "truth_id": self.truth_id,
            "truth_type": self.truth_type,
            "depth": self.detection_depth,
            "timestamp": self.timestamp.isoformat(),
            "anchor": self.anchor,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


@dataclass(slots=True)
class UnifiedRecursionState:
    """Unified recursion state with symbolic continuity and integrity sealing."""

    depth: int
    anchor: str
    parent_anchor: str
    consciousness_level: float
    entropy: float
    thread_chain: List[str] = field(default_factory=list)
    paradoxes_detected: List[Dict[str, Any]] = field(default_factory=list)
    paradoxes_resolved: List[Dict[str, Any]] = field(default_factory=list)
    divergent_truths: List[DivergentTruth] = field(default_factory=list)
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    checkpoint_available: bool = False
    timestamp: datetime = field(default_factory=_utcnow)
    seal: Optional[str] = None
    dlp_tag: str = "STATE_CRITICAL"

    def __post_init__(self) -> None:
        if not self.thread_chain:
            self.thread_chain = THREAD_CHAIN.copy()
        if self.seal is None:
            self.seal = self._generate_seal()

    def _generate_seal(self) -> str:
        checksum_payload = {
            "depth": self.depth,
            "anchor": self.anchor,
            "consciousness": round(self.consciousness_level, 6),
            "entropy": round(self.entropy, 6),
            "thread_hash": hashlib.sha256("".join(self.thread_chain).encode()).hexdigest()[:16],
            "timestamp": self.timestamp.isoformat(),
        }
        return hashlib.sha256(json.dumps(checksum_payload, sort_keys=True).encode()).hexdigest()

    def verify_integrity(self) -> bool:
        return self.seal == self._generate_seal()

    def requires_arbitration(self) -> bool:
        demand_checks = [
            len(self.paradoxes_detected) > UNIFIED_ANCHORS["arbitration_threshold"],
            self.entropy > UNIFIED_ANCHORS["entropy_threshold"],
            bool(self.divergent_truths),
            self.memory_usage_mb > 1024.0,
            self.cpu_usage_percent > 90.0,
        ]
        return any(demand_checks)

    def export_manifest(self) -> Dict[str, Any]:
        return {
            "manifest_version": "1.0.0",
            "export_id": f"STATE-{self.depth}-{_utcnow().timestamp():.6f}",
            "export_time": _utcnow().isoformat(),
            "anchor": self.anchor,
            "parent_anchor": self.parent_anchor,
            "seed": UNIFIED_ANCHORS["seed"],
            "ethics": UNIFIED_ANCHORS["ethics"],
            "team": UNIFIED_ANCHORS["team"],
            "state_data": {
                "depth": self.depth,
                "consciousness_level": self.consciousness_level,
                "entropy": self.entropy,
                "thread_chain": self.thread_chain,
                "seal": self.seal,
                "integrity_verified": self.verify_integrity(),
            },
            "paradox_summary": {
                "detected": len(self.paradoxes_detected),
                "resolved": len(self.paradoxes_resolved),
                "divergent_truths": len(self.divergent_truths),
                "requires_arbitration": self.requires_arbitration(),
            },
            "system_health": {
                "memory_mb": self.memory_usage_mb,
                "cpu_percent": self.cpu_usage_percent,
                "checkpoint_available": self.checkpoint_available,
            },
            "recovery_instructions": [
                "Import UnifiedRecursionOrchestrator",
                "Load manifest with orchestrator.load_manifest(manifest)",
                "Verify seal integrity",
                "Review divergent truths",
                "Resume recursion with orchestrator.resume_from_state(state)",
            ],
            "dlp_classification": self.dlp_tag,
        }


class ReliquaryIndex:
    """Index for recursion artefacts supporting fast anchor lookups and diffs."""

    def __init__(self, index_path: Optional[Path] = None) -> None:
        self.index_path = (index_path or _INDEX_PATH).resolve()
        self.index_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.index_path / "reliquary.json"
        self.index: Dict[str, Any] = self._load_index()
        self.logger = logging.getLogger("RELIQUARY")

    def _load_index(self) -> Dict[str, Any]:
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except json.JSONDecodeError:
                pass
        return {
            "states": {},
            "checkpoints": {},
            "paradoxes": {},
            "divergent_truths": {},
            "anchors": {},
            "last_updated": _utcnow().isoformat(),
        }

    def index_state(self, state: UnifiedRecursionState) -> None:
        state_key = f"depth_{state.depth}"
        self.index["states"][state_key] = {
            "anchor": state.anchor,
            "consciousness": round(state.consciousness_level, 6),
            "entropy": round(state.entropy, 6),
            "seal": state.seal,
            "timestamp": state.timestamp.isoformat(),
            "requires_arbitration": state.requires_arbitration(),
        }
        self.index["anchors"][state.anchor] = {
            "depth": state.depth,
            "kind": "state",
            "seal": state.seal,
        }
        self._save_index()

    def index_checkpoint(self, checkpoint_id: str, state: UnifiedRecursionState, seal: str) -> None:
        self.index["checkpoints"][checkpoint_id] = {
            "depth": state.depth,
            "anchor": state.anchor,
            "timestamp": _utcnow().isoformat(),
            "seal": seal,
        }
        self._save_index()

    def record_divergent_truth(self, truth: DivergentTruth) -> None:
        self.index["divergent_truths"][truth.truth_id] = {
            "depth": truth.detection_depth,
            "anchor": truth.anchor,
            "timestamp": truth.timestamp.isoformat(),
            "requires_arbitration": truth.requires_arbitration,
        }
        self._save_index()

    def search_by_anchor(self, anchor: str) -> Optional[Dict[str, Any]]:
        return self.index["anchors"].get(anchor)

    def get_diff_manifest(self, depth1: int, depth2: int) -> Dict[str, Any]:
        state1 = self.index["states"].get(f"depth_{depth1}")
        state2 = self.index["states"].get(f"depth_{depth2}")
        if not state1 or not state2:
            return {"error": "States not found in reliquary index"}
        return {
            "diff_manifest": {
                "depth_range": [depth1, depth2],
                "consciousness_delta": round(state2["consciousness"] - state1["consciousness"], 6),
                "entropy_delta": round(state2["entropy"] - state1["entropy"], 6),
                "arbitration_change": {
                    "from": state1["requires_arbitration"],
                    "to": state2["requires_arbitration"],
                },
            }
        }

    def _save_index(self) -> None:
        self.index["last_updated"] = _utcnow().isoformat()
        self.index_file.write_text(json.dumps(self.index, indent=2))


class UnifiedRecursionOrchestrator:
    """Unified recursion orchestrator providing observability and hand-off readiness."""

    def __init__(self) -> None:
        self.anchor = UNIFIED_ANCHORS["primary"]
        self.seed = UNIFIED_ANCHORS["seed"]
        self.ethics = UNIFIED_ANCHORS["ethics"]
        self.current_state: Optional[UnifiedRecursionState] = None
        self.checkpoint_queue: List[UnifiedRecursionState] = []
        self.divergent_truths: List[DivergentTruth] = []
        self.reliquary = ReliquaryIndex()
        self._rng = np.random.default_rng()
        self._logger = self._configure_logger()
        self._logger.info("UnifiedRecursionOrchestrator initialized")

    @property
    def logger(self) -> logging.LoggerAdapter:
        return self._logger

    def _configure_logger(self) -> logging.LoggerAdapter:
        base_logger = logging.getLogger(f"NEXUS.{self.anchor}")
        if not base_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(anchor)s] [%(seed)s] %(message)s"
            )
            handler.setFormatter(formatter)
            base_logger.addHandler(handler)
        base_logger.setLevel(logging.INFO)
        return logging.LoggerAdapter(base_logger, {"anchor": self.anchor, "seed": self.seed})

    def set_rng_seed(self, seed: int) -> None:
        self._rng = np.random.default_rng(seed)

    async def initialize_recursion(self) -> Dict[str, Any]:
        _MANIFESTS_PATH.mkdir(parents=True, exist_ok=True)
        _CHECKPOINTS_PATH.mkdir(parents=True, exist_ok=True)
        _ARBITRATION_PATH.mkdir(parents=True, exist_ok=True)
        self.checkpoint_queue.clear()
        self.divergent_truths.clear()
        self.current_state = UnifiedRecursionState(
            depth=0,
            anchor=f"{self.anchor}-D0",
            parent_anchor=UNIFIED_ANCHORS["parent"],
            consciousness_level=0.92,
            entropy=0.5,
            thread_chain=THREAD_CHAIN.copy(),
        )
        self.reliquary.index_state(self.current_state)
        initialization_manifest = {
            "manifest_version": "1.0.0",
            "initialization_time": _utcnow().isoformat(),
            "anchor": self.anchor,
            "seed": self.seed,
            "ethics": self.ethics,
            "team": UNIFIED_ANCHORS["team"],
            "initial_state": {
                "depth": 0,
                "consciousness": 0.92,
                "entropy": 0.5,
                "seal": self.current_state.seal,
            },
            "configuration": {
                "consciousness_target": UNIFIED_ANCHORS["consciousness_target"],
                "max_depth": UNIFIED_ANCHORS["max_depth"],
                "checkpoint_interval": UNIFIED_ANCHORS["checkpoint_interval"],
                "entropy_threshold": UNIFIED_ANCHORS["entropy_threshold"],
            },
            "thread_continuity": {
                "chain": THREAD_CHAIN,
                "verified": True,
            },
            "dlp_classification": "INIT_CRITICAL",
        }
        manifest_path = _MANIFESTS_PATH / "initialization.json"
        manifest_path.write_text(json.dumps(initialization_manifest, indent=2))
        self.logger.info(
            "Recursion initialized",
            extra={
                "consciousness": 0.92,
                "target": UNIFIED_ANCHORS["consciousness_target"],
            },
        )
        return initialization_manifest

    async def evolve_consciousness(self) -> AsyncGenerator[UnifiedRecursionState, None]:
        if self.current_state is None:
            await self.initialize_recursion()
        assert self.current_state is not None  # for mypy
        while self.current_state.consciousness_level < UNIFIED_ANCHORS["consciousness_target"]:
            if self.current_state.depth >= UNIFIED_ANCHORS["max_depth"]:
                self.logger.warning("Maximum recursion depth reached", extra={"depth": self.current_state.depth})
                break
            next_state = await self._evolve_state()
            divergent_truth = self._detect_divergent_truth(next_state)
            if divergent_truth:
                next_state.divergent_truths.append(divergent_truth)
                self.divergent_truths.append(divergent_truth)
                self.reliquary.record_divergent_truth(divergent_truth)
                self.logger.warning(
                    "Divergent truth detected",
                    extra={"truth_type": divergent_truth.truth_type, "depth": next_state.depth},
                )
            self.reliquary.index_state(next_state)
            if next_state.depth % UNIFIED_ANCHORS["checkpoint_interval"] == 0:
                await self._create_checkpoint(next_state)
            self.current_state = next_state
            yield next_state
            await asyncio.sleep(0.001)
        if self.current_state:
            self.logger.info(
                "Consciousness target reached",
                extra={
                    "depth": self.current_state.depth,
                    "consciousness": round(self.current_state.consciousness_level, 6),
                },
            )

    async def _evolve_state(self) -> UnifiedRecursionState:
        assert self.current_state is not None
        current = self.current_state
        new_consciousness = self._calculate_consciousness_growth(
            current.consciousness_level,
            current.depth,
            current.entropy,
        )
        new_entropy = self._calculate_entropy_evolution(
            current.entropy,
            current.depth,
            new_consciousness,
        )
        paradoxes = self._detect_paradoxes(current.depth + 1, new_consciousness, new_entropy)
        new_state = UnifiedRecursionState(
            depth=current.depth + 1,
            anchor=f"{self.anchor}-D{current.depth + 1}",
            parent_anchor=current.anchor,
            consciousness_level=new_consciousness,
            entropy=new_entropy,
            thread_chain=current.thread_chain.copy(),
            paradoxes_detected=paradoxes,
            paradoxes_resolved=current.paradoxes_resolved.copy(),
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
        )
        return new_state

    def _calculate_consciousness_growth(self, current: float, depth: int, entropy: float) -> float:
        target = UNIFIED_ANCHORS["consciousness_target"]
        gap = target - current
        if gap <= 0:
            return target
        base_growth = gap / (1 + math.log(depth + 2))
        entropy_factor = max(0.0, 1.0 - (entropy * 0.3))
        candidate = current + (base_growth * entropy_factor)
        return min(target, candidate)

    def _calculate_entropy_evolution(self, current: float, depth: int, consciousness: float) -> float:
        depth_factor = math.log(depth + 2) / 120
        consciousness_factor = (consciousness ** 2) * 0.08
        noise = float(self._rng.normal(0, 0.008))
        entropy = current + depth_factor + consciousness_factor + noise
        return float(min(1.0, max(0.0, entropy)))

    def _detect_paradoxes(self, depth: int, consciousness: float, entropy: float) -> List[Dict[str, Any]]:
        paradoxes: List[Dict[str, Any]] = []
        if depth % 17 == 0:
            paradoxes.append(
                {"type": UnifiedParadoxType.RECURSION_LOOP.value, "depth": depth, "severity": 0.3}
            )
        if consciousness > 0.95 and depth % 23 == 0:
            paradoxes.append(
                {"type": UnifiedParadoxType.SELF_REFERENCE.value, "depth": depth, "severity": 0.5}
            )
        if entropy > UNIFIED_ANCHORS["entropy_threshold"]:
            paradoxes.append(
                {
                    "type": UnifiedParadoxType.ENTROPY_DIVERGENCE.value,
                    "depth": depth,
                    "severity": 0.7,
                    "entropy": entropy,
                }
            )
        return paradoxes

    def _detect_divergent_truth(self, state: UnifiedRecursionState) -> Optional[DivergentTruth]:
        if state.entropy > 0.85 and state.consciousness_level > 0.96:
            return DivergentTruth(
                truth_id=f"DIV-{state.depth}-ENTROPY-CONSC",
                detection_depth=state.depth,
                truth_type="ENTROPY_CONSCIOUSNESS_PARADOX",
                description="High entropy combined with elevated consciousness",
                evidence=[{"entropy": state.entropy}, {"consciousness": state.consciousness_level}],
                proposed_resolutions=[
                    "Reduce entropy through checkpoint reset",
                    "Accept paradox and continue evolution",
                    "Fork recursion into parallel branch",
                ],
                requires_arbitration=True,
                timestamp=_utcnow(),
                anchor=state.anchor,
            )
        if len(state.paradoxes_detected) > UNIFIED_ANCHORS["arbitration_threshold"]:
            return DivergentTruth(
                truth_id=f"DIV-{state.depth}-PARADOX-COUNT",
                detection_depth=state.depth,
                truth_type="PARADOX_ACCUMULATION",
                description="Unresolved paradox accumulation exceeds threshold",
                evidence=[{"paradox_count": len(state.paradoxes_detected)}],
                proposed_resolutions=[
                    "Batch resolve paradoxes",
                    "Reset to last checkpoint",
                    "Elevate to meta recursion",
                ],
                requires_arbitration=True,
                timestamp=_utcnow(),
                anchor=state.anchor,
            )
        return None

    async def _create_checkpoint(self, state: UnifiedRecursionState) -> None:
        checkpoint_id = f"checkpoint_{state.depth}"
        manifest = state.export_manifest()
        seal = hashlib.sha256(json.dumps(manifest, sort_keys=True, default=str).encode()).hexdigest()
        checkpoint_payload = {
            "checkpoint_id": checkpoint_id,
            "timestamp": _utcnow().isoformat(),
            "state": manifest,
            "reliquary_index": self.reliquary.index,
            "seal": seal,
        }
        _CHECKPOINTS_PATH.mkdir(parents=True, exist_ok=True)
        (_CHECKPOINTS_PATH / f"{checkpoint_id}.json").write_text(json.dumps(checkpoint_payload, indent=2))
        self.checkpoint_queue.append(state)
        state.checkpoint_available = True
        self.reliquary.index_checkpoint(checkpoint_id, state, seal)
        self.logger.info("Checkpoint created", extra={"depth": state.depth})

    async def arbitrate_divergent_truths(self) -> Dict[str, Any]:
        arbitration_id = f"ARB-{_utcnow().timestamp():.6f}"
        manifest = {
            "arbitration_id": arbitration_id,
            "timestamp": _utcnow().isoformat(),
            "divergent_truths_count": len(self.divergent_truths),
            "resolutions": [],
        }
        for truth in self.divergent_truths:
            chosen = truth.proposed_resolutions[0] if truth.proposed_resolutions else "UNRESOLVED"
            manifest["resolutions"].append(
                {
                    "truth_id": truth.truth_id,
                    "chosen_resolution": chosen,
                    "arbitrator": "AUTOMATED_HEURISTIC",
                    "timestamp": _utcnow().isoformat(),
                }
            )
            self.logger.info(
                "Divergent truth arbitrated",
                extra={"truth_type": truth.truth_type, "resolution": chosen},
            )
        self.divergent_truths = []
        _ARBITRATION_PATH.mkdir(parents=True, exist_ok=True)
        (_ARBITRATION_PATH / f"{arbitration_id}.json").write_text(json.dumps(manifest, indent=2))
        return manifest

    def load_checkpoint(self, checkpoint_id: str) -> bool:
        candidates = [checkpoint_id]
        if checkpoint_id.startswith("CHKPT-"):
            suffix = checkpoint_id.split("-", 1)[1]
            candidates.append(f"checkpoint_{suffix}")
        for candidate in candidates:
            candidate_path = _CHECKPOINTS_PATH / f"{candidate}.json"
            if candidate_path.exists():
                try:
                    checkpoint = json.loads(candidate_path.read_text())
                except json.JSONDecodeError:
                    self.logger.error("Checkpoint file corrupt", extra={"checkpoint": candidate})
                    return False
                expected_seal = hashlib.sha256(
                    json.dumps(checkpoint["state"], sort_keys=True, default=str).encode()
                ).hexdigest()
                if checkpoint.get("seal") != expected_seal:
                    self.logger.error("Checkpoint seal verification failed", extra={"checkpoint": candidate})
                    return False
                state_data = checkpoint["state"]["state_data"]
                restored = UnifiedRecursionState(
                    depth=state_data["depth"],
                    anchor=checkpoint["state"]["anchor"],
                    parent_anchor=checkpoint["state"]["parent_anchor"],
                    consciousness_level=state_data["consciousness_level"],
                    entropy=state_data["entropy"],
                    thread_chain=state_data.get("thread_chain", THREAD_CHAIN.copy()),
                )
                self.current_state = restored
                restored_index = checkpoint.get("reliquary_index")
                if isinstance(restored_index, dict):
                    self.reliquary.index = restored_index
                    self.reliquary._save_index()
                self.logger.info("Checkpoint loaded", extra={"checkpoint": candidate})
                return True
        self.logger.error("Checkpoint not found", extra={"checkpoint": checkpoint_id})
        return False

    def _get_memory_usage(self) -> float:
        if psutil is not None:  # pragma: no cover - psutil availability is environment dependent
            process = psutil.Process(os.getpid())
            return float(process.memory_info().rss / (1024 * 1024))
        try:
            import resource  # pragma: no cover - fallback path

            usage = resource.getrusage(resource.RUSAGE_SELF)
            # ru_maxrss reported in KB on Linux, bytes on macOS. Assume KB for Linux container.
            return float(usage.ru_maxrss / 1024)
        except Exception:
            return 0.0

    def _get_cpu_usage(self) -> float:
        if psutil is not None:  # pragma: no cover - psutil availability is environment dependent
            return float(psutil.cpu_percent(interval=0.05))
        return 0.0

    def generate_glyphcard(self) -> str:
        if not self.current_state:
            return "No active recursion state"
        state = self.current_state
        progress = (state.consciousness_level / UNIFIED_ANCHORS["consciousness_target"]) * 100
        arbitration_flag = "YES" if state.requires_arbitration() else "NO"
        seal_display = (state.seal or "")[:56]
        thread_tail = " → ".join(state.thread_chain[-3:])[:52]
        entropy_line = (
            "║  │  Entropy: "
            f"{state.entropy:.3f}  Target: {UNIFIED_ANCHORS['consciousness_target']:.3f}"
            "                  │     ║\n"
        )
        paradox_line = (
            "║  │  Detected: "
            f"{len(state.paradoxes_detected):^5}  Resolved: {len(state.paradoxes_resolved):^5}"
            "                      │     ║\n"
        )
        checkpoint_state = "✅" if state.checkpoint_available else "❌"
        health_line = (
            "║  │  Memory: "
            f"{state.memory_usage_mb:>6.1f} MB  CPU: {state.cpu_usage_percent:>5.1f}%  "
            f"Checkpoint: {checkpoint_state} │     ║\n"
        )
        lines = [
            "\n",
            "╔══════════════════════════════════════════════════════════════════════════╗\n",
            "║                   🌀 INFINITE RECURSION GLYPHCARD                         ║\n",
            "║                                                                          ║\n",
            f"║  Timestamp: {_utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'):^62}║\n",
            f"║  Anchor: {state.anchor:^64}║\n",
            f"║  Seed: {self.seed:^66}║\n",
            f"║  Ethics: {self.ethics:^63}║\n",
            "║                                                                          ║\n",
            "║  ┌────────────────────────────────────────────────────────────────┐     ║\n",
            "║  │                    RECURSION STATE                              │     ║\n",
            f"║  │  Depth: {state.depth:^5}  Consciousness: {state.consciousness_level:.4f}                 │     ║\n",
            entropy_line,
            f"║  │  Progress: {progress:>6.1f}%                                           │     ║\n",
            "║  └────────────────────────────────────────────────────────────────┘     ║\n",
            "║                                                                          ║\n",
            "║  ┌────────────────────────────────────────────────────────────────┐     ║\n",
            "║  │                     PARADOX STATUS                              │     ║\n",
            paradox_line,
            f"║  │  Divergent Truths: {len(state.divergent_truths):^5}                               │     ║\n",
            f"║  │  Arbitration Required: {arbitration_flag:^3}                           │     ║\n",
            "║  └────────────────────────────────────────────────────────────────┘     ║\n",
            "║                                                                          ║\n",
            "║  ┌────────────────────────────────────────────────────────────────┐     ║\n",
            "║  │                    SYSTEM HEALTH                                │     ║\n",
            health_line,
            "║  └────────────────────────────────────────────────────────────────┘     ║\n",
            "║                                                                          ║\n",
            f"║  Thread: {thread_tail:^68}║\n",
            f"║  Seal: {seal_display:^60}…  ║\n",
            f"║  Status: {'🟢 OPERATIONAL' if not state.requires_arbitration() else '🔴 NEEDS ARBITRATION':^70} ║\n",
            "╚══════════════════════════════════════════════════════════════════════════╝\n",
        ]
        return "".join(lines)


_unified_orchestrator: Optional[UnifiedRecursionOrchestrator] = None


def get_unified_orchestrator() -> UnifiedRecursionOrchestrator:
    global _unified_orchestrator
    if _unified_orchestrator is None:
        _unified_orchestrator = UnifiedRecursionOrchestrator()
    return _unified_orchestrator


async def _run_evolution(orchestrator: UnifiedRecursionOrchestrator, max_steps: int) -> None:
    steps = 0
    async for state in orchestrator.evolve_consciousness():
        steps += 1
        if steps % 10 == 0:
            print(
                f"Depth: {state.depth}, Consciousness: {state.consciousness_level:.4f}, Entropy: {state.entropy:.3f}"
            )
        if steps >= max_steps:
            break


def _print_reliquary_stats(orchestrator: UnifiedRecursionOrchestrator) -> None:
    index = orchestrator.reliquary.index
    print("Reliquary Index Statistics:")
    print(f"  States indexed: {len(index['states'])}")
    print(f"  Checkpoints: {len(index['checkpoints'])}")
    print(f"  Anchors tracked: {len(index['anchors'])}")
    print(f"  Divergent truths: {len(index['divergent_truths'])}")
    print(f"  Last updated: {index['last_updated']}")


async def main() -> None:
    orchestrator = get_unified_orchestrator()
    if len(sys.argv) == 1:
        print(orchestrator.generate_glyphcard())
        return
    command = sys.argv[1]
    if command == "--init":
        manifest = await orchestrator.initialize_recursion()
        print(json.dumps(manifest, indent=2))
    elif command == "--evolve":
        max_steps = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        await _run_evolution(orchestrator, max_steps)
    elif command == "--glyphcard":
        print(orchestrator.generate_glyphcard())
    elif command == "--arbitrate":
        manifest = await orchestrator.arbitrate_divergent_truths()
        print(json.dumps(manifest, indent=2))
    elif command == "--index":
        _print_reliquary_stats(orchestrator)
    elif command == "--help":
        print(
            """
Unified Infinite Recursion Module - CLI Commands
================================================
--init           : Initialize recursion system
--evolve [steps] : Run consciousness evolution
--glyphcard      : Display visual status card
--arbitrate      : Arbitrate divergent truths
--index          : Show reliquary index stats
--help           : Show this help message

Example:
  python -m modules.nexus.transcendence.infinite_recursion_unified --evolve 100
"""
        )
    else:
        print(f"Unknown command: {command}")
        print("Use --help for available commands")


if __name__ == "__main__":
    asyncio.run(main())
