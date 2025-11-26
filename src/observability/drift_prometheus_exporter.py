"""
Drift Prometheus Exporter

Prometheus metrics exporter for the DriftDetector system, enabling observability
of drift metrics in Grafana dashboards and alerting pipelines.

DLP: drift_prometheus_exporter_v1
Anchors: EOS_SEED_ORION, HALO_CONTINUITY_GRAFT_005
"""

import logging
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.monitoring.drift_detector import DriftDetector, DriftAlert

logger = logging.getLogger(__name__)


@dataclass
class DriftMetricSnapshot:
    """Snapshot of drift metrics for a specific agent/metric combination."""
    agent_id: str
    metric_name: str
    current_value: float
    baseline_mean: float
    baseline_stddev: float
    deviation: float
    moving_average: float
    timestamp: str


class DriftPrometheusExporter:
    """
    Prometheus Exporter for DriftDetector Metrics

    Exposes drift metrics as Prometheus gauges/counters for monitoring and alerting.
    Integrates with existing DriftDetector instance to provide real-time drift
    delta values per agent/metric.

    DLP: drift_prometheus_exporter_v1
    Anchors: EOS_SEED_ORION, HALO_CONTINUITY_GRAFT_005
    """

    def __init__(
        self,
        drift_detector: Optional["DriftDetector"] = None,
        service_name: str = "aurora-drift-exporter"
    ):
        """
        Initialize drift Prometheus exporter.

        Args:
            drift_detector: Optional DriftDetector instance to integrate with
            service_name: Service identifier for metrics
        """
        self.service_name = service_name
        self._drift_detector = drift_detector
        self._lock = threading.Lock()

        # Metric storage
        self._drift_deltas: Dict[str, float] = {}  # key: agent_id:metric_name
        self._baseline_means: Dict[str, float] = {}
        self._baseline_stddevs: Dict[str, float] = {}
        self._moving_averages: Dict[str, float] = {}
        self._current_values: Dict[str, float] = {}

        # Alert counters: {(agent_id, level, method): count}
        self._alert_counts: Dict[tuple, int] = defaultdict(int)

        # Recent measurements for summary
        self._recent_measurements: List[DriftMetricSnapshot] = []
        self._max_recent = 100

        # Configuration info
        self._config_info: Dict[str, Any] = {}
        if drift_detector:
            self._config_info = {
                "z_score_threshold": drift_detector.z_score_threshold,
                "moving_avg_window": drift_detector.moving_avg_window,
                "info_threshold": drift_detector.info_threshold,
                "warning_threshold": drift_detector.warning_threshold,
                "critical_threshold": drift_detector.critical_threshold,
            }

        logger.info("DriftPrometheusExporter initialized for service: %s", service_name)

    def set_drift_detector(self, drift_detector: "DriftDetector"):
        """
        Set or update the drift detector instance.

        Args:
            drift_detector: DriftDetector instance to integrate with
        """
        self._drift_detector = drift_detector
        self._config_info = {
            "z_score_threshold": drift_detector.z_score_threshold,
            "moving_avg_window": drift_detector.moving_avg_window,
            "info_threshold": drift_detector.info_threshold,
            "warning_threshold": drift_detector.warning_threshold,
            "critical_threshold": drift_detector.critical_threshold,
        }
        logger.info("DriftDetector instance set for exporter")

    def record_drift_measurement(
        self,
        agent_id: str,
        metric_name: str,
        current_value: float,
        baseline_mean: float,
        baseline_stddev: float,
        deviation: float,
        moving_average: float = 0.0
    ):
        """
        Record a drift measurement for Prometheus export.

        Args:
            agent_id: Identifier for the agent
            metric_name: Name of the metric
            current_value: Current metric value
            baseline_mean: Baseline mean value
            baseline_stddev: Baseline standard deviation
            deviation: Calculated deviation from baseline
            moving_average: Current moving average value
        """
        key = f"{agent_id}:{metric_name}"
        timestamp = datetime.now(timezone.utc).isoformat()

        with self._lock:
            self._drift_deltas[key] = deviation
            self._baseline_means[key] = baseline_mean
            self._baseline_stddevs[key] = baseline_stddev
            self._moving_averages[key] = moving_average
            self._current_values[key] = current_value

            # Record snapshot
            snapshot = DriftMetricSnapshot(
                agent_id=agent_id,
                metric_name=metric_name,
                current_value=current_value,
                baseline_mean=baseline_mean,
                baseline_stddev=baseline_stddev,
                deviation=deviation,
                moving_average=moving_average,
                timestamp=timestamp
            )
            self._recent_measurements.append(snapshot)
            if len(self._recent_measurements) > self._max_recent:
                self._recent_measurements.pop(0)

    def record_alert(self, alert: "DriftAlert"):
        """
        Record a drift alert for Prometheus counter increment.

        Args:
            alert: DriftAlert object from DriftDetector
        """
        with self._lock:
            key = (alert.agent_id, alert.level.value, alert.method.value)
            self._alert_counts[key] += 1

    def export_metrics(self) -> str:
        """
        Generate Prometheus text format output.

        Returns:
            Prometheus-formatted metrics string
        """
        lines = []

        with self._lock:
            # Drift delta gauge
            lines.append("# HELP aurora_drift_delta Current drift deviation from baseline")
            lines.append("# TYPE aurora_drift_delta gauge")
            for key, value in self._drift_deltas.items():
                agent_id, metric_name = key.split(":", 1)
                lines.append(
                    f'aurora_drift_delta{{agent_id="{agent_id}",metric_name="{metric_name}"}} {value}'
                )

            lines.append("")

            # Baseline mean gauge
            lines.append("# HELP aurora_drift_baseline_mean Baseline mean value")
            lines.append("# TYPE aurora_drift_baseline_mean gauge")
            for key, value in self._baseline_means.items():
                agent_id, metric_name = key.split(":", 1)
                lines.append(
                    f'aurora_drift_baseline_mean{{agent_id="{agent_id}",metric_name="{metric_name}"}} {value}'
                )

            lines.append("")

            # Baseline stddev gauge
            lines.append("# HELP aurora_drift_baseline_stddev Baseline standard deviation")
            lines.append("# TYPE aurora_drift_baseline_stddev gauge")
            for key, value in self._baseline_stddevs.items():
                agent_id, metric_name = key.split(":", 1)
                lines.append(
                    f'aurora_drift_baseline_stddev{{agent_id="{agent_id}",metric_name="{metric_name}"}} {value}'
                )

            lines.append("")

            # Moving average gauge
            lines.append("# HELP aurora_drift_moving_average Current moving average value")
            lines.append("# TYPE aurora_drift_moving_average gauge")
            for key, value in self._moving_averages.items():
                agent_id, metric_name = key.split(":", 1)
                lines.append(
                    f'aurora_drift_moving_average{{agent_id="{agent_id}",metric_name="{metric_name}"}} {value}'
                )

            lines.append("")

            # Alert counter
            lines.append("# HELP aurora_drift_alerts_total Total drift alerts generated")
            lines.append("# TYPE aurora_drift_alerts_total counter")
            for (agent_id, level, method), count in self._alert_counts.items():
                lines.append(
                    f'aurora_drift_alerts_total{{agent_id="{agent_id}",level="{level}",method="{method}"}} {count}'
                )

            lines.append("")

            # Detector info
            lines.append("# HELP aurora_drift_detector_info Drift detector configuration info")
            lines.append("# TYPE aurora_drift_detector_info gauge")
            if self._config_info:
                labels = ",".join(
                    f'{k}="{v}"' for k, v in self._config_info.items()
                )
                lines.append(f"aurora_drift_detector_info{{{labels}}} 1")
            else:
                lines.append('aurora_drift_detector_info{configured="false"} 0')

        return "\n".join(lines) + "\n"

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Return summary of drift metrics for API consumption.

        Returns:
            Summary dictionary with drift metrics
        """
        with self._lock:
            total_alerts = sum(self._alert_counts.values())

            # Count alerts by level
            alerts_by_level: Dict[str, int] = defaultdict(int)
            for (_, level, _), count in self._alert_counts.items():
                alerts_by_level[level] += count

            # Count alerts by agent
            alerts_by_agent: Dict[str, int] = defaultdict(int)
            for (agent_id, _, _), count in self._alert_counts.items():
                alerts_by_agent[agent_id] += count

            return {
                "service_name": self.service_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_monitored_metrics": len(self._drift_deltas),
                "total_alerts": total_alerts,
                "alerts_by_level": dict(alerts_by_level),
                "alerts_by_agent": dict(alerts_by_agent),
                "config": self._config_info,
                "recent_measurements_count": len(self._recent_measurements),
                "context_tag": "drift_prometheus_exporter_v1",
                "anchors": ["EOS_SEED_ORION", "HALO_CONTINUITY_GRAFT_005"],
            }

    def get_recent_measurements(
        self,
        agent_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get recent drift measurements.

        Args:
            agent_id: Optional filter by agent ID
            limit: Maximum number of measurements to return

        Returns:
            List of measurement dictionaries
        """
        with self._lock:
            measurements = self._recent_measurements.copy()

        if agent_id:
            measurements = [m for m in measurements if m.agent_id == agent_id]

        # Return most recent first
        measurements = measurements[-limit:][::-1]

        return [
            {
                "agent_id": m.agent_id,
                "metric_name": m.metric_name,
                "current_value": m.current_value,
                "baseline_mean": m.baseline_mean,
                "baseline_stddev": m.baseline_stddev,
                "deviation": m.deviation,
                "moving_average": m.moving_average,
                "timestamp": m.timestamp,
            }
            for m in measurements
        ]

    def get_baselines(self) -> Dict[str, Any]:
        """
        Get current baseline configurations.

        Returns:
            Dictionary of baseline configurations
        """
        with self._lock:
            baselines = {}
            for key in self._baseline_means.keys():
                agent_id, metric_name = key.split(":", 1)
                baselines[key] = {
                    "agent_id": agent_id,
                    "metric_name": metric_name,
                    "mean": self._baseline_means.get(key, 0.0),
                    "stddev": self._baseline_stddevs.get(key, 0.0),
                    "moving_average": self._moving_averages.get(key, 0.0),
                    "current_value": self._current_values.get(key, 0.0),
                }

            return {
                "count": len(baselines),
                "baselines": baselines,
                "context_tag": "drift_prometheus_exporter_v1",
            }

    def sync_from_detector(self):
        """
        Synchronize metrics from the associated DriftDetector instance.

        Updates internal metric storage with current detector state.
        """
        if not self._drift_detector:
            logger.warning("No DriftDetector instance set for sync")
            return

        with self._lock:
            for key, baseline in self._drift_detector.baselines.items():
                self._baseline_means[key] = baseline.mean
                self._baseline_stddevs[key] = baseline.std_dev
                self._moving_averages[key] = baseline.moving_average

            # Sync alerts - count alerts by (agent_id, level, method)
            alert_counts: Dict[tuple, int] = defaultdict(int)
            for alert in self._drift_detector.alerts:
                alert_key = (alert.agent_id, alert.level.value, alert.method.value)
                alert_counts[alert_key] += 1
            # Merge with existing counts (take max to avoid double-counting)
            for key, count in alert_counts.items():
                self._alert_counts[key] = max(self._alert_counts.get(key, 0), count)

        logger.debug("Synced metrics from DriftDetector")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the exporter.

        Returns:
            Health check result dictionary
        """
        with self._lock:
            has_detector = self._drift_detector is not None
            metrics_count = len(self._drift_deltas)
            alerts_count = sum(self._alert_counts.values())

        return {
            "healthy": True,
            "service_name": self.service_name,
            "has_detector": has_detector,
            "metrics_count": metrics_count,
            "alerts_count": alerts_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_tag": "drift_prometheus_exporter_v1",
            "anchors": ["EOS_SEED_ORION", "HALO_CONTINUITY_GRAFT_005"],
        }


# Global exporter instance
_global_drift_exporter: Optional[DriftPrometheusExporter] = None


def get_drift_exporter(
    drift_detector: Optional["DriftDetector"] = None,
    **kwargs
) -> DriftPrometheusExporter:
    """
    Get or create global drift Prometheus exporter instance.

    Args:
        drift_detector: Optional DriftDetector to associate with exporter
        **kwargs: Additional arguments passed to DriftPrometheusExporter

    Returns:
        DriftPrometheusExporter instance
    """
    global _global_drift_exporter
    if _global_drift_exporter is None:
        _global_drift_exporter = DriftPrometheusExporter(drift_detector, **kwargs)
    elif drift_detector is not None and _global_drift_exporter._drift_detector is None:
        _global_drift_exporter.set_drift_detector(drift_detector)
    return _global_drift_exporter


def reset_drift_exporter():
    """Reset global drift exporter instance (useful for testing)."""
    global _global_drift_exporter
    _global_drift_exporter = None
