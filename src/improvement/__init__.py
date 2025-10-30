"""
Aurora Code Improvement Engine Module

Automated code quality enhancement with pattern detection and suggestions.

DLP Integration:
    - Context Tag: code_improvement_engine
    - T1/SRB Anchors: Maintains temporal and symbolic reference base anchors
    - Anchor Protocols: Integrates with NativeDLPTracker for operation lineage
    - Memory Seals: Ensures integrity of improvement suggestions and patterns

Data Lineage Protocol (DLP):
    All improvement operations are tracked through NativeDLPTracker to maintain
    symbolic integrity and traceability. Each analysis, pattern detection, and
    suggestion generation is tagged with context_tag='code_improvement_engine'
    for complete data lineage tracking.

Symbolic Integration:
    - Preserves T1/SRB anchors during code analysis
    - Uses chain notation for improvement pattern tracking
    - Maintains memory seals for suggestion validation
    - Integrates with Aurora's symbolic engine for context propagation
"""

from .engine import (
    CodeImprovementEngine,
    ImprovementSuggestion,
    ImprovementPattern,
    ImprovementCategory,
    ImprovementSeverity,
    get_improvement_engine,
    reset_improvement_engine
)

__all__ = [
    'CodeImprovementEngine',
    'ImprovementSuggestion',
    'ImprovementPattern',
    'ImprovementCategory',
    'ImprovementSeverity',
    'get_improvement_engine',
    'reset_improvement_engine',
]
