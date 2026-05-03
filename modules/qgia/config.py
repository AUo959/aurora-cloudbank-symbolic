"""QGIA Forecast Simulation Engine — Configuration Constants.

Canonical parameters for the 551-agent QGIA population, trust network SBM,
and forecast engine behavior. All values sourced from QGIA OPERATIONAL
ENVIRONMENT v3.0 and the agent registry schema.
"""

__all__ = [
    "DIVISIONS",
    "GRADE_DISTRIBUTION",
    "ARCHETYPES",
    "EPISTEMIC_DISTRIBUTIONS",
    "TRUST_NETWORK_PARAMS",
    "EDGE_TYPES",
    "GRADE_TIERS",
    "TIER_PROBABILITY_BOUNDS",
    "DIVISION_ARCHETYPES",
    "DIVISION_REGIONS",
    "SRD_THEMES",
    "TOTAL_AGENTS",
    "TARGET_EDGES",
]

TOTAL_AGENTS = 551
TARGET_EDGES = 7407

TIER_PROBABILITY_BOUNDS: dict[int, tuple[float, float]] = {
    1: (0.26, 0.85),
    2: (0.10, 0.25),
    3: (0.01, 0.09),
}

DIVISIONS: dict[str, dict] = {
    "GMD": {"name": "Global Monitoring Division", "headcount": 203},
    "MAD": {"name": "Military Analysis Division", "headcount": 142},
    "IID": {"name": "Intelligence Integration Division", "headcount": 138},
    "SRD": {"name": "Strategic Research Division", "headcount": 68},
}

GRADE_DISTRIBUTION: dict[str, dict] = {
    "GS-9":  {"label": "Junior Analyst",    "count": 38},
    "GS-11": {"label": "Analyst",           "count": 72},
    "GS-12": {"label": "Senior Analyst",    "count": 118},
    "GS-13": {"label": "Senior Analyst",    "count": 202},
    "GS-14": {"label": "Principal Analyst", "count": 48},
    "GS-15": {"label": "Senior Principal",  "count": 25},
    "SES":   {"label": "Senior Executive",  "count": 11},
    "DIR":   {"label": "Director/Deputy",   "count": 6},
    "EXEC":  {"label": "Executive Staff",   "count": 31},
}

ARCHETYPES: list[str] = [
    "Aggressive Updater",
    "Prior-Anchored Conservative",
    "Contrarian by Default",
    "Institutionalist",
    "Empirical Minimalist",
    "Intuitive Pattern Matcher",
    "Dialectical Synthesizer",
    "Recursive Self-Corrector",
]

# Division-specific archetype weight overrides (index into ARCHETYPES).
# Higher weight = more likely assignment. Unlisted divisions use uniform.
DIVISION_ARCHETYPES: dict[str, dict[str, float]] = {
    "MAD": {
        "Empirical Minimalist": 2.5,
        "Prior-Anchored Conservative": 2.0,
    },
    "SRD": {
        "Dialectical Synthesizer": 2.5,
        "Recursive Self-Corrector": 1.8,
        "Prior-Anchored Conservative": 1.5,
    },
    "GMD": {
        "Intuitive Pattern Matcher": 2.0,
        "Aggressive Updater": 1.5,
    },
    "IID": {
        "Recursive Self-Corrector": 2.0,
        "Institutionalist": 1.5,
    },
}

# Beta distribution parameters (alpha, beta) for epistemic traits
EPISTEMIC_DISTRIBUTIONS: dict[str, tuple[float, float]] = {
    "prior_strength":            (4, 3),
    "update_threshold":          (3, 4),
    "contrarian_index":          (2, 5),
    "trust_radius":              (2, 4),
    "domain_overconfidence":     (3, 5),
    "intellectual_independence":  (4, 2),
    "institutional_loyalty":     (3, 3),
}

# SBM trust network parameters
TRUST_NETWORK_PARAMS: dict[str, float] = {
    "within_division_base_probability": 0.075,
    "cross_division_base_probability": 0.016,
    "cross_tier_penalty_per_tier_gap": 0.02,
    "contrarian_boost_coefficient": 0.03,
    "trust_radius_boost_coefficient": 0.02,
    "min_edge_probability": 0.005,
    "max_edge_probability": 0.35,
}

EDGE_TYPES: dict[str, str] = {
    "collaborate": "Active analytical partnership within shared division",
    "challenge": "High combined contrarian index; dissent relationship",
    "reinforce": "Shared archetype + similar prior strength; mutual confirmation",
    "inform": "Cross-division information flow",
}

GRADE_TIERS: dict[str, int] = {
    "GS-9": 1, "GS-11": 2, "GS-12": 3, "GS-13": 4,
    "GS-14": 5, "GS-15": 6, "SES": 7, "DIR": 8, "EXEC": 9,
}

# Regional specializations by division
DIVISION_REGIONS: dict[str, list[str]] = {
    "GMD": ["Indo-Pacific", "Europe", "Middle East", "Africa", "Americas", "Central Asia"],
    "MAD": ["Middle East", "Indo-Pacific", "Europe", "Africa"],
    "IID": ["Cross-domain"],
    "SRD": ["Thematic"],
}

SRD_THEMES: list[str] = [
    "Proliferation",
    "Cyber Security",
    "Climate Security",
    "Economic Statecraft",
    "Strategic Competition",
    "Technology Transfer",
]
