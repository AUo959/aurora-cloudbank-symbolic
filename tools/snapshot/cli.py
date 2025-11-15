#!/usr/bin/env python3
"""
Aurora CloudBank Snapshot CLI

Command-line interface for sealing, verifying, and restoring snapshots.

Usage:
    python -m tools.snapshot.cli seal --manifest manifest.json --state-file state.json --out-dir .snapshots
    python -m tools.snapshot.cli verify .snapshots/snapshot_xyz.json
    python -m tools.snapshot.cli restore .snapshots/snapshot_xyz.json --out restored_state.json
    python -m tools.snapshot.cli compute-manifest-checksum --manifest manifest.json --write
"""

import logging

logger = logging.getLogger(__name__)

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add repo root to path for imports
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.snapshot.snapshot import SnapshotSealer, save_snapshot, load_snapshot


def cmd_seal(args):
    """Seal a snapshot from manifest and state files"""
    # Load manifest
    with open(args.manifest, 'r') as f:
        manifest = json.load(f)

    # Load state
    with open(args.state_file, 'r') as f:
        state = json.load(f)

    # Create sealer and seal
    sealer = SnapshotSealer(anchor_seed=manifest.get('anchor_seed', 'EOS_SEED_ORION'))
    snapshot = sealer.seal_snapshot(manifest, state, context_tag=args.context_tag)

    # Generate output filename
    timestamp = datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
    module_name = manifest.get('module', 'unknown')
    filename = f"snapshot_{module_name}_{timestamp}.json"
    output_path = Path(args.out_dir) / filename

    # Save snapshot
    save_snapshot(snapshot, output_path)

    logger.info("Snapshot sealed successfully!")
    print(f"📦 Output: {output_path}")
    print(f"🔒 State hash: {snapshot['state_hash'][:16]}...")
    print(f"🔐 Manifest checksum: {snapshot['manifest']['checksum'][:16]}...")
    print(f"🏷️  Context: {snapshot['metadata']['context_tag']}")

    return 0


def cmd_verify(args):
    """Verify a snapshot's integrity"""
    snapshot_path = Path(args.snapshot)
    
    if not snapshot_path.exists():
        logger.error("Snapshot not found: {snapshot_path}")
        return 1

    # Load snapshot
    snapshot = load_snapshot(snapshot_path)

    # Verify
    sealer = SnapshotSealer()
    is_valid, issues = sealer.verify_snapshot(snapshot)

    if is_valid:
        logger.info("Snapshot verification PASSED")
        print(f"📦 File: {snapshot_path}")
        print(f"🔒 State hash: {snapshot['state_hash'][:16]}...")
        print(f"🔐 Manifest checksum: {snapshot['manifest']['checksum'][:16]}...")
        print(f"🏷️  Module: {snapshot['manifest'].get('module', 'unknown')}")
        print(f"📅 Sealed: {snapshot['metadata'].get('sealed_at', 'unknown')}")
        return 0
    else:
        logger.error("Snapshot verification FAILED")
        print(f"📦 File: {snapshot_path}")
        print(f"\n🚨 Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return 1


def cmd_restore(args):
    """Restore state from a verified snapshot"""
    snapshot_path = Path(args.snapshot)
    
    if not snapshot_path.exists():
        logger.error("Snapshot not found: {snapshot_path}")
        return 1

    # Load snapshot
    snapshot = load_snapshot(snapshot_path)

    # Restore (will verify first)
    sealer = SnapshotSealer()
    try:
        state = sealer.restore_state(snapshot)
        
        # Save restored state
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(state, f, indent=2)

        logger.info("State restored successfully!")
        print(f"📦 Source: {snapshot_path}")
        print(f"💾 Output: {output_path}")
        print(f"🏷️  Module: {snapshot['manifest'].get('module', 'unknown')}")
        return 0

    except ValueError as e:
        logger.error("Restore failed: {e}")
        return 1


def cmd_compute_manifest_checksum(args):
    """Compute and optionally write manifest checksum"""
    with open(args.manifest, 'r') as f:
        manifest = json.load(f)

    sealer = SnapshotSealer()
    checksum = sealer.compute_manifest_checksum(manifest)

    print(f"🔐 Manifest checksum: {checksum}")

    if args.write:
        manifest['checksum'] = checksum
        with open(args.manifest, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"✍️  Updated manifest file: {args.manifest}")

    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Aurora CloudBank Snapshot CLI - Seal, verify, and restore quantum-symbolic state'
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Seal command
    seal_parser = subparsers.add_parser('seal', help='Seal a new snapshot')
    seal_parser.add_argument('--manifest', required=True, help='Path to manifest.json')
    seal_parser.add_argument('--state-file', required=True, help='Path to state JSON file')
    seal_parser.add_argument('--out-dir', default='.snapshots', help='Output directory')
    seal_parser.add_argument('--context-tag', help='Optional context tag')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify snapshot integrity')
    verify_parser.add_argument('snapshot', help='Path to snapshot file')

    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore state from snapshot')
    restore_parser.add_argument('snapshot', help='Path to snapshot file')
    restore_parser.add_argument('--out', default='restored_state.json', help='Output state file')

    # Compute checksum command
    checksum_parser = subparsers.add_parser('compute-manifest-checksum', 
                                            help='Compute manifest checksum')
    checksum_parser.add_argument('--manifest', required=True, help='Path to manifest.json')
    checksum_parser.add_argument('--write', action='store_true', 
                                 help='Write checksum back to manifest')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    command_map = {
        'seal': cmd_seal,
        'verify': cmd_verify,
        'restore': cmd_restore,
        'compute-manifest-checksum': cmd_compute_manifest_checksum
    }

    return command_map[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
