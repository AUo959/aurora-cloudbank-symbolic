# Aurora OpenTelemetry Integration

## Overview

The Aurora observability module provides comprehensive system monitoring through OpenTelemetry integration, including:

- **Distributed Tracing**: Track request flows across Aurora components
- **Performance Metrics**: Monitor operation latency, throughput, and resources
- **Adoption Analytics**: Track feature usage and user engagement patterns
- **Prometheus Export**: Compatible with standard monitoring stacks
- **DLP Integration**: All metrics tagged with context for lineage tracking

## Installation

### Basic Observability (Fallback Mode)

No additional dependencies required. Basic metrics collection works out of the box:

```python
from src.observability import get_telemetry

telemetry = get_telemetry()
with telemetry.trace_operation("my_operation"):
    # Your code here
    pass
```

### Full OpenTelemetry Support

For distributed tracing and external export:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-prometheus
```

## Quick Start

### Basic Usage

```python
from src.observability import get_telemetry

# Get global telemetry instance
telemetry = get_telemetry("my-service")

# Trace operations
with telemetry.trace_operation("process_request", {"user_id": "123"}):
    # Your code
    result = do_work()

# Track feature usage
telemetry.record_feature_usage("reflection_generation")

# Get metrics snapshot
snapshot = telemetry.get_metrics_snapshot(context_tag="request_xyz")
print(f"Performance: {snapshot.performance_metrics}")
print(f"Usage: {snapshot.adoption_metrics}")
```

### Async Operations

```python
from src.observability import get_telemetry

telemetry = get_telemetry()

@telemetry.trace_async("fetch_data")
async def fetch_data(user_id: str):
    # Automatically traced
    return await database.query(user_id)
```

### FastAPI Integration

```python
from fastapi import FastAPI
from src.observability import get_telemetry

app = FastAPI()
telemetry = get_telemetry("aurora-api")

@app.get("/api/data")
async def get_data():
    with telemetry.trace_operation("api_get_data"):
        telemetry.record_feature_usage("api_endpoint_data")
        return {"status": "ok"}

@app.get("/metrics")
async def metrics():
    """Prometheus-compatible metrics endpoint"""
    return Response(
        content=telemetry.export_prometheus_format(),
        media_type="text/plain"
    )
```

## API Reference

### AuroraTelemetry

Main telemetry class for observability.

```python
telemetry = AuroraTelemetry(
    service_name="aurora-cloudbank",
    enable_prometheus=True
)
```

**Parameters:**
- `service_name` (str): Service identifier for telemetry data
- `enable_prometheus` (bool): Enable Prometheus metric export

#### trace_operation(operation_name, attributes=None)

Context manager for tracing operations.

```python
with telemetry.trace_operation("operation_name", {"key": "value"}):
    # Traced code
    pass
```

**Returns:** Span object (or None in fallback mode)

#### trace_async(operation_name)

Decorator for tracing async functions.

```python
@telemetry.trace_async("async_operation")
async def my_function():
    pass
```

#### record_feature_usage(feature_name, count=1)

Track feature usage for adoption metrics.

```python
telemetry.record_feature_usage("reflection_generation", count=5)
```

#### record_error(operation, error_type)

Record error occurrence.

```python
telemetry.record_error("api_call", "ValueError")
```

#### get_metrics_snapshot(context_tag=None)

Get current metrics snapshot.

```python
snapshot = telemetry.get_metrics_snapshot(context_tag="request_123")
```

**Returns:** `MetricSnapshot` with performance, adoption, and error metrics

#### export_prometheus_format()

Export metrics in Prometheus text format.

```python
prometheus_data = telemetry.export_prometheus_format()
```

**Returns:** String in Prometheus exposition format

### Global Singleton

```python
from src.observability import get_telemetry, reset_telemetry

# Get or create global instance
telemetry = get_telemetry("service-name")

# Reset for testing
reset_telemetry()
```

## Metrics Collected

### Performance Metrics

- **Operation Duration**: Time taken for each operation (histogram)
- **Operation Count**: Number of times each operation executed
- **Average Latency**: Mean operation time in milliseconds

### Adoption Metrics

- **Feature Usage**: Count of feature invocations
- **Active Sessions**: Number of concurrent sessions
- **Workflow Completion**: Success rate of operations

### Error Metrics

- **Error Count**: Errors by operation and type
- **Error Rate**: Percentage of failed operations
- **Exception Types**: Distribution of error types

## Prometheus Integration

### Metrics Endpoint

Add to your FastAPI application:

```python
from fastapi.responses import Response

@app.get("/metrics")
async def prometheus_metrics():
    telemetry = get_telemetry()
    return Response(
        content=telemetry.export_prometheus_format(),
        media_type="text/plain"
    )
```

### Prometheus Configuration

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'aurora-cloudbank'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Example Queries

```promql
# Operation rate
rate(aurora_operations_total[5m])

# Average operation duration
histogram_quantile(0.95, aurora_operation_duration_bucket)

# Feature usage trends
increase(aurora_feature_usage_total[1h])

# Error rate
rate(aurora_errors[5m]) / rate(aurora_operations_total[5m])
```

## DLP Integration

All metrics support DLP context tags for lineage tracking:

```python
from src.core.native_dlp_export import NativeDLPTracker

dlp_tracker = NativeDLPTracker()
context_tag = dlp_tracker.create_tag(
    operation="api_request",
    data={"endpoint": "/data"}
)

snapshot = telemetry.get_metrics_snapshot(context_tag=context_tag)
```

## Testing

Run the observability test suite:

```bash
# All observability tests
pytest -m observability

# Specific test file
pytest tests/test_telemetry.py -v

# With coverage
pytest tests/test_telemetry.py --cov=src/observability
```

## Architecture

### Graceful Degradation

The module uses graceful degradation:

1. **Full Mode**: When OpenTelemetry installed
   - Distributed tracing with spans
   - External metric export
   - Context propagation

2. **Fallback Mode**: When OpenTelemetry unavailable
   - Local metric collection
   - Performance tracking
   - Prometheus export still functional

### Zero Dependencies

Core functionality requires no external dependencies beyond Aurora's standard stack. OpenTelemetry packages are optional enhancements.

## Best Practices

### 1. Use Context Managers

Always use `trace_operation` as a context manager to ensure proper cleanup:

```python
with telemetry.trace_operation("operation"):
    do_work()  # Automatically timed and traced
```

### 2. Add Meaningful Attributes

Include contextual attributes for better observability:

```python
with telemetry.trace_operation("process", {"user_id": user, "type": work_type}):
    process_work()
```

### 3. Track Feature Usage

Record feature usage to understand adoption:

```python
telemetry.record_feature_usage(f"reflection_type_{reflection_type}")
```

### 4. Include DLP Tags

Always include context tags for audit trails:

```python
snapshot = telemetry.get_metrics_snapshot(context_tag=dlp_tag)
```

### 5. Export Regularly

Set up periodic metric export for monitoring:

```python
async def export_metrics():
    snapshot = telemetry.get_metrics_snapshot()
    await store_metrics(snapshot)
```

## Troubleshooting

### OpenTelemetry Not Available

If you see warnings about OpenTelemetry:

```
WARNING: OpenTelemetry not available - install with: pip install opentelemetry-api...
```

**Solution:** Either install OpenTelemetry packages or continue using fallback mode (metrics still collected locally).

### Prometheus Export Empty

If `/metrics` endpoint returns no data:

1. Ensure operations have been traced: `with telemetry.trace_operation(...)`
2. Check feature usage recorded: `telemetry.record_feature_usage(...)`
3. Verify telemetry initialized: `telemetry = get_telemetry()`

### High Memory Usage

If metrics collection uses too much memory:

1. Clear metric history periodically:
   ```python
   telemetry._operation_times.clear()
   ```

2. Implement retention policies:
   ```python
   # Keep only recent data
   for key in telemetry._operation_times:
       telemetry._operation_times[key] = telemetry._operation_times[key][-1000:]
   ```

## Roadmap

Future enhancements planned:

- [ ] Grafana dashboard templates
- [ ] Automatic alert configuration
- [ ] Metric aggregation strategies
- [ ] Historical data retention policies
- [ ] Integration with Aurora reflections
- [ ] Real-time metric streaming
- [ ] Custom metric exporters

## Contributing

When adding new metrics:

1. Follow naming convention: `aurora.<component>.<metric_name>`
2. Add unit tests in `tests/test_telemetry.py`
3. Update this documentation
4. Include DLP context tag support

## License

Part of Aurora CloudBank Symbolic project. See main project LICENSE.
