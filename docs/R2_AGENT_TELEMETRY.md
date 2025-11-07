# R-2 Agent Production Telemetry Integration

## Overview

The R-2 Agent Production Telemetry Integration provides comprehensive observability for R-2 agent operations in production environments. It enables monitoring, anomaly detection, performance tracking, and real-time insights into agent behavior.

## Features

### ✅ Distributed Tracing
- **Correlation IDs**: Unique identifiers for distributed operation tracking
- **Context Propagation**: Maintains context across service boundaries
- **OpenTelemetry Integration**: Industry-standard instrumentation
- **Span Attributes**: Rich metadata for operation details

### ✅ Performance Metrics
- **Latency Tracking**: P50, P95, P99 duration percentiles
- **Throughput Monitoring**: Operations per second by type
- **Success Rate Tracking**: Real-time success/failure ratios
- **Resource Usage**: CPU, memory, I/O monitoring per operation

### ✅ Anomaly Detection
- **Statistical Analysis**: Z-score based anomaly detection
- **Threshold Alerts**: Configurable thresholds for critical metrics
- **Pattern Recognition**: Failure rate and performance degradation detection
- **Baseline Comparison**: Compare current vs historical performance

### ✅ Privacy & Security
- **PII Filtering**: Automatic removal of sensitive information
- **Redaction Patterns**: Email, API keys, tokens, credentials
- **Configurable Privacy**: Toggle PII filtering on/off
- **Audit Trail**: Complete DLP context tags for compliance

### ✅ Visualization & Dashboards
- **Grafana Dashboard**: Pre-built operational dashboard
- **Prometheus Export**: Standard metrics format
- **Real-time Monitoring**: 30-second refresh intervals
- **Custom Alerts**: Prometheus alerting rules included

## Installation

### Requirements

```bash
# Core dependencies (already in requirements.txt)
pip install prometheus-client>=0.19.0
pip install psutil>=5.9.0

# Optional OpenTelemetry (in requirements-optional.txt)
pip install opentelemetry-api>=1.21.0
pip install opentelemetry-sdk>=1.21.0
```

### Setup

1. **Import the telemetry module**:

```python
from src.observability import get_r2_telemetry

# Initialize global telemetry instance
telemetry = get_r2_telemetry(
    service_name="r2-agent",
    enable_otel=True,
    enable_anomaly_detection=True,
    enable_pii_filtering=True
)
```

2. **Add to FastAPI application**:

```python
from api.r2_telemetry_routes import router as r2_telemetry_router

app = FastAPI()
app.include_router(r2_telemetry_router)
```

3. **Configure Prometheus scraping** (prometheus.yml):

```yaml
scrape_configs:
  - job_name: 'r2-agent'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/r2-telemetry/metrics'
```

4. **Load alerting rules**:

```yaml
rule_files:
  - "monitoring/prometheus/r2_agent_alerts.yml"
```

5. **Import Grafana dashboard**:

Import `monitoring/grafana/r2_agent_dashboard.json` into your Grafana instance.

## Usage

### Basic Operation Tracing

```python
from src.observability import get_r2_telemetry

telemetry = get_r2_telemetry()

# Trace an R-2 agent operation
with telemetry.trace_agent_operation(
    operation_type="dependency_audit",
    context_tag="audit_2024_q4_001",
    symbolic_anchor="T1:42"
) as metrics:
    # Your R-2 agent logic here
    results = perform_dependency_audit()
    
    # Add operation metadata
    metrics.decisions_made = 5
    metrics.tools_invoked = ["npm_audit", "pip_check"]
    metrics.repositories_accessed = ["main-repo"]
    metrics.artifacts_generated = 1
```

### Capturing Custom Metadata

```python
with telemetry.trace_agent_operation(
    "health_check",
    context_tag="health_2024_001",
    # Additional metadata
    repository="aurora-cloudbank-symbolic",
    branch="main",
    priority="high"
) as metrics:
    status = check_system_health()
    metrics.metadata["status"] = status
```

### Getting Metrics Summary

```python
# Get summary for the last hour
summary = telemetry.get_metrics_summary(time_window_seconds=3600)

print(f"Total Operations: {summary['total_operations']}")
print(f"Success Rate: {summary['success_rate']:.2%}")
print(f"Average Duration: {summary['average_duration_ms']:.2f}ms")
```

### Exporting Prometheus Metrics

```python
# Get metrics in Prometheus format
prometheus_data = telemetry.export_prometheus_metrics()
print(prometheus_data)
```

### Querying Recent Operations

```python
# Get last 10 operations
recent_ops = telemetry.get_recent_operations(limit=10)

# Get only failed operations
failures = telemetry.get_recent_operations(
    limit=20,
    include_failures_only=True
)

# Filter by operation type
audits = telemetry.get_recent_operations(
    limit=10,
    operation_type="dependency_audit"
)
```

## API Endpoints

### GET /r2-telemetry/metrics
Export Prometheus metrics for scraping.

**Response**: Plain text Prometheus format

### GET /r2-telemetry/summary
Get comprehensive metrics summary.

**Query Parameters**:
- `time_window` (optional): Time window in seconds (default: 3600)
- `context_tag` (optional): DLP context tag for export

**Response**:
```json
{
  "service_name": "r2-agent",
  "timestamp": 1699564800.0,
  "total_operations": 150,
  "successful_operations": 145,
  "failed_operations": 5,
  "success_rate": 0.967,
  "average_duration_ms": 234.5,
  "operations_by_type": {
    "dependency_audit": {"count": 50, "success": 49, "failures": 1},
    "health_check": {"count": 100, "success": 96, "failures": 4}
  },
  "anomaly_count": 2
}
```

### GET /r2-telemetry/operations/recent
Get recent operation details.

**Query Parameters**:
- `limit`: Max operations to return (1-100, default: 10)
- `operation_type`: Filter by type
- `failures_only`: Only return failures

### GET /r2-telemetry/health
Get telemetry system health status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-07T19:42:48Z",
  "telemetry_enabled": true,
  "service_name": "r2-agent",
  "recent_metrics": {
    "success_rate": 0.98,
    "total_operations": 50,
    "anomaly_count": 0
  }
}
```

### GET /r2-telemetry/anomalies
Get detected anomalies.

**Query Parameters**:
- `limit`: Max anomalies to return (default: 20)

### POST /r2-telemetry/test-operation
Test endpoint for generating sample telemetry.

**Query Parameters**:
- `operation_type`: Type of test operation
- `should_fail`: Simulate failure

## Anomaly Detection

### Detection Methods

1. **Z-Score Analysis**: Detects statistical outliers in:
   - Operation duration
   - CPU usage
   - Memory consumption

2. **Failure Rate Monitoring**: Alerts when failure rate exceeds 30%

3. **Performance Degradation**: Compares current vs historical baselines

### Configuration

```python
from src.observability.r2_agent_telemetry import AnomalyDetector

detector = AnomalyDetector(
    window_size=100,      # Number of samples to track
    z_threshold=3.0       # Z-score threshold (3.0 = 99.7%)
)
```

### Anomaly Types

- `duration_ms`: Unusually long operation duration
- `cpu_usage`: Abnormally high CPU consumption
- `memory_usage`: Excessive memory usage
- `high_failure_rate`: Elevated failure rate

## Privacy & PII Filtering

### Automatic Redaction

The system automatically redacts:
- Email addresses
- API keys and tokens
- Passwords and secrets
- Credit card numbers
- Phone numbers

### Manual Filtering

```python
from src.observability import PIIFilter

# Filter dictionary data
sensitive_data = {"email": "user@example.com", "api_key": "secret123"}
clean_data = PIIFilter.filter_dict(sensitive_data)
# Result: {"email": "[REDACTED]", "api_key": "[REDACTED]"}

# Filter string content
text = "Contact admin@example.com with token abc123def456"
clean_text = PIIFilter.filter_string(text)
# Result: "Contact [REDACTED] with [REDACTED]"
```

### Disabling PII Filtering

```python
telemetry = R2AgentTelemetry(enable_pii_filtering=False)
```

## Alerting Rules

### Critical Alerts

- **R2AgentHighFailureRate**: >20% failure rate for 5 minutes
- **R2AgentOperationsStalled**: No operations for 10 minutes
- **R2AgentMultipleAnomalies**: >10 anomalies in 1 hour
- **R2AgentHealthCritical**: <50% success rate for 5 minutes

### Warning Alerts

- **R2AgentAnomalyDetected**: Any anomaly detected
- **R2AgentSlowOperations**: P95 duration >5 seconds
- **R2AgentHighCPU**: >80% CPU for 5 minutes
- **R2AgentHighMemory**: >1GB memory for 5 minutes
- **R2AgentHealthDegraded**: <80% success rate for 10 minutes

## Performance Impact

The telemetry system is designed for minimal overhead:

- **Metric Collection**: <1% CPU overhead
- **Memory Usage**: ~10-50MB for operation history
- **Network Impact**: ~1KB/operation for OpenTelemetry export
- **Overall Impact**: <5% performance overhead (meets requirement)

## Best Practices

### 1. Always Use Context Tags

```python
with telemetry.trace_agent_operation(
    "operation_type",
    context_tag=f"operation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
):
    # operation logic
```

### 2. Include Symbolic Anchors

```python
with telemetry.trace_agent_operation(
    "operation_type",
    symbolic_anchor=f"T1:{current_state}"
):
    # operation logic
```

### 3. Track Decision Points

```python
with telemetry.trace_agent_operation("decision_making") as metrics:
    decision = make_decision()
    metrics.decisions_made += 1
    metrics.metadata["decision"] = decision
```

### 4. Monitor Resource-Intensive Operations

```python
with telemetry.trace_agent_operation("heavy_computation") as metrics:
    result = perform_heavy_task()
    # Resource metrics automatically captured
```

### 5. Handle Errors Gracefully

```python
try:
    with telemetry.trace_agent_operation("risky_operation") as metrics:
        result = risky_task()
except Exception as e:
    # Error automatically recorded with type and message
    logger.error("Operation failed: %s", e)
```

## Troubleshooting

### Telemetry Not Recording

1. Check if OpenTelemetry is installed:
   ```python
   from src.observability import OTEL_AVAILABLE
   print(f"OpenTelemetry Available: {OTEL_AVAILABLE}")
   ```

2. Verify telemetry is enabled:
   ```python
   telemetry = get_r2_telemetry()
   print(f"Telemetry Enabled: {telemetry.enabled}")
   ```

3. Check for errors in logs:
   ```bash
   grep "telemetry" application.log
   ```

### Metrics Not Appearing in Prometheus

1. Verify endpoint is accessible:
   ```bash
   curl http://localhost:8000/r2-telemetry/metrics
   ```

2. Check Prometheus scrape configuration
3. Verify network connectivity
4. Check Prometheus logs for scrape errors

### High Memory Usage

1. Limit operation history:
   ```python
   # Periodically clear old metrics
   telemetry._operation_metrics = telemetry._operation_metrics[-1000:]
   ```

2. Reduce anomaly detector window size:
   ```python
   detector = AnomalyDetector(window_size=50)  # Instead of 100
   ```

## DLP Compliance

All telemetry includes DLP tracking:

- **Context Tags**: Every operation has a unique context tag
- **Symbolic Anchors**: Aurora symbolic anchors maintained
- **Correlation IDs**: Distributed tracing support
- **Metadata Preservation**: Complete lineage tracking

Example DLP-compliant export:

```python
summary = telemetry.get_metrics_summary(
    context_tag="dlp_export_q4_2024_001"
)
# Summary includes context_tag for audit trail
```

## Contributing

When adding new operation types:

1. Use descriptive operation names
2. Include relevant metadata
3. Track decision points
4. Maintain DLP compliance
5. Document in operation types registry

## Support

For issues or questions:
- GitHub Issues: https://github.com/AUo959/aurora-cloudbank-symbolic/issues
- Documentation: https://github.com/AUo959/aurora-cloudbank-symbolic/wiki
- Security: See SECURITY.md for security-related issues

## License

See LICENSE file in repository root.
