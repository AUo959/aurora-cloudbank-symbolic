"""
API tests for tiered RD consent management (issue #1200).

Covers the issue's acceptance criteria explicitly:
 - grant / denial / revocation / expiry / unauthorized disclosure
 - consent decisions are persisted (across store reload), revocable, auditable
 - individual-data reads enforce an explicit current grant
 - the Tier 1 aggregate response carries no individual identifiers and
   suppresses small buckets

Follows the tests/test_aumemmanager_api.py pattern: env secrets before
imports, slowapi stub, a minimal FastAPI app with just the router under
test, and CSRF bearer tokens from generate_csrf_token.
"""

import json
import os
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests._slowapi_stub import install_slowapi_stub

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-rd-consent-api")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-rd-consent-api")
install_slowapi_stub()

from modules.hr.consent import api as consent_api  # noqa: E402
from modules.hr.consent.store import ConsentStore  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _headers(requester: str, role: str = "crew") -> dict:
    token = generate_csrf_token("test-session")
    return {
        "Authorization": f"Bearer {token}",
        "X-Aurora-Requester": requester,
        "X-Aurora-Requester-Role": role,
    }


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # Isolate both persistence surfaces: the JSON grant store and the
    # insight_ledger root (which otherwise defaults to cwd/data/ledgers).
    monkeypatch.setenv("AURORA_LEDGER_PATH", str(tmp_path / "ledgers"))
    store = ConsentStore(storage_path=tmp_path / "consent_grants.json")
    monkeypatch.setattr(consent_api, "_store", store)

    app = FastAPI()
    app.include_router(consent_api.router, prefix="/rd")
    return TestClient(app)


def _create_grant(client, subject="crew_ana", tier=2, grantee="hr", **overrides):
    body = {
        "subject_id": subject,
        "tier": tier,
        "data_class": "coherence_profile",
        "purpose": "team_coherence_review",
        "grantee": grantee,
    }
    body.update(overrides)
    return client.post("/rd/consent/grants", json=body, headers=_headers(subject))


def test_grant_create_and_check_allows_access(client):
    resp = _create_grant(client)
    assert resp.status_code == 201
    grant = resp.json()["grant"]
    assert grant["status"] == "active"

    check = client.get(
        "/rd/consent/check",
        params={
            "subject_id": "crew_ana",
            "data_class": "coherence_profile",
            "purpose": "team_coherence_review",
        },
        headers=_headers("hr_officer", role="hr"),
    )
    assert check.status_code == 200
    decision = check.json()["decision"]
    assert decision["allowed"] is True
    assert decision["grant_id"] == grant["grant_id"]


def test_denial_without_grant(client):
    check = client.get(
        "/rd/consent/check",
        params={
            "subject_id": "crew_ana",
            "data_class": "coherence_profile",
            "purpose": "team_coherence_review",
        },
        headers=_headers("hr_officer", role="hr"),
    )
    assert check.status_code == 200
    assert check.json()["decision"]["allowed"] is False


def test_only_subject_can_create_grant(client):
    """No automated layer or third party can fabricate consent."""
    body = {
        "subject_id": "crew_ana",
        "tier": 2,
        "data_class": "coherence_profile",
        "purpose": "team_coherence_review",
        "grantee": "hr",
    }
    # HR trying to consent on the subject's behalf → 403
    resp = client.post(
        "/rd/consent/grants", json=body, headers=_headers("hr_officer", role="hr")
    )
    assert resp.status_code == 403
    # No requester identity at all → 401
    token = generate_csrf_token("test-session")
    resp = client.post(
        "/rd/consent/grants", json=body, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 401


def test_revocation_removes_access(client):
    grant_id = _create_grant(client).json()["grant"]["grant_id"]

    resp = client.post(
        f"/rd/consent/grants/{grant_id}/revoke",
        json={"reason": "withdrawal without penalty"},
        headers=_headers("crew_ana"),
    )
    assert resp.status_code == 200
    assert resp.json()["grant"]["status"] == "revoked"

    check = client.get(
        "/rd/consent/check",
        params={
            "subject_id": "crew_ana",
            "data_class": "coherence_profile",
            "purpose": "team_coherence_review",
        },
        headers=_headers("hr_officer", role="hr"),
    )
    assert check.json()["decision"]["allowed"] is False

    # Double revocation is rejected, and the record is retained (auditable).
    resp = client.post(
        f"/rd/consent/grants/{grant_id}/revoke",
        json={"reason": "again"},
        headers=_headers("crew_ana"),
    )
    assert resp.status_code == 409


def test_third_party_cannot_revoke(client):
    grant_id = _create_grant(client).json()["grant"]["grant_id"]
    resp = client.post(
        f"/rd/consent/grants/{grant_id}/revoke",
        json={"reason": "not mine to revoke"},
        headers=_headers("crew_bo", role="crew"),
    )
    assert resp.status_code == 403


def test_expiry_removes_access(client):
    grant_resp = _create_grant(client, expires_in_days=1)
    grant_id = grant_resp.json()["grant"]["grant_id"]

    # Force the stored expiry into the past instead of sleeping.
    store = consent_api.get_store()
    stored = store.get(grant_id)
    stored.expires_at = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
    ).isoformat()

    check = client.get(
        "/rd/consent/check",
        params={
            "subject_id": "crew_ana",
            "data_class": "coherence_profile",
            "purpose": "team_coherence_review",
        },
        headers=_headers("hr_officer", role="hr"),
    )
    assert check.json()["decision"]["allowed"] is False

    listing = client.get(
        "/rd/consent/subjects/crew_ana/grants", headers=_headers("crew_ana")
    )
    assert listing.json()["grants"][0]["status"] == "expired"


def test_unauthorized_disclosure_blocked(client):
    """Individual consent records are visible to self and HR only (Tier 2)."""
    _create_grant(client)
    grant_id = _create_grant(
        client, subject="crew_bo", grantee="hr"
    ).json()["grant"]["grant_id"]

    # Another crew member cannot list someone else's grants...
    resp = client.get(
        "/rd/consent/subjects/crew_ana/grants", headers=_headers("crew_bo")
    )
    assert resp.status_code == 403
    # ...or fetch a grant by id (404, not 403 — existence is individual data).
    resp = client.get(f"/rd/consent/grants/{grant_id}", headers=_headers("crew_ana"))
    assert resp.status_code == 404
    # Self and HR can.
    assert (
        client.get(f"/rd/consent/grants/{grant_id}", headers=_headers("crew_bo")).status_code
        == 200
    )
    assert (
        client.get(
            f"/rd/consent/grants/{grant_id}", headers=_headers("hr_officer", role="hr")
        ).status_code
        == 200
    )


def test_tier3_requires_named_project_lead(client):
    resp = _create_grant(client, tier=3, grantee="project_lead:lead_kim")
    assert resp.status_code == 201

    # A tier 3 grantee that names nobody is rejected.
    resp = _create_grant(
        client, subject="crew_bo", tier=3, grantee="everyone"
    )
    assert resp.status_code == 409

    # The named lead gets access; a different lead does not.
    params = {
        "subject_id": "crew_ana",
        "data_class": "coherence_profile",
        "purpose": "team_coherence_review",
    }
    allowed = client.get(
        "/rd/consent/check", params=params, headers=_headers("lead_kim", role="project_lead")
    )
    assert allowed.json()["decision"]["allowed"] is True
    denied = client.get(
        "/rd/consent/check", params=params, headers=_headers("lead_rex", role="project_lead")
    )
    assert denied.json()["decision"]["allowed"] is False


def test_grants_persist_across_store_reload(client, tmp_path):
    _create_grant(client)
    path = consent_api.get_store()._path

    reloaded = ConsentStore(storage_path=path)
    grants = reloaded.list_for_subject("crew_ana")
    assert len(grants) == 1
    assert grants[0].is_active()


def test_aggregate_is_anonymized_and_suppresses_small_buckets(client):
    # 2 active grants — below the k=5 threshold, so counts must be suppressed.
    _create_grant(client)
    _create_grant(client, subject="crew_bo")

    resp = client.get("/rd/consent/aggregate")
    assert resp.status_code == 200
    payload = resp.json()["aggregate"]
    assert payload["anonymized"] is True
    assert payload["total_active_grants"] == "<5"
    assert payload["active_by_tier"].get("tier_2") == "<5"

    # No individual identifiers anywhere in the response.
    raw = json.dumps(resp.json())
    assert "crew_ana" not in raw
    assert "crew_bo" not in raw
    assert "grant_id" not in raw


def test_audit_events_land_in_insight_ledger(client):
    """Grant + revoke + a denial should appear in the hash-chained ledger."""
    resp = _create_grant(client)
    if not resp.json().get("audit_recorded"):
        pytest.skip("insight_ledger unavailable in this environment")
    grant_id = resp.json()["grant"]["grant_id"]
    client.post(
        f"/rd/consent/grants/{grant_id}/revoke",
        json={"reason": "test withdrawal"},
        headers=_headers("crew_ana"),
    )
    client.get(
        "/rd/consent/check",
        params={
            "subject_id": "crew_ana",
            "data_class": "coherence_profile",
            "purpose": "team_coherence_review",
        },
        headers=_headers("hr_officer", role="hr"),
    )

    ledger = consent_api.get_store()._ledger
    entries = ledger.query_history()
    tags = [tag for e in entries for tag in (e.tags or [])]
    assert "grant_created" in tags
    assert "grant_revoked" in tags
    assert "access_denied" in tags
    integrity = ledger.verify_integrity()
    assert integrity["chain_intact"] is True
    assert integrity["failed_entries"] == []
