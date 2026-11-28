"""Deterministic GUMAS Phase-11 controls (A replay, B class, C polity) and Run 0."""

from .authority import preflight, refusal_receipt, require, seal_authority
from .constants import (
    CAPABILITY_CONTROLS,
    CAPABILITY_RUN0,
    PHASE11_CONTRACT_ID,
    PHASE11_VERSION,
    VARIANTS,
)
from .controls import execute_controls, execute_variant, verify_evidence
from .identity import Phase11Error, source_identity
from .inputs import check_input_deltas, derive_documents, resolve_inputs
from .runner import export_reports, run_receipt, run_to_termination

__all__ = [
    "CAPABILITY_CONTROLS",
    "CAPABILITY_RUN0",
    "PHASE11_CONTRACT_ID",
    "PHASE11_VERSION",
    "Phase11Error",
    "VARIANTS",
    "check_input_deltas",
    "derive_documents",
    "execute_controls",
    "execute_variant",
    "export_reports",
    "preflight",
    "refusal_receipt",
    "require",
    "resolve_inputs",
    "run_receipt",
    "run_to_termination",
    "seal_authority",
    "source_identity",
    "verify_evidence",
]
__version__ = PHASE11_VERSION
