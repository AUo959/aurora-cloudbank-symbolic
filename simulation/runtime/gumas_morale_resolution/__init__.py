"""Deterministic GUMAS Phase-8 morale and battle-resolution runtime."""
from .kernel import Phase8Error, step_phase8_state
__all__ = ["Phase8Error", "step_phase8_state"]
