#!/usr/bin/env python3
"""
R-2 Agent Telemetry Integration Example

Demonstrates how to integrate production telemetry into R-2 agent operations
for comprehensive monitoring and observability.
"""

import sys
import time
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.observability import get_r2_telemetry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_dependency_audit():
    """
    Example R-2 agent operation: Dependency Audit
    
    Demonstrates telemetry integration for dependency auditing operations.
    """
    telemetry = get_r2_telemetry()
    
    logger.info("Starting dependency audit with telemetry")
    
    with telemetry.trace_agent_operation(
        operation_type="dependency_audit",
        context_tag=f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        symbolic_anchor="T1:AUDIT_START",
        repository="aurora-cloudbank-symbolic",
        audit_type="security"
    ) as metrics:
        # Simulate audit steps
        logger.info("Scanning dependencies...")
        time.sleep(0.5)
        
        # Track decisions
        logger.info("Analyzing vulnerabilities...")
        metrics.decisions_made = 3
        
        # Track tools used
        metrics.tools_invoked = ["pip-audit", "safety", "bandit"]
        
        # Simulate repository access
        metrics.repositories_accessed = ["main-repo"]
        
        # Generate audit report
        logger.info("Generating audit report...")
        time.sleep(0.2)
        metrics.artifacts_generated = 1
        
        # Add custom metadata
        metrics.metadata.update({
            "vulnerabilities_found": 2,
            "severity": "medium",
            "action_required": True
        })
        
        logger.info("Dependency audit completed successfully")
        return {
            "status": "completed",
            "vulnerabilities": 2,
            "report": "audit_report.json"
        }


def example_health_check():
    """
    Example R-2 agent operation: Health Check
    
    Demonstrates telemetry for system health monitoring.
    """
    telemetry = get_r2_telemetry()
    
    logger.info("Starting health check with telemetry")
    
    with telemetry.trace_agent_operation(
        operation_type="health_check",
        context_tag=f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        symbolic_anchor="T1:HEALTH_CHECK",
        check_type="comprehensive"
    ) as metrics:
        # Check various system components
        components = ["api", "database", "cache", "storage"]
        healthy_components = 0
        
        for component in components:
            logger.info(f"Checking {component}...")
            time.sleep(0.1)
            
            # Simulate health check
            is_healthy = True  # In real scenario, perform actual check
            if is_healthy:
                healthy_components += 1
            
            metrics.decisions_made += 1
        
        # Track tools
        metrics.tools_invoked = ["ping", "curl", "redis-cli"]
        
        # Calculate health status
        health_ratio = healthy_components / len(components)
        metrics.metadata.update({
            "components_checked": len(components),
            "components_healthy": healthy_components,
            "health_ratio": health_ratio,
            "status": "healthy" if health_ratio > 0.8 else "degraded"
        })
        
        logger.info(f"Health check completed: {healthy_components}/{len(components)} components healthy")
        return {
            "status": "healthy" if health_ratio > 0.8 else "degraded",
            "components": components,
            "healthy_count": healthy_components
        }


def example_configuration_drift_detection():
    """
    Example R-2 agent operation: Configuration Drift Detection
    
    Demonstrates telemetry for drift monitoring operations.
    """
    telemetry = get_r2_telemetry()
    
    logger.info("Starting configuration drift detection with telemetry")
    
    with telemetry.trace_agent_operation(
        operation_type="config_drift_detection",
        context_tag=f"drift_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        symbolic_anchor="T1:DRIFT_CHECK",
        scope="workflows"
    ) as metrics:
        # Scan for drift
        logger.info("Scanning workflow configurations...")
        time.sleep(0.3)
        
        # Simulate drift detection
        drifts_found = 1
        metrics.decisions_made = 2
        
        # Track files accessed
        metrics.metadata["files_scanned"] = 15
        metrics.metadata["drifts_found"] = drifts_found
        
        if drifts_found > 0:
            logger.warning(f"Configuration drift detected: {drifts_found} issues")
            metrics.artifacts_generated = 1  # Drift report
        else:
            logger.info("No configuration drift detected")
        
        metrics.tools_invoked = ["git", "diff", "yaml-lint"]
        
        return {
            "status": "drift_detected" if drifts_found > 0 else "no_drift",
            "drift_count": drifts_found
        }


def example_failed_operation():
    """
    Example R-2 agent operation: Failed Operation
    
    Demonstrates how telemetry captures failures and errors.
    """
    telemetry = get_r2_telemetry()
    
    logger.info("Starting operation that will fail (for demonstration)")
    
    try:
        with telemetry.trace_agent_operation(
            operation_type="integration_validation",
            context_tag=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbolic_anchor="T1:VALIDATION_START"
        ) as metrics:
            logger.info("Validating integrations...")
            time.sleep(0.2)
            
            metrics.decisions_made = 1
            
            # Simulate a failure
            logger.error("Integration validation failed!")
            raise ValueError("Integration validation failed: Missing required configuration")
            
    except ValueError as e:
        logger.error(f"Operation failed as expected: {e}")
        # Error is automatically recorded by telemetry
        return {"status": "failed", "error": str(e)}


def demonstrate_metrics_retrieval():
    """
    Demonstrate how to retrieve and display telemetry metrics
    """
    telemetry = get_r2_telemetry()
    
    logger.info("\n" + "=" * 60)
    logger.info("TELEMETRY METRICS SUMMARY")
    logger.info("=" * 60)
    
    # Get summary for last hour
    summary = telemetry.get_metrics_summary(time_window_seconds=3600)
    
    logger.info(f"Service Name: {summary['service_name']}")
    logger.info(f"Total Operations: {summary['total_operations']}")
    logger.info(f"Successful: {summary['successful_operations']}")
    logger.info(f"Failed: {summary['failed_operations']}")
    logger.info(f"Success Rate: {summary['success_rate']:.2%}")
    logger.info(f"Average Duration: {summary['average_duration_ms']:.2f}ms")
    logger.info(f"Anomalies Detected: {summary['anomaly_count']}")
    
    logger.info("\nOperations by Type:")
    for op_type, stats in summary['operations_by_type'].items():
        logger.info(f"  {op_type}:")
        logger.info(f"    Count: {stats['count']}")
        logger.info(f"    Success: {stats['success']}")
        logger.info(f"    Failures: {stats['failures']}")
    
    # Get recent operations
    logger.info("\nRecent Operations:")
    recent_ops = telemetry.get_recent_operations(limit=5)
    for op in recent_ops:
        status_icon = "✓" if op.success else "✗"
        logger.info(f"  {status_icon} {op.operation_type} - {op.duration_ms:.2f}ms")
    
    # Check for anomalies
    if summary['anomaly_count'] > 0:
        logger.warning(f"\n⚠️  {summary['anomaly_count']} anomalies detected!")
        recent_anomalies = summary['recent_anomalies']
        for anomaly in recent_anomalies[-3:]:
            logger.warning(f"  - {anomaly['anomaly_type']}: Score {anomaly['anomaly_score']:.2f}")
    
    logger.info("=" * 60 + "\n")


def demonstrate_prometheus_export():
    """
    Demonstrate Prometheus metrics export
    """
    telemetry = get_r2_telemetry()
    
    logger.info("\n" + "=" * 60)
    logger.info("PROMETHEUS METRICS EXPORT")
    logger.info("=" * 60)
    
    prometheus_data = telemetry.export_prometheus_metrics()
    logger.info(prometheus_data)
    logger.info("=" * 60 + "\n")


def main():
    """
    Main demonstration function
    """
    logger.info("R-2 Agent Telemetry Integration Examples")
    logger.info("=" * 60)
    
    # Run example operations
    logger.info("\n1. Running dependency audit...")
    example_dependency_audit()
    
    logger.info("\n2. Running health check...")
    example_health_check()
    
    logger.info("\n3. Running configuration drift detection...")
    example_configuration_drift_detection()
    
    logger.info("\n4. Running failed operation (demonstration)...")
    example_failed_operation()
    
    # Small delay to ensure metrics are recorded
    time.sleep(0.5)
    
    # Display collected metrics
    demonstrate_metrics_retrieval()
    
    # Show Prometheus export format
    demonstrate_prometheus_export()
    
    logger.info("✓ All examples completed successfully!")
    logger.info("\nTelemetry endpoints available at:")
    logger.info("  - Metrics: http://localhost:8000/r2-telemetry/metrics")
    logger.info("  - Summary: http://localhost:8000/r2-telemetry/summary")
    logger.info("  - Health: http://localhost:8000/r2-telemetry/health")
    logger.info("  - Recent Ops: http://localhost:8000/r2-telemetry/operations/recent")


if __name__ == "__main__":
    main()
