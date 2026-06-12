"""
All sensor reading dataclasses — spec §reading_types.py.

Nested dataclasses from the spec are flattened to module level (the spec's
inline nesting is illustrative, not importable). Names preserved.

Unit discipline: every numeric field whose scale could be confused carries an
explicit ``MetricUnit`` either structurally (field name) or via
``SensorReading.units``. DRIFT_DELTA and DEVIATION_FRACTION are different
scales measuring different things (spec §Repository Alignment Notes).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple


class Layer(str, Enum):
    """Source layer for a signal or sensor."""
    L1 = "L1"   # physical reality / platform
    L2 = "L2"   # simulation state
    L3 = "L3"   # symbolic / narrative / governance
    CROSS = "CROSS"


class MetricUnit(str, Enum):
    """Explicit unit labels — mandatory on dashboards and alert routing."""
    DRIFT_DELTA = "drift_delta"                  # Δ scale, threshold 0.002
    DEVIATION_FRACTION = "deviation_fraction"    # 0.2/0.5/0.8 scale
    RATIO = "ratio"                              # generic 0-1
    COUNT = "count"
    SECONDS = "seconds"
    PER_HOUR = "per_hour"
    CELSIUS = "celsius"
    PERCENT = "percent"


@dataclass
class SensorSignal:
    """Raw signal emitted by a sensor onto the data bus."""
    sensor_id: str
    source_layer: str                            # Layer value
    category: str
    name: str
    value: float
    unit: MetricUnit
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InterpretedSignal:
    """Layer-contextualized signal (output of LayerInterpreter)."""
    signal: SensorSignal
    context: str                                 # e.g. "physical_reality"
    literal: bool                                # L1 literal; L3 may be metaphor
    actionable: bool                             # L3 informs, L1 acts
    cross_layer_implications: List[str] = field(default_factory=list)


@dataclass
class SensorReading:
    """Generic reading: a batch of named values from one sensor pass."""
    sensor_id: str
    timestamp: datetime
    layer: str
    category: str
    values: Dict[str, float] = field(default_factory=dict)
    units: Dict[str, MetricUnit] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Symbolic observatory readings
# --------------------------------------------------------------------------

@dataclass
class ResonanceEvent:
    event_id: str
    concept: str                                 # resonating concept/theme
    source_layer: str                            # where it originated
    echo_locations: List[str]                    # where it appeared
    semantic_similarity: float                   # 0-1
    classification: Literal["convergence", "bleed", "uncertain"]
    first_observed: datetime
    frequency: int


@dataclass
class ConceptResonanceReading:
    timestamp: datetime
    observation_window_seconds: int
    resonances: List[ResonanceEvent]
    resonance_count: int
    narrative_convergences: List[str]            # positive: story aligning
    metaphor_bleeds: List[str]                   # concerning: layer crossing
    resonance_intensity: float                   # 0-1 cross-layer echo
    bleed_risk: float                            # 0-1


@dataclass
class EthicalWarning:
    warning_id: str
    warning_type: str                            # tone|boundary|accumulation|pattern
    severity: Literal["advisory", "caution", "warning", "critical"]
    description: str
    evidence: List[str]
    suggested_response: str


@dataclass
class EthicalSignalReading:
    timestamp: datetime
    observation_window_seconds: int
    entity_id: str
    risk_score: float                            # 0-1 (sentinel scale)
    risk_trend: Literal["decreasing", "stable", "increasing", "accelerating"]
    risk_velocity: float                         # change per hour
    tone_escalation: float
    boundary_testing: float
    rule_deviation_accumulation: float
    warnings: List[EthicalWarning]
    intervention_recommended: bool
    recommended_action: Optional[str]            # recommendation ONLY —
    # MonitoringSystem / L3 governance own the action (one-way observation)


@dataclass
class PreSignature:
    signature_id: str
    signature_type: str          # hash_instability|timing_drift|state_divergence|snapshot_drift
    magnitude: float
    location: str
    first_detected: datetime
    predicted_impact: str


@dataclass
class WeightedPreSignature(PreSignature):
    """v0.3.0: integration-depth-weighted pre-signature (Lotus §IV)."""
    depth_weight: float = 0.0                    # SII depth of affected symbol(s)
    priority: float = 0.0                        # magnitude * (0.3 + 0.7*depth)
    classification: Literal["rupture", "drift", "peripheral_noise"] = "drift"


@dataclass
class DriftPreSignatureReading:
    timestamp: datetime
    current_drift_delta: float                   # unit: DRIFT_DELTA
    drift_threshold: float
    headroom: float
    drift_velocity: float                        # Δ/hour
    time_to_threshold_hours: Optional[float]
    trend: Literal["converging", "stable", "diverging", "critical"]
    pre_signatures: List[PreSignature]
    anchor_hash_stability: float
    snapshot_diff_magnitude: float
    cross_relay_divergence: float
    micro_corrections_1h: int
    correction_effectiveness: float


@dataclass
class IntegrationDepthReading:
    """v0.3.0: snapshot of integration depth across the symbol graph."""
    timestamp: datetime
    symbol_count: int
    depths: Dict[str, float]                     # symbol_id -> depth (0-1)
    core_symbols: List[str]                      # depth >= 0.8
    peripheral_symbols: List[str]                # depth < 0.2
    median_depth: float
    depth_deltas_1h: Dict[str, float]
    rupture_candidates: List[str]


# --------------------------------------------------------------------------
# Fusion readings
# --------------------------------------------------------------------------

@dataclass
class PrecursorPattern:
    """RQ-2: canon-like artifact with hash identity and evidence requirement."""
    pattern_id: str
    anomaly_type: str
    signals: List[str]
    confidence: float
    typical_eta_seconds: float
    status: Literal["staged", "live", "retired"] = "live"
    pattern_hash: Optional[str] = None
    provenance: Dict[str, str] = field(default_factory=dict)  # incident/author/date
    backtest_precision: Optional[float] = None
    low_n: bool = False


@dataclass
class AnomalyForecast:
    forecast_id: str
    timestamp: datetime
    anomaly_type: Literal["drift", "ethics", "resonance", "structural", "containment"]
    probability: float
    predicted_eta_seconds: float
    confidence: float
    contributing_signals: List[str]
    pattern_matched: Optional[str]
    trajectory: str                              # accelerating|linear|decelerating
    recommended_intervention: str
    intervention_urgency: Literal["immediate", "soon", "monitor", "none"]
    anchor: str = "EOS_SEED_ORION"
    ethics_cleared: bool = True
    # v0.3.0 AFS alignment (Forecast Question Module, PK-04 C5):
    resolution_criteria: Optional[str] = None
    confidence_interval: Optional[Tuple[float, float]] = None


@dataclass
class OscillationHealthReading:
    timestamp: datetime
    observation_window_seconds: int
    corrections_per_hour: float
    correction_frequency_trend: Literal["decreasing", "stable", "increasing"]
    avg_correction_magnitude: float
    magnitude_trend: Literal["shrinking", "stable", "growing"]
    same_direction_streak: int
    direction_alternation_rate: float
    drift_after_correction: float
    correction_success_rate: float
    oscillation_healthy: bool
    oscillation_risk: Literal["none", "low", "medium", "high"]
    diagnosis: str
    # v0.3.0 Convergence Regulator coupling:
    regulator_share: float = 0.0                 # fraction regulator-intentional


@dataclass
class ResonanceReading:
    """Cross-layer resonance measurement."""
    timestamp: datetime
    l1_l2_resonance: float
    l2_l3_resonance: float
    l1_l3_resonance: float
    system_resonance: float                      # harmonic mean
    dissonance_detected: bool
    dissonance_locations: List[str]
    dissonance_severity: float


@dataclass
class CoherenceCertification:
    """System-wide coherence certification — the final verdict."""
    timestamp: datetime
    certification_id: str
    system_coherent: bool
    confidence: float
    structural_coherence: float
    operational_coherence: float
    symbolic_coherence: float
    temporal_coherence: float
    layer_resonance: float
    reality_grounding: float
    anchor_verified: bool
    anchor_id: str                               # EOS_SEED_ORION
    ethics_protocol: str                         # Picard_Delta_3
    blocking_issues: List[str]
    advisory_issues: List[str]
    certified_by: str
    verification_hash: str
    previous_certification_id: Optional[str]


# --------------------------------------------------------------------------
# Handshake (Phase 3, declared here so reading_types is the single source)
# --------------------------------------------------------------------------

@dataclass
class StepResult:
    step: str
    passed: bool
    reason: str = ""
    action: Optional[str] = None


@dataclass
class HandshakeResult:
    relay_id: str
    success: bool
    failed_step: Optional[str]
    step_results: Dict[str, StepResult]
    status: str                                  # ACTIVE|FAILED|PENDING
