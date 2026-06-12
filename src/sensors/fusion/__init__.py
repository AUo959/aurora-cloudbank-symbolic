"""Fusion core: correlation, prediction, oscillation health, certification."""

from src.sensors.fusion.certification import CoherenceCertifier
from src.sensors.fusion.oscillation import (
    OscillationHealthMonitor,
    RegulatorMarkerConsumer,
)
from src.sensors.fusion.predictor import FusionPredictor, default_pattern_library
from src.sensors.fusion.resonance import CrossLayerResonanceCalculator

__all__ = [
    "CoherenceCertifier",
    "CrossLayerResonanceCalculator",
    "FusionPredictor",
    "OscillationHealthMonitor",
    "RegulatorMarkerConsumer",
    "default_pattern_library",
]
