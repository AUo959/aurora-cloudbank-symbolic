"""
Tests for Drift Detection System
"""

import pytest
from datetime import datetime, timedelta
from src.monitoring.drift_detector import (
    DriftDetector,
    DriftAlert,
    DriftLevel,
    DriftMethod,
    BaselineMetrics
)


class TestDriftDetector:
    """Test suite for DriftDetector"""
    
    def test_initialization(self):
        """Test drift detector initialization"""
        detector = DriftDetector(
            z_score_threshold=3.0,
            moving_avg_window=10
        )
        
        assert detector.z_score_threshold == 3.0
        assert detector.moving_avg_window == 10
        assert len(detector.baselines) == 0
        assert len(detector.alerts) == 0
    
    def test_establish_baseline(self):
        """Test baseline establishment"""
        detector = DriftDetector()
        
        values = [10.0, 12.0, 11.0, 13.0, 10.0, 12.0]
        baseline = detector.establish_baseline(
            agent_id="test-agent",
            metric_name="test_metric",
            values=values
        )
        
        assert baseline.agent_id == "test-agent"
        assert baseline.metric_name == "test_metric"
        assert baseline.mean == pytest.approx(11.33, rel=0.01)
        assert baseline.sample_count == 6
        assert baseline.min_value == 10.0
        assert baseline.max_value == 13.0
    
    def test_establish_baseline_empty_values(self):
        """Test baseline with empty values raises error"""
        detector = DriftDetector()
        
        with pytest.raises(ValueError, match="Cannot establish baseline with empty values"):
            detector.establish_baseline(
                agent_id="test-agent",
                metric_name="test_metric",
                values=[]
            )
    
    def test_detect_drift_no_baseline(self):
        """Test drift detection without baseline returns None"""
        detector = DriftDetector()
        
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=50.0
        )
        
        assert alert is None
    
    def test_detect_drift_within_threshold(self):
        """Test drift detection within threshold"""
        detector = DriftDetector(
            info_threshold=0.2,
            warning_threshold=0.5
        )
        
        values = [10.0, 12.0, 11.0, 13.0, 10.0, 12.0]
        detector.establish_baseline("test-agent", "test_metric", values)
        
        # Value within threshold (11.5 vs baseline ~11.33)
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=11.5
        )
        
        assert alert is None
    
    def test_detect_drift_info_level(self):
        """Test drift detection at info level"""
        detector = DriftDetector(
            info_threshold=0.2,
            warning_threshold=0.5
        )
        
        values = [10.0, 12.0, 11.0, 13.0, 10.0, 12.0]
        baseline = detector.establish_baseline("test-agent", "test_metric", values)
        
        # 25% deviation (info level)
        deviation_value = baseline.mean * 1.25
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=deviation_value
        )
        
        assert alert is not None
        assert alert.level == DriftLevel.INFO
        assert alert.agent_id == "test-agent"
        assert alert.metric_name == "test_metric"
    
    def test_detect_drift_warning_level(self):
        """Test drift detection at warning level"""
        detector = DriftDetector(
            info_threshold=0.2,
            warning_threshold=0.5,
            critical_threshold=0.8,
            z_score_threshold=10.0  # Higher threshold to avoid z-score override
        )
        
        values = [10.0, 12.0, 11.0, 13.0, 10.0, 12.0]
        baseline = detector.establish_baseline("test-agent", "test_metric", values)
        
        # 55% deviation (warning level, below critical)
        deviation_value = baseline.mean * 1.55
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=deviation_value
        )
        
        assert alert is not None
        assert alert.level == DriftLevel.WARNING
    
    def test_detect_drift_critical_level(self):
        """Test drift detection at critical level"""
        detector = DriftDetector(
            info_threshold=0.2,
            warning_threshold=0.5,
            critical_threshold=0.8
        )
        
        values = [10.0, 12.0, 11.0, 13.0, 10.0, 12.0]
        baseline = detector.establish_baseline("test-agent", "test_metric", values)
        
        # 100% deviation (critical level)
        deviation_value = baseline.mean * 2.0
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=deviation_value
        )
        
        assert alert is not None
        assert alert.level == DriftLevel.CRITICAL
    
    def test_detect_drift_z_score(self):
        """Test z-score based drift detection"""
        detector = DriftDetector(z_score_threshold=3.0)
        
        # Baseline with low variance
        values = [10.0, 10.1, 9.9, 10.2, 9.8, 10.0]
        baseline = detector.establish_baseline("test-agent", "test_metric", values)
        
        # Value far outside normal range (z-score > 3)
        extreme_value = baseline.mean + 4 * baseline.std_dev
        alert = detector.detect_drift(
            agent_id="test-agent",
            metric_name="test_metric",
            current_value=extreme_value
        )
        
        assert alert is not None
        assert alert.level == DriftLevel.CRITICAL
        assert alert.method == DriftMethod.Z_SCORE
    
    def test_get_alerts_no_filters(self):
        """Test getting all alerts"""
        detector = DriftDetector()
        
        values = [10.0, 12.0, 11.0]
        detector.establish_baseline("agent-1", "metric-1", values)
        
        # Generate some alerts
        detector.detect_drift("agent-1", "metric-1", 20.0)
        detector.detect_drift("agent-1", "metric-1", 25.0)
        
        alerts = detector.get_alerts()
        assert len(alerts) == 2
    
    def test_get_alerts_filtered_by_agent(self):
        """Test filtering alerts by agent"""
        detector = DriftDetector()
        
        detector.establish_baseline("agent-1", "metric-1", [10.0, 11.0, 12.0])
        detector.establish_baseline("agent-2", "metric-1", [10.0, 11.0, 12.0])
        
        detector.detect_drift("agent-1", "metric-1", 20.0)
        detector.detect_drift("agent-2", "metric-1", 20.0)
        
        alerts = detector.get_alerts(agent_id="agent-1")
        assert len(alerts) == 1
        assert alerts[0].agent_id == "agent-1"
    
    def test_get_alerts_filtered_by_level(self):
        """Test filtering alerts by level"""
        detector = DriftDetector()
        
        values = [10.0, 11.0, 12.0]
        detector.establish_baseline("agent-1", "metric-1", values)
        
        # Generate critical alert
        detector.detect_drift("agent-1", "metric-1", 30.0)
        
        critical_alerts = detector.get_alerts(level=DriftLevel.CRITICAL)
        assert len(critical_alerts) >= 1
    
    def test_clear_alerts(self):
        """Test clearing alerts"""
        detector = DriftDetector()
        
        values = [10.0, 11.0, 12.0]
        detector.establish_baseline("agent-1", "metric-1", values)
        
        detector.detect_drift("agent-1", "metric-1", 20.0)
        assert len(detector.alerts) > 0
        
        detector.clear_alerts()
        assert len(detector.alerts) == 0
    
    def test_export_import_baselines(self):
        """Test baseline export and import"""
        detector1 = DriftDetector()
        
        values = [10.0, 11.0, 12.0]
        detector1.establish_baseline("agent-1", "metric-1", values)
        
        # Export
        exported = detector1.export_baselines()
        assert "agent-1:metric-1" in exported
        
        # Import to new detector
        detector2 = DriftDetector()
        detector2.import_baselines(exported)
        
        assert "agent-1:metric-1" in detector2.baselines
        assert detector2.baselines["agent-1:metric-1"].mean == pytest.approx(11.0)
    
    def test_moving_average_tracking(self):
        """Test moving average updates"""
        detector = DriftDetector(moving_avg_window=3)
        
        values = [10.0, 11.0, 12.0]
        baseline = detector.establish_baseline("agent-1", "metric-1", values)
        
        # Add new values
        detector.detect_drift("agent-1", "metric-1", 13.0)
        detector.detect_drift("agent-1", "metric-1", 14.0)
        
        # Check moving window updated
        assert len(baseline.moving_window) == 3
        assert 14.0 in baseline.moving_window
    
    def test_alert_context_tag(self):
        """Test context tag in alerts"""
        detector = DriftDetector()
        
        values = [10.0, 11.0, 12.0]
        detector.establish_baseline("agent-1", "metric-1", values)
        
        alert = detector.detect_drift(
            agent_id="agent-1",
            metric_name="metric-1",
            current_value=30.0,
            context_tag="test_context_001"
        )
        
        assert alert is not None
        assert alert.context_tag == "test_context_001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
