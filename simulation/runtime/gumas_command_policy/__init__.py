"""Deterministic command-team policy for the GUMAS tactical runtime."""

from .policy import POLICY_ID, POLICY_VERSION, decide

__all__ = ["POLICY_ID", "POLICY_VERSION", "decide"]
__version__ = POLICY_VERSION
