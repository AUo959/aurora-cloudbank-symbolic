"""
Resilience Sentinel Dashboard

Real-time monitoring, alerting, and health tracking for Aurora CloudBank Symbolic.

Provides:
- System metric collection (CPU, memory, disk)
- Custom metric registration
- Alert rule management with threshold detection
- Health status aggregation
- Historical metric tracking
- Multi-channel alert notifications

Anchor: T1-RSD-001
Version: 0.2.0
"""

from .alert_manager import Alert, AlertManager, AlertRule, AlertSeverity
from .metrics import Metric, MetricHistory, MetricType
from .monitoring_engine import HealthStatus, MetricCollector, MonitoringEngine

try:
    from .notifications import (
        NotificationRouter,
        NotificationChannel,
        NotificationConfig,
        LogNotificationChannel,
        WebhookNotificationChannel,
        EmailNotificationChannel,
        ConsoleNotificationChannel,
        get_notification_router,
    )
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    NotificationRouter = None
    NotificationChannel = None
    NotificationConfig = None
    LogNotificationChannel = None
    WebhookNotificationChannel = None
    EmailNotificationChannel = None
    ConsoleNotificationChannel = None
    get_notification_router = None

__version__ = "0.2.0"
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
    # Notifications
    "NotificationRouter",
    "NotificationChannel",
    "NotificationConfig",
    "LogNotificationChannel",
    "WebhookNotificationChannel",
    "EmailNotificationChannel",
    "ConsoleNotificationChannel",
    "get_notification_router",
    "NOTIFICATIONS_AVAILABLE",
]
