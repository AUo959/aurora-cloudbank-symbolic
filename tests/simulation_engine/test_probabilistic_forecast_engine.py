"""
Tests for Probabilistic Forecast Engine.

Test Coverage:
- Time series data creation and validation
- Trend detection (linear)
- Volatility calculation
- Forecast methods (naive, moving average, trend projection, exponential smoothing, Monte Carlo)
- Confidence interval calculation
- Forecast accuracy
- Edge cases and error handling

Anchor: TEST-FORECAST-ENGINE-V1
"""

import pytest
import json
from tools.simulation_engine.probabilistic_forecast_engine import (
    ProbabilisticForecastEngine,
    TimeSeriesData,
    ForecastResult,
    ForecastMethod
)


@pytest.mark.unit
@pytest.mark.simulation
class TestTimeSeriesData:
    """Test TimeSeriesData creation and validation."""
    
    def test_basic_creation(self):
        """Test basic time series creation."""
        data = TimeSeriesData(
            values=[10, 15, 20, 25, 30],
            frequency="daily"
        )
        assert len(data.values) == 5
        assert data.frequency == "daily"
        assert data.timestamps is None
    
    def test_with_timestamps(self):
        """Test time series with timestamps."""
        timestamps = ["2024-01-01", "2024-01-02", "2024-01-03"]
        values = [100, 110, 105]
        
        data = TimeSeriesData(
            values=values,
            timestamps=timestamps,
            frequency="daily"
        )
        
        assert data.timestamps == timestamps
        assert len(data.values) == 3
    
    def test_mismatched_length_raises_error(self):
        """Test that mismatched timestamps/values raises error."""
        with pytest.raises(ValueError):
            TimeSeriesData(
                values=[10, 20, 30],
                timestamps=["2024-01-01", "2024-01-02"]  # Only 2 timestamps
            )


@pytest.mark.unit
@pytest.mark.simulation
class TestForecastEngine:
    """Test Probabilistic Forecast Engine core functionality."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = ProbabilisticForecastEngine(anchor_seed="TEST_SEED")
        assert engine.anchor_seed == "TEST_SEED"
        assert engine.forecast_count == 0
    
    def test_detect_trend_upward(self):
        """Test trend detection for upward trend."""
        engine = ProbabilisticForecastEngine()
        
        # Clear upward trend
        values = [10, 20, 30, 40, 50]
        slope, intercept = engine._detect_trend(values)
        
        assert slope > 0  # Positive slope
        assert intercept > 0
    
    def test_detect_trend_downward(self):
        """Test trend detection for downward trend."""
        engine = ProbabilisticForecastEngine()
        
        # Clear downward trend
        values = [50, 40, 30, 20, 10]
        slope, intercept = engine._detect_trend(values)
        
        assert slope < 0  # Negative slope
    
    def test_detect_trend_flat(self):
        """Test trend detection for flat series."""
        engine = ProbabilisticForecastEngine()
        
        # Flat series
        values = [100, 100, 100, 100, 100]
        slope, intercept = engine._detect_trend(values)
        
        assert abs(slope) < 0.01  # Near-zero slope
        assert abs(intercept - 100) < 1  # Intercept near mean
    
    def test_calculate_volatility(self):
        """Test volatility calculation."""
        engine = ProbabilisticForecastEngine()
        
        # Low volatility
        stable_values = [100, 101, 100, 101, 100]
        stable_vol = engine._calculate_volatility(stable_values)
        
        # High volatility
        volatile_values = [100, 120, 90, 130, 80]
        volatile_vol = engine._calculate_volatility(volatile_values)
        
        assert volatile_vol > stable_vol


@pytest.mark.unit
@pytest.mark.simulation
class TestNaiveForecast:
    """Test naive forecasting method."""
    
    def test_naive_forecast_basic(self):
        """Test basic naive forecast."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[10, 15, 20, 25, 30])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.NAIVE,
            seed=42
        )
        
        assert isinstance(result, ForecastResult)
        assert result.horizon == 3
        # Naive forecast should repeat last value
        assert all(v == 30 for v in result.point_forecast)


@pytest.mark.unit
@pytest.mark.simulation
class TestMovingAverageForecast:
    """Test moving average forecasting method."""
    
    def test_moving_average_basic(self):
        """Test basic moving average forecast."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[10, 20, 30, 40, 50])
        
        result = engine.forecast(
            data=data,
            horizon=2,
            method=ForecastMethod.MOVING_AVERAGE,
            seed=42
        )
        
        assert result.horizon == 2
        # MA should be around average of recent values (30-50)
        assert all(30 <= v <= 50 for v in result.point_forecast)


@pytest.mark.unit
@pytest.mark.simulation
class TestTrendProjectionForecast:
    """Test trend projection forecasting method."""
    
    def test_trend_projection_upward(self):
        """Test trend projection with upward trend."""
        engine = ProbabilisticForecastEngine()
        
        # Clear upward trend
        data = TimeSeriesData(values=[10, 20, 30, 40, 50])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.TREND_PROJECTION,
            seed=42
        )
        
        # Forecast should continue upward trend
        assert result.point_forecast[0] > 50
        assert result.point_forecast[1] > result.point_forecast[0]
        assert result.point_forecast[2] > result.point_forecast[1]


@pytest.mark.unit
@pytest.mark.simulation
class TestExponentialSmoothingForecast:
    """Test exponential smoothing forecasting method."""
    
    def test_exponential_smoothing_basic(self):
        """Test basic exponential smoothing forecast."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[100, 110, 105, 115, 120])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.EXPONENTIAL_SMOOTHING,
            seed=42
        )
        
        assert result.horizon == 3
        # Forecast should be reasonable given the data
        assert all(100 <= v <= 150 for v in result.point_forecast)


@pytest.mark.integration
@pytest.mark.simulation
class TestMonteCarloForecast:
    """Test Monte Carlo forecasting method."""
    
    def test_monte_carlo_basic(self):
        """Test basic Monte Carlo forecast."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[100, 105, 110, 115, 120])
        
        result = engine.forecast(
            data=data,
            horizon=5,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=1000,
            seed=42
        )
        
        assert result.horizon == 5
        assert len(result.point_forecast) == 5
        # Forecast should follow trend
        assert result.point_forecast[0] > 120
    
    def test_monte_carlo_confidence_intervals(self):
        """Test Monte Carlo confidence interval calculation."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[50, 55, 60, 65, 70])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=5000,
            seed=42
        )
        
        # Check that confidence intervals are properly ordered
        for i in range(result.horizon):
            assert result.lower_bound_95[i] < result.lower_bound_80[i]
            assert result.lower_bound_80[i] < result.point_forecast[i]
            assert result.point_forecast[i] < result.upper_bound_80[i]
            assert result.upper_bound_80[i] < result.upper_bound_95[i]
    
    def test_monte_carlo_with_high_volatility(self):
        """Test Monte Carlo with high volatility data."""
        engine = ProbabilisticForecastEngine()
        
        # High volatility series
        data = TimeSeriesData(values=[100, 120, 90, 130, 80, 140])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=2000,
            seed=42
        )
        
        # Wide confidence intervals expected with high volatility
        ci_width = result.upper_bound_95[0] - result.lower_bound_95[0]
        assert ci_width > 50  # Significant uncertainty


@pytest.mark.integration
@pytest.mark.simulation
class TestForecastAccuracy:
    """Test forecast accuracy on synthetic data."""
    
    def test_linear_trend_accuracy(self):
        """Test forecast accuracy on perfect linear trend."""
        engine = ProbabilisticForecastEngine()
        
        # Perfect linear trend: y = 10 + 5*x
        values = [10 + 5*i for i in range(10)]
        data = TimeSeriesData(values=values)
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.TREND_PROJECTION,
            seed=42
        )
        
        # Forecast should be very close to actual trend
        expected_1 = 10 + 5*10  # = 60
        expected_2 = 10 + 5*11  # = 65
        expected_3 = 10 + 5*12  # = 70
        
        assert abs(result.point_forecast[0] - expected_1) < 1
        assert abs(result.point_forecast[1] - expected_2) < 1
        assert abs(result.point_forecast[2] - expected_3) < 1


@pytest.mark.unit
@pytest.mark.simulation
class TestResultSerialization:
    """Test result serialization and export."""
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[100, 110, 120, 130])
        
        result = engine.forecast(
            data=data,
            horizon=2,
            method=ForecastMethod.NAIVE,
            seed=42
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "point_forecast" in result_dict
        assert "lower_bound_80" in result_dict
        assert "upper_bound_95" in result_dict
        assert "anchor" in result_dict
    
    def test_export_forecast(self, tmp_path):
        """Test exporting forecast to JSON."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[50, 55, 60, 65, 70])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=100,
            seed=42
        )
        
        filepath = tmp_path / "test_forecast.json"
        engine.export_forecast(result, str(filepath))
        
        assert filepath.exists()
        
        with open(filepath) as f:
            data = json.load(f)
        
        assert data["horizon"] == result.horizon
        assert data["method"] == result.method


@pytest.mark.unit
@pytest.mark.simulation
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_value_series(self):
        """Test forecast with single historical value."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[100])
        
        result = engine.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.NAIVE,
            seed=42
        )
        
        # Should propagate the single value
        assert all(v == 100 for v in result.point_forecast)
    
    def test_short_history(self):
        """Test forecast with very short history."""
        engine = ProbabilisticForecastEngine()
        
        data = TimeSeriesData(values=[100, 110])
        
        result = engine.forecast(
            data=data,
            horizon=2,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=500,
            seed=42
        )
        
        assert len(result.point_forecast) == 2
        # Should still produce valid forecast
        assert all(v > 0 for v in result.point_forecast)
    
    def test_reproducibility_with_seed(self):
        """Test that seed produces reproducible results."""
        data = TimeSeriesData(values=[100, 105, 110, 115, 120])
        
        engine1 = ProbabilisticForecastEngine()
        result1 = engine1.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=1000,
            seed=42
        )
        
        engine2 = ProbabilisticForecastEngine()
        result2 = engine2.forecast(
            data=data,
            horizon=3,
            method=ForecastMethod.MONTE_CARLO,
            num_simulations=1000,
            seed=42
        )
        
        # Results should be identical with same seed
        assert result1.point_forecast == result2.point_forecast
        assert result1.lower_bound_95 == result2.lower_bound_95
        assert result1.upper_bound_95 == result2.upper_bound_95
    
    def test_negative_values_allowed(self):
        """Test forecast can handle negative values."""
        engine = ProbabilisticForecastEngine()
        
        # Series with negative values
        data = TimeSeriesData(values=[-10, -5, 0, 5, 10])
        
        result = engine.forecast(
            data=data,
            horizon=2,
            method=ForecastMethod.TREND_PROJECTION,
            seed=42
        )
        
        # Should continue upward trend into positive
        assert result.point_forecast[0] > 10
