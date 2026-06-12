"""Phase 1 foundation tests: types, window, registry, bus, interpreter, budget."""

import time

from src.sensors.core import (
    LayerInterpreter,
    MetricUnit,
    PerformanceBudget,
    RollingWindow,
    SensorDataBus,
    SensorRegistry,
    SensorSignal,
    utcnow,
)
from src.sensors.internal import EnvironmentalSensor


def test_rolling_window_appends_and_counts():
    w = RollingWindow(60)
    w.append({"x": 1})
    w.append({"x": 2})
    assert len(w) == 2
    assert [i["x"] for i in w.items()] == [1, 2]


def test_rolling_window_evicts_old_items():
    w = RollingWindow(0)  # zero-second window: everything is stale
    w.append({"x": 1})
    time.sleep(0.01)
    assert len(w) == 0


def test_registry_rejects_duplicates_and_filters():
    reg = SensorRegistry()
    s = EnvironmentalSensor()
    reg.register(s, phases=["phase_1"])
    assert reg.get(s.sensor_id) is s
    assert reg.by_layer("L1") == [s]
    assert reg.by_category("environmental") == [s]
    assert reg.for_phase("phase_1") == [s]
    try:
        reg.register(EnvironmentalSensor())
        raise AssertionError("duplicate registration should fail")
    except ValueError:
        pass


def test_bus_pubsub_and_window_query():
    bus = SensorDataBus()
    seen = []
    bus.subscribe("t1", lambda topic, p: seen.append(p))
    bus.publish("t1", {"v": 1})
    bus.publish("t2", {"v": 2})
    assert seen == [{"v": 1}]
    assert len(bus.window(60)) == 2
    assert len(bus.window(60, topic="t2")) == 1


def test_bus_listener_faults_do_not_propagate():
    bus = SensorDataBus()
    bus.subscribe("t", lambda *_: 1 / 0)
    bus.publish("t", {"v": 1})  # must not raise


def test_layer_interpreter_one_way_semantics():
    interp = LayerInterpreter()
    l1 = interp.interpret(SensorSignal(
        "s", "L1", "structural", "hull", 0.9, MetricUnit.RATIO, utcnow()))
    l3 = interp.interpret(SensorSignal(
        "s", "L3", "resonance", "echo", 0.5, MetricUnit.RATIO, utcnow()))
    assert l1.literal and l1.actionable
    assert not l3.literal and not l3.actionable  # L3 informs, L1 acts


def test_budget_records_violations_and_doubles_decimation():
    b = PerformanceBudget(tick_budget_seconds=0.001)
    n0 = b.decimation_n
    b.start_tick()
    with b.timed_operation("internal_sensor"):
        time.sleep(0.02)  # > 10ms budget and > tick aggregate
    assert any(v.operation_type == "internal_sensor" for v in b.violations)
    assert b.end_tick() is False
    assert b.decimation_n == n0 * 2
    assert any(v.operation_type == "per_tick_aggregate" for v in b.violations)


def test_metric_unit_scales_are_distinct():
    # Guard against the unit-conflation hazard called out in v0.3.0.
    assert MetricUnit.DRIFT_DELTA != MetricUnit.DEVIATION_FRACTION
