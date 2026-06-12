"""Sensor discovery and registration."""

from __future__ import annotations

import logging
import threading
from typing import Dict, List, Optional

from src.sensors.core.sensor_base import Sensor

logger = logging.getLogger(__name__)


class SensorRegistry:
    """Central registry; lookup by id, layer, category, or phase tap."""

    def __init__(self):
        self._sensors: Dict[str, Sensor] = {}
        self._phase_taps: Dict[str, List[str]] = {}  # phase_id -> [sensor_id]
        self._lock = threading.Lock()

    def register(self, sensor: Sensor, phases: Optional[List[str]] = None) -> None:
        with self._lock:
            if sensor.sensor_id in self._sensors:
                raise ValueError(f"Duplicate sensor_id: {sensor.sensor_id}")
            self._sensors[sensor.sensor_id] = sensor
            for phase in phases or []:
                self._phase_taps.setdefault(phase, []).append(sensor.sensor_id)
        logger.debug("Registered sensor %s (phases=%s)", sensor.sensor_id, phases)

    def get(self, sensor_id: str) -> Optional[Sensor]:
        return self._sensors.get(sensor_id)

    def all(self) -> List[Sensor]:
        return list(self._sensors.values())

    def by_layer(self, layer: str) -> List[Sensor]:
        return [s for s in self._sensors.values()
                if (s.layer.value if hasattr(s.layer, "value") else s.layer) == layer]

    def by_category(self, category: str) -> List[Sensor]:
        return [s for s in self._sensors.values() if s.category == category]

    def for_phase(self, phase_id: str) -> List[Sensor]:
        """Sensors tapped at a given tick phase (spec Phase→Sensor Tap Map)."""
        ids = self._phase_taps.get(phase_id, [])
        return [self._sensors[i] for i in ids if self._sensors[i].enabled]

    def enabled(self) -> List[Sensor]:
        return [s for s in self._sensors.values() if s.enabled]
