"""
Aurora Subroutine System
========================
Anchor: SUBROUTINE-SYS-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Official subroutine authoring and tracking system for Aurora's neural net.
Provides versioning, provenance, and execution monitoring for all subroutines.
"""

from src.subroutines.reality_sim_monitor import RealitySimMonitor
from src.subroutines.registry import SubroutineRegistry, Subroutine

__version__ = "1.0.0"
__all__ = [
    "RealitySimMonitor",
    "SubroutineRegistry",
    "Subroutine"
]
