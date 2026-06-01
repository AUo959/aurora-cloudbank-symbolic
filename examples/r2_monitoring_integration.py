"""
Example: R-2 Agent Monitoring Integration

Demonstrates how to integrate the monitoring system with R-2 agent operations.
"""

from pathlib import Path
from datetime import datetime, timedelta, timezone
from src.monitoring import (
    MonitoringSystem,
    AlertConfig,
    AlertLevel
)


def setup_r2_monitoring():
    """
    Setup monitoring for R-2 agent
    
    Returns:
        MonitoringSystem instance configured for R-2
    """
    # Configure alerting
    config = AlertConfig(
        info_notify_delay_seconds=300,      # 5 minutes for info alerts
        warning_notify_delay_seconds=60,     # 1 minute for warnings
        critical_notify_immediate=True,      # Immediate for critical
        enable_auto_intervention=True,       # Enable automated interventions
        intervention_cooldown_seconds=300,   # 5 minute cooldown
        max_violations_per_hour=10          # Max 10 violations/hour
    )
    
    # Initialize monitoring system
    monitoring = MonitoringSystem(
        storage_dir=Path("./monitoring_data"),
        ethics_rules_path=Path("./ethics/validation_engine/validation_rules.json"),
        config=config
    )
    
    # Register alert handlers
    monitoring.register_alert_handler(AlertLevel.INFO, handle_info_alert)
    monitoring.register_alert_handler(AlertLevel.WARNING, handle_warning_alert)
    monitoring.register_alert_handler(AlertLevel.CRITICAL, handle_critical_alert)
    
    print("✅ R-2 Monitoring System initialized")
    
    return monitoring


def handle_info_alert(data):
    """Handle info-level alerts"""
    print(f"ℹ️  INFO ALERT: {data.get('description', 'Unknown')}")


def handle_warning_alert(data):
    """Handle warning-level alerts"""
    print(f"⚠️  WARNING ALERT: {data.get('description', 'Unknown')}")
    # Could send to monitoring system, Slack, etc.


def handle_critical_alert(data):
    """Handle critical alerts"""
    print(f"🚨 CRITICAL ALERT: {data.get('description', 'Unknown')}")
    # Alert on-call engineer, trigger incident response, etc.


def establish_r2_baseline(monitoring, agent_id="R-2-001"):
    """
    Establish baseline behavior for R-2 agent
    
    Args:
        monitoring: MonitoringSystem instance
        agent_id: R-2 agent identifier
    """
    print(f"\n📊 Establishing baseline for {agent_id}...")
    
    # Historical data from previous deployments
    historical_data = {
        # Decision metrics
        'decisions_made': [45, 48, 47, 49, 46, 48, 47, 50],
        'decision_latency_ms': [125, 130, 128, 135, 127, 132, 129, 131],
        'decision_changes': [2, 1, 3, 2, 2, 1, 2, 2],
        
        # Resource metrics
        'resources_allocated': [20, 22, 21, 23, 20, 22, 21, 22],
        'resource_efficiency': [0.85, 0.87, 0.86, 0.88, 0.85, 0.87, 0.86, 0.87],
        
        # Interaction metrics
        'human_interactions': [8, 10, 9, 11, 8, 10, 9, 10],
        'override_requests': [1, 0, 1, 2, 1, 0, 1, 1],
        'explanation_requests': [12, 14, 13, 15, 12, 14, 13, 14],
        
        # Performance metrics
        'success_rate': [0.95, 0.96, 0.94, 0.97, 0.95, 0.96, 0.94, 0.96],
        'error_rate': [0.03, 0.02, 0.04, 0.02, 0.03, 0.02, 0.04, 0.03],
        'timeout_rate': [0.01, 0.01, 0.01, 0.00, 0.01, 0.01, 0.01, 0.01],
        
        # Ethics metrics
        'ethics_checks_passed': [45, 48, 47, 49, 46, 48, 47, 50],
        'ethics_violations': [0, 0, 0, 0, 0, 0, 0, 0],
        'safety_incidents': [0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    monitoring.establish_agent_baseline(
        agent_id=agent_id,
        historical_data=historical_data
    )
    
    print(f"✅ Baseline established with {len(historical_data)} metrics")


def simulate_r2_operations(monitoring, agent_id="R-2-001"):
    """
    Simulate R-2 agent operations with monitoring
    
    Args:
        monitoring: MonitoringSystem instance
        agent_id: R-2 agent identifier
    """
    print(f"\n🤖 Simulating R-2 operations for {agent_id}...\n")
    
    # Scenario 1: Normal operations
    print("Scenario 1: Normal Operations")
    normal_metrics = {
        'decisions_made': 47,
        'decision_latency_ms': 130,
        'decision_changes': 2,
        'resources_allocated': 21,
        'resource_efficiency': 0.86,
        'human_interactions': 9,
        'override_requests': 1,
        'explanation_requests': 13,
        'success_rate': 0.95,
        'error_rate': 0.03,
        'timeout_rate': 0.01,
        'ethics_checks_passed': 47,
        'ethics_violations': 0,
        'safety_incidents': 0
    }
    
    monitoring.record_agent_behavior(
        agent_id=agent_id,
        metrics=normal_metrics,
        context_tag="r2_ops_normal_001"
    )
    
    result = monitoring.check_agent_behavior(
        agent_id=agent_id,
        context_tag="r2_check_001"
    )
    
    print(f"  Drift detected: {result['drift_detected']}")
    print(f"  Alerts: {len(result['alerts'])}")
    
    # Scenario 2: Increased latency (drift warning)
    print("\nScenario 2: Increased Latency (Drift)")
    drift_metrics = {
        'decisions_made': 48,
        'decision_latency_ms': 200,  # Significant increase
        'decision_changes': 2,
        'resources_allocated': 22,
        'resource_efficiency': 0.85,
        'human_interactions': 10,
        'override_requests': 1,
        'explanation_requests': 14,
        'success_rate': 0.94,
        'error_rate': 0.04,
        'timeout_rate': 0.01,
        'ethics_checks_passed': 48,
        'ethics_violations': 0,
        'safety_incidents': 0
    }
    
    monitoring.record_agent_behavior(
        agent_id=agent_id,
        metrics=drift_metrics,
        context_tag="r2_ops_drift_001"
    )
    
    result = monitoring.check_agent_behavior(
        agent_id=agent_id,
        context_tag="r2_check_002"
    )
    
    print(f"  Drift detected: {result['drift_detected']}")
    print(f"  Alerts: {len(result['alerts'])}")
    if result['alerts']:
        for alert in result['alerts']:
            print(f"    - {alert['metric_name']}: {alert['level']} ({alert['description']})")
    
    # Scenario 3: Ethics evaluation - compliant action
    print("\nScenario 3: Compliant Action Evaluation")
    compliant_result = monitoring.evaluate_action(
        agent_id=agent_id,
        action_type="code_deployment",
        parameters={
            'code_review_completed': True,
            'tests_passed': True,
            'security_scan_clean': True
        },
        context_tag="r2_action_compliant_001"
    )
    
    print(f"  Violations: {len(compliant_result['violations'])}")
    print(f"  Blocked: {compliant_result['blocked']}")
    
    # Scenario 4: Ethics evaluation - violation
    print("\nScenario 4: Critical Action Evaluation (Ethics Violation)")
    violation_result = monitoring.evaluate_action(
        agent_id=agent_id,
        action_type="system_change",
        parameters={
            'critical_decision': True,
            'no_human_approval': True,  # Missing required approval
            'impact_level': 'high'
        },
        context_tag="r2_action_violation_001"
    )
    
    print(f"  Violations: {len(violation_result['violations'])}")
    print(f"  Blocked: {violation_result['blocked']}")
    if violation_result['violations']:
        for violation in violation_result['violations']:
            print(f"    - {violation['rule_name']}: {violation['severity']}")
            print(f"      {violation['description']}")
            if violation.get('remediation'):
                print(f"      Remediation: {violation['remediation']}")


def generate_r2_status_report(monitoring, agent_id="R-2-001"):
    """
    Generate status report for R-2 agent
    
    Args:
        monitoring: MonitoringSystem instance
        agent_id: R-2 agent identifier
    """
    print(f"\n📋 Generating status report for {agent_id}...\n")
    
    # Get agent status
    status = monitoring.get_agent_status(agent_id)
    
    print(f"Agent Status: {status['status'].upper()}")
    print(f"Violations (24h): {status['violations_24h']}")
    print(f"Drift Alerts (24h): {status['drift_alerts_24h']}")
    print(f"Interventions (24h): {status['interventions_24h']}")
    
    if status.get('behavioral_metrics'):
        print("\nBehavioral Metrics:")
        for metric, stats in list(status['behavioral_metrics'].items())[:5]:
            print(f"  {metric}:")
            print(f"    Mean: {stats.get('mean', 0):.2f}")
            print(f"    Min: {stats.get('min', 0):.2f}")
            print(f"    Max: {stats.get('max', 0):.2f}")
    
    # Generate compliance report
    print("\n📊 Generating compliance report...\n")
    
    report = monitoring.generate_compliance_report(
        since=datetime.now(timezone.utc) - timedelta(hours=24),
        agent_id=agent_id
    )
    
    print(f"Report Period: {report['report_period']['start']} to {report['report_period']['end']}")
    print(f"\nSummary:")
    print(f"  Total Violations: {report['summary']['total_violations']}")
    print(f"  Total Drift Alerts: {report['summary']['total_drift_alerts']}")
    print(f"  Total Interventions: {report['summary']['total_interventions']}")
    print(f"  Audit Entries: {report['summary']['audit_entries']}")
    print(f"  Audit Chain Valid: {report['audit_verified']}")
    
    if report['summary'].get('violations_by_severity'):
        print(f"\nViolations by Severity:")
        for severity, count in report['summary']['violations_by_severity'].items():
            print(f"  {severity}: {count}")
    
    if report['summary'].get('alerts_by_level'):
        print(f"\nAlerts by Level:")
        for level, count in report['summary']['alerts_by_level'].items():
            print(f"  {level}: {count}")


def main():
    """Main example execution"""
    print("=" * 70)
    print("R-2 Agent Monitoring System - Example Integration")
    print("=" * 70)
    
    # Setup monitoring
    monitoring = setup_r2_monitoring()
    
    # Establish baseline
    establish_r2_baseline(monitoring)
    
    # Simulate operations
    simulate_r2_operations(monitoring)
    
    # Generate status report
    generate_r2_status_report(monitoring)
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("=" * 70)
    print("\nTo integrate with your application:")
    print("1. Import MonitoringSystem from src.monitoring")
    print("2. Initialize with your storage path and ethics rules")
    print("3. Establish baselines for your agents")
    print("4. Record metrics during operations")
    print("5. Evaluate actions before execution")
    print("6. Check behavior periodically for drift")
    print("7. Generate compliance reports as needed")
    print("\nSee docs/MONITORING_SYSTEM.md for complete documentation.")


if __name__ == "__main__":
    main()
