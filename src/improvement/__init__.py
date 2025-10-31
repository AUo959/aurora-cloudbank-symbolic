"""
Aurora Code Improvement Engine Module

Automated code quality enhancement with pattern detection and suggestions.
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
