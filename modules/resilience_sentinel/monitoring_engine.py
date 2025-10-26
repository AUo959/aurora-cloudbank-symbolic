"""
Monitoring Engine Core

Central monitoring system that collects metrics, evaluates health status,
and coordinates alert generation.

Anchor: T1-RSD-001-ENGINE
"""

import time
import psutil
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .metrics import Metric, MetricType, MetricHistory
from .alert_manager import AlertManager, AlertSeverity, AlertRule, DEFAULT_RULES


class HealthStatus(Enum):
    """Overall system health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """
    Individual health check result.

    Attributes:
        name: Check name
        status: Health status
        value: Metric value
        threshold: Threshold for health
        message: Status message
        timestamp: Check timestamp
    """
    name: str
    status: HealthStatus
    value: float
    threshold: float
    message: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp,
        }


class MetricCollector:
    """
    Collects system and application metrics.

    Provides methods to gather CPU, memory, disk, and custom metrics.
    """

    def __init__(self):
        """Initialize metric collector."""
        self.custom_collectors: Dict[str, Callable] = {}

    def collect_cpu_usage(self) -> Metric:
        """Collect CPU usage percentage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        return Metric(
            name="cpu_usage",
            type=MetricType.CPU_USAGE,
            value=cpu_percent,
            unit="percent",
            tags={"source": "psutil"},
        )

    def collect_memory_usage(self) -> Metric:
        """Collect memory usage percentage."""
        mem = psutil.virtual_memory()
        return Metric(
            name="memory_usage",
            type=MetricType.MEMORY_USAGE,
            value=mem.percent,
            unit="percent",
            tags={"source": "psutil", "total": str(mem.total)},
        )

    def collect_disk_usage(self, path: str = "/") -> Metric:
        """Collect disk usage percentage."""
        disk = psutil.disk_usage(path)
        return Metric(
            name="disk_usage",
            type=MetricType.DISK_USAGE,
            value=disk.percent,
            unit="percent",
            tags={"source": "psutil", "path": path},
        )

    def collect_all_system_metrics(self) -> List[Metric]:
        """Collect all standard system metrics."""
        metrics = [
            self.collect_cpu_usage(),
            self.collect_memory_usage(),
            self.collect_disk_usage(),
        ]
        return metrics

    def register_custom_collector(self, name: str, collector: Callable[[], Metric]):
        """
        Register a custom metric collector.

        Args:
            name: Collector name
            collector: Callable that returns a Metric
        """
        self.custom_collectors[name] = collector

    def collect_custom_metric(self, name: str) -> Optional[Metric]:
        """
        Collect a custom metric.

        Args:
            name: Name of registered collector

        Returns:
            Metric or None if collector not found
        """
        if name not in self.custom_collectors:
            return None

        try:
            return self.custom_collectors[name]()
        except Exception as e:
            # Return error metric
            return Metric(
                name=name,
                type=MetricType.CUSTOM,
                value=-1,
                tags={"error": str(e)},
            )

    def collect_all_custom_metrics(self) -> List[Metric]:
        """Collect all registered custom metrics."""
        metrics = []
        for name in self.custom_collectors:
            metric = self.collect_custom_metric(name)
            if metric:
                metrics.append(metric)
        return metrics


class MonitoringEngine:
    """
    Core monitoring engine.

    Orchestrates metric collection, history tracking, alert evaluation,
    and health status determination.
    """

    def __init__(
        self,
        collection_interval: int = 60,
        history_size: int = 1000,
        enable_default_rules: bool = True,
    ):
        """
        Initialize monitoring engine.

        Args:
            collection_interval: Seconds between metric collections
            history_size: Maximum metrics to store per metric name
            enable_default_rules: Whether to load default alert rules
        """
        self.collection_interval = collection_interval
        self.history = MetricHistory(max_size=history_size)
        self.collector = MetricCollector()
        self.alert_manager = AlertManager()
        self.is_running = False
        self.last_collection_time = 0.0
        self.health_checks: List[HealthCheck] = []

        # Load default alert rules
        if enable_default_rules:
            for rule in DEFAULT_RULES.values():
                self.alert_manager.add_rule(rule)

    def collect_metrics(self) -> List[Metric]:
        """
        Collect all metrics (system + custom).

        Returns:
            List of collected metrics
        """
        metrics = []

        # Collect system metrics
        metrics.extend(self.collector.collect_all_system_metrics())

        # Collect custom metrics
        metrics.extend(self.collector.collect_all_custom_metrics())

        # Store in history
        for metric in metrics:
            self.history.add(metric)

        self.last_collection_time = time.time()
        return metrics

    def evaluate_alerts(self, metrics: List[Metric]) -> List[Any]:
        """
        Evaluate metrics against alert rules.

        Args:
            metrics: Metrics to evaluate

        Returns:
            List of triggered alerts
        """
        all_alerts = []
        for metric in metrics:
            alerts = self.alert_manager.evaluate_metric(metric)
            all_alerts.extend(alerts)
        return all_alerts

    def run_health_checks(self) -> HealthStatus:
        """
        Run comprehensive health checks.

        Returns:
            Overall health status
        """
        self.health_checks = []

        # CPU health check
        cpu_metric = self.history.get_latest("cpu_usage")
        if cpu_metric:
            cpu_status = self._determine_health(
                cpu_metric.value,
                healthy_threshold=70,
                degraded_threshold=85,
                unhealthy_threshold=95,
            )
            self.health_checks.append(HealthCheck(
                name="cpu",
                status=cpu_status,
                value=cpu_metric.value,
                threshold=70,
                message=f"CPU usage: {cpu_metric.value:.1f}%",
            ))

        # Memory health check
        mem_metric = self.history.get_latest("memory_usage")
        if mem_metric:
            mem_status = self._determine_health(
                mem_metric.value,
                healthy_threshold=75,
                degraded_threshold=85,
                unhealthy_threshold=95,
            )
            self.health_checks.append(HealthCheck(
                name="memory",
                status=mem_status,
                value=mem_metric.value,
                threshold=75,
                message=f"Memory usage: {mem_metric.value:.1f}%",
            ))

        # Disk health check
        disk_metric = self.history.get_latest("disk_usage")
        if disk_metric:
            disk_status = self._determine_health(
                disk_metric.value,
                healthy_threshold=80,
                degraded_threshold=90,
                unhealthy_threshold=95,
            )
            self.health_checks.append(HealthCheck(
                name="disk",
                status=disk_status,
                value=disk_metric.value,
                threshold=80,
                message=f"Disk usage: {disk_metric.value:.1f}%",
            ))

        # Aggregate overall health
        return self._aggregate_health_status()

    def _determine_health(
        self,
        value: float,
        healthy_threshold: float,
        degraded_threshold: float,
        unhealthy_threshold: float,
    ) -> HealthStatus:
        """Determine health status based on value and thresholds."""
        if value <= healthy_threshold:
            return HealthStatus.HEALTHY
        elif value <= degraded_threshold:
            return HealthStatus.DEGRADED
        elif value <= unhealthy_threshold:
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.CRITICAL

    def _aggregate_health_status(self) -> HealthStatus:
        """Aggregate individual health checks into overall status."""
        if not self.health_checks:
            return HealthStatus.UNKNOWN

        # Use worst status as overall status
        statuses = [check.status for check in self.health_checks]

        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        elif HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        elif HealthStatus.HEALTHY in statuses:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN

    def get_health_report(self) -> Dict[str, Any]:
        """
        Get comprehensive health report.

        Returns:
            Dict with overall status and individual checks
        """
        overall = self.run_health_checks()

        return {
            "status": overall.value,
            "timestamp": time.time(),
            "checks": [check.to_dict() for check in self.health_checks],
            "alerts": {
                "active": len(self.alert_manager.get_active_alerts()),
                "unacknowledged": len(self.alert_manager.get_unacknowledged_alerts()),
            },
        }

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = self.history.get_summary()
        summary["last_collection"] = self.last_collection_time
        summary["collection_interval"] = self.collection_interval

        # Add stats for key metrics
        key_metrics = ["cpu_usage", "memory_usage", "disk_usage"]
        summary["metrics_stats"] = {}

        for metric_name in key_metrics:
            if metric_name in self.history.metrics:
                summary["metrics_stats"][metric_name] = self.history.get_stats(metric_name)

        return summary

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.

        Returns:
            Dict with health, metrics, alerts, and system info
        """
        return {
            "health": self.get_health_report(),
            "metrics": self.get_metrics_summary(),
            "alerts": self.alert_manager.get_alert_stats(),
            "recent_alerts": [a.to_dict() for a in self.alert_manager.get_recent_alerts(10)],
            "system": {
                "collection_interval": self.collection_interval,
                "history_size": self.history.max_size,
                "rules_enabled": sum(1 for r in self.alert_manager.rules.values() if r.enabled),
            },
        }

    def register_custom_metric(self, name: str, collector: Callable[[], Metric]):
        """
        Register a custom metric collector.

        Args:
            name: Metric name
            collector: Callable returning Metric
        """
        self.collector.register_custom_collector(name, collector)

    def add_alert_rule(self, rule: AlertRule):
        """Add an alert rule."""
        self.alert_manager.add_rule(rule)

    def register_alert_handler(self, severity: AlertSeverity, handler: Callable):
        """
        Register alert handler.

        Args:
            severity: Alert severity to handle
            handler: Callable accepting Alert
        """
        self.alert_manager.register_handler(severity, handler)
