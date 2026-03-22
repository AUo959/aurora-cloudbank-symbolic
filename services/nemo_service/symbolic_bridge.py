"""
Aurora NeMo Service — Symbolic Bridge
# Symbolic Anchor: T1
# SRB: NEMO_SERVICE_v1
# DLP: [nemo, symbolic, bridge, entropy]
# Chain Notation: #SERVICES//NEMO//SYMBOLIC_BRIDGE//
# Ethics Protocol: Picard_Delta_3
# Anchor Seed: EOS_SEED_ORION

Bridge between the NeMo inference engine and Aurora's symbolic simulation
ecosystem.  Responsibilities:

- Anchor resolution and injection into inference context
- Entropy logging (per-call and periodic)
- Drift detection with flagging for downstream arbitration
- Memory sealing protocol hooks
"""

import hashlib
import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("nemo_service.symbolic_bridge")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class AnchorState:
    """
    Current T1/SRB symbolic anchor state.

    T1  — temporal anchor (monotonic call counter).
    SRB — spatial-relational boundary tag.
    """

    t1: int = 0
    srb: str = "NEMO_SERVICE_v1"
    anchor_seed: str = "EOS_SEED_ORION"
    ethics_protocol: str = "Picard_Delta_3"
    last_updated: float = field(default_factory=time.time)

    def advance(self) -> None:
        """Increment the T1 temporal anchor by one step."""
        self.t1 += 1
        self.last_updated = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the anchor state to a plain dict."""
        return {
            "t1": self.t1,
            "srb": self.srb,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "last_updated": self.last_updated,
        }


@dataclass
class EntropyReading:
    """A single entropy measurement taken during an inference pass."""

    call_index: int
    entropy_value: float
    model_type: str
    timestamp: float = field(default_factory=time.time)
    drift_flagged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict."""
        return {
            "call_index": self.call_index,
            "entropy_value": self.entropy_value,
            "model_type": self.model_type,
            "timestamp": self.timestamp,
            "drift_flagged": self.drift_flagged,
        }


# ---------------------------------------------------------------------------
# Symbolic Bridge
# ---------------------------------------------------------------------------


class SymbolicBridge:
    """
    Bridge between NeMo inference operations and the Aurora symbolic engine.

    Usage::

        bridge = SymbolicBridge(anchor_seed="EOS_SEED_ORION")
        ctx = bridge.resolve_anchor_context(model_type="llm")
        # ... run inference ...
        bridge.log_entropy(call_index=n, entropy=0.72, model_type="llm")
    """

    def __init__(
        self,
        anchor_seed: str = "EOS_SEED_ORION",
        srb_tag: str = "NEMO_SERVICE_v1",
        ethics_protocol: str = "Picard_Delta_3",
        drift_threshold: float = 0.15,
    ) -> None:
        """Initialise the symbolic bridge with anchor and entropy settings."""
        self._anchor = AnchorState(
            anchor_seed=anchor_seed,
            srb=srb_tag,
            ethics_protocol=ethics_protocol,
        )
        self._drift_threshold = drift_threshold
        self._entropy_history: List[EntropyReading] = []
        self._call_counter: int = 0
        self._baseline_entropy: Optional[float] = None

        logger.info(
            "SymbolicBridge initialised",
            extra={
                "anchor_seed": anchor_seed,
                "srb": srb_tag,
                "ethics_protocol": ethics_protocol,
                "chain_notation": "#SERVICES//NEMO//SYMBOLIC_BRIDGE//",
            },
        )

    # ------------------------------------------------------------------
    # Anchor management
    # ------------------------------------------------------------------

    def resolve_anchor_context(self, model_type: str) -> Dict[str, Any]:
        """
        Advance the T1 anchor and return the current anchor context dict.

        This context should be embedded in inference requests and responses
        for full symbolic traceability.
        """
        self._anchor.advance()
        self._call_counter += 1

        ctx = {
            "chain_notation": f"#SERVICES//NEMO//{model_type.upper()}//T1:{self._anchor.t1}//",
            **self._anchor.to_dict(),
            "call_counter": self._call_counter,
        }

        logger.debug("Anchor context resolved: T1=%d SRB=%s", self._anchor.t1, self._anchor.srb)
        return ctx

    def get_anchor_state(self) -> Dict[str, Any]:
        """Return the current anchor state without advancing it."""
        return self._anchor.to_dict()

    # ------------------------------------------------------------------
    # Entropy logging
    # ------------------------------------------------------------------

    def log_entropy(
        self,
        call_index: int,
        entropy: float,
        model_type: str,
    ) -> EntropyReading:
        """
        Record an entropy reading and detect drift against the baseline.

        If no baseline has been set yet the first reading becomes the
        baseline.  Subsequent readings are compared against the baseline
        and flagged if the absolute delta exceeds the configured threshold.

        # Drift detection: Flag divergent states for downstream arbitration
        """
        if self._baseline_entropy is None:
            self._baseline_entropy = entropy
            logger.info("Entropy baseline established: %.4f", entropy)

        drift = abs(entropy - self._baseline_entropy)
        drift_flagged = drift > self._drift_threshold

        reading = EntropyReading(
            call_index=call_index,
            entropy_value=entropy,
            model_type=model_type,
            drift_flagged=drift_flagged,
        )
        self._entropy_history.append(reading)

        if drift_flagged:
            logger.warning(
                "Entropy drift detected — delta=%.4f threshold=%.4f",
                drift,
                self._drift_threshold,
                extra={"event": "entropy_drift", "drift_delta": drift},
            )
        else:
            logger.debug("Entropy logged: %.4f (delta=%.4f)", entropy, drift)

        return reading

    def compute_entropy(self, logits: List[float]) -> float:
        """
        Compute Shannon entropy from a list of raw logit values.

        Converts logits to a normalised probability distribution before
        computing H = -Σ p(x) log p(x).
        """
        if not logits:
            return 0.0

        # Softmax normalisation
        max_logit = max(logits)
        exps = [math.exp(v - max_logit) for v in logits]
        total = sum(exps)
        probs = [e / total for e in exps]

        return -sum(p * math.log(p + 1e-12) for p in probs)

    def get_entropy_history(self) -> List[Dict[str, Any]]:
        """Return the full entropy history as a list of dicts."""
        return [r.to_dict() for r in self._entropy_history]

    def get_latest_entropy(self) -> Optional[Dict[str, Any]]:
        """Return the most recent entropy reading, or None if empty."""
        if not self._entropy_history:
            return None
        return self._entropy_history[-1].to_dict()

    # ------------------------------------------------------------------
    # Memory sealing
    # ------------------------------------------------------------------

    def seal_context(self, payload: Dict[str, Any]) -> str:
        """
        Compute a SHA256 seal over a serialised context payload.

        Returns the hex digest string.  This should be recorded alongside
        every state snapshot for continuity verification.
        """
        import json

        serialised = json.dumps(payload, sort_keys=True, default=str)
        seal = hashlib.sha256(serialised.encode()).hexdigest()
        logger.debug("Context sealed: %s…", seal[:16])
        return seal

    # ------------------------------------------------------------------
    # Summary / introspection
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return a full bridge summary suitable for the /nemo/status endpoint."""
        return {
            "anchor": self._anchor.to_dict(),
            "call_counter": self._call_counter,
            "baseline_entropy": self._baseline_entropy,
            "entropy_readings": len(self._entropy_history),
            "drift_threshold": self._drift_threshold,
            "latest_entropy": self.get_latest_entropy(),
            "srb": self._anchor.srb,
            "ethics_protocol": self._anchor.ethics_protocol,
            "chain_notation": "#SERVICES//NEMO//SYMBOLIC_BRIDGE//",
        }
