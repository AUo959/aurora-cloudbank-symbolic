# Quick Start Guide: R-2 Agent Monitoring System

## Installation

### 1. Dependencies

```bash
# Core dependencies (already in requirements.txt)
pip install fastapi pydantic

# Optional for enhanced features
pip install opentelemetry-api opentelemetry-sdk
```

### 2. Verify Installation

```python
from src.monitoring import MonitoringSystem
print("✅ Monitoring system imported successfully")
```

## Basic Setup (5 Minutes)

### Step 1: Initialize Monitoring System

```python
from pathlib import Path
from src.monitoring import MonitoringSystem, AlertConfig

# Create monitoring system
monitoring = MonitoringSystem(
    storage_dir=Path("./monitoring_data"),
    ethics_rules_path=Path("./ethics/validation_engine/validation_rules.json")
)
```

### Step 2: Establish Agent Baseline

```python
# Historical data (at least 5-10 data points per metric)
historical_data = {
    'decisions_made': [45, 48, 47, 49, 46],
    'success_rate': [0.95, 0.96, 0.94, 0.97, 0.95],
    'error_rate': [0.03, 0.02, 0.04, 0.02, 0.03]
}

monitoring.establish_agent_baseline(
    agent_id="R-2-001",
    historical_data=historical_data
)
```

### Step 3: Record Behavior

```python
# Record current metrics
metrics = {
    'decisions_made': 47,
    'success_rate': 0.96,
    'error_rate': 0.02
}

monitoring.record_agent_behavior(
    agent_id="R-2-001",
    metrics=metrics
)
```

### Step 4: Check for Drift

```python
# Check behavior
result = monitoring.check_agent_behavior(agent_id="R-2-001")

if result['drift_detected']:
    print(f"⚠️  Drift detected: {len(result['alerts'])} alerts")
    for alert in result['alerts']:
        print(f"  - {alert['metric_name']}: {alert['level']}")
```

### Step 5: Evaluate Actions

```python
# Before executing critical actions
evaluation = monitoring.evaluate_action(
    agent_id="R-2-001",
    action_type="deployment",
    parameters={
        'critical_decision': False,
        'tests_passed': True
    }
)

if evaluation['blocked']:
    print("❌ Action blocked due to ethics violations")
else:
    print("✅ Action approved")
    # Proceed with action
```

## FastAPI Integration (2 Minutes)

```python
from fastapi import FastAPI
from src.monitoring.dashboard_api import create_monitoring_router

app = FastAPI()

# Add monitoring routes
monitoring_router = create_monitoring_router(
    storage_dir=Path("./monitoring_data"),
    ethics_rules_path=Path("./ethics/validation_engine/validation_rules.json")
)

if monitoring_router:
    app.include_router(monitoring_router)

# Run server
# uvicorn your_app:app --reload
```

Access endpoints:
- Health: `GET /monitoring/health`
- Dashboard stats: `GET /monitoring/dashboard/stats`
- Check behavior: `POST /monitoring/behavior/check?agent_id=R-2-001`
- Get alerts: `GET /monitoring/alerts`

## Dashboard Access

1. Start your FastAPI server
2. Open `src/dashboard/monitoring_dashboard.html` in a browser
3. Or integrate the HTML into your web application

Features:
- ✅ Real-time statistics
- ✅ Filterable alerts and violations
- ✅ Auto-refresh every 30 seconds
- ✅ Visual severity indicators

## Common Patterns

### Pattern 1: Continuous Monitoring Loop

```python
import time

while True:
    # Record current state
    metrics = collect_current_metrics()  # Your function
    monitoring.record_agent_behavior("R-2-001", metrics)
    
    # Check for drift every hour
    result = monitoring.check_agent_behavior("R-2-001")
    
    if result['drift_detected']:
        handle_drift_alerts(result['alerts'])
    
    time.sleep(3600)  # Check every hour
```

### Pattern 2: Action Validation

```python
def execute_critical_action(action_type, params):
    """Execute action with ethics validation"""
    
    # Evaluate before execution
    evaluation = monitoring.evaluate_action(
        agent_id="R-2-001",
        action_type=action_type,
        parameters=params
    )
    
    if evaluation['blocked']:
        raise PermissionError(
            f"Action blocked: {len(evaluation['violations'])} violations"
        )
    
    # Execute action
    result = perform_action(action_type, params)
    
    # Record metrics
    monitoring.record_agent_behavior("R-2-001", {
        'decisions_made': 1,
        'success_rate': 1.0 if result.success else 0.0
    })
    
    return result
```

### Pattern 3: Scheduled Reporting

```python
from datetime import datetime, timedelta

def generate_daily_report():
    """Generate daily compliance report"""
    
    report = monitoring.generate_compliance_report(
        since=datetime.utcnow() - timedelta(days=1),
        agent_id="R-2-001"
    )
    
    # Save report
    with open(f"reports/compliance_{datetime.now().date()}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Send to stakeholders
    if report['summary']['total_violations'] > 0:
        notify_compliance_team(report)

# Schedule daily at 8 AM
# Or use cron: 0 8 * * * python -c "from your_module import generate_daily_report; generate_daily_report()"
```

### Pattern 4: Custom Alert Handlers

```python
def setup_custom_handlers(monitoring):
    """Register custom alert handlers"""
    
    def slack_notification(data):
        import requests
        requests.post(SLACK_WEBHOOK, json={
            'text': f"Alert: {data.get('description')}"
        })
    
    def pagerduty_incident(data):
        # Create PagerDuty incident for critical alerts
        create_incident(data)
    
    monitoring.register_alert_handler(
        AlertLevel.WARNING,
        slack_notification
    )
    monitoring.register_alert_handler(
        AlertLevel.CRITICAL,
        pagerduty_incident
    )
```

## Troubleshooting

### Issue: High false positive rate

**Solution**: Adjust thresholds
```python
monitoring = MonitoringSystem(
    config=AlertConfig(
        info_threshold=0.3,      # Increase from 0.2
        warning_threshold=0.6,   # Increase from 0.5
        critical_threshold=1.0   # Increase from 0.8
    )
)
```

### Issue: Missing violations

**Solution**: Verify rule conditions and parameters
```python
# Check what rules are loaded
rules = monitoring.ethics_engine.export_rules()
print(f"Loaded {len(rules)} rules")

# Test specific rule
evaluation = monitoring.evaluate_action(
    agent_id="test",
    action_type="test",
    parameters={'critical_decision': True, 'no_human_approval': True}
)
print(f"Violations: {len(evaluation['violations'])}")
```

### Issue: Audit chain verification fails

**Solution**: Check for tampering or corruption
```python
is_valid = monitoring.audit_logger.verify_chain()
if not is_valid:
    print("⚠️  Audit chain compromised!")
    # Investigate or restore from backup
```

## Configuration

See `config/monitoring_config.yaml` for full configuration options:

- Alert thresholds
- Intervention settings
- Storage options
- Notification channels
- Performance tuning

## Next Steps

1. **Establish baselines** for all your agents
2. **Integrate with CI/CD** to monitor deployments
3. **Set up alerting** to Slack, email, or PagerDuty
4. **Schedule reports** for compliance reviews
5. **Review documentation** at `docs/MONITORING_SYSTEM.md`

## Example Script

Run the complete example:
```bash
python examples/r2_monitoring_integration.py
```

This demonstrates:
- System initialization
- Baseline establishment
- Normal operations
- Drift detection
- Ethics evaluation
- Status reporting

## Support

- **Documentation**: `docs/MONITORING_SYSTEM.md`
- **Examples**: `examples/r2_monitoring_integration.py`
- **Tests**: `tests/test_*_*.py`
- **Configuration**: `config/monitoring_config.yaml`

## Key Metrics to Monitor

For R-2 Agent specifically:
- `decisions_made`: Decision count per period
- `decision_latency_ms`: Decision processing time
- `success_rate`: Successful operations ratio
- `error_rate`: Error occurrence ratio
- `ethics_checks_passed`: Compliance rate
- `human_interactions`: Human oversight frequency
- `deployment_success_rate`: Deployment success (custom)
- `code_health_score`: Codebase health (custom)

Start with these core metrics and expand as needed!
