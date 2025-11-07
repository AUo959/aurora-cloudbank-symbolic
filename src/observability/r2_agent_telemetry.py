"""
R-2 Agent Production Telemetry Integration

Provides comprehensive observability for R-2 agent operations including:
- Distributed tracing for agent execution flows
- Performance metrics (latency, throughput, success rate)
- Resource usage tracking (CPU, memory, I/O)
- Anomaly detection for unusual behavior patterns
- Privacy-preserving telemetry with PII filtering
- Integration with visualization platforms

DLP Integration: All telemetry includes context tags and symbolic anchors
for complete lineage tracking and governance compliance.
"""

import logging
import time
import hashlib
import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime
from collections import deque, defaultdict

# Optional dependencies with graceful fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

try:
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.trace import Status, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None
    metrics = None

logger = logging.getLogger(__name__)


@dataclass
class AgentOperationMetrics:
    """Metrics for a single R-2 agent operation"""
    operation_id: str
    operation_type: str
    start_time: float
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    
    # Performance metrics
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    io_read_bytes: Optional[int] = None
    io_write_bytes: Optional[int] = None
    
    # Agent-specific metrics
    decisions_made: int = 0
    tools_invoked: List[str] = field(default_factory=list)
    repositories_accessed: List[str] = field(default_factory=list)
    artifacts_generated: int = 0
    
    # DLP tracking
    context_tag: Optional[str] = None
    symbolic_anchor: Optional[str] = None
    correlation_id: Optional[str] = None
    
    # Additional attributes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection analysis"""
    is_anomalous: bool
    anomaly_score: float
    anomaly_type: Optional[str] = None
    threshold: float = 0.0
    baseline_value: Optional[float] = None
    current_value: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


class PIIFilter:
    """Filter to remove PII from telemetry data"""
    
    # Patterns that might contain PII
    PII_PATTERNS = [
        'email', 'password', 'token', 'api_key', 'secret',
        'ssn', 'credit_card', 'phone', 'address', 'name'
    ]
    
    @staticmethod
    def filter_dict(data: Dict[str, Any], redact_value: str = "[REDACTED]") -> Dict[str, Any]:
        """
        Recursively filter PII from dictionary data
        
        Args:
            data: Dictionary to filter
            redact_value: Value to use for redacted fields
            
        Returns:
            Filtered dictionary with PII removed
        """
        if not isinstance(data, dict):
            return data
            
        filtered = {}
        for key, value in data.items():
            # Check if key suggests PII
            key_lower = key.lower()
            if any(pattern in key_lower for pattern in PIIFilter.PII_PATTERNS):
                filtered[key] = redact_value
            elif isinstance(value, dict):
                filtered[key] = PIIFilter.filter_dict(value, redact_value)
            elif isinstance(value, list):
                filtered[key] = [
                    PIIFilter.filter_dict(item, redact_value) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                filtered[key] = value
                
        return filtered
    
    @staticmethod
    def filter_string(text: str, redact_value: str = "[REDACTED]") -> str:
        """
        Filter potential PII from string content
        
        Args:
            text: Text to filter
            redact_value: Value to use for redacted content
            
        Returns:
            Filtered text
        """
        # Simple implementation - can be enhanced with regex patterns
        import re
        
        # Email pattern
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', redact_value, text)
        
        # API key patterns (common formats)
        text = re.sub(r'\b[A-Za-z0-9]{32,}\b', redact_value, text)
        
        # Token patterns
        text = re.sub(r'(token|key|secret)["\s:=]+[A-Za-z0-9_-]+', f'\\1: {redact_value}', text, flags=re.IGNORECASE)
        
        return text


class AnomalyDetector:
    """
    Statistical anomaly detection for agent operations
    
    Uses simple statistical methods to detect unusual patterns:
    - Z-score for continuous metrics
    - Moving average for time series
    - Threshold-based for discrete events
    """
    
    def __init__(self, window_size: int = 100, z_threshold: float = 3.0):
        """
        Initialize anomaly detector
        
        Args:
            window_size: Number of recent observations to track
            z_threshold: Z-score threshold for anomaly detection
        """
        self.window_size = window_size
        self.z_threshold = z_threshold
        
        # Track recent metrics
        self._duration_history: deque = deque(maxlen=window_size)
        self._cpu_history: deque = deque(maxlen=window_size)
        self._memory_history: deque = deque(maxlen=window_size)
        self._error_history: deque = deque(maxlen=window_size)
        
        # Track failure patterns
        self._recent_failures: deque = deque(maxlen=50)
        self._failure_rate_threshold = 0.3  # 30% failure rate triggers anomaly
    
    def update_metrics(self, metrics: AgentOperationMetrics):
        """Update detector with new metrics"""
        if metrics.duration_ms:
            self._duration_history.append(metrics.duration_ms)
        if metrics.cpu_usage_percent:
            self._cpu_history.append(metrics.cpu_usage_percent)
        if metrics.memory_usage_mb:
            self._memory_history.append(metrics.memory_usage_mb)
        
        self._error_history.append(0 if metrics.success else 1)
        
        if not metrics.success:
            self._recent_failures.append({
                'timestamp': time.time(),
                'error_type': metrics.error_type,
                'operation_type': metrics.operation_type
            })
    
    def detect_anomalies(self, metrics: AgentOperationMetrics) -> List[AnomalyDetectionResult]:
        """
        Detect anomalies in given metrics
        
        Args:
            metrics: Operation metrics to analyze
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check duration anomaly
        if metrics.duration_ms and len(self._duration_history) > 10:
            duration_anomaly = self._check_z_score_anomaly(
                metrics.duration_ms,
                self._duration_history,
                "duration_ms",
                "Unusually long operation duration"
            )
            if duration_anomaly:
                anomalies.append(duration_anomaly)
        
        # Check CPU anomaly
        if metrics.cpu_usage_percent and len(self._cpu_history) > 10:
            cpu_anomaly = self._check_z_score_anomaly(
                metrics.cpu_usage_percent,
                self._cpu_history,
                "cpu_usage",
                "Unusually high CPU usage"
            )
            if cpu_anomaly:
                anomalies.append(cpu_anomaly)
        
        # Check memory anomaly
        if metrics.memory_usage_mb and len(self._memory_history) > 10:
            memory_anomaly = self._check_z_score_anomaly(
                metrics.memory_usage_mb,
                self._memory_history,
                "memory_usage",
                "Unusually high memory usage"
            )
            if memory_anomaly:
                anomalies.append(memory_anomaly)
        
        # Check failure rate anomaly
        if len(self._error_history) > 20:
            failure_rate = sum(self._error_history) / len(self._error_history)
            if failure_rate > self._failure_rate_threshold:
                anomalies.append(AnomalyDetectionResult(
                    is_anomalous=True,
                    anomaly_score=failure_rate,
                    anomaly_type="high_failure_rate",
                    threshold=self._failure_rate_threshold,
                    current_value=failure_rate,
                    details={"recent_failures": len([f for f in self._recent_failures])}
                ))
        
        return anomalies
    
    def _check_z_score_anomaly(
        self,
        value: float,
        history: deque,
        metric_name: str,
        description: str
    ) -> Optional[AnomalyDetectionResult]:
        """Check if value is anomalous using z-score"""
        if len(history) < 10:
            return None
        
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return None
        
        z_score = abs((value - mean) / std_dev)
        
        if z_score > self.z_threshold:
            return AnomalyDetectionResult(
                is_anomalous=True,
                anomaly_score=z_score,
                anomaly_type=metric_name,
                threshold=self.z_threshold,
                baseline_value=mean,
                current_value=value,
                details={"description": description}
            )
        
        return None


class R2AgentTelemetry:
    """
    Production telemetry system for R-2 agent operations
    
    Provides comprehensive observability including:
    - Distributed tracing with correlation IDs
    - Performance and resource metrics
    - Anomaly detection
    - Privacy-preserving data collection
    - Prometheus-compatible export
    """
    
    def __init__(
        self,
        service_name: str = "r2-agent",
        enable_otel: bool = True,
        enable_anomaly_detection: bool = True,
        enable_pii_filtering: bool = True
    ):
        """
        Initialize R-2 agent telemetry
        
        Args:
            service_name: Service identifier for telemetry
            enable_otel: Enable OpenTelemetry integration
            enable_anomaly_detection: Enable anomaly detection
            enable_pii_filtering: Enable PII filtering
        """
        self.service_name = service_name
        self.enabled = OTEL_AVAILABLE and enable_otel
        self.pii_filter_enabled = enable_pii_filtering
        
        # Metrics storage
        self._operation_metrics: List[AgentOperationMetrics] = []
        self._metrics_lock = threading.Lock()
        
        # Anomaly detection
        self.anomaly_detector = AnomalyDetector() if enable_anomaly_detection else None
        self._detected_anomalies: List[AnomalyDetectionResult] = []
        
        # Performance counters
        self._operation_counts = defaultdict(int)
        self._success_counts = defaultdict(int)
        self._error_counts = defaultdict(int)
        
        # Process monitoring (optional - requires psutil)
        if PSUTIL_AVAILABLE:
            try:
                self._process = psutil.Process()
            except Exception as e:
                self._process = None
                logger.debug("Process monitoring unavailable: %s", e)
        else:
            self._process = None
            logger.debug("psutil not available - resource monitoring disabled")
        
        # Initialize OpenTelemetry
        if self.enabled:
            self._setup_otel()
        else:
            logger.info("R-2 telemetry running in fallback mode (OpenTelemetry unavailable)")
    
    def _setup_otel(self):
        """Initialize OpenTelemetry instrumentation"""
        try:
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
                "service.type": "agent",
                "deployment.environment": "production"
            })
            
            # Setup tracing
            tracer_provider = TracerProvider(resource=resource)
            trace.set_tracer_provider(tracer_provider)
            self.tracer = trace.get_tracer(__name__)
            
            # Setup metrics
            meter_provider = MeterProvider(resource=resource)
            metrics.set_meter_provider(meter_provider)
            self.meter = metrics.get_meter(__name__)
            
            # Create metric instruments
            self._operation_duration_histogram = self.meter.create_histogram(
                name="r2.agent.operation.duration",
                description="Duration of R-2 agent operations",
                unit="ms"
            )
            
            self._operation_counter = self.meter.create_counter(
                name="r2.agent.operations.total",
                description="Total count of agent operations",
                unit="1"
            )
            
            self._success_counter = self.meter.create_counter(
                name="r2.agent.operations.success",
                description="Successful operations count",
                unit="1"
            )
            
            self._error_counter = self.meter.create_counter(
                name="r2.agent.operations.errors",
                description="Failed operations count",
                unit="1"
            )
            
            self._cpu_gauge = self.meter.create_gauge(
                name="r2.agent.resource.cpu",
                description="CPU usage percentage",
                unit="%"
            )
            
            self._memory_gauge = self.meter.create_gauge(
                name="r2.agent.resource.memory",
                description="Memory usage in MB",
                unit="MB"
            )
            
            self._anomaly_counter = self.meter.create_counter(
                name="r2.agent.anomalies.detected",
                description="Count of detected anomalies",
                unit="1"
            )
            
            logger.info("OpenTelemetry initialized for R-2 agent telemetry")
            
        except Exception as e:
            logger.error("Failed to initialize OpenTelemetry: %s", e)
            self.enabled = False
    
    def generate_correlation_id(self) -> str:
        """Generate unique correlation ID for distributed tracing"""
        timestamp = str(time.time())
        random_component = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:16]
        return f"r2-{timestamp[:10]}-{random_component}"
    
    def _capture_resource_metrics(self) -> Dict[str, float]:
        """Capture current resource usage metrics"""
        if not self._process:
            return {}
        
        try:
            cpu_percent = self._process.cpu_percent(interval=0.1)
            memory_info = self._process.memory_info()
            io_counters = self._process.io_counters() if hasattr(self._process, 'io_counters') else None
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': self._process.memory_percent()
            }
            
            if io_counters:
                metrics['io_read_bytes'] = io_counters.read_bytes
                metrics['io_write_bytes'] = io_counters.write_bytes
            
            return metrics
        except Exception as e:
            logger.debug("Failed to capture resource metrics: %s", e)
            return {}
    
    @contextmanager
    def trace_agent_operation(
        self,
        operation_type: str,
        context_tag: Optional[str] = None,
        symbolic_anchor: Optional[str] = None,
        **metadata
    ):
        """
        Context manager for tracing R-2 agent operations
        
        Args:
            operation_type: Type of operation (e.g., 'dependency_audit', 'health_check')
            context_tag: DLP context tag for lineage tracking
            symbolic_anchor: Aurora symbolic anchor
            **metadata: Additional metadata to attach
        
        Example:
            with telemetry.trace_agent_operation(
                "dependency_audit",
                context_tag="audit_2024_001",
                symbolic_anchor="T1:42"
            ):
                # Your R-2 agent operation here
                pass
        """
        # Generate correlation ID
        correlation_id = self.generate_correlation_id()
        operation_id = hashlib.sha256(f"{operation_type}-{correlation_id}".encode()).hexdigest()[:16]
        
        # Create metrics object
        start_time = time.time()
        start_resources = self._capture_resource_metrics()
        
        operation_metrics = AgentOperationMetrics(
            operation_id=operation_id,
            operation_type=operation_type,
            start_time=start_time,
            context_tag=context_tag,
            symbolic_anchor=symbolic_anchor,
            correlation_id=correlation_id,
            metadata=metadata
        )
        
        # Start OpenTelemetry span if available
        span = None
        if self.enabled and self.tracer:
            span = self.tracer.start_span(f"r2.agent.{operation_type}")
            span.set_attribute("operation.id", operation_id)
            span.set_attribute("operation.type", operation_type)
            span.set_attribute("correlation.id", correlation_id)
            if context_tag:
                span.set_attribute("dlp.context_tag", context_tag)
            if symbolic_anchor:
                span.set_attribute("aurora.symbolic_anchor", symbolic_anchor)
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    span.set_attribute(f"metadata.{key}", value)
        
        try:
            yield operation_metrics
            
            # Operation completed successfully
            operation_metrics.success = True
            
            if span:
                span.set_status(Status(StatusCode.OK))
            
        except Exception as e:
            # Operation failed
            operation_metrics.success = False
            operation_metrics.error_type = type(e).__name__
            operation_metrics.error_message = str(e)
            
            if span:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
            
            raise
            
        finally:
            # Finalize metrics
            end_time = time.time()
            operation_metrics.end_time = end_time
            operation_metrics.duration_ms = (end_time - start_time) * 1000
            
            # Capture end resource metrics
            end_resources = self._capture_resource_metrics()
            operation_metrics.cpu_usage_percent = end_resources.get('cpu_percent')
            operation_metrics.memory_usage_mb = end_resources.get('memory_mb')
            operation_metrics.io_read_bytes = end_resources.get('io_read_bytes')
            operation_metrics.io_write_bytes = end_resources.get('io_write_bytes')
            
            # Apply PII filtering
            if self.pii_filter_enabled:
                operation_metrics.metadata = PIIFilter.filter_dict(operation_metrics.metadata)
                if operation_metrics.error_message:
                    operation_metrics.error_message = PIIFilter.filter_string(operation_metrics.error_message)
            
            # Record metrics
            self._record_operation_metrics(operation_metrics)
            
            # Detect anomalies
            if self.anomaly_detector:
                anomalies = self.anomaly_detector.detect_anomalies(operation_metrics)
                if anomalies:
                    self._handle_anomalies(operation_metrics, anomalies)
            
            # End span
            if span:
                span.end()
    
    def _record_operation_metrics(self, metrics: AgentOperationMetrics):
        """Record operation metrics"""
        with self._metrics_lock:
            self._operation_metrics.append(metrics)
            
            # Update counters
            self._operation_counts[metrics.operation_type] += 1
            if metrics.success:
                self._success_counts[metrics.operation_type] += 1
            else:
                self._error_counts[metrics.operation_type] += 1
            
            # Update anomaly detector
            if self.anomaly_detector:
                self.anomaly_detector.update_metrics(metrics)
        
        # Record to OpenTelemetry
        if self.enabled:
            attrs = {"operation_type": metrics.operation_type}
            
            self._operation_counter.add(1, attributes=attrs)
            
            if metrics.success:
                self._success_counter.add(1, attributes=attrs)
            else:
                self._error_counter.add(1, attributes={
                    **attrs,
                    "error_type": metrics.error_type or "unknown"
                })
            
            if metrics.duration_ms:
                self._operation_duration_histogram.record(metrics.duration_ms, attributes=attrs)
            
            if metrics.cpu_usage_percent:
                self._cpu_gauge.set(metrics.cpu_usage_percent, attributes=attrs)
            
            if metrics.memory_usage_mb:
                self._memory_gauge.set(metrics.memory_usage_mb, attributes=attrs)
    
    def _handle_anomalies(self, metrics: AgentOperationMetrics, anomalies: List[AnomalyDetectionResult]):
        """Handle detected anomalies"""
        for anomaly in anomalies:
            self._detected_anomalies.append(anomaly)
            
            # Log anomaly
            logger.warning(
                "Anomaly detected in R-2 agent operation: %s | Operation: %s | Score: %.2f",
                anomaly.anomaly_type,
                metrics.operation_type,
                anomaly.anomaly_score
            )
            
            # Record to OpenTelemetry
            if self.enabled and hasattr(self, '_anomaly_counter'):
                self._anomaly_counter.add(1, attributes={
                    "anomaly_type": anomaly.anomaly_type or "unknown",
                    "operation_type": metrics.operation_type
                })
    
    def get_metrics_summary(
        self,
        time_window_seconds: Optional[int] = None,
        context_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary of collected metrics
        
        Args:
            time_window_seconds: Optional time window to filter metrics
            context_tag: Optional DLP context tag for export
            
        Returns:
            Summary dictionary with metrics
        """
        with self._metrics_lock:
            metrics = self._operation_metrics.copy()
        
        # Filter by time window if specified
        if time_window_seconds:
            cutoff_time = time.time() - time_window_seconds
            metrics = [m for m in metrics if m.start_time >= cutoff_time]
        
        # Calculate summary statistics
        total_operations = len(metrics)
        successful_operations = sum(1 for m in metrics if m.success)
        failed_operations = total_operations - successful_operations
        
        durations = [m.duration_ms for m in metrics if m.duration_ms]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Group by operation type
        operations_by_type = defaultdict(lambda: {"count": 0, "success": 0, "failures": 0})
        for m in metrics:
            operations_by_type[m.operation_type]["count"] += 1
            if m.success:
                operations_by_type[m.operation_type]["success"] += 1
            else:
                operations_by_type[m.operation_type]["failures"] += 1
        
        # Recent anomalies
        recent_anomalies = self._detected_anomalies[-10:] if self._detected_anomalies else []
        
        summary = {
            "service_name": self.service_name,
            "timestamp": time.time(),
            "context_tag": context_tag,
            "time_window_seconds": time_window_seconds,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
            "average_duration_ms": avg_duration,
            "operations_by_type": dict(operations_by_type),
            "recent_anomalies": [asdict(a) for a in recent_anomalies],
            "anomaly_count": len(self._detected_anomalies)
        }
        
        return summary
    
    def export_prometheus_metrics(self) -> str:
        """
        Export metrics in Prometheus text format
        
        Returns:
            Prometheus-formatted metrics
        """
        lines = []
        
        # Operations total
        lines.append("# HELP r2_agent_operations_total Total count of R-2 agent operations")
        lines.append("# TYPE r2_agent_operations_total counter")
        for op_type, count in self._operation_counts.items():
            lines.append(f'r2_agent_operations_total{{operation_type="{op_type}"}} {count}')
        
        lines.append("")
        
        # Success counter
        lines.append("# HELP r2_agent_operations_success Successful R-2 agent operations")
        lines.append("# TYPE r2_agent_operations_success counter")
        for op_type, count in self._success_counts.items():
            lines.append(f'r2_agent_operations_success{{operation_type="{op_type}"}} {count}')
        
        lines.append("")
        
        # Error counter
        lines.append("# HELP r2_agent_operations_errors Failed R-2 agent operations")
        lines.append("# TYPE r2_agent_operations_errors counter")
        for op_type, count in self._error_counts.items():
            lines.append(f'r2_agent_operations_errors{{operation_type="{op_type}"}} {count}')
        
        lines.append("")
        
        # Anomaly counter
        lines.append("# HELP r2_agent_anomalies_detected Total anomalies detected")
        lines.append("# TYPE r2_agent_anomalies_detected counter")
        lines.append(f'r2_agent_anomalies_detected {len(self._detected_anomalies)}')
        
        return "\n".join(lines) + "\n"
    
    def get_recent_operations(
        self,
        limit: int = 10,
        operation_type: Optional[str] = None,
        include_failures_only: bool = False
    ) -> List[AgentOperationMetrics]:
        """
        Get recent operations
        
        Args:
            limit: Maximum number of operations to return
            operation_type: Filter by operation type
            include_failures_only: Only return failed operations
            
        Returns:
            List of operation metrics
        """
        with self._metrics_lock:
            metrics = self._operation_metrics.copy()
        
        # Apply filters
        if operation_type:
            metrics = [m for m in metrics if m.operation_type == operation_type]
        
        if include_failures_only:
            metrics = [m for m in metrics if not m.success]
        
        # Sort by start time (most recent first) and limit
        metrics.sort(key=lambda m: m.start_time, reverse=True)
        return metrics[:limit]


# Global telemetry instance for R-2 agent
_global_r2_telemetry: Optional[R2AgentTelemetry] = None


def get_r2_telemetry(**kwargs) -> R2AgentTelemetry:
    """Get or create global R-2 agent telemetry instance"""
    global _global_r2_telemetry
    if _global_r2_telemetry is None:
        _global_r2_telemetry = R2AgentTelemetry(**kwargs)
    return _global_r2_telemetry


def reset_r2_telemetry():
    """Reset global R-2 telemetry instance (useful for testing)"""
    global _global_r2_telemetry
    _global_r2_telemetry = None
