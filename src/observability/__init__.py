"""
Aurora Observability Module

Provides comprehensive system observability through:
- OpenTelemetry integration for distributed tracing
- Performance metrics collection and export
- Adoption and usage analytics
- Prometheus-compatible metric export
- R-2 Agent production telemetry with anomaly detection
- Drift metrics Prometheus export for DriftDetector integration
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

from .drift_prometheus_exporter import (
    DriftPrometheusExporter,
    DriftMetricSnapshot,
    get_drift_exporter,
    reset_drift_exporter
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
    # Drift Prometheus exporter
    'DriftPrometheusExporter',
    'DriftMetricSnapshot',
    'get_drift_exporter',
    'reset_drift_exporter',
]
