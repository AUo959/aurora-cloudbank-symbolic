"""
Aurora Observability Module

Provides comprehensive system observability through:
- OpenTelemetry integration for distributed tracing
- Performance metrics collection and export
- Adoption and usage analytics
- Prometheus-compatible metric export
"""

from .telemetry import (
    AuroraTelemetry,
    MetricSnapshot,
    get_telemetry,
    reset_telemetry,
    OTEL_AVAILABLE
)

__all__ = [
    'AuroraTelemetry',
    'MetricSnapshot',
    'get_telemetry',
    'reset_telemetry',
    'OTEL_AVAILABLE',
]
