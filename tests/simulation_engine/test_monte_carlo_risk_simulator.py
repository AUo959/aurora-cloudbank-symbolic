"""
Tests for Monte Carlo Risk Simulator.

Test Coverage:
- Distribution parameter creation and validation
- Simulation execution with various distributions
- Sensitivity analysis
- Scenario comparison
- Statistical accuracy of results
- Edge cases and error handling

Anchor: TEST-MONTE-CARLO-V1
"""

import json

import pytest

from tools.simulation_engine.monte_carlo_risk_simulator import (
    DistributionType,
    MonteCarloRiskSimulator,
    RiskScenario,
    SimulationParameter,
    SimulationResult,
)


@pytest.mark.unit
@pytest.mark.simulation
class TestSimulationParameter:
    """Test SimulationParameter creation and validation."""
    
    def test_normal_distribution(self):
        """Test normal distribution parameter."""
        param = SimulationParameter(
            name="test_param",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        assert param.name == "test_param"
        assert param.distribution == DistributionType.NORMAL
        assert param.params["mean"] == 100
        assert param.params["std"] == 10
    
    def test_uniform_distribution(self):
        """Test uniform distribution parameter."""
        param = SimulationParameter(
            name="uniform_param",
            distribution=DistributionType.UNIFORM,
            params={"low": 0, "high": 100}
        )
        assert param.params["low"] == 0
        assert param.params["high"] == 100
    
    def test_triangular_distribution(self):
        """Test triangular distribution parameter."""
        param = SimulationParameter(
            name="tri_param",
            distribution=DistributionType.TRIANGULAR,
            params={"low": 10, "mode": 50, "high": 90}
        )
        assert param.params["low"] == 10
        assert param.params["mode"] == 50
        assert param.params["high"] == 90


@pytest.mark.unit
@pytest.mark.unit
@pytest.mark.simulation
class TestMonteCarloRiskSimulator:
    """Test Monte Carlo Risk Simulator core functionality."""
    
    def test_simulator_initialization(self):
        """Test simulator initialization."""
        simulator = MonteCarloRiskSimulator(
            name="Test Simulator",
            anchor_seed="TEST_SEED"
        )
        assert simulator.name == "Test Simulator"
        assert simulator.anchor_seed == "TEST_SEED"
        assert simulator.simulation_count == 0
    
    def test_register_scenario(self):
        """Test registering scenarios to simulator."""
        simulator = MonteCarloRiskSimulator(name="Test")
        
        param = SimulationParameter(
            name="revenue",
            distribution=DistributionType.NORMAL,
            params={"mean": 1000, "std": 100}
        )
        
        scenario = RiskScenario(
            name="test_scenario",
            parameters=[param],
            outcome_function=lambda p: p["revenue"]
        )
        
        simulator.register_scenario(scenario)
        assert len(simulator.scenarios) == 1
        assert "test_scenario" in simulator.scenarios
    
    def test_run_simulation_basic(self):
        """Test basic simulation execution."""
        simulator = MonteCarloRiskSimulator(name="Basic Test")
        
        # Simple simulation: revenue - cost
        revenue_param = SimulationParameter(
            name="revenue",
            distribution=DistributionType.NORMAL,
            params={"mean": 10000, "std": 1000}
        )
        
        cost_param = SimulationParameter(
            name="cost",
            distribution=DistributionType.NORMAL,
            params={"mean": 7000, "std": 500}
        )
        
        def profit_model(params):
            return params["revenue"] - params["cost"]
        
        scenario = RiskScenario(
            name="profit_scenario",
            parameters=[revenue_param, cost_param],
            outcome_function=profit_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="profit_scenario",
            num_simulations=1000,
            seed=42
        )
        
        assert isinstance(result, SimulationResult)
        assert result.num_simulations == 1000
        assert result.mean is not None
        assert result.median is not None
        assert result.std_dev is not None
        # Profit should be positive on average
        assert result.mean > 0
        assert result.median > 0
    
    def test_run_simulation_with_uniform(self):
        """Test simulation with uniform distribution."""
        simulator = MonteCarloRiskSimulator(name="Uniform Test")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.UNIFORM,
            params={"low": 50, "high": 150}
        )
        
        def simple_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="uniform_scenario",
            parameters=[value_param],
            outcome_function=simple_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="uniform_scenario",
            num_simulations=1000,
            seed=42
        )
        
        assert result.num_simulations == 1000
        # Mean should be close to 100 (midpoint of 50-150)
        assert 90 <= result.mean <= 110
    
    def test_percentiles_calculation(self):
        """Test percentile calculations."""
        simulator = MonteCarloRiskSimulator(name="Percentile Test")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="percentile_scenario",
            parameters=[value_param],
            outcome_function=identity_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="percentile_scenario",
            num_simulations=10000,
            seed=42
        )
        
        # P5 should be less than mean
        assert result.percentile_5 < result.mean
        # P95 should be greater than mean
        assert result.percentile_95 > result.mean
        # Median should be close to mean for normal distribution
        assert abs(result.median - result.mean) < 2
    
    def test_confidence_interval(self):
        """Test 95% confidence interval."""
        simulator = MonteCarloRiskSimulator(name="CI Test")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 50, "std": 5}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="ci_scenario",
            parameters=[value_param],
            outcome_function=identity_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="ci_scenario",
            num_simulations=5000,
            seed=42
        )
        
        ci_lower, ci_upper = result.confidence_interval_95
        
        # CI should contain the mean
        assert ci_lower < result.mean < ci_upper
        # CI width should be reasonable (roughly 4 * std_dev for 95%)
        ci_width = ci_upper - ci_lower
        assert 15 < ci_width < 25  # Roughly 4 * 5


@pytest.mark.integration
@pytest.mark.simulation
class TestSensitivityAnalysis:
    """Test sensitivity analysis functionality."""
    
    def test_sensitivity_analysis_basic(self):
        """Test basic sensitivity analysis."""
        simulator = MonteCarloRiskSimulator(name="Sensitivity Test")
        
        price_param = SimulationParameter(
            name="price",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        
        volume_param = SimulationParameter(
            name="volume",
            distribution=DistributionType.NORMAL,
            params={"mean": 1000, "std": 100}
        )
        
        def revenue_model(params):
            return params["price"] * params["volume"]
        
        scenario = RiskScenario(
            name="revenue_scenario",
            parameters=[price_param, volume_param],
            outcome_function=revenue_model
        )
        
        simulator.register_scenario(scenario)
        sensitivity = simulator.run_sensitivity_analysis(
            scenario_name="revenue_scenario",
            num_simulations=500,
            parameter_variations=10
        )
        
        assert "price" in sensitivity
        assert "volume" in sensitivity
        
        # Each parameter should have outcome samples
        assert len(sensitivity["price"]) > 0
        assert len(sensitivity["volume"]) > 0
        
        # Results should be lists of floats
        assert isinstance(sensitivity["price"], list)
        assert isinstance(sensitivity["volume"], list)


@pytest.mark.integration
@pytest.mark.simulation
class TestScenarioComparison:
    """Test scenario comparison functionality."""
    
    def test_compare_scenarios_basic(self):
        """Test basic scenario comparison."""
        simulator = MonteCarloRiskSimulator(name="Comparison")
        
        # Optimistic scenario
        optimistic_param = SimulationParameter(
            name="revenue",
            distribution=DistributionType.NORMAL,
            params={"mean": 15000, "std": 1000}
        )
        
        optimistic_scenario = RiskScenario(
            name="Optimistic",
            parameters=[optimistic_param],
            outcome_function=lambda p: p["revenue"]
        )
        
        # Pessimistic scenario
        pessimistic_param = SimulationParameter(
            name="revenue",
            distribution=DistributionType.NORMAL,
            params={"mean": 8000, "std": 2000}
        )
        
        pessimistic_scenario = RiskScenario(
            name="Pessimistic",
            parameters=[pessimistic_param],
            outcome_function=lambda p: p["revenue"]
        )
        
        simulator.register_scenario(optimistic_scenario)
        simulator.register_scenario(pessimistic_scenario)
        
        opt_result = simulator.run_simulation("Optimistic", num_simulations=1000, seed=42)
        pess_result = simulator.run_simulation("Pessimistic", num_simulations=1000, seed=42)
        
        # Optimistic should have higher mean than pessimistic
        assert opt_result.mean > pess_result.mean


@pytest.mark.unit
@pytest.mark.simulation
class TestResultSerialization:
    """Test result serialization and export."""
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        simulator = MonteCarloRiskSimulator(name="Export Test")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.UNIFORM,
            params={"low": 10, "high": 20}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="dict_scenario",
            parameters=[value_param],
            outcome_function=identity_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="dict_scenario",
            num_simulations=100,
            seed=42
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "mean" in result_dict
        assert "median" in result_dict
        assert "std_dev" in result_dict
        assert "anchor" in result_dict
    
    def test_export_simulation(self, tmp_path):
        """Test exporting simulation to JSON."""
        simulator = MonteCarloRiskSimulator(name="Export Test")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 50, "std": 5}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="export_scenario",
            parameters=[value_param],
            outcome_function=identity_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="export_scenario",
            num_simulations=100,
            seed=42
        )
        
        filepath = tmp_path / "test_export.json"
        
        # Export manually using to_dict
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f)
        
        assert filepath.exists()
        
        # Load and verify
        with open(filepath) as f:
            data = json.load(f)
        
        assert data["mean"] == result.mean
        assert data["anchor"] == result.anchor


@pytest.mark.unit
@pytest.mark.simulation
class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_single_iteration(self):
        """Test simulation with single iteration."""
        simulator = MonteCarloRiskSimulator(name="Single Iter")
        
        value_param = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario = RiskScenario(
            name="single_iter_scenario",
            parameters=[value_param],
            outcome_function=identity_model
        )
        
        simulator.register_scenario(scenario)
        result = simulator.run_simulation(
            scenario_name="single_iter_scenario",
            num_simulations=1,
            seed=42
        )
        
        assert result.num_simulations == 1
        assert result.mean is not None
        # With single iteration, std_dev should be 0
        assert result.std_dev == 0
    
    def test_reproducibility_with_seed(self):
        """Test that seed produces reproducible results."""
        simulator1 = MonteCarloRiskSimulator(name="Test 1")
        simulator2 = MonteCarloRiskSimulator(name="Test 2")
        
        value_param1 = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        
        value_param2 = SimulationParameter(
            name="value",
            distribution=DistributionType.NORMAL,
            params={"mean": 100, "std": 10}
        )
        
        def identity_model(params):
            return params["value"]
        
        scenario1 = RiskScenario(
            name="repro_scenario",
            parameters=[value_param1],
            outcome_function=identity_model
        )
        
        scenario2 = RiskScenario(
            name="repro_scenario",
            parameters=[value_param2],
            outcome_function=identity_model
        )
        
        simulator1.register_scenario(scenario1)
        simulator2.register_scenario(scenario2)
        
        result1 = simulator1.run_simulation(
            scenario_name="repro_scenario",
            num_simulations=100,
            seed=42
        )
        
        result2 = simulator2.run_simulation(
            scenario_name="repro_scenario",
            num_simulations=100,
            seed=42
        )
        
        # Results should be identical with same seed
        assert result1.mean == result2.mean
        assert result1.std_dev == result2.std_dev
        assert result1.median == result2.median
