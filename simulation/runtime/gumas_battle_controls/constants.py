"""Versioned constants for the GUMAS Phase-11 battle controls and Run-0 harness."""

PHASE11_CONTRACT_ID = "GUMAS_DETERMINISM_SUBSTITUTION_CONTROLS_RUN0_v1_0"
PHASE11_VERSION = "1.0.0"
CANONICAL_JSON_PROFILE = "aurora-canonical-json-v1"
HISTORICAL_CANON_STATUS = "non_canon_simulation_instance"

AUTHORITY_SCHEMA = "aurora://simulation/gumas/phase11_execution_authority/v1.0"
REFUSAL_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase11_refusal_receipt/v1.0"
RUN_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase11_run_receipt/v1.0"
CONTROL_RECEIPT_SCHEMA = "aurora://simulation/gumas/phase11_control_receipt/v1.0"
EVIDENCE_SCHEMA = "aurora://simulation/gumas/phase11_controls_evidence/v1.0"

CAPABILITY_CONTROLS = "gumas_battle_controls_execution"
CAPABILITY_RUN0 = "gumas_run0_execution"
CAPABILITIES = frozenset({CAPABILITY_CONTROLS, CAPABILITY_RUN0})

SCOPE_REPOSITORY = "AUo959/aurora-cloudbank-symbolic"
SCOPE_BASELINE_ID = "SIM-L2-FR-P17-EQUAL-001"
SCOPE_BASELINE_VERSION = "1.2"

VARIANT_CONTROL = "control"
VARIANT_CLASS = "class_substitution"
VARIANT_POLITY = "polity_substitution"
VARIANTS = (VARIANT_CONTROL, VARIANT_CLASS, VARIANT_POLITY)

# Control B: the source set's own substitution witness, applied to each side so
# the frozen material-symmetry contract still holds (19 vessels per side).
CLASS_SUBSTITUTION = {
    "remove_baseline_class_id": "CLASS-PEREGRINE-01",
    "remove_count": 1,
    "add": {
        "class_id": "CLASS-BASTION-01",
        "class_name": "Bastion-Class",
        "count": 1,
        "role": "orbital_defense",
    },
    "add_canonrec_class_id": "cls_bastion",
}

# Control C: the operating CanonRec authority changes; hardware is unchanged.
# org_union_naval_forces is Union-bound, so every control class still binds.
POLITY_SUBSTITUTION = {
    "authority_id": "org_union_naval_forces",
    "source": {
        "kind": "organization",
        "path": "canon/L2/entities/organizations/org_union_naval_forces.json",
    },
}

# Safety bound on a single run; Phase 8 terminates at the 6 h hard limit
# (2,160 ten-second macrosteps), so a correct run never reaches this.
MAX_MACROSTEPS = 2_200
