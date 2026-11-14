"""Deterministic GUMAS Phase-9 live observation and macrostep boundary."""

from .constants import PHASE9_CONTRACT_ID, PHASE9_VERSION
from .identity import Phase9Error, source_identity
from .live_observation import derive_live_observations
from .orchestrator import (
    accepted_source_identities,
    execute_macrostep,
    initialize_run_context,
)

__all__ = [
    "PHASE9_CONTRACT_ID",
    "PHASE9_VERSION",
    "Phase9Error",
    "accepted_source_identities",
    "derive_live_observations",
    "execute_macrostep",
    "initialize_run_context",
    "source_identity",
]
__version__ = PHASE9_VERSION
