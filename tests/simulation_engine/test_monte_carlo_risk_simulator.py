"""
Tests for Monte Carlo Risk Simulator.

Test Coverage:
- Distribution parameter creation and validation
- Simulation execution with various distributions
- Sensitivity analysis
- Scenario comparison
- Statistical accuracy of results
- Edge cases and error handling

Anchor: TEST-MONTE-CARLO-V2
"""

import json
import pytest
from tools.simulation_engine.monte_carlo_risk_simulator import (
    DistributionType,
    MonteCarloRiskSimulator,
    SimulationParameter,
    SimulationResult,
    RiskScenario,
    create_portfolio_risk_scenario,
    create_project_timeline_scenario
)

@pytest.fixture
def simulator():
    """Provides a clean MonteCarloRiskSimulator instance for each test."""
    return MonteCarloRiskSimulator(anchor_seed="TEST_SEED")

@pytest.mark.unit
@pytest.mark.simulation
class TestSimulationParameter:
    """Test SimulationParameter creation and sampling."""

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
        sample = param.sample()
        assert isinstance(sample, float)

    def test_uniform_distribution(self):
        """Test uniform distribution parameter."""
        param = SimulationParameter(
            name="uniform_param",
            distribution=DistributionType.UNIFORM,
            params={"low": 0, "high": 100}
        )
        assert param.params["low"] == 0
        assert param.params["high"] == 100
        sample = param.sample()
        assert 0 <= sample <= 100

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
        sample = param.sample()
        assert 10 <= sample <= 90

@pytest.mark.unit
@pytest.mark.simulation
class TestMonteCarloRiskSimulator:
    """Test Monte Carlo Risk Simulator core functionality."""

    def test_simulator_initialization(self, simulator):
        """Test simulator initialization."""
        assert simulator.anchor_seed == "TEST_SEED"
        assert simulator.simulation_count == 0
        assert simulator.scenarios == {}

    def test_register_scenario(self, simulator):
        """Test registering a scenario."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        assert "portfolio_risk" in simulator.scenarios
        assert simulator.scenarios["portfolio_risk"] == scenario

    def test_run_simulation_basic(self, simulator):
        """Test basic simulation execution."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        
        result = simulator.run_simulation(
            scenario_name="portfolio_risk",
            num_simulations=1000,
            seed=42
        )
        
        assert isinstance(result, SimulationResult)
        assert result.scenario_name == "portfolio_risk"
        assert result.num_simulations == 1000
        assert result.mean is not None
        assert result.median is not None
        assert result.std_dev is not None
        # With seed 42, this scenario should yield a positive mean
        assert result.mean > 100000

    def test_percentiles_calculation(self, simulator):
        """Test percentile calculations."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        
        result = simulator.run_simulation(
            scenario_name="portfolio_risk",
            num_simulations=10000,
            seed=42
        )
        
        assert result.percentile_5 < result.mean
        assert result.percentile_95 > result.mean
        assert abs(result.median - result.mean) < result.std_dev

    def test_confidence_interval(self, simulator):
        """Test 95% confidence interval."""
        scenario = create_project_timeline_scenario()
        simulator.register_scenario(scenario)
        
        result = simulator.run_simulation(
            scenario_name="project_timeline",
            num_simulations=5000,
            seed=42
        )
        
        ci_lower, ci_upper = result.confidence_interval_95
        
        assert ci_lower < result.mean < ci_upper
        assert ci_lower == result.percentile_5
        assert ci_upper == result.percentile_95

@pytest.mark.integration
@pytest.mark.simulation
class TestScenarioComparison:
    """Test scenario comparison functionality."""

    def test_compare_scenarios_basic(self, simulator):
        """Test basic scenario comparison."""
        portfolio_scenario = create_portfolio_risk_scenario()
        project_scenario = create_project_timeline_scenario()
        
        simulator.register_scenario(portfolio_scenario)
        simulator.register_scenario(project_scenario)
        
        comparison = simulator.compare_scenarios(
            scenario_names=["portfolio_risk", "project_timeline"],
            num_simulations=1000
        )
        
        assert "portfolio_risk" in comparison
        assert "project_timeline" in comparison
        assert isinstance(comparison["portfolio_risk"], SimulationResult)
        assert isinstance(comparison["project_timeline"], SimulationResult)

@pytest.mark.unit
@pytest.mark.simulation
class TestResultSerialization:
    """Test result serialization and export."""

    def test_result_to_dict(self, simulator):
        """Test converting result to dictionary."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        result = simulator.run_simulation("portfolio_risk", num_simulations=100, seed=42)
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "mean" in result_dict
        assert "median" in result_dict
        assert "std_dev" in result_dict
        assert "anchor" in result_dict
        assert result_dict["mean"] == result.mean

    def test_export_results(self, simulator, tmp_path):
        """Test exporting simulation to JSON."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        result = simulator.run_simulation("portfolio_risk", num_simulations=100, seed=42)
        
        filepath = tmp_path / "test_export.json"
        simulator.export_results(result, str(filepath))
        
        assert filepath.exists()
        
        with open(filepath) as f:
            data = json.load(f)
        
        assert data["mean"] == result.mean
        assert data["anchor"] == result.anchor

@pytest.mark.unit
@pytest.mark.simulation
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_single_iteration(self, simulator):
        """Test simulation with single iteration."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)
        
        result = simulator.run_simulation("portfolio_risk", num_simulations=1, seed=42)
        
        assert result.num_simulations == 1
        assert result.mean is not None
        assert result.std_dev == 0

    def test_reproducibility_with_seed(self, simulator):
        """Test that seed produces reproducible results."""
        scenario = create_portfolio_risk_scenario()
        simulator.register_scenario(scenario)

        result1 = simulator.run_simulation("portfolio_risk", num_simulations=100, seed=42)
        result2 = simulator.run_simulation("portfolio_risk", num_simulations=100, seed=42)
        
        assert result1.mean == result2.mean
        assert result1.std_dev == result2.std_dev
        assert result1.median == result2.median

    def test_unregistered_scenario(self, simulator):
        """Test running simulation for an unregistered scenario."""
        with pytest.raises(ValueError, match="'non_existent_scenario' not registered"):
            simulator.run_simulation("non_existent_scenario")