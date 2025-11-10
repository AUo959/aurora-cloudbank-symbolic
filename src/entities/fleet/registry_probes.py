"""Probe registry accessors (modularized)."""
from __future__ import annotations

from typing import Optional

from .oppy import OPPYNavigator
from .aurora_subcore import AuroraSubCore

__all__ = [
    "get_alpha_surveyor_oppy",
    "get_alpha_surveyor_hermes",
    "get_beta_array_oppy",
    "get_beta_array_icarus",
]


# Global instances for Alpha Surveyor
_alpha_surveyor_oppy: Optional[OPPYNavigator] = None
_alpha_surveyor_hermes: Optional[AuroraSubCore] = None


def get_alpha_surveyor_oppy() -> OPPYNavigator:
    """Get OPPY Deep-Survey Core for Alpha Surveyor autonomous probe."""
    global _alpha_surveyor_oppy
    if _alpha_surveyor_oppy is None:
        _alpha_surveyor_oppy = OPPYNavigator(vessel_id="ORP-1")
    return _alpha_surveyor_oppy


def get_alpha_surveyor_hermes() -> AuroraSubCore:
    """Get Aurora Sub-Node H (Hermes 'The Messenger') for Alpha Surveyor probe."""
    global _alpha_surveyor_hermes
    if _alpha_surveyor_hermes is None:
        _alpha_surveyor_hermes = AuroraSubCore(
            subcore_id="AURORA_SUB_HERMES",
            vessel_id="ORP-1"
        )
    return _alpha_surveyor_hermes


# Global instances for Beta Array
_beta_array_oppy: Optional[OPPYNavigator] = None
_beta_array_icarus: Optional[AuroraSubCore] = None


def get_beta_array_oppy() -> OPPYNavigator:
    """Get OPPY Quantum Relay Core for Beta Array quantum-field probe."""
    global _beta_array_oppy
    if _beta_array_oppy is None:
        _beta_array_oppy = OPPYNavigator(vessel_id="ORP-2")
    return _beta_array_oppy


def get_beta_array_icarus() -> AuroraSubCore:
    """Get Aurora Sub-Node I (Icarus 'The Listener') for Beta Array quantum-field probe."""
    global _beta_array_icarus
    if _beta_array_icarus is None:
        _beta_array_icarus = AuroraSubCore(
            subcore_id="AURORA_SUB_ICARUS",
            vessel_id="ORP-2"
        )
    return _beta_array_icarus
