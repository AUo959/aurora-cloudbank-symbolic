"""
Test Suite for Insight Ledger

Comprehensive tests for cryptographic integrity, append-only semantics,
and API endpoints.

Anchor: T1-TIL-003
"""

import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from modules.insight_ledger.api import initialize_ledger, router
from modules.insight_ledger.crypto_signatures import SignatureManager, generate_secret_key, validate_secret_key
from modules.insight_ledger.ledger_core import InsightLedger
from modules.insight_ledger.schemas import AuditQuery, InsightRecord, InsightType

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_ledger_dir():
    """Create temporary directory for ledger storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def ledger(temp_ledger_dir):
    """Create fresh ledger instance."""
    return InsightLedger(storage_path=temp_ledger_dir, auto_checkpoint=10)


@pytest.fixture
def signature_manager():
    """Create signature manager instance."""
    return SignatureManager()


@pytest.fixture
def api_client(temp_ledger_dir):
    """Create FastAPI test client with initialized ledger."""
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)

    # Initialize ledger
    initialize_ledger(storage_path=temp_ledger_dir)

    return TestClient(app)


@pytest.fixture
def sample_insight():
    """Create sample insight record."""
    return InsightRecord(
        insight_type=InsightType.DECISION,
        content="Test decision with context",
        context={"test_key": "test_value"},
        source="test-suite",
        tags=["testing", "sample"],
        severity="info",
        related_anchor="T1-TIL-003",
    )


# ============================================================================
# Cryptography Tests
# ============================================================================


@pytest.mark.unit
def test_signature_manager_initialization():
    """Test signature manager creation and key generation."""
    # Auto-generate key
    sm1 = SignatureManager()
    assert sm1.secret_key_hex is not None
    assert len(sm1.secret_key_hex) == 64  # 32 bytes = 64 hex chars

    # Load existing key
    key = sm1.secret_key_hex
    sm2 = SignatureManager(secret_key=key)
    assert sm2.secret_key_hex == key


@pytest.mark.unit
def test_data_hashing(signature_manager):
    """Test deterministic data hashing."""
    data = {"key1": "value1", "key2": 123, "key3": [1, 2, 3]}

    hash1 = signature_manager.hash_data(data)
    hash2 = signature_manager.hash_data(data)

    assert hash1 == hash2  # Deterministic
    assert len(hash1) == 64  # SHA-256 = 64 hex chars


@pytest.mark.unit
def test_entry_signing_and_verification(signature_manager):
    """Test HMAC signature creation and verification."""
    entry_data = {
        "entry_id": "test_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content": "Test content",
        "source": "test",
    }

    # Sign entry
    signature = signature_manager.sign_entry(entry_data)
    assert signature is not None
    assert len(signature) == 64  # HMAC-SHA256 = 64 hex chars

    # Verify signature
    assert signature_manager.verify_signature(entry_data, signature)

    # Tampered data should fail
    tampered_data = {**entry_data, "content": "Modified content"}
    assert not signature_manager.verify_signature(tampered_data, signature)


@pytest.mark.unit
def test_hash_chain_link_verification(signature_manager):
    """Test hash chain linking and verification."""
    entry_id = "test_001"
    timestamp = datetime.now(timezone.utc)
    content = "Test content"
    previous_hash = "abc123"
    signature = "def456"

    # Create hash
    entry_hash = signature_manager.hash_entry(entry_id, timestamp, content, previous_hash, signature)

    # Verify hash
    assert signature_manager.verify_chain_link(
        entry_id, timestamp, content, previous_hash, signature, entry_hash
    )

    # Wrong hash should fail
    assert not signature_manager.verify_chain_link(
        entry_id, timestamp, content, previous_hash, signature, "wrong_hash"
    )


@pytest.mark.unit
def test_secret_key_generation():
    """Test secret key generation and validation."""
    key = generate_secret_key()
    assert validate_secret_key(key)
    assert len(key) == 64  # 32 bytes = 64 hex chars

    # Invalid keys
    assert not validate_secret_key("invalid")
    assert not validate_secret_key("abc")  # Too short
    assert not validate_secret_key("zzz123")  # Invalid hex


# ============================================================================
# Ledger Core Tests
# ============================================================================


@pytest.mark.unit
def test_ledger_initialization(temp_ledger_dir):
    """Test ledger initialization and genesis entry."""
    ledger = InsightLedger(storage_path=temp_ledger_dir)

    stats = ledger.get_stats()
    assert stats.total_entries == 1  # Genesis entry
    assert stats.integrity_verified

    # Check files created
    ledger_path = Path(temp_ledger_dir)
    assert (ledger_path / "entries.jsonl").exists()
    assert (ledger_path / "index.json").exists()
    assert (ledger_path / "ledger.key").exists()


@pytest.mark.unit
def test_record_single_insight(ledger, sample_insight):
    """Test recording a single insight."""
    entry = ledger.record_insight(sample_insight)

    assert entry.entry_id is not None
    assert entry.content == sample_insight.content
    assert entry.signature is not None
    assert entry.entry_hash is not None
    assert entry.previous_hash is not None  # Linked to genesis


@pytest.mark.unit
def test_append_only_semantics(ledger):
    """Test that entries are truly append-only."""
    # Record multiple entries
    for i in range(5):
        insight = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content=f"Entry {i}",
            source="test",
        )
        ledger.record_insight(insight)

    # Verify count
    stats = ledger.get_stats()
    assert stats.total_entries == 6  # 5 + genesis

    # Entries file should have 6 lines
    entries_file = Path(ledger.storage_path) / "entries.jsonl"
    lines = entries_file.read_text().strip().split("\n")
    assert len(lines) == 6


@pytest.mark.unit
def test_hash_chain_integrity(ledger):
    """Test hash chain linking between entries."""
    entries = []

    # Record chain of entries
    for i in range(5):
        insight = InsightRecord(
            insight_type=InsightType.DECISION,
            content=f"Decision {i}",
            source="test",
        )
        entry = ledger.record_insight(insight)
        entries.append(entry)

    # Verify chain links
    for i in range(1, len(entries)):
        assert entries[i].previous_hash == entries[i - 1].entry_hash


@pytest.mark.integration
def test_ledger_persistence(temp_ledger_dir, sample_insight):
    """Test ledger persistence across instances."""
    # Create ledger and record entry
    ledger1 = InsightLedger(storage_path=temp_ledger_dir)
    entry1 = ledger1.record_insight(sample_insight)

    # Load ledger again
    ledger2 = InsightLedger(storage_path=temp_ledger_dir)
    stats = ledger2.get_stats()

    assert stats.total_entries == 2  # Genesis + sample
    assert stats.integrity_verified

    # Query should return the entry
    entries = ledger2.query_history(AuditQuery(limit=10))
    assert len(entries) == 2
    assert any(e.entry_id == entry1.entry_id for e in entries)


@pytest.mark.unit
def test_auto_checkpointing(temp_ledger_dir):
    """Test automatic checkpoint creation."""
    ledger = InsightLedger(storage_path=temp_ledger_dir, auto_checkpoint=5)

    # Record 10 entries (should trigger 2 checkpoints at 5 and 10)
    for i in range(10):
        insight = InsightRecord(
            insight_type=InsightType.METRIC,
            content=f"Metric {i}",
            source="test",
        )
        ledger.record_insight(insight)

    # Total: 1 genesis + 10 insights + 2 checkpoints = 13
    stats = ledger.get_stats()
    assert stats.total_entries == 13


@pytest.mark.unit
def test_query_history_basic(ledger):
    """Test basic history querying."""
    # Record diverse entries
    for i in range(5):
        insight = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content=f"Analysis {i}",
            source=f"source-{i % 2}",
            tags=[f"tag{i}"],
        )
        ledger.record_insight(insight)

    # Query all
    entries = ledger.query_history(AuditQuery(limit=100))
    assert len(entries) == 6  # 5 + genesis

    # Query with limit
    entries = ledger.query_history(AuditQuery(limit=3))
    assert len(entries) == 3


@pytest.mark.unit
def test_query_history_by_type(ledger):
    """Test querying by insight type."""
    # Record mixed types
    types_recorded = [InsightType.DECISION, InsightType.ANALYSIS, InsightType.ALERT]

    for itype in types_recorded:
        insight = InsightRecord(insight_type=itype, content=f"Content for {itype}", source="test")
        ledger.record_insight(insight)

    # Query decisions only
    entries = ledger.query_history(AuditQuery(insight_types=[InsightType.DECISION]))
    assert all(e.insight_type == InsightType.DECISION for e in entries)
    assert len(entries) == 1


@pytest.mark.unit
def test_query_history_by_source(ledger):
    """Test querying by source."""
    sources = ["auth-service", "data-service", "ml-service"]

    for source in sources:
        insight = InsightRecord(
            insight_type=InsightType.DECISION, content=f"Decision from {source}", source=source
        )
        ledger.record_insight(insight)

    # Query auth-service only
    entries = ledger.query_history(AuditQuery(sources=["auth-service"]))
    assert all(e.source == "auth-service" for e in entries)
    assert len(entries) == 1


@pytest.mark.unit
def test_query_history_by_time_range(ledger):
    """Test querying by time range."""
    now = datetime.now(timezone.utc)

    # Record entries with slight delays
    for i in range(3):
        insight = InsightRecord(
            insight_type=InsightType.METRIC, content=f"Metric {i}", source="test"
        )
        ledger.record_insight(insight)

    # Query recent entries (last minute)
    start_time = now - timedelta(minutes=1)
    entries = ledger.query_history(AuditQuery(start_time=start_time))

    # Should get all test entries (not genesis which is older)
    assert len(entries) >= 3


@pytest.mark.unit
def test_query_history_by_tags(ledger):
    """Test querying by tags."""
    # Record entries with different tags
    ledger.record_insight(
        InsightRecord(
            insight_type=InsightType.ALERT,
            content="Alert 1",
            source="test",
            tags=["critical", "security"],
        )
    )
    ledger.record_insight(
        InsightRecord(
            insight_type=InsightType.ALERT, content="Alert 2", source="test", tags=["performance"]
        )
    )

    # Query security tags
    entries = ledger.query_history(AuditQuery(tags=["security"]))
    assert len(entries) == 1
    assert "security" in entries[0].tags


@pytest.mark.unit
def test_query_history_text_search(ledger):
    """Test full-text search in content."""
    ledger.record_insight(
        InsightRecord(
            insight_type=InsightType.ANALYSIS, content="Database performance analysis", source="test"
        )
    )
    ledger.record_insight(
        InsightRecord(
            insight_type=InsightType.ANALYSIS, content="Network latency analysis", source="test"
        )
    )

    # Search for "database"
    entries = ledger.query_history(AuditQuery(search_text="database"))
    assert len(entries) == 1
    assert "database" in entries[0].content.lower()


@pytest.mark.unit
def test_verify_integrity_clean_ledger(ledger, sample_insight):
    """Test integrity verification on clean ledger."""
    # Record some entries
    for i in range(5):
        ledger.record_insight(sample_insight)

    # Verify
    report = ledger.verify_integrity()

    assert report["chain_intact"]
    assert report["verified_entries"] == report["total_entries"]
    assert len(report["failed_entries"]) == 0
    assert len(report["errors"]) == 0


@pytest.mark.unit
def test_verify_integrity_with_limit(ledger):
    """Test partial integrity verification."""
    # Record 10 entries
    for i in range(10):
        insight = InsightRecord(
            insight_type=InsightType.METRIC, content=f"Metric {i}", source="test"
        )
        ledger.record_insight(insight)

    # Verify only first 5
    report = ledger.verify_integrity(limit=5)

    assert report["total_entries"] == 5
    assert report["verified_entries"] <= 5


@pytest.mark.integration
def test_verify_integrity_after_tampering(temp_ledger_dir):
    """Test detection of tampered entries."""
    ledger = InsightLedger(storage_path=temp_ledger_dir)

    # Record entries
    for i in range(3):
        insight = InsightRecord(
            insight_type=InsightType.DECISION, content=f"Decision {i}", source="test"
        )
        ledger.record_insight(insight)

    # Tamper with entries file
    entries_file = Path(temp_ledger_dir) / "entries.jsonl"
    content = entries_file.read_text()

    # Modify a content field (breaks signature)
    tampered_content = content.replace("Decision 1", "TAMPERED Decision 1")
    entries_file.write_text(tampered_content)

    # Create new ledger instance and verify
    ledger2 = InsightLedger(storage_path=temp_ledger_dir)
    report = ledger2.verify_integrity()

    assert not report["chain_intact"]
    assert len(report["failed_entries"]) > 0
    assert len(report["errors"]) > 0


@pytest.mark.unit
def test_get_stats(ledger):
    """Test ledger statistics generation."""
    # Record mixed entries
    for i in range(3):
        insight = InsightRecord(
            insight_type=InsightType.DECISION, content=f"Decision {i}", source="auth-service"
        )
        ledger.record_insight(insight)

    for i in range(2):
        insight = InsightRecord(
            insight_type=InsightType.ALERT, content=f"Alert {i}", source="monitor-service"
        )
        ledger.record_insight(insight)

    stats = ledger.get_stats()

    assert stats.total_entries == 6  # 5 + genesis
    assert stats.first_entry_time is not None
    assert stats.last_entry_time is not None
    assert stats.entries_by_type["decision"] == 3
    assert stats.entries_by_type["alert"] == 2
    assert stats.entries_by_source["auth-service"] == 3
    assert stats.entries_by_source["monitor-service"] == 2
    assert stats.ledger_size_bytes > 0


@pytest.mark.unit
def test_export_ledger(ledger, temp_ledger_dir):
    """Test ledger export to JSON."""
    # Record entries
    for i in range(5):
        insight = InsightRecord(
            insight_type=InsightType.ANALYSIS, content=f"Analysis {i}", source="test"
        )
        ledger.record_insight(insight)

    # Export
    export_path = Path(temp_ledger_dir) / "export.json"
    count = ledger.export_ledger(str(export_path), include_genesis=True)

    assert count == 6  # 5 + genesis
    assert export_path.exists()

    # Verify export content
    with open(export_path) as f:
        export_data = json.load(f)

    assert "ledger_metadata" in export_data
    assert "entries" in export_data
    assert len(export_data["entries"]) == 6


@pytest.mark.unit
def test_export_ledger_without_genesis(ledger, temp_ledger_dir):
    """Test ledger export excluding genesis."""
    # Record entries
    for i in range(3):
        insight = InsightRecord(
            insight_type=InsightType.METRIC, content=f"Metric {i}", source="test"
        )
        ledger.record_insight(insight)

    # Export without genesis
    export_path = Path(temp_ledger_dir) / "export_no_genesis.json"
    count = ledger.export_ledger(str(export_path), include_genesis=False)

    assert count == 3  # Excluding genesis

    with open(export_path) as f:
        export_data = json.load(f)

    assert len(export_data["entries"]) == 3


# ============================================================================
# API Tests
# ============================================================================


@pytest.mark.api
def test_api_record_insight(api_client):
    """Test POST /ledger/insight endpoint."""
    insight_data = {
        "insight": {
            "insight_type": "decision",
            "content": "Test API decision",
            "source": "api-test",
            "severity": "info",
        }
    }

    response = api_client.post("/ledger/insight", json=insight_data)

    assert response.status_code == 201
    data = response.json()
    assert data["success"]
    assert data["entry_id"] is not None
    assert data["entry"]["content"] == "Test API decision"


@pytest.mark.api
def test_api_verify_integrity(api_client):
    """Test GET /ledger/verify endpoint."""
    response = api_client.get("/ledger/verify")

    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "summary" in data
    assert data["report"]["chain_intact"]


@pytest.mark.api
def test_api_query_history(api_client):
    """Test POST /ledger/history endpoint."""
    # Record some entries
    for i in range(3):
        insight_data = {
            "insight": {
                "insight_type": "analysis",
                "content": f"Analysis {i}",
                "source": "api-test",
            }
        }
        api_client.post("/ledger/insight", json=insight_data)

    # Query
    query_data = {"limit": 10}
    response = api_client.post("/ledger/history", json=query_data)

    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert data["total_returned"] >= 3


@pytest.mark.api
def test_api_get_stats(api_client):
    """Test GET /ledger/stats endpoint."""
    response = api_client.get("/ledger/stats")

    assert response.status_code == 200
    data = response.json()
    assert "total_entries" in data
    assert "integrity_verified" in data
    assert data["total_entries"] >= 1  # Genesis


@pytest.mark.api
def test_api_export_ledger(api_client, temp_ledger_dir):
    """Test POST /ledger/export endpoint."""
    export_path = Path(temp_ledger_dir) / "api_export.json"

    response = api_client.post(
        "/ledger/export", params={"output_path": str(export_path), "include_genesis": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["entries_exported"] >= 1
    assert export_path.exists()


@pytest.mark.api
def test_api_get_entry_by_id(api_client):
    """Test GET /ledger/entry/{entry_id} endpoint."""
    # Record entry
    insight_data = {
        "insight": {
            "insight_type": "alert",
            "content": "Test alert",
            "source": "api-test",
        }
    }
    create_response = api_client.post("/ledger/insight", json=insight_data)
    entry_id = create_response.json()["entry_id"]

    # Retrieve by ID
    response = api_client.get(f"/ledger/entry/{entry_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["entry_id"] == entry_id
    assert data["content"] == "Test alert"


@pytest.mark.api
def test_api_get_entry_not_found(api_client):
    """Test GET /ledger/entry/{entry_id} with invalid ID."""
    response = api_client.get("/ledger/entry/invalid_id_xyz")

    assert response.status_code == 404


@pytest.mark.api
def test_api_health_check(api_client):
    """Test GET /ledger/health endpoint."""
    response = api_client.get("/ledger/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["ledger_initialized"]
    assert "total_entries" in data


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


@pytest.mark.unit
def test_invalid_insight_type():
    """Test validation of invalid insight type."""
    with pytest.raises(ValueError):
        InsightRecord(
            insight_type="invalid_type",  # type: ignore
            content="Test",
            source="test",
        )


@pytest.mark.unit
def test_empty_content_validation():
    """Test validation of empty content."""
    with pytest.raises(ValueError):
        InsightRecord(
            insight_type=InsightType.DECISION,
            content="",  # Empty not allowed
            source="test",
        )


@pytest.mark.unit
def test_duplicate_tags_removed(ledger):
    """Test that duplicate tags are removed."""
    insight = InsightRecord(
        insight_type=InsightType.ALERT,
        content="Test alert",
        source="test",
        tags=["tag1", "tag2", "tag1", "tag2"],  # Duplicates
    )

    entry = ledger.record_insight(insight)
    assert len(entry.tags) == 2  # Duplicates removed
    assert set(entry.tags) == {"tag1", "tag2"}


@pytest.mark.integration
def test_concurrent_writes(temp_ledger_dir):
    """Test thread-safe concurrent writes."""
    import threading

    ledger = InsightLedger(storage_path=temp_ledger_dir)
    results = []

    def write_entry(n):
        insight = InsightRecord(
            insight_type=InsightType.METRIC, content=f"Concurrent entry {n}", source="thread-test"
        )
        entry = ledger.record_insight(insight)
        results.append(entry.entry_id)

    # Start 10 threads
    threads = []
    for i in range(10):
        t = threading.Thread(target=write_entry, args=(i,))
        t.start()
        threads.append(t)

    # Wait for all
    for t in threads:
        t.join()

    # Verify all entries recorded
    assert len(results) == 10
    assert len(set(results)) == 10  # All unique IDs

    stats = ledger.get_stats()
    assert stats.total_entries == 11  # 10 + genesis


@pytest.mark.unit
def test_query_pagination(ledger):
    """Test query pagination with offset."""
    # Record 10 entries
    for i in range(10):
        insight = InsightRecord(
            insight_type=InsightType.ANALYSIS, content=f"Entry {i}", source="test"
        )
        ledger.record_insight(insight)

    # First page
    page1 = ledger.query_history(AuditQuery(limit=5, offset=0))
    assert len(page1) == 5

    # Second page
    page2 = ledger.query_history(AuditQuery(limit=5, offset=5))
    assert len(page2) == 5

    # No overlap
    page1_ids = {e.entry_id for e in page1}
    page2_ids = {e.entry_id for e in page2}
    assert len(page1_ids & page2_ids) == 0


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.slow
def test_large_ledger_performance(temp_ledger_dir):
    """Test performance with larger ledger (1000 entries)."""
    ledger = InsightLedger(storage_path=temp_ledger_dir, auto_checkpoint=100)

    # Record 1000 entries
    for i in range(1000):
        insight = InsightRecord(
            insight_type=InsightType.METRIC,
            content=f"Performance test entry {i}",
            source="perf-test",
        )
        ledger.record_insight(insight)

    stats = ledger.get_stats()
    assert stats.total_entries >= 1000

    # Verify integrity (should complete in reasonable time)
    report = ledger.verify_integrity()
    assert report["chain_intact"]
    assert report["verification_time_ms"] < 10000  # Less than 10 seconds


@pytest.mark.slow
def test_query_performance(temp_ledger_dir):
    """Test query performance on larger dataset."""
    ledger = InsightLedger(storage_path=temp_ledger_dir)

    # Record 500 entries
    for i in range(500):
        insight = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content=f"Query test entry {i}",
            source=f"source-{i % 10}",
            tags=[f"tag{i % 5}"],
        )
        ledger.record_insight(insight)

    # Query with filters
    entries = ledger.query_history(AuditQuery(sources=["source-5"], limit=100))

    assert len(entries) > 0
    assert all(e.source == "source-5" for e in entries)
