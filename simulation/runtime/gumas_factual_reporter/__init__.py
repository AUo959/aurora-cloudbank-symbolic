"""Deterministic GUMAS Phase-10 factual reporter and evidence exporter."""

from .constants import (
    PHASE10_CONTRACT_ID,
    PHASE10_VERSION,
    PUBLIC_SUMMARY_PROFILE,
    SIMULATION_TRUTH_PROFILE,
)
from .exporter import export_factual_report
from .identity import Phase10Error, source_identity
from .validation import validate_report_input

__all__ = [
    "PHASE10_CONTRACT_ID",
    "PHASE10_VERSION",
    "PUBLIC_SUMMARY_PROFILE",
    "SIMULATION_TRUTH_PROFILE",
    "Phase10Error",
    "export_factual_report",
    "source_identity",
    "validate_report_input",
]
__version__ = PHASE10_VERSION
