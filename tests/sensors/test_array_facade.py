"""End-to-end facade tests: composition, budget wiring, certification verdict."""

from src.sensors.array import SensorArrayFacade


def _array(**kw):
    return SensorArrayFacade(**kw)


def test_facade_registers_all_sensor_categories():
    a = _array()
    status = a.health_status()
    assert status["sensors_registered"] == 17
    assert status["sensors_enabled"] == 17


def test_category_reads_publish_to_bus():
    a = _array()
    r = a.read_category("internal", "environmental")
    assert r is not None and r.alerts == []
    assert len(a.bus) == 1


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
