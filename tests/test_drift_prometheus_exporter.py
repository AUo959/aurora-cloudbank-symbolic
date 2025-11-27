"""
Tests for Drift Prometheus Exporter

Tests for the DriftPrometheusExporter class and drift metrics API endpoints.

DLP: test_drift_prometheus_exporter_v1
"""

import pytest

from src.monitoring.drift_detector import (
    DriftDetector,
    DriftAlert,
    DriftLevel,
    DriftMethod
)
from src.observability.drift_prometheus_exporter import (
    DriftPrometheusExporter,
    get_drift_exporter,
    reset_drift_exporter
)


@pytest.fixture(autouse=True)
def reset_exporter_fixture():
    """Reset exporter before each test"""
    reset_drift_exporter()
    yield
    reset_drift_exporter()


@pytest.fixture
def drift_detector():
    """Create a configured drift detector"""
    return DriftDetector(
        z_score_threshold=3.0,
        moving_avg_window=10,
        info_threshold=0.2,
        warning_threshold=0.5,
        critical_threshold=0.8
    )


@pytest.fixture
def exporter(drift_detector):
    """Create an exporter with a detector"""
    return DriftPrometheusExporter(drift_detector=drift_detector)


class TestDriftPrometheusExporterInit:
    """Test DriftPrometheusExporter initialization"""

    @pytest.mark.unit
    def test_initialization_without_detector(self):
        """Test exporter initialization without detector"""
        exporter = DriftPrometheusExporter()
        assert exporter.service_name == "aurora-drift-exporter"
        assert exporter._drift_detector is None
        assert exporter._config_info == {}

    @pytest.mark.unit
    def test_initialization_with_detector(self, drift_detector):
        """Test exporter initialization with detector"""
        exporter = DriftPrometheusExporter(drift_detector=drift_detector)
        assert exporter._drift_detector is drift_detector
        assert exporter._config_info["z_score_threshold"] == 3.0
        assert exporter._config_info["moving_avg_window"] == 10

    @pytest.mark.unit
    def test_initialization_with_custom_service_name(self):
        """Test exporter with custom service name"""
        exporter = DriftPrometheusExporter(service_name="custom-service")
        assert exporter.service_name == "custom-service"

    @pytest.mark.unit
    def test_set_drift_detector(self):
        """Test setting detector after initialization"""
        exporter = DriftPrometheusExporter()
        detector = DriftDetector()
        exporter.set_drift_detector(detector)
        assert exporter._drift_detector is detector
        assert "z_score_threshold" in exporter._config_info


class TestDriftMeasurementRecording:
    """Test drift measurement recording"""

    @pytest.mark.unit
    def test_record_drift_measurement(self, exporter):
        """Test recording a drift measurement"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="response_time",
            current_value=150.0,
            baseline_mean=100.0,
            baseline_stddev=10.0,
            deviation=0.5,
            moving_average=120.0
        )

        key = "agent-1:response_time"
        assert exporter._drift_deltas[key] == 0.5
        assert exporter._baseline_means[key] == 100.0
        assert exporter._baseline_stddevs[key] == 10.0
        assert exporter._moving_averages[key] == 120.0
        assert exporter._current_values[key] == 150.0

    @pytest.mark.unit
    def test_record_multiple_measurements(self, exporter):
        """Test recording multiple measurements"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="metric_a",
            current_value=100.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.1
        )
        exporter.record_drift_measurement(
            agent_id="agent-2",
            metric_name="metric_b",
            current_value=200.0,
            baseline_mean=180.0,
            baseline_stddev=10.0,
            deviation=0.2
        )

        assert len(exporter._drift_deltas) == 2
        assert "agent-1:metric_a" in exporter._drift_deltas
        assert "agent-2:metric_b" in exporter._drift_deltas

    @pytest.mark.unit
    def test_measurement_updates_existing(self, exporter):
        """Test that measurements update existing values"""
        key = "agent-1:metric"

        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="metric",
            current_value=100.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.1
        )

        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="metric",
            current_value=110.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.22
        )

        assert exporter._drift_deltas[key] == 0.22
        assert exporter._current_values[key] == 110.0


class TestAlertRecording:
    """Test alert recording"""

    @pytest.mark.unit
    def test_record_alert(self, exporter):
        """Test recording a drift alert"""
        alert = DriftAlert(
            timestamp="2024-01-01T00:00:00Z",
            agent_id="agent-1",
            metric_name="response_time",
            level=DriftLevel.WARNING,
            method=DriftMethod.Z_SCORE,
            current_value=150.0,
            baseline_value=100.0,
            deviation=0.5,
            description="Test alert"
        )

        exporter.record_alert(alert)

        key = ("agent-1", "warning", "z_score")
        assert exporter._alert_counts[key] == 1

    @pytest.mark.unit
    def test_record_multiple_alerts(self, exporter):
        """Test recording multiple alerts"""
        for i in range(5):
            alert = DriftAlert(
                timestamp=f"2024-01-0{i+1}T00:00:00Z",
                agent_id="agent-1",
                metric_name="response_time",
                level=DriftLevel.CRITICAL,
                method=DriftMethod.THRESHOLD,
                current_value=200.0 + i,
                baseline_value=100.0,
                deviation=1.0 + i * 0.1,
                description=f"Alert {i}"
            )
            exporter.record_alert(alert)

        key = ("agent-1", "critical", "threshold")
        assert exporter._alert_counts[key] == 5


class TestPrometheusExport:
    """Test Prometheus metrics export"""

    @pytest.mark.unit
    def test_export_empty_metrics(self, exporter):
        """Test exporting with no metrics"""
        output = exporter.export_metrics()

        assert "aurora_drift_delta" in output
        assert "aurora_drift_baseline_mean" in output
        assert "aurora_drift_baseline_stddev" in output
        assert "aurora_drift_moving_average" in output
        assert "aurora_drift_alerts_total" in output
        assert "aurora_drift_detector_info" in output

    @pytest.mark.unit
    def test_export_with_metrics(self, exporter):
        """Test exporting with recorded metrics"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="response_time",
            current_value=150.0,
            baseline_mean=100.0,
            baseline_stddev=10.0,
            deviation=0.5,
            moving_average=120.0
        )

        output = exporter.export_metrics()

        assert 'agent_id="agent-1"' in output
        assert 'metric_name="response_time"' in output
        assert "0.5" in output  # deviation

    @pytest.mark.unit
    def test_export_with_alerts(self, exporter):
        """Test exporting with recorded alerts"""
        alert = DriftAlert(
            timestamp="2024-01-01T00:00:00Z",
            agent_id="agent-1",
            metric_name="response_time",
            level=DriftLevel.WARNING,
            method=DriftMethod.Z_SCORE,
            current_value=150.0,
            baseline_value=100.0,
            deviation=0.5,
            description="Test alert"
        )
        exporter.record_alert(alert)

        output = exporter.export_metrics()

        assert 'level="warning"' in output
        assert 'method="z_score"' in output

    @pytest.mark.unit
    def test_export_format_is_valid(self, exporter):
        """Test that export format is valid Prometheus text format"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="test",
            current_value=100.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.1
        )

        output = exporter.export_metrics()

        # Verify basic format requirements
        lines = output.strip().split("\n")
        for line in lines:
            if line and not line.startswith("#"):
                # Should be metric_name{labels} value format
                assert "{" in line or line.split()[-1].replace(".", "").isdigit()


class TestMetricsSummary:
    """Test metrics summary generation"""

    @pytest.mark.unit
    def test_get_metrics_summary_empty(self, exporter):
        """Test summary with no metrics"""
        summary = exporter.get_metrics_summary()

        assert summary["service_name"] == "aurora-drift-exporter"
        assert summary["total_monitored_metrics"] == 0
        assert summary["total_alerts"] == 0
        assert "context_tag" in summary
        assert "anchors" in summary

    @pytest.mark.unit
    def test_get_metrics_summary_with_data(self, exporter):
        """Test summary with recorded data"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="metric_a",
            current_value=100.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.1
        )

        alert = DriftAlert(
            timestamp="2024-01-01T00:00:00Z",
            agent_id="agent-1",
            metric_name="metric_a",
            level=DriftLevel.INFO,
            method=DriftMethod.THRESHOLD,
            current_value=100.0,
            baseline_value=90.0,
            deviation=0.1,
            description="Info alert"
        )
        exporter.record_alert(alert)

        summary = exporter.get_metrics_summary()

        assert summary["total_monitored_metrics"] == 1
        assert summary["total_alerts"] == 1
        assert "info" in summary["alerts_by_level"]


class TestRecentMeasurements:
    """Test recent measurements retrieval"""

    @pytest.mark.unit
    def test_get_recent_measurements_empty(self, exporter):
        """Test getting measurements when empty"""
        measurements = exporter.get_recent_measurements()
        assert measurements == []

    @pytest.mark.unit
    def test_get_recent_measurements(self, exporter):
        """Test getting recent measurements"""
        for i in range(5):
            exporter.record_drift_measurement(
                agent_id="agent-1",
                metric_name=f"metric_{i}",
                current_value=100.0 + i,
                baseline_mean=90.0,
                baseline_stddev=5.0,
                deviation=0.1 * i
            )

        measurements = exporter.get_recent_measurements(limit=3)

        assert len(measurements) == 3
        # Most recent first
        assert measurements[0]["metric_name"] == "metric_4"

    @pytest.mark.unit
    def test_get_recent_measurements_filtered_by_agent(self, exporter):
        """Test filtering measurements by agent"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="metric",
            current_value=100.0,
            baseline_mean=90.0,
            baseline_stddev=5.0,
            deviation=0.1
        )
        exporter.record_drift_measurement(
            agent_id="agent-2",
            metric_name="metric",
            current_value=200.0,
            baseline_mean=180.0,
            baseline_stddev=10.0,
            deviation=0.2
        )

        agent1_measurements = exporter.get_recent_measurements(agent_id="agent-1")

        assert len(agent1_measurements) == 1
        assert agent1_measurements[0]["agent_id"] == "agent-1"


class TestBaselines:
    """Test baseline retrieval"""

    @pytest.mark.unit
    def test_get_baselines_empty(self, exporter):
        """Test getting baselines when empty"""
        baselines = exporter.get_baselines()
        assert baselines["count"] == 0
        assert baselines["baselines"] == {}

    @pytest.mark.unit
    def test_get_baselines_with_data(self, exporter):
        """Test getting baselines with recorded data"""
        exporter.record_drift_measurement(
            agent_id="agent-1",
            metric_name="response_time",
            current_value=150.0,
            baseline_mean=100.0,
            baseline_stddev=10.0,
            deviation=0.5,
            moving_average=120.0
        )

        baselines = exporter.get_baselines()

        assert baselines["count"] == 1
        assert "agent-1:response_time" in baselines["baselines"]
        baseline = baselines["baselines"]["agent-1:response_time"]
        assert baseline["mean"] == 100.0
        assert baseline["stddev"] == 10.0


class TestSyncFromDetector:
    """Test syncing from DriftDetector"""

    @pytest.mark.unit
    def test_sync_without_detector(self):
        """Test sync when no detector set"""
        exporter = DriftPrometheusExporter()
        # Should not raise
        exporter.sync_from_detector()

    @pytest.mark.unit
    def test_sync_with_detector(self, drift_detector):
        """Test sync from detector with baselines"""
        drift_detector.establish_baseline(
            agent_id="agent-1",
            metric_name="metric",
            values=[10.0, 11.0, 12.0, 13.0, 14.0]
        )

        exporter = DriftPrometheusExporter(drift_detector=drift_detector)
        exporter.sync_from_detector()

        assert "agent-1:metric" in exporter._baseline_means


class TestHealthCheck:
    """Test health check functionality"""

    @pytest.mark.unit
    def test_health_check_without_detector(self):
        """Test health check without detector"""
        exporter = DriftPrometheusExporter()
        health = exporter.health_check()

        assert health["healthy"] is True
        assert health["has_detector"] is False
        assert "timestamp" in health
        assert "context_tag" in health

    @pytest.mark.unit
    def test_health_check_with_detector(self, exporter):
        """Test health check with detector"""
        health = exporter.health_check()

        assert health["healthy"] is True
        assert health["has_detector"] is True


class TestGlobalExporter:
    """Test global exporter instance management"""

    @pytest.mark.unit
    def test_get_drift_exporter_creates_instance(self):
        """Test that get_drift_exporter creates an instance"""
        exporter = get_drift_exporter()
        assert isinstance(exporter, DriftPrometheusExporter)

    @pytest.mark.unit
    def test_get_drift_exporter_returns_same_instance(self):
        """Test that get_drift_exporter returns same instance"""
        exporter1 = get_drift_exporter()
        exporter2 = get_drift_exporter()
        assert exporter1 is exporter2

    @pytest.mark.unit
    def test_get_drift_exporter_with_detector(self, drift_detector):
        """Test get_drift_exporter with detector parameter"""
        exporter = get_drift_exporter(drift_detector=drift_detector)
        assert exporter._drift_detector is drift_detector

    @pytest.mark.unit
    def test_reset_drift_exporter(self):
        """Test resetting global exporter"""
        exporter1 = get_drift_exporter()
        reset_drift_exporter()
        exporter2 = get_drift_exporter()
        assert exporter1 is not exporter2


class TestIntegrationWithDriftDetector:
    """Integration tests with DriftDetector"""

    @pytest.mark.integration
    def test_full_workflow(self, drift_detector):
        """Test full workflow of detection and export"""
        exporter = DriftPrometheusExporter(drift_detector=drift_detector)

        # Establish baseline
        baseline = drift_detector.establish_baseline(
            agent_id="agent-1",
            metric_name="latency",
            values=[100.0, 102.0, 98.0, 101.0, 99.0, 100.0]
        )

        # Record baseline in exporter
        exporter.record_drift_measurement(
            agent_id=baseline.agent_id,
            metric_name=baseline.metric_name,
            current_value=baseline.mean,
            baseline_mean=baseline.mean,
            baseline_stddev=baseline.std_dev,
            deviation=0.0,
            moving_average=baseline.moving_average
        )

        # Detect drift
        alert = drift_detector.detect_drift(
            agent_id="agent-1",
            metric_name="latency",
            current_value=200.0  # Big deviation
        )

        if alert:
            exporter.record_alert(alert)
            exporter.record_drift_measurement(
                agent_id=alert.agent_id,
                metric_name=alert.metric_name,
                current_value=alert.current_value,
                baseline_mean=alert.baseline_value,
                baseline_stddev=baseline.std_dev,
                deviation=alert.deviation,
                moving_average=drift_detector.baselines["agent-1:latency"].moving_average
            )

        # Export and verify
        output = exporter.export_metrics()
        summary = exporter.get_metrics_summary()

        assert 'agent_id="agent-1"' in output
        assert summary["total_monitored_metrics"] >= 1
        assert summary["total_alerts"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
