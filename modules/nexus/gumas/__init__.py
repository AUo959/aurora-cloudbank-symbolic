#!/usr/bin/env python3
"""
GUMAS/Orion Status Module Package
Anchor: T8-STATUS-GUMAS-2025
Seed: EOS_SEED_ORION
"""

from .gumas_orion_status_enhanced import (
    GUMASOrionStatusModule,
    EntropyState,
    StatusSnapshot,
    SYMBOLIC_ANCHORS,
    THREAD_CHAIN,
    create_status_module,
    run_status_check
)

__all__ = [
    'GUMASOrionStatusModule',
    'EntropyState', 
    'StatusSnapshot',
    'SYMBOLIC_ANCHORS',
    'THREAD_CHAIN',
    'create_status_module',
    'run_status_check'
]

__version__ = "8.1.0"
__anchor__ = "T8-STATUS-GUMAS-2025"
__seed__ = "EOS_SEED_ORION"