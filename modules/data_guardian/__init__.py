"""
T1-EDG - Ethical Data Guardian Module
Aurora CloudBank data privacy and PII protection system.

Chain: #005//001/EDG
Anchor: T1-EDG-001
Version: 0.1.0
"""

from .detection_rules import PIIDetector, DetectionRule, PIIType
from .redaction import RedactionEngine, RedactionStrategy
from .middleware import DataGuardianMiddleware
from .cli import DataGuardianCLI

__all__ = [
    "PIIDetector",
    "DetectionRule",
    "PIIType",
    "RedactionEngine",
    "RedactionStrategy",
    "DataGuardianMiddleware",
    "DataGuardianCLI",
]

__version__ = "0.1.0"
__anchor__ = "T1-EDG-001"
