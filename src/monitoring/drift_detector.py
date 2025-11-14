"""
Drift Detection System

Implements statistical and ML-based drift detection for agent behavior monitoring.
Detects deviations from baseline patterns using multiple algorithms.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
import statistics

logger = logging.getLogger(__name__)


class DriftLevel(Enum):
    """Severity level of detected drift"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DriftMethod(Enum):
    """Method used to detect drift"""
    Z_SCORE = "z_score"
    MOVING_AVERAGE = "moving_average"
    THRESHOLD = "threshold"
    PATTERN_CHANGE = "pattern_change"


@dataclass
class DriftAlert:
    """Alert generated when drift is detected"""
    timestamp: str
    agent_id: str
    metric_name: str
    level: DriftLevel
    method: DriftMethod
    current_value: float
    baseline_value: float
    deviation: float
    description: str
    context_tag: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['level'] = self.level.value
        data['method'] = self.method.value
        return data


@dataclass
class BaselineMetrics:
    """Baseline behavior metrics for an agent"""
    agent_id: str
    metric_name: str
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    sample_count: int
    last_updated: str
    moving_average: float = 0.0
    moving_window: List[float] = field(default_factory=list)


class DriftDetector:
    """
    Drift Detection System for Agent Behavior
    
    Monitors agent behavior metrics and detects deviations from baseline patterns
    using multiple statistical methods.
    
    Features:
    - Z-score based drift detection
    - Moving average trend analysis
    - Threshold-based alerting
    - Configurable sensitivity levels
    - Multi-level alert generation
    """
    
    def __init__(
        self,
        z_score_threshold: float = 3.0,
        moving_avg_window: int = 10,
        info_threshold: float = 0.2,
        warning_threshold: float = 0.5,
        critical_threshold: float = 0.8
    ):
        """
        Initialize drift detector
        
        Args:
            z_score_threshold: Standard deviations for z-score alerts (default: 3.0)
            moving_avg_window: Window size for moving average (default: 10)
            info_threshold: Relative change threshold for info alerts (default: 0.2 = 20%)
            warning_threshold: Relative change threshold for warning alerts (default: 0.5 = 50%)
            critical_threshold: Relative change threshold for critical alerts (default: 0.8 = 80%)
        """
        self.z_score_threshold = z_score_threshold
        self.moving_avg_window = moving_avg_window
        self.info_threshold = info_threshold
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        # Storage for baselines and alerts
        self.baselines: Dict[str, BaselineMetrics] = {}
        self.alerts: List[DriftAlert] = []
        
        logger.info("Drift detector initialized with z_threshold=%.1f", z_score_threshold)
    
    def establish_baseline(
        self,
        agent_id: str,
        metric_name: str,
        values: List[float]
    ) -> BaselineMetrics:
        """
        Establish baseline metrics from historical data
        
        Args:
            agent_id: Identifier for the agent
            metric_name: Name of the metric
            values: Historical values to establish baseline
        
        Returns:
            BaselineMetrics object
        """
        if not values:
            raise ValueError("Cannot establish baseline with empty values")
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
        
        baseline = BaselineMetrics(
            agent_id=agent_id,
            metric_name=metric_name,
            mean=mean,
            std_dev=std_dev,
            min_value=min(values),
            max_value=max(values),
            sample_count=len(values),
            last_updated=datetime.now(timezone.utc).isoformat(),
            moving_average=mean,
            moving_window=list(values[-self.moving_avg_window:])
        )
        
        key = f"{agent_id}:{metric_name}"
        self.baselines[key] = baseline
        
        logger.info(
            "Baseline established for %s:%s - mean=%.2f, std=%.2f",
            agent_id, metric_name, mean, std_dev
        )
        
        return baseline
    
    def detect_drift(
        self,
        agent_id: str,
        metric_name: str,
        current_value: float,
        context_tag: Optional[str] = None
    ) -> Optional[DriftAlert]:
        """
        Detect drift in agent behavior metric
        
        Args:
            agent_id: Identifier for the agent
            metric_name: Name of the metric
            current_value: Current metric value
            context_tag: DLP context tag for tracking
        
        Returns:
            DriftAlert if drift detected, None otherwise
        """
        key = f"{agent_id}:{metric_name}"
        
        if key not in self.baselines:
            logger.warning("No baseline for %s:%s - cannot detect drift", agent_id, metric_name)
            return None
        
        baseline = self.baselines[key]
        
        # Update moving average
        baseline.moving_window.append(current_value)
        if len(baseline.moving_window) > self.moving_avg_window:
            baseline.moving_window.pop(0)
        baseline.moving_average = statistics.mean(baseline.moving_window)
        
        # Check for drift using multiple methods
        alert = None
        
        # Method 1: Z-score detection
        if baseline.std_dev > 0:
            z_score = abs((current_value - baseline.mean) / baseline.std_dev)
            if z_score > self.z_score_threshold:
                alert = self._create_alert(
                    agent_id, metric_name, current_value, baseline,
                    DriftLevel.CRITICAL, DriftMethod.Z_SCORE,
                    f"Z-score of {z_score:.2f} exceeds threshold of {self.z_score_threshold}",
                    context_tag
                )
        
        # Method 2: Relative change from baseline
        if alert is None and baseline.mean != 0:
            relative_change = abs((current_value - baseline.mean) / baseline.mean)
            
            if relative_change > self.critical_threshold:
                level = DriftLevel.CRITICAL
            elif relative_change > self.warning_threshold:
                level = DriftLevel.WARNING
            elif relative_change > self.info_threshold:
                level = DriftLevel.INFO
            else:
                level = None
            
            if level:
                alert = self._create_alert(
                    agent_id, metric_name, current_value, baseline,
                    level, DriftMethod.THRESHOLD,
                    f"Relative change of {relative_change*100:.1f}% from baseline",
                    context_tag
                )
        
        # Method 3: Moving average deviation
        if alert is None and len(baseline.moving_window) >= 3:
            ma_deviation = abs(current_value - baseline.moving_average) / baseline.moving_average if baseline.moving_average != 0 else 0
            
            if ma_deviation > self.warning_threshold:
                alert = self._create_alert(
                    agent_id, metric_name, current_value, baseline,
                    DriftLevel.WARNING, DriftMethod.MOVING_AVERAGE,
                    f"Deviation from moving average: {ma_deviation*100:.1f}%",
                    context_tag
                )
        
        if alert:
            self.alerts.append(alert)
            logger.warning(
                "Drift detected: %s:%s [%s] - current=%.2f, baseline=%.2f",
                agent_id, metric_name, alert.level.value, current_value, baseline.mean
            )
        
        return alert
    
    def _create_alert(
        self,
        agent_id: str,
        metric_name: str,
        current_value: float,
        baseline: BaselineMetrics,
        level: DriftLevel,
        method: DriftMethod,
        description: str,
        context_tag: Optional[str]
    ) -> DriftAlert:
        """Create a drift alert"""
        # Use epsilon for near-zero baselines to avoid inflated deviations
        epsilon = 1e-10
        if abs(baseline.mean) < epsilon:
            deviation = abs(current_value - baseline.mean)
        else:
            deviation = abs(current_value - baseline.mean) / baseline.mean
        
        return DriftAlert(
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=agent_id,
            metric_name=metric_name,
            level=level,
            method=method,
            current_value=current_value,
            baseline_value=baseline.mean,
            deviation=deviation,
            description=description,
            context_tag=context_tag,
            metadata={
                'std_dev': baseline.std_dev,
                'moving_average': baseline.moving_average,
                'sample_count': baseline.sample_count
            }
        )
    
    def get_alerts(
        self,
        agent_id: Optional[str] = None,
        level: Optional[DriftLevel] = None,
        since: Optional[datetime] = None
    ) -> List[DriftAlert]:
        """
        Get filtered list of drift alerts
        
        Args:
            agent_id: Filter by agent ID
            level: Filter by alert level
            since: Filter alerts after this time
        
        Returns:
            List of matching alerts
        """
        alerts = self.alerts
        
        if agent_id:
            alerts = [a for a in alerts if a.agent_id == agent_id]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        if since:
            alerts = [
                a for a in alerts
                if datetime.fromisoformat(a.timestamp) >= since
            ]
        
        return alerts
    
    def clear_alerts(self, before: Optional[datetime] = None):
        """
        Clear old alerts
        
        Args:
            before: Clear alerts before this time (default: all alerts)
        """
        if before:
            self.alerts = [
                a for a in self.alerts
                if datetime.fromisoformat(a.timestamp) >= before
            ]
        else:
            self.alerts.clear()
        
        logger.info("Cleared drift alerts (before=%s)", before)
    
    def export_baselines(self) -> Dict[str, Any]:
        """Export all baselines for persistence"""
        return {
            key: {
                'agent_id': b.agent_id,
                'metric_name': b.metric_name,
                'mean': b.mean,
                'std_dev': b.std_dev,
                'min_value': b.min_value,
                'max_value': b.max_value,
                'sample_count': b.sample_count,
                'last_updated': b.last_updated,
                'moving_average': b.moving_average,
                'moving_window': b.moving_window
            }
            for key, b in self.baselines.items()
        }
    
    def import_baselines(self, data: Dict[str, Any]):
        """Import baselines from persisted data"""
        for key, b_data in data.items():
            self.baselines[key] = BaselineMetrics(**b_data)
        
        logger.info("Imported %d baselines", len(data))
