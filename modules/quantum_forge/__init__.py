"""
Quantum Forge v2.0 Module

Advanced quantum-symbolic agent generation with ethics enforcement and
constellation binding.

T1: QUANTUM_FORGE_INIT_v2.0
SRB: MODULE_BOUNDARY
DLP: context_tag=qf_init, symbolic_hash=QF_INIT_v2
"""

from modules.quantum_forge.quantum_forge_v2 import (
    QuantumForge,
    GUMAS_Thermax,
    Aurora_Core_Flowstate,
    EthicsLevel,
    FlowstateMode,
    InterventionType,
    SymbolicMemoryNode,
    QuantumAgent
)

__version__ = "2.0.0"

__all__ = [
    "QuantumForge",
    "GUMAS_Thermax",
    "Aurora_Core_Flowstate",
    "EthicsLevel",
    "FlowstateMode",
    "InterventionType",
    "SymbolicMemoryNode",
    "QuantumAgent"
]
