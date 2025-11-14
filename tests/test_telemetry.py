"""
Tests for Aurora OpenTelemetry Integration
"""

import pytest
import time
from src.observability import AuroraTelemetry, get_telemetry, reset_telemetry


@pytest.mark.unit
@pytest.mark.observability
def test_telemetry_initialization():
    """Test basic telemetry initialization"""
    telemetry = AuroraTelemetry(service_name="test-service")
    assert telemetry.service_name == "test-service"
    assert isinstance(telemetry.enabled, bool)


@pytest.mark.unit
@pytest.mark.observability
def test_trace_operation_context():
    """Test operation tracing context manager"""
    telemetry = AuroraTelemetry()
    
    with telemetry.trace_operation("test_operation"):
        time.sleep(0.01)
    
    # Should have recorded performance metrics
    snapshot = telemetry.get_metrics_snapshot()
    assert "test_operation_avg_ms" in snapshot.performance_metrics
    assert snapshot.performance_metrics["test_operation_count"] == 1


@pytest.mark.unit
@pytest.mark.observability
def test_feature_usage_tracking():
    """Test feature usage metrics"""
    telemetry = AuroraTelemetry()
    
    telemetry.record_feature_usage("reflection_generation", 5)
    telemetry.record_feature_usage("ticket_creation", 3)
    
    snapshot = telemetry.get_metrics_snapshot()
    assert snapshot.adoption_metrics["reflection_generation"] == 5
    assert snapshot.adoption_metrics["ticket_creation"] == 3


@pytest.mark.unit
@pytest.mark.observability
def test_error_tracking():
    """Test error metric recording"""
    telemetry = AuroraTelemetry()
    
    telemetry.record_error("api_call", "ValueError")
    telemetry.record_error("api_call", "TypeError")
    telemetry.record_error("api_call", "ValueError")
    
    snapshot = telemetry.get_metrics_snapshot()
    assert snapshot.error_metrics["api_call:ValueError"] == 2
    assert snapshot.error_metrics["api_call:TypeError"] == 1


@pytest.mark.unit
@pytest.mark.observability
def test_metrics_snapshot_with_context_tag():
    """Test metrics snapshot includes DLP context tag"""
    telemetry = AuroraTelemetry()
    telemetry.record_feature_usage("test_feature")
    
    snapshot = telemetry.get_metrics_snapshot(context_tag="test_context_123")
    assert snapshot.context_tag == "test_context_123"
    assert isinstance(snapshot.timestamp, float)
    assert "test_feature" in snapshot.adoption_metrics


@pytest.mark.unit
@pytest.mark.observability
def test_trace_operation_with_exception():
    """Test tracing records exceptions"""
    telemetry = AuroraTelemetry()
    
    with pytest.raises(ValueError):
        with telemetry.trace_operation("failing_operation"):
            raise ValueError("Test error")
    
    snapshot = telemetry.get_metrics_snapshot()
    assert "failing_operation:ValueError" in snapshot.error_metrics


@pytest.mark.unit
@pytest.mark.observability
def test_prometheus_export_format():
    """Test Prometheus metric export format"""
    telemetry = AuroraTelemetry()
    
    telemetry.record_feature_usage("api_endpoint", 10)
    with telemetry.trace_operation("test_op"):
        pass
    
    prometheus_data = telemetry.export_prometheus_format()
    
    assert "aurora_operations_total" in prometheus_data
    assert "aurora_feature_usage_total" in prometheus_data
    assert 'feature="api_endpoint"' in prometheus_data
    assert "10" in prometheus_data


@pytest.mark.integration
@pytest.mark.observability
async def test_trace_async_decorator():
    """Test async function tracing decorator"""
    telemetry = AuroraTelemetry()
    
    @telemetry.trace_async("async_operation")
    async def example_async_function():
        await asyncio.sleep(0.01)
        return "result"
    
    import asyncio
    result = await example_async_function()
    assert result == "result"
    
    snapshot = telemetry.get_metrics_snapshot()
    assert "async_operation_count" in snapshot.performance_metrics


@pytest.mark.unit
@pytest.mark.observability
def test_global_telemetry_instance():
    """Test global telemetry singleton pattern"""
    reset_telemetry()
    
    telemetry1 = get_telemetry("service1")
    telemetry2 = get_telemetry("service2")
    
    # Should return same instance
    assert telemetry1 is telemetry2
    assert telemetry1.service_name == "service1"  # First call sets name


@pytest.mark.unit
@pytest.mark.observability
def test_performance_statistics_calculation():
    """Test performance statistics are calculated correctly"""
    telemetry = AuroraTelemetry()
    
    # Record multiple operations
    for i in range(5):
        with telemetry.trace_operation("repeated_op"):
            time.sleep(0.001 * (i + 1))
    
    snapshot = telemetry.get_metrics_snapshot()
    assert snapshot.performance_metrics["repeated_op_count"] == 5
    assert snapshot.performance_metrics["repeated_op_avg_ms"] > 0


@pytest.mark.unit
@pytest.mark.observability
def test_telemetry_fallback_mode():
    """Test telemetry works even without OpenTelemetry installed"""
    telemetry = AuroraTelemetry()
    
    # Should work regardless of OTEL availability
    with telemetry.trace_operation("fallback_test"):
        pass
    
    telemetry.record_feature_usage("fallback_feature")
    snapshot = telemetry.get_metrics_snapshot()
    
    assert "fallback_test_count" in snapshot.performance_metrics
    assert "fallback_feature" in snapshot.adoption_metrics
