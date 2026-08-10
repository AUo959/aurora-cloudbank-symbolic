"""End-to-end facade tests: composition, budget wiring, certification verdict."""

from src.sensors.array import SensorArrayFacade


def _array(**kw):
    return SensorArrayFacade(**kw)


def test_facade_registers_all_sensor_categories():
    a = _array()
    status = a.health_status()
    assert status["sensors_registered"] == 18
    assert status["sensors_enabled"] == 18


def test_category_reads_publish_to_bus():
    a = _array()
    r = a.read_category("internal", "environmental")
    assert r is not None and r.alerts == []
    assert len(a.bus) == 1


def test_provider_readings_disclose_bound_and_defaulted_metrics():
    unbound = _array().read_category("internal", "l1_runtime")
    bound = _array(
        providers={"l1_runtime": lambda: {"tick": 3, "event_count": 2}}
    ).read_category("internal", "l1_runtime")

    assert unbound is not None
    assert unbound.metadata["provider_bound"] is False
    assert set(unbound.metadata["defaulted_metrics"]) == set(unbound.values)
    assert bound is not None
    assert bound.metadata["provider_bound"] is True
    assert bound.metadata["reported_metrics"] == ["event_count", "tick"]
    assert "tick" not in bound.metadata["defaulted_metrics"]


def test_provider_alert_flows_to_certification():
    a = _array(providers={
        "reality_anchor": lambda: {"anchor_chain_valid": 0.0},
    })
    cert = a.certification()
    assert not cert.anchor_verified
    assert not cert.system_coherent
    assert cert.reality_grounding == 0.0


def test_healthy_array_certifies_coherent():
    a = _array()
    cert = a.certification()
    assert cert.system_coherent, cert.blocking_issues
    assert cert.verification_hash


def test_integration_depth_endpoint_data():
    a = _array()
    a.sii.record_reference("L2:faction:marshals", "dep1")
    snap = a.integration_depth()
    assert "EOS_SEED_ORION" in snap.depths
    assert snap.depths["EOS_SEED_ORION"] == 1.0


def test_budget_tracked_through_facade():
    a = _array()
    a.read_category("internal", "environmental")
    a.forecasts()
    perf = a.performance()
    assert "sii_update" in perf["budgets"]
    assert perf["tick_budget_fraction"] == 0.10
