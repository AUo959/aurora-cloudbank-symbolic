"""
Ethical Data Guardian Module

Purpose: Automated detection and masking of sensitive attributes (PII)
         prior to model ingestion or export.

Anchor: T1-EDG-001 (Foundation Layer)
DLP Context: DATA-GUARDIAN-FOUNDATION-V1
Integration: FastAPI middleware interceptor

Features:
- Real-time PII detection (email, SSN, phone, credit cards, etc.)
- Configurable redaction rules per region/policy
- Audit trail of all redaction operations
- Performance optimized for high-throughput scenarios
"""

__version__ = "0.1.0"
__anchor__ = "T1-EDG-001"

from .detection_rules import PIIDetector, DetectionRule
from .middleware import DataGuardianMiddleware
from .redaction import RedactionEngine

__all__ = [
    "PIIDetector",
    "DetectionRule", 
    "DataGuardianMiddleware",
    "RedactionEngine",
]
