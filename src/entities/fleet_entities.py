"""
Aurora CloudBank Living Computation - Fleet Entities
=====================================================

COMPATIBILITY SHIM: This module now imports from the modular fleet package.

All entities have been modularized into src/entities/fleet/ for improved
maintainability. This file preserves backward compatibility by re-exporting
all symbols from the new package structure.

Original monolithic implementation split into:
- fleet/types.py: FleetTelemetry, NavigationPlan dataclasses
- fleet/oppy.py: OPPYNavigator entity
- fleet/aurora_subcore.py: AuroraSubCore entity
- fleet/registry_vessels.py: Vessel singleton accessors
- fleet/registry_probes.py: Probe singleton accessors
- fleet/registry_drones.py: Drone singleton accessors
"""

# Re-export all symbols from modular package
from .fleet import (  # noqa: F401
    # Data types
    FleetTelemetry,
    NavigationPlan,
    # Core entities
    OPPYNavigator,
    AuroraSubCore,
    # Vessel registries
    get_constancy_oppy,
    get_constancy_athena,
    get_helios_oppy,
    get_helios_helion,
    get_liora_oppy,
    get_liora_ai,
    get_archimedes_oppy,
    get_archimedes_daedalus,
    get_pioneer_oppy,
    get_pioneer_mercury,
    get_lacewing_oppy,
    get_lacewing_lyra,
    # Probe registries
    get_alpha_surveyor_oppy,
    get_alpha_surveyor_hermes,
    get_beta_array_oppy,
    get_beta_array_icarus,
    # Drone registries
    get_gamma_swarm_oppy,
    get_gamma_swarm_janus,
    get_delta_scout_oppy,
    get_delta_scout_kepler,
    get_shadowfax_oppy,
    get_shadowfax_lucent,
    get_wisp_oppy,
    get_wisp_mira,
)

__all__ = [
    # Data types
    "FleetTelemetry",
    "NavigationPlan",
    # Core entities
    "OPPYNavigator",
    "AuroraSubCore",
    # Vessel registries
    "get_constancy_oppy",
    "get_constancy_athena",
    "get_helios_oppy",
    "get_helios_helion",
    "get_liora_oppy",
    "get_liora_ai",
    "get_archimedes_oppy",
    "get_archimedes_daedalus",
    "get_pioneer_oppy",
    "get_pioneer_mercury",
    "get_lacewing_oppy",
    "get_lacewing_lyra",
    # Probe registries
    "get_alpha_surveyor_oppy",
    "get_alpha_surveyor_hermes",
    "get_beta_array_oppy",
    "get_beta_array_icarus",
    # Drone registries
    "get_gamma_swarm_oppy",
    "get_gamma_swarm_janus",
    "get_delta_scout_oppy",
    "get_delta_scout_kepler",
    "get_shadowfax_oppy",
    "get_shadowfax_lucent",
    "get_wisp_oppy",
    "get_wisp_mira",
]
