"""Tiered RD consent management (issue #1200).

Implements the three-tier Consent Architecture described in
docs/api/RD_API_REFERENCE.md:

 - Tier 1 (Default):          aggregated, anonymized data — no grant needed
 - Tier 2 (Consent Required): individual profiles visible to self and HR
 - Tier 3 (Explicit Request): data shared with a named project lead

Design approved on #1200 (Option A): grant state of record is an atomic
JSON file under data/hr/; every consent event is additionally appended to
the insight_ledger hash chain for tamper-evident audit history.
"""

from .store import ConsentStore, ConsentGrant, ConsentError

__all__ = ["ConsentStore", "ConsentGrant", "ConsentError"]
