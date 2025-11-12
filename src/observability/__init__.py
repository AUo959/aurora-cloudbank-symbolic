"""
Aurora Observability Module

Provides comprehensive system observability through:
- OpenTelemetry integration for distributed tracing
- Performance metrics collection and export
- Adoption and usage analytics
- Prometheus-compatible metric export
- R-2 Agent production telemetry with anomaly detection
"""

from .telemetry import (
    AuroraTelemetry,
    MetricSnapshot,
    get_telemetry,
    reset_telemetry,
    OTEL_AVAILABLE
)

from .r2_agent_telemetry import (
    R2AgentTelemetry,
    AgentOperationMetrics,
    AnomalyDetectionResult,
    PIIFilter,
    AnomalyDetector,
    get_r2_telemetry,
    reset_r2_telemetry
)

__all__ = [
    # Core telemetry
    'AuroraTelemetry',
    'MetricSnapshot',
    'get_telemetry',
    'reset_telemetry',
    'OTEL_AVAILABLE',
    # R-2 Agent telemetry
    'R2AgentTelemetry',
    'AgentOperationMetrics',
    'AnomalyDetectionResult',
    'PIIFilter',
    'AnomalyDetector',
    'get_r2_telemetry',
    'reset_r2_telemetry',
]
