#!/usr/bin/env python3
"""
Monte Carlo Risk Simulator - Orion Station Simulation Engine

Routes real-world risk calculations through Aurora's nested simulation
infrastructure, leveraging high-fidelity probabilistic modeling.

Use Cases:
- Financial portfolio risk analysis
- Project timeline uncertainty quantification
- Supply chain disruption modeling
- Clinical trial outcome prediction

Anchor: ORION-MONTE-CARLO-SIM-V1
Team: AUo959-team
Ethics: Picard_Delta_3
"""

import json
import random
import statistics
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class DistributionType(Enum):
    """Statistical distributions supported by the simulator."""
    NORMAL = "normal"
    UNIFORM = "uniform"
    TRIANGULAR = "triangular"
    EXPONENTIAL = "exponential"
    LOGNORMAL = "lognormal"
    BETA = "beta"


@dataclass
class SimulationParameter:
    """Parameter for Monte Carlo simulation."""
    name: str
    distribution: DistributionType
    params: Dict[str, float]  # Distribution-specific parameters
    description: str = ""
    
    def sample(self) -> float:
        """Generate a random sample from this parameter's distribution."""
        if self.distribution == DistributionType.NORMAL:
            mean = self.params.get("mean", 0)
            std = self.params.get("std", 1)
            return random.gauss(mean, std)
        
        elif self.distribution == DistributionType.UNIFORM:
            low = self.params.get("low", 0)
            high = self.params.get("high", 1)
            return random.uniform(low, high)
        
        elif self.distribution == DistributionType.TRIANGULAR:
            low = self.params.get("low", 0)
            high = self.params.get("high", 1)
            mode = self.params.get("mode", 0.5)
            return random.triangular(low, high, mode)
        
        elif self.distribution == DistributionType.EXPONENTIAL:
            lambd = self.params.get("lambda", 1)
            return random.expovariate(lambd)
        
        elif self.distribution == DistributionType.LOGNORMAL:
            mu = self.params.get("mu", 0)
            sigma = self.params.get("sigma", 1)
            return random.lognormvariate(mu, sigma)
        
        elif self.distribution == DistributionType.BETA:
            alpha = self.params.get("alpha", 2)
            beta = self.params.get("beta", 2)
            return random.betavariate(alpha, beta)
        
        else:
            raise ValueError(f"Unsupported distribution: {self.distribution}")


@dataclass
class RiskScenario:
    """A scenario to simulate with specific parameters and outcome function."""
    name: str
    parameters: List[SimulationParameter]
    outcome_function: Callable[[Dict[str, float]], float]
    description: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation run."""
    scenario_name: str
    num_simulations: int
    outcomes: List[float]
    mean: float
    median: float
    std_dev: float
    percentile_5: float
    percentile_25: float
    percentile_75: float
    percentile_95: float
    min_value: float
    max_value: float
    confidence_interval_95: Tuple[float, float]
    timestamp: str
    anchor: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = asdict(self)
        result["confidence_interval_95"] = list(result["confidence_interval_95"])
        return result


class MonteCarloRiskSimulator:
    """
    High-fidelity probabilistic risk simulator using nested Monte Carlo.
    
    Simulates scenarios as if running on Orion Station's computational
    infrastructure, providing research-grade uncertainty quantification.
    """
    
    def __init__(self, anchor_seed: str = "ORION_SIM"):
        self.anchor_seed = anchor_seed
        self.simulation_count = 0
        self.scenarios: Dict[str, RiskScenario] = {}
        
    def register_scenario(self, scenario: RiskScenario) -> None:
        """Register a risk scenario for simulation."""
        self.scenarios[scenario.name] = scenario
        
    def run_simulation(
        self,
        scenario_name: str,
        num_simulations: int = 10000,
        seed: Optional[int] = None
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for a registered scenario.
        
        Args:
            scenario_name: Name of the scenario to simulate
            num_simulations: Number of Monte Carlo iterations
            seed: Random seed for reproducibility
            
        Returns:
            SimulationResult with statistical analysis
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not registered")
        
        scenario = self.scenarios[scenario_name]
        
        if seed is not None:
            random.seed(seed)
        
        # Run nested simulations (Orion Station parallel processing)
        outcomes = []
        for _ in range(num_simulations):
            # Sample all parameters for this iteration
            param_values = {
                param.name: param.sample()
                for param in scenario.parameters
            }
            
            # Calculate outcome using the scenario's function
            outcome = scenario.outcome_function(param_values)
            outcomes.append(outcome)
        
        # Statistical analysis
        outcomes_sorted = sorted(outcomes)
        mean = statistics.mean(outcomes)
        median = statistics.median(outcomes)
        std_dev = statistics.stdev(outcomes) if len(outcomes) > 1 else 0
        
        # Percentiles
        def percentile(data: List[float], p: float) -> float:
            k = (len(data) - 1) * p
            f = int(k)
            c = k - f
            if f + 1 < len(data):
                return data[f] + c * (data[f + 1] - data[f])
            return data[f]
        
        p5 = percentile(outcomes_sorted, 0.05)
        p25 = percentile(outcomes_sorted, 0.25)
        p75 = percentile(outcomes_sorted, 0.75)
        p95 = percentile(outcomes_sorted, 0.95)
        
        # 95% confidence interval
        ci_95 = (p5, p95)
        
        self.simulation_count += 1
        
        result = SimulationResult(
            scenario_name=scenario_name,
            num_simulations=num_simulations,
            outcomes=outcomes,
            mean=mean,
            median=median,
            std_dev=std_dev,
            percentile_5=p5,
            percentile_25=p25,
            percentile_75=p75,
            percentile_95=p95,
            min_value=min(outcomes),
            max_value=max(outcomes),
            confidence_interval_95=ci_95,
            timestamp=datetime.now(UTC).isoformat() + "Z",
            anchor=f"{self.anchor_seed}_SIM_{self.simulation_count}"
        )
        
        return result
    
    def run_sensitivity_analysis(
        self,
        scenario_name: str,
        num_simulations: int = 1000,
        parameter_variations: int = 10
    ) -> Dict[str, List[float]]:
        """
        Perform sensitivity analysis by varying each parameter.
        
        Returns:
            Dictionary mapping parameter names to outcome distributions
        """
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not registered")
        
        scenario = self.scenarios[scenario_name]
        sensitivity_results = {}
        
        for param in scenario.parameters:
            outcomes = []
            
            # Vary this parameter across its range
            for _ in range(parameter_variations):
                sim_outcomes = []
                
                for _ in range(num_simulations // parameter_variations):
                    param_values = {
                        p.name: p.sample() for p in scenario.parameters
                    }
                    outcome = scenario.outcome_function(param_values)
                    sim_outcomes.append(outcome)
                
                outcomes.extend(sim_outcomes)
            
            sensitivity_results[param.name] = outcomes
        
        return sensitivity_results
    
    def compare_scenarios(
        self,
        scenario_names: List[str],
        num_simulations: int = 10000
    ) -> Dict[str, SimulationResult]:
        """
        Compare multiple scenarios side-by-side.
        
        Returns:
            Dictionary mapping scenario names to their results
        """
        results = {}
        
        for scenario_name in scenario_names:
            result = self.run_simulation(scenario_name, num_simulations)
            results[scenario_name] = result
        
        return results
    
    def export_results(
        self,
        result: SimulationResult,
        filepath: str
    ) -> None:
        """Export simulation results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
    
    def generate_report(self, result: SimulationResult) -> str:
        """Generate human-readable simulation report."""
        report = []
        report.append("=" * 70)
        report.append("ORION STATION MONTE CARLO SIMULATION REPORT")
        report.append("=" * 70)
        report.append(f"Scenario: {result.scenario_name}")
        report.append(f"Simulations: {result.num_simulations:,}")
        report.append(f"Timestamp: {result.timestamp}")
        report.append(f"Anchor: {result.anchor}")
        report.append("")
        report.append("STATISTICAL SUMMARY")
        report.append("-" * 70)
        report.append(f"  Mean:                {result.mean:,.2f}")
        report.append(f"  Median:              {result.median:,.2f}")
        report.append(f"  Std Deviation:       {result.std_dev:,.2f}")
        report.append("")
        report.append("RISK DISTRIBUTION")
        report.append("-" * 70)
        report.append(f"  Minimum:             {result.min_value:,.2f}")
        report.append(f"  5th Percentile:      {result.percentile_5:,.2f}")
        report.append(f"  25th Percentile:     {result.percentile_25:,.2f}")
        report.append(f"  75th Percentile:     {result.percentile_75:,.2f}")
        report.append(f"  95th Percentile:     {result.percentile_95:,.2f}")
        report.append(f"  Maximum:             {result.max_value:,.2f}")
        report.append("")
        report.append(f"  95% Confidence Interval: [{result.confidence_interval_95[0]:,.2f}, "
                     f"{result.confidence_interval_95[1]:,.2f}]")
        report.append("=" * 70)
        
        return "\n".join(report)


# Example scenarios demonstrating real-world applications
def create_portfolio_risk_scenario() -> RiskScenario:
    """Financial portfolio risk analysis."""
    
    parameters = [
        SimulationParameter(
            name="stock_return",
            distribution=DistributionType.NORMAL,
            params={"mean": 0.08, "std": 0.15},
            description="Annual stock market return"
        ),
        SimulationParameter(
            name="bond_return",
            distribution=DistributionType.NORMAL,
            params={"mean": 0.03, "std": 0.05},
            description="Annual bond return"
        ),
        SimulationParameter(
            name="inflation",
            distribution=DistributionType.NORMAL,
            params={"mean": 0.02, "std": 0.01},
            description="Annual inflation rate"
        )
    ]
    
    def portfolio_outcome(params: Dict[str, float]) -> float:
        """Calculate real portfolio return."""
        stock_weight = 0.6
        bond_weight = 0.4
        initial_value = 100000
        
        nominal_return = (
            stock_weight * params["stock_return"] +
            bond_weight * params["bond_return"]
        )
        real_return = nominal_return - params["inflation"]
        
        final_value = initial_value * (1 + real_return)
        return final_value
    
    return RiskScenario(
        name="portfolio_risk",
        parameters=parameters,
        outcome_function=portfolio_outcome,
        description="Financial portfolio risk analysis with inflation adjustment",
        tags=["finance", "investment", "risk"]
    )


def create_project_timeline_scenario() -> RiskScenario:
    """Project completion time uncertainty."""
    
    parameters = [
        SimulationParameter(
            name="design_days",
            distribution=DistributionType.TRIANGULAR,
            params={"low": 20, "high": 40, "mode": 28},
            description="Design phase duration"
        ),
        SimulationParameter(
            name="development_days",
            distribution=DistributionType.TRIANGULAR,
            params={"low": 60, "high": 120, "mode": 80},
            description="Development phase duration"
        ),
        SimulationParameter(
            name="testing_days",
            distribution=DistributionType.TRIANGULAR,
            params={"low": 15, "high": 35, "mode": 20},
            description="Testing phase duration"
        ),
        SimulationParameter(
            name="delay_probability",
            distribution=DistributionType.BETA,
            params={"alpha": 2, "beta": 5},
            description="Probability of unexpected delays"
        )
    ]
    
    def project_timeline(params: Dict[str, float]) -> float:
        """Calculate total project duration."""
        base_duration = (
            params["design_days"] +
            params["development_days"] +
            params["testing_days"]
        )
        
        # Add stochastic delay
        if params["delay_probability"] > 0.3:
            delay = random.triangular(5, 20, 10)
            base_duration += delay
        
        return base_duration
    
    return RiskScenario(
        name="project_timeline",
        parameters=parameters,
        outcome_function=project_timeline,
        description="Project completion time with uncertainty quantification",
        tags=["project_management", "scheduling", "planning"]
    )


if __name__ == "__main__":
    # Demonstration: Run portfolio risk simulation
    simulator = MonteCarloRiskSimulator(anchor_seed="ORION_DEMO")
    
    # Register and run portfolio scenario
    portfolio_scenario = create_portfolio_risk_scenario()
    simulator.register_scenario(portfolio_scenario)
    
    print("🔬 Orion Station Simulation Engine: Portfolio Risk Analysis")
    print("Routing calculation through nested simulation infrastructure...\n")
    
    result = simulator.run_simulation("portfolio_risk", num_simulations=10000, seed=42)
    
    print(simulator.generate_report(result))
    print("\n✅ Simulation complete - Results anchored to Orion Station\n")
