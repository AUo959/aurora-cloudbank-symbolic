"""Deterministic bounded movement and geometry for GUMAS tactical runtime."""

from .constants import MOVEMENT_CONTRACT_ID, MOVEMENT_VERSION
from .kernel import (
    MovementError,
    initialize_motion_state,
    occulted_by_p17,
    order_from_command_receipt,
    pair_geometry,
    step_motion_state,
)

__all__ = [
    "MOVEMENT_CONTRACT_ID",
    "MOVEMENT_VERSION",
    "MovementError",
    "initialize_motion_state",
    "occulted_by_p17",
    "order_from_command_receipt",
    "pair_geometry",
    "step_motion_state",
]
__version__ = MOVEMENT_VERSION
