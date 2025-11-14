"""
Pattern Analyzer Module - Thread Transfer Bridge v2
==================================================

Historical pattern analysis for drift prediction improvement.

Features:
- Time-series pattern detection
- Seasonal trend analysis
- Anomaly detection
- Pattern classification

Thread: T1→BRIDGE_V2→PATTERN_ANALYZER
DLP: context_tag=bridge_v2_pattern_analysis
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Detected pattern types."""
    STABLE = "stable"              # Low variance, predictable
    TRENDING = "trending"          # Gradual increase/decrease
    CYCLICAL = "cyclical"          # Repeating patterns
    VOLATILE = "volatile"          # High variance, unpredictable
    ANOMALOUS = "anomalous"        # Unusual behavior


@dataclass
class DriftPattern:
    """Detected drift pattern."""
    pattern_type: PatternType
    confidence: float
    period_hours: Optional[int]     # For cyclical patterns
    trend_direction: Optional[str]  # "increasing" or "decreasing"
    volatility: float               # Measure of variance
    detected_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "pattern_type": self.pattern_type.value,
            "confidence": self.confidence,
            "period_hours": self.period_hours,
            "trend_direction": self.trend_direction,
            "volatility": self.volatility,
            "detected_at": self.detected_at.isoformat(),
            "metadata": self.metadata
        }


class PatternAnalyzer:
    """
    Pattern analyzer for historical drift data.
    
    Analyzes time-series drift patterns to improve predictions.
    """
    
    def __init__(self, min_observations: int = 24):
        """
        Initialize pattern analyzer.

        Args:
            min_observations: Minimum observations needed for analysis
        """
        self.min_observations = min_observations
        self.observations: List[Tuple[datetime, float]] = []

    def add_observation(self, timestamp: datetime, drift: float):
        """Add drift observation."""
        self.observations.append((timestamp, drift))
        
        # Keep last 1000 observations
        if len(self.observations) > 1000:
            self.observations = self.observations[-1000:]

    async def analyze_patterns(self) -> List[DriftPattern]:
        """
        Analyze drift patterns.

        Returns:
            List of detected patterns
        """
        if len(self.observations) < self.min_observations:
            logger.warning(
                f"Insufficient observations for pattern analysis: "
                f"{len(self.observations)} < {self.min_observations}"
            )
            return []
        
        patterns = []
        
        # Analyze stability
        stability_pattern = await self._analyze_stability()
        if stability_pattern:
            patterns.append(stability_pattern)
        
        # Analyze trends
        trend_pattern = await self._analyze_trends()
        if trend_pattern:
            patterns.append(trend_pattern)
        
        # Analyze cycles
        cycle_pattern = await self._analyze_cycles()
        if cycle_pattern:
            patterns.append(cycle_pattern)
        
        # Detect anomalies
        anomaly_pattern = await self._detect_anomalies()
        if anomaly_pattern:
            patterns.append(anomaly_pattern)
        
        return patterns

    async def _analyze_stability(self) -> Optional[DriftPattern]:
        """Analyze drift stability."""
        drifts = [obs[1] for obs in self.observations]
        
        # Calculate statistics
        mean_drift = sum(drifts) / len(drifts)
        variance = sum((d - mean_drift) ** 2 for d in drifts) / len(drifts)
        std_dev = variance ** 0.5
        
        # Coefficient of variation
        cv = std_dev / mean_drift if mean_drift > 0 else 0
        
        if cv < 0.3:  # Low variance = stable
            return DriftPattern(
                pattern_type=PatternType.STABLE,
                confidence=0.9,
                period_hours=None,
                trend_direction=None,
                volatility=cv,
                detected_at=datetime.now(),
                metadata={
                    "mean_drift": mean_drift,
                    "std_dev": std_dev,
                    "cv": cv
                }
            )
        
        return None

    async def _analyze_trends(self) -> Optional[DriftPattern]:
        """Analyze drift trends."""
        if len(self.observations) < 10:
            return None
        
        # Simple linear regression
        n = len(self.observations)
        x = list(range(n))
        y = [obs[1] for obs in self.observations]
        
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return None
        
        slope = numerator / denominator
        
        # Significant trend if slope is notable
        if abs(slope) > 0.001:
            direction = "increasing" if slope > 0 else "decreasing"
            
            # Calculate R² for confidence
            y_pred = [slope * xi + (y_mean - slope * x_mean) for xi in x]
            ss_tot = sum((yi - y_mean) ** 2 for yi in y)
            ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            return DriftPattern(
                pattern_type=PatternType.TRENDING,
                confidence=min(0.95, r_squared),
                period_hours=None,
                trend_direction=direction,
                volatility=abs(slope),
                detected_at=datetime.now(),
                metadata={
                    "slope": slope,
                    "r_squared": r_squared
                }
            )
        
        return None

    async def _analyze_cycles(self) -> Optional[DriftPattern]:
        """Analyze cyclical patterns."""
        if len(self.observations) < 48:  # Need at least 2 days
            return None
        
        drifts = [obs[1] for obs in self.observations]
        
        # Check for daily cycles (24-hour period)
        daily_autocorr = self._autocorrelation(drifts, 24)
        
        if daily_autocorr > 0.7:  # Strong daily pattern
            return DriftPattern(
                pattern_type=PatternType.CYCLICAL,
                confidence=daily_autocorr,
                period_hours=24,
                trend_direction=None,
                volatility=0.0,
                detected_at=datetime.now(),
                metadata={
                    "autocorrelation": daily_autocorr,
                    "period_hours": 24
                }
            )
        
        return None

    async def _detect_anomalies(self) -> Optional[DriftPattern]:
        """Detect anomalous patterns."""
        if len(self.observations) < self.min_observations:
            return None
        
        drifts = [obs[1] for obs in self.observations]
        
        # Calculate statistics
        mean_drift = sum(drifts) / len(drifts)
        variance = sum((d - mean_drift) ** 2 for d in drifts) / len(drifts)
        std_dev = variance ** 0.5
        
        # Count anomalies (> 3 standard deviations)
        anomalies = sum(1 for d in drifts if abs(d - mean_drift) > 3 * std_dev)
        anomaly_ratio = anomalies / len(drifts)
        
        if anomaly_ratio > 0.05:  # More than 5% anomalies
            return DriftPattern(
                pattern_type=PatternType.ANOMALOUS,
                confidence=min(0.95, anomaly_ratio * 10),
                period_hours=None,
                trend_direction=None,
                volatility=anomaly_ratio,
                detected_at=datetime.now(),
                metadata={
                    "anomaly_count": anomalies,
                    "anomaly_ratio": anomaly_ratio,
                    "threshold_std_devs": 3
                }
            )
        
        return None

    def _autocorrelation(self, series: List[float], lag: int) -> float:
        """
        Calculate autocorrelation at given lag.

        Args:
            series: Time series data
            lag: Lag period

        Returns:
            Autocorrelation coefficient (-1 to 1)
        """
        if lag >= len(series):
            return 0.0
        
        n = len(series) - lag
        mean = sum(series) / len(series)
        
        numerator = sum(
            (series[i] - mean) * (series[i + lag] - mean)
            for i in range(n)
        )
        
        denominator = sum((s - mean) ** 2 for s in series)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

    def get_statistics(self) -> Dict[str, Any]:
        """Get drift statistics."""
        if not self.observations:
            return {
                "count": 0,
                "error": "No observations"
            }
        
        drifts = [obs[1] for obs in self.observations]
        
        mean_drift = sum(drifts) / len(drifts)
        min_drift = min(drifts)
        max_drift = max(drifts)
        variance = sum((d - mean_drift) ** 2 for d in drifts) / len(drifts)
        std_dev = variance ** 0.5
        
        return {
            "count": len(self.observations),
            "mean": mean_drift,
            "min": min_drift,
            "max": max_drift,
            "std_dev": std_dev,
            "variance": variance,
            "time_span_hours": (
                (self.observations[-1][0] - self.observations[0][0]).total_seconds() / 3600
                if len(self.observations) > 1 else 0
            )
        }


# Global analyzer instance
_analyzer = None


def get_pattern_analyzer() -> PatternAnalyzer:
    """Get global pattern analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = PatternAnalyzer()
    return _analyzer
