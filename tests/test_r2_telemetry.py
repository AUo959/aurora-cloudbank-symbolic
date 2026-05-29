"""
Tests for R-2 Agent Production Telemetry Integration
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch

from src.observability import (
    R2AgentTelemetry,
    AgentOperationMetrics,
    AnomalyDetectionResult,
    PIIFilter,
    AnomalyDetector,
    get_r2_telemetry,
    reset_r2_telemetry
)


@pytest.fixture(autouse=True)
def reset_telemetry_fixture():
    """Reset telemetry before each test"""
    reset_r2_telemetry()
    yield
    reset_r2_telemetry()


@pytest.mark.unit
@pytest.mark.observability
def test_r2_telemetry_initialization():
    """Test R-2 telemetry basic initialization"""
    telemetry = R2AgentTelemetry(service_name="test-r2-agent")
    assert telemetry.service_name == "test-r2-agent"
    assert telemetry.anomaly_detector is not None
    assert isinstance(telemetry.enabled, bool)


@pytest.mark.unit
@pytest.mark.observability
def test_correlation_id_generation():
    """Test correlation ID generation for distributed tracing"""
    telemetry = R2AgentTelemetry()
    
    correlation_id = telemetry.generate_correlation_id()
    assert correlation_id.startswith("r2-")
    assert len(correlation_id) > 15
    
    # IDs should be unique
    correlation_id2 = telemetry.generate_correlation_id()
    assert correlation_id != correlation_id2


@pytest.mark.unit
@pytest.mark.observability
def test_trace_agent_operation_success():
    """Test successful agent operation tracing"""
    telemetry = R2AgentTelemetry()
    
    with telemetry.trace_agent_operation(
        "dependency_audit",
        context_tag="test_audit_001",
        symbolic_anchor="T1:42"
    ) as metrics:
        time.sleep(0.01)
        metrics.decisions_made = 5
        metrics.tools_invoked = ["tool1", "tool2"]
        metrics.artifacts_generated = 2
    
    # Verify metrics were recorded
    summary = telemetry.get_metrics_summary()
    assert summary["total_operations"] == 1
    assert summary["successful_operations"] == 1
    assert summary["failed_operations"] == 0
    assert summary["success_rate"] == 1.0
    
    # Verify operation details
    operations = telemetry.get_recent_operations(limit=1)
    assert len(operations) == 1
    op = operations[0]
    assert op.operation_type == "dependency_audit"
    assert op.success is True
    assert op.decisions_made == 5
    assert op.tools_invoked == ["tool1", "tool2"]
    assert op.context_tag == "test_audit_001"
    assert op.symbolic_anchor == "T1:42"


@pytest.mark.unit
@pytest.mark.observability
def test_trace_agent_operation_failure():
    """Test failed agent operation tracing"""
    telemetry = R2AgentTelemetry()
    
    with pytest.raises(ValueError):
        with telemetry.trace_agent_operation(
            "health_check",
            context_tag="test_health_001"
        ):
            raise ValueError("Test error")
    
    # Verify failure was recorded
    summary = telemetry.get_metrics_summary()
    assert summary["total_operations"] == 1
    assert summary["failed_operations"] == 1
    assert summary["success_rate"] == 0.0
    
    # Verify error details
    operations = telemetry.get_recent_operations(include_failures_only=True)
    assert len(operations) == 1
    assert operations[0].success is False
    assert operations[0].error_type == "ValueError"
    assert "Test error" in operations[0].error_message


@pytest.mark.unit
@pytest.mark.observability
def test_pii_filter_dict():
    """Test PII filtering from dictionary data"""
    data = {
        "username": "john_doe",
        "email": "john@example.com",
        "api_key": "secret123456",
        "normal_field": "safe_value",
        "nested": {
            "password": "my_password",
            "data": "public_data"
        }
    }
    
    filtered = PIIFilter.filter_dict(data)
    
    assert filtered["username"] == "john_doe"  # username is safe
    assert filtered["email"] == "[REDACTED]"
    assert filtered["api_key"] == "[REDACTED]"
    assert filtered["normal_field"] == "safe_value"
    assert filtered["nested"]["password"] == "[REDACTED]"
    assert filtered["nested"]["data"] == "public_data"


@pytest.mark.unit
@pytest.mark.observability
def test_pii_filter_string():
    """Test PII filtering from string content"""
    text = "Contact john@example.com for access token abc123def456ghi789"
    
    filtered = PIIFilter.filter_string(text)
    
    assert "john@example.com" not in filtered
    assert "[REDACTED]" in filtered
    assert "abc123def456ghi789" not in filtered


@pytest.mark.unit
@pytest.mark.observability
def test_pii_filtering_enabled():
    """Test that PII filtering is applied to operation metadata"""
    telemetry = R2AgentTelemetry(enable_pii_filtering=True)
    
    with telemetry.trace_agent_operation(
        "test_operation",
        email="user@example.com",
        api_key="secret123"
    ):
        pass
    
    operations = telemetry.get_recent_operations(limit=1)
    metadata = operations[0].metadata
    
    assert metadata["email"] == "[REDACTED]"
    assert metadata["api_key"] == "[REDACTED]"


@pytest.mark.unit
@pytest.mark.observability
def test_anomaly_detector_duration():
    """Test anomaly detection for unusually long durations"""
    detector = AnomalyDetector(window_size=50, z_threshold=2.0)
    
    # Add normal operations
    for _ in range(30):
        metrics = AgentOperationMetrics(
            operation_id="test",
            operation_type="test",
            start_time=time.time(),
            duration_ms=100.0,
            success=True
        )
        detector.update_metrics(metrics)
    
    # Add anomalous operation (10x slower)
    anomalous_metrics = AgentOperationMetrics(
        operation_id="test_slow",
        operation_type="test",
        start_time=time.time(),
        duration_ms=1000.0,
        success=True
    )
    
    # Must update metrics first to maintain history
    detector.update_metrics(anomalous_metrics)
    anomalies = detector.detect_anomalies(anomalous_metrics)
    
    assert len(anomalies) > 0
    assert any(a.anomaly_type == "duration_ms" for a in anomalies)


@pytest.mark.unit
@pytest.mark.observability
def test_anomaly_detector_failure_rate():
    """Test anomaly detection for high failure rates"""
    detector = AnomalyDetector()
    
    # Add many failures
    for i in range(30):
        metrics = AgentOperationMetrics(
            operation_id=f"test_{i}",
            operation_type="test",
            start_time=time.time(),
            success=False if i % 2 == 0 else True  # 50% failure rate
        )
        detector.update_metrics(metrics)
    
    # Check for failure rate anomaly
    test_metrics = AgentOperationMetrics(
        operation_id="test",
        operation_type="test",
        start_time=time.time(),
        success=False
    )
    
    anomalies = detector.detect_anomalies(test_metrics)
    
    # Should detect high failure rate
    assert any(a.anomaly_type == "high_failure_rate" for a in anomalies)


@pytest.mark.unit
@pytest.mark.observability
def test_metrics_summary_filtering():
    """Test metrics summary with time window filtering"""
    telemetry = R2AgentTelemetry()
    
    # Add operation from "past"
    with telemetry.trace_agent_operation("old_operation"):
        pass
    
    # Manually adjust timestamp to simulate old operation
    telemetry._operation_metrics[0].start_time = time.time() - 7200  # 2 hours ago
    
    # Add recent operation
    with telemetry.trace_agent_operation("recent_operation"):
        pass
    
    # Summary with 1 hour window should only include recent
    summary = telemetry.get_metrics_summary(time_window_seconds=3600)
    assert summary["total_operations"] == 1
    
    # Summary without window should include both
    summary_all = telemetry.get_metrics_summary()
    assert summary_all["total_operations"] == 2


@pytest.mark.unit
@pytest.mark.observability
def test_prometheus_export_format():
    """Test Prometheus metrics export format"""
    telemetry = R2AgentTelemetry()
    
    # Record some operations
    with telemetry.trace_agent_operation("dependency_audit"):
        pass
    
    with telemetry.trace_agent_operation("health_check"):
        pass
    
    prometheus_data = telemetry.export_prometheus_metrics()
    
    # Verify format
    assert "r2_agent_operations_total" in prometheus_data
    assert "r2_agent_operations_success" in prometheus_data
    assert "r2_agent_anomalies_detected" in prometheus_data
    assert 'operation_type="dependency_audit"' in prometheus_data
    assert 'operation_type="health_check"' in prometheus_data


@pytest.mark.unit
@pytest.mark.observability
def test_operation_filtering_by_type():
    """Test filtering operations by type"""
    telemetry = R2AgentTelemetry()
    
    # Add different operation types
    with telemetry.trace_agent_operation("audit"):
        pass
    
    with telemetry.trace_agent_operation("health_check"):
        pass
    
    with telemetry.trace_agent_operation("audit"):
        pass
    
    # Filter by type
    audit_ops = telemetry.get_recent_operations(operation_type="audit")
    assert len(audit_ops) == 2
    assert all(op.operation_type == "audit" for op in audit_ops)
    
    health_ops = telemetry.get_recent_operations(operation_type="health_check")
    assert len(health_ops) == 1


@pytest.mark.unit
@pytest.mark.observability
def test_global_telemetry_instance():
    """Test global R-2 telemetry singleton"""
    reset_r2_telemetry()
    
    telemetry1 = get_r2_telemetry(service_name="r2-test")
    telemetry2 = get_r2_telemetry()
    
    # Should return same instance
    assert telemetry1 is telemetry2
    assert telemetry1.service_name == "r2-test"


@pytest.mark.unit
@pytest.mark.observability
def test_resource_metrics_capture():
    """Test resource usage metrics capture"""
    telemetry = R2AgentTelemetry()
    
    with telemetry.trace_agent_operation("resource_test") as metrics:
        # Do some work
        _ = [i ** 2 for i in range(10000)]
    
    operations = telemetry.get_recent_operations(limit=1)
    op = operations[0]
    
    # Should have captured resource metrics (if psutil available)
    if telemetry._process:
        assert op.cpu_usage_percent is not None
        assert op.memory_usage_mb is not None


@pytest.mark.unit
@pytest.mark.observability
def test_anomaly_detection_integration():
    """Test full anomaly detection integration"""
    telemetry = R2AgentTelemetry(enable_anomaly_detection=True)
    
    # Add normal operations
    for _ in range(30):
        with telemetry.trace_agent_operation("normal_op"):
            time.sleep(0.001)
    
    # Add anomalous operation
    with telemetry.trace_agent_operation("slow_op"):
        time.sleep(0.1)  # Much slower
    
    # Check if anomaly was detected
    summary = telemetry.get_metrics_summary()
    assert summary["anomaly_count"] > 0


@pytest.mark.unit
@pytest.mark.observability
def test_operation_metadata_tracking():
    """Test that operation metadata is properly tracked"""
    telemetry = R2AgentTelemetry()
    
    with telemetry.trace_agent_operation(
        "test_op",
        context_tag="ctx_001",
        symbolic_anchor="T1:100",
        custom_field="custom_value",
        repo="test-repo"
    ) as metrics:
        metrics.decisions_made = 7
        metrics.repositories_accessed = ["repo1", "repo2"]
        metrics.artifacts_generated = 3
    
    operations = telemetry.get_recent_operations(limit=1)
    op = operations[0]
    
    assert op.context_tag == "ctx_001"
    assert op.symbolic_anchor == "T1:100"
    assert op.decisions_made == 7
    assert op.repositories_accessed == ["repo1", "repo2"]
    assert op.artifacts_generated == 3
    assert op.metadata["custom_field"] == "custom_value"


@pytest.mark.integration
@pytest.mark.observability
@pytest.mark.slow  # #792: concurrent operations with per-task asyncio.sleep
async def test_concurrent_operations():
    """Test telemetry with concurrent operations"""
    telemetry = R2AgentTelemetry()
    
    async def run_operation(op_type: str, duration: float):
        with telemetry.trace_agent_operation(op_type):
            await asyncio.sleep(duration)
    
    # Run multiple operations concurrently
    await asyncio.gather(
        run_operation("op1", 0.01),
        run_operation("op2", 0.01),
        run_operation("op3", 0.01),
    )
    
    summary = telemetry.get_metrics_summary()
    assert summary["total_operations"] == 3
    assert summary["successful_operations"] == 3


@pytest.mark.unit
@pytest.mark.observability
def test_telemetry_with_disabled_otel():
    """Test telemetry works even without OpenTelemetry"""
    telemetry = R2AgentTelemetry(enable_otel=False)
    
    # Should still work in fallback mode
    with telemetry.trace_agent_operation("fallback_test"):
        pass
    
    summary = telemetry.get_metrics_summary()
    assert summary["total_operations"] == 1


@pytest.mark.unit
@pytest.mark.observability
def test_metrics_snapshot_with_context_tag():
    """Test metrics snapshot includes DLP context tag"""
    telemetry = R2AgentTelemetry()
    
    with telemetry.trace_agent_operation("test"):
        pass
    
    summary = telemetry.get_metrics_summary(context_tag="dlp_export_001")
    assert summary["context_tag"] == "dlp_export_001"
    assert summary["total_operations"] == 1
