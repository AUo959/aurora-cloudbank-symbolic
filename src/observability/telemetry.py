"""
Aurora OpenTelemetry Integration

Provides comprehensive observability through OpenTelemetry:
- Distributed tracing for request flows
- Performance metrics collection
- Adoption and usage analytics
- Prometheus export support

DLP Integration: All metrics include context tags for lineage tracking
"""

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from functools import wraps

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.prometheus import PrometheusMetricReader
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None
    metrics = None

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot of collected metrics for export"""
    timestamp: float
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    adoption_metrics: Dict[str, int] = field(default_factory=dict)
    error_metrics: Dict[str, int] = field(default_factory=dict)
    context_tag: Optional[str] = None


class AuroraTelemetry:
    """
    Aurora CloudBank OpenTelemetry Integration
    
    Provides observability through:
    - Distributed tracing with context propagation
    - Performance metrics (latency, throughput, resources)
    - Adoption metrics (feature usage, engagement)
    - Prometheus export for monitoring stacks
    """
    
    def __init__(self, service_name: str = "aurora-cloudbank", enable_prometheus: bool = True):
        """
        Initialize telemetry system
        
        Args:
            service_name: Service identifier for telemetry data
            enable_prometheus: Enable Prometheus metric export endpoint
        """
        self.service_name = service_name
        self.enabled = OTEL_AVAILABLE
        self._prometheus_enabled = enable_prometheus and OTEL_AVAILABLE
        
        # Performance counters
        self._operation_times: Dict[str, List[float]] = {}
        self._operation_counts: Dict[str, int] = {}
        self._error_counts: Dict[str, int] = {}
        
        # Adoption metrics
        self._feature_usage: Dict[str, int] = {}
        self._active_sessions: int = 0
        
        if self.enabled:
            self._setup_otel()
        else:
            logger.warning(
                "OpenTelemetry not available - install with: "
                "pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-prometheus"
            )
            self._setup_fallback()
    
    def _setup_otel(self):
        """Initialize OpenTelemetry SDK"""
        try:
            # Create resource with service identification
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "deployment.environment": "development"
            })
            
            # Setup tracing
            tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)
            
            # Setup metrics with optional Prometheus export
            if self._prometheus_enabled:
                try:
                    prometheus_reader = PrometheusMetricReader()
                    meter_provider = MeterProvider(
                        resource=resource,
                        metric_readers=[prometheus_reader]
                    )
                except Exception as e:
                    logger.warning("Prometheus export not available: %s", e)
                    meter_provider = MeterProvider(resource=resource)
            else:
                meter_provider = MeterProvider(resource=resource)
            
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter(__name__)
            
            # Create instruments
            self._operation_duration = self.meter.create_histogram(
                name="aurora.operation.duration",
                description="Duration of Aurora operations in seconds",
                unit="s"
            )
            self._feature_counter = self.meter.create_counter(
                name="aurora.feature.usage",
                description="Count of feature usage",
                unit="1"
            )
            self._error_counter = self.meter.create_counter(
                name="aurora.errors",
                description="Count of errors by type",
                unit="1"
            )
            
            logger.info("OpenTelemetry initialized for service: %s", self.service_name)
            
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry: %s", e)
            self.enabled = False
            self._setup_fallback()
    
    def _setup_fallback(self):
        """Minimal fallback when OpenTelemetry unavailable"""
        self.tracer = None
        self.meter = None
        logger.info("Using fallback telemetry (metrics collection only)")
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Context manager for tracing operations
        
        Args:
            operation_name: Name of the operation to trace
            attributes: Additional attributes to attach to the span
        
        Example:
            with telemetry.trace_operation("process_reflection", {"user_id": "123"}):
                # Your code here
                pass
        """
        start_time = time.time()
        
        if self.enabled and self.tracer:
            with self.tracer.start_as_current_span(operation_name) as span:
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)
                
                try:
                    yield span
                except Exception as e:
                    span.record_exception(e)
                    self.record_error(operation_name, type(e).__name__)
                    raise
                finally:
                    duration = time.time() - start_time
                    self._record_performance(operation_name, duration)
        else:
            # Fallback: just track timing and errors
            try:
                yield None
            except Exception as e:
                self.record_error(operation_name, type(e).__name__)
                raise
            finally:
                duration = time.time() - start_time
                self._record_performance(operation_name, duration)
    
    def trace_async(self, operation_name: str):
        """
        Decorator for tracing async functions
        
        Example:
            @telemetry.trace_async("fetch_data")
            async def fetch_data(user_id: str):
                ...
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                with self.trace_operation(operation_name):
                    return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def _record_performance(self, operation: str, duration: float):
        """Record performance metric"""
        # Update local tracking
        if operation not in self._operation_times:
            self._operation_times[operation] = []
            self._operation_counts[operation] = 0
        
        self._operation_times[operation].append(duration)
        self._operation_counts[operation] += 1
        
        # Record to OpenTelemetry
        if self.enabled and hasattr(self, '_operation_duration'):
            self._operation_duration.record(
                duration,
                attributes={"operation": operation}
            )
    
    def record_feature_usage(self, feature_name: str, count: int = 1):
        """
        Record feature usage for adoption metrics
        
        Args:
            feature_name: Name of the feature being used
            count: Number of times used (default: 1)
        """
        self._feature_usage[feature_name] = self._feature_usage.get(feature_name, 0) + count
        
        if self.enabled and hasattr(self, '_feature_counter'):
            self._feature_counter.add(
                count,
                attributes={"feature": feature_name}
            )
    
    def record_error(self, operation: str, error_type: str):
        """
        Record error occurrence
        
        Args:
            operation: Operation where error occurred
            error_type: Type/class of the error
        """
        key = f"{operation}:{error_type}"
        self._error_counts[key] = self._error_counts.get(key, 0) + 1
        
        if self.enabled and hasattr(self, '_error_counter'):
            self._error_counter.add(
                1,
                attributes={"operation": operation, "error_type": error_type}
            )
    
    def get_metrics_snapshot(self, context_tag: Optional[str] = None) -> MetricSnapshot:
        """
        Get current metrics snapshot for export
        
        Args:
            context_tag: DLP context tag for lineage tracking
        
        Returns:
            MetricSnapshot with current metrics
        """
        # Calculate performance statistics
        performance = {}
        for operation, times in self._operation_times.items():
            if times:
                performance[f"{operation}_avg_ms"] = sum(times) / len(times) * 1000
                performance[f"{operation}_count"] = self._operation_counts[operation]
        
        return MetricSnapshot(
            timestamp=time.time(),
            performance_metrics=performance,
            adoption_metrics=self._feature_usage.copy(),
            error_metrics=self._error_counts.copy(),
            context_tag=context_tag
        )
    
    def export_prometheus_format(self) -> str:
        """
        Export metrics in Prometheus text format
        
        Returns:
            Prometheus-formatted metric data
        """
        lines = []
        lines.append("# HELP aurora_operations_total Total count of operations")
        lines.append("# TYPE aurora_operations_total counter")
        
        for operation, count in self._operation_counts.items():
            lines.append(f'aurora_operations_total{{operation="{operation}"}} {count}')
        
        lines.append("")
        lines.append("# HELP aurora_feature_usage_total Feature usage count")
        lines.append("# TYPE aurora_feature_usage_total counter")
        
        for feature, count in self._feature_usage.items():
            lines.append(f'aurora_feature_usage_total{{feature="{feature}"}} {count}')
        
        return "\n".join(lines) + "\n"


# Global telemetry instance
_global_telemetry: Optional[AuroraTelemetry] = None


def get_telemetry(service_name: str = "aurora-cloudbank") -> AuroraTelemetry:
    """Get or create global telemetry instance"""
    global _global_telemetry
    if _global_telemetry is None:
        _global_telemetry = AuroraTelemetry(service_name)
    return _global_telemetry


def reset_telemetry():
    """Reset global telemetry instance (useful for testing)"""
    global _global_telemetry
    _global_telemetry = None
