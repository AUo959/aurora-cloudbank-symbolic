"""Sensor array core: types, base classes, registry, bus, interpreter, budget."""

from src.sensors.core.data_bus import SensorDataBus, TOPIC_REGULATOR_MARKER
from src.sensors.core.layer_interpreter import LayerInterpreter
from src.sensors.core.performance_budget import BudgetViolation, PerformanceBudget
from src.sensors.core.reading_types import (
    AnomalyForecast,
    CoherenceCertification,
    ConceptResonanceReading,
    DriftPreSignatureReading,
    EthicalSignalReading,
    EthicalWarning,
    HandshakeResult,
    IntegrationDepthReading,
    InterpretedSignal,
    Layer,
    MetricUnit,
    OscillationHealthReading,
    PrecursorPattern,
    PreSignature,
    ResonanceEvent,
    ResonanceReading,
    SensorReading,
    SensorSignal,
    StepResult,
    WeightedPreSignature,
)
from src.sensors.core.sensor_base import (
    MetricSpec,
    ProviderSensor,
    RollingWindow,
    Sensor,
    utcnow,
)
from src.sensors.core.sensor_registry import SensorRegistry

__all__ = [
    "AnomalyForecast",
    "BudgetViolation",
    "CoherenceCertification",
    "ConceptResonanceReading",
    "DriftPreSignatureReading",
    "EthicalSignalReading",
    "EthicalWarning",
    "HandshakeResult",
    "IntegrationDepthReading",
    "InterpretedSignal",
    "Layer",
    "LayerInterpreter",
    "MetricSpec",
    "MetricUnit",
    "OscillationHealthReading",
    "PerformanceBudget",
    "ProviderSensor",
    "PrecursorPattern",
    "PreSignature",
    "ResonanceEvent",
    "ResonanceReading",
    "RollingWindow",
    "Sensor",
    "SensorDataBus",
    "SensorReading",
    "SensorRegistry",
    "SensorSignal",
    "StepResult",
    "TOPIC_REGULATOR_MARKER",
    "WeightedPreSignature",
    "utcnow",
]
