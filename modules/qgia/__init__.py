"""QGIA — Quantum Geopolitical Intelligence Agency modules

Submodules:
- QSFE (Forecast Simulation Engine): Multi-agent belief propagation forecast engine
- Knowledge Indexer: Walks QGIA repos and produces knowledge-index.json
- Knowledge Bridge: Searchable index + QSFE enrichment layer

Ref: Aurora Constellation Architecture Proposal v1.0.0
"""

__version__ = "1.0.0"
__author__ = "Pilot (AUo959)"

MODULE_MANIFEST = {
    "name": "QGIA Forecast Simulation Engine",
    "version": __version__,
    "symbolic_tag": "s.tag::module.qgia.qsfe",
    "node": "L1_QGIA",
    "charter": "Picard_Delta_3",
    "description": "Multi-agent belief propagation forecast engine for QGIA analytical operations",
    "author": __author__,
    "registered": "2026-03-12",
    "dependencies": ["numpy", "pydantic>=2.0"],
}

from .forecast_engine import QGIAForecastEngine
from .output_formatter import format_forecast
from .population_generator import generate_population
from .scenario import (
    EXAMPLE_SCENARIOS,
    create_scenario,
    european_energy_crisis,
    iran_nuclear_escalation,
    south_china_sea_confrontation,
    subsaharan_instability,
)
from .schemas import (
    Agent,
    Division,
    EpistemicProfile,
    ForecastOutput,
    ScenarioInput,
    TierAssessment,
    TrustEdge,
)
from .trust_network import build_adjacency, generate_trust_network

__all__ = [
    "MODULE_MANIFEST",
    "QGIAForecastEngine",
    "format_forecast",
    "generate_population",
    "generate_trust_network",
    "build_adjacency",
    "create_scenario",
    "iran_nuclear_escalation",
    "south_china_sea_confrontation",
    "european_energy_crisis",
    "subsaharan_instability",
    "EXAMPLE_SCENARIOS",
    "Agent",
    "Division",
    "EpistemicProfile",
    "ForecastOutput",
    "ScenarioInput",
    "TierAssessment",
    "TrustEdge",
]
