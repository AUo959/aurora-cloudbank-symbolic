"""
Auto-Stabilization System for Aurora Symbolic Anchors
Provides automatic stabilization protocols with threshold management
"""

import time
import math
from typing import Dict, List, Any, Optional, Callable, Tuple
from enum import Enum
from .drift_detection import DriftDetector, DriftType, DriftSeverity


class StabilizationStrategy(Enum):
    """Stabilization strategies for different drift patterns"""
    DAMPING = "damping"              # Gradual correction with exponential decay
    RESET = "reset"                  # Reset to baseline values
    SMOOTHING = "smoothing"          # Moving average smoothing
    FEEDBACK = "feedback"            # Feedback control loop
    ADAPTIVE = "adaptive"            # Adaptive strategy selection


class StabilizationStatus(Enum):
    """Status of stabilization operations"""
    STABLE = "stable"
    STABILIZING = "stabilizing"
    UNSTABLE = "unstable"
    CRITICAL = "critical"
    DISABLED = "disabled"


class AutoStabilizer:
    """Automatic stabilization system for symbolic anchor entropy"""
    
    def __init__(self, drift_detector: Optional[DriftDetector] = None):
        self.drift_detector = drift_detector or DriftDetector()
        self.stabilization_active = True
        self.status = StabilizationStatus.STABLE
        
        # Stabilization thresholds
        self.thresholds = {
            'intervention_threshold': 0.3,    # When to start stabilization
            'critical_threshold': 0.7,        # When to use emergency protocols
            'stability_target': 0.05,         # Target stability level
            'max_correction_rate': 0.1        # Maximum correction per step
        }
        
        # Strategy configuration
        self.strategy_preferences = {
            DriftType.GRADUAL: StabilizationStrategy.DAMPING,
            DriftType.SUDDEN: StabilizationStrategy.RESET,
            DriftType.OSCILLATING: StabilizationStrategy.SMOOTHING,
            DriftType.CHAOTIC: StabilizationStrategy.FEEDBACK,
            DriftType.STABLE: StabilizationStrategy.ADAPTIVE
        }
        
        # Stabilization history
        self.stabilization_history: List[Dict[str, Any]] = []
        self.baseline_entropy = 0.5  # Default baseline entropy
        self.correction_history: List[float] = []
        
        # Feedback control parameters
        self.pid_gains = {'kp': 0.5, 'ki': 0.1, 'kd': 0.2}
        self.integral_error = 0.0
        self.previous_error = 0.0
        
    def stabilize_entropy(self, current_entropy: float, entropy_history: List[float], 
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main stabilization function"""
        if not self.stabilization_active:
            return {
                'action': 'none',
                'reason': 'stabilization_disabled',
                'status': StabilizationStatus.DISABLED
            }
        
        # Detect drift patterns
        drift_report = self.drift_detector.detect_drift(entropy_history)
        
        # Assess need for intervention
        intervention_needed = self._assess_intervention_need(current_entropy, drift_report)
        
        if not intervention_needed['required']:
            self.status = StabilizationStatus.STABLE
            return {
                'action': 'monitor',
                'status': self.status,
                'current_entropy': current_entropy,
                'drift_report': drift_report,
                'intervention_assessment': intervention_needed
            }
        
        # Select stabilization strategy
        strategy = self._select_stabilization_strategy(drift_report, intervention_needed)
        
        # Apply stabilization
        stabilization_result = self._apply_stabilization(
            current_entropy, entropy_history, strategy, drift_report, context
        )
        
        # Update status
        self._update_stabilization_status(stabilization_result)
        
        # Record stabilization action
        self._record_stabilization_action(stabilization_result)
        
        return stabilization_result
    
    def _assess_intervention_need(self, current_entropy: float, drift_report: Dict[str, Any]) -> Dict[str, Any]:
        """Assess whether stabilization intervention is needed"""
        drift_detected = drift_report.get('drift_detected', False)
        drift_severity = drift_report.get('drift_severity', DriftSeverity.MINIMAL)
        drift_confidence = drift_report.get('detection_confidence', 0.0)
        
        # Calculate deviation from baseline
        baseline_deviation = abs(current_entropy - self.baseline_entropy)
        
        # Assess intervention criteria
        criteria = {
            'drift_detected': drift_detected,
            'severity_threshold': drift_severity.value in ['significant', 'critical'],
            'confidence_threshold': drift_confidence > 0.5,
            'baseline_deviation': baseline_deviation > self.thresholds['intervention_threshold'],
            'critical_level': baseline_deviation > self.thresholds['critical_threshold']
        }
        
        # Determine if intervention is required
        intervention_required = any([
            criteria['severity_threshold'] and criteria['confidence_threshold'],
            criteria['critical_level'],
            criteria['baseline_deviation'] and drift_detected
        ])
        
        return {
            'required': intervention_required,
            'criteria': criteria,
            'baseline_deviation': baseline_deviation,
            'urgency': 'critical' if criteria['critical_level'] else 'normal'
        }
    
    def _select_stabilization_strategy(self, drift_report: Dict[str, Any], 
                                      intervention: Dict[str, Any]) -> StabilizationStrategy:
        """Select appropriate stabilization strategy"""
        drift_type = drift_report.get('drift_type', DriftType.STABLE)
        urgency = intervention.get('urgency', 'normal')
        
        # Emergency protocols for critical situations
        if urgency == 'critical':
            return StabilizationStrategy.RESET
        
        # Use preferred strategy for detected drift type
        preferred_strategy = self.strategy_preferences.get(drift_type, StabilizationStrategy.ADAPTIVE)
        
        # Adaptive strategy selection
        if preferred_strategy == StabilizationStrategy.ADAPTIVE:
            return self._adaptive_strategy_selection(drift_report, intervention)
        
        return preferred_strategy
    
    def _adaptive_strategy_selection(self, drift_report: Dict[str, Any], 
                                   intervention: Dict[str, Any]) -> StabilizationStrategy:
        """Adaptively select stabilization strategy based on current conditions"""
        drift_confidence = drift_report.get('detection_confidence', 0.0)
        baseline_deviation = intervention.get('baseline_deviation', 0.0)
        
        # Strategy selection logic
        if drift_confidence > 0.8 and baseline_deviation > 0.5:
            return StabilizationStrategy.FEEDBACK
        elif baseline_deviation > 0.3:
            return StabilizationStrategy.DAMPING
        else:
            return StabilizationStrategy.SMOOTHING
    
    def _apply_stabilization(self, current_entropy: float, entropy_history: List[float],
                           strategy: StabilizationStrategy, drift_report: Dict[str, Any],
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Apply selected stabilization strategy"""
        timestamp = time.time()
        
        # Strategy implementation dispatch
        if strategy == StabilizationStrategy.DAMPING:
            result = self._apply_damping_stabilization(current_entropy, entropy_history)
        elif strategy == StabilizationStrategy.RESET:
            result = self._apply_reset_stabilization(current_entropy)
        elif strategy == StabilizationStrategy.SMOOTHING:
            result = self._apply_smoothing_stabilization(current_entropy, entropy_history)
        elif strategy == StabilizationStrategy.FEEDBACK:
            result = self._apply_feedback_stabilization(current_entropy, entropy_history)
        else:
            result = self._apply_adaptive_stabilization(current_entropy, entropy_history, drift_report)
        
        # Common result formatting
        stabilization_result = {
            'action': 'stabilize',
            'strategy': strategy,
            'timestamp': timestamp,
            'original_entropy': current_entropy,
            'corrected_entropy': result['corrected_entropy'],
            'correction_magnitude': result['correction_magnitude'],
            'confidence': result.get('confidence', 0.8),
            'status': self.status,
            'drift_report': drift_report,
            'context': context or {}
        }
        
        return stabilization_result
    
    def _apply_damping_stabilization(self, current_entropy: float, history: List[float]) -> Dict[str, Any]:
        """Apply exponential damping correction"""
        damping_factor = 0.7  # Adjustable damping strength
        
        # Calculate target entropy (moving toward baseline)
        error = current_entropy - self.baseline_entropy
        correction = -error * damping_factor * self.thresholds['max_correction_rate']
        
        corrected_entropy = current_entropy + correction
        
        return {
            'corrected_entropy': corrected_entropy,
            'correction_magnitude': abs(correction),
            'damping_factor': damping_factor,
            'error': error
        }
    
    def _apply_reset_stabilization(self, current_entropy: float) -> Dict[str, Any]:
        """Apply reset stabilization (emergency protocol)"""
        # Reset to baseline with safety margin
        safety_margin = 0.02
        corrected_entropy = self.baseline_entropy + (
            safety_margin if current_entropy > self.baseline_entropy else -safety_margin
        )
        
        correction_magnitude = abs(corrected_entropy - current_entropy)
        
        return {
            'corrected_entropy': corrected_entropy,
            'correction_magnitude': correction_magnitude,
            'reset_target': self.baseline_entropy,
            'safety_margin': safety_margin
        }
    
    def _apply_smoothing_stabilization(self, current_entropy: float, history: List[float]) -> Dict[str, Any]:
        """Apply moving average smoothing"""
        window_size = min(5, len(history))  # Use last 5 values or available
        
        if len(history) < window_size:
            # Not enough history, use simple correction
            return self._apply_damping_stabilization(current_entropy, history)
        
        # Calculate moving average
        recent_values = history[-window_size:]
        moving_average = sum(recent_values) / len(recent_values)
        
        # Smooth toward moving average
        smoothing_factor = 0.3
        corrected_entropy = current_entropy * (1 - smoothing_factor) + moving_average * smoothing_factor
        
        return {
            'corrected_entropy': corrected_entropy,
            'correction_magnitude': abs(corrected_entropy - current_entropy),
            'moving_average': moving_average,
            'smoothing_factor': smoothing_factor,
            'window_size': window_size
        }
    
    def _apply_feedback_stabilization(self, current_entropy: float, history: List[float]) -> Dict[str, Any]:
        """Apply PID feedback control"""
        # Calculate error
        error = current_entropy - self.baseline_entropy
        
        # Update integral error
        self.integral_error += error
        
        # Calculate derivative error
        derivative_error = error - self.previous_error
        
        # PID correction
        pid_correction = (
            self.pid_gains['kp'] * error +
            self.pid_gains['ki'] * self.integral_error +
            self.pid_gains['kd'] * derivative_error
        )
        
        # Apply correction with rate limiting
        correction = max(-self.thresholds['max_correction_rate'], 
                        min(self.thresholds['max_correction_rate'], -pid_correction))
        
        corrected_entropy = current_entropy + correction
        
        # Update previous error
        self.previous_error = error
        
        return {
            'corrected_entropy': corrected_entropy,
            'correction_magnitude': abs(correction),
            'pid_correction': pid_correction,
            'error_terms': {
                'proportional': error,
                'integral': self.integral_error,
                'derivative': derivative_error
            }
        }
    
    def _apply_adaptive_stabilization(self, current_entropy: float, history: List[float],
                                    drift_report: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adaptive stabilization based on current conditions"""
        # Analyze recent stabilization effectiveness
        recent_corrections = self.correction_history[-10:] if len(self.correction_history) >= 10 else self.correction_history
        
        if not recent_corrections:
            # No correction history, use damping
            return self._apply_damping_stabilization(current_entropy, history)
        
        # Calculate average correction effectiveness
        avg_correction = sum(recent_corrections) / len(recent_corrections)
        
        # Adapt strategy based on effectiveness
        if avg_correction < 0.1:  # Small corrections working well
            return self._apply_smoothing_stabilization(current_entropy, history)
        else:  # Need stronger intervention
            return self._apply_feedback_stabilization(current_entropy, history)
    
    def _update_stabilization_status(self, result: Dict[str, Any]):
        """Update stabilization status based on result"""
        correction_magnitude = result.get('correction_magnitude', 0.0)
        
        if correction_magnitude < 0.01:
            self.status = StabilizationStatus.STABLE
        elif correction_magnitude < 0.1:
            self.status = StabilizationStatus.STABILIZING
        elif correction_magnitude < 0.3:
            self.status = StabilizationStatus.UNSTABLE
        else:
            self.status = StabilizationStatus.CRITICAL
    
    def _record_stabilization_action(self, result: Dict[str, Any]):
        """Record stabilization action in history"""
        self.stabilization_history.append(result)
        
        # Record correction magnitude for adaptive learning
        correction_magnitude = result.get('correction_magnitude', 0.0)
        self.correction_history.append(correction_magnitude)
        
        # Maintain history limits
        if len(self.stabilization_history) > 1000:
            self.stabilization_history = self.stabilization_history[-500:]
        
        if len(self.correction_history) > 100:
            self.correction_history = self.correction_history[-50:]
    
    def get_stabilization_summary(self) -> Dict[str, Any]:
        """Get comprehensive stabilization system summary"""
        recent_actions = [a for a in self.stabilization_history 
                         if time.time() - a['timestamp'] < 3600]  # Last hour
        
        if recent_actions:
            avg_correction = sum(a['correction_magnitude'] for a in recent_actions) / len(recent_actions)
            strategies_used = [a['strategy'] for a in recent_actions]
            most_used_strategy = max(set(strategies_used), key=strategies_used.count)
        else:
            avg_correction = 0.0
            most_used_strategy = None
        
        return {
            'status': self.status,
            'active': self.stabilization_active,
            'baseline_entropy': self.baseline_entropy,
            'total_stabilizations': len(self.stabilization_history),
            'recent_stabilizations': len(recent_actions),
            'average_recent_correction': avg_correction,
            'most_used_strategy': most_used_strategy,
            'thresholds': self.thresholds,
            'pid_gains': self.pid_gains,
            'strategy_preferences': {k.value: v.value for k, v in self.strategy_preferences.items()}
        }
    
    def configure_stabilizer(self, baseline_entropy: float = None, **thresholds):
        """Configure stabilizer parameters"""
        if baseline_entropy is not None:
            self.baseline_entropy = baseline_entropy
        
        for key, value in thresholds.items():
            if key in self.thresholds:
                self.thresholds[key] = value
    
    def set_pid_gains(self, kp: float = None, ki: float = None, kd: float = None):
        """Configure PID controller gains"""
        if kp is not None:
            self.pid_gains['kp'] = kp
        if ki is not None:
            self.pid_gains['ki'] = ki
        if kd is not None:
            self.pid_gains['kd'] = kd
    
    def reset_stabilizer(self):
        """Reset stabilizer state"""
        self.integral_error = 0.0
        self.previous_error = 0.0
        self.status = StabilizationStatus.STABLE
        self.correction_history.clear()
    
    def enable_stabilization(self):
        """Enable automatic stabilization"""
        self.stabilization_active = True
    
    def disable_stabilization(self):
        """Disable automatic stabilization"""
        self.stabilization_active = False
        self.status = StabilizationStatus.DISABLED