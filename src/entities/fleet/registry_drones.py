"""Drone registry accessors (modularized)."""
from __future__ import annotations

from typing import Optional

from .oppy import OPPYNavigator
from .aurora_subcore import AuroraSubCore

__all__ = [
    "get_gamma_swarm_oppy",
    "get_gamma_swarm_janus",
    "get_delta_scout_oppy",
    "get_delta_scout_kepler",
    "get_shadowfax_oppy",
    "get_shadowfax_lucent",
    "get_wisp_oppy",
    "get_wisp_mira",
]


# Global instances for ORD-1 Gamma Swarm
_gamma_swarm_oppy: Optional[OPPYNavigator] = None
_gamma_swarm_janus: Optional[AuroraSubCore] = None


def get_gamma_swarm_oppy() -> OPPYNavigator:
    """Get OPPY Swarm Kernel for ORD-1 Gamma Swarm maintenance drones."""
    global _gamma_swarm_oppy
    if _gamma_swarm_oppy is None:
        _gamma_swarm_oppy = OPPYNavigator(vessel_id="ORD-1")
    return _gamma_swarm_oppy


def get_gamma_swarm_janus() -> AuroraSubCore:
    """Get Aurora Sub-Node J (Janus 'The Gatekeeper') for ORD-1 Gamma Swarm."""
    global _gamma_swarm_janus
    if _gamma_swarm_janus is None:
        _gamma_swarm_janus = AuroraSubCore(
            subcore_id="AURORA_SUB_JANUS",
            vessel_id="ORD-1"
        )
    return _gamma_swarm_janus


# Global instances for ORD-2 Delta Scout
_delta_scout_oppy: Optional[OPPYNavigator] = None
_delta_scout_kepler: Optional[AuroraSubCore] = None


def get_delta_scout_oppy() -> OPPYNavigator:
    """Get OPPY Recon Node for ORD-2 Delta Scout reconnaissance drone."""
    global _delta_scout_oppy
    if _delta_scout_oppy is None:
        _delta_scout_oppy = OPPYNavigator(vessel_id="ORD-2")
    return _delta_scout_oppy


def get_delta_scout_kepler() -> AuroraSubCore:
    """Get Aurora Sub-Node K (Kepler 'The Observer') for ORD-2 Delta Scout."""
    global _delta_scout_kepler
    if _delta_scout_kepler is None:
        _delta_scout_kepler = AuroraSubCore(
            subcore_id="AURORA_SUB_KEPLER",
            vessel_id="ORD-2"
        )
    return _delta_scout_kepler


# Global instances for ORD-3 Shadowfax
_shadowfax_oppy: Optional[OPPYNavigator] = None
_shadowfax_lucent: Optional[AuroraSubCore] = None


def get_shadowfax_oppy() -> OPPYNavigator:
    """Get OPPY Audit Kernel for ORD-3 Shadowfax audit drone."""
    global _shadowfax_oppy
    if _shadowfax_oppy is None:
        _shadowfax_oppy = OPPYNavigator(vessel_id="ORD-3")
    return _shadowfax_oppy


def get_shadowfax_lucent() -> AuroraSubCore:
    """Get Aurora Sub-Node L (Lucent 'The Illuminator') for ORD-3 Shadowfax."""
    global _shadowfax_lucent
    if _shadowfax_lucent is None:
        _shadowfax_lucent = AuroraSubCore(
            subcore_id="AURORA_SUB_LUCENT",
            vessel_id="ORD-3"
        )
    return _shadowfax_lucent


# Global instances for ORD-4 Wisp
_wisp_oppy: Optional[OPPYNavigator] = None
_wisp_mira: Optional[AuroraSubCore] = None


def get_wisp_oppy() -> OPPYNavigator:
    """Get OPPY Courier Core for ORD-4 Wisp courier drone."""
    global _wisp_oppy
    if _wisp_oppy is None:
        _wisp_oppy = OPPYNavigator(vessel_id="ORD-4")
    return _wisp_oppy


def get_wisp_mira() -> AuroraSubCore:
    """Get Aurora Sub-Node M (Mira 'The Messenger') for ORD-4 Wisp."""
    global _wisp_mira
    if _wisp_mira is None:
        _wisp_mira = AuroraSubCore(
            subcore_id="AURORA_SUB_MIRA",
            vessel_id="ORD-4"
        )
    return _wisp_mira
