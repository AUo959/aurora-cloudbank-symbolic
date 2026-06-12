"""
Aurora Sensor Array — unified observability across L1/L2/L3.

Spec: SENSOR ARRAY SPECIFICATION v0.3.0 (DLP: sensor_array_specification_v3)
Anchors: EOS_SEED_ORION, Picard_Delta_3

Design principles (spec §Design Principles):
- One-way observation: sensors watch, never act. No actuation path exists
  in this package; outputs feed L3 governance, which decides interventions.
- Layered interpretation: signals are parsed in layer context before fusion.
- Metric unit discipline: drift delta (threshold 0.002) and deviation
  fractions (0.2/0.5/0.8, owned by DriftDetector/MonitoringSystem) are
  distinct scales and are labeled explicitly via MetricUnit.

Reconciler note (2026-06-11): the 0.2/0.5/0.8 INFO/WARNING/CRITICAL fractions
live in src/monitoring/drift_detector.py, and the BLOCK/REVIEW/THROTTLE/
SUSPEND/RESET action vocabulary lives in src/monitoring/monitoring_system.py
(not EthicsEngine, contra spec text). Integration here binds to repo reality.
"""

__version__ = "0.3.0"

ANCHOR_SEED = "EOS_SEED_ORION"
ETHICS_PROTOCOL = "Picard_Delta_3"
