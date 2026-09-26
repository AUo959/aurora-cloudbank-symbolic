"""Scenario-local constants for deterministic Phase-7 damage resolution."""

PHASE7_CONTRACT_ID = "GUMAS_DAMAGE_DISPOSITION_v1_0"
PHASE7_VERSION = "1.0.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"

ARMOR_ABSORPTION_EFFICIENCY_Q1000 = 850
DAMAGE_CONTROL_MAX_MITIGATION_Q1000 = 250

READINESS_SHOCK_WEIGHTS_Q1000 = {
    "propulsion": 900,
    "weapons": 900,
    "sensors": 700,
    "ew": 700,
    "damage_control": 800,
    "overall": 600,
}

READINESS_FIELDS = (
    "overall",
    "sensors",
    "ew",
    "propulsion",
    "weapons",
    "damage_control",
)

PROTECTED_PRIOR_DISPOSITIONS = {"destroyed"}
