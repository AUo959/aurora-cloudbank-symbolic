# Telemetry and Observability

## Overview

Aurora CloudBank Symbolic now includes comprehensive telemetry and observability capabilities, providing insights into:
- System performance and operation metrics
- Feature adoption and usage patterns
- Error tracking and anomaly detection
- Resource utilization monitoring

## Architecture

The telemetry system consists of two main components:

1. **Aurora Core Telemetry** (`src/observability/telemetry.py`)
   - General-purpose OpenTelemetry integration
   - Prometheus metrics export
   - Performance and adoption tracking

2. **R-2 Agent Telemetry** (`src/observability/r2_agent_telemetry.py`)
   - Agent-specific operation tracking
   - Anomaly detection with statistical analysis
   - PII filtering for privacy preservation
   - Detailed resource usage monitoring

## Telemetry Endpoints

### Core Telemetry

#### `GET /metrics`
Prometheus-compatible metrics endpoint for standard telemetry.

**Response Format:** Prometheus text exposition format

**Metrics Provided:**
- `aurora_operations_total{operation="..."}` - Total operation count by type
- `aurora_feature_usage_total{feature="..."}` - Feature usage count

**Example:**
```bash
curl http://localhost:8000/metrics
```

**Response:**
```prometheus
# HELP aurora_operations_total Total count of operations
# TYPE aurora_operations_total counter
aurora_operations_total{operation="GET_health"} 5
aurora_operations_total{operation="POST_geometric_vector"} 12

# HELP aurora_feature_usage_total Feature usage count
# TYPE aurora_feature_usage_total counter
aurora_feature_usage_total{feature="geometric_algebra_api"} 12
aurora_feature_usage_total{feature="agent_mode_api"} 8
```

#### `GET /telemetry/snapshot`
Get structured JSON snapshot of current telemetry metrics.

**Query Parameters:**
- `context_tag` (optional): DLP context tag for lineage tracking

**Response:**
```json
{
  "timestamp": 1700000000.0,
  "performance_metrics": {
    "GET_health_avg_ms": 2.5,
    "GET_health_count": 5,
    "POST_geometric_vector_avg_ms": 15.3,
    "POST_geometric_vector_count": 12
  },
  "adoption_metrics": {
    "geometric_algebra_api": 12,
    "agent_mode_api": 8,
    "memory_api": 3
  },
  "error_metrics": {
    "api_call:ValueError": 2,
    "operation:HTTPException": 1
  },
  "context_tag": "my_context_tag"
}
```

### R-2 Agent Telemetry

#### `GET /r2-telemetry/metrics`
Prometheus metrics specifically for R-2 agent operations.

**Response Format:** Prometheus text exposition format

**Metrics Provided:**
- `r2_agent_operations_total` - Total agent operations
- `r2_agent_operations_success` - Successful operations
- `r2_agent_anomalies_detected` - Detected anomalies

**Example:**
```bash
curl http://localhost:8000/r2-telemetry/metrics
```

#### `GET /r2-telemetry/health`
Health status of the R-2 telemetry system.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-18T15:30:00.000Z",
  "telemetry_enabled": true,
  "service_name": "aurora-r2-agent",
  "recent_metrics": {
    "success_rate": 0.95,
    "total_operations": 150,
    "anomaly_count": 2,
    "average_duration_ms": 45.3
  }
}
```

**Status Values:**
- `healthy`: Success rate ≥ 95%, no anomalies
- `degraded`: Success rate ≥ 80%
- `unhealthy`: Success rate < 80%

#### `GET /r2-telemetry/summary`
Comprehensive metrics summary for R-2 agent operations.

**Query Parameters:**
- `time_window` (default: 3600): Time window in seconds to summarize
- `context_tag` (optional): DLP context tag

**Response:**
```json
{
  "total_operations": 150,
  "successful_operations": 143,
  "failed_operations": 7,
  "success_rate": 0.953,
  "average_duration_ms": 45.3,
  "anomaly_count": 2,
  "operations_by_type": {
    "dependency_audit": 50,
    "health_check": 75,
    "security_scan": 25
  },
  "context_tag": "my_context_tag"
}
```

#### `GET /r2-telemetry/operations/recent`
Get list of recent R-2 agent operations.

**Query Parameters:**
- `limit` (default: 10, max: 100): Number of operations to return
- `operation_type` (optional): Filter by specific operation type
- `failures_only` (default: false): Only return failed operations

**Response:**
```json
[
  {
    "operation_id": "op_12345",
    "operation_type": "dependency_audit",
    "start_time": 1700000000.0,
    "duration_ms": 45.3,
    "success": true,
    "decisions_made": 5,
    "tools_invoked": ["npm_audit", "pip_check"],
    "context_tag": "audit_001"
  }
]
```

#### `GET /r2-telemetry/anomalies`
Get recently detected anomalies in R-2 agent operations.

**Query Parameters:**
- `limit` (default: 20, max: 100): Number of anomalies to return

**Response:**
```json
[
  {
    "is_anomalous": true,
    "anomaly_score": 3.5,
    "anomaly_type": "duration_ms",
    "threshold": 2.0,
    "baseline_value": 45.0,
    "current_value": 350.0,
    "details": {
      "operation_id": "op_12345",
      "operation_type": "security_scan"
    }
  }
]
```

#### `GET /r2-telemetry/operations/types`
Get statistics for all tracked operation types.

**Response:**
```json
{
  "total_types": 3,
  "operations": {
    "dependency_audit": {
      "count": 50,
      "success_rate": 0.96
    },
    "health_check": {
      "count": 75,
      "success_rate": 0.99
    },
    "security_scan": {
      "count": 25,
      "success_rate": 0.88
    }
  }
}
```

#### `POST /r2-telemetry/test-operation`
Test endpoint to generate sample telemetry data (useful for testing monitoring systems).

**Query Parameters:**
- `operation_type` (default: "test"): Type of operation to simulate
- `should_fail` (default: false): Whether to simulate a failure

**Response:**
```json
{
  "success": true,
  "message": "Test operation completed successfully",
  "operation_id": "op_test_123",
  "correlation_id": "r2-test-456"
}
```

## Automatic Request Tracing

All HTTP requests are automatically traced via middleware, which:
- Records request duration
- Tracks HTTP method and path
- Records errors and exceptions
- Classifies requests by feature area (geometric, agent, memory, quantum APIs)

No code changes required - tracing happens automatically for all endpoints.

## Integration with Monitoring Systems

### Prometheus Setup

1. **Configure Prometheus to scrape Aurora metrics:**

```yaml
scrape_configs:
  - job_name: 'aurora-cloudbank'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'

  - job_name: 'aurora-r2-agent'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/r2-telemetry/metrics'
```

2. **View metrics in Prometheus UI:**
   - Navigate to `http://localhost:9090`
   - Query: `aurora_operations_total`
   - Query: `r2_agent_operations_total`

### Grafana Dashboards

Example queries for Grafana dashboards:

**Operation Rate:**
```promql
rate(aurora_operations_total[5m])
```

**R-2 Agent Success Rate:**
```promql
r2_agent_operations_success / r2_agent_operations_total
```

**Anomaly Detection Rate:**
```promql
rate(r2_agent_anomalies_detected[1h])
```

## Data Lineage Protocol (DLP) Integration

All telemetry endpoints support DLP tracking via the `context_tag` parameter:

```bash
# Tag metrics export with DLP context
curl "http://localhost:8000/telemetry/snapshot?context_tag=deployment_v2.1.0"

# Tag R-2 summary with audit context
curl "http://localhost:8000/r2-telemetry/summary?context_tag=security_audit_2025Q1"
```

Context tags are included in all metric snapshots and can be used to:
- Track metrics across deployment versions
- Link telemetry to specific operations or audits
- Maintain lineage for compliance and governance

## Privacy and Security

### PII Filtering

R-2 Agent Telemetry includes automatic PII filtering to protect sensitive data:

**Redacted Fields:**
- Emails, API keys, tokens
- Passwords, secrets
- Social Security Numbers
- Credit card numbers
- Phone numbers

**Example:**
```python
# Original data
{"email": "user@example.com", "api_key": "secret123"}

# Filtered in telemetry
{"email": "[REDACTED]", "api_key": "[REDACTED]"}
```

### Anomaly Detection

Statistical anomaly detection identifies unusual patterns:
- Duration anomalies (operations taking unusually long)
- High failure rate detection
- Resource usage spikes
- Z-score based threshold detection (default: 2.0σ)

## Testing

Run telemetry integration tests:

```bash
# All telemetry tests
pytest tests/test_telemetry.py tests/test_r2_telemetry.py tests/test_telemetry_integration.py -v

# Integration tests only
pytest tests/test_telemetry_integration.py -v

# Quick smoke test
pytest tests/test_telemetry_integration.py::test_health_endpoint_still_works -v
```

## Troubleshooting

### Metrics not appearing

**Check telemetry initialization:**
```python
from src.observability import get_telemetry
telemetry = get_telemetry()
print(f"Telemetry enabled: {telemetry.enabled}")
```

**Check for OpenTelemetry:**
```bash
pip list | grep opentelemetry
```

If OpenTelemetry is not installed, telemetry falls back to internal tracking only.

### R-2 telemetry routes not found

Verify R-2 telemetry router is loaded in logs:
```
✅ R2 Telemetry API routes integrated successfully
```

If not present, check import errors in startup logs.

### High anomaly count

Anomalies may indicate:
- Performance degradation (check operation durations)
- Increased error rates (review error logs)
- Resource constraints (monitor CPU/memory)

Review anomalies:
```bash
curl http://localhost:8000/r2-telemetry/anomalies?limit=10
```

## Related Documentation

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Export Format](https://prometheus.io/docs/instrumenting/exposition_formats/)
- [DLP (Data Lineage Protocol)](../TICKET_DLP_AUTO_TRACKING.md)
- [R-2 Agent Documentation](../docs/R2_AGENT.md)

## Future Enhancements

Planned improvements:
- [ ] Distributed tracing with Jaeger/Zipkin export
- [ ] Custom dashboard for Aurora-specific metrics
- [ ] Alert rules and notification integration
- [ ] Historical metric storage and trend analysis
- [ ] Integration with cloud-native monitoring (Datadog, New Relic)
