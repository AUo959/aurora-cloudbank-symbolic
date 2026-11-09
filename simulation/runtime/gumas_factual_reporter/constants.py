"""Versioned constants for the deterministic GUMAS Phase-10 reporter."""

PHASE10_CONTRACT_ID = "GUMAS_DETERMINISTIC_FACTUAL_REPORTER_EVIDENCE_EXPORT_v1_0"
PHASE10_VERSION = "1.0.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"
HISTORICAL_CANON_STATUS = "non_canon_simulation_instance"
GENESIS_MARKER = "GENESIS"

INPUT_SCHEMA = "aurora://simulation/gumas/phase10_report_input/v1.0"
MACROSTEP_PACKET_SCHEMA = "aurora://simulation/gumas/phase10_macrostep_artifacts/v1.0"
NORMALIZED_REPORT_SCHEMA = "aurora://simulation/gumas/phase10_normalized_factual_report/v1.0"
FACTUAL_EVENT_SCHEMA = "aurora://simulation/gumas/phase10_factual_event/v1.0"
EVIDENCE_INDEX_SCHEMA = "aurora://simulation/gumas/phase10_evidence_index/v1.0"
RENDERED_REPORT_SCHEMA = "aurora://simulation/gumas/phase10_rendered_report/v1.0"
EXPORT_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase10_export_receipt/v1.0"

PHASE9_RUN_CONTEXT_SCHEMA = "aurora://simulation/gumas/phase9_run_context/v1.0"
PHASE9_LEDGER_ENTRY_SCHEMA = "aurora://simulation/gumas/phase9_ledger_entry/v1.0"
PHASE9_OBSERVATION_RECEIPT_SCHEMA = (
    "aurora://simulation/gumas/live_command_observation_receipt/v1.0"
)
PHASE9_CONTRACT_ID = "GUMAS_LIVE_OBSERVATION_ORCHESTRATOR_LEDGER_v1_0"
PHASE9_VERSION = "1.0.0"

COMMAND_RECEIPT_SCHEMA = "aurora://simulation/gumas/command_decision_receipt/v1.0"
MOVEMENT_RECEIPT_SCHEMA = "aurora://simulation/gumas/movement_step_receipt/v1.0"
PHASE6_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase6_step_receipt/v1.0"
PHASE7_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase7_step_receipt/v1.0"
PHASE8_RESOLUTION_SCHEMA = "aurora://simulation/gumas/phase8_resolution_state/v1.0"
PHASE8_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase8_step_receipt/v1.0"

SIMULATION_TRUTH_PROFILE = "simulation_truth_v1"
PUBLIC_SUMMARY_PROFILE = "public_summary_v1"
REPORT_PROFILES = frozenset({SIMULATION_TRUTH_PROFILE, PUBLIC_SUMMARY_PROFILE})

PUBLIC_FACT_TYPES = frozenset(
    {
        "macrostep_boundary",
        "movement_aggregate",
        "sensing_fire_aggregate",
        "damage_aggregate",
        "side_resolution",
        "terminal_outcome",
    }
)

AUTHORITATIVE_MODULE_NAMES = (
    "__init__.py",
    "constants.py",
    "identity.py",
    "validation.py",
    "projection.py",
    "rendering.py",
    "exporter.py",
)
