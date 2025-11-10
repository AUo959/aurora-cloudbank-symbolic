"""Fleet entity modular package.

Public re-exports maintained for backward compatibility with existing imports
expecting `src.entities.fleet_entities` contents.

Modules are imported with graceful degradation to avoid breaking imports while
modularization is in progress.
"""

from .types import FleetTelemetry, NavigationPlan  # noqa: F401

__all__ = [
    # Data types
    "FleetTelemetry",
    "NavigationPlan",
]

# Optional: OPPY navigator
try:
    from .oppy import OPPYNavigator  # type: ignore  # noqa: F401

    __all__.append("OPPYNavigator")
except Exception:  # pragma: no cover - module may be missing during refactor
    OPPYNavigator = None  # type: ignore

# Optional: Aurora sub-core
try:
    from .aurora_subcore import AuroraSubCore  # type: ignore  # noqa: F401

    __all__.append("AuroraSubCore")
except Exception:  # pragma: no cover
    AuroraSubCore = None  # type: ignore

# Optional: Vessel registries
try:
    from .registry_vessels import (  # noqa: F401
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
    )

    __all__.extend(
        [
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
        ]
    )
except Exception:  # pragma: no cover
    pass

# Optional: Probe registries
try:
    from .registry_probes import (  # noqa: F401
        get_alpha_surveyor_oppy,
        get_alpha_surveyor_hermes,
        get_beta_array_oppy,
        get_beta_array_icarus,
    )

    __all__.extend(
        [
            "get_alpha_surveyor_oppy",
            "get_alpha_surveyor_hermes",
            "get_beta_array_oppy",
            "get_beta_array_icarus",
        ]
    )
except Exception:  # pragma: no cover
    pass

# Optional: Drone registries
try:
    from .registry_drones import (  # noqa: F401
        get_gamma_swarm_oppy,
        get_gamma_swarm_janus,
        get_delta_scout_oppy,
        get_delta_scout_kepler,
        get_shadowfax_oppy,
        get_shadowfax_lucent,
        get_wisp_oppy,
        get_wisp_mira,
    )

    __all__.extend(
        [
            "get_gamma_swarm_oppy",
            "get_gamma_swarm_janus",
            "get_delta_scout_oppy",
            "get_delta_scout_kepler",
            "get_shadowfax_oppy",
            "get_shadowfax_lucent",
            "get_wisp_oppy",
            "get_wisp_mira",
        ]
    )
except Exception:  # pragma: no cover
    pass
