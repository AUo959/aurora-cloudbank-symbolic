"""
Drift Prediction Module - Thread Transfer Bridge v2
==================================================

LSTM-based drift prediction for proactive thread continuity management.

Features:
- Historical drift pattern analysis
- LSTM time-series prediction
- 24-hour prediction horizon
- Auto-correction recommendations
- Feature engineering (11 features)

Thread: T1→BRIDGE_V2→DRIFT_PRED
DLP: context_tag=bridge_v2_drift_prediction
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

# Optional ML imports with graceful fallback
try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not available - drift prediction will use statistical fallback")


class DriftSeverity(Enum):
    """Drift severity levels."""
    NONE = "none"              # < 0.001%
    LOW = "low"                # 0.001% - 0.1%
    MEDIUM = "medium"          # 0.1% - 0.5%
    HIGH = "high"              # 0.5% - 1.0%
    CRITICAL = "critical"      # > 1.0%


class PredictionConfidence(Enum):
    """Prediction confidence levels."""
    HIGH = "high"              # > 90% accuracy
    MEDIUM = "medium"          # 70-90% accuracy
    LOW = "low"                # < 70% accuracy


@dataclass
class DriftFeatures:
    """Drift features for ML model (11 features total)."""
    drift_velocity: float              # Rate of drift change (Δ/hour)
    drift_acceleration: float          # Rate of velocity change
    handshake_count: int               # Number of handshakes in window
    average_handshake_duration: float  # Average duration (seconds)
    failed_handshake_ratio: float      # Failures / total
    time_of_day: float                 # Hour of day (0-23)
    day_of_week: int                   # Day (0-6)
    thread_age_hours: float            # Thread lifetime
    anchor_changes: int                # Anchor updates in window
    sync_frequency: float              # Syncs per hour
    node_count: int                    # Active nodes in cluster
    
    def to_vector(self) -> List[float]:
        """Convert to feature vector."""
        return [
            self.drift_velocity,
            self.drift_acceleration,
            float(self.handshake_count),
            self.average_handshake_duration,
            self.failed_handshake_ratio,
            self.time_of_day,
            float(self.day_of_week),
            self.thread_age_hours,
            float(self.anchor_changes),
            self.sync_frequency,
            float(self.node_count)
        ]
    
    @classmethod
    def from_vector(cls, vector: List[float]) -> "DriftFeatures":
        """Create from feature vector."""
        return cls(
            drift_velocity=vector[0],
            drift_acceleration=vector[1],
            handshake_count=int(vector[2]),
            average_handshake_duration=vector[3],
            failed_handshake_ratio=vector[4],
            time_of_day=vector[5],
            day_of_week=int(vector[6]),
            thread_age_hours=vector[7],
            anchor_changes=int(vector[8]),
            sync_frequency=vector[9],
            node_count=int(vector[10])
        )


@dataclass
class DriftPrediction:
    """Drift prediction result."""
    predicted_drift: float             # Predicted drift percentage
    severity: DriftSeverity
    confidence: PredictionConfidence
    prediction_horizon_hours: int
    timestamp: datetime
    features: DriftFeatures
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "predicted_drift": self.predicted_drift,
            "severity": self.severity.value,
            "confidence": self.confidence.value,
            "prediction_horizon_hours": self.prediction_horizon_hours,
            "timestamp": self.timestamp.isoformat(),
            "features": self.features.__dict__,
            "recommendations": self.recommendations,
            "metadata": self.metadata
        }


class LSTMDriftModel(nn.Module if HAS_TORCH else object):
    """
    LSTM model for drift prediction.
    
    Architecture:
    - Input: 11 features x sequence_length timesteps
    - LSTM: 64 hidden units, 2 layers
    - Dropout: 0.2
    - Output: 1 value (predicted drift %)
    """
    
    def __init__(self, input_size: int = 11, hidden_size: int = 64, num_layers: int = 2):
        """Initialize LSTM model."""
        if not HAS_TORCH:
            logger.warning("PyTorch not available - LSTM model disabled")
            return
        
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x):
        """Forward pass."""
        if not HAS_TORCH:
            return None
        
        # LSTM forward
        lstm_out, _ = self.lstm(x)
        
        # Take last timestep output
        last_output = lstm_out[:, -1, :]
        
        # Fully connected layer
        prediction = self.fc(last_output)
        
        return prediction


class DriftPredictor:
    """
    Drift prediction engine.
    
    Uses LSTM model to predict future drift based on historical patterns.
    Falls back to statistical methods if PyTorch unavailable.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        prediction_horizon: int = 24
    ):
        """
        Initialize drift predictor.

        Args:
            model_path: Optional path to pre-trained model
            prediction_horizon: Hours to predict ahead (default: 24)
        """
        self.prediction_horizon = prediction_horizon
        self.model = None
        self.history: List[Tuple[datetime, DriftFeatures, float]] = []
        self._history_lock = asyncio.Lock()
        
        if HAS_TORCH:
            self.model = LSTMDriftModel()
            if model_path:
                try:
                    self.model.load_state_dict(torch.load(model_path))
                    self.model.eval()
                    logger.info(f"Loaded pre-trained model from {model_path}")
                except Exception as e:
                    logger.warning(f"Failed to load model: {e}")
        else:
            logger.info("Using statistical fallback for drift prediction")

    async def predict_drift(
        self,
        current_features: DriftFeatures,
        thread_id: Optional[str] = None
    ) -> DriftPrediction:
        """
        Predict future drift.

        Args:
            current_features: Current drift features
            thread_id: Optional thread identifier

        Returns:
            DriftPrediction object
        """
        try:
            if HAS_TORCH and self.model:
                predicted_drift = await self._predict_with_lstm(current_features)
            else:
                predicted_drift = await self._predict_statistical(current_features)
            
            # Determine severity
            severity = self._determine_severity(predicted_drift)
            
            # Determine confidence
            confidence = self._determine_confidence(current_features)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                predicted_drift,
                severity,
                current_features
            )
            
            prediction = DriftPrediction(
                predicted_drift=predicted_drift,
                severity=severity,
                confidence=confidence,
                prediction_horizon_hours=self.prediction_horizon,
                timestamp=datetime.now(),
                features=current_features,
                recommendations=recommendations,
                metadata={"thread_id": thread_id} if thread_id else {}
            )
            
            logger.info(
                f"Drift prediction: {predicted_drift:.4f}% "
                f"(severity={severity.value}, confidence={confidence.value})"
            )
            
            return prediction
            
        except Exception as e:
            logger.error(f"Drift prediction failed: {e}")
            # Return safe fallback prediction
            return DriftPrediction(
                predicted_drift=0.001,
                severity=DriftSeverity.NONE,
                confidence=PredictionConfidence.LOW,
                prediction_horizon_hours=self.prediction_horizon,
                timestamp=datetime.now(),
                features=current_features,
                recommendations=["Unable to generate accurate prediction"],
                metadata={"error": str(e)}
            )

    async def _predict_with_lstm(self, features: DriftFeatures) -> float:
        """Predict using LSTM model."""
        if not HAS_TORCH or not self.model:
            return await self._predict_statistical(features)
        
        try:
            # Convert features to tensor
            feature_vector = features.to_vector()
            
            # Create sequence (use history if available, otherwise repeat current)
            if len(self.history) >= 10:
                sequence = [h[1].to_vector() for h in self.history[-10:]]
            else:
                # Repeat current features to create sequence
                sequence = [feature_vector] * 10
            
            # Convert to tensor
            x = torch.tensor([sequence], dtype=torch.float32)
            
            # Predict
            with torch.no_grad():
                prediction = self.model(x)
                predicted_drift = float(prediction[0, 0].item())
            
            # Clamp to reasonable range
            predicted_drift = max(0.0, min(5.0, predicted_drift))
            
            return predicted_drift
            
        except Exception as e:
            logger.error(f"LSTM prediction failed: {e}")
            return await self._predict_statistical(features)

    async def _predict_statistical(self, features: DriftFeatures) -> float:
        """
        Statistical fallback prediction.
        
        Uses linear extrapolation based on velocity and acceleration.
        """
        # Base prediction on current velocity and acceleration
        base_drift = features.drift_velocity * self.prediction_horizon
        acceleration_component = (
            0.5 * features.drift_acceleration * (self.prediction_horizon ** 2)
        )
        
        predicted_drift = abs(base_drift + acceleration_component)
        
        # Adjust for historical patterns
        if len(self.history) > 0:
            recent_drifts = [h[2] for h in self.history[-24:]]  # Last 24 hours
            avg_drift = sum(recent_drifts) / len(recent_drifts)
            
            # Blend prediction with historical average
            predicted_drift = 0.7 * predicted_drift + 0.3 * avg_drift
        
        # Factor in risk indicators
        risk_multiplier = 1.0
        if features.failed_handshake_ratio > 0.1:
            risk_multiplier += 0.5
        if features.anchor_changes > 5:
            risk_multiplier += 0.3
        
        predicted_drift *= risk_multiplier
        
        # Clamp to reasonable range
        return max(0.0, min(5.0, predicted_drift))

    def _determine_severity(self, drift: float) -> DriftSeverity:
        """Determine drift severity level."""
        if drift < 0.001:
            return DriftSeverity.NONE
        elif drift < 0.1:
            return DriftSeverity.LOW
        elif drift < 0.5:
            return DriftSeverity.MEDIUM
        elif drift < 1.0:
            return DriftSeverity.HIGH
        else:
            return DriftSeverity.CRITICAL

    def _determine_confidence(self, features: DriftFeatures) -> PredictionConfidence:
        """Determine prediction confidence."""
        confidence_score = 0.9  # Start optimistic
        
        # Reduce confidence based on uncertainty indicators
        if len(self.history) < 10:
            confidence_score -= 0.2  # Insufficient history
        
        if features.failed_handshake_ratio > 0.2:
            confidence_score -= 0.15  # High failure rate
        
        if features.drift_acceleration > 0.01:
            confidence_score -= 0.1  # Rapidly changing conditions
        
        if confidence_score >= 0.9:
            return PredictionConfidence.HIGH
        elif confidence_score >= 0.7:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW

    def _generate_recommendations(
        self,
        predicted_drift: float,
        severity: DriftSeverity,
        features: DriftFeatures
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if severity in [DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            recommendations.append("URGENT: Consider immediate anchor re-synchronization")
        
        if severity in [DriftSeverity.MEDIUM, DriftSeverity.HIGH, DriftSeverity.CRITICAL]:
            recommendations.append("Increase handshake frequency to every 5 minutes")
        
        if features.failed_handshake_ratio > 0.1:
            recommendations.append(
                f"High failure rate ({features.failed_handshake_ratio:.1%}) - "
                "investigate network or node issues"
            )
        
        if features.anchor_changes > 10:
            recommendations.append(
                "High anchor churn detected - consider stabilizing thread context"
            )
        
        if features.node_count < 3:
            recommendations.append(
                "Low node count - add redundancy for improved stability"
            )
        
        if predicted_drift > 0.5 and features.sync_frequency < 0.5:
            recommendations.append(
                "Increase sync frequency to at least once per 2 hours"
            )
        
        if not recommendations:
            recommendations.append("System operating within normal parameters")
        
        return recommendations

    async def record_observation(
        self,
        features: DriftFeatures,
        actual_drift: float
    ):
        """
        Record actual drift observation for model improvement.

        Args:
            features: Features at time of observation
            actual_drift: Actual measured drift
        """
        async with self._history_lock:
            self.history.append((datetime.now(), features, actual_drift))
            
            # Keep last 1000 observations
            if len(self.history) > 1000:
                self.history = self.history[-1000:]
            
            logger.debug(
                f"Recorded drift observation: {actual_drift:.4f}% "
                f"(history size: {len(self.history)})"
            )

    async def get_prediction_accuracy(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate prediction accuracy over recent history.

        Args:
            hours: Hours to analyze

        Returns:
            Accuracy metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        async with self._history_lock:
            recent = [h for h in self.history if h[0] >= cutoff_time]
        
        if len(recent) < 2:
            return {
                "accuracy": 0.0,
                "observations": 0,
                "error": "Insufficient data"
            }
        
        # Calculate mean absolute error
        errors = []
        for i in range(len(recent) - 1):
            actual = recent[i + 1][2]
            # Use features from previous timestep to "predict" next
            features = recent[i][1]
            predicted = await self._predict_statistical(features)
            errors.append(abs(predicted - actual))
        
        mae = sum(errors) / len(errors) if errors else 0.0
        accuracy = max(0.0, 1.0 - mae / 0.5)  # Normalize to 0-1
        
        return {
            "accuracy": accuracy,
            "mean_absolute_error": mae,
            "observations": len(recent),
            "time_window_hours": hours
        }


# Global predictor instance
_predictor = None


def get_drift_predictor() -> DriftPredictor:
    """Get global drift predictor instance."""
    global _predictor
    if _predictor is None:
        _predictor = DriftPredictor()
    return _predictor
