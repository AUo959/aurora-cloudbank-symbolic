"""Aurora Fusion package.

A composable layer that assembles high-value, battle-tested modules from
Aurora CloudBank into a new runtime profile without replacing existing systems.
"""

from .engine import AuroraFusionEngine
from .module_map import ModuleSignal, get_high_value_module_matrix
from .profiles import FUSION_PROFILES, FusionProfile

__all__ = [
    "AuroraFusionEngine",
    "FusionProfile",
    "FUSION_PROFILES",
    "ModuleSignal",
    "get_high_value_module_matrix",
]

