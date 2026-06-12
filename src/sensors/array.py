"""
SensorArrayFacade — assembles the full array and backs the API router.

Wiring only; no behavior of its own. Construction order mirrors the data
flow: sensors -> interpreter -> bus -> fusion -> certification.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from src.sensors import constants as C
from src.sensors.core.data_bus import SensorDataBus
from src.sensors.core.layer_interpreter import LayerInterpreter
from src.sensors.core.performance_budget import PerformanceBudget
from src.sensors.core.reading_types import (
    AnomalyForecast,
    CoherenceCertification,
    SensorReading,
)
from src.sensors.core.sensor_registry import SensorRegistry
from src.sensors.external import (
    AstronomicalSensor,
    CommunicationsSensor,
    DeepSpaceSensor,
    ProximitySensor,
    SalvageSensor,
)
from src.sensors.fusion import (
    CoherenceCertifier,
    CrossLayerResonanceCalculator,
    FusionPredictor,
    OscillationHealthMonitor,
    RegulatorMarkerConsumer,
)
from src.sensors.internal import (
    BiometricsSensor,
    EnvironmentalSensor,
    OperationalSensor,
    StructuralSensor,
)
from src.sensors.observatory.physical import (
    BoundarySensor,
    ContainmentSensor,
    EarthRelaySensor,
    FidelitySensor,
    RealityAnchorSensor,
)
from src.sensors.observatory.symbolic import (
    ConceptResonanceDetector,
    DriftPreSignatureMonitor,
    EthicalSignalSentinel,
    SymbolIntegrationIndex,
)

logger = logging.getLogger(__name__)

Provider = Callable[[], Dict[str, float]]


class SensorArrayFacade:
    """Single composition root for the sensor array."""

    def __init__(
        self,
        providers: Optional[Dict[str, Provider]] = None,
        ethics_engine: Optional[Any] = None,
        drift_detector: Optional[Any] = None,
        canonical_tags: Optional[set] = None,
    ):
        p = providers or {}
        self.bus = SensorDataBus()
        self.interpreter = LayerInterpreter()
        self.budget = PerformanceBudget()
        self.registry = SensorRegistry()

        # Symbolic infrastructure (v0.3.0)
        self.sii = SymbolIntegrationIndex()
        self.concept_resonance = ConceptResonanceDetector(canonical_tags)
        self.concept_resonance.sii = self.sii
        self.ethical_signal = EthicalSignalSentinel(ethics_engine)
        self.drift_presig = DriftPreSignatureMonitor(
            drift_detector=drift_detector, sii=self.sii)

        # Salvage survey (push-fed from the root control plane's
        # aurora_salvage_scan report; see sensor docstring)
        self.salvage = SalvageSensor()

        # Physical sensors
        self._sensors = [
            self.salvage,
            EnvironmentalSensor(p.get("environmental")),
            StructuralSensor(p.get("structural")),
            BiometricsSensor(p.get("biometrics")),
            OperationalSensor(p.get("operational")),
            ProximitySensor(p.get("proximity")),
            DeepSpaceSensor(p.get("deep_space")),
            AstronomicalSensor(p.get("astronomical")),
            CommunicationsSensor(p.get("communications")),
            ContainmentSensor(p.get("containment")),
            FidelitySensor(p.get("fidelity")),
            BoundarySensor(p.get("boundary")),
            RealityAnchorSensor(p.get("reality_anchor")),
            EarthRelaySensor(p.get("earth_relay")),
            self.concept_resonance,
            self.ethical_signal,
            self.drift_presig,
        ]
        for s in self._sensors:
            self.registry.register(s)

        # Fusion
        self.marker_consumer = RegulatorMarkerConsumer(self.bus)
        self.oscillation = OscillationHealthMonitor(self.marker_consumer)
        self.predictor = FusionPredictor()
        self.resonance_calc = CrossLayerResonanceCalculator()
        self.certifier = CoherenceCertifier()

    # -- API surface (backs src/sensors/api/routes.py) ---------------------------

    def read_category(self, group: str, category: str) -> Optional[SensorReading]:
        matches = self.registry.by_category(category)
        if not matches:
            return None
        with self.budget.timed_operation(matches[0].budget_key):
            reading = matches[0].read()
        self.bus.publish(f"sensors.{group}.{category}",
                         {"reading": reading, "timestamp": reading.timestamp})
        return reading

    def concept_resonance_reading(self):
        with self.budget.timed_operation("concept_resonance"):
            return self.concept_resonance.detect_resonance()

    def ethical_signal_reading(self, entity_id: Optional[str] = None):
        reading = self.ethical_signal.read()
        if entity_id is not None:
            return {"entity_id": entity_id,
                    "risk_score": self.ethical_signal.risk_scores.get(entity_id, 0.0)}
        return reading

    def drift_presignature(self):
        with self.budget.timed_operation("drift_presig"):
            return self.drift_presig.analyze()

    def integration_depth(self):
        with self.budget.timed_operation("sii_update"):
            return self.sii.snapshot()

    def fusion_resonance(self):
        with self.budget.timed_operation("fusion_correlation"):
            return self.resonance_calc.calculate()

    def oscillation_health(self):
        return self.oscillation.analyze()

    def forecasts(self, anomaly_type: Optional[str] = None) -> List[AnomalyForecast]:
        with self.budget.timed_operation("fusion_prediction"):
            out = self.predictor.forecast()
        if anomaly_type:
            out = [f for f in out if f.anomaly_type == anomaly_type]
        return out

    def certification(self) -> CoherenceCertification:
        with self.budget.timed_operation("coherence_certification"):
            sii_snap = self.sii.snapshot()
            resonance = self.resonance_calc.calculate()
            drift = self.drift_presig.analyze()

            def score(category: str) -> float:
                sensors = self.registry.by_category(category)
                if not sensors:
                    return 1.0
                reading = sensors[0].read()
                return 0.5 if reading.alerts else 1.0

            symbolic = 1.0 - min(
                len(sii_snap.rupture_candidates) * 0.5, 1.0)
            anchor_ok = True
            anchor_sensors = self.registry.by_category("reality_anchor")
            if anchor_sensors:
                anchor_ok = not anchor_sensors[0].read().alerts

            return self.certifier.certify(
                structural=score("structural"),
                operational=score("operational"),
                symbolic=symbolic,
                temporal=score("fidelity"),
                layer_resonance=resonance.system_resonance,
                reality_grounding=1.0 if anchor_ok else 0.0,
                anchor_verified=anchor_ok,
                advisory_issues=(
                    [f"drift trend: {drift.trend}"]
                    if drift.trend in ("diverging", "critical") else []),
                rupture_candidates=sii_snap.rupture_candidates,
            )

    def health_status(self) -> Dict[str, Any]:
        return {
            "sensors_registered": len(self.registry.all()),
            "sensors_enabled": len(self.registry.enabled()),
            "bus_archive_depth": len(self.bus),
            "budget_violations": len(self.budget.violations),
            "decimation_n": self.budget.decimation_n,
        }

    def performance(self) -> Dict[str, Any]:
        return {
            "budgets": dict(self.budget.BUDGETS),
            "violations": [
                {"operation": v.operation_type,
                 "elapsed_s": v.elapsed_seconds,
                 "budget_s": v.budget_seconds}
                for v in self.budget.violations[-50:]
            ],
            "tick_budget_fraction": C.TICK_BUDGET_FRACTION,
        }
