"""Regression tests for CloudHub VSA and quantum route placeholders."""

import os
import unittest

import numpy as np
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("CSRF_SECRET_KEY", "test-csrf-secret-for-cloudhub-real-routes")
os.environ.setdefault("WS_AUTH_SECRET", "test-ws-secret-for-cloudhub-real-routes")

from api.aurora_gui_cloudhub_fastapi import app, vsa_store  # noqa: E402
from modules.symbolic_core.quantum_vsa import QuantumSymbolicVector  # noqa: E402
from src.middleware.fastapi_security import generate_csrf_token  # noqa: E402


def _auth_headers() -> dict[str, str]:
    token = generate_csrf_token("cloudhub-real-routes-session")
    return {"Authorization": f"Bearer {token}"}


def _client() -> TestClient:
    vsa_store.clear()
    return TestClient(app)


def _store_vector(symbol: str, values: list[int]) -> None:
    vector = QuantumSymbolicVector(symbol, len(values))
    vector.vector = np.asarray(values)
    vector.dim = len(values)
    vector.vector_type = "bipolar"
    vsa_store[symbol] = vector


def test_public_quantum_circuit_route_requires_auth() -> None:
    client = _client()

    response = client.post(
        "/quantum/circuit",
        json={"symbol": "alpha", "depth": 2, "qubits": 3},
    )

    assert response.status_code in (401, 403)


def test_public_quantum_circuit_route_uses_real_backend() -> None:
    client = _client()

    response = client.post(
        "/quantum/circuit",
        json={"symbol": "alpha", "depth": 2, "qubits": 3},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload.get("message") != "Quantum circuit executed"
    assert "circuit_qasm" in payload or payload.get("error") == "Qiskit not available"


def test_vsa_bind_route_uses_elementwise_vector_binding() -> None:
    client = _client()
    _store_vector("a", [1, -1, 1, -1])
    _store_vector("b", [1, 1, -1, -1])

    response = client.post(
        "/vsa/bind",
        json={"symbol_a": "a", "symbol_b": "b", "result_name": "a_bound_b", "dimension": 4},
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"] == [1, -1, -1, 1]
    assert vsa_store["a_bound_b"].vector.tolist() == [1, -1, -1, 1]


def test_vsa_similarity_route_is_deterministic_and_vector_based() -> None:
    client = _client()
    _store_vector("a", [1, -1, 1, -1])
    _store_vector("b", [1, 1, -1, -1])

    first = client.post(
        "/vsa/similarity",
        json={"symbol_a": "a", "symbol_b": "b"},
        headers=_auth_headers(),
    )
    second = client.post(
        "/vsa/similarity",
        json={"symbol_a": "a", "symbol_b": "b"},
        headers=_auth_headers(),
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["similarity"] == second.json()["similarity"]
    assert first.json()["similarity"] == pytest.approx(0.0)


def test_vsa_operation_rejects_non_executable_placeholder_operations() -> None:
    checks = unittest.TestCase()
    client = _client()

    response = client.post(
        "/vsa/operation",
        json={"symbol": "alpha", "dimension": 4, "operation_type": "similarity"},
        headers=_auth_headers(),
    )

    checks.assertEqual(response.status_code, 400)
    checks.assertNotIn("Similarity not implemented in demo", response.text)
