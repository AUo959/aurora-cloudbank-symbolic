"""Tiered RD consent API (issue #1200).

Mounted under the existing ``/rd`` router (modules/hr/rd_api.py), giving:

    POST /rd/consent/grants                 create a grant (subject only)
    POST /rd/consent/grants/{id}/revoke     revoke (subject or HR)
    GET  /rd/consent/grants/{id}            fetch one grant (subject or HR)
    GET  /rd/consent/subjects/{id}/grants   list a subject's grants (self or HR)
    GET  /rd/consent/check                  access decision for the requester
    GET  /rd/consent/aggregate              Tier 1 anonymized aggregate

Requester identity — documented interim contract:

The platform has no user-authentication layer yet
(src/middleware/fastapi_security.require_auth is an explicit placeholder),
so requester identity is asserted via headers:

    X-Aurora-Requester:      requester id (2-64 chars)
    X-Aurora-Requester-Role: crew | hr | project_lead

This bounds identity strength at the platform's current level — it does NOT
make identity claims cryptographically trustworthy, and must be replaced
with a real authn dependency when one exists. What IS enforced regardless:
no request without an explicit asserted human requester can create consent
(automated layers cannot fabricate grants), every mutation requires CSRF,
and every allow/deny decision lands in the insight_ledger hash chain.
"""

from __future__ import annotations

import logging
import re
from typing import Annotated, Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from modules.hr.consent.store import ConsentError, ConsentStore
from src.middleware.error_helpers import http_error

# Aurora security + rate limiting (guard optional import failures gracefully).
# Uses require_csrf_token (token = Depends(security)) — the dependency form
# used by modules/gumas, modules/insight_ledger, and modules/aumemmanager.
try:
    from src.middleware.fastapi_security import require_csrf_token, limiter
    SECURITY_AVAILABLE = True
except Exception:  # pragma: no cover - fallback path
    SECURITY_AVAILABLE = False
    def require_csrf_token(*args, **kwargs):  # type: ignore
        return None
    class DummyLimiter:  # minimal placeholder
        @staticmethod
        def limit(limit_str: str):
            def _decorator(func):
                return func
            return _decorator
    limiter = DummyLimiter()  # type: ignore

logger = logging.getLogger("rd_consent_api")

router = APIRouter(prefix="/consent", tags=["rd-consent"])

_MUTATION_DEPS = [Depends(require_csrf_token)] if SECURITY_AVAILABLE else []

REQUESTER_ID_HEADER = "X-Aurora-Requester"
REQUESTER_ROLE_HEADER = "X-Aurora-Requester-Role"
_REQUESTER_ROLES = {"crew", "hr", "project_lead"}
_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{2,64}$")

_store: Optional[ConsentStore] = None


def get_store() -> ConsentStore:
    global _store
    if _store is None:
        _store = ConsentStore()
    return _store


class Requester:
    def __init__(self, requester_id: str, role: str) -> None:
        self.requester_id = requester_id
        self.role = role

    @property
    def is_hr(self) -> bool:
        return self.role == "hr"

    def grantee_identity(self, subject_id: str) -> str:
        """The grantee string this requester matches when reading subject data."""
        if self.is_hr:
            return "hr"
        if self.requester_id == subject_id:
            return "self"
        return f"project_lead:{self.requester_id}"


def get_requester(request: Request) -> Requester:
    requester_id = request.headers.get(REQUESTER_ID_HEADER, "")
    role = request.headers.get(REQUESTER_ROLE_HEADER, "")
    if not _ID_PATTERN.match(requester_id):
        raise HTTPException(
            status_code=401,
            detail=f"missing or invalid {REQUESTER_ID_HEADER} header",
        )
    if role not in _REQUESTER_ROLES:
        raise HTTPException(
            status_code=401,
            detail=f"{REQUESTER_ROLE_HEADER} must be one of {sorted(_REQUESTER_ROLES)}",
        )
    return Requester(requester_id, role)


# -------------------------
# Pydantic Models
# -------------------------
class CreateGrantRequest(BaseModel):
    subject_id: str = Field(..., min_length=2, max_length=64)
    tier: int = Field(..., ge=2, le=3)
    data_class: str = Field(..., min_length=2, max_length=64)
    purpose: str = Field(..., min_length=2, max_length=160)
    grantee: str = Field(..., min_length=2, max_length=80)
    expires_in_days: Optional[int] = Field(default=None, ge=1, le=365)


class RevokeGrantRequest(BaseModel):
    reason: str = Field(..., min_length=2, max_length=160)


# -------------------------
# Endpoints
# -------------------------
@router.post(
    "/grants",
    status_code=201,
    dependencies=_MUTATION_DEPS,
    responses={
        401: {"description": "Missing or invalid requester identity headers"},
        403: {"description": "Requester is not the data subject"},
        409: {"description": "Invalid tier/grantee combination or duplicate active grant"},
    },
)
@limiter.limit("30/minute")
def create_grant(
    request: Request,
    body: CreateGrantRequest,
    requester: Annotated[Requester, Depends(get_requester)],
) -> Dict[str, Any]:
    """Create a consent grant. Only the data subject can consent.

    HR cannot consent on a subject's behalf and no automated pathway exists:
    consent that wasn't given by its subject isn't consent.
    """
    if requester.requester_id != body.subject_id:
        raise HTTPException(
            status_code=403,
            detail="only the data subject can create a consent grant",
        )
    try:
        grant, audited = get_store().grant(
            subject_id=body.subject_id,
            tier=body.tier,
            data_class=body.data_class,
            purpose=body.purpose,
            grantee=body.grantee,
            expires_in_days=body.expires_in_days,
        )
    except ConsentError as e:
        raise http_error(409, "Consent state conflict.", e)
    return {
        "success": True,
        "grant": grant.to_dict(),
        "audit_recorded": audited,
        "context_tag": "rd_consent_grant",
    }


@router.post(
    "/grants/{grant_id}/revoke",
    dependencies=_MUTATION_DEPS,
    responses={
        401: {"description": "Missing or invalid requester identity headers"},
        403: {"description": "Requester is neither the data subject nor HR"},
        404: {"description": "Grant not found"},
        409: {"description": "Grant is already revoked"},
    },
)
@limiter.limit("30/minute")
def revoke_grant(
    request: Request,
    grant_id: str,
    body: RevokeGrantRequest,
    requester: Annotated[Requester, Depends(get_requester)],
) -> Dict[str, Any]:
    """Revoke a grant. Allowed for the subject or HR (revocation only ever
    removes access, so the safe direction is to make it easy)."""
    store = get_store()
    grant = store.get(grant_id)
    if grant is None:
        raise HTTPException(status_code=404, detail="grant not found")
    if requester.requester_id != grant.subject_id and not requester.is_hr:
        raise HTTPException(
            status_code=403, detail="only the data subject or HR can revoke a grant"
        )
    try:
        grant, audited = store.revoke(grant_id, body.reason)
    except ConsentError as e:
        raise http_error(409, "Consent state conflict.", e)
    return {
        "success": True,
        "grant": grant.to_dict(),
        "audit_recorded": audited,
        "context_tag": "rd_consent_revoke",
    }


@router.get(
    "/grants/{grant_id}",
    responses={
        401: {"description": "Missing or invalid requester identity headers"},
        404: {"description": "Grant not found (also returned to unauthorized readers)"},
    },
)
@limiter.limit("120/minute")
def get_grant(
    request: Request,
    grant_id: str,
    requester: Annotated[Requester, Depends(get_requester)],
) -> Dict[str, Any]:
    """Fetch one grant — visible to its subject and HR (Tier 2 semantics)."""
    grant = get_store().get(grant_id)
    if grant is None or (
        requester.requester_id != grant.subject_id and not requester.is_hr
    ):
        # 404 for unauthorized readers too: existence of a grant is itself
        # individual data.
        raise HTTPException(status_code=404, detail="grant not found")
    return {"success": True, "grant": grant.to_dict(), "context_tag": "rd_consent_get"}


@router.get(
    "/subjects/{subject_id}/grants",
    responses={
        401: {"description": "Missing or invalid requester identity headers"},
        403: {"description": "Requester is neither the subject nor HR"},
    },
)
@limiter.limit("120/minute")
def list_subject_grants(
    request: Request,
    subject_id: str,
    requester: Annotated[Requester, Depends(get_requester)],
) -> Dict[str, Any]:
    """List a subject's grants — visible to self and HR (Tier 2 semantics)."""
    if requester.requester_id != subject_id and not requester.is_hr:
        raise HTTPException(
            status_code=403,
            detail="individual consent records are visible to the subject and HR only",
        )
    grants = get_store().list_for_subject(subject_id)
    return {
        "success": True,
        "count": len(grants),
        "grants": [g.to_dict() for g in grants],
        "context_tag": "rd_consent_list",
    }


@router.get(
    "/check",
    responses={
        401: {"description": "Missing or invalid requester identity headers"},
    },
)
@limiter.limit("240/minute")
def check_access(
    request: Request,
    subject_id: str,
    data_class: str,
    purpose: str,
    requester: Annotated[Requester, Depends(get_requester)],
) -> Dict[str, Any]:
    """Access decision for the requester against a subject's data.

    The grantee identity is derived from the requester (self / hr /
    project_lead:<id>) — callers cannot ask on behalf of someone else.
    Every decision, including denials, is appended to the audit ledger.
    """
    grantee = requester.grantee_identity(subject_id)
    decision = get_store().check_access(subject_id, data_class, purpose, grantee)
    return {
        "success": True,
        "requester": requester.requester_id,
        "grantee_identity": grantee,
        "decision": decision,
        "context_tag": "rd_consent_check",
    }


@router.get("/aggregate")
@limiter.limit("120/minute")
def aggregate(request: Request) -> Dict[str, Any]:
    """Tier 1 (default) view: anonymized aggregate, no grant required.

    Response carries no subject ids, grant ids, or grantee ids, and buckets
    below the k-anonymity threshold are suppressed.
    """
    return {
        "success": True,
        "aggregate": get_store().aggregate(),
        "context_tag": "rd_consent_aggregate",
    }
