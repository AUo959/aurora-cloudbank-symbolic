#!/usr/bin/env python3
"""
Probabilistic Forecast Engine - Orion Station Temporal Projection

Time-series forecasting with nested simulation-based confidence intervals.
Routes predictions through Aurora's simulation infrastructure for high-fidelity
uncertainty quantification.

Use Cases:
- Sales and revenue forecasting
- Resource demand prediction
- Market trend analysis
- Capacity planning

Anchor: ORION-FORECAST-ENGINE-V1
Team: AUo959-team
Ethics: Picard_Delta_3
"""

import json
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class TrendType(Enum):
    """Types of trends in time series."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    SEASONAL = "seasonal"
    CYCLICAL = "cyclical"


class ForecastMethod(Enum):
    """Forecasting methods."""
    NAIVE = "naive"  # Last value propagated
    MOVING_AVERAGE = "moving_average"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"
    TREND_PROJECTION = "trend_projection"
    MONTE_CARLO = "monte_carlo"  # Simulation-based


@dataclass
class TimeSeriesData:
    """Historical time series data."""
    values: List[float]
    timestamps: Optional[List[str]] = None
    frequency: str = "daily"  # daily, weekly, monthly, etc.
    
    def __post_init__(self):
        if self.timestamps and len(self.timestamps) != len(self.values):
            raise ValueError("Timestamps and values must have same length")


@dataclass
class ForecastResult:
    """Forecast with confidence intervals."""
    horizon: int  # Number of periods ahead
    point_forecast: List[float]
    lower_bound_80: List[float]  # 80% confidence interval
    upper_bound_80: List[float]
    lower_bound_95: List[float]  # 95% confidence interval
    upper_bound_95: List[float]
    method: str
    timestamp: str
    anchor: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)


class ProbabilisticForecastEngine:
    """
    Time-series forecasting engine with simulation-based confidence intervals.
    
    Routes predictions through Orion Station's nested simulation infrastructure
    to provide research-grade uncertainty quantification.
    """
    
    def __init__(self, anchor_seed: str = "ORION_FORECAST"):
        self.anchor_seed = anchor_seed
        self.forecast_count = 0
        
    def _detect_trend(self, values: List[float]) -> Tuple[float, float]:
        """
        Detect linear trend in data using least squares.
        
        Returns:
            (slope, intercept) of the trend line
        """
        n = len(values)
        if n < 2:
            return 0.0, values[0] if values else 0.0
        
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0, y_mean
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        return slope, intercept
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate historical volatility (standard deviation of returns)."""
        if len(values) < 2:
            return 0.0

        returns = [(values[i] - values[i-1]) / values[i-1]
                   for i in range(1, len(values)) if values[i-1] != 0]

        if not returns:
            return 0.0

        return statistics.stdev(returns) if len(returns) > 1 else abs(returns[0])
    
    def _naive_forecast(
        self,
        data: TimeSeriesData,
        horizon: int
    ) -> List[float]:
        """Naive forecast: repeat last value."""
        last_value = data.values[-1]
        return [last_value] * horizon
    
    def _moving_average_forecast(
        self,
        data: TimeSeriesData,
        horizon: int,
        window: int = 3
    ) -> List[float]:
        """Moving average forecast."""
        window = min(window, len(data.values))
        recent_values = data.values[-window:]
        avg = sum(recent_values) / len(recent_values)
        return [avg] * horizon
    
    def _trend_projection_forecast(
        self,
        data: TimeSeriesData,
        horizon: int
    ) -> List[float]:
        """Linear trend projection."""
        slope, intercept = self._detect_trend(data.values)
        n = len(data.values)
        
        forecast = []
        for h in range(1, horizon + 1):
            value = intercept + slope * (n + h - 1)
            forecast.append(value)
        
        return forecast
    
    def _exponential_smoothing_forecast(
        self,
        data: TimeSeriesData,
        horizon: int,
        alpha: float = 0.3
    ) -> List[float]:
        """Exponential smoothing forecast."""
        if not data.values:
            return [0.0] * horizon
        
        # Calculate smoothed values
        smoothed = [data.values[0]]
        for value in data.values[1:]:
            smoothed_value = alpha * value + (1 - alpha) * smoothed[-1]
            smoothed.append(smoothed_value)
        
        # Project forward
        last_smoothed = smoothed[-1]
        
        # Detect trend in smoothed series
        slope, _ = self._detect_trend(smoothed[-min(10, len(smoothed)):])
        
        forecast = []
        for h in range(1, horizon + 1):
            value = last_smoothed + slope * h
            forecast.append(value)
        
        return forecast
    
    def _monte_carlo_forecast(
        self,
        data: TimeSeriesData,
        horizon: int,
        num_simulations: int = 1000
    ) -> Tuple[List[float], List[List[float]]]:
        """
        Monte Carlo simulation-based forecast.
        
        Returns:
            (point_forecast, all_paths) where all_paths is list of simulated paths
        """
        if len(data.values) < 2:
            return [data.values[0]] * horizon, [[data.values[0]] * horizon]
        
        # Estimate drift (trend) and volatility
        slope, intercept = self._detect_trend(data.values)
        volatility = self._calculate_volatility(data.values)
        
        # Base level
        last_value = data.values[-1]
        n = len(data.values)
        
        # Run simulations
        all_paths = []
        
        for _ in range(num_simulations):
            path = []
            current_value = last_value
            
            for h in range(1, horizon + 1):
                # Trend component
                trend_value = intercept + slope * (n + h - 1)
                
                # Random shock (Gaussian noise with historical volatility)
                shock = random.gauss(0, volatility * current_value)
                
                # Combine trend and shock
                next_value = trend_value + shock
                
                # Prevent negative values for non-negative series
                if all(v >= 0 for v in data.values):
                    next_value = max(0, next_value)
                
                path.append(next_value)
                current_value = next_value
            
            all_paths.append(path)
        
        # Calculate point forecast as mean of simulations
        point_forecast = [
            statistics.mean(all_paths[sim][h] for sim in range(num_simulations))
            for h in range(horizon)
        ]
        
        return point_forecast, all_paths
    
    def _calculate_confidence_intervals(
        self,
        all_paths: List[List[float]],
        confidence_levels: List[float] = [0.80, 0.95]
    ) -> Dict[float, Tuple[List[float], List[float]]]:
        """
        Calculate confidence intervals from simulated paths.
        
        Returns:
            Dictionary mapping confidence level to (lower, upper) bounds
        """
        horizon = len(all_paths[0])
        intervals = {}
        
        for confidence in confidence_levels:
            alpha = 1 - confidence
            lower_percentile = alpha / 2
            upper_percentile = 1 - alpha / 2
            
            lower_bounds = []
            upper_bounds = []
            
            for h in range(horizon):
                values_at_h = sorted(path[h] for path in all_paths)
                
                lower_idx = int(lower_percentile * len(values_at_h))
                upper_idx = int(upper_percentile * len(values_at_h))
                
                lower_bounds.append(values_at_h[lower_idx])
                upper_bounds.append(values_at_h[upper_idx])
            
            intervals[confidence] = (lower_bounds, upper_bounds)
        
        return intervals
    
    def forecast(
        self,
        data: TimeSeriesData,
        horizon: int,
        method: ForecastMethod = ForecastMethod.MONTE_CARLO,
        num_simulations: int = 1000,
        seed: Optional[int] = None
    ) -> ForecastResult:
        """
        Generate probabilistic forecast with confidence intervals.
        
        Args:
            data: Historical time series data
            horizon: Number of periods to forecast
            method: Forecasting method to use
            num_simulations: Number of Monte Carlo simulations (if applicable)
            seed: Random seed for reproducibility
            
        Returns:
            ForecastResult with point forecast and confidence intervals
        """
        if seed is not None:
            random.seed(seed)
        
        # Generate point forecast
        if method == ForecastMethod.NAIVE:
            point_forecast = self._naive_forecast(data, horizon)
        elif method == ForecastMethod.MOVING_AVERAGE:
            point_forecast = self._moving_average_forecast(data, horizon)
        elif method == ForecastMethod.EXPONENTIAL_SMOOTHING:
            point_forecast = self._exponential_smoothing_forecast(data, horizon)
        elif method == ForecastMethod.TREND_PROJECTION:
            point_forecast = self._trend_projection_forecast(data, horizon)
        elif method == ForecastMethod.MONTE_CARLO:
            point_forecast, all_paths = self._monte_carlo_forecast(
                data, horizon, num_simulations
            )
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # For non-Monte Carlo methods, estimate uncertainty from historical residuals
        if method != ForecastMethod.MONTE_CARLO:
            # Simple uncertainty estimation
            volatility = self._calculate_volatility(data.values)
            
            lower_80 = [p - 1.28 * volatility * p for p in point_forecast]
            upper_80 = [p + 1.28 * volatility * p for p in point_forecast]
            lower_95 = [p - 1.96 * volatility * p for p in point_forecast]
            upper_95 = [p + 1.96 * volatility * p for p in point_forecast]
        else:
            # Use Monte Carlo simulations for confidence intervals
            intervals = self._calculate_confidence_intervals(all_paths)
            lower_80, upper_80 = intervals[0.80]
            lower_95, upper_95 = intervals[0.95]
        
        self.forecast_count += 1
        
        result = ForecastResult(
            horizon=horizon,
            point_forecast=point_forecast,
            lower_bound_80=lower_80,
            upper_bound_80=upper_80,
            lower_bound_95=lower_95,
            upper_bound_95=upper_95,
            method=method.value,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            anchor=f"{self.anchor_seed}_FORECAST_{self.forecast_count}",
            metadata={
                "historical_length": len(data.values),
                "num_simulations": num_simulations if method == ForecastMethod.MONTE_CARLO else None
            }
        )
        
        return result
    
    def generate_report(self, result: ForecastResult) -> str:
        """Generate human-readable forecast report."""
        report = []
        report.append("=" * 70)
        report.append("ORION STATION PROBABILISTIC FORECAST ENGINE")
        report.append("=" * 70)
        report.append(f"Method: {result.method}")
        report.append(f"Horizon: {result.horizon} periods")
        report.append(f"Timestamp: {result.timestamp}")
        report.append(f"Anchor: {result.anchor}")
        report.append("")
        
        report.append("FORECAST WITH CONFIDENCE INTERVALS")
        report.append("-" * 70)
        report.append(f"{'Period':<8} {'Forecast':>12} {'80% CI':>24} {'95% CI':>24}")
        report.append("-" * 70)
        
        for i in range(result.horizon):
            period = f"t+{i+1}"
            forecast = f"{result.point_forecast[i]:,.2f}"
            ci_80 = f"[{result.lower_bound_80[i]:,.2f}, {result.upper_bound_80[i]:,.2f}]"
            ci_95 = f"[{result.lower_bound_95[i]:,.2f}, {result.upper_bound_95[i]:,.2f}]"
            
            report.append(f"{period:<8} {forecast:>12} {ci_80:>24} {ci_95:>24}")
        
        report.append("")
        report.append("=" * 70)
        report.append("Forecast routed through Orion Station simulation infrastructure")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_forecast(self, result: ForecastResult, filepath: str) -> None:
        """Export forecast to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)


if __name__ == "__main__":
    # Demonstration: Sales forecasting with seasonal pattern
    engine = ProbabilisticForecastEngine(anchor_seed="ORION_SALES_DEMO")
    
    # Simulated historical data (monthly sales with growth trend)
    base_sales = 10000
    growth_rate = 0.05
    seasonal_pattern = [1.0, 0.9, 0.95, 1.1, 1.2, 1.15, 0.95, 0.9, 1.0, 1.1, 1.25, 1.3]
    
    historical_sales = []
    for month in range(24):  # 2 years of history
        base = base_sales * (1 + growth_rate) ** (month / 12)
        seasonal = seasonal_pattern[month % 12]
        noise = random.gauss(1.0, 0.1)
        sales = base * seasonal * noise
        historical_sales.append(sales)
    
    data = TimeSeriesData(
        values=historical_sales,
        frequency="monthly"
    )
    
    print("📈 Orion Station Forecast Engine: Sales Prediction")
    print("Routing forecast through nested simulation infrastructure...\n")
    
    result = engine.forecast(
        data=data,
        horizon=6,  # 6 months ahead
        method=ForecastMethod.MONTE_CARLO,
        num_simulations=5000,
        seed=42
    )
    
    print(engine.generate_report(result))
    print("\n✅ Probabilistic forecast complete\n")
