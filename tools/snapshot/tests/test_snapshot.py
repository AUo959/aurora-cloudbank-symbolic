#!/usr/bin/env python3
"""
Tests for Aurora CloudBank Snapshot Sealing Tool
"""

import json
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import pytest
from tools.snapshot.snapshot import SnapshotSealer


@pytest.fixture
def sample_manifest():
    """Sample manifest for testing"""
    return {
        "module": "test_module",
        "description": "Test module for snapshot sealing",
        "anchor_seed": "EOS_SEED_ORION",
        "version": "v0.1.0",
        "team": "AUo959-team",
        "symbolic_tags": ["T1", "SRB", "test"],
        "dlp_tags": {
            "critical": ["state_data"],
            "confidential": [],
            "public": ["metadata"]
        }
    }


@pytest.fixture
def sample_state():
    """Sample state for testing"""
    return {
        "counter": 42,
        "items": ["x", "y", "z"],
        "config": {"enabled": True, "threshold": 0.95}
    }


@pytest.fixture
def sealer():
    """Create SnapshotSealer instance"""
    return SnapshotSealer()


def test_compute_state_hash(sealer, sample_state):
    """Test state hash computation"""
    hash1 = sealer.compute_state_hash(sample_state)
    hash2 = sealer.compute_state_hash(sample_state)
    
    # Same state should produce same hash
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 produces 64 hex chars
    
    # Different state should produce different hash
    modified_state = sample_state.copy()
    modified_state['counter'] = 43
    hash3 = sealer.compute_state_hash(modified_state)
    assert hash1 != hash3


def test_compute_manifest_checksum(sealer, sample_manifest):
    """Test manifest checksum computation"""
    checksum1 = sealer.compute_manifest_checksum(sample_manifest)
    checksum2 = sealer.compute_manifest_checksum(sample_manifest)
    
    # Same manifest should produce same checksum
    assert checksum1 == checksum2
    assert len(checksum1) == 64
    
    # Checksum field should be excluded from computation
    manifest_with_checksum = sample_manifest.copy()
    manifest_with_checksum['checksum'] = 'old_checksum'
    checksum3 = sealer.compute_manifest_checksum(manifest_with_checksum)
    assert checksum1 == checksum3


def test_seal_snapshot(sealer, sample_manifest, sample_state):
    """Test snapshot sealing"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state, context_tag="test_seal")
    
    # Check structure
    assert 'manifest' in snapshot
    assert 'state' in snapshot
    assert 'state_hash' in snapshot
    assert 'metadata' in snapshot
    assert 'verification' in snapshot
    
    # Check manifest includes checksum
    assert 'checksum' in snapshot['manifest']
    
    # Check metadata
    assert snapshot['metadata']['anchor_seed'] == 'EOS_SEED_ORION'
    assert snapshot['metadata']['team'] == 'AUo959-team'
    assert snapshot['metadata']['version'] == 'v0.1.0'
    assert snapshot['metadata']['context_tag'] == 'test_seal'
    assert snapshot['metadata']['ethics_anchor'] == 'Picard_Delta_3'
    
    # Check verification section
    assert snapshot['verification']['seal_integrity'] == 'SEALED'


def test_seal_snapshot_missing_fields(sealer, sample_state):
    """Test sealing with incomplete manifest"""
    incomplete_manifest = {
        "module": "test_module"
        # Missing required fields
    }
    
    with pytest.raises(ValueError, match="missing required fields"):
        sealer.seal_snapshot(incomplete_manifest, sample_state)


def test_verify_snapshot_valid(sealer, sample_manifest, sample_state):
    """Test verification of valid snapshot"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    is_valid, issues = sealer.verify_snapshot(snapshot)
    
    assert is_valid is True
    assert len(issues) == 0


def test_verify_snapshot_tampered_state(sealer, sample_manifest, sample_state):
    """Test verification detects tampered state"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    
    # Tamper with state
    snapshot['state']['counter'] = 999
    
    is_valid, issues = sealer.verify_snapshot(snapshot)
    
    assert is_valid is False
    assert len(issues) > 0
    assert any('State hash mismatch' in issue for issue in issues)


def test_verify_snapshot_tampered_manifest(sealer, sample_manifest, sample_state):
    """Test verification detects tampered manifest"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    
    # Tamper with manifest
    snapshot['manifest']['version'] = 'v999.0.0'
    
    is_valid, issues = sealer.verify_snapshot(snapshot)
    
    assert is_valid is False
    assert len(issues) > 0
    assert any('Manifest checksum mismatch' in issue for issue in issues)


def test_verify_snapshot_invalid_seal(sealer, sample_manifest, sample_state):
    """Test verification detects invalid seal marker"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    
    # Tamper with seal marker
    snapshot['verification']['seal_integrity'] = 'TAMPERED'
    
    is_valid, issues = sealer.verify_snapshot(snapshot)
    
    assert is_valid is False
    assert any('Invalid seal integrity marker' in issue for issue in issues)


def test_restore_state_valid(sealer, sample_manifest, sample_state):
    """Test restoring state from valid snapshot"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    restored_state = sealer.restore_state(snapshot)
    
    assert restored_state == sample_state


def test_restore_state_invalid(sealer, sample_manifest, sample_state):
    """Test restoring state from invalid snapshot fails"""
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state)
    
    # Tamper with state
    snapshot['state']['counter'] = 999
    
    with pytest.raises(ValueError, match="verification failed"):
        sealer.restore_state(snapshot)


def test_roundtrip(sealer, sample_manifest, sample_state):
    """Test full seal -> verify -> restore roundtrip"""
    # Seal
    snapshot = sealer.seal_snapshot(sample_manifest, sample_state, context_tag="roundtrip_test")
    
    # Verify
    is_valid, issues = sealer.verify_snapshot(snapshot)
    assert is_valid is True
    
    # Restore
    restored_state = sealer.restore_state(snapshot)
    assert restored_state == sample_state


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
