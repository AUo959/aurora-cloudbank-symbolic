"""GUMAS Unified P0-P2: isolated synthetic L2 causal field research kernel."""

from .model import Actor, Corridor, PhysicsProfile, Site, Universe
from .kernel import CausalEngine, FeasibilityError, verify_ledger
from .legacy_political import observe_legacy_political_snapshot
from .bindings import identity_binding_view, prepare_fixture_identity_binding
from .time_alignment import (
    operator_cross_scale_frame, prepare_fixture_clock_anchor,
    project_tactical_interval,
)

__all__ = [
    "Actor", "Corridor", "PhysicsProfile", "Site", "Universe",
    "CausalEngine", "FeasibilityError", "verify_ledger",
    "observe_legacy_political_snapshot",
    "identity_binding_view", "prepare_fixture_identity_binding",
    "operator_cross_scale_frame", "prepare_fixture_clock_anchor",
    "project_tactical_interval",
]
