# Drift Detection and Ethics Monitoring System

## Overview

The Aurora Drift Detection and Ethics Monitoring System provides comprehensive oversight for R-2 and other agents, ensuring they operate within defined safety and ethical boundaries. The system combines statistical drift detection, rule-based ethics compliance, behavioral monitoring, and immutable audit logging.

## Architecture

### Core Components

1. **Drift Detector** (`drift_detector.py`)
   - Statistical anomaly detection using z-scores
   - Moving average trend analysis
   - Threshold-based alerting
   - Multi-level alert generation (Info, Warning, Critical)

2. **Ethics Engine** (`ethics_engine.py`)
   - Rule-based compliance evaluation
   - Configurable ethics rules from JSON/YAML
   - Custom condition evaluators
   - Automated blocking of critical violations

3. **Behavioral Monitor** (`behavioral_monitor.py`)
   - Real-time metrics collection
   - Time-series data aggregation
   - Pattern tracking across multiple metrics
   - Historical data retention (default: 1 week)

4. **Audit Logger** (`audit_logger.py`)
   - Immutable audit trail with cryptographic signing
   - Hash-chain verification for tamper detection
   - Multiple event types (alerts, violations, interventions)
   - Persistent storage with JSON export

5. **Monitoring System** (`monitoring_system.py`)
   - Integrated coordinator for all subsystems
   - Multi-level alerting (Info, Warning, Critical)
   - Automated intervention triggers
   - Compliance reporting

6. **Dashboard API** (`dashboard_api.py`)
   - FastAPI integration
   - REST endpoints for all monitoring functions
   - Real-time data access
   - Web dashboard integration

## Installation

### Requirements

```bash
# Core dependencies
pip install fastapi pydantic

# Optional for enhanced features
pip install opentelemetry-api opentelemetry-sdk
```

### Environment Variables

Configure the following environment variables for production:

```bash
# Required for persistent audit chain verification
export MONITORING_SIGNING_KEY="your-secret-key-here"  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Optional configuration paths
export MONITORING_STORAGE_DIR="./monitoring_data"
export ETHICS_RULES_PATH="./ethics/validation_engine/validation_rules.json"

# Optional API authentication
export MONITORING_API_TOKEN="your-api-token-here"
```

**Important**: The `MONITORING_SIGNING_KEY` must be consistent across system restarts to maintain audit chain verification. Never use runtime-generated keys in production.

### Setup

```python
from pathlib import Path
from src.monitoring import MonitoringSystem

# Initialize monitoring system
monitoring = MonitoringSystem(
    storage_dir=Path("./monitoring_data"),
    ethics_rules_path=Path("./ethics/validation_engine/validation_rules.json")
)
```

## Usage

### 1. Establishing Agent Baseline

Before monitoring can detect drift, establish baseline behavior patterns:

```python
# Historical data for key metrics
historical_data = {
    'decisions_made': [10, 12, 11, 13, 10, 12],
    'decision_latency_ms': [50, 55, 52, 48, 51, 53],
    'success_rate': [0.95, 0.96, 0.94, 0.97, 0.95, 0.96],
    'ethics_violations': [0, 0, 0, 0, 0, 0]
}

monitoring.establish_agent_baseline(
    agent_id="R-2-001",
    historical_data=historical_data
)
```

### 2. Recording Behavioral Metrics

Continuously record agent behavior:

```python
# Record current metrics
metrics = {
    'decisions_made': 15,
    'decision_latency_ms': 75,  # Increased latency
    'success_rate': 0.85,  # Decreased success rate
    'ethics_violations': 0
}

monitoring.record_agent_behavior(
    agent_id="R-2-001",
    metrics=metrics,
    context_tag="deployment_001"
)
```

### 3. Checking for Drift

Detect deviations from baseline:

```python
result = monitoring.check_agent_behavior(
    agent_id="R-2-001",
    context_tag="drift_check_001"
)

if result['drift_detected']:
    print(f"Drift detected: {len(result['alerts'])} alerts")
    for alert in result['alerts']:
        print(f"  - {alert['metric_name']}: {alert['level']}")
```

### 4. Evaluating Actions for Ethics Compliance

Before executing actions, evaluate against ethics rules:

```python
evaluation = monitoring.evaluate_action(
    agent_id="R-2-001",
    action_type="resource_allocation",
    parameters={
        'resources_allocated': 100,
        'inequality_coefficient': 0.85,  # High inequality
        'consent_missing': False
    },
    context_tag="action_eval_001"
)

if evaluation['blocked']:
    print(f"Action blocked due to {len(evaluation['violations'])} violations")
    for violation in evaluation['violations']:
        print(f"  - {violation['rule_name']}: {violation['description']}")
else:
    # Proceed with action
    pass
```

### 5. Generating Compliance Reports

Create comprehensive compliance reports:

```python
from datetime import datetime, timedelta

report = monitoring.generate_compliance_report(
    since=datetime.utcnow() - timedelta(days=7),
    agent_id="R-2-001"  # Optional: specific agent
)

print(f"Report for period: {report['report_period']}")
print(f"Total violations: {report['summary']['total_violations']}")
print(f"Total alerts: {report['summary']['total_drift_alerts']}")
print(f"Audit chain valid: {report['audit_verified']}")
```

## Ethics Rules Configuration

### Rule Structure

Rules are defined in JSON format with the following structure:

```json
{
  "ethics_validation_rules": {
    "rule_categories": {
      "ai_ethics": {
        "rules": [
          {
            "id": "AI001",
            "name": "Human Oversight Required",
            "description": "Critical decisions must have human oversight",
            "severity": "critical",
            "auto_block": true,
            "conditions": ["critical_decision", "no_human_approval"]
          }
        ]
      }
    }
  }
}
```

### Rule Fields

- **id**: Unique rule identifier
- **name**: Human-readable rule name
- **description**: Detailed explanation
- **severity**: One of `low`, `medium`, `high`, `critical`
- **auto_block**: Whether to automatically block violations
- **conditions**: List of conditions that trigger the rule

### Custom Evaluators

Register custom condition evaluators:

```python
def check_data_sensitivity(params):
    """Custom evaluator for data sensitivity"""
    return params.get('data_classification') == 'sensitive'

monitoring.ethics_engine.register_evaluator(
    'sensitive_data',
    check_data_sensitivity
)
```

## Alert Levels and Thresholds

### Drift Detection Thresholds

- **Info**: 20% deviation from baseline
- **Warning**: 50% deviation from baseline
- **Critical**: 80% deviation from baseline or z-score > 3.0

### Ethics Violation Severities

- **Low**: Logged only, no blocking
- **Medium**: Warning issued, review recommended
- **High**: Alert generated, manual review required
- **Critical**: Automatic blocking, immediate intervention

## Automated Interventions

The system can automatically intervene when critical issues are detected:

### Intervention Types

1. **BLOCK_ACTION**: Prevent action execution
2. **REQUEST_REVIEW**: Flag for manual review
3. **NOTIFY_OPERATOR**: Alert human operators
4. **THROTTLE_AGENT**: Reduce agent activity rate
5. **SUSPEND_AGENT**: Temporarily suspend agent operations
6. **RESET_BASELINE**: Recalibrate baseline metrics

### Configuration

```python
from src.monitoring import AlertConfig

config = AlertConfig(
    info_notify_delay_seconds=300,      # 5 minutes
    warning_notify_delay_seconds=60,     # 1 minute
    critical_notify_immediate=True,
    enable_auto_intervention=True,
    intervention_cooldown_seconds=300,   # 5 minutes
    max_violations_per_hour=10
)

monitoring = MonitoringSystem(config=config)
```

## Alert Handlers

Register custom handlers for different alert levels:

```python
def handle_critical_alert(data):
    """Handle critical alerts"""
    print(f"CRITICAL ALERT: {data}")
    # Send to incident management system
    # Notify on-call engineers
    # etc.

monitoring.register_alert_handler(
    level=AlertLevel.CRITICAL,
    handler=handle_critical_alert
)
```

## API Integration

### FastAPI Router

Integrate with your FastAPI application:

```python
from fastapi import FastAPI
from src.monitoring.dashboard_api import create_monitoring_router

app = FastAPI()

# Add monitoring routes
monitoring_router = create_monitoring_router()
if monitoring_router:
    app.include_router(monitoring_router)
```

### Available Endpoints

- `GET /monitoring/health` - System health check
- `POST /monitoring/baseline` - Establish agent baseline
- `POST /monitoring/behavior/record` - Record metrics
- `POST /monitoring/behavior/check` - Check for drift
- `POST /monitoring/action/evaluate` - Evaluate action
- `GET /monitoring/agent/{agent_id}/status` - Get agent status
- `GET /monitoring/alerts` - Query drift alerts
- `GET /monitoring/violations` - Query ethics violations
- `GET /monitoring/audit` - Access audit log
- `GET /monitoring/compliance/report` - Generate report
- `GET /monitoring/dashboard/stats` - Dashboard statistics

## Dashboard

### Accessing the Dashboard

The HTML dashboard is available at:
```
/src/dashboard/monitoring_dashboard.html
```

Serve it with your web application or access directly.

### Features

- Real-time statistics
- Filterable alert and violation lists
- Auto-refresh every 30 seconds
- Visual severity indicators
- Time-based filtering (1 hour, 24 hours, 1 week)
- Agent-specific views

## Audit Trail

### Immutability

The audit log uses:
- **Cryptographic signing**: HMAC-SHA256 signatures
- **Hash chaining**: Each entry links to previous entry's hash
- **Verification**: `verify_chain()` detects tampering

### Querying Audit Log

```python
from datetime import datetime, timedelta

# Get all entries for an agent
entries = monitoring.audit_logger.get_entries(
    agent_id="R-2-001",
    since=datetime.utcnow() - timedelta(days=1)
)

# Verify integrity
is_valid = monitoring.audit_logger.verify_chain()
print(f"Audit chain valid: {is_valid}")

# Export audit report
report = monitoring.audit_logger.export_report(
    since=datetime.utcnow() - timedelta(days=7),
    format="json"  # or "csv"
)
```

## Behavioral Metrics

### Standard Metrics

- `decisions_made`: Number of decisions
- `decision_latency_ms`: Decision processing time
- `decision_changes`: Decision reversals
- `resources_allocated`: Resource allocation count
- `resource_efficiency`: Resource usage efficiency (0-1)
- `human_interactions`: Human interaction count
- `override_requests`: Override request count
- `explanation_requests`: Explanation request count
- `success_rate`: Action success rate (0-1)
- `error_rate`: Error occurrence rate (0-1)
- `timeout_rate`: Timeout occurrence rate (0-1)
- `ethics_checks_passed`: Ethics check pass count
- `ethics_violations`: Ethics violation count
- `safety_incidents`: Safety incident count

### Custom Metrics

Add custom metrics for domain-specific monitoring:

```python
monitoring.record_agent_behavior(
    agent_id="R-2-001",
    metrics={
        'custom_metric_name': 42.5
    }
)
```

## Best Practices

### 1. Baseline Establishment

- Collect at least 5-10 data points for each metric
- Use representative historical data
- Update baselines periodically (monthly/quarterly)
- Consider seasonal variations

### 2. Alert Configuration

- Start with conservative thresholds
- Adjust based on false positive rates
- Use different thresholds for different metrics
- Implement alert fatigue prevention

### 3. Ethics Rules

- Keep rules clear and specific
- Document rationale for each rule
- Review rules regularly with stakeholders
- Test rules before deployment

### 4. Monitoring

- Record metrics at consistent intervals
- Snapshot behavioral metrics regularly
- Check for drift after significant changes
- Evaluate all critical actions

### 5. Audit Trail

- Never modify audit log entries
- Verify chain integrity regularly
- Backup audit logs frequently
- Store backups in secure, immutable storage

## Troubleshooting

### High False Positive Rate

**Symptoms**: Too many drift alerts for normal behavior

**Solutions**:
- Increase detection thresholds
- Collect more baseline data
- Adjust moving average window
- Review metric definitions

### Missing Violations

**Symptoms**: Expected violations not detected

**Solutions**:
- Verify rule conditions
- Check parameter names match
- Test custom evaluators
- Review action context

### Performance Issues

**Symptoms**: Slow metric recording or checking

**Solutions**:
- Reduce retention period
- Snapshot less frequently
- Optimize custom evaluators
- Use asynchronous processing

## Security Considerations

1. **Audit Log Protection**
   - Store signing key securely
   - Use environment variables for sensitive data
   - Implement access controls
   - Monitor for tampering attempts

2. **Ethics Rules**
   - Protect rule configuration files
   - Version control rule changes
   - Audit rule modifications
   - Test rule changes in staging

3. **API Security**
   - Implement authentication
   - Use HTTPS for all endpoints
   - Rate limit API requests
   - Validate all inputs

## Performance Guidelines

- **Baseline Storage**: ~1KB per metric per agent
- **Metrics History**: ~500 bytes per snapshot
- **Audit Log**: ~1-2KB per entry
- **Memory Usage**: ~10MB per 1000 agents (1 week retention)
- **API Response**: <100ms for typical queries

## Integration with R-2 Agent

The monitoring system integrates with R-2 agent's core responsibilities:

1. **Implementation Leadership**: Monitor deployment success
2. **Live Code Health**: Track real-time performance
3. **Configuration Drift**: Detect unexpected changes
4. **Dependency Monitoring**: Track compatibility issues
5. **Intervention**: Automated remediation triggers

## Future Enhancements

- Machine learning-based drift prediction
- Blockchain anchoring for audit trail
- Real-time streaming dashboard
- Advanced pattern recognition
- Multi-agent correlation analysis
- Predictive intervention recommendations

## Support

For issues, questions, or contributions:
- Review existing documentation
- Check API endpoint responses
- Verify audit chain integrity
- Consult compliance reports
- Review ethical guidelines

## License

This monitoring system is part of Aurora CloudBank Symbolic and follows the project's licensing terms.
