# R-2 Agent Production Monitoring Setup

This directory contains monitoring configurations for R-2 agent production telemetry.

## Directory Structure

```
monitoring/
├── grafana/
│   └── r2_agent_dashboard.json    # Pre-built Grafana dashboard
├── prometheus/
│   └── r2_agent_alerts.yml        # Prometheus alerting rules
└── README.md                      # This file
```

## Quick Setup

### 1. Prometheus Configuration

Add to your `prometheus.yml`:

```yaml
# Scrape R-2 agent metrics
scrape_configs:
  - job_name: 'r2-agent'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/r2-telemetry/metrics'

# Load alerting rules
rule_files:
  - "monitoring/prometheus/r2_agent_alerts.yml"
```

Reload Prometheus configuration:
```bash
curl -X POST http://localhost:9090/-/reload
```

### 2. Grafana Dashboard

1. Open Grafana web interface
2. Go to **Dashboards** → **Import**
3. Upload `monitoring/grafana/r2_agent_dashboard.json`
4. Select your Prometheus data source
5. Click **Import**

The dashboard includes 11 panels:
- Health Status (success rate gauge)
- Total Operations counter
- Detected Anomalies counter
- Average Operation Duration
- Operations by Type (timeseries)
- Success vs Failure Rate (timeseries)
- Operation Duration Distribution (p50, p95, p99)
- CPU Usage (timeseries)
- Memory Usage (timeseries)
- Error Types Distribution (pie chart)
- Recent Anomalies (table)

### 3. Alerting

The alert rules in `r2_agent_alerts.yml` define:

**Critical Alerts:**
- High failure rate (>20%)
- Operations stalled (no ops for 10min)
- Multiple anomalies (>10 per hour)
- Critical health (<50% success rate)

**Warning Alerts:**
- Anomaly detected
- Slow operations (p95 >5s)
- High CPU (>80%)
- High memory (>1GB)
- Degraded health (<80% success rate)

Configure alert destinations in your Prometheus `alertmanager.yml`.

## Metrics Available

### Counters
- `r2_agent_operations_total` - Total operations by type
- `r2_agent_operations_success` - Successful operations
- `r2_agent_operations_errors` - Failed operations
- `r2_agent_anomalies_detected` - Total anomalies detected

### Histograms
- `r2_agent_operation_duration` - Operation duration distribution

### Gauges
- `r2_agent_resource_cpu` - CPU usage percentage
- `r2_agent_resource_memory` - Memory usage in MB

## Testing Metrics Endpoint

Test that metrics are being exposed:

```bash
curl http://localhost:8000/r2-telemetry/metrics
```

Expected output:
```
# HELP r2_agent_operations_total Total count of R-2 agent operations
# TYPE r2_agent_operations_total counter
r2_agent_operations_total{operation_type="dependency_audit"} 42
r2_agent_operations_total{operation_type="health_check"} 156
...
```

## Querying Metrics in Prometheus

Example PromQL queries:

```promql
# Success rate over last 5 minutes
rate(r2_agent_operations_success[5m]) / rate(r2_agent_operations_total[5m])

# Average operation duration
avg(r2_agent_operation_duration)

# Operations per second by type
rate(r2_agent_operations_total[5m])

# P95 latency
histogram_quantile(0.95, rate(r2_agent_operation_duration_bucket[5m]))

# Error rate by type
rate(r2_agent_operations_errors[5m])
```

## Troubleshooting

### Metrics Not Appearing

1. **Check telemetry is enabled:**
   ```bash
   curl http://localhost:8000/r2-telemetry/health
   ```

2. **Verify Prometheus scraping:**
   - Open Prometheus UI: http://localhost:9090
   - Go to Status → Targets
   - Check if `r2-agent` target is up

3. **Check application logs:**
   ```bash
   grep "telemetry" /path/to/application.log
   ```

### Dashboard Empty

1. Ensure Prometheus data source is configured correctly
2. Verify metrics are being scraped (check Prometheus Targets)
3. Check time range in dashboard (default: last 6 hours)
4. Generate some test operations:
   ```bash
   curl -X POST "http://localhost:8000/r2-telemetry/test-operation"
   ```

### Alerts Not Firing

1. Verify alerting rules are loaded:
   ```bash
   curl http://localhost:9090/api/v1/rules
   ```

2. Check alert status in Prometheus UI:
   - Go to Alerts
   - Look for R-2 agent alerts

3. Verify Alertmanager is configured and running:
   ```bash
   curl http://localhost:9093/api/v1/status
   ```

## Integration with CI/CD

Add telemetry health checks to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
- name: Check R-2 Telemetry
  run: |
    response=$(curl -s http://localhost:8000/r2-telemetry/health)
    status=$(echo $response | jq -r '.status')
    if [ "$status" != "healthy" ]; then
      echo "Telemetry unhealthy: $status"
      exit 1
    fi
```

## Security Considerations

- **PII Filtering**: Telemetry automatically redacts sensitive data
- **Network Security**: Restrict metrics endpoint access in production
- **Data Retention**: Configure Prometheus retention policy appropriately
- **RBAC**: Use Grafana RBAC to control dashboard access

## Advanced Configuration

### Custom Alert Thresholds

Edit `r2_agent_alerts.yml` to adjust thresholds:

```yaml
# Example: Lower failure rate threshold to 15%
- alert: R2AgentHighFailureRate
  expr: |
    (rate(r2_agent_operations_errors[5m]) / rate(r2_agent_operations_total[5m])) > 0.15
```

### Additional Dashboards

Create custom dashboards for specific use cases:
- Team-specific operations
- Repository-specific metrics
- Time-of-day patterns
- Correlation with external events

## Support

For issues or questions:
- Documentation: `docs/R2_AGENT_TELEMETRY.md`
- GitHub Issues: https://github.com/AUo959/aurora-cloudbank-symbolic/issues
- Security: See SECURITY.md

## License

See LICENSE file in repository root.
