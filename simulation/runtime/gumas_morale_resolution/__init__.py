"""Deterministic GUMAS Phase-8 morale and battle-resolution runtime boundary."""
from . import kernel as _kernel
from .boundary import Phase8Error, boundary_source_identity, step_phase8_state

# Patch the public kernel entry point so direct submodule imports also receive
# the authoritative validated boundary, matching the accepted Phase-7 pattern.
_kernel.step_phase8_state = step_phase8_state

__all__ = [
    "Phase8Error",
    "boundary_source_identity",
    "step_phase8_state",
]
