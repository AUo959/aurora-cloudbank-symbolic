"""
Superposition Gate

Combines independently-evaluated Verdicts from heterogeneous safety/ethics
evaluators (or heterogeneous execution backends) into one decision via a
deterministic, hard-veto-first collapse rule -- without requiring the source
evaluators to share an implementation or call each other.

This module is intentionally standalone. It is not wired into GUMAS, the
Ethics Field, or quantum_forge yet; integrating it into any of those
existing (currently mutually disconnected) safety subsystems is future work
that can be done independently, one caller at a time, without changing this
module. See README.md in this directory for the design rationale.

DLP: context_tag=superposition_gate_init, symbolic_hash=SUPERPOSITION_GATE_v1
"""

__version__ = "0.1.0"

from .core import EmptyVerdictSetError, collapse
from .models import CollapsedVerdict, Verdict, VerdictSeverity

__all__ = [
    "Verdict",
    "VerdictSeverity",
    "CollapsedVerdict",
    "collapse",
    "EmptyVerdictSetError",
]
