"""QGIA Forecast Simulation Engine — SBM Trust Network Generator.

Generates the ~7,407-edge directed trust network using a Stochastic Block
Model. Edge probabilities depend on division membership, tier proximity,
combined contrarian index, and geometric mean trust radius. No networkx
dependency — uses adjacency dicts.
"""

import math

import numpy as np

from .config import GRADE_TIERS, TRUST_NETWORK_PARAMS
from .schemas import Agent, TrustEdge

__all__ = ["generate_trust_network", "build_adjacency"]


def _edge_probability(agent_i: Agent, agent_j: Agent, params: dict) -> float:
    """Compute SBM edge probability for directed pair (i -> j)."""
    same_div = agent_i.division == agent_j.division
    base = params["within_division_base_probability"] if same_div else params["cross_division_base_probability"]

    tier_i = GRADE_TIERS[agent_i.grade]
    tier_j = GRADE_TIERS[agent_j.grade]
    tier_gap = abs(tier_i - tier_j)
    tier_penalty = params["cross_tier_penalty_per_tier_gap"] * tier_gap

    ci_avg = (agent_i.epistemic_profile.contrarian_index + agent_j.epistemic_profile.contrarian_index) / 2
    contrarian_boost = params["contrarian_boost_coefficient"] * ci_avg

    tr_i = agent_i.epistemic_profile.trust_radius
    tr_j = agent_j.epistemic_profile.trust_radius
    geo_mean_tr = math.sqrt(tr_i * tr_j) if (tr_i > 0 and tr_j > 0) else 0.0
    trust_boost = params["trust_radius_boost_coefficient"] * geo_mean_tr

    prob = base - tier_penalty + contrarian_boost + trust_boost
    return max(params["min_edge_probability"], min(params["max_edge_probability"], prob))


def _classify_edge(source: Agent, target: Agent) -> str:
    """Determine the edge type for an existing edge."""
    tier_target = GRADE_TIERS[target.grade]
    tier_source = GRADE_TIERS[source.grade]

    if source.epistemic_profile.contrarian_index > 0.35 and tier_target > tier_source:
        return "challenge"
    if (
        source.archetype == target.archetype
        and abs(source.epistemic_profile.prior_strength - target.epistemic_profile.prior_strength) < 0.15
    ):
        return "reinforce"
    if source.division == target.division:
        return "collaborate"
    return "inform"


def _edge_weight(source: Agent, target: Agent) -> float:
    """Compute edge weight from geometric mean trust radius and tier proximity."""
    tr_s = source.epistemic_profile.trust_radius
    tr_t = target.epistemic_profile.trust_radius
    geo_mean = math.sqrt(tr_s * tr_t) if (tr_s > 0 and tr_t > 0) else 0.0
    tier_gap = abs(GRADE_TIERS[source.grade] - GRADE_TIERS[target.grade])
    weight = geo_mean * (1.0 - tier_gap * 0.1)
    return max(0.0, min(1.0, weight))


def generate_trust_network(
    agents: list[Agent],
    seed: int = 42,
    params: dict | None = None,
) -> list[TrustEdge]:
    """Generate the directed trust network via SBM sampling.

    Args:
        agents: Full 551-agent population.
        seed: RNG seed for reproducibility.
        params: Override SBM parameters (defaults to config).

    Returns:
        List of TrustEdge objects (target ~7,407 edges).
    """
    if params is None:
        params = TRUST_NETWORK_PARAMS

    rng = np.random.default_rng(seed)
    edges: list[TrustEdge] = []
    n = len(agents)

    # Pre-compute uniform random matrix for Bernoulli sampling
    # For memory efficiency with 551 agents (~303k pairs), generate in chunks
    for i in range(n):
        # Generate random values for all potential targets of agent i
        randoms = rng.random(n)
        for j in range(n):
            if i == j:
                continue
            prob = _edge_probability(agents[i], agents[j], params)
            if randoms[j] < prob:
                etype = _classify_edge(agents[i], agents[j])
                weight = _edge_weight(agents[i], agents[j])
                edges.append(
                    TrustEdge(
                        source=agents[i].agent_id,
                        target=agents[j].agent_id,
                        edge_type=etype,
                        weight=weight,
                    )
                )

    return edges


def build_adjacency(edges: list[TrustEdge]) -> dict[str, list[TrustEdge]]:
    """Build an adjacency dict keyed by target agent_id.

    Returns a mapping from each agent_id to the list of incoming edges
    (edges where that agent is the target), which is what belief propagation
    needs — "who influences me?"
    """
    adj: dict[str, list[TrustEdge]] = {}
    for edge in edges:
        adj.setdefault(edge.target, []).append(edge)
    return adj


def build_outgoing_adjacency(edges: list[TrustEdge]) -> dict[str, list[TrustEdge]]:
    """Build an adjacency dict keyed by source agent_id (outgoing edges)."""
    adj: dict[str, list[TrustEdge]] = {}
    for edge in edges:
        adj.setdefault(edge.source, []).append(edge)
    return adj
