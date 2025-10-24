#!/usr/bin/env python3
"""
Aurora CloudBank Snapshot & Sealing Tool

Quantum-symbolic state snapshot with DLP tracking, manifest checksums,
and Picard_Delta_3 ethical anchoring.

Anchor: EOS_SEED_ORION
Team: AUo959-team
Version: v0.1.0
Ethics: Picard_Delta_3 (Divergent Truths require human arbitration)
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class SnapshotSealer:
    """
    Seal quantum-symbolic state with DLP tags, manifest checksums,
    and T1/SRB anchor protocols.
    """

    def __init__(self, anchor_seed: str = "EOS_SEED_ORION"):
        self.anchor_seed = anchor_seed
        self.team = "AUo959-team"
        self.version = "v0.1.0"

    def compute_state_hash(self, state: Dict[str, Any]) -> str:
        """
        Compute SHA-256 hash of state (canonical JSON).
        
        Args:
            state: State dictionary to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        canonical = json.dumps(state, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def compute_manifest_checksum(self, manifest: Dict[str, Any]) -> str:
        """
        Compute manifest checksum (excludes 'checksum' field itself).
        
        Args:
            manifest: Manifest dictionary
            
        Returns:
            Hex-encoded SHA-256 checksum
        """
        # Remove checksum field if present
        manifest_copy = {k: v for k, v in manifest.items() if k != 'checksum'}
        canonical = json.dumps(manifest_copy, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

    def seal_snapshot(
        self,
        manifest: Dict[str, Any],
        state: Dict[str, Any],
        context_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Seal snapshot with manifest, state hash, and DLP tracking.
        
        Args:
            manifest: Module manifest with anchor_seed, team, version, dlp_tags
            state: Current state to snapshot
            context_tag: Optional context identifier
            
        Returns:
            Sealed snapshot dictionary
        """
        # Validate manifest
        required_fields = ['module', 'anchor_seed', 'version', 'team', 'dlp_tags']
        missing = [f for f in required_fields if f not in manifest]
        if missing:
            raise ValueError(f"Manifest missing required fields: {missing}")

        # Compute hashes
        state_hash = self.compute_state_hash(state)
        manifest_checksum = self.compute_manifest_checksum(manifest)

        # Create sealed snapshot
        snapshot = {
            # Manifest section
            'manifest': {
                **manifest,
                'checksum': manifest_checksum
            },
            
            # State section
            'state': state,
            'state_hash': state_hash,
            
            # Metadata section
            'metadata': {
                'sealed_at': datetime.utcnow().isoformat() + 'Z',
                'anchor_seed': manifest.get('anchor_seed', self.anchor_seed),
                'team': manifest.get('team', self.team),
                'version': manifest.get('version', self.version),
                'context_tag': context_tag or f"snapshot_{manifest['module']}",
                'ethics_anchor': 'Picard_Delta_3',
                'dlp_protocol': 'aurora_native_v1'
            },
            
            # Verification section
            'verification': {
                'state_hash': state_hash,
                'manifest_checksum': manifest_checksum,
                'seal_integrity': 'SEALED'
            }
        }

        return snapshot

    def verify_snapshot(self, snapshot: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Verify snapshot integrity.
        
        Args:
            snapshot: Sealed snapshot to verify
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check structure
        required_sections = ['manifest', 'state', 'state_hash', 'metadata', 'verification']
        missing_sections = [s for s in required_sections if s not in snapshot]
        if missing_sections:
            issues.append(f"Missing sections: {missing_sections}")
            return False, issues

        # Verify state hash
        computed_hash = self.compute_state_hash(snapshot['state'])
        stored_hash = snapshot['state_hash']
        if computed_hash != stored_hash:
            issues.append(f"State hash mismatch: computed={computed_hash}, stored={stored_hash}")

        # Verify manifest checksum
        manifest = snapshot['manifest']
        computed_checksum = self.compute_manifest_checksum(manifest)
        stored_checksum = manifest.get('checksum', '')
        if computed_checksum != stored_checksum:
            issues.append(f"Manifest checksum mismatch: computed={computed_checksum}, stored={stored_checksum}")

        # Verify seal integrity marker
        seal_integrity = snapshot.get('verification', {}).get('seal_integrity', '')
        if seal_integrity != 'SEALED':
            issues.append(f"Invalid seal integrity marker: {seal_integrity}")

        # Check DLP tags presence
        if 'dlp_tags' not in manifest:
            issues.append("Manifest missing DLP tags")

        is_valid = len(issues) == 0
        return is_valid, issues

    def restore_state(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restore state from verified snapshot.
        
        Args:
            snapshot: Sealed snapshot
            
        Returns:
            Restored state dictionary
            
        Raises:
            ValueError: If snapshot verification fails
        """
        is_valid, issues = self.verify_snapshot(snapshot)
        if not is_valid:
            raise ValueError(f"Snapshot verification failed: {issues}")

        return snapshot['state']


def save_snapshot(snapshot: Dict[str, Any], output_path: Path) -> None:
    """
    Save snapshot to JSON file.
    
    Args:
        snapshot: Sealed snapshot
        output_path: Path to save file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(snapshot, f, indent=2)


def load_snapshot(snapshot_path: Path) -> Dict[str, Any]:
    """
    Load snapshot from JSON file.
    
    Args:
        snapshot_path: Path to snapshot file
        
    Returns:
        Snapshot dictionary
    """
    with open(snapshot_path, 'r') as f:
        return json.load(f)


# Export public API
__all__ = [
    'SnapshotSealer',
    'save_snapshot',
    'load_snapshot'
]
