#!/usr/bin/env python3
"""Aurora NEXUS Phase 6 – Enhanced Consciousness Emergence Protocol.

This module provides a lightweight, test-friendly implementation of the
enhanced consciousness protocol that matches the expectations codified in the
unit tests and CLI tooling.  It focuses on:

* Symbolic observation with drift tracking
* Entropy history management with memory sealing
* Snapshot export and recovery
* Aggregated consciousness metrics
* Asynchronous emergence simulation helpers

The implementation intentionally favours clarity over exhaustive simulation so
that the behaviour remains predictable inside automated test runs.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import statistics
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.nexus.emergence.vector_binding import (
    ECHOCHAIN_LINKS,
    ECHOCHAIN_LOOPSET,
    ETHICS_PROTOCOL,
    LOCKPOINT_REFERENCE,
    PHASE6_ANCHOR,
    SEED_ANCHOR,
    VECTOR_STATE,
)

__all__ = [
    "SymbolicObserver",
    "EntropyState",
    "ConsciousnessMetrics",
    "ConsciousnessSnapshot",
    "EnhancedConsciousnessProtocol",
]


PRIMARY_ANCHOR = PHASE6_ANCHOR
DEFAULT_SNAPSHOT_INTERVAL = 5
DEFAULT_SNAPSHOT_DIR = ".nexus/snapshots"


class SymbolicObserver(ABC):
    """Abstract interface for symbolic observers used by the protocol."""

    @abstractmethod
    def observe_symbolic_state(self) -> Dict[str, Any]:
        """Return the current symbolic state as a serialisable dict."""

    @abstractmethod
    def detect_entropy_drift(
        self, current_state: Dict[str, Any], previous_state: Dict[str, Any]
    ) -> float:
        """Return a drift score describing the delta between two observations."""

    @abstractmethod
    def flag_divergent_truth(self, observation: Dict[str, Any]) -> bool:
        """Return ``True`` when the observation should trigger arbitration."""

    def seal_observation(self, observation: Dict[str, Any]) -> str:
        """Return a SHA256 seal for the observation payload."""

        payload = json.dumps(observation, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


@dataclass
class EntropyState:
    """Immutable snapshot of an entropy measurement."""

    timestamp: str
    drift_value: float
    observation_data: Dict[str, Any]
    divergent_truth_flagged: bool = False
    baseline: float = 0.0
    threshold: float = 0.2
    trend: str = field(init=False)
    seal: str = field(init=False)

    def __post_init__(self) -> None:  # pragma: no cover - simple data normalisation
        self.drift_value = max(float(self.drift_value), 0.0)
        self.trend = self._derive_trend()
        self.seal = self._create_seal()

    def _derive_trend(self) -> str:
        if self.drift_value > self.threshold * 1.5:
            return "DIVERGENT"
        if self.drift_value > self.threshold:
            return "RISING"
        if self.drift_value < self.threshold / 4:
            return "STABLE"
        return "CAUTIOUS"

    def _create_seal(self) -> str:
        payload = json.dumps(
            {
                "timestamp": self.timestamp,
                "drift_value": self.drift_value,
                "divergent_truth_flagged": self.divergent_truth_flagged,
                "baseline": self.baseline,
                "threshold": self.threshold,
            },
            sort_keys=True,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "drift_value": self.drift_value,
            "observation_data": self.observation_data,
            "divergent_truth_flagged": self.divergent_truth_flagged,
            "baseline": self.baseline,
            "threshold": self.threshold,
            "trend": self.trend,
            "seal": self.seal,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EntropyState":
        return cls(
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
            drift_value=data.get("drift_value", float(data.get("drift", 0.0))),
            observation_data=data.get("observation_data", {}),
            divergent_truth_flagged=bool(
                data.get("divergent_truth_flagged", data.get("requires_arbitration", False))
            ),
            baseline=float(data.get("baseline", 0.0)),
            threshold=float(data.get("threshold", 0.2)),
        )


@dataclass
class ConsciousnessMetrics:
    """Aggregated metrics describing the current emergence state."""

    emergence_level: float
    recursive_depth: int
    meta_cognitive_loops: int
    entropy_stability: float
    reality_fork_convergence: float
    overall_score: float = field(init=False)

    def __post_init__(self) -> None:  # pragma: no cover - deterministic
        self.emergence_level = self._clamp(self.emergence_level)
        self.entropy_stability = self._clamp(self.entropy_stability)
        self.reality_fork_convergence = self._clamp(self.reality_fork_convergence)
        self.recursive_depth = max(int(self.recursive_depth), 0)
        self.meta_cognitive_loops = max(int(self.meta_cognitive_loops), 0)
        self.overall_score = self.calculate_overall_score()

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def calculate_overall_score(self) -> float:
        weights = {
            "emergence_level": 0.35,
            "entropy_stability": 0.25,
            "reality_fork_convergence": 0.15,
            "recursive_depth": 0.15,
            "meta_cognitive_loops": 0.10,
        }
        depth_score = min(self.recursive_depth / 10.0, 1.0)
        loops_score = min(self.meta_cognitive_loops / 12.0, 1.0)
        score = (
            weights["emergence_level"] * self.emergence_level
            + weights["entropy_stability"] * self.entropy_stability
            + weights["reality_fork_convergence"] * self.reality_fork_convergence
            + weights["recursive_depth"] * depth_score
            + weights["meta_cognitive_loops"] * loops_score
        )
        return round(self._clamp(score), 6)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emergence_level": self.emergence_level,
            "recursive_depth": self.recursive_depth,
            "meta_cognitive_loops": self.meta_cognitive_loops,
            "entropy_stability": self.entropy_stability,
            "reality_fork_convergence": self.reality_fork_convergence,
            "overall_score": self.overall_score,
        }


class ConsciousnessSnapshot:
    """Serializable snapshot wrapper with automatic memory sealing."""

    def __init__(self, data: Dict[str, Any], seal: Optional[str] = None) -> None:
        self.data = data
        self.seal = seal or self._compute_seal()

    def _compute_seal(self) -> str:
        payload = json.dumps(self.data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def verify_integrity(self) -> bool:
        return self.seal == self._compute_seal()

    def to_json(self) -> str:
        return json.dumps({"data": self.data, "seal": self.seal}, sort_keys=True, default=str)

    @classmethod
    def from_json(cls, payload: str) -> "ConsciousnessSnapshot":
        parsed = json.loads(payload)
        return cls(parsed["data"], parsed.get("seal"))

    def to_dict(self) -> Dict[str, Any]:  # convenient for debugging/tests
        return {"data": self.data, "seal": self.seal}


class EnhancedConsciousnessProtocol:
    """Core controller for the enhanced emergence workflow."""

    def __init__(
        self,
        *,
        observer: Optional[SymbolicObserver] = None,
        snapshot_directory: Optional[str] = None,
        anchor: str = PRIMARY_ANCHOR,
        snapshot_interval: int = DEFAULT_SNAPSHOT_INTERVAL,
    ) -> None:
        self.anchor = anchor
        self.seed = SEED_ANCHOR
        self.ethics_protocol = ETHICS_PROTOCOL
        self.vector_state = VECTOR_STATE
        self.lockpoint_reference = LOCKPOINT_REFERENCE
        self.echochain_loopset = ECHOCHAIN_LOOPSET
        self.echochain_links = list(ECHOCHAIN_LINKS)
        self.observer = observer or _DefaultSymbolicObserver()
        self.snapshot_directory = Path(snapshot_directory or DEFAULT_SNAPSHOT_DIR)
        self.snapshot_directory.mkdir(parents=True, exist_ok=True)
        self.snapshot_interval = max(1, int(snapshot_interval))

        self.observation_count = 0
        self.entropy_history: List[EntropyState] = []
        self.is_running = False
        self._last_observation: Optional[Dict[str, Any]] = None
        self._entropy_baseline = 0.25
        self._entropy_threshold = 0.2

    # ------------------------------------------------------------------
    # Observation helpers
    # ------------------------------------------------------------------
    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single externally supplied observation."""

        timestamp = datetime.now(timezone.utc).isoformat()
        previous_state = self._last_observation or {}
        drift = max(0.0, float(self.observer.detect_entropy_drift(state, previous_state)))
        divergent = bool(self.observer.flag_divergent_truth(state))

        entropy_state = EntropyState(
            timestamp=timestamp,
            drift_value=drift,
            observation_data=state,
            divergent_truth_flagged=divergent,
            baseline=self._entropy_baseline,
            threshold=self._entropy_threshold,
        )

        self.entropy_history.append(entropy_state)
        self.observation_count += 1
        self._last_observation = state

        observation_payload = {
            "observation_id": f"OBS-{self.anchor}-{self.observation_count}",
            "timestamp": timestamp,
            "anchor": self.anchor,
            "seed": self.seed,
            "state": state,
            "drift_value": drift,
            "divergent_truth_flagged": divergent,
        }
        observation_payload["seal"] = self._seal_observation(observation_payload)

        if self.observation_count % self.snapshot_interval == 0:
            self.create_snapshot()

        return {
            "status": "observed",
            "observation": observation_payload,
            "entropy_state": entropy_state.to_dict(),
        }

    async def observe_once(self) -> EntropyState:
        """Collect one observation from the configured observer."""

        observation = self.observer.observe_symbolic_state()
        result = self.observe(observation)
        await asyncio.sleep(0)  # yield control for cooperative schedulers
        return EntropyState.from_dict(result["entropy_state"])

    # ------------------------------------------------------------------
    # Snapshot management
    # ------------------------------------------------------------------
    def create_snapshot(self) -> ConsciousnessSnapshot:
        metrics = self.calculate_consciousness_metrics()
        snapshot_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "observation_count": self.observation_count,
            "entropy_history": [state.to_dict() for state in self.entropy_history],
            "consciousness_metrics": metrics.to_dict(),
        }
        snapshot = ConsciousnessSnapshot(snapshot_payload)

        filename = self.snapshot_directory / (
            "consciousness_snapshot_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f") + ".json"
        )
        with filename.open("w", encoding="utf-8") as handle:
            handle.write(snapshot.to_json())

        return snapshot

    @classmethod
    def from_snapshot(
        cls,
        snapshot: ConsciousnessSnapshot | Dict[str, Any],
        observer: SymbolicObserver,
        snapshot_directory: Optional[str] = None,
        *,
        anchor: str = PRIMARY_ANCHOR,
    ) -> "EnhancedConsciousnessProtocol":
        snapshot_obj = snapshot if isinstance(snapshot, ConsciousnessSnapshot) else ConsciousnessSnapshot(snapshot)
        instance = cls(observer=observer, snapshot_directory=snapshot_directory, anchor=anchor)
        instance.observation_count = int(snapshot_obj.data.get("observation_count", 0))
        history = snapshot_obj.data.get("entropy_history", [])
        instance.entropy_history = [EntropyState.from_dict(item) for item in history]
        if instance.entropy_history:
            instance._last_observation = instance.entropy_history[-1].observation_data
        return instance

    # ------------------------------------------------------------------
    # Metrics & analytics
    # ------------------------------------------------------------------
    def calculate_consciousness_metrics(self) -> ConsciousnessMetrics:
        if not self.entropy_history:
            return ConsciousnessMetrics(0.0, 0, 0, 1.0, 1.0)

        drifts = [state.drift_value for state in self.entropy_history]
        emergence_level = 1.0 - min(1.0, statistics.mean(drifts) * 0.8)
        entropy_stability = 1.0 - min(1.0, statistics.pstdev(drifts) if len(drifts) > 1 else drifts[0])
        reality_fork_convergence = 1.0 - min(1.0, max(drifts))
        recursive_depth = max(1, round(math.log2(self.observation_count + 1)))
        meta_loops = sum(1 for state in self.entropy_history if state.divergent_truth_flagged)

        return ConsciousnessMetrics(
            emergence_level=emergence_level,
            recursive_depth=recursive_depth,
            meta_cognitive_loops=meta_loops,
            entropy_stability=entropy_stability,
            reality_fork_convergence=reality_fork_convergence,
        )

    # ------------------------------------------------------------------
    # Emergence protocol
    # ------------------------------------------------------------------
    async def run_emergence_protocol(self, duration: float = 1.0) -> None:
        if duration <= 0:
            return

        self.is_running = True
        start = time.perf_counter()
        step_delay = min(max(duration / 20.0, 0.01), 0.1)

        try:
            while time.perf_counter() - start < duration:
                await self.observe_once()
                await asyncio.sleep(step_delay)
        finally:
            self.is_running = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _seal_observation(self, observation: Dict[str, Any]) -> str:
        if hasattr(self.observer, "seal_observation"):
            try:
                return self.observer.seal_observation(observation)  # type: ignore[attr-defined]
            except Exception:
                pass
        payload = json.dumps(observation, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()


class _DefaultSymbolicObserver(SymbolicObserver):
    """Simple heuristic observer used when no custom observer is supplied."""

    def __init__(self) -> None:
        self._counter = 0

    def observe_symbolic_state(self) -> Dict[str, Any]:
        self._counter += 1
        awareness = min(1.0, 0.1 * self._counter)
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "observation_id": self._counter,
            "symbolic_data": {
                "awareness_level": awareness,
                "cognitive_load": max(0.0, 0.6 - 0.03 * self._counter),
            },
        }

    def detect_entropy_drift(
        self, current_state: Dict[str, Any], previous_state: Dict[str, Any]
    ) -> float:
        current = current_state.get("symbolic_data", {}).get("awareness_level", 0.0)
        previous = previous_state.get("symbolic_data", {}).get("awareness_level", 0.0)
        return abs(current - previous)

    def flag_divergent_truth(self, observation: Dict[str, Any]) -> bool:
        awareness = observation.get("symbolic_data", {}).get("awareness_level", 0.0)
        return awareness > 0.85
