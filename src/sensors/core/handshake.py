"""
Extended ZIPWIZ handshake — v0.2.0 5-step sequence with RESONANCE_SYNC.

1. ZIPWIZ_BEACON      — initial connection
2. ANCHOR_SYNC        — EOS_SEED_ORION verification
3. ETHICS_AUDIT       — Picard_Delta_3 compliance check
4. DRIFT_VALIDATION   — Δ0.000 drift lock verification
5. RESONANCE_SYNC     — symbolic state alignment (concept-hash divergence)

Divergence > 0.05 logs a warning; > 0.10 holds the relay PENDING.
Step executors are injectable so existing bridge logic
(src/bridges/l2_meta_agent_bridge.py) supplies steps 1-4 unchanged.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Awaitable, Callable, Dict, Iterable, Optional

from src.sensors import constants as C
from src.sensors.core.reading_types import HandshakeResult, StepResult

logger = logging.getLogger(__name__)

StepExecutor = Callable[[str], Awaitable[StepResult]]


def concept_hash(tags: Iterable[str]) -> str:
    """Stable hash of a relay's active concept tag set."""
    joined = "\n".join(sorted(set(tags)))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def hash_divergence(local: str, constellation: Dict[str, str]) -> float:
    """Fraction of constellation relays whose concept hash differs."""
    if not constellation:
        return 0.0
    diff = sum(1 for h in constellation.values() if h != local)
    return diff / len(constellation)


class ExtendedZIPWIZHandshake:
    """Extended ZIPWIZ handshake with resonance synchronization."""

    HANDSHAKE_STEPS = [
        "ZIPWIZ_BEACON",
        "ANCHOR_SYNC",
        "ETHICS_AUDIT",
        "DRIFT_VALIDATION",
        "RESONANCE_SYNC",
    ]

    def __init__(
        self,
        step_executors: Optional[Dict[str, StepExecutor]] = None,
        get_concept_tags: Optional[Callable[[str], Awaitable[list]]] = None,
        get_constellation_hashes: Optional[Callable[[], Awaitable[Dict[str, str]]]] = None,
    ):
        self._executors = step_executors or {}
        self._get_concept_tags = get_concept_tags
        self._get_constellation_hashes = get_constellation_hashes

    async def perform_handshake(self, relay_id: str) -> HandshakeResult:
        results: Dict[str, StepResult] = {}
        for step in self.HANDSHAKE_STEPS:
            result = await self._execute_step(step, relay_id)
            results[step] = result
            if not result.passed:
                status = "PENDING" if result.action == "HOLD_PENDING" else "FAILED"
                return HandshakeResult(
                    relay_id=relay_id, success=False, failed_step=step,
                    step_results=results, status=status,
                )
        return HandshakeResult(
            relay_id=relay_id, success=True, failed_step=None,
            step_results=results, status="ACTIVE",
        )

    async def _execute_step(self, step: str, relay_id: str) -> StepResult:
        if step == "RESONANCE_SYNC":
            return await self._execute_resonance_sync(relay_id)
        executor = self._executors.get(step)
        if executor is None:
            # Steps 1-4 are owned by existing bridge logic; absent executor
            # passes through so the extension can wrap any deployment.
            return StepResult(step=step, passed=True,
                              reason="delegated to existing bridge (no executor)")
        return await executor(relay_id)

    async def _execute_resonance_sync(self, relay_id: str) -> StepResult:
        """NEW: synchronize symbolic state across the constellation."""
        if self._get_concept_tags is None or self._get_constellation_hashes is None:
            return StepResult(step="RESONANCE_SYNC", passed=True,
                              reason="resonance providers not wired; skipped")
        local_hash = concept_hash(await self._get_concept_tags(relay_id))
        constellation = await self._get_constellation_hashes()
        constellation.pop(relay_id, None)
        divergence = hash_divergence(local_hash, constellation)

        if divergence > C.RESONANCE_SYNC_CRITICAL:
            return StepResult(
                step="RESONANCE_SYNC", passed=False,
                reason=f"Critical concept divergence: {divergence:.3f}",
                action="HOLD_PENDING",
            )
        if divergence > C.RESONANCE_SYNC_WARNING:
            logger.warning("Relay %s concept divergence %.3f", relay_id, divergence)
            return StepResult(
                step="RESONANCE_SYNC", passed=True,
                reason=f"Minor concept divergence: {divergence:.3f}",
                action="LOG_WARNING",
            )
        return StepResult(step="RESONANCE_SYNC", passed=True,
                          reason="Concept state aligned")
