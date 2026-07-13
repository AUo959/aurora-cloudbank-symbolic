"""PROJECT SENTINEL Stream 1 — async biometric data ingestion interface (stub).

Defines the ingestion boundary between a future real-time biometric feed
(Dr. Vasquez / Medical division) and ``CognitiveLoadMonitor``'s provider
callable. No transport (websocket, MQTT, device SDK, etc.) is implemented —
this stub only fixes the shape so the real feed can be wired later without
changing the sensor side.

Layer-boundary constraint (see SENTINEL_ARCHITECTURE.md): implementations
must emit aggregated/anonymized values by default. Individual-level
biometric identity must never be attached to a value that flows into a
performance-evaluation surface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict


class BiometricStreamSource(ABC):
    """Abstract async source of aggregated crew biometric signals.

    A concrete implementation (not part of this stub) would poll or
    subscribe to the real Medical-division feed and normalize readings
    into the metric names ``CognitiveLoadMonitor`` expects
    (``hrv_rmssd_ms``, ``cortisol_proxy_index``, ``aggregate_load_score``).
    """

    @abstractmethod
    async def read_latest(self) -> Dict[str, float]:
        """Return the latest aggregated metric snapshot.

        Must return an empty dict rather than raise when no data is
        available yet — sensors fall back to each metric's default.
        """
        raise NotImplementedError


class NullBiometricStream(BiometricStreamSource):
    """No-op stream used until a real feed is wired. Always empty."""

    async def read_latest(self) -> Dict[str, float]:
        return {}
