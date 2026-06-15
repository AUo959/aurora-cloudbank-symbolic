# Resilience Sentinel Dashboard Guide

**Real-time Monitoring, Alerting & Health Tracking for Aurora CloudBank**

Anchor: T1-RSD-DOCS-001  
Version: 0.2.0  
Status: Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [Core Concepts](#core-concepts)
5. [Metrics System](#metrics-system)
6. [Alert Management](#alert-management)
7. [Notification Channels](#notification-channels)
8. [API Reference](#api-reference)
9. [Integration Guide](#integration-guide)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Overview

Resilience Sentinel Dashboard provides comprehensive real-time monitoring and alerting for Aurora CloudBank Symbolic. It tracks system health, collects performance metrics, evaluates alert rules, and delivers notifications through multiple channels.

### Key Features

✅ **System Metrics** - CPU, memory, disk monitoring via `psutil`  
✅ **Custom Metrics** - Register application-specific metrics  
✅ **Alert Rules** - Threshold-based alert generation with cooldowns  
✅ **Multi-Channel Notifications** - Log, console, webhook, email  
✅ **Health Status** - Aggregated health evaluation (healthy/degraded/unhealthy/critical)  
✅ **Historical Data** - Rolling window metric storage  
✅ **WebSocket Streaming** - Real-time dashboard updates  
✅ **REST API** - Complete programmatic access  

### Architecture

```
MonitoringEngine (Orchestrator)
├── MetricCollector → Gathers system & custom metrics
├── MetricHistory → Stores rolling window of data
├── AlertManager → Evaluates rules & generates alerts
└── NotificationRouter → Delivers alerts to channels
```

---

## Quick Start

### Basic Usage

```python
from modules.resilience_sentinel import MonitoringEngine

# Create monitoring engine
engine = MonitoringEngine(
    collection_interval=60,  # Collect metrics every 60 seconds
    history_size=1000,       # Store last 1000 metrics per type
    enable_default_rules=True,  # Load default alert rules
    enable_notifications=True,  # Enable alert notifications
)

# Collect metrics
metrics = engine.collect_metrics()
print(f"Collected {len(metrics)} metrics")

# Evaluate alerts
alerts = engine.evaluate_alerts(metrics)
print(f"Triggered {len(alerts)} alerts")

# Check health
status = engine.run_health_checks()
print(f"System health: {status.value}")

# Get dashboard data
dashboard = engine.get_dashboard_data()
```

### FastAPI Integration

```python
from fastapi import FastAPI
from modules.resilience_sentinel.api import router as sentinel_router

app = FastAPI()
app.include_router(sentinel_router)

# Access at:
# - GET /sentinel/health
# - GET /sentinel/metrics
# - GET /sentinel/alerts
# - WS /sentinel/ws/metrics
```

### Command Line Quick Check

```bash
# Run monitoring engine
python -c "
from modules.resilience_sentinel import MonitoringEngine
engine = MonitoringEngine()
engine.collect_metrics()
print(engine.get_health_report())
"
```

---

## Installation

### Requirements

- Python 3.11+
- psutil (for system metrics)
- FastAPI 0.117+ (for API endpoints)
- pytest (for tests)

### Install Dependencies

```bash
pip install psutil fastapi uvicorn
```

### Module Import

```python
from modules.resilience_sentinel import (
    MonitoringEngine,
    MetricCollector,
    HealthStatus,
    AlertManager,
    AlertRule,
    AlertSeverity,
    MetricType,
    Metric,
    NotificationRouter,
)
```

---

## Core Concepts

### Metrics

Metrics are timestamped measurements of system or application state.

**Metric Types:**
- `CPU_USAGE` - CPU utilization percentage
- `MEMORY_USAGE` - Memory utilization percentage  
- `DISK_USAGE` - Disk space utilization
- `REQUEST_COUNT` - API request count
- `ERROR_RATE` - Error percentage
- `RESPONSE_TIME` - Response time in ms
- `HEALTH_SCORE` - Overall health score
- `CUSTOM` - User-defined metrics

**Metric Structure:**
```python
Metric(
    name="cpu_usage",
    type=MetricType.CPU_USAGE,
    value=75.5,
    timestamp=1234567890.0,
    unit="percent",
    tags={"source": "psutil", "host": "server1"}
)
```

### Alert Rules

Alert rules define conditions that trigger notifications.

**Rule Components:**
- **name**: Unique identifier
- **metric_name**: Metric to monitor
- **condition**: Comparison operator (`>`, `<`, `>=`, `<=`, `==`, `!=`)
- **threshold**: Trigger value
- **severity**: INFO, WARNING, ERROR, CRITICAL
- **message_template**: Alert message with `{value}` and `{threshold}` placeholders
- **cooldown_seconds**: Minimum time between alerts (prevents spam)

**Example:**
```python
AlertRule(
    name="high_cpu",
    metric_name="cpu_usage",
    condition=">",
    threshold=80.0,
    severity=AlertSeverity.WARNING,
    message_template="CPU usage is {value:.1f}% (threshold: {threshold}%)",
    cooldown_seconds=300,  # 5 minutes
)
```

### Health Status

Aggregated system health evaluation based on multiple checks.

**Status Levels:**
- `HEALTHY` - All systems normal
- `DEGRADED` - Minor issues detected
- `UNHEALTHY` - Significant issues
- `CRITICAL` - System in critical state
- `UNKNOWN` - Unable to determine health

### Notifications

Multi-channel alert delivery system with severity-based routing.

**Available Channels:**
- **Log** - Python logging integration
- **Console** - Color-coded terminal output
- **Webhook** - HTTP POST to external services
- **Email** - SMTP email notifications
- **Custom** - User-defined handlers

---

## Metrics System

### System Metrics Collection

```python
collector = MetricCollector()

# Individual metrics
cpu = collector.collect_cpu_usage()
memory = collector.collect_memory_usage()
disk = collector.collect_disk_usage("/")

# All system metrics
metrics = collector.collect_all_system_metrics()
```

### Custom Metrics

```python
from modules.resilience_sentinel import Metric, MetricType

# Define custom collector
def collect_queue_depth():
    queue_size = get_queue_size()  # Your implementation
    return Metric(
        name="queue_depth",
        type=MetricType.QUEUE_DEPTH,
        value=float(queue_size),
        unit="count",
        tags={"queue": "main"},
    )

# Register with engine
engine.register_custom_metric("queue_depth", collect_queue_depth)

# Collect all metrics (system + custom)
all_metrics = engine.collect_metrics()
```

### Metric History

```python
# Get latest value
latest = engine.history.get_latest("cpu_usage")
print(f"Current CPU: {latest.value}%")

# Get statistics
stats = engine.history.get_stats("cpu_usage")
print(f"Average: {stats['average']}")
print(f"Min: {stats['min']}, Max: {stats['max']}")
print(f"Trend: {stats['trend']}")  # increasing/decreasing/stable

# Get historical data
recent_100 = engine.history.get_recent("cpu_usage", count=100)
```

### Rolling Window Storage

Metric history uses a fixed-size rolling window (configurable via `history_size`):

```python
engine = MonitoringEngine(history_size=1000)  # Keep last 1000 metrics per type
```

Older metrics are automatically discarded when the window is full, keeping memory usage bounded.

---

## Alert Management

### Creating Alert Rules

```python
from modules.resilience_sentinel import AlertRule, AlertSeverity

# High memory warning
memory_rule = AlertRule(
    name="high_memory",
    metric_name="memory_usage",
    condition=">",
    threshold=85.0,
    severity=AlertSeverity.WARNING,
    message_template="Memory usage at {value:.1f}% (threshold: {threshold}%)",
    cooldown_seconds=300,
)

engine.add_alert_rule(memory_rule)
```

### Default Alert Rules

The engine comes with pre-configured rules:

- **high_cpu**: Warning at >80% CPU
- **critical_cpu**: Critical at >95% CPU
- **high_memory**: Warning at >85% memory
- **high_error_rate**: Error at >5% error rate
- **low_health_score**: Warning at <80 health score

Disable with `enable_default_rules=False`.

### Alert Lifecycle

```python
# Collect metrics and evaluate
metrics = engine.collect_metrics()
alerts = engine.evaluate_alerts(metrics)

# Access alert details
for alert in alerts:
    print(f"[{alert.severity.value}] {alert.title}")
    print(f"Message: {alert.message}")
    print(f"Metric: {alert.metric_name} = {alert.metric_value}")
    
# Acknowledge alert
engine.alert_manager.acknowledge_alert(alert.id)

# Resolve alert
engine.alert_manager.resolve_alert(alert.id)

# Query active alerts
active = engine.alert_manager.get_active_alerts()
critical_only = engine.alert_manager.get_active_alerts(AlertSeverity.CRITICAL)
```

### Alert Cooldowns

Cooldowns prevent alert spam by blocking repeated alerts for the same rule within a time window:

```python
rule = AlertRule(
    name="test",
    metric_name="test",
    condition=">",
    threshold=50.0,
    severity=AlertSeverity.INFO,
    message_template="Test",
    cooldown_seconds=300,  # Wait 5 minutes before re-triggering
)
```

---

## Notification Channels

### Configuration

```python
from modules.resilience_sentinel.notifications import (
    NotificationConfig,
    NotificationRouter,
    LogNotificationChannel,
    ConsoleNotificationChannel,
    AlertSeverity,
)

router = NotificationRouter()

# Log all alerts
log_config = NotificationConfig(
    channel_type="log",
    name="main_log",
    enabled=True,
    severity_filter=None,  # All severities
)
router.register_channel(LogNotificationChannel(log_config))

# Console for critical only
console_config = NotificationConfig(
    channel_type="console",
    name="critical_console",
    enabled=True,
    severity_filter=[AlertSeverity.CRITICAL, AlertSeverity.ERROR],
)
router.register_channel(ConsoleNotificationChannel(console_config))
```

### Notification Routing

```python
# Route alert to all channels
alert = alerts[0]
results = await router.route_alert(alert)

# Check delivery status
for channel_name, success in results.items():
    print(f"{channel_name}: {'✓' if success else '✗'}")
```

### Custom Notification Handlers

```python
from modules.resilience_sentinel.notifications import CustomNotificationChannel

async def slack_handler(alert):
    # Post to Slack webhook
    payload = {
        "text": f"Alert: {alert.title}",
        "attachments": [{
            "color": "danger" if alert.severity == AlertSeverity.CRITICAL else "warning",
            "fields": [
                {"title": "Severity", "value": alert.severity.value},
                {"title": "Message", "value": alert.message},
            ]
        }]
    }
    # await post_to_slack(payload)
    return True

config = NotificationConfig(channel_type="custom", name="slack")
channel = CustomNotificationChannel(config, handler=slack_handler)
router.register_channel(channel)
```

### Notification History

```python
# View recent notifications
history = router.get_notification_history(limit=50)

for record in history:
    print(f"Alert {record['alert_id']} → {record['channel']}: {record['success']}")
```

---

## API Reference

### REST Endpoints

#### Health & Metrics

**GET `/sentinel/health`**
```python
response = {
    "status": "healthy",  # healthy/degraded/unhealthy/critical/unknown
    "timestamp": 1234567890.0,
    "checks": [
        {
            "name": "cpu",
            "status": "healthy",
            "value": 45.2,
            "threshold": 70.0,
            "message": "CPU usage: 45.2%"
        }
    ],
    "alerts": {
        "active": 2,
        "unacknowledged": 1
    }
}
```

**GET `/sentinel/metrics`**
```python
response = {
    "total_metrics": 3,
    "metric_names": ["cpu_usage", "memory_usage", "disk_usage"],
    "total_data_points": 1500,
    "last_collection": 1234567890.0,
    "metrics_stats": {
        "cpu_usage": {
            "average": 55.3,
            "min": 20.1,
            "max": 89.5,
            "trend": "stable"
        }
    }
}
```

**GET `/sentinel/metrics/{name}`**
```python
# GET /sentinel/metrics/cpu_usage
response = {
    "metric_name": "cpu_usage",
    "count": 500,
    "latest": 67.2,
    "average": 55.3,
    "min": 20.1,
    "max": 89.5,
    "trend": "increasing"
}
```

**GET `/sentinel/metrics/{name}/history?count=100`**
```python
response = [
    {
        "name": "cpu_usage",
        "type": "cpu_usage",
        "value": 67.2,
        "timestamp": 1234567890.0,
        "datetime": "2025-10-26T12:00:00",
        "unit": "percent",
        "tags": {"source": "psutil"}
    }
]
```

**POST `/sentinel/metrics/collect`**

Manually trigger metric collection:
```python
response = {
    "success": True,
    "metrics_collected": 5,
    "alerts_triggered": 1,
    "metrics": [...],
    "alerts": [...]
}
```

#### Alerts

**GET `/sentinel/alerts?active_only=true&severity=critical`**
```python
response = {
    "alerts": [
        {
            "id": "alert_1_1234567890",
            "severity": "critical",
            "title": "Critical CPU Usage - cpu_usage",
            "message": "CPU usage critical at 96.5% (threshold: 95.0%)",
            "metric_name": "cpu_usage",
            "metric_value": 96.5,
            "threshold": 95.0,
            "acknowledged": False,
            "resolved": False
        }
    ],
    "count": 1,
    "stats": {
        "total_alerts": 10,
        "active_alerts": 1,
        "by_severity": {
            "critical": 1,
            "error": 0,
            "warning": 2,
            "info": 0
        }
    }
}
```

**POST `/sentinel/alerts/acknowledge`**
```python
request = {"alert_id": "alert_1_1234567890"}
response = {"success": True, "message": "Alert alert_1_1234567890 acknowledged"}
```

**POST `/sentinel/alerts/resolve`**
```python
request = {"alert_id": "alert_1_1234567890"}
response = {"success": True, "message": "Alert alert_1_1234567890 resolved"}
```

#### Alert Rules

**GET `/sentinel/alerts/rules`**
```python
response = [
    {
        "name": "high_cpu",
        "metric_name": "cpu_usage",
        "condition": ">",
        "threshold": 80.0,
        "severity": "warning",
        "message_template": "CPU usage is {value:.1f}%",
        "cooldown_seconds": 300,
        "enabled": True
    }
]
```

**POST `/sentinel/alerts/rules`**
```python
request = {
    "name": "custom_rule",
    "metric_name": "queue_depth",
    "condition": ">",
    "threshold": 100.0,
    "severity": "warning",
    "message_template": "Queue depth: {value}",
    "cooldown_seconds": 600,
    "enabled": True,
    "tags": {"team": "backend"}
}
response = {"success": True, "rule": {...}}
```

**DELETE `/sentinel/alerts/rules/{name}`**
```python
response = {"success": True, "message": "Rule 'custom_rule' deleted"}
```

#### Notifications

**GET `/sentinel/notifications/status`**
```python
response = {
    "enabled": True,
    "channels": {
        "default_log": {
            "enabled": True,
            "type": "log",
            "severity_filter": None
        },
        "critical_console": {
            "enabled": True,
            "type": "console",
            "severity_filter": ["critical", "error"]
        }
    },
    "recent_notifications": [...]
}
```

**GET `/sentinel/notifications/history?limit=50`**
```python
response = {
    "enabled": True,
    "history": [
        {
            "alert_id": "alert_1_1234567890",
            "channel": "default_log",
            "success": True,
            "timestamp": 1234567890.0,
            "severity": "critical"
        }
    ]
}
```

#### Dashboard

**GET `/sentinel/dashboard`**

Comprehensive snapshot for dashboard UI:
```python
response = {
    "health": {...},    # Health report
    "metrics": {...},   # Metrics summary
    "alerts": {...},    # Alert stats
    "recent_alerts": [...],  # Last 10 alerts
    "system": {
        "collection_interval": 60,
        "history_size": 1000,
        "rules_enabled": 5
    }
}
```

### WebSocket

**WS `/sentinel/ws/metrics`**

Real-time metric streaming:
```python
# Connect
ws = websocket.connect("ws://localhost:8000/sentinel/ws/metrics")

# Receive updates
message = ws.recv()
data = json.loads(message)

if data["type"] == "dashboard_update":
    # Full dashboard snapshot
    dashboard = data["data"]
    
elif data["type"] == "new_alerts":
    # New alerts triggered
    alerts = data["alerts"]
```

---

## Integration Guide

### Aurora API Integration

Add Resilience Sentinel router to `aurora_api.py`:

```python
from fastapi import FastAPI
from modules.resilience_sentinel.api import router as sentinel_router

app = FastAPI(title="Aurora CloudBank API")

# Include Resilience Sentinel endpoints
app.include_router(sentinel_router, tags=["Monitoring"])

# Endpoints available at /sentinel/*
```

### Background Monitoring Task

```python
import asyncio
from modules.resilience_sentinel import MonitoringEngine

async def background_monitor():
    engine = MonitoringEngine(
        collection_interval=60,
        enable_notifications=True
    )
    
    while True:
        # Collect metrics
        metrics = engine.collect_metrics()
        
        # Evaluate and notify
        result = await engine.evaluate_and_notify_alerts(metrics)
        
        # Wait for next collection
        await asyncio.sleep(engine.collection_interval)

# Start background task
asyncio.create_task(background_monitor())
```

### Custom Metric Integration

```python
# Application metrics
def collect_api_metrics():
    return Metric(
        name="api_request_count",
        type=MetricType.REQUEST_COUNT,
        value=float(get_request_count()),
        tags={"endpoint": "/api/data"}
    )

def collect_cache_hit_rate():
    return Metric(
        name="cache_hit_rate",
        type=MetricType.CACHE_HIT_RATE,
        value=calculate_cache_hit_rate(),
        unit="percent"
    )

# Register with engine
engine.register_custom_metric("api_requests", collect_api_metrics)
engine.register_custom_metric("cache_hits", collect_cache_hit_rate)
```

---

## Configuration

### Engine Configuration

```python
engine = MonitoringEngine(
    collection_interval=60,      # Seconds between collections
    history_size=1000,            # Max metrics per type
    enable_default_rules=True,    # Load preset alert rules
    enable_notifications=True,    # Enable notification delivery
)
```

### Alert Rule Configuration

```python
# Conservative (fewer false positives)
rule = AlertRule(
    name="conservative_cpu",
    metric_name="cpu_usage",
    condition=">",
    threshold=90.0,               # High threshold
    severity=AlertSeverity.WARNING,
    message_template="CPU: {value}%",
    cooldown_seconds=600,         # 10 minute cooldown
)

# Aggressive (catch issues early)
rule = AlertRule(
    name="aggressive_cpu",
    metric_name="cpu_usage",
    condition=">",
    threshold=70.0,               # Low threshold
    severity=AlertSeverity.INFO,
    message_template="CPU: {value}%",
    cooldown_seconds=60,          # 1 minute cooldown
)
```

### Notification Configuration

```python
# Production: Log everything, console for critical
production_config = [
    NotificationConfig("log", "main_log", enabled=True),
    NotificationConfig("console", "critical", enabled=True, 
                      severity_filter=[AlertSeverity.CRITICAL])
]

# Development: Console for all
dev_config = [
    NotificationConfig("console", "dev", enabled=True)
]
```

---

## Troubleshooting

### No Metrics Collected

**Issue:** `engine.collect_metrics()` returns empty list

**Solutions:**
1. Check psutil is installed: `pip install psutil`
2. Verify custom metric collectors return `Metric` objects
3. Check for exceptions in custom collectors

### Alerts Not Triggering

**Issue:** Metrics collected but no alerts generated

**Solutions:**
1. Verify alert rules are added: `engine.alert_manager.get_all_rules()`
2. Check rule metric names match collected metrics
3. Verify thresholds are triggerable
4. Check rule cooldown hasn't blocked alerts

### Notifications Not Sending

**Issue:** Alerts trigger but notifications don't deliver

**Solutions:**
1. Check notifications enabled: `enable_notifications=True`
2. Verify channels registered: `router.list_channels()`
3. Check severity filters: `config.should_notify(alert)`
4. Review notification history: `router.get_notification_history()`

### WebSocket Disconnects

**Issue:** WebSocket connection drops frequently

**Solutions:**
1. Implement reconnection logic in client
2. Check network stability
3. Verify collection interval isn't too short (causing data flood)
4. Monitor server resources

### High Memory Usage

**Issue:** Monitoring system consuming too much memory

**Solutions:**
1. Reduce `history_size` parameter
2. Clear resolved alerts: `manager.clear_resolved_alerts()`
3. Limit notification history: `router.clear_history()`
4. Reduce custom metric frequency

---

## Best Practices

### Alert Rule Design

1. **Start Conservative** - Higher thresholds, longer cooldowns
2. **Severity Hierarchy** - Use INFO for monitoring, WARNING for attention, ERROR for action, CRITICAL for immediate response
3. **Clear Messages** - Include context, values, and thresholds
4. **Reasonable Cooldowns** - Balance between notification fatigue and timely alerts

### Metric Collection

1. **Efficient Collectors** - Keep custom collectors fast (<100ms)
2. **Appropriate Intervals** - 60s for most metrics, 300s for slow-changing
3. **Meaningful Tags** - Add context for filtering and analysis
4. **Bounded History** - Use reasonable `history_size` (500-2000)

### Notification Management

1. **Severity Filters** - Route critical alerts to immediate channels (SMS, PagerDuty)
2. **Aggregation** - Batch similar alerts to reduce noise
3. **Escalation** - Increase severity if issues persist
4. **Testing** - Test notification channels regularly

### Performance

1. **Async Operations** - Use `evaluate_and_notify_alerts()` for concurrent notification delivery
2. **Background Tasks** - Run monitoring in separate async tasks
3. **Caching** - MetricHistory caches stats automatically
4. **Resource Limits** - Monitor the monitoring system itself

### Security

1. **Access Control** - Protect API endpoints with authentication
2. **Sensitive Data** - Avoid logging sensitive info in alerts
3. **Webhook Security** - Use HTTPS and verify webhooks
4. **Rate Limiting** - Prevent notification spam attacks

---

## Appendix

### Metric Type Reference

| Type | Description | Unit | Range |
|------|-------------|------|-------|
| CPU_USAGE | CPU utilization | percent | 0-100 |
| MEMORY_USAGE | Memory utilization | percent | 0-100 |
| DISK_USAGE | Disk space used | percent | 0-100 |
| REQUEST_COUNT | API requests | count | 0+ |
| ERROR_RATE | Error percentage | percent | 0-100 |
| RESPONSE_TIME | Response latency | ms | 0+ |
| HEALTH_SCORE | Overall health | score | 0-100 |
| CUSTOM | User-defined | varies | varies |

### Alert Severity Guidelines

| Severity | Use Case | Response Time | Examples |
|----------|----------|---------------|----------|
| INFO | Informational | None | Metric thresholds crossed, routine events |
| WARNING | Attention needed | Hours | High resource usage, degraded performance |
| ERROR | Action required | Minutes | Service errors, repeated failures |
| CRITICAL | Immediate response | Seconds | System down, data loss risk, security breach |

### API Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Metric/alert/rule doesn't exist |
| 500 | Internal Error | Server error |

---

## Support & Resources

- **GitHub**: [aurora-cloudbank-symbolic](https://github.com/AUo959/aurora-cloudbank-symbolic)
- **Tests**: `tests/test_resilience_sentinel.py` (37 tests, 100% pass rate)
- **API Docs**: Run server and visit `/docs` for interactive API documentation

**Anchor**: T1-RSD-DOCS-001  
**Version**: 0.2.0  
**Last Updated**: October 2025  
**Maintainer**: Aurora CloudBank Team
