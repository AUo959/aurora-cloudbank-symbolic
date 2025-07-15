"""
Drift Detection System for Aurora Symbolic Anchors
Monitors and detects entropy drift patterns in T1 and SRB anchors
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from enum import Enum


class DriftType(Enum):
    """Types of entropy drift patterns"""
    GRADUAL = "gradual"
    SUDDEN = "sudden"
    OSCILLATING = "oscillating"
    CHAOTIC = "chaotic"
    STABLE = "stable"


class DriftSeverity(Enum):
    """Severity levels for detected drift"""
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SIGNIFICANT = "significant"
    CRITICAL = "critical"


class DriftDetector:
    """Advanced drift detection for symbolic anchor entropy"""
    
    def __init__(self):
        self.drift_history: List[Dict[str, Any]] = []
        self.detection_sensitivity = 0.1
        self.min_samples_for_detection = 5
        
        # Drift pattern recognition thresholds
        self.thresholds = {
            'gradual_slope': 0.05,      # Slope threshold for gradual drift
            'sudden_change': 0.3,       # Single-step change threshold
            'oscillation_amplitude': 0.2,  # Oscillation amplitude threshold
            'chaos_variance': 0.5,      # Variance threshold for chaotic behavior
            'stability_window': 0.02    # Stability window for stable classification
        }
        
        # Drift severity mapping
        self.severity_thresholds = {
            DriftSeverity.MINIMAL: 0.1,
            DriftSeverity.MODERATE: 0.3,
            DriftSeverity.SIGNIFICANT: 0.6,
            DriftSeverity.CRITICAL: 1.0
        }
    
    def detect_drift(self, entropy_values: List[float], timestamps: Optional[List[float]] = None) -> Dict[str, Any]:
        """Detect drift patterns in entropy values"""
        if len(entropy_values) < self.min_samples_for_detection:
            return {
                'drift_detected': False,
                'reason': 'insufficient_samples',
                'sample_count': len(entropy_values)
            }
        
        # Generate timestamps if not provided
        if timestamps is None:
            timestamps = [time.time() - (len(entropy_values) - i) for i in range(len(entropy_values))]
        
        # Analyze drift patterns
        drift_analysis = self._analyze_drift_patterns(entropy_values, timestamps)
        
        # Determine overall drift status
        drift_detected = drift_analysis['drift_type'] != DriftType.STABLE
        
        # Calculate drift metrics
        drift_metrics = self._calculate_drift_metrics(entropy_values, timestamps)
        
        # Assess drift severity
        severity = self._assess_drift_severity(drift_analysis, drift_metrics)
        
        # Generate drift report
        drift_report = {
            'drift_detected': drift_detected,
            'drift_type': drift_analysis['drift_type'],
            'drift_severity': severity,
            'drift_metrics': drift_metrics,
            'pattern_analysis': drift_analysis,
            'detection_confidence': drift_analysis.get('confidence', 0.0),
            'timestamp': time.time(),
            'sample_count': len(entropy_values)
        }
        
        # Store in history
        self.drift_history.append(drift_report)
        
        # Maintain history size
        if len(self.drift_history) > 1000:
            self.drift_history = self.drift_history[-500:]
        
        return drift_report
    
    def _analyze_drift_patterns(self, values: List[float], timestamps: List[float]) -> Dict[str, Any]:
        """Analyze entropy values for specific drift patterns"""
        n = len(values)
        
        # Calculate basic statistics
        mean_val = sum(values) / n
        variance = sum((v - mean_val) ** 2 for v in values) / n
        std_dev = math.sqrt(variance)
        
        # Calculate trend (linear regression slope)
        trend = self._calculate_linear_trend(timestamps, values)
        
        # Calculate differences between consecutive values
        diffs = [values[i+1] - values[i] for i in range(n-1)]
        max_diff = max(abs(d) for d in diffs) if diffs else 0.0
        
        # Pattern detection
        patterns = {
            'gradual': self._detect_gradual_drift(trend),
            'sudden': self._detect_sudden_drift(diffs),
            'oscillating': self._detect_oscillating_drift(values),
            'chaotic': self._detect_chaotic_drift(variance, std_dev),
            'stable': self._detect_stable_drift(variance, max_diff)
        }
        
        # Determine primary drift type
        drift_type = self._determine_primary_drift_type(patterns)
        
        return {
            'drift_type': drift_type,
            'patterns': patterns,
            'statistics': {
                'mean': mean_val,
                'variance': variance,
                'std_dev': std_dev,
                'trend': trend,
                'max_diff': max_diff
            },
            'confidence': patterns.get(drift_type.value, {}).get('confidence', 0.0)
        }
    
    def _calculate_linear_trend(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate linear trend using least squares regression"""
        n = len(x_values)
        if n < 2:
            return 0.0
        
        x_mean = sum(x_values) / n
        y_mean = sum(y_values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _detect_gradual_drift(self, trend: float) -> Dict[str, Any]:
        """Detect gradual drift based on trend analysis"""
        abs_trend = abs(trend)
        is_gradual = abs_trend > self.thresholds['gradual_slope']
        
        confidence = min(abs_trend / self.thresholds['gradual_slope'], 1.0) if is_gradual else 0.0
        
        return {
            'detected': is_gradual,
            'confidence': confidence,
            'trend_magnitude': abs_trend,
            'direction': 'increasing' if trend > 0 else 'decreasing'
        }
    
    def _detect_sudden_drift(self, diffs: List[float]) -> Dict[str, Any]:
        """Detect sudden drift based on large single-step changes"""
        if not diffs:
            return {'detected': False, 'confidence': 0.0}
        
        max_abs_diff = max(abs(d) for d in diffs)
        is_sudden = max_abs_diff > self.thresholds['sudden_change']
        
        confidence = min(max_abs_diff / self.thresholds['sudden_change'], 1.0) if is_sudden else 0.0
        
        return {
            'detected': is_sudden,
            'confidence': confidence,
            'max_change': max_abs_diff,
            'change_points': [i for i, d in enumerate(diffs) if abs(d) > self.thresholds['sudden_change']]
        }
    
    def _detect_oscillating_drift(self, values: List[float]) -> Dict[str, Any]:
        """Detect oscillating drift patterns"""
        if len(values) < 4:
            return {'detected': False, 'confidence': 0.0}
        
        # Look for alternating increases/decreases
        direction_changes = 0
        for i in range(1, len(values) - 1):
            prev_diff = values[i] - values[i-1]
            next_diff = values[i+1] - values[i]
            if prev_diff * next_diff < 0:  # Sign change indicates direction change
                direction_changes += 1
        
        # Calculate oscillation amplitude
        amplitude = (max(values) - min(values)) / 2 if values else 0.0
        
        # Oscillation detected if many direction changes and significant amplitude
        oscillation_ratio = direction_changes / (len(values) - 2)
        is_oscillating = (oscillation_ratio > 0.5 and 
                         amplitude > self.thresholds['oscillation_amplitude'])
        
        confidence = min(oscillation_ratio * (amplitude / self.thresholds['oscillation_amplitude']), 1.0) if is_oscillating else 0.0
        
        return {
            'detected': is_oscillating,
            'confidence': confidence,
            'amplitude': amplitude,
            'direction_changes': direction_changes,
            'oscillation_ratio': oscillation_ratio
        }
    
    def _detect_chaotic_drift(self, variance: float, std_dev: float) -> Dict[str, Any]:
        """Detect chaotic drift based on high variance"""
        is_chaotic = variance > self.thresholds['chaos_variance']
        
        confidence = min(variance / self.thresholds['chaos_variance'], 1.0) if is_chaotic else 0.0
        
        return {
            'detected': is_chaotic,
            'confidence': confidence,
            'variance': variance,
            'std_dev': std_dev
        }
    
    def _detect_stable_drift(self, variance: float, max_diff: float) -> Dict[str, Any]:
        """Detect stable (no drift) patterns"""
        is_stable = (variance < self.thresholds['stability_window'] and 
                    max_diff < self.thresholds['stability_window'])
        
        # Inverse confidence - higher confidence for more stable values
        stability_score = 1.0 / (1.0 + variance + max_diff)
        confidence = stability_score if is_stable else 0.0
        
        return {
            'detected': is_stable,
            'confidence': confidence,
            'variance': variance,
            'max_diff': max_diff,
            'stability_score': stability_score
        }
    
    def _determine_primary_drift_type(self, patterns: Dict[str, Dict[str, Any]]) -> DriftType:
        """Determine the primary drift type based on pattern analysis"""
        # Get confidence scores for each pattern
        confidences = {
            DriftType.CHAOTIC: patterns['chaotic']['confidence'],
            DriftType.SUDDEN: patterns['sudden']['confidence'],
            DriftType.OSCILLATING: patterns['oscillating']['confidence'],
            DriftType.GRADUAL: patterns['gradual']['confidence'],
            DriftType.STABLE: patterns['stable']['confidence']
        }
        
        # Return the type with highest confidence
        return max(confidences.items(), key=lambda x: x[1])[0]
    
    def _calculate_drift_metrics(self, values: List[float], timestamps: List[float]) -> Dict[str, Any]:
        """Calculate comprehensive drift metrics"""
        if len(values) < 2:
            return {'status': 'insufficient_data'}
        
        # Rate of change metrics
        total_change = abs(values[-1] - values[0])
        time_span = timestamps[-1] - timestamps[0] if len(timestamps) >= 2 else 1.0
        average_rate = total_change / time_span if time_span > 0 else 0.0
        
        # Volatility metrics
        diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
        volatility = math.sqrt(sum(d*d for d in diffs) / len(diffs)) if diffs else 0.0
        
        # Directional consistency
        positive_changes = sum(1 for d in diffs if d > 0)
        negative_changes = sum(1 for d in diffs if d < 0)
        directional_consistency = abs(positive_changes - negative_changes) / len(diffs) if diffs else 0.0
        
        return {
            'total_change': total_change,
            'average_rate': average_rate,
            'volatility': volatility,
            'directional_consistency': directional_consistency,
            'time_span': time_span,
            'sample_count': len(values)
        }
    
    def _assess_drift_severity(self, drift_analysis: Dict[str, Any], drift_metrics: Dict[str, Any]) -> DriftSeverity:
        """Assess the severity of detected drift"""
        if drift_analysis['drift_type'] == DriftType.STABLE:
            return DriftSeverity.MINIMAL
        
        # Calculate combined severity score
        confidence = drift_analysis.get('confidence', 0.0)
        volatility = drift_metrics.get('volatility', 0.0)
        total_change = drift_metrics.get('total_change', 0.0)
        
        severity_score = (confidence + volatility + total_change) / 3.0
        
        # Map to severity levels
        for severity, threshold in reversed(list(self.severity_thresholds.items())):
            if severity_score >= threshold:
                return severity
        
        return DriftSeverity.MINIMAL
    
    def get_drift_summary(self) -> Dict[str, Any]:
        """Get summary of recent drift detection"""
        if not self.drift_history:
            return {'status': 'no_drift_data'}
        
        recent_drifts = [d for d in self.drift_history if time.time() - d['timestamp'] < 3600]  # Last hour
        
        drift_types = [d['drift_type'] for d in recent_drifts]
        severities = [d['drift_severity'] for d in recent_drifts]
        
        return {
            'total_detections': len(self.drift_history),
            'recent_detections': len(recent_drifts),
            'most_common_drift_type': max(set(drift_types), key=drift_types.count) if drift_types else None,
            'highest_recent_severity': max(severities) if severities else DriftSeverity.MINIMAL,
            'detection_sensitivity': self.detection_sensitivity,
            'thresholds': self.thresholds
        }
    
    def configure_detection(self, sensitivity: float = None, **thresholds):
        """Configure drift detection parameters"""
        if sensitivity is not None:
            self.detection_sensitivity = max(0.01, min(1.0, sensitivity))
        
        for key, value in thresholds.items():
            if key in self.thresholds:
                self.thresholds[key] = value