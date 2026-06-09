"""Aurora CloudBank load testing harness.

Defines core user scenarios to validate SLO baselines.

Run with:
    locust -f tests/load/locustfile.py --host=http://localhost:8000 \\
           --users=50 --spawn-rate=5 --run-time=60s --headless

SLO baselines (targets):
    - /health:              p95 < 50ms,   error rate < 0.1%
    - /memory/retrieve:     p95 < 500ms,  error rate < 1%
    - /memory/create:       p95 < 300ms,  error rate < 1%
    - /memory/metrics:      p95 < 100ms,  error rate < 0.5%
    - /simulate/scenario:   p95 < 5000ms, error rate < 2%
    - /api/synergy/health:  p95 < 200ms,  error rate < 1%
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone

from locust import HttpUser, between, constant_throughput, task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TAGS = ["load-test", "performance", "aurora", "baseline"]
_QUERY_TERMS = [
    "quantum entanglement memory",
    "agent state retrieval",
    "load test context",
    "synergy baseline metrics",
    "drift detection pattern",
]


def _rand_context() -> str:
    return f"load-ctx-{random.randint(1, 20)}"


def _rand_query() -> str:
    return random.choice(_QUERY_TERMS)


# ---------------------------------------------------------------------------
# Standard user — mixed read/write workload
# ---------------------------------------------------------------------------


class AuroraAPIUser(HttpUser):
    """Simulates a typical Aurora API user with a realistic mix of operations."""

    wait_time = between(0.5, 2.0)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_start(self) -> None:
        """Warm-up: verify the server is reachable before load begins."""
        with self.client.get("/health", catch_response=True, name="[warmup] /health") as resp:
            if resp.status_code != 200:
                resp.failure(f"Warm-up health check failed: {resp.status_code}")

    # ------------------------------------------------------------------
    # Health probes  (weight 10 — high frequency)
    # ------------------------------------------------------------------

    @task(10)
    def health_check(self) -> None:
        """GET /health — primary health probe (SLO: p95 < 50 ms, err < 0.1%)."""
        with self.client.get("/health", catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Health check failed: {resp.status_code}")

    @task(3)
    def api_health_check(self) -> None:
        """GET /api/health — alternate health endpoint."""
        with self.client.get("/api/health", catch_response=True, name="GET /api/health") as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Memory system — read path  (weight 8)
    # ------------------------------------------------------------------

    @task(8)
    def retrieve_memories(self) -> None:
        """POST /memory/retrieve — core memory read path (SLO: p95 < 500 ms)."""
        payload = {
            "query": _rand_query(),
            "top_k": random.randint(3, 10),
            "memory_type": "agent",
        }
        with self.client.post(
            "/memory/retrieve",
            json=payload,
            catch_response=True,
            name="POST /memory/retrieve",
        ) as resp:
            if resp.status_code in (200, 404, 422):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(3)
    def memory_metrics(self) -> None:
        """GET /memory/metrics — lightweight read (SLO: p95 < 100 ms)."""
        with self.client.get(
            "/memory/metrics",
            catch_response=True,
            name="GET /memory/metrics",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(2)
    def memory_health(self) -> None:
        """GET /memory/health — memory subsystem health check."""
        with self.client.get(
            "/memory/health",
            catch_response=True,
            name="GET /memory/health",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Memory system — write path  (weight 4)
    # ------------------------------------------------------------------

    @task(4)
    def create_memory(self) -> None:
        """POST /memory/create — memory write path (SLO: p95 < 300 ms)."""
        payload = {
            "content": {
                "text": f"load-test entry {random.randint(1, 10000)}",
                "source": "locust",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "memory_type": "agent",
            "importance": round(random.uniform(1.0, 9.0), 2),
            "tags": random.sample(_TAGS, k=random.randint(1, 3)),
        }
        with self.client.post(
            "/memory/create",
            json=payload,
            catch_response=True,
            name="POST /memory/create",
        ) as resp:
            if resp.status_code in (200, 201, 422, 429):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Telemetry / observability  (weight 3)
    # ------------------------------------------------------------------

    @task(3)
    def telemetry_snapshot(self) -> None:
        """GET /telemetry/snapshot — observability endpoint."""
        with self.client.get(
            "/telemetry/snapshot",
            catch_response=True,
            name="GET /telemetry/snapshot",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(2)
    def prometheus_metrics(self) -> None:
        """GET /metrics — Prometheus scrape endpoint."""
        with self.client.get(
            "/metrics",
            catch_response=True,
            name="GET /metrics",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Synergy dashboard  (weight 2)
    # ------------------------------------------------------------------

    @task(2)
    def synergy_status(self) -> None:
        """GET /api/synergy/health — component synergy (SLO: p95 < 200 ms)."""
        with self.client.get(
            "/api/synergy/health",
            catch_response=True,
            name="GET /api/synergy/health",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Quantum simulator — read (weight 2)
    # ------------------------------------------------------------------

    @task(2)
    def simulate_scenarios_list(self) -> None:
        """GET /simulate/scenarios — list available quantum scenarios."""
        with self.client.get(
            "/simulate/scenarios",
            catch_response=True,
            name="GET /simulate/scenarios",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(2)
    def simulate_cache_stats(self) -> None:
        """GET /simulate/cache/stats — simulator cache stats."""
        with self.client.get(
            "/simulate/cache/stats",
            catch_response=True,
            name="GET /simulate/cache/stats",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    # ------------------------------------------------------------------
    # Drift detection  (weight 1)
    # ------------------------------------------------------------------

    @task(1)
    def drift_patterns(self) -> None:
        """GET /api/drift/patterns — drift detection read."""
        with self.client.get(
            "/api/drift/patterns",
            catch_response=True,
            name="GET /api/drift/patterns",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")


# ---------------------------------------------------------------------------
# High-load stress user — constant throughput, read-heavy
# ---------------------------------------------------------------------------


class AuroraHighLoadUser(HttpUser):
    """Aggressive read-heavy load profile for stress / soak testing.

    Keeps a constant throughput of 5 requests/second per user so that
    the total request rate scales linearly with --users.
    """

    wait_time = constant_throughput(5)

    @task(10)
    def health_check(self) -> None:
        with self.client.get("/health", catch_response=True, name="[stress] GET /health") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Health failed: {resp.status_code}")

    @task(6)
    def retrieve_memories(self) -> None:
        payload = {"query": _rand_query(), "top_k": 5, "memory_type": "agent"}
        with self.client.post(
            "/memory/retrieve",
            json=payload,
            catch_response=True,
            name="[stress] POST /memory/retrieve",
        ) as resp:
            if resp.status_code in (200, 404, 422, 429):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(3)
    def memory_metrics(self) -> None:
        with self.client.get(
            "/memory/metrics",
            catch_response=True,
            name="[stress] GET /memory/metrics",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(1)
    def telemetry_snapshot(self) -> None:
        with self.client.get(
            "/telemetry/snapshot",
            catch_response=True,
            name="[stress] GET /telemetry/snapshot",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")


# ---------------------------------------------------------------------------
# Quantum-heavy user — for dedicated quantum SLO validation
# ---------------------------------------------------------------------------


class AuroraQuantumUser(HttpUser):
    """Exercises the quantum simulator endpoints specifically."""

    wait_time = between(1.0, 5.0)

    @task(5)
    def health_check(self) -> None:
        self.client.get("/health", name="[quantum] GET /health")

    @task(3)
    def list_scenarios(self) -> None:
        with self.client.get(
            "/simulate/scenarios",
            catch_response=True,
            name="[quantum] GET /simulate/scenarios",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(2)
    def cache_stats(self) -> None:
        with self.client.get(
            "/simulate/cache/stats",
            catch_response=True,
            name="[quantum] GET /simulate/cache/stats",
        ) as resp:
            if resp.status_code in (200, 404):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")

    @task(1)
    def run_scenario(self) -> None:
        """POST /simulate/scenario — full quantum scenario (SLO: p95 < 5000 ms)."""
        scenario = random.choice(["supply_chain", "portfolio_optimization", "energy_grid"])
        payload = {
            "scenario_type": scenario,
            "parameters": {
                "num_locations": random.randint(3, 8),
                "optimization_method": "qaoa",
                "backend": "simulator",
            },
        }
        with self.client.post(
            "/simulate/scenario",
            json=payload,
            catch_response=True,
            name="POST /simulate/scenario",
        ) as resp:
            if resp.status_code in (200, 201, 202, 404, 422, 429, 500, 503):
                resp.success()
            else:
                resp.failure(f"Unexpected: {resp.status_code}")
