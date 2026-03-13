"""
Tests for the Aurora NeMo Service.
# Symbolic Anchor: T1
# SRB: NEMO_SERVICE_v1
# DLP: [nemo, tests]
# Chain Notation: #SERVICES//NEMO//TESTS//
# Ethics Protocol: Picard_Delta_3
"""

import hashlib
import json
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    """Return a FastAPI test client for the NeMo service."""
    from services.nemo_service.server import app

    return TestClient(app)


@pytest.fixture()
def symbolic_bridge():
    """Return a fresh SymbolicBridge instance for unit tests."""
    from services.nemo_service.symbolic_bridge import SymbolicBridge

    return SymbolicBridge(
        anchor_seed="EOS_SEED_ORION",
        drift_threshold=0.15,
    )


@pytest.fixture()
def state_manager(tmp_path):
    """Return a StateManager instance using a temporary directory."""
    from services.nemo_service.state_manager import StateManager

    return StateManager(snapshots_dir=str(tmp_path))


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    """Tests for GET /nemo/health."""

    def test_health_returns_200(self, client):
        """Health endpoint should return HTTP 200."""
        response = client.get("/nemo/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Health response should contain required fields."""
        data = client.get("/nemo/health").json()
        assert data["status"] == "ok"
        assert data["service"] == "aurora-nemo-service"
        assert data["ethics_protocol"] == "Picard_Delta_3"
        assert data["anchor_seed"] == "EOS_SEED_ORION"
        assert data["srb"] == "NEMO_SERVICE_v1"

    def test_health_includes_entropy_state(self, client):
        """Health response should include entropy_state and memory_drift keys."""
        data = client.get("/nemo/health").json()
        assert "entropy_state" in data
        assert "memory_drift" in data

    def test_health_includes_timestamp(self, client):
        """Health response should include a numeric timestamp."""
        data = client.get("/nemo/health").json()
        assert isinstance(data["timestamp"], (int, float))


# ---------------------------------------------------------------------------
# Status endpoint
# ---------------------------------------------------------------------------


class TestStatusEndpoint:
    """Tests for GET /nemo/status."""

    def test_status_returns_200(self, client):
        """Status endpoint should return HTTP 200."""
        response = client.get("/nemo/status")
        assert response.status_code == 200

    def test_status_response_structure(self, client):
        """Status response should include model, gpu, and symbolic_anchor sections."""
        data = client.get("/nemo/status").json()
        assert "model" in data
        assert "gpu" in data
        assert "symbolic_anchor" in data
        assert "inference" in data
        assert "snapshots" in data

    def test_status_module_id(self, client):
        """Status response should expose the Aurora module ID."""
        data = client.get("/nemo/status").json()
        assert data["module_id"] == "AURORA_NEMO_SERVICE"

    def test_status_ethics_protocol(self, client):
        """Status response should expose the ethics protocol."""
        data = client.get("/nemo/status").json()
        assert data["ethics_protocol"] == "Picard_Delta_3"


# ---------------------------------------------------------------------------
# Inference endpoint (mocked NeMo model)
# ---------------------------------------------------------------------------


class TestInferEndpoint:
    """Tests for POST /nemo/infer with a mocked NeMo model."""

    def test_infer_returns_200_without_model(self, client):
        """Infer endpoint should return 200 with mock result when no model is loaded."""
        response = client.post(
            "/nemo/infer",
            json={"text": "Hello world", "model_type": "llm"},
        )
        assert response.status_code == 200

    def test_infer_response_has_result(self, client):
        """Infer response must contain a result field."""
        data = client.post(
            "/nemo/infer",
            json={"text": "Test input", "model_type": "nlu"},
        ).json()
        assert "result" in data
        assert "anchor_context" in data

    def test_infer_mock_flag_when_no_model(self, client):
        """Mock result should set mock=True when NeMo model is not loaded."""
        data = client.post(
            "/nemo/infer",
            json={"text": "Test", "model_type": "llm"},
        ).json()
        result = data["result"]
        assert result.get("mock") is True

    def test_infer_anchor_context_present(self, client):
        """Inference response must include anchor_context with T1 and SRB."""
        data = client.post(
            "/nemo/infer",
            json={"text": "Symbolic test", "model_type": "llm"},
        ).json()
        ctx = data["anchor_context"]
        assert "t1" in ctx
        assert "srb" in ctx

    def test_infer_latency_ms_present(self, client):
        """Inference response should include latency_ms."""
        data = client.post(
            "/nemo/infer",
            json={"text": "Latency test", "model_type": "llm"},
        ).json()
        assert isinstance(data["latency_ms"], (int, float))
        assert data["latency_ms"] >= 0

    def test_infer_model_type_reflected(self, client):
        """Inference response should echo back the requested model_type."""
        data = client.post(
            "/nemo/infer",
            json={"text": "Type test", "model_type": "asr"},
        ).json()
        assert data["model_type"] == "asr"


# ---------------------------------------------------------------------------
# Generate endpoint
# ---------------------------------------------------------------------------


class TestGenerateEndpoint:
    """Tests for POST /nemo/generate."""

    def test_generate_returns_200(self, client):
        """Generate endpoint should return HTTP 200."""
        response = client.post(
            "/nemo/generate",
            json={"prompt": "Once upon a time"},
        )
        assert response.status_code == 200

    def test_generate_response_has_text(self, client):
        """Generate response must include generated_text."""
        data = client.post(
            "/nemo/generate",
            json={"prompt": "Test prompt"},
        ).json()
        assert "generated_text" in data
        assert isinstance(data["generated_text"], str)

    def test_generate_tokens_counted(self, client):
        """Generate response should include tokens_generated."""
        data = client.post(
            "/nemo/generate",
            json={"prompt": "Token count test"},
        ).json()
        assert isinstance(data["tokens_generated"], int)
        assert data["tokens_generated"] >= 0


# ---------------------------------------------------------------------------
# Snapshot creation and restore with SHA256 verification
# ---------------------------------------------------------------------------


class TestSnapshotEndpoints:
    """Tests for POST /nemo/snapshot and POST /nemo/restore."""

    def test_snapshot_returns_200(self, client):
        """Snapshot endpoint should return HTTP 200."""
        response = client.post("/nemo/snapshot", json={"description": "test snapshot"})
        assert response.status_code == 200

    def test_snapshot_response_structure(self, client):
        """Snapshot response must include snapshot_id and seal."""
        data = client.post(
            "/nemo/snapshot",
            json={"description": "structure test"},
        ).json()
        assert "snapshot_id" in data
        assert "seal" in data
        assert "timestamp" in data

    def test_snapshot_seal_is_sha256(self, client):
        """Snapshot seal must be a 64-character SHA256 hex string."""
        data = client.post(
            "/nemo/snapshot",
            json={"description": "sha256 check"},
        ).json()
        seal = data["seal"]
        assert len(seal) == 64
        assert all(c in "0123456789abcdef" for c in seal)

    def test_restore_snapshot(self, client):
        """Restore should successfully return the snapshot data."""
        # Create a snapshot first
        snap = client.post(
            "/nemo/snapshot",
            json={"description": "restore test"},
        ).json()
        snapshot_id = snap["snapshot_id"]

        # Now restore it
        restore = client.post(
            "/nemo/restore",
            json={"snapshot_id": snapshot_id},
        ).json()
        assert restore["restored"] is True
        assert restore["snapshot_id"] == snapshot_id

    def test_restore_invalid_snapshot_returns_404(self, client):
        """Restoring a non-existent snapshot should return HTTP 404."""
        response = client.post(
            "/nemo/restore",
            json={"snapshot_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert response.status_code == 404

    def test_restore_seal_matches(self, client):
        """Seal in restore response must match the original snapshot seal."""
        snap = client.post(
            "/nemo/snapshot",
            json={"description": "seal match test"},
        ).json()
        restore = client.post(
            "/nemo/restore",
            json={"snapshot_id": snap["snapshot_id"]},
        ).json()
        assert restore["seal"] == snap["seal"]


# ---------------------------------------------------------------------------
# Symbolic bridge — unit tests
# ---------------------------------------------------------------------------


class TestSymbolicBridge:
    """Unit tests for SymbolicBridge."""

    def test_resolve_anchor_context_advances_t1(self, symbolic_bridge):
        """Each call to resolve_anchor_context should increment T1."""
        ctx1 = symbolic_bridge.resolve_anchor_context("llm")
        ctx2 = symbolic_bridge.resolve_anchor_context("llm")
        assert ctx2["t1"] == ctx1["t1"] + 1

    def test_resolve_anchor_context_contains_srb(self, symbolic_bridge):
        """Anchor context must contain the SRB tag."""
        ctx = symbolic_bridge.resolve_anchor_context("llm")
        assert "srb" in ctx
        assert ctx["srb"] == "NEMO_SERVICE_v1"

    def test_log_entropy_sets_baseline_on_first_call(self, symbolic_bridge):
        """First entropy call should establish the baseline."""
        reading = symbolic_bridge.log_entropy(0, 0.5, "llm")
        assert reading.entropy_value == 0.5
        assert not reading.drift_flagged

    def test_log_entropy_detects_drift(self, symbolic_bridge):
        """A reading that exceeds the drift threshold should be flagged."""
        symbolic_bridge.log_entropy(0, 0.5, "llm")   # baseline = 0.5
        reading = symbolic_bridge.log_entropy(1, 0.8, "llm")  # delta = 0.3 > 0.15
        assert reading.drift_flagged

    def test_compute_entropy_returns_float(self, symbolic_bridge):
        """compute_entropy should return a non-negative float."""
        entropy = symbolic_bridge.compute_entropy([1.0, 2.0, 3.0, 4.0])
        assert isinstance(entropy, float)
        assert entropy >= 0.0

    def test_seal_context_is_sha256(self, symbolic_bridge):
        """seal_context should return a 64-char SHA256 hex digest."""
        seal = symbolic_bridge.seal_context({"key": "value", "t1": 42})
        assert len(seal) == 64
        assert all(c in "0123456789abcdef" for c in seal)

    def test_seal_context_deterministic(self, symbolic_bridge):
        """The same payload should produce the same seal."""
        payload = {"key": "value", "number": 7}
        seal1 = symbolic_bridge.seal_context(payload)
        seal2 = symbolic_bridge.seal_context(payload)
        assert seal1 == seal2

    def test_summary_contains_required_fields(self, symbolic_bridge):
        """Bridge summary should expose all expected keys."""
        summary = symbolic_bridge.summary()
        for key in ("anchor", "call_counter", "drift_threshold", "srb", "ethics_protocol"):
            assert key in summary


# ---------------------------------------------------------------------------
# State manager — unit tests
# ---------------------------------------------------------------------------


class TestStateManager:
    """Unit tests for StateManager."""

    def test_create_snapshot_returns_id(self, state_manager):
        """create_snapshot should return a non-empty snapshot ID."""
        sid = state_manager.create_snapshot({"test": "data"})
        assert sid
        assert len(sid) == 36  # UUID4 format

    def test_snapshot_seal_is_sha256(self, state_manager):
        """Stored snapshot seal must be a 64-character SHA256 hex string."""
        sid = state_manager.create_snapshot({"payload": "abc"})
        snap = state_manager.get_snapshot(sid)
        seal = snap["seal"]
        assert len(seal) == 64
        assert all(c in "0123456789abcdef" for c in seal)

    def test_verify_snapshot_passes(self, state_manager):
        """verify_snapshot should return True for an untampered snapshot."""
        sid = state_manager.create_snapshot({"integrity": True})
        assert state_manager.verify_snapshot(sid) is True

    def test_verify_snapshot_detects_tampering(self, state_manager):
        """verify_snapshot should return False if data has been mutated."""
        sid = state_manager.create_snapshot({"secret": "original"})
        # Tamper via the internal history list (only way to mutate without updating seal)
        snap = next(s for s in state_manager._history if s.snapshot_id == sid)
        snap.data["secret"] = "tampered"  # Mutate without updating seal
        assert state_manager.verify_snapshot(sid) is False

    def test_restore_snapshot_returns_data(self, state_manager):
        """restore_snapshot should return the original data payload."""
        original = {"restore_key": "restore_value", "count": 99}
        sid = state_manager.create_snapshot(original)
        restored = state_manager.restore_snapshot(sid)
        assert restored["restore_key"] == "restore_value"
        assert restored["count"] == 99

    def test_restore_raises_on_missing_snapshot(self, state_manager):
        """restore_snapshot should raise ValueError for an unknown ID."""
        with pytest.raises(ValueError, match="Snapshot not found"):
            state_manager.restore_snapshot("nonexistent-id")

    def test_list_snapshots_returns_all(self, state_manager):
        """list_snapshots should return one entry per created snapshot."""
        state_manager.create_snapshot({"a": 1})
        state_manager.create_snapshot({"b": 2})
        snapshots = state_manager.list_snapshots()
        assert len(snapshots) >= 2

    def test_list_snapshots_newest_first(self, state_manager):
        """list_snapshots should be ordered newest-first by timestamp."""
        state_manager.create_snapshot({"order": "first"})
        time.sleep(0.01)
        state_manager.create_snapshot({"order": "second"})
        snaps = state_manager.list_snapshots()
        assert snaps[0]["timestamp"] >= snaps[1]["timestamp"]


# ---------------------------------------------------------------------------
# Config loading and validation
# ---------------------------------------------------------------------------


class TestConfig:
    """Tests for NeMoConfig loading and defaults."""

    def test_config_loads_defaults(self):
        """Config should load with sensible defaults."""
        from services.nemo_service.config import NeMoConfig

        cfg = NeMoConfig()
        assert cfg.aurora_module_id == "AURORA_NEMO_SERVICE"
        assert cfg.aurora_ethics_protocol == "Picard_Delta_3"
        assert cfg.nemo_anchor_seed == "EOS_SEED_ORION"
        assert cfg.port == 8090

    def test_config_env_override(self, monkeypatch):
        """Config should pick up environment variable overrides."""
        monkeypatch.setenv("NEMO_PORT", "9000")
        from services.nemo_service.config import NeMoConfig

        cfg = NeMoConfig()
        assert cfg.port == 9000

    def test_get_config_returns_instance(self):
        """get_config() should return a NeMoConfig instance."""
        from services.nemo_service.config import NeMoConfig, get_config

        cfg = get_config()
        assert isinstance(cfg, NeMoConfig)

    def test_dlp_classification_default(self):
        """DLP classification should default to INTERNAL."""
        from services.nemo_service.config import DLPClassification, NeMoConfig

        cfg = NeMoConfig()
        assert cfg.dlp_classification == DLPClassification.INTERNAL
