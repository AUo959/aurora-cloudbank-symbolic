"""Prometheus metrics for the Playground execution backend."""
from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram

execution_counter = Counter(
    "playground_executions_total",
    "Count of code executions per language",
    labelnames=["language"],
)
execution_errors = Counter(
    "playground_execution_errors_total",
    "Count of execution errors per language",
    labelnames=["language"],
)
execution_latency = Histogram(
    "playground_execution_seconds",
    "Execution duration per language",
    labelnames=["language"],
)
sessions_gauge = Gauge(
    "playground_sessions_active",
    "Active playground sessions",
)
