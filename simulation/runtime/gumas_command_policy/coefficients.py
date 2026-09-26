"""Versioned coefficient tables for GUMAS command policy v1.0."""
from __future__ import annotations

from typing import Any, Mapping

POLICY_ID = "GUMAS_COMMAND_POLICY_v1_0"
POLICY_VERSION = "1.0.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"

OBSERVATION_DEFAULTS: Mapping[str, int] = {
    "contact_quality": 500,
    "relative_advantage": 500,
    "own_damage": 500,
    "enemy_damage_estimate": 500,
    "logistics_strain": 500,
    "mobility_margin": 500,
    "geometry_opportunity": 500,
    "withdrawal_viability": 500,
    "mission_pressure": 500,
    "time_pressure": 500,
    "negotiation_signal": 0,
    "ew_opportunity": 0,
    "carrier_opportunity": 0,
    "repair_need": 0,
    "enemy_closing_pressure": 500,
    "uncertainty": 500,
}

COMMANDER_FIELDS = (
    "command_skill",
    "aggression",
    "casualty_aversion",
    "adaptability",
    "deception",
    "discipline",
    "negotiation_openness",
    "initiative",
)
SPECIALIST_FIELDS = (
    "domain_skill",
    "initiative",
    "discipline",
    "stress_tolerance",
    "risk_tolerance",
    "commander_alignment",
)
ROLE_ORDER = (
    "tactical",
    "navigation",
    "ew_sensors",
    "carrier_ops",
    "engineering",
    "logistics",
)

STRATEGIC_WEIGHTS: Mapping[str, Mapping[str, int]] = {
    "HOLD": {
        "cmd.discipline": 220,
        "cmd.command_skill": 180,
        "cmd.casualty_aversion": 130,
        "obs.uncertainty": 170,
        "obs.contact_quality": -100,
        "obs.mission_pressure": -90,
        "obs.enemy_closing_pressure": 100,
        "obs.own_damage": 90,
    },
    "PRESS": {
        "cmd.aggression": 240,
        "cmd.initiative": 180,
        "cmd.command_skill": 130,
        "cmd.discipline": 70,
        "obs.relative_advantage": 160,
        "obs.contact_quality": 130,
        "obs.mission_pressure": 120,
        "obs.enemy_damage_estimate": 80,
        "cmd.casualty_aversion": -170,
        "obs.own_damage": -180,
        "obs.logistics_strain": -120,
        "obs.uncertainty": -110,
    },
    "POSITIONAL_MANEUVER": {
        "cmd.adaptability": 220,
        "cmd.deception": 190,
        "cmd.initiative": 120,
        "cmd.command_skill": 100,
        "obs.geometry_opportunity": 190,
        "obs.mobility_margin": 150,
        "obs.ew_opportunity": 90,
        "obs.uncertainty": 50,
        "obs.own_damage": -90,
        "obs.logistics_strain": -70,
    },
    "DISENGAGE": {
        "cmd.casualty_aversion": 240,
        "obs.own_damage": 230,
        "obs.logistics_strain": 170,
        "obs.withdrawal_viability": 190,
        "obs.enemy_closing_pressure": 100,
        "obs.uncertainty": 70,
        "cmd.aggression": -150,
        "cmd.initiative": -80,
        "obs.mission_pressure": -170,
        "obs.relative_advantage": -120,
    },
    "CEASEFIRE_PROBE": {
        "cmd.negotiation_openness": 280,
        "cmd.casualty_aversion": 150,
        "cmd.command_skill": 80,
        "obs.negotiation_signal": 260,
        "obs.own_damage": 110,
        "obs.logistics_strain": 90,
        "derived.parity": 110,
        "cmd.aggression": -130,
        "obs.mission_pressure": -100,
        "obs.uncertainty": -60,
    },
}

# Specialist score tables are versioned policy data. Attribute keys use sp.*;
# observation keys use obs.*; derived inverse values use derived.*.
SPECIALIST_RULES: Mapping[str, Mapping[str, Mapping[str, Any]]] = {
    "tactical": {
        "HOLD_FIRE": {
            "weights": {
                "obs.uncertainty": 240,
                "obs.own_damage": 100,
                "obs.contact_quality": -140,
                "sp.discipline": 170,
                "derived.risk_aversion": 160,
                "sp.domain_skill": 70,
            },
            "compat": {
                "HOLD": 220,
                "DISENGAGE": 160,
                "CEASEFIRE_PROBE": 180,
                "PRESS": -220,
            },
            "safety": True,
        },
        "CONTROLLED_FIRE": {
            "weights": {
                "obs.contact_quality": 180,
                "obs.relative_advantage": 80,
                "obs.uncertainty": -80,
                "sp.domain_skill": 180,
                "sp.discipline": 120,
                "sp.stress_tolerance": 80,
            },
            "compat": {
                "HOLD": 80,
                "PRESS": 100,
                "POSITIONAL_MANEUVER": 80,
            },
            "safety": False,
        },
        "MAX_EFFECT_FIRE": {
            "weights": {
                "obs.contact_quality": 200,
                "obs.relative_advantage": 160,
                "obs.enemy_damage_estimate": 100,
                "obs.mission_pressure": 120,
                "obs.uncertainty": -150,
                "sp.domain_skill": 140,
                "sp.initiative": 160,
                "sp.risk_tolerance": 220,
                "sp.stress_tolerance": 70,
            },
            "compat": {
                "PRESS": 240,
                "POSITIONAL_MANEUVER": 40,
                "DISENGAGE": -240,
                "CEASEFIRE_PROBE": -240,
            },
            "safety": False,
        },
    },
    "navigation": {
        "HOLD_VECTOR": {
            "weights": {
                "obs.uncertainty": 120,
                "obs.geometry_opportunity": -80,
                "sp.domain_skill": 90,
                "sp.discipline": 150,
                "derived.risk_aversion": 100,
            },
            "compat": {"HOLD": 220, "CEASEFIRE_PROBE": 80},
            "safety": True,
        },
        "POSITION_FOR_ADVANTAGE": {
            "weights": {
                "obs.geometry_opportunity": 220,
                "obs.mobility_margin": 180,
                "obs.contact_quality": 80,
                "sp.domain_skill": 200,
                "sp.initiative": 150,
                "sp.risk_tolerance": 100,
            },
            "compat": {"POSITIONAL_MANEUVER": 260, "PRESS": 80},
            "safety": False,
        },
        "EVASIVE_VECTOR": {
            "weights": {
                "obs.own_damage": 150,
                "obs.enemy_closing_pressure": 180,
                "obs.uncertainty": 80,
                "obs.mobility_margin": 100,
                "sp.domain_skill": 180,
                "sp.stress_tolerance": 140,
                "sp.discipline": 100,
            },
            "compat": {
                "HOLD": 80,
                "DISENGAGE": 160,
                "POSITIONAL_MANEUVER": 80,
            },
            "safety": True,
        },
        "WITHDRAW_VECTOR": {
            "weights": {
                "obs.own_damage": 190,
                "obs.logistics_strain": 140,
                "obs.withdrawal_viability": 220,
                "obs.enemy_closing_pressure": 110,
                "sp.domain_skill": 140,
                "sp.stress_tolerance": 90,
                "derived.risk_aversion": 130,
            },
            "compat": {
                "DISENGAGE": 280,
                "CEASEFIRE_PROBE": 80,
                "PRESS": -240,
            },
            "safety": True,
        },
    },
    "ew_sensors": {
        "PASSIVE_TRACK": {
            "weights": {
                "derived.contact_deficit": 180,
                "obs.uncertainty": 170,
                "sp.domain_skill": 160,
                "sp.discipline": 100,
                "derived.risk_aversion": 80,
            },
            "compat": {"HOLD": 180, "CEASEFIRE_PROBE": 120},
            "safety": True,
        },
        "PROTECT_NETWORK": {
            "weights": {
                "obs.enemy_closing_pressure": 100,
                "obs.own_damage": 100,
                "obs.uncertainty": 120,
                "sp.domain_skill": 180,
                "sp.stress_tolerance": 130,
                "sp.discipline": 120,
            },
            "compat": {"HOLD": 120, "DISENGAGE": 120},
            "safety": True,
        },
        "ACTIVE_JAM": {
            "weights": {
                "obs.ew_opportunity": 250,
                "obs.contact_quality": 120,
                "obs.mission_pressure": 80,
                "sp.domain_skill": 190,
                "sp.initiative": 130,
                "sp.risk_tolerance": 100,
            },
            "compat": {"PRESS": 190, "POSITIONAL_MANEUVER": 130},
            "safety": False,
        },
        "DECEPTIVE_EMISSIONS": {
            "weights": {
                "obs.ew_opportunity": 220,
                "obs.geometry_opportunity": 130,
                "obs.uncertainty": -80,
                "sp.domain_skill": 190,
                "sp.initiative": 120,
                "sp.risk_tolerance": 100,
            },
            "compat": {"POSITIONAL_MANEUVER": 260, "PRESS": 50},
            "safety": False,
        },
    },
    "carrier_ops": {
        "HOLD_CRAFT": {
            "weights": {
                "obs.logistics_strain": 150,
                "obs.own_damage": 120,
                "obs.uncertainty": 140,
                "sp.domain_skill": 100,
                "sp.discipline": 100,
                "derived.risk_aversion": 170,
            },
            "compat": {
                "HOLD": 180,
                "DISENGAGE": 200,
                "CEASEFIRE_PROBE": 160,
            },
            "safety": True,
        },
        "SCREEN_FLEET": {
            "weights": {
                "obs.enemy_closing_pressure": 140,
                "obs.own_damage": 90,
                "obs.contact_quality": 80,
                "obs.carrier_opportunity": 80,
                "sp.domain_skill": 170,
                "sp.discipline": 120,
                "sp.stress_tolerance": 110,
            },
            "compat": {
                "HOLD": 100,
                "POSITIONAL_MANEUVER": 100,
                "DISENGAGE": 80,
            },
            "safety": True,
        },
        "COMMIT_STRIKE_CRAFT": {
            "weights": {
                "obs.carrier_opportunity": 260,
                "obs.contact_quality": 140,
                "obs.relative_advantage": 100,
                "obs.mission_pressure": 100,
                "obs.logistics_strain": -100,
                "sp.domain_skill": 170,
                "sp.initiative": 130,
                "sp.risk_tolerance": 180,
            },
            "compat": {
                "PRESS": 240,
                "POSITIONAL_MANEUVER": 80,
                "DISENGAGE": -220,
            },
            "safety": False,
        },
    },
    "engineering": {
        "BALANCED_POWER": {
            "weights": {
                "derived.repair_deficit": 120,
                "obs.uncertainty": 80,
                "sp.domain_skill": 140,
                "sp.discipline": 130,
                "sp.stress_tolerance": 100,
            },
            "compat": {"HOLD": 120, "POSITIONAL_MANEUVER": 60},
            "safety": False,
        },
        "REINFORCE_DEFENSE": {
            "weights": {
                "obs.own_damage": 160,
                "obs.enemy_closing_pressure": 170,
                "obs.contact_quality": 80,
                "sp.domain_skill": 180,
                "sp.stress_tolerance": 140,
                "sp.discipline": 80,
            },
            "compat": {"HOLD": 150, "PRESS": 40, "DISENGAGE": 100},
            "safety": True,
        },
        "PRIORITIZE_PROPULSION": {
            "weights": {
                "derived.mobility_deficit": 170,
                "obs.geometry_opportunity": 100,
                "obs.withdrawal_viability": 100,
                "obs.enemy_closing_pressure": 100,
                "sp.domain_skill": 180,
                "sp.initiative": 120,
                "sp.risk_tolerance": 70,
            },
            "compat": {
                "POSITIONAL_MANEUVER": 180,
                "DISENGAGE": 180,
                "PRESS": 50,
            },
            "safety": True,
        },
        "DAMAGE_CONTROL_SURGE": {
            "weights": {
                "obs.repair_need": 280,
                "obs.own_damage": 200,
                "obs.logistics_strain": 60,
                "sp.domain_skill": 190,
                "sp.stress_tolerance": 160,
                "sp.initiative": 80,
            },
            "compat": {"HOLD": 100, "DISENGAGE": 160, "PRESS": -80},
            "safety": True,
        },
    },
    "logistics": {
        "CONSERVE": {
            "weights": {
                "obs.logistics_strain": 250,
                "obs.own_damage": 80,
                "obs.uncertainty": 80,
                "sp.domain_skill": 160,
                "sp.discipline": 120,
                "derived.risk_aversion": 140,
            },
            "compat": {
                "HOLD": 150,
                "DISENGAGE": 170,
                "CEASEFIRE_PROBE": 120,
                "PRESS": -120,
            },
            "safety": True,
        },
        "BALANCED_EXPENDITURE": {
            "weights": {
                "derived.logistics_margin": 120,
                "obs.contact_quality": 60,
                "sp.domain_skill": 180,
                "sp.discipline": 120,
                "sp.stress_tolerance": 80,
            },
            "compat": {
                "HOLD": 80,
                "POSITIONAL_MANEUVER": 80,
                "PRESS": 40,
            },
            "safety": False,
        },
        "SURGE_EXPENDITURE": {
            "weights": {
                "obs.mission_pressure": 180,
                "obs.relative_advantage": 120,
                "obs.contact_quality": 100,
                "obs.logistics_strain": -180,
                "sp.domain_skill": 140,
                "sp.initiative": 140,
                "sp.risk_tolerance": 180,
            },
            "compat": {
                "PRESS": 240,
                "POSITIONAL_MANEUVER": 50,
                "DISENGAGE": -220,
            },
            "safety": False,
        },
    },
}
