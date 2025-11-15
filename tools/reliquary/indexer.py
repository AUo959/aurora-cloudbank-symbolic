#!/usr/bin/env python3
"""
Aurora CloudBank Reliquary Indexer

Indexes all manifest.json files in the repository and validates checksums.

Anchor: EOS_SEED_ORION
Team: AUo959-team
Version: v0.1.0
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.snapshot.snapshot import SnapshotSealer


def find_manifests(root_dir: Path) -> list:
    """
    Find all manifest.json files in repository.
    
    Args:
        root_dir: Root directory to search
        
    Returns:
        List of manifest file paths
    """
    manifests = []
    
    # Search for manifest.json files (exclude .git, node_modules, venv, etc.)
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.pytest_cache'}
    
    for manifest_path in root_dir.rglob('manifest.json'):
        # Skip if in excluded directory
        if any(excluded in manifest_path.parts for excluded in exclude_dirs):
            continue
        manifests.append(manifest_path)
    
    return sorted(manifests)


def index_manifests(root_dir: Path, output_file: Path) -> dict:
    """
    Index all manifests and validate checksums.
    
    Args:
        root_dir: Repository root directory
        output_file: Path to write reliquary index
        
    Returns:
        Index dictionary
    """
    sealer = SnapshotSealer()
    manifests = find_manifests(root_dir)
    
    print(f"🔍 Found {len(manifests)} manifest.json files")
    
    index = {
        'generated_at': datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z'),
        'anchor_seed': 'EOS_SEED_ORION',
        'team': 'AUo959-team',
        'version': 'v0.1.0',
        'total_manifests': len(manifests),
        'manifests': []
    }
    
    checksum_mismatches = []
    
    for manifest_path in manifests:
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            # Compute checksum
            computed_checksum = sealer.compute_manifest_checksum(manifest)
            stored_checksum = manifest.get('checksum', None)
            
            # Check if checksum matches
            checksum_status = 'MATCH' if stored_checksum == computed_checksum else 'MISMATCH'
            if checksum_status == 'MISMATCH':
                checksum_mismatches.append(str(manifest_path))
            
            manifest_entry = {
                'path': str(manifest_path.relative_to(root_dir)),
                'module': manifest.get('module', 'unknown'),
                'version': manifest.get('version', 'unknown'),
                'checksum_computed': computed_checksum,
                'checksum_stored': stored_checksum,
                'checksum_status': checksum_status,
                'has_dlp_tags': 'dlp_tags' in manifest
            }
            
            index['manifests'].append(manifest_entry)
            
            status_icon = '✅' if checksum_status == 'MATCH' else '❌'
            print(f"  {status_icon} {manifest_entry['path']}")
            
        except Exception as e:
            print(f"  ⚠️  Error processing {manifest_path}: {e}")
    
    # Write index
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"\n📦 Reliquary index written to: {output_file}")
    
    if checksum_mismatches:
        print(f"\n⚠️  {len(checksum_mismatches)} manifest(s) with checksum mismatches:")
        for path in checksum_mismatches:
            print(f"    - {path}")
        print("\nRun compute-manifest-checksum to update checksums.")
    else:
        print("\n✅ All manifests have valid checksums")
    
    return index


def main():
    """Main indexer entry point"""
    parser = argparse.ArgumentParser(
        description='Aurora CloudBank Reliquary Indexer - Index and validate manifests'
    )
    parser.add_argument('--root', default='.', 
                        help='Repository root directory (default: current directory)')
    parser.add_argument('--output', default='.reliquary/reliquary_index.json',
                        help='Output index file path')
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    output_file = root_dir / args.output
    
    print("=" * 70)
    print("🗄️  Aurora CloudBank Reliquary Indexer")
    print("=" * 70)
    print(f"📁 Repository root: {root_dir}")
    print(f"📝 Output index: {output_file}")
    print()
    
    index = index_manifests(root_dir, output_file)
    
    return 0 if not any(m['checksum_status'] == 'MISMATCH' for m in index['manifests']) else 1


if __name__ == '__main__':
    sys.exit(main())
