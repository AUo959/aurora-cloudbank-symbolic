"""
Tests for symbolic/quantum_bridge/quantum_bridge.py
"""

import sys
from pathlib import Path

import pytest

# Add repo root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from symbolic.quantum_bridge.quantum_bridge import (  # noqa: E402
    BridgeHealth,
    CausalAnchorViolation,
    QuantumBridge,
)


@pytest.mark.unit
@pytest.mark.aurora
class TestQuantumBridgeConfig:
    def test_loads_config_from_default_path(self):
        bridge = QuantumBridge()
        assert bridge.config["bridge_id"] == "ORION_QUANTUM_BRIDGE_001"
        assert bridge.config["synchronization_parameters"]["reality_sampling_rate"] == 100


@pytest.mark.unit
@pytest.mark.aurora
class TestSampleReality:
    def test_default_provider_yields_empty_signals(self):
        bridge = QuantumBridge()
        sample = bridge.sample_reality()
        assert sample["signals"] == {}
        assert sample["bridge_id"] == "ORION_QUANTUM_BRIDGE_001"
        assert sample["sampled_at_hz"] == 100

    def test_injected_provider_signals_flow_through(self):
        bridge = QuantumBridge(reality_provider=lambda: {"coherence": 0.9, "field_strength": 0.5})
        sample = bridge.sample_reality()
        assert sample["signals"]["field_strength"] == 0.5
        assert sample["coherence"] == 0.9


@pytest.mark.unit
@pytest.mark.aurora
class TestValidateCausalAnchor:
    def test_first_sample_always_valid(self):
        bridge = QuantumBridge()
        sample = bridge.sample_reality()
        assert bridge.validate_causal_anchor(sample) is True

    def test_out_of_order_sample_raises(self):
        bridge = QuantumBridge()
        first = bridge.sample_reality()
        stale = dict(first)
        stale["timestamp"] = "2000-01-01T00:00:00Z"
        with pytest.raises(CausalAnchorViolation):
            bridge.validate_causal_anchor(stale)


@pytest.mark.unit
@pytest.mark.aurora
class TestEncodeToMeshThreads:
    def test_empty_signals_produce_no_threads(self):
        bridge = QuantumBridge()
        sample = bridge.sample_reality()
        assert bridge.encode_to_mesh_threads(sample) == []

    def test_signals_produce_thread_descriptors(self):
        bridge = QuantumBridge(
            reality_provider=lambda: {"coherence": 0.9, "field_strength": 0.5, "spin_state": 1}
        )
        sample = bridge.sample_reality()
        threads = bridge.encode_to_mesh_threads(sample)

        thread_by_tag = {t.tags[-1]: t for t in threads}
        assert set(thread_by_tag) == {"field_strength", "spin_state"}
        assert all(t.source == "ORION_QUANTUM_BRIDGE_001" for t in threads)
        assert all(t.anchor_alignment == 0.9 for t in threads)
        assert all(0.0 <= t.entropy_hint <= 1.0 for t in threads)

    def test_causally_invalid_sample_blocks_encoding(self):
        bridge = QuantumBridge(reality_provider=lambda: {"coherence": 0.9, "x": 1})
        first = bridge.sample_reality()
        bridge.encode_to_mesh_threads(first)

        stale = dict(first)
        stale["timestamp"] = "2000-01-01T00:00:00Z"
        with pytest.raises(CausalAnchorViolation):
            bridge.encode_to_mesh_threads(stale)


@pytest.mark.unit
@pytest.mark.aurora
class TestCheckDrift:
    def test_coherent_sample_returns_none(self):
        bridge = QuantumBridge(reality_provider=lambda: {"coherence": 0.99})
        sample = bridge.sample_reality()
        assert bridge.check_drift(sample) is None

    def test_low_coherence_returns_drift_event(self):
        bridge = QuantumBridge(reality_provider=lambda: {"coherence": 0.5})
        sample = bridge.sample_reality()
        event = bridge.check_drift(sample)

        assert event is not None
        assert event["event_type"] == "aurora.drift.detected"
        assert event["source_node"] == "ORION-QUANTUM-BRIDGE"
        assert event["payload"]["coherence"] == 0.5
        assert "timestamp" in event
        assert event["provenance"]["l3_compliance"] is True


@pytest.mark.unit
@pytest.mark.aurora
class TestGetBridgeHealth:
    def test_healthy_before_any_sample(self):
        bridge = QuantumBridge()
        health = bridge.get_bridge_health()
        assert isinstance(health, BridgeHealth)
        assert health.status == "healthy"
        assert health.node == "ORION-QUANTUM-BRIDGE"

    def test_degraded_after_low_coherence_sample(self):
        bridge = QuantumBridge(reality_provider=lambda: {"coherence": 0.5})
        bridge.sample_reality()
        health = bridge.get_bridge_health()
        assert health.status == "degraded"
        assert health.last_coherence == 0.5
