"""
Sensor Data Bus — unified event stream with bounded archive.

Pub/sub for fusion consumers plus a time-indexed archive supporting:
- RQ-2 T-minus window extraction for post-incident pattern authoring,
- RQ-3 rolling-origin backtesting,
- the AFS Feature Store adapter (Phase 7).

Subscribers must be observers only. Publishing is sensor-side; nothing on the
bus has a path back into engine or platform state (one-way observation).
"""

from __future__ import annotations

import logging
import threading
from collections import deque
from datetime import datetime, timedelta
from typing import Any, Callable, Deque, Dict, List, Optional

from src.sensors.core.sensor_base import utcnow

logger = logging.getLogger(__name__)

BusListener = Callable[[str, Dict[str, Any]], None]

#: Topic for Convergence Regulator intentional-perturbation markers
#: (v0.3.0 §Convergence Regulator Coupling; exact schema = open question #2).
TOPIC_REGULATOR_MARKER = "regulator.intentional_perturbation"


class SensorDataBus:
    """In-memory topic bus with a bounded, time-queryable archive."""

    def __init__(self, archive_maxlen: int = 100_000):
        self._subscribers: Dict[str, List[BusListener]] = {}
        self._archive: Deque[Dict[str, Any]] = deque(maxlen=archive_maxlen)
        self._lock = threading.Lock()

    def subscribe(self, topic: str, listener: BusListener) -> None:
        with self._lock:
            self._subscribers.setdefault(topic, []).append(listener)

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        event = {
            "topic": topic,
            "payload": payload,
            "timestamp": payload.get("timestamp") or utcnow(),
        }
        with self._lock:
            self._archive.append(event)
            listeners = list(self._subscribers.get(topic, [])) + \
                list(self._subscribers.get("*", []))
        for listener in listeners:
            try:
                listener(topic, payload)
            except Exception:  # noqa: BLE001 — listener faults never propagate
                logger.exception("Bus listener failed for topic %s", topic)

    # -- archive queries -----------------------------------------------------

    def window(
        self,
        seconds: float,
        topic: Optional[str] = None,
        until: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Events in the trailing window; ``until`` enables T-minus extraction."""
        end = until or utcnow()
        start = end - timedelta(seconds=seconds)
        with self._lock:
            return [
                e for e in self._archive
                if start <= e["timestamp"] <= end
                and (topic is None or e["topic"] == topic)
            ]

    def __len__(self) -> int:
        return len(self._archive)
