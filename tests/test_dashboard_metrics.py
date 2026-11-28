"""Dashboard contract checks using runtime counters, never synthetic success data."""
from types import SimpleNamespace

import pytest


@pytest.mark.unit
def test_dashboard_snapshot_reads_counters_and_marks_unknowns(monkeypatch):
    monkeypatch.setenv("CSRF_SECRET_KEY", "dashboard-test-csrf-not-a-production-key")
    monkeypatch.setenv("WS_AUTH_SECRET", "dashboard-test-ws-not-a-production-key")
    from src.observability import dashboard_metrics as metrics

    memory = {"total_memories": 12, "active_memories": 7, "compressed_memories": 3, "archived_memories": 2}
    monkeypatch.setattr(metrics, "memory_manager", SimpleNamespace(get_metrics=lambda: memory.copy()))
    agent = SimpleNamespace(
        status="ready", active_tasks=[object()], stats={"tasks_completed": 4, "tasks_failed": 2}
    )
    monkeypatch.setattr(metrics, "get_all_crew_agents", lambda: {"test": agent})
    monkeypatch.setattr(metrics, "active_simulations", {
        "running": SimpleNamespace(status="running")
    })
    monkeypatch.setattr(metrics, "get_cache", lambda: SimpleNamespace(
        max_cache_size=1000,
        list_scenarios=lambda limit: [SimpleNamespace(simulation_id="done")],
    ))
    monkeypatch.setattr(metrics, "get_pusher", lambda: SimpleNamespace(
        get_metrics=lambda: {"request_count": 8, "avg_latency_ms": 12.5}
    ))
    monkeypatch.setattr(metrics.psutil, "cpu_percent", lambda interval: 17.0)
    monkeypatch.setattr(metrics.psutil, "virtual_memory", lambda: SimpleNamespace(percent=42.0))

    result = metrics.collect_dashboard_metrics()
    assert result["memory"]["total_memories"] == 12
    assert result["memory"]["cache_hit_rate"] is None
    assert result["quantum"] == {
        "simulations_running": 1, "total_simulations": 2, "average_speedup": None
    }
    assert result["agents"]["total_tasks"] == 7
    assert result["agents"]["completed_tasks"] == 4
    assert result["system"]["api_requests_per_minute"] == 8
    assert result["system"]["average_response_time_ms"] == 12.5
    assert result["system"]["cpu_usage"] == 17.0
    assert result["system"]["memory_usage"] == 42.0

    # Completion removes the running entry but retains its cached result.
    monkeypatch.setattr(metrics, "active_simulations", {})
    assert metrics.collect_dashboard_metrics()["quantum"]["total_simulations"] == 1


@pytest.mark.api
def test_dashboard_contract_is_mounted_on_primary_api(monkeypatch):
    monkeypatch.setenv("CSRF_SECRET_KEY", "dashboard-test-csrf-not-a-production-key")
    monkeypatch.setenv("WS_AUTH_SECRET", "dashboard-test-ws-not-a-production-key")
    from fastapi.testclient import TestClient
    from api.aurora_api import app
    from src.observability import dashboard_metrics as metrics

    def snapshot_on_owner_loop():
        import asyncio
        # A synchronous worker-thread endpoint has no running event loop and
        # races the async simulation/cache writers. Keep this read serialized.
        asyncio.get_running_loop()
        return {"context_tag": "contract-check"}

    monkeypatch.setattr(metrics, "collect_dashboard_metrics", snapshot_on_owner_loop)
    response = TestClient(app).get("/api/system/metrics")
    assert response.status_code == 200
    assert response.json() == {"context_tag": "contract-check"}


@pytest.mark.unit
def test_missing_optional_components_preserve_other_metrics(monkeypatch):
    monkeypatch.setenv("CSRF_SECRET_KEY", "dashboard-test-csrf-not-a-production-key")
    monkeypatch.setenv("WS_AUTH_SECRET", "dashboard-test-ws-not-a-production-key")
    from src.observability import dashboard_metrics as metrics

    monkeypatch.setattr(metrics, "memory_manager", None)
    monkeypatch.setattr(metrics, "active_simulations", None)
    monkeypatch.setattr(metrics, "get_cache", None)
    monkeypatch.setattr(metrics, "get_all_crew_agents", lambda: {})
    result = metrics.collect_dashboard_metrics()
    assert result["memory"]["total_memories"] is None
    assert result["quantum"]["total_simulations"] is None
    assert result["agents"]["total_agents"] == 0
    assert result["system"]["memory_usage"] >= 0
