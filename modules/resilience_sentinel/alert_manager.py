"""
Alert Management System

Handles alert generation, severity classification, rule evaluation,
and notification routing.

Anchor: T1-RSD-001-ALERTS
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .metrics import Metric


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """
    Represents a system alert.

    Attributes:
        id: Unique alert identifier
        severity: Alert severity level
        title: Short alert description
        message: Detailed alert message
        metric_name: Related metric name
        metric_value: Current metric value
        threshold: Threshold that triggered the alert
        timestamp: When alert was generated
        tags: Additional metadata
        acknowledged: Whether alert has been acknowledged
        resolved: Whether alert has been resolved
    """
    id: str
    severity: AlertSeverity
    title: str
    message: str
    metric_name: str
    metric_value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)
    tags: Dict[str, str] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "id": self.id,
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "tags": self.tags,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "acknowledged_at": self.acknowledged_at,
            "resolved_at": self.resolved_at,
        }

    def acknowledge(self):
        """Mark alert as acknowledged."""
        self.acknowledged = True
        self.acknowledged_at = time.time()

    def resolve(self):
        """Mark alert as resolved."""
        self.resolved = True
        self.resolved_at = time.time()


@dataclass
class AlertRule:
    """
    Defines conditions that trigger alerts.

    Attributes:
        name: Rule name
        metric_name: Metric to monitor
        condition: Comparison operator ('>', '<', '>=', '<=', '==', '!=')
        threshold: Threshold value
        severity: Alert severity when triggered
        message_template: Message template with {value} and {threshold} placeholders
        cooldown_seconds: Minimum time between alerts for same rule
        enabled: Whether rule is active
    """
    name: str
    metric_name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    message_template: str
    cooldown_seconds: int = 300  # 5 minutes default
    enabled: bool = True
    last_triggered: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def evaluate(self, metric: Metric) -> bool:
        """
        Evaluate if metric triggers this rule.

        Args:
            metric: Metric to evaluate

        Returns:
            True if rule conditions are met
        """
        if not self.enabled:
            return False

        # Check cooldown
        if self.last_triggered:
            if time.time() - self.last_triggered < self.cooldown_seconds:
                return False

        # Evaluate condition
        value = metric.value
        threshold = self.threshold

        conditions = {
            '>': value > threshold,
            '<': value < threshold,
            '>=': value >= threshold,
            '<=': value <= threshold,
            '==': value == threshold,
            '!=': value != threshold,
        }

        return conditions.get(self.condition, False)

    def format_message(self, metric_value: float) -> str:
        """Format alert message with actual values."""
        return self.message_template.format(
            value=metric_value,
            threshold=self.threshold,
            metric=self.metric_name,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "name": self.name,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "message_template": self.message_template,
            "cooldown_seconds": self.cooldown_seconds,
            "enabled": self.enabled,
            "last_triggered": self.last_triggered,
            "tags": self.tags,
        }


class AlertManager:
    """
    Manages alert rules, evaluation, and notification.

    Provides centralized alert management with rule-based triggers,
    severity classification, and notification routing.
    """

    def __init__(self):
        """Initialize alert manager."""
        self.rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.alert_counter = 0
        self.handlers: Dict[AlertSeverity, List[Callable]] = {
            severity: [] for severity in AlertSeverity
        }

    def add_rule(self, rule: AlertRule):
        """
        Add an alert rule.

        Args:
            rule: AlertRule to add
        """
        self.rules[rule.name] = rule

    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove an alert rule.

        Args:
            rule_name: Name of rule to remove

        Returns:
            True if rule was removed
        """
        if rule_name in self.rules:
            del self.rules[rule_name]
            return True
        return False

    def get_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get a specific rule."""
        return self.rules.get(rule_name)

    def get_all_rules(self) -> List[AlertRule]:
        """Get all alert rules."""
        return list(self.rules.values())

    def enable_rule(self, rule_name: str):
        """Enable a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = True

    def disable_rule(self, rule_name: str):
        """Disable a rule."""
        if rule_name in self.rules:
            self.rules[rule_name].enabled = False

    def evaluate_metric(self, metric: Metric) -> List[Alert]:
        """
        Evaluate metric against all rules.

        Args:
            metric: Metric to evaluate

        Returns:
            List of alerts triggered
        """
        triggered_alerts = []

        for rule in self.rules.values():
            if rule.metric_name != metric.name:
                continue

            if rule.evaluate(metric):
                alert = self._create_alert(rule, metric)
                triggered_alerts.append(alert)
                self.alerts.append(alert)
                rule.last_triggered = time.time()
                self._dispatch_alert(alert)

        return triggered_alerts

    def _create_alert(self, rule: AlertRule, metric: Metric) -> Alert:
        """Create alert from rule and metric."""
        self.alert_counter += 1
        alert_id = f"alert_{self.alert_counter}_{int(time.time())}"

        message = rule.format_message(metric.value)
        title = f"{rule.name} - {metric.name}"

        return Alert(
            id=alert_id,
            severity=rule.severity,
            title=title,
            message=message,
            metric_name=metric.name,
            metric_value=metric.value,
            threshold=rule.threshold,
            tags={**rule.tags, **metric.tags},
        )

    def _dispatch_alert(self, alert: Alert):
        """Dispatch alert to registered handlers."""
        handlers = self.handlers.get(alert.severity, [])
        for handler in handlers:
            try:
                handler(alert)
            except Exception as e:
                # Log but don't fail on handler errors
                print(f"Alert handler error: {e}")

    def register_handler(self, severity: AlertSeverity, handler: Callable):
        """
        Register an alert handler function.

        Args:
            severity: Alert severity to handle
            handler: Callable that accepts an Alert
        """
        if severity not in self.handlers:
            self.handlers[severity] = []
        self.handlers[severity].append(handler)

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """
        Get active (unresolved) alerts.

        Args:
            severity: Filter by severity (None = all)

        Returns:
            List of active alerts
        """
        active = [a for a in self.alerts if not a.resolved]

        if severity:
            active = [a for a in active if a.severity == severity]

        return active

    def get_unacknowledged_alerts(self) -> List[Alert]:
        """Get alerts that haven't been acknowledged."""
        return [a for a in self.alerts if not a.acknowledged and not a.resolved]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge

        Returns:
            True if alert was found and acknowledged
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledge()
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.

        Args:
            alert_id: Alert ID to resolve

        Returns:
            True if alert was found and resolved
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolve()
                return True
        return False

    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics."""
        active = self.get_active_alerts()
        unack = self.get_unacknowledged_alerts()

        severity_counts = {severity: 0 for severity in AlertSeverity}
        for alert in active:
            severity_counts[alert.severity] += 1

        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active),
            "unacknowledged_alerts": len(unack),
            "by_severity": {s.value: c for s, c in severity_counts.items()},
            "rules_count": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
        }

    def clear_resolved_alerts(self):
        """Remove resolved alerts from history."""
        self.alerts = [a for a in self.alerts if not a.resolved]

    def get_recent_alerts(self, count: int = 100) -> List[Alert]:
        """Get most recent alerts."""
        return sorted(self.alerts, key=lambda a: a.timestamp, reverse=True)[:count]


# Predefined rule templates
DEFAULT_RULES = {
    "high_cpu": AlertRule(
        name="High CPU Usage",
        metric_name="cpu_usage",
        condition=">",
        threshold=80.0,
        severity=AlertSeverity.WARNING,
        message_template="CPU usage is {value:.1f}% (threshold: {threshold}%)",
    ),
    "critical_cpu": AlertRule(
        name="Critical CPU Usage",
        metric_name="cpu_usage",
        condition=">",
        threshold=95.0,
        severity=AlertSeverity.CRITICAL,
        message_template="CPU usage critical at {value:.1f}% (threshold: {threshold}%)",
    ),
    "high_memory": AlertRule(
        name="High Memory Usage",
        metric_name="memory_usage",
        condition=">",
        threshold=85.0,
        severity=AlertSeverity.WARNING,
        message_template="Memory usage is {value:.1f}% (threshold: {threshold}%)",
    ),
    "high_error_rate": AlertRule(
        name="High Error Rate",
        metric_name="error_rate",
        condition=">",
        threshold=5.0,
        severity=AlertSeverity.ERROR,
        message_template="Error rate at {value:.1f}% (threshold: {threshold}%)",
    ),
    "low_health_score": AlertRule(
        name="Low Health Score",
        metric_name="health_score",
        condition="<",
        threshold=80.0,
        severity=AlertSeverity.WARNING,
        message_template="Health score dropped to {value:.1f} (threshold: {threshold})",
    ),
}
