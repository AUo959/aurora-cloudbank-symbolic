"""Deterministic Phase-6 sensing/EW/targeting/weapons runtime."""

from .constants import PHASE6_CONTRACT_ID, PHASE6_VERSION
from .kernel import (
    Phase6Error,
    build_observation_state,
    step_phase6_state,
)

__all__ = [
    "PHASE6_CONTRACT_ID",
    "PHASE6_VERSION",
    "Phase6Error",
    "build_observation_state",
    "step_phase6_state",
]
__version__ = PHASE6_VERSION
