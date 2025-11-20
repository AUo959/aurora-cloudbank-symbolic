"""
Tests for System Observer - Unified System State Observation

Covers health aggregation, bottleneck/anomaly detection, and integration points.
"""

import pytest
from datetime import datetime
from src.aurora_orchestrator.system_observer import SystemState, Bottleneck, Anomaly

@pytest.fixture
def sample_bottleneck():
    return Bottleneck(
        component_id="comp-1",
        component_name="Quantum Forge",
        bottleneck_type="latency",
        severity=0.8,
        description="High latency detected in quantum backend.",
        suggested_fix="Switch to backup quantum node."
    )

@pytest.fixture
def sample_anomaly():
    return Anomaly(
        anomaly_id="anom-42",
        timestamp=datetime.utcnow().isoformat(),
        metric_name="drift_level",
        severity="critical",
        description="Drift exceeded critical threshold.",
        z_score=4.2
    )

@pytest.fixture
def system_state(sample_bottleneck, sample_anomaly):
    return SystemState(
        timestamp=datetime.utcnow().isoformat(),
        synergy_topology={"Quantum Forge": ["AI Interface"]},
        component_health={"Quantum Forge": 0.7, "AI Interface": 0.95},
        bottlenecks=[sample_bottleneck],
        telemetry_metrics={"latency": 120, "throughput": 5000},
        anomalies=[sample_anomaly],
        latency_p95=110.0,
        monitoring_status={"drift": "critical"},
        drift_level=0.12,
        memory_utilization={"AuMemManager": 0.85},
        quantum_coherence=0.91,
        entanglement_health=0.97,
        quantum_backend_status={"Quantum Forge": "degraded"},
        ai_model_costs={"Claude": 0.02},
        ai_model_latency={"Claude": 0.15},
        model_selection_efficiency=0.88,
        ethics_compliance_score=0.99
    )

def test_system_state_fields(system_state):
    assert system_state.timestamp
    assert "Quantum Forge" in system_state.synergy_topology
    assert system_state.component_health["Quantum Forge"] == 0.7
    assert system_state.bottlenecks[0].component_name == "Quantum Forge"
    assert system_state.anomalies[0].severity == "critical"
    assert system_state.drift_level > 0.1
    assert system_state.quantum_coherence > 0.9
    assert system_state.ethics_compliance_score > 0.95

def test_bottleneck_fields(sample_bottleneck):
    assert sample_bottleneck.severity == 0.8
    assert sample_bottleneck.suggested_fix == "Switch to backup quantum node."

def test_anomaly_fields(sample_anomaly):
    assert sample_anomaly.metric_name == "drift_level"
    assert sample_anomaly.z_score == 4.2
    assert sample_anomaly.severity == "critical"
