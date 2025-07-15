"""
Enhanced Entropy State Tracker for Aurora Symbolic Operations
Integrates with existing NativeEntropyTracker for comprehensive entropy monitoring
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple

try:
    from ...core.native_symbolic_anchor import NativeEntropyTracker
except ImportError:
    # Fallback if relative import fails
    try:
        from src.core.native_symbolic_anchor import NativeEntropyTracker
    except ImportError:
        # Create a mock class if the import fails completely
        class NativeEntropyTracker:
            def __init__(self):
                self.entropy_history = []
                self.tracking_window = 100
            
            def track_entropy(self, value):
                self.entropy_history.append((time.time(), value))
                if len(self.entropy_history) > self.tracking_window:
                    self.entropy_history = self.entropy_history[-self.tracking_window:]
            
            def get_entropy_trend(self):
                return {'trend': 0.0, 'stability': 1.0, 'current': 0.0}


class EntropyStateTracker:
    """Enhanced entropy state tracking with drift detection and alerts"""
    
    def __init__(self, base_tracker: Optional[NativeEntropyTracker] = None):
        self.base_tracker = base_tracker or NativeEntropyTracker()
        self.entropy_thresholds = {
            'stability_warning': 0.1,
            'stability_critical': 0.05,
            'drift_warning': 0.5,
            'drift_critical': 1.0
        }
        self.alert_history: List[Dict[str, Any]] = []
        self.monitoring_active = True
        
        # Enhanced tracking capabilities
        self.entropy_windows = {
            'short_term': [],  # Last 10 measurements
            'medium_term': [],  # Last 50 measurements
            'long_term': []    # Last 200 measurements
        }
        self.window_sizes = {'short_term': 10, 'medium_term': 50, 'long_term': 200}
    
    def track_enhanced_entropy(self, entropy_value: float, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Enhanced entropy tracking with multi-window analysis"""
        # Update base tracker
        self.base_tracker.track_entropy(entropy_value)
        
        # Update windowed tracking
        timestamp = time.time()
        entropy_entry = {
            'value': entropy_value,
            'timestamp': timestamp,
            'context': context or {}
        }
        
        for window_name, window in self.entropy_windows.items():
            window.append(entropy_entry)
            max_size = self.window_sizes[window_name]
            if len(window) > max_size:
                window.pop(0)
        
        # Perform analysis
        analysis = self._perform_entropy_analysis()
        
        # Check for alerts
        alerts = self._check_entropy_alerts(analysis)
        if alerts:
            self.alert_history.extend(alerts)
        
        return {
            'current_entropy': entropy_value,
            'analysis': analysis,
            'alerts': alerts,
            'monitoring_status': 'active' if self.monitoring_active else 'disabled'
        }
    
    def _perform_entropy_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive entropy analysis across windows"""
        analysis = {}
        
        for window_name, window in self.entropy_windows.items():
            if not window:
                analysis[window_name] = {'status': 'no_data'}
                continue
            
            values = [entry['value'] for entry in window]
            timestamps = [entry['timestamp'] for entry in window]
            
            # Basic statistics
            mean_entropy = sum(values) / len(values)
            variance = sum((v - mean_entropy) ** 2 for v in values) / len(values)
            std_dev = math.sqrt(variance)
            
            # Trend analysis
            if len(values) >= 2:
                trend = self._calculate_trend(timestamps, values)
            else:
                trend = 0.0
            
            # Stability assessment
            stability = 1.0 / (1.0 + variance) if variance > 0 else 1.0
            
            analysis[window_name] = {
                'status': 'active',
                'mean': mean_entropy,
                'variance': variance,
                'std_dev': std_dev,
                'trend': trend,
                'stability': stability,
                'sample_count': len(values)
            }
        
        # Cross-window analysis
        analysis['cross_window'] = self._cross_window_analysis()
        
        return analysis
    
    def _calculate_trend(self, timestamps: List[float], values: List[float]) -> float:
        """Calculate entropy trend using linear regression"""
        n = len(values)
        if n < 2:
            return 0.0
        
        # Normalize timestamps to start from 0
        t_start = timestamps[0]
        x_values = [t - t_start for t in timestamps]
        
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator > 0 else 0.0
    
    def _cross_window_analysis(self) -> Dict[str, Any]:
        """Analyze entropy patterns across different time windows"""
        windows_with_data = {name: window for name, window in self.entropy_windows.items() if window}
        
        if len(windows_with_data) < 2:
            return {'status': 'insufficient_data'}
        
        # Compare stability across windows
        stabilities = {}
        trends = {}
        
        for name, window in windows_with_data.items():
            values = [entry['value'] for entry in window]
            timestamps = [entry['timestamp'] for entry in window]
            
            mean_val = sum(values) / len(values)
            variance = sum((v - mean_val) ** 2 for v in values) / len(values)
            stabilities[name] = 1.0 / (1.0 + variance) if variance > 0 else 1.0
            trends[name] = self._calculate_trend(timestamps, values) if len(values) >= 2 else 0.0
        
        # Assess convergence/divergence
        stability_values = list(stabilities.values())
        trend_values = list(trends.values())
        
        stability_convergence = max(stability_values) - min(stability_values)
        trend_convergence = max(trend_values) - min(trend_values)
        
        return {
            'status': 'active',
            'stability_by_window': stabilities,
            'trends_by_window': trends,
            'stability_convergence': stability_convergence,
            'trend_convergence': trend_convergence,
            'overall_stability': sum(stability_values) / len(stability_values),
            'overall_trend': sum(trend_values) / len(trend_values)
        }
    
    def _check_entropy_alerts(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for entropy-based alerts and warnings"""
        alerts = []
        timestamp = time.time()
        
        if not self.monitoring_active:
            return alerts
        
        # Check stability alerts
        cross_window = analysis.get('cross_window', {})
        overall_stability = cross_window.get('overall_stability', 1.0)
        
        if overall_stability < self.entropy_thresholds['stability_critical']:
            alerts.append({
                'type': 'stability_critical',
                'level': 'critical',
                'message': f'Entropy stability critically low: {overall_stability:.4f}',
                'timestamp': timestamp,
                'value': overall_stability,
                'threshold': self.entropy_thresholds['stability_critical']
            })
        elif overall_stability < self.entropy_thresholds['stability_warning']:
            alerts.append({
                'type': 'stability_warning',
                'level': 'warning',
                'message': f'Entropy stability warning: {overall_stability:.4f}',
                'timestamp': timestamp,
                'value': overall_stability,
                'threshold': self.entropy_thresholds['stability_warning']
            })
        
        # Check drift alerts
        overall_trend = abs(cross_window.get('overall_trend', 0.0))
        
        if overall_trend > self.entropy_thresholds['drift_critical']:
            alerts.append({
                'type': 'drift_critical',
                'level': 'critical',
                'message': f'Entropy drift critically high: {overall_trend:.4f}',
                'timestamp': timestamp,
                'value': overall_trend,
                'threshold': self.entropy_thresholds['drift_critical']
            })
        elif overall_trend > self.entropy_thresholds['drift_warning']:
            alerts.append({
                'type': 'drift_warning',
                'level': 'warning',
                'message': f'Entropy drift warning: {overall_trend:.4f}',
                'timestamp': timestamp,
                'value': overall_trend,
                'threshold': self.entropy_thresholds['drift_warning']
            })
        
        return alerts
    
    def get_entropy_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive entropy state summary"""
        base_trend = self.base_tracker.get_entropy_trend()
        recent_alerts = [alert for alert in self.alert_history if time.time() - alert['timestamp'] < 3600]  # Last hour
        
        return {
            'base_entropy_trend': base_trend,
            'enhanced_analysis': self._perform_entropy_analysis() if any(self.entropy_windows.values()) else None,
            'recent_alerts': recent_alerts,
            'alert_count': len(self.alert_history),
            'monitoring_active': self.monitoring_active,
            'thresholds': self.entropy_thresholds,
            'tracking_windows': {name: len(window) for name, window in self.entropy_windows.items()}
        }
    
    def set_entropy_thresholds(self, **thresholds):
        """Update entropy monitoring thresholds"""
        for key, value in thresholds.items():
            if key in self.entropy_thresholds:
                self.entropy_thresholds[key] = value
    
    def clear_alert_history(self):
        """Clear alert history"""
        self.alert_history.clear()
    
    def toggle_monitoring(self, active: bool):
        """Enable or disable entropy monitoring"""
        self.monitoring_active = active