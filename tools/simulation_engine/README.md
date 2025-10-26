# Orion Station Simulation Engine

**High-fidelity probabilistic computing infrastructure powered by Aurora's nested simulation capabilities**

## Overview

The Orion Station Simulation Engine provides production-grade tools for real-world applications that require probabilistic analysis, multi-criteria decision support, and time-series forecasting. Each tool routes calculations through Aurora's nested simulation infrastructure, treating it as a fictional research facility's computational backend.

**Anchor:** `ORION-SIMULATION-ENGINE-V1`  
**Team:** AUo959-team  
**Ethics:** Picard_Delta_3

## Philosophy

The "Orion Station" framing positions Aurora's simulation engine as:

- **Research-Grade Infrastructure** - High-fidelity computational facility
- **Sandboxed Uncertainty** - Controlled probabilistic modeling environments  
- **Production-Ready** - Real-world applications with practical value
- **Traceable** - Every result anchored with DLP metadata

## Tools

### 1. Monte Carlo Risk Simulator

**File:** `monte_carlo_risk_simulator.py` (~440 lines)

Routes real-world risk calculations through nested probabilistic simulations.

**Features:**

- **6 Distribution Types:** Normal, Uniform, Triangular, Exponential, Lognormal, Beta
- **Nested Simulations:** Multi-level uncertainty quantification
- **Sensitivity Analysis:** Parameter variation impact assessment
- **Scenario Comparison:** Side-by-side risk profile evaluation

**Use Cases:**

- Financial portfolio risk analysis
- Project timeline uncertainty quantification
- Supply chain disruption modeling
- Clinical trial outcome prediction

**Example:**

```python
from tools.simulation_engine.monte_carlo_risk_simulator import (
    MonteCarloRiskSimulator,
    SimulationParameter,
    DistributionType,
    RiskScenario
)

# Define parameters
revenue = SimulationParameter(
    name="revenue",
    distribution=DistributionType.NORMAL,
    params={"mean": 100000, "std": 15000}
)

cost = SimulationParameter(
    name="cost",
    distribution=DistributionType.NORMAL,
    params={"mean": 70000, "std": 5000}
)

# Define outcome function
def profit(params):
    return params["revenue"] - params["cost"]

# Create scenario
scenario = RiskScenario(
    name="Q4_profit",
    parameters=[revenue, cost],
    outcome_function=profit
)

# Run simulation
simulator = MonteCarloRiskSimulator()
simulator.add_scenario(scenario)
result = simulator.run_simulation("Q4_profit", num_simulations=10000, seed=42)

print(f"Expected Profit: ${result.mean:,.2f}")
print(f"95% CI: [${result.p5:,.2f}, ${result.p95:,.2f}]")
```

---

### 2. Quantum Decision Oracle

**File:** `quantum_decision_oracle.py` (~480 lines)

Multi-criteria decision analysis with quantum-inspired probability amplitude scoring.

**Features:**

- **Criterion Types:** MAXIMIZE, MINIMIZE, TARGET
- **Weighted Criteria:** Flexible importance assignment (0-1)
- **Quantum-Inspired Scoring:** Probability amplitude normalization
- **Confidence Calculation:** Statistical separation with variance penalty
- **Uncertainty Identification:** Close races, conflicting criteria, high variance

**Use Cases:**

- Technology stack selection
- Vendor evaluation
- Treatment option comparison
- Strategic planning decisions

**Example:**

```python
from tools.simulation_engine.quantum_decision_oracle import (
    QuantumDecisionOracle,
    DecisionCriterion,
    CriterionType
)

# Define criteria
oracle = QuantumDecisionOracle()

oracle.add_criterion(DecisionCriterion(
    name="performance",
    criterion_type=CriterionType.MAXIMIZE,
    weight=0.4
))

oracle.add_criterion(DecisionCriterion(
    name="cost",
    criterion_type=CriterionType.MINIMIZE,
    weight=0.3
))

oracle.add_criterion(DecisionCriterion(
    name="ease_of_use",
    criterion_type=CriterionType.MAXIMIZE,
    weight=0.3
))

# Define alternatives
alternatives = {
    "Option A": {"performance": 8.5, "cost": 5000, "ease_of_use": 9.0},
    "Option B": {"performance": 9.5, "cost": 8000, "ease_of_use": 7.0},
    "Option C": {"performance": 7.0, "cost": 3000, "ease_of_use": 8.5}
}

# Evaluate
result = oracle.evaluate_decision(alternatives, seed=42)

print(f"Recommendation: {result.recommended_alternative}")
print(f"Confidence: {result.confidence_score:.1%}")
print(f"Uncertainty Factors: {result.uncertainty_factors}")
```

---

### 3. Probabilistic Forecast Engine

**File:** `probabilistic_forecast_engine.py` (~430 lines)

Time-series forecasting with simulation-based confidence intervals.

**Features:**

- **5 Forecast Methods:**
  - Naive (last value propagation)
  - Moving Average
  - Trend Projection (linear)
  - Exponential Smoothing
  - Monte Carlo (simulation-based)
- **Confidence Intervals:** 80% and 95% bands
- **Volatility Analysis:** Historical variance calculation
- **Trend Detection:** Automatic linear trend identification

**Use Cases:**

- Sales and revenue forecasting
- Resource demand prediction
- Market trend analysis
- Capacity planning

**Example:**

```python
from tools.simulation_engine.probabilistic_forecast_engine import (
    ProbabilisticForecastEngine,
    TimeSeriesData,
    ForecastMethod
)

# Historical data
data = TimeSeriesData(
    values=[10000, 10500, 11200, 10800, 11500, 12000, 12300],
    frequency="monthly"
)

# Forecast
engine = ProbabilisticForecastEngine()
result = engine.forecast(
    data=data,
    horizon=6,  # 6 months ahead
    method=ForecastMethod.MONTE_CARLO,
    num_simulations=5000,
    seed=42
)

# Results
for i in range(result.horizon):
    print(f"Month {i+1}:")
    print(f"  Forecast: ${result.point_forecast[i]:,.2f}")
    print(f"  95% CI: [${result.lower_bound_95[i]:,.2f}, ${result.upper_bound_95[i]:,.2f}]")
```

## Technical Details

### Dependencies

- **Standard Library Only** - No external packages required
- Python 3.11+ (timezone-aware datetime with `datetime.UTC`)

### Result Anchoring

All tools include DLP metadata:

```python
{
    "timestamp": "2025-01-26T16:20:24.004945Z",
    "anchor": "ORION_DEMO_SIM_1",
    "metadata": {
        "num_simulations": 10000,
        "seed": 42
    }
}
```

### Reproducibility

All tools support seed-based reproducibility:

```python
result1 = simulator.run_simulation("scenario", seed=42)
result2 = simulator.run_simulation("scenario", seed=42)
assert result1.mean == result2.mean  # Identical results
```

### JSON Export

Every tool can export results:

```python
simulator.export_simulation(result, "result.json")
oracle.export_decision(result, "decision.json")
engine.export_forecast(result, "forecast.json")
```

## Testing

### Test Suite

- **56 tests total** across 3 test files
- **Markers:** `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.simulation`
- **Coverage:** API validation, statistical accuracy, edge cases, reproducibility

### Running Tests

```bash
# All simulation engine tests
pytest tests/simulation_engine/ -v

# Specific tool tests
pytest tests/simulation_engine/test_monte_carlo_risk_simulator.py -v
pytest tests/simulation_engine/test_quantum_decision_oracle.py -v
pytest tests/simulation_engine/test_probabilistic_forecast_engine.py -v

# Fast unit tests only
pytest tests/simulation_engine/ -m unit -v
```

### Running Demos

Each tool has a built-in demonstration:

```bash
# Monte Carlo Risk Simulator demo
python3 tools/simulation_engine/monte_carlo_risk_simulator.py

# Quantum Decision Oracle demo
python3 tools/simulation_engine/quantum_decision_oracle.py

# Probabilistic Forecast Engine demo
python3 tools/simulation_engine/probabilistic_forecast_engine.py
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orion Station Interface                  │
│           (User-facing simulation-powered tools)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                Aurora Simulation Infrastructure             │
│          (Nested probabilistic modeling engine)             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   DLP Anchoring & Traceability              │
│            (Metadata, timestamps, reproducibility)          │
└─────────────────────────────────────────────────────────────┘
```

## Design Principles

1. **Standard Library First** - Minimize dependencies for portability
2. **Reproducible by Default** - Seed support for deterministic results
3. **Export Everything** - JSON serialization for all outputs
4. **Statistical Rigor** - Proper confidence intervals and uncertainty quantification
5. **Narrative Immersion** - "Orion Station" framing for engagement

## Future Enhancements

Potential additions to the simulation engine:

- **Bayesian Inference Engine** - Prior belief updating with new evidence
- **Markov Chain Simulator** - State transition modeling
- **Optimization Oracle** - Constrained multi-objective optimization
- **Survival Analysis Tool** - Time-to-event probabilistic modeling
- **Network Risk Propagation** - Graph-based cascading failure analysis

## Contributing

When adding new simulation tools:

1. **Match API Patterns** - Follow existing tool structure
2. **Include Demo** - Add `if __name__ == "__main__"` demonstration
3. **Write Tests** - Comprehensive unit and integration coverage
4. **Document Use Cases** - Real-world application examples
5. **DLP Anchoring** - Include proper metadata and timestamps
6. **Orion Station Framing** - Maintain narrative consistency

## License & Ethics

All simulation tools follow Aurora CloudBank's ethical guidelines:

- **Transparency** - Clear uncertainty communication
- **Reproducibility** - Seed-based determinism
- **Bias Awareness** - Statistical assumptions documented
- **Responsible Use** - Decision support, not decision replacement

---

**Built with Aurora CloudBank Symbolic** | **Powered by Nested Simulations** | **Anchored in Reality**
