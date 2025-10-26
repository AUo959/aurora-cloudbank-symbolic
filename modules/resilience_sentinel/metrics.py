"""
Metrics Collection and Storage

Defines metric types, data structures, and history tracking for the
Resilience Sentinel Dashboard.

Anchor: T1-RSD-001-METRICS
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque


class MetricType(Enum):
    """Types of metrics that can be collected."""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    REQUEST_COUNT = "request_count"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    API_AVAILABILITY = "api_availability"
    HEALTH_SCORE = "health_score"
    ACTIVE_CONNECTIONS = "active_connections"
    QUEUE_DEPTH = "queue_depth"
    CACHE_HIT_RATE = "cache_hit_rate"
    CUSTOM = "custom"


@dataclass
class Metric:
    """
    Represents a single metric measurement.

    Attributes:
        name: Metric name/identifier
        type: Type of metric
        value: Current metric value
        timestamp: When the metric was collected
        unit: Unit of measurement (e.g., 'percent', 'ms', 'count')
        tags: Additional metadata tags
    """
    name: str
    type: MetricType
    value: float
    timestamp: float = field(default_factory=time.time)
    unit: str = ""
    tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type.value,
            "value": self.value,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "unit": self.unit,
            "tags": self.tags,
        }

    def is_above_threshold(self, threshold: float) -> bool:
        """Check if metric value exceeds threshold."""
        return self.value > threshold

    def is_below_threshold(self, threshold: float) -> bool:
        """Check if metric value is below threshold."""
        return self.value < threshold


class MetricHistory:
    """
    Stores and manages historical metric data.

    Implements a rolling window to keep memory usage bounded.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize metric history.

        Args:
            max_size: Maximum number of metrics to store per metric name
        """
        self.max_size = max_size
        self.metrics: Dict[str, deque] = {}
        self.stats_cache: Dict[str, Dict[str, float]] = {}

    def add(self, metric: Metric):
        """
        Add a metric to history.

        Args:
            metric: Metric to add
        """
        if metric.name not in self.metrics:
            self.metrics[metric.name] = deque(maxlen=self.max_size)
            self.stats_cache[metric.name] = {}

        self.metrics[metric.name].append(metric)
        # Invalidate stats cache for this metric
        self.stats_cache[metric.name] = {}

    def get_recent(self, metric_name: str, count: int = 100) -> List[Metric]:
        """
        Get most recent metrics.

        Args:
            metric_name: Name of metric to retrieve
            count: Number of recent metrics to return

        Returns:
            List of recent metrics (most recent last)
        """
        if metric_name not in self.metrics:
            return []

        recent = list(self.metrics[metric_name])
        return recent[-count:] if len(recent) > count else recent

    def get_latest(self, metric_name: str) -> Optional[Metric]:
        """
        Get the most recent metric value.

        Args:
            metric_name: Name of metric to retrieve

        Returns:
            Latest metric or None if no data
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None

        return self.metrics[metric_name][-1]

    def get_average(self, metric_name: str, count: Optional[int] = None) -> Optional[float]:
        """
        Calculate average value over recent metrics.

        Args:
            metric_name: Name of metric
            count: Number of recent values to average (None = all)

        Returns:
            Average value or None if no data
        """
        if metric_name not in self.metrics or not self.metrics[metric_name]:
            return None

        # Check cache
        cache_key = f"avg_{count or 'all'}"
        if cache_key in self.stats_cache.get(metric_name, {}):
            return self.stats_cache[metric_name][cache_key]

        recent = self.get_recent(metric_name, count or self.max_size)
        if not recent:
            return None

        avg = sum(m.value for m in recent) / len(recent)

        # Cache result
        if metric_name not in self.stats_cache:
            self.stats_cache[metric_name] = {}
        self.stats_cache[metric_name][cache_key] = avg

        return avg

    def get_max(self, metric_name: str, count: Optional[int] = None) -> Optional[float]:
        """Get maximum value over recent metrics."""
        recent = self.get_recent(metric_name, count or self.max_size)
        if not recent:
            return None
        return max(m.value for m in recent)

    def get_min(self, metric_name: str, count: Optional[int] = None) -> Optional[float]:
        """Get minimum value over recent metrics."""
        recent = self.get_recent(metric_name, count or self.max_size)
        if not recent:
            return None
        return min(m.value for m in recent)

    def get_trend(self, metric_name: str, count: int = 10) -> str:
        """
        Determine trend direction (increasing/decreasing/stable).

        Args:
            metric_name: Name of metric
            count: Number of recent values to analyze

        Returns:
            "increasing", "decreasing", or "stable"
        """
        recent = self.get_recent(metric_name, count)
        if len(recent) < 2:
            return "stable"

        # Calculate simple linear trend
        values = [m.value for m in recent]
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

        diff = second_half - first_half
        threshold = 0.05 * first_half  # 5% change threshold

        if diff > threshold:
            return "increasing"
        elif diff < -threshold:
            return "decreasing"
        else:
            return "stable"

    def get_stats(self, metric_name: str) -> Dict[str, Any]:
        """
        Get comprehensive statistics for a metric.

        Args:
            metric_name: Name of metric

        Returns:
            Dict with avg, min, max, count, trend, latest
        """
        if metric_name not in self.metrics:
            return {"error": "Metric not found"}

        latest = self.get_latest(metric_name)
        return {
            "metric_name": metric_name,
            "count": len(self.metrics[metric_name]),
            "latest": latest.value if latest else None,
            "average": self.get_average(metric_name),
            "min": self.get_min(metric_name),
            "max": self.get_max(metric_name),
            "trend": self.get_trend(metric_name),
            "timestamp": latest.timestamp if latest else None,
        }

    def clear(self, metric_name: Optional[str] = None):
        """
        Clear metric history.

        Args:
            metric_name: Specific metric to clear (None = clear all)
        """
        if metric_name:
            if metric_name in self.metrics:
                self.metrics[metric_name].clear()
                self.stats_cache[metric_name] = {}
        else:
            self.metrics.clear()
            self.stats_cache.clear()

    def get_all_metrics(self) -> List[str]:
        """Get list of all tracked metric names."""
        return list(self.metrics.keys())

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        return {
            "total_metrics": len(self.metrics),
            "metric_names": self.get_all_metrics(),
            "total_data_points": sum(len(q) for q in self.metrics.values()),
            "max_size": self.max_size,
        }
