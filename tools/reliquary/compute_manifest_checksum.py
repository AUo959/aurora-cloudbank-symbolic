#!/usr/bin/env python3
"""
Aurora CloudBank Manifest Checksum Utility

Compute and update manifest checksums for integrity verification.

Anchor: EOS_SEED_ORION
Team: AUo959-team
Version: v0.1.0
"""

import logging

logger = logging.getLogger(__name__)

import argparse
import json
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.snapshot.snapshot import SnapshotSealer


def compute_and_update_checksum(manifest_path: Path, write: bool = False) -> str:
    """
    Compute manifest checksum and optionally update the file.
    
    Args:
        manifest_path: Path to manifest.json
        write: If True, write checksum back to file
        
    Returns:
        Computed checksum
    """
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    sealer = SnapshotSealer()
    checksum = sealer.compute_manifest_checksum(manifest)
    
    if write:
        manifest['checksum'] = checksum
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
    
    return checksum


def main():
    """Main checksum utility entry point"""
    parser = argparse.ArgumentParser(
        description='Compute and update manifest checksums'
    )
    parser.add_argument('manifest', help='Path to manifest.json file')
    parser.add_argument('--write', action='store_true',
                        help='Write checksum back to manifest file')
    
    args = parser.parse_args()
    
    manifest_path = Path(args.manifest)
    
    if not manifest_path.exists():
        logger.error("Manifest not found: {manifest_path}")
        return 1
    
    checksum = compute_and_update_checksum(manifest_path, write=args.write)
    
    print(f"🔐 Manifest checksum: {checksum}")
    if args.write:
        print(f"✍️  Updated: {manifest_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
