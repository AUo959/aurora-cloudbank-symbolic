"""
Resilience Sentinel Dashboard Test Suite

Comprehensive tests for monitoring, metrics, alerts, and notifications.

Anchor: T1-RSD-004-TESTS
"""

import time

import pytest

from modules.resilience_sentinel.alert_manager import Alert, AlertManager, AlertRule, AlertSeverity
from modules.resilience_sentinel.metrics import Metric, MetricHistory, MetricType
from modules.resilience_sentinel.monitoring_engine import HealthStatus, MetricCollector, MonitoringEngine
from modules.resilience_sentinel.notifications import (
    ConsoleNotificationChannel,
    LogNotificationChannel,
    NotificationConfig,
    NotificationRouter,
)

# ============================================================================
# Metric Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.resilience
class TestMetrics:
    """Tests for metric collection and storage."""

    def test_metric_creation(self):
        """Test creating a metric."""
        metric = Metric(
            name="test_cpu",
            type=MetricType.CPU_USAGE,
            value=75.5,
            unit="percent",
            tags={"source": "test"},
        )

        assert metric.name == "test_cpu"
        assert metric.type == MetricType.CPU_USAGE
        assert metric.value == 75.5
        assert metric.unit == "percent"
        assert "source" in metric.tags

    def test_metric_threshold_checks(self):
        """Test metric threshold comparison methods."""
        metric = Metric(
            name="test_metric",
            type=MetricType.CUSTOM,
            value=80.0,
        )

        assert metric.is_above_threshold(75.0)
        assert not metric.is_above_threshold(85.0)
        assert metric.is_below_threshold(85.0)
        assert not metric.is_below_threshold(75.0)

    def test_metric_to_dict(self):
        """Test metric serialization."""
        metric = Metric(
            name="test_metric",
            type=MetricType.MEMORY_USAGE,
            value=60.0,
            timestamp=1234567890.0,
            unit="percent",
        )

        data = metric.to_dict()
        assert data["name"] == "test_metric"
        assert data["type"] == "memory_usage"
        assert data["value"] == 60.0
        assert "datetime" in data

    def test_metric_history_add(self):
        """Test adding metrics to history."""
        history = MetricHistory(max_size=10)
        metric = Metric("test", MetricType.CPU_USAGE, 50.0)

        history.add(metric)
        assert len(history.metrics["test"]) == 1

    def test_metric_history_rolling_window(self):
        """Test rolling window behavior."""
        history = MetricHistory(max_size=3)

        for i in range(5):
            metric = Metric("test", MetricType.CPU_USAGE, float(i))
            history.add(metric)

        # Should only keep last 3
        assert len(history.metrics["test"]) == 3

    def test_metric_history_get_latest(self):
        """Test getting latest metric."""
        history = MetricHistory()
        history.add(Metric("test", MetricType.CPU_USAGE, 10.0))
        history.add(Metric("test", MetricType.CPU_USAGE, 20.0))

        latest = history.get_latest("test")
        assert latest is not None
        assert latest.value == 20.0

    def test_metric_history_get_average(self):
        """Test calculating average."""
        history = MetricHistory()
        history.add(Metric("test", MetricType.CPU_USAGE, 10.0))
        history.add(Metric("test", MetricType.CPU_USAGE, 20.0))
        history.add(Metric("test", MetricType.CPU_USAGE, 30.0))

        avg = history.get_average("test")
        assert avg == 20.0

    def test_metric_history_get_trend(self):
        """Test trend detection."""
        history = MetricHistory()

        # Increasing trend
        for i in range(10):
            history.add(Metric("test", MetricType.CPU_USAGE, float(i * 10)))

        trend = history.get_trend("test", count=10)
        assert trend == "increasing"

    def test_metric_history_stats(self):
        """Test comprehensive stats."""
        history = MetricHistory()
        for i in range(5):
            history.add(Metric("test", MetricType.CPU_USAGE, float(i * 10)))

        stats = history.get_stats("test")
        assert stats["count"] == 5
        assert stats["min"] == 0.0
        assert stats["max"] == 40.0
        assert stats["average"] == 20.0


# ============================================================================
# Alert Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.resilience
class TestAlerts:
    """Tests for alert management."""

    def test_alert_creation(self):
        """Test creating an alert."""
        alert = Alert(
            id="test_001",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="Test message",
            metric_name="cpu_usage",
            metric_value=85.0,
            threshold=80.0,
        )

        assert alert.id == "test_001"
        assert alert.severity == AlertSeverity.WARNING
        assert not alert.acknowledged
        assert not alert.resolved

    def test_alert_acknowledge(self):
        """Test acknowledging an alert."""
        alert = Alert(
            id="test_001",
            severity=AlertSeverity.WARNING,
            title="Test",
            message="Test",
            metric_name="test",
            metric_value=100.0,
            threshold=80.0,
        )

        alert.acknowledge()
        assert alert.acknowledged
        assert alert.acknowledged_at is not None

    def test_alert_resolve(self):
        """Test resolving an alert."""
        alert = Alert(
            id="test_001",
            severity=AlertSeverity.WARNING,
            title="Test",
            message="Test",
            metric_name="test",
            metric_value=100.0,
            threshold=80.0,
        )

        alert.resolve()
        assert alert.resolved
        assert alert.resolved_at is not None

    def test_alert_rule_evaluation(self):
        """Test alert rule evaluation."""
        rule = AlertRule(
            name="high_cpu",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            message_template="CPU is {value}%",
        )

        # Should trigger
        metric_high = Metric("cpu_usage", MetricType.CPU_USAGE, 85.0)
        assert rule.evaluate(metric_high)

        # Should not trigger
        metric_low = Metric("cpu_usage", MetricType.CPU_USAGE, 75.0)
        assert not rule.evaluate(metric_low)

    def test_alert_rule_cooldown(self):
        """Test alert rule cooldown."""
        rule = AlertRule(
            name="test_rule",
            metric_name="test",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.INFO,
            message_template="Test",
            cooldown_seconds=2,
        )

        metric = Metric("test", MetricType.CUSTOM, 100.0)

        # First evaluation should pass
        assert rule.evaluate(metric)
        rule.last_triggered = time.time()

        # Second evaluation should be blocked by cooldown
        assert not rule.evaluate(metric)

    def test_alert_manager_add_rule(self):
        """Test adding rules to alert manager."""
        manager = AlertManager()
        rule = AlertRule(
            name="test_rule",
            metric_name="test",
            condition=">",
            threshold=50.0,
            severity=AlertSeverity.INFO,
            message_template="Test",
        )

        manager.add_rule(rule)
        assert "test_rule" in manager.rules

    def test_alert_manager_evaluate_metric(self):
        """Test evaluating metrics against rules."""
        manager = AlertManager()
        rule = AlertRule(
            name="test_rule",
            metric_name="cpu_usage",
            condition=">",
            threshold=80.0,
            severity=AlertSeverity.WARNING,
            message_template="High CPU: {value}%",
        )
        manager.add_rule(rule)

        metric = Metric("cpu_usage", MetricType.CPU_USAGE, 90.0)
        alerts = manager.evaluate_metric(metric)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING

    def test_alert_manager_get_active_alerts(self):
        """Test filtering active alerts."""
        manager = AlertManager()

        alert1 = Alert(
            id="1", severity=AlertSeverity.WARNING, title="Test 1",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )
        alert2 = Alert(
            id="2", severity=AlertSeverity.ERROR, title="Test 2",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )

        manager.alerts = [alert1, alert2]
        alert1.resolve()

        active = manager.get_active_alerts()
        assert len(active) == 1
        assert active[0].id == "2"

    def test_alert_manager_acknowledge_alert(self):
        """Test acknowledging alerts."""
        manager = AlertManager()
        alert = Alert(
            id="test_001", severity=AlertSeverity.WARNING, title="Test",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )
        manager.alerts.append(alert)

        success = manager.acknowledge_alert("test_001")
        assert success
        assert alert.acknowledged


# ============================================================================
# Monitoring Engine Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.resilience
class TestMonitoringEngine:
    """Tests for monitoring engine."""

    def test_metric_collector_cpu(self):
        """Test CPU metric collection."""
        collector = MetricCollector()
        metric = collector.collect_cpu_usage()

        assert metric.name == "cpu_usage"
        assert metric.type == MetricType.CPU_USAGE
        assert 0 <= metric.value <= 100

    def test_metric_collector_memory(self):
        """Test memory metric collection."""
        collector = MetricCollector()
        metric = collector.collect_memory_usage()

        assert metric.name == "memory_usage"
        assert metric.type == MetricType.MEMORY_USAGE
        assert 0 <= metric.value <= 100

    def test_metric_collector_custom(self):
        """Test custom metric collection."""
        collector = MetricCollector()

        def custom_collector():
            return Metric("custom_metric", MetricType.CUSTOM, 42.0)

        collector.register_custom_collector("custom", custom_collector)
        metric = collector.collect_custom_metric("custom")

        assert metric is not None
        assert metric.value == 42.0

    def test_monitoring_engine_initialization(self):
        """Test monitoring engine setup."""
        engine = MonitoringEngine(
            collection_interval=30,
            history_size=500,
            enable_default_rules=True,
        )

        assert engine.collection_interval == 30
        assert engine.history.max_size == 500
        assert len(engine.alert_manager.rules) > 0

    def test_monitoring_engine_collect_metrics(self):
        """Test metric collection."""
        engine = MonitoringEngine()
        metrics = engine.collect_metrics()

        assert len(metrics) >= 3  # CPU, memory, disk
        assert all(isinstance(m, Metric) for m in metrics)

    def test_monitoring_engine_health_checks(self):
        """Test health status evaluation."""
        engine = MonitoringEngine()
        engine.collect_metrics()
        status = engine.run_health_checks()

        assert isinstance(status, HealthStatus)

    def test_monitoring_engine_custom_metric(self):
        """Test registering custom metrics."""
        engine = MonitoringEngine()

        def custom():
            return Metric("custom", MetricType.CUSTOM, 99.0)

        engine.register_custom_metric("custom", custom)
        metrics = engine.collect_metrics()

        custom_metrics = [m for m in metrics if m.name == "custom"]
        assert len(custom_metrics) == 1


# ============================================================================
# Notification Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.resilience
class TestNotifications:
    """Tests for notification system."""

    def test_notification_config(self):
        """Test notification configuration."""
        config = NotificationConfig(
            channel_type="log",
            name="test_channel",
            enabled=True,
            severity_filter=[AlertSeverity.CRITICAL],
        )

        alert_critical = Alert(
            id="1", severity=AlertSeverity.CRITICAL, title="Test",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )
        alert_info = Alert(
            id="2", severity=AlertSeverity.INFO, title="Test",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )

        assert config.should_notify(alert_critical)
        assert not config.should_notify(alert_info)

    @pytest.mark.asyncio
    async def test_log_notification_channel(self):
        """Test log notification channel."""
        config = NotificationConfig(channel_type="log", name="test_log")
        channel = LogNotificationChannel(config)

        alert = Alert(
            id="test", severity=AlertSeverity.WARNING, title="Test",
            message="Test message", metric_name="test",
            metric_value=100, threshold=80
        )

        success = await channel.send(alert)
        assert success

    @pytest.mark.asyncio
    async def test_console_notification_channel(self):
        """Test console notification channel."""
        config = NotificationConfig(channel_type="console", name="test_console")
        channel = ConsoleNotificationChannel(config)

        alert = Alert(
            id="test", severity=AlertSeverity.ERROR, title="Test",
            message="Test message", metric_name="test",
            metric_value=100, threshold=80
        )

        success = await channel.send(alert)
        assert success

    @pytest.mark.asyncio
    async def test_notification_router(self):
        """Test notification routing."""
        router = NotificationRouter()

        config = NotificationConfig(channel_type="log", name="test")
        channel = LogNotificationChannel(config)
        router.register_channel(channel)

        alert = Alert(
            id="test", severity=AlertSeverity.WARNING, title="Test",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )

        results = await router.route_alert(alert)
        assert "test" in results
        assert results["test"] is True

    def test_notification_router_channel_management(self):
        """Test channel registration/unregistration."""
        router = NotificationRouter()

        config = NotificationConfig(channel_type="log", name="test")
        channel = LogNotificationChannel(config)

        router.register_channel(channel)
        assert "test" in router.channels

        router.unregister_channel("test")
        assert "test" not in router.channels

    @pytest.mark.asyncio
    async def test_notification_history(self):
        """Test notification history tracking."""
        router = NotificationRouter()

        config = NotificationConfig(channel_type="log", name="test")
        channel = LogNotificationChannel(config)
        router.register_channel(channel)

        alert = Alert(
            id="test_123", severity=AlertSeverity.INFO, title="Test",
            message="Test", metric_name="test", metric_value=100, threshold=80
        )

        await router.route_alert(alert)

        history = router.get_notification_history()
        assert len(history) > 0
        assert history[0]["alert_id"] == "test_123"


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.resilience
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_end_to_end_monitoring_flow(self):
        """Test complete monitoring workflow."""
        engine = MonitoringEngine()

        # Collect metrics
        metrics = engine.collect_metrics()
        assert len(metrics) > 0

        # Evaluate alerts (may or may not trigger depending on system state)
        engine.evaluate_alerts(metrics)

        # Check health
        status = engine.run_health_checks()
        assert isinstance(status, HealthStatus)

    @pytest.mark.asyncio
    async def test_monitoring_with_notifications(self):
        """Test monitoring with notification delivery."""
        engine = MonitoringEngine(enable_notifications=True)

        # Add a rule that will definitely trigger
        rule = AlertRule(
            name="test_rule",
            metric_name="test_metric",
            condition=">",
            threshold=0.0,
            severity=AlertSeverity.INFO,
            message_template="Test alert: {value}",
        )
        engine.add_alert_rule(rule)

        # Register custom metric
        def always_high():
            return Metric("test_metric", MetricType.CUSTOM, 100.0)

        engine.register_custom_metric("test_metric", always_high)

        # Collect and notify
        metrics = engine.collect_metrics()
        result = await engine.evaluate_and_notify_alerts(metrics)

        assert "alerts" in result
        assert "notification_results" in result

    def test_alert_lifecycle(self):
        """Test complete alert lifecycle."""
        manager = AlertManager()

        # Add rule
        rule = AlertRule(
            name="test_rule",
            metric_name="cpu_usage",
            condition=">",
            threshold=0.0,  # Will always trigger
            severity=AlertSeverity.WARNING,
            message_template="CPU: {value}%",
        )
        manager.add_rule(rule)

        # Trigger alert
        metric = Metric("cpu_usage", MetricType.CPU_USAGE, 50.0)
        alerts = manager.evaluate_metric(metric)
        assert len(alerts) > 0

        alert_id = alerts[0].id

        # Acknowledge
        success = manager.acknowledge_alert(alert_id)
        assert success

        # Resolve
        success = manager.resolve_alert(alert_id)
        assert success

        # Check it's no longer active
        active = manager.get_active_alerts()
        assert len(active) == 0


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.slow
@pytest.mark.resilience
class TestPerformance:
    """Performance tests for monitoring system."""

    def test_metric_collection_performance(self):
        """Test metric collection speed."""
        engine = MonitoringEngine()

        start = time.time()
        for _ in range(10):
            engine.collect_metrics()
        duration = time.time() - start

        # Should be reasonably fast (< 2 seconds for 10 collections)
        assert duration < 2.0

    def test_history_storage_performance(self):
        """Test history storage with large datasets."""
        history = MetricHistory(max_size=10000)

        start = time.time()
        for i in range(10000):
            metric = Metric("test", MetricType.CUSTOM, float(i))
            history.add(metric)
        duration = time.time() - start

        # Should handle 10k metrics quickly
        assert duration < 1.0

    def test_alert_evaluation_performance(self):
        """Test alert evaluation speed."""
        manager = AlertManager()

        # Add multiple rules
        for i in range(10):
            rule = AlertRule(
                name=f"rule_{i}",
                metric_name="test",
                condition=">",
                threshold=50.0,
                severity=AlertSeverity.INFO,
                message_template="Test",
            )
            manager.add_rule(rule)

        metric = Metric("test", MetricType.CUSTOM, 75.0)

        start = time.time()
        for _ in range(100):
            manager.evaluate_metric(metric)
        duration = time.time() - start

        # Should evaluate 100 metrics quickly
        assert duration < 0.5
