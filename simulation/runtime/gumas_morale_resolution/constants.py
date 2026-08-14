"""Scenario-local constants for deterministic GUMAS Phase-8 resolution."""

PHASE8_CONTRACT_ID = "GUMAS_MORALE_RESOLUTION_TERMINATION_v1_0"
PHASE8_VERSION = "1.0.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"

WITHDRAWAL_BOUNDARY_UM = 20_000_000_000_000
HARD_LIMIT_MS = 21_600_000
CEASEFIRE_OFFER_TTL_MACROSTEPS = 3
MUTUAL_DISENGAGE_REQUIRED_STREAK = 2
WITHDRAWAL_SUCCESS_FRACTION_Q1000 = 700

BATTLE_SHOCK_WEIGHTS_Q1000 = {
    "fleet_hull_loss": 700,
    "new_incapacity": 300,
}
MORALE_LOSS_WEIGHTS_Q1000 = {
    "local_hull_loss": 500,
    "fleet_hull_loss": 300,
    "new_incapacity": 200,
}
COHESION_LOSS_WEIGHTS_Q1000 = {
    "fleet_hull_loss": 400,
    "new_incapacity": 300,
    "shock_coupled_dissent": 300,
}
SURRENDER_PRESSURE_WEIGHTS_Q1000 = {
    "combat_deficit": 300,
    "hull_deficit": 250,
    "morale_deficit": 200,
    "cohesion_deficit": 100,
    "withdrawal_failure": 150,
}
SURRENDER_THRESHOLD_BASE_Q1000 = 500
SURRENDER_THRESHOLD_RESOLVE_SPAN_Q1000 = 250
SURRENDER_MAX_COMBAT_EFFECTIVE_FRACTION_Q1000 = 500
SURRENDER_MAX_FLEET_MORALE_Q1000 = 450

ACTIVE_PHYSICAL_DISPOSITIONS = {"combat_capable", "degraded"}
SURVIVING_PHYSICAL_DISPOSITIONS = {"combat_capable", "degraded", "disabled"}
KNOWN_STRATEGIC_POSTURES = {
    "PRESS",
    "POSITIONAL_MANEUVER",
    "HOLD",
    "DISENGAGE",
    "CEASEFIRE_PROBE",
}
