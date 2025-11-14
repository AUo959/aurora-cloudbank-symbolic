from fastapi.testclient import TestClient


def test_full_and_mediation_endpoints():
    # Import inside test to avoid import-time side effects if optional modules missing
    from api.aurora_api import app

    client = TestClient(app)

    # Full coherence should succeed even if vectors are minimal
    r_full = client.get("/rd/coherence/full")
    assert r_full.status_code == 200, r_full.text
    body = r_full.json()
    assert body.get("success") is True
    assert "average_coherence" in body

    # Mediation should return a list (possibly empty), and success True
    r_med = client.get("/rd/coherence/mediation")
    assert r_med.status_code == 200, r_med.text
    med = r_med.json()
    assert med.get("success") is True
    assert "pairs" in med
