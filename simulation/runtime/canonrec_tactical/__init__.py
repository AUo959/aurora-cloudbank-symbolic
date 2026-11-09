"""Deterministic CanonRec tactical resolution for GUMAS."""

from .resolver import (
    CanonRecResolutionError,
    CanonRecTacticalResolver,
    DERIVATION_VERSION,
    RESOLVER_VERSION,
)

__all__ = [
    "CanonRecResolutionError",
    "CanonRecTacticalResolver",
    "DERIVATION_VERSION",
    "RESOLVER_VERSION",
]
