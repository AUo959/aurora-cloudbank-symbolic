"""
AuMemManager - Advanced Hierarchical Memory Management Module

This module provides quantum-symbolic memory management with three-tier architecture,
quantum vector flight control, and attention-based retrieval for Aurora CloudBank.

Features:
- Hierarchical memory tiers (Active/Compressed/Archived)
- Quantum-symbolic vector flight control
- Attention-based retrieval with learned importance
- Lossy compression with semantic anchor preservation
- Production-ready implementation with threading support

Integration with Aurora CloudBank:
- DLP tracking and symbolic anchor compliance  
- CASK cultural awareness integration
- Sonnet4 enhanced reasoning capabilities
- SSMT v3.0 automation compatibility
"""

from .hierarchical_memory import (
    HierarchicalMemoryManager,
    MemoryItem,
    MemoryType,
    MemoryStatus,
    QuantumSymbolicVector,
    AttentionWeight
)

from .quantum_flight_control import (
    QuantumFlightController
)

__version__ = "1.0.0"
__author__ = "Aurora CloudBank Integration Team"

# Export main classes for easy import
__all__ = [
    'HierarchicalMemoryManager',
    'MemoryItem', 
    'MemoryType',
    'MemoryStatus',
    'QuantumSymbolicVector',
    'AttentionWeight',
    'QuantumFlightController'
]