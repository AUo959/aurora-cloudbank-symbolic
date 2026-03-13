"""QGIA Forecast Simulation Engine — Pydantic v2 Data Models.

All data structures for agents, trust edges, scenarios, tier assessments,
and forecast outputs. Uses Pydantic v2 native syntax.
"""

from enum import Enum

from pydantic import BaseModel, Field

__all__ = [
    "Division",
    "EpistemicProfile",
    "Agent",
    "TrustEdge",
    "ScenarioInput",
    "TierAssessment",
    "ForecastOutput",
]


class Division(str, Enum):
    """QGIA organizational divisions."""

    GMD = "GMD"
    MAD = "MAD"
    IID = "IID"
    SRD = "SRD"


class EpistemicProfile(BaseModel):
    """Beta-distributed epistemic trait vector for a single analyst."""

    prior_strength: float = Field(ge=0.0, le=1.0)
    update_threshold: float = Field(ge=0.0, le=1.0)
    contrarian_index: float = Field(ge=0.0, le=1.0)
    trust_radius: float = Field(ge=0.0, le=1.0)
    domain_overconfidence: float = Field(ge=0.0, le=1.0)
    intellectual_independence: float = Field(ge=0.0, le=1.0)
    institutional_loyalty: float = Field(ge=0.0, le=1.0)


class Agent(BaseModel):
    """A single QGIA analyst with division, grade, archetype, and epistemic profile."""

    agent_id: str
    division: Division
    grade: str
    archetype: str
    epistemic_profile: EpistemicProfile
    regional_specialization: str
    initial_belief: float = 0.5


class TrustEdge(BaseModel):
    """Directed trust/influence edge between two analysts."""

    source: str
    target: str
    edge_type: str
    weight: float = Field(ge=0.0, le=1.0)


class ScenarioInput(BaseModel):
    """Input scenario for the forecast engine."""

    scenario_id: str
    title: str
    description: str
    region: str
    domain: str
    evidence_fragments: list[dict]
    requesting_node: str = "L1_QGIA"


class TierAssessment(BaseModel):
    """Single tier assessment within a forecast output."""

    tier: int
    label: str
    scenario_variant: str
    probability: float
    confidence: float
    confidence_components: dict
    reasoning_chain: list[str]
    dissent_count: int
    key_dissenters: list[str]


class ForecastOutput(BaseModel):
    """Complete forecast output from the QSFE pipeline."""

    forecast_id: str
    scenario_id: str
    timestamp: str
    classification: str = "QGIA ANALYTICAL PRODUCT"
    tier_assessments: list[TierAssessment]
    provenance: dict
    echo_chamber_warnings: list[str]
    analyst_participation: dict
    meta: dict
