"""
Trustworthy Insight Ledger

Immutable, cryptographically-signed audit trail for AI insights, decisions,
and analysis results. Provides transparency, accountability, and verification.

Anchor: T1-TIL-001
Version: 0.1.0
"""

from .crypto_signatures import SignatureManager, VerificationResult
from .ledger_core import EntryType, InsightLedger, LedgerEntry
from .schemas import AuditQuery, InsightRecord, LedgerStats

__version__ = "0.1.0"
__anchor__ = "T1-TIL-001"

__all__ = [
    # Core Ledger
    "InsightLedger",
    "LedgerEntry",
    "EntryType",
    # Cryptography
    "SignatureManager",
    "VerificationResult",
    # Schemas
    "InsightRecord",
    "AuditQuery",
    "LedgerStats",
]
