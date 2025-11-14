"""Compatibility shim for legacy QuantumRenderer imports."""

from modules.opal2.quantum_renderer import (  # noqa: F401
    QuantumRenderer,
    RenderContext,
    RenderMode,
    QuantumState,
    RenderResult,
)

__all__ = [
    "QuantumRenderer",
    "RenderContext",
    "RenderMode",
    "QuantumState",
    "RenderResult",
]
