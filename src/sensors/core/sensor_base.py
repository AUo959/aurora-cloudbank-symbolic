"""
Sensor base classes and the RollingWindow time-series utility.

One-way observation is enforced structurally: ``Sensor.ingest`` receives
read-only views and ``Sensor.read`` returns a reading; there is no method on
any sensor that mutates external state. Sensors that need engine access get
frozen ``GUMASStateView`` snapshots (Phase 7), never live state.
"""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Deque, Dict, Iterator, List, Optional

from src.sensors.core.reading_types import Layer, SensorReading

logger = logging.getLogger(__name__)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RollingWindow:
    """Time-bounded append-only window used by every sensor in the spec.

    Items are dicts that must carry a ``timestamp`` (timezone-aware datetime).
    Items older than ``window_seconds`` are evicted lazily on access.
    Thread-safe for the in-process observer default (spec open question #4).
    """

    def __init__(self, window_seconds: int, maxlen: Optional[int] = None):
        self.window_seconds = window_seconds
        self._items: Deque[Dict[str, Any]] = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def append(self, item: Dict[str, Any]) -> None:
        if "timestamp" not in item:
            item = {**item, "timestamp": utcnow()}
        with self._lock:
            self._items.append(item)

    def _evict(self) -> None:
        cutoff = utcnow() - timedelta(seconds=self.window_seconds)
        while self._items and self._items[0]["timestamp"] < cutoff:
            self._items.popleft()

    def items(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._evict()
            return list(self._items)

    def __len__(self) -> int:
        with self._lock:
            self._evict()
            return len(self._items)

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        return iter(self.items())


class Sensor(ABC):
    """Abstract sensor. Watchers, not actors.

    Subclasses implement ``read()`` to produce a reading from accumulated
    observations, and optionally ``ingest()`` to accept streamed inputs
    (phase taps, agent outputs, action records).
    """

    #: PerformanceBudget key for this sensor's read operation.
    budget_key: str = "internal_sensor"

    def __init__(self, sensor_id: str, layer: Layer, category: str):
        self.sensor_id = sensor_id
        self.layer = layer
        self.category = category
        self.enabled = True
        #: Rupture-class sensors are never decimated (spec §Per-Tick Budget).
        self.critical = False

    def ingest(self, source: str, payload: Dict[str, Any]) -> None:  # noqa: B027
        """Accept a streamed observation. Default: no-op (intentionally
        non-abstract — pull-only sensors need no stream input)."""

    @abstractmethod
    def read(self) -> SensorReading:
        """Produce the current reading. MUST NOT mutate external state."""

    def _reading(
        self,
        values: Dict[str, float],
        units: Optional[Dict[str, Any]] = None,
        alerts: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SensorReading:
        return SensorReading(
            sensor_id=self.sensor_id,
            timestamp=utcnow(),
            layer=self.layer.value if isinstance(self.layer, Layer) else self.layer,
            category=self.category,
            values=values,
            units=units or {},
            alerts=alerts or [],
            metadata=metadata or {},
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} {self.sensor_id} [{self.layer}/{self.category}]>"


@dataclass
class MetricSpec:
    """Declarative metric: where it comes from and when it alerts."""
    name: str
    unit: Any                                     # MetricUnit
    alert_when: Optional[Callable[[float], bool]] = None
    alert_message: str = ""
    default: float = 0.0


class ProviderSensor(Sensor):
    """Threshold sensor driven by a metrics-provider callable.

    ``provider()`` returns ``{metric_name: value}``; missing metrics fall back
    to each spec's default. Wiring to real monitoring surfaces (R-2 telemetry,
    MonitoringSystem, subsystem validate_state) happens by swapping providers —
    the sensor itself never reaches into engine state.
    """

    def __init__(
        self,
        sensor_id: str,
        layer: Layer,
        category: str,
        metrics: List[MetricSpec],
        provider: Optional[Callable[[], Dict[str, float]]] = None,
    ):
        super().__init__(sensor_id, layer, category)
        self.metrics = metrics
        self.provider = provider or (lambda: {})

    def read(self) -> SensorReading:
        raw = self.provider() or {}
        values: Dict[str, float] = {}
        units: Dict[str, Any] = {}
        alerts: List[str] = []
        for m in self.metrics:
            v = float(raw.get(m.name, m.default))
            values[m.name] = v
            units[m.name] = m.unit
            if m.alert_when is not None and m.alert_when(v):
                alerts.append(m.alert_message or f"{m.name} threshold breach: {v}")
        return self._reading(values, units=units, alerts=alerts)
