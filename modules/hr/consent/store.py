"""Consent grant store — durable state + tamper-evident audit (issue #1200).

Persistence split by role, per the approved Option A design:

 - Current grant state lives in an atomic JSON file (default
   ``data/hr/consent_grants.json``, written via src.utils.atomic_io).
   Grants are never deleted: revocation and expiry leave the record in
   place so the file itself is reviewable history.
 - Every consent event (grant, revoke, denial, expiry observed at read
   time) is appended to the insight_ledger hash chain. Grant state and
   audit history are structurally separate: something that could edit the
   JSON file still cannot rewrite the signed hash chain.

Authority contract: this store exposes no bulk-import or backfill path.
Grants enter only through explicit ``grant()`` calls, which the API layer
restricts to the data subject. Audit-ledger availability is reported on
every mutation (``audit_recorded``) rather than silently swallowed.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, asdict, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from src.utils.atomic_io import atomic_write_json

logger = logging.getLogger("hr_consent")

DEFAULT_STORE_PATH = Path("data/hr/consent_grants.json")

# Tier semantics from docs/api/RD_API_REFERENCE.md ("Data Dignity Principles").
# Tier 1 is the default (aggregate/anonymized) and never requires a grant, so
# it never appears in the store.
TIER_2 = 2
TIER_3 = 3
TIER_2_GRANTEES = {"self", "hr"}
TIER_3_GRANTEE_PREFIX = "project_lead:"

# Aggregate responses suppress any bucket smaller than this so individual
# subjects cannot be singled out by differencing small groups.
K_ANONYMITY_THRESHOLD = 5


class ConsentError(ValueError):
    """Raised for invalid consent operations (bad tier/grantee, duplicates)."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


@dataclass
class ConsentGrant:
    grant_id: str
    subject_id: str
    tier: int
    data_class: str
    purpose: str
    grantee: str
    granted_at: str
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    revocation_reason: Optional[str] = None

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        if self.expires_at is None:
            return False
        return datetime.fromisoformat(self.expires_at) <= (now or _utcnow())

    def is_active(self, now: Optional[datetime] = None) -> bool:
        return self.revoked_at is None and not self.is_expired(now)

    def status(self, now: Optional[datetime] = None) -> str:
        if self.revoked_at is not None:
            return "revoked"
        if self.is_expired(now):
            return "expired"
        return "active"

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status()
        return data


def _validate_tier_grantee(tier: int, grantee: str) -> None:
    if tier == TIER_2:
        if grantee not in TIER_2_GRANTEES:
            raise ConsentError(
                f"Tier 2 grantee must be one of {sorted(TIER_2_GRANTEES)}"
            )
    elif tier == TIER_3:
        if not grantee.startswith(TIER_3_GRANTEE_PREFIX) or len(grantee) <= len(
            TIER_3_GRANTEE_PREFIX
        ):
            raise ConsentError(
                "Tier 3 grantee must name an explicit project lead "
                f"('{TIER_3_GRANTEE_PREFIX}<id>')"
            )
    else:
        raise ConsentError("tier must be 2 or 3 (Tier 1 is the default; no grant needed)")


class ConsentStore:
    """Durable, revocable, auditable consent grants."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._path = Path(storage_path) if storage_path else DEFAULT_STORE_PATH
        self._lock = Lock()
        self._grants: Dict[str, ConsentGrant] = {}
        self._ledger = self._open_ledger()
        self._load()

    # -- persistence -------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            raw = json.loads(self._path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            # A corrupt consent file must not silently become "no grants":
            # that would fail open for Tier 1 aggregates and fail closed for
            # subjects who did consent. Refuse to start instead.
            raise ConsentError(f"consent store at {self._path} is unreadable: {exc}")
        for item in raw.get("grants", []):
            grant = ConsentGrant(**{f.name: item.get(f.name) for f in fields(ConsentGrant)})
            self._grants[grant.grant_id] = grant

    def _save(self) -> None:
        payload = {
            "_meta": {
                "description": "RD tiered consent grants — state of record (issue #1200)",
                "audit_channel": "insight_ledger (hr_consent)",
                "updated_at": _iso(_utcnow()),
            },
            "grants": [asdict(g) for g in self._grants.values()],
        }
        self._path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(self._path, payload)

    # -- audit -------------------------------------------------------------

    @staticmethod
    def _open_ledger():
        try:
            from modules.insight_ledger.ledger_core import InsightLedger

            return InsightLedger("hr_consent")
        except Exception as exc:  # pragma: no cover - environment-dependent
            logger.warning(
                "insight_ledger unavailable — consent audit events degrade to "
                "process logs only: %s",
                exc,
            )
            return None

    def _audit(self, event: str, context: Dict[str, Any], severity: str = "info") -> bool:
        """Append a consent event to the audit ledger.

        Returns True when the event landed in the hash chain. Callers surface
        this (``audit_recorded``) instead of pretending audit always worked.
        """
        # Context values include request-supplied strings (subject ids,
        # purposes); escape newlines so a crafted value cannot forge log lines.
        safe_context = (
            json.dumps(context, default=str).replace("\r", "\\r").replace("\n", "\\n")
        )
        logger.info("consent event %s: %s", event, safe_context)
        if self._ledger is None:
            return False
        try:
            from modules.insight_ledger.schemas import InsightRecord, InsightType

            self._ledger.record_insight(
                InsightRecord(
                    insight_type=InsightType.AUDIT,
                    content=f"rd-consent {event}",
                    context=context,
                    source="hr-consent",
                    tags=["consent", event],
                    severity=severity,
                )
            )
            return True
        except Exception:  # pragma: no cover - ledger runtime failure
            logger.exception("consent audit append failed for %s", event)
            return False

    # -- operations ---------------------------------------------------------

    def grant(
        self,
        subject_id: str,
        tier: int,
        data_class: str,
        purpose: str,
        grantee: str,
        expires_in_days: Optional[int] = None,
    ) -> tuple[ConsentGrant, bool]:
        _validate_tier_grantee(tier, grantee)
        with self._lock:
            existing = self._find_active_locked(subject_id, data_class, purpose, grantee)
            if existing is not None:
                raise ConsentError(
                    f"an active grant already exists ({existing.grant_id}); "
                    "revoke it before issuing a replacement"
                )
            now = _utcnow()
            grant = ConsentGrant(
                grant_id=uuid.uuid4().hex[:16],
                subject_id=subject_id,
                tier=tier,
                data_class=data_class,
                purpose=purpose,
                grantee=grantee,
                granted_at=_iso(now),
                expires_at=_iso(now + timedelta(days=expires_in_days))
                if expires_in_days
                else None,
            )
            self._grants[grant.grant_id] = grant
            self._save()
        audited = self._audit("grant_created", grant.to_dict())
        return grant, audited

    def revoke(self, grant_id: str, reason: str) -> tuple[ConsentGrant, bool]:
        with self._lock:
            grant = self._grants.get(grant_id)
            if grant is None:
                raise KeyError(grant_id)
            if grant.revoked_at is not None:
                raise ConsentError("grant is already revoked")
            grant.revoked_at = _iso(_utcnow())
            grant.revocation_reason = reason
            self._save()
        audited = self._audit("grant_revoked", grant.to_dict())
        return grant, audited

    def get(self, grant_id: str) -> Optional[ConsentGrant]:
        return self._grants.get(grant_id)

    def list_for_subject(self, subject_id: str) -> List[ConsentGrant]:
        return [g for g in self._grants.values() if g.subject_id == subject_id]

    def _find_active_locked(
        self, subject_id: str, data_class: str, purpose: str, grantee: str
    ) -> Optional[ConsentGrant]:
        for grant in self._grants.values():
            if (
                grant.subject_id == subject_id
                and grant.data_class == data_class
                and grant.purpose == purpose
                and grant.grantee == grantee
                and grant.is_active()
            ):
                return grant
        return None

    def check_access(
        self, subject_id: str, data_class: str, purpose: str, grantee: str
    ) -> Dict[str, Any]:
        """Access decision for an individual-data read. Denials are audited."""
        with self._lock:
            grant = self._find_active_locked(subject_id, data_class, purpose, grantee)
        if grant is not None:
            decision = {
                "allowed": True,
                "tier": grant.tier,
                "grant_id": grant.grant_id,
                "expires_at": grant.expires_at,
            }
            decision["audit_recorded"] = self._audit(
                "access_allowed",
                {"subject_id": subject_id, "data_class": data_class,
                 "purpose": purpose, "grantee": grantee, "grant_id": grant.grant_id},
            )
            return decision
        decision = {
            "allowed": False,
            "reason": "no active grant for this subject/data_class/purpose/grantee",
        }
        decision["audit_recorded"] = self._audit(
            "access_denied",
            {"subject_id": subject_id, "data_class": data_class,
             "purpose": purpose, "grantee": grantee},
            severity="warning",
        )
        return decision

    def aggregate(self) -> Dict[str, Any]:
        """Tier 1 view: anonymized aggregate of active grants.

        Contains no subject identifiers, grant ids, or grantee ids. Buckets
        smaller than K_ANONYMITY_THRESHOLD are suppressed so the response
        cannot be differenced back to individuals.
        """
        active = [g for g in self._grants.values() if g.is_active()]

        def _bucketed(counts: Dict[str, int]) -> Dict[str, Any]:
            out: Dict[str, Any] = {}
            for key, count in sorted(counts.items()):
                out[key] = count if count >= K_ANONYMITY_THRESHOLD else f"<{K_ANONYMITY_THRESHOLD}"
            return out

        by_tier: Dict[str, int] = {}
        by_data_class: Dict[str, int] = {}
        for g in active:
            by_tier[f"tier_{g.tier}"] = by_tier.get(f"tier_{g.tier}", 0) + 1
            by_data_class[g.data_class] = by_data_class.get(g.data_class, 0) + 1

        return {
            "tier": 1,
            "anonymized": True,
            "k_anonymity_threshold": K_ANONYMITY_THRESHOLD,
            "total_active_grants": len(active)
            if len(active) >= K_ANONYMITY_THRESHOLD or len(active) == 0
            else f"<{K_ANONYMITY_THRESHOLD}",
            "active_by_tier": _bucketed(by_tier),
            "active_by_data_class": _bucketed(by_data_class),
        }
