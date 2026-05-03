# QGIA Forecast Simulation Engine (QSFE)

**Symbolic Tag:** `s.tag::module.qgia.qsfe`
**Node:** L1_QGIA (L1-B)
**Charter:** Picard_Delta_3
**Version:** 1.0.0

## Overview

The QSFE is the analytical core of the Quantum Geopolitical Intelligence Agency (QGIA), a registered L1 peer node in the Aurora-GUMAS network. It implements multi-agent belief propagation across a 551-analyst population to produce three-tier probabilistic intelligence forecasts.

## Architecture

```
modules/qgia/
├── __init__.py                # Module manifest + public API
├── config.py                  # Canonical QGIA parameters
├── schemas.py                 # Pydantic v2 data models
├── population_generator.py    # 551-agent Monte Carlo generator
├── trust_network.py           # SBM trust network (~7,407 edges)
├── forecast_engine.py         # Core QSFE — belief propagation + aggregation
├── scenario.py                # Scenario model + 4 example templates
├── output_formatter.py        # Three-tier formatted output
└── README.md
```

## Usage

```python
from modules.qgia import QGIAForecastEngine, iran_nuclear_escalation, format_forecast

# Initialize engine (generates population + trust network)
engine = QGIAForecastEngine(seed=42)

# Create a scenario
scenario = iran_nuclear_escalation()

# Run the forecast
output = engine.run_forecast(scenario)

# Format for human consumption
report = format_forecast(output, scenario_title=scenario.title)
print(report)
```

## Algorithm

1. **Crisis Response Cell Selection** — Filters the 551-agent population to analysts whose regional specialization matches the scenario. IID analysts (cross-domain integrators) always participate.

2. **Initial Belief Formation** — Each analyst forms an initial belief from evidence fragments, weighted by reliability and modulated by their archetype (Aggressive Updaters amplify signal, Contrarians invert, Conservatives dampen, etc.).

3. **Belief Propagation** — 5-8 rounds of message passing on the trust network. Edge types modulate influence: collaborate (1.0x), reinforce (1.2x), inform (0.7x), challenge (-0.5x). Convergence threshold: 0.01.

4. **Tier Aggregation** — Final beliefs are aggregated into three tiers using a bounded normalization process:
   - Raw probabilities are clamped to per-tier bands: Tier I ∈ [0.26, 0.85], Tier II ∈ [0.10, 0.25], Tier III ∈ [0.01, 0.09]
   - A bounded simplex projection adjusts the three raw values so the outputs form a valid probability distribution: **P(I) + P(II) + P(III) = 1.0**
   - Post-normalization values remain inside the documented tier bands

5. **Dissent & Echo Chamber Analysis** — Identifies analysts >1.5σ from consensus, ranks by influence. Detects reinforce-edge clusters with low internal variance.

## Dependencies

- `numpy` — Beta-distributed RNG, statistical aggregation
- `pydantic>=2.0` — Data model validation

No `networkx` dependency — trust graph uses adjacency dicts.

## Related Documents

- [QGIA L1 Node Registration](../../docs/architecture/QGIA_L1_NODE_REGISTRATION.md)
- [Analyst Orientation Guide](../../docs/philosophy/07_ANALYST_ORIENTATION.md)
- [QGIA Canon Staff Registry](../../docs/architecture/QGIA_CANON_STAFF_REGISTRY.md)

## Parameter Reference

### Epistemic Distributions (Beta)

| Trait | Alpha | Beta | Description |
|---|---|---|---|
| prior_strength | 4 | 3 | Resistance to prior revision |
| update_threshold | 3 | 4 | Evidence weight for belief update |
| contrarian_index | 2 | 5 | Propensity to challenge consensus |
| trust_radius | 2 | 4 | Breadth of trusted peer network |
| domain_overconfidence | 3 | 5 | Calibration gap in specialty |
| intellectual_independence | 4 | 2 | Autonomy from peer pressure |
| institutional_loyalty | 3 | 3 | Deference to hierarchy |

### Trust Network SBM

| Parameter | Value |
|---|---|
| Within-division base probability | 0.12 |
| Cross-division base probability | 0.025 |
| Cross-tier penalty per gap | 0.04 |
| Contrarian boost coefficient | 0.05 |
| Trust radius boost coefficient | 0.04 |
| Edge probability range | [0.005, 0.35] |
| Target edges | ~7,407 |
