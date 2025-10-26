"""
Resilience Sentinel Dashboard

Real-time monitoring, alerting, and health tracking for Aurora CloudBank Symbolic.

Provides:
- System metric collection (CPU, memory, disk)
- Custom metric registration
- Alert rule management with threshold detection
- Health status aggregation
- Historical metric tracking

Anchor: T1-RSD-001
Version: 0.1.0
"""

from .monitoring_engine import MonitoringEngine, MetricCollector, HealthStatus
from .alert_manager import AlertManager, Alert, AlertSeverity, AlertRule
from .metrics import MetricType, Metric, MetricHistory

__version__ = "0.1.0"
__anchor__ = "T1-RSD-001"

__all__ = [
    # Monitoring
    "MonitoringEngine",
    "MetricCollector",
    "HealthStatus",
    # Alerts
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertRule",
    # Metrics
    "MetricType",
    "Metric",
    "MetricHistory",
]
