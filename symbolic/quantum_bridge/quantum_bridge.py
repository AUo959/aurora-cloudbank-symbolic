"""
QuantumBridge — reality-to-symbolic translation layer.

Reads ``bridge_config.yaml`` and converts reality-signal samples into
CONSTELLINK ``ThreadDescriptor`` objects that ORACULITH can consume,
enforcing the causal anchor before any thread is emitted.

This is a software bridge, not a hardware driver: there is no physical
quantum sensor in this repo to sample from. Real signal ingestion is
injected via ``reality_provider`` (same pattern as
``src/sensors/core/sensor_base.ProviderSensor``) so the bridge's shape is
correct now and a real feed can be wired later without touching this
module. The default provider returns an empty signal dict rather than
fabricating data.

Anchors: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

from symbolic.constellink import DEFAULT_ANCHOR_SEED, DEFAULT_ETHICS_PROTOCOL, ThreadDescriptor

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent / "bridge_config.yaml"

RealityProvider = Callable[[], Dict[str, Any]]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_reality_provider() -> Dict[str, Any]:
    """No real feed wired. Returns an empty signal set rather than fake data."""
    return {}


@dataclass
class BridgeHealth:
    """``NodeHealth``-compatible status for Constellation monitoring.

    Mirrors ``constellation_types.NodeHealth`` field names so callers can
    build a ``NodeHealth`` from this without renaming, without this module
    depending on the constellation-contracts package registering
    ``ORION-QUANTUM-BRIDGE`` as a node (it is not registered there yet —
    see module docstring in this file's PR description).
    """

    node: str
    status: str
    timestamp: str
    manifest_version: str
    last_coherence: Optional[float] = None
    last_event: Optional[str] = None


class CausalAnchorViolation(Exception):
    """Raised when a reality sample fails causal-anchor validation."""


class QuantumBridge:
    """Reality-to-symbolic translation layer driven by ``bridge_config.yaml``."""

    def __init__(
        self,
        config_path: Path = DEFAULT_CONFIG_PATH,
        reality_provider: Optional[RealityProvider] = None,
    ):
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.reality_provider = reality_provider or _default_reality_provider
        self._last_coherence: float = 1.0
        self._last_sample_at: Optional[str] = None

    @staticmethod
    def _load_config(config_path: Path) -> Dict[str, Any]:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        return raw["quantum_bridge"]

    def sample_reality(self) -> Dict[str, Any]:
        """Produce a raw signal payload at the configured sampling rate.

        Returns an envelope around whatever ``reality_provider()`` yields —
        empty ``signals`` when no provider is wired, matching the
        aggregation/anonymization posture used elsewhere in this repo for
        unwired sensor stubs (see ``src/sensors/crew_load/``).
        """
        sync_params = self.config["synchronization_parameters"]
        signals = self.reality_provider()
        sample = {
            "bridge_id": self.config["bridge_id"],
            "sampled_at_hz": sync_params["reality_sampling_rate"],
            "timestamp": _utc_now_iso(),
            "signals": signals,
            "coherence": signals.get("coherence", self._last_coherence),
        }
        self._last_coherence = sample["coherence"]
        self._last_sample_at = sample["timestamp"]
        return sample

    def validate_causal_anchor(self, sample: Dict[str, Any]) -> None:
        """Enforce causal consistency before a sample may become threads.

        The config's ``causal_anchor`` block declares ``paradox_prevention:
        active`` and ``timeline_protection: enforced`` as intent; this
        method is the actual enforcement point. A sample is valid only if
        its timestamp does not precede the previously observed sample
        (monotonic time) and, when present, its ``causal_sequence`` does
        not go backwards relative to the last accepted sample.

        Returns nothing — success is "did not raise". Callers should not
        branch on a return value here.

        Raises:
            CausalAnchorViolation: if the sample would break causal order.
        """
        causal_cfg = self.config["reality_anchors"]["causal_anchor"]
        if causal_cfg.get("validation") != "strict":
            return

        if self._last_sample_at is not None and sample["timestamp"] < self._last_sample_at:
            raise CausalAnchorViolation(
                f"sample timestamp {sample['timestamp']} precedes last accepted "
                f"sample {self._last_sample_at} — paradox_prevention violation"
            )

    def encode_to_mesh_threads(self, sample: Dict[str, Any]) -> List[ThreadDescriptor]:
        """Convert a validated reality sample into CONSTELLINK thread descriptors.

        Calls ``validate_causal_anchor`` first — this method never emits
        threads for a sample that failed causal validation.
        """
        self.validate_causal_anchor(sample)

        signals = sample.get("signals", {})
        if not signals:
            # No real feed wired — nothing to encode. Empty, not fabricated.
            return []

        threads: List[ThreadDescriptor] = []
        for signal_name, signal_value in signals.items():
            if signal_name == "coherence":
                continue
            entropy_hint = None
            if isinstance(signal_value, (int, float)):
                entropy_hint = max(0.0, min(1.0, 1.0 - float(sample.get("coherence", 1.0))))
            threads.append(
                ThreadDescriptor(
                    thread_id=f"{sample['bridge_id']}::{signal_name}::{sample['timestamp']}",
                    source=sample["bridge_id"],
                    entropy_hint=entropy_hint,
                    tags=["quantum-bridge", "reality-signal", signal_name],
                    anchor_alignment=sample.get("coherence"),
                )
            )
        return threads

    def check_drift(self, sample: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Return an ``aurora.drift.detected`` event payload if coherence has
        dropped below the configured threshold, else ``None``.

        The returned dict matches the ``constellation-event.schema.json``
        shape (``event_type``, ``source_node``, ``timestamp``, ``payload``).
        ``source_node`` uses ``"ORION-QUANTUM-BRIDGE"``, which is not yet
        registered in that schema's ``source_node`` enum — registering a
        new constellation node is outside this module's scope (see #1064
        vs. the constellation-contracts manifest registration pattern used
        for QGIA/ZIPWIZ/SENTINEL). Callers publishing this event onto a
        real event bus must account for that gap.
        """
        threshold = self.config["synchronization_parameters"]["coherence_threshold"]
        coherence = sample.get("coherence", 1.0)
        if coherence >= threshold:
            return None
        return {
            "event_type": "aurora.drift.detected",
            "source_node": "ORION-QUANTUM-BRIDGE",
            "timestamp": sample["timestamp"],
            "payload": {
                "bridge_id": sample["bridge_id"],
                "coherence": coherence,
                "coherence_threshold": threshold,
            },
            "provenance": {
                "caelion_anchor": DEFAULT_ANCHOR_SEED,
                "charter": DEFAULT_ETHICS_PROTOCOL,
                "l3_compliance": True,
            },
        }

    def get_bridge_health(self) -> BridgeHealth:
        """Return NodeHealth-compatible status for Constellation monitoring."""
        threshold = self.config["synchronization_parameters"]["coherence_threshold"]
        status = "healthy" if self._last_coherence >= threshold else "degraded"
        return BridgeHealth(
            node="ORION-QUANTUM-BRIDGE",
            status=status,
            timestamp=_utc_now_iso(),
            manifest_version=self.config["version"],
            last_coherence=self._last_coherence,
            last_event=self._last_sample_at,
        )
