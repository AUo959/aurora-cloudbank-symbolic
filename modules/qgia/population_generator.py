"""QGIA Forecast Simulation Engine — Agent Population Generator.

Generates the full 551-agent population using Monte Carlo sampling with
Beta-distributed epistemic parameters. Division headcounts, grade
distribution, archetype weighting, and regional specializations all
follow canonical QGIA parameters.
"""

import numpy as np

from .config import (
    ARCHETYPES,
    DIVISIONS,
    DIVISION_ARCHETYPES,
    DIVISION_REGIONS,
    EPISTEMIC_DISTRIBUTIONS,
    GRADE_DISTRIBUTION,
    GRADE_TIERS,
    SRD_THEMES,
)
from .schemas import Agent, Division, EpistemicProfile

__all__ = ["generate_population"]


def _build_archetype_weights(division: str) -> np.ndarray:
    """Build archetype probability weights for a division."""
    weights = np.ones(len(ARCHETYPES), dtype=float)
    overrides = DIVISION_ARCHETYPES.get(division, {})
    for i, archetype in enumerate(ARCHETYPES):
        if archetype in overrides:
            weights[i] = overrides[archetype]
    return weights / weights.sum()


def _assign_grades(rng: np.random.Generator, count: int) -> list[str]:
    """Distribute grades across *count* agents matching the canonical distribution."""
    grade_pool: list[str] = []
    for grade, info in GRADE_DISTRIBUTION.items():
        grade_pool.extend([grade] * info["count"])
    # Pool has exactly 551 entries — sample without replacement when count == 551,
    # otherwise sample proportionally.
    if count == len(grade_pool):
        rng.shuffle(grade_pool)
        return grade_pool
    # Proportional sampling for sub-populations
    probs = np.array([GRADE_DISTRIBUTION[g]["count"] for g in GRADE_DISTRIBUTION])
    probs = probs / probs.sum()
    grades = list(GRADE_DISTRIBUTION.keys())
    return [grades[i] for i in rng.choice(len(grades), size=count, p=probs)]


def generate_population(seed: int = 42) -> list[Agent]:
    """Generate the canonical 551-agent QGIA population.

    Args:
        seed: RNG seed for reproducibility.

    Returns:
        List of 551 Agent models with fully populated epistemic profiles.
    """
    rng = np.random.default_rng(seed)

    # Build flat list of (division, count) to fill
    division_slots: list[str] = []
    for div_code, div_info in DIVISIONS.items():
        division_slots.extend([div_code] * div_info["headcount"])

    # Assign grades across the full population
    grades = _assign_grades(rng, len(division_slots))

    # Shuffle together so division-grade pairs are mixed
    indices = np.arange(len(division_slots))
    rng.shuffle(indices)

    agents: list[Agent] = []
    # Track per-division sequence numbers
    div_seq: dict[str, int] = {d: 0 for d in DIVISIONS}

    for idx in indices:
        div_code = division_slots[idx]
        grade = grades[idx]
        tier = GRADE_TIERS[grade]

        div_seq[div_code] += 1
        agent_id = f"QGIA-{div_code}-{tier}-{div_seq[div_code]:04d}"

        archetype_weights = _build_archetype_weights(div_code)
        archetype = ARCHETYPES[rng.choice(len(ARCHETYPES), p=archetype_weights)]

        # Sample epistemic profile from Beta distributions
        profile_data = {}
        for trait, (alpha, beta) in EPISTEMIC_DISTRIBUTIONS.items():
            profile_data[trait] = float(rng.beta(alpha, beta))

        # Regional specialization
        regions = DIVISION_REGIONS[div_code]
        if div_code == "SRD":
            specialization = rng.choice(SRD_THEMES)
        elif div_code == "IID":
            specialization = "Cross-domain"
        else:
            specialization = rng.choice(regions)

        agents.append(
            Agent(
                agent_id=agent_id,
                division=Division(div_code),
                grade=grade,
                archetype=archetype,
                epistemic_profile=EpistemicProfile(**profile_data),
                regional_specialization=specialization,
            )
        )

    return agents
