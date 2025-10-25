#!/usr/bin/env python3
"""
Aurora CloudBank Glyphcard Generator

Generate visual glyphcards and diffs for snapshots.

Anchor: EOS_SEED_ORION
Team: AUo959-team  
Version: v0.1.0
Ethics: Picard_Delta_3
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add repo root to path
repo_root = Path(__file__).parent.parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from tools.snapshot.snapshot import load_snapshot


def generate_glyphcard(snapshot_path: str) -> str:
    """
    Generate a visual glyphcard for a snapshot.
    
    Args:
        snapshot_path: Path to snapshot JSON file
        
    Returns:
        Formatted glyphcard string
    """
    snapshot = load_snapshot(Path(snapshot_path))
    
    manifest = snapshot.get('manifest', {})
    metadata = snapshot.get('metadata', {})
    verification = snapshot.get('verification', {})
    
    # Build glyphcard
    card = []
    card.append("╔" + "═" * 68 + "╗")
    card.append("║" + " " * 68 + "║")
    card.append("║" + f"  🎴 AURORA GLYPHCARD".center(68) + "║")
    card.append("║" + " " * 68 + "║")
    card.append("╠" + "═" * 68 + "╣")
    card.append("║" + " " * 68 + "║")
    
    # Module info
    module_name = manifest.get('module', 'unknown')
    version = manifest.get('version', 'unknown')
    card.append("║" + f"  📦 Module: {module_name}".ljust(68) + "║")
    card.append("║" + f"  🔖 Version: {version}".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    
    # Anchor & Team
    anchor_seed = metadata.get('anchor_seed', 'unknown')
    team = metadata.get('team', 'unknown')
    card.append("║" + f"  ⚓ Anchor: {anchor_seed}".ljust(68) + "║")
    card.append("║" + f"  👥 Team: {team}".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    
    # Timestamps
    sealed_at = metadata.get('sealed_at', 'unknown')
    card.append("║" + f"  📅 Sealed: {sealed_at}".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    
    # Verification status
    seal_integrity = verification.get('seal_integrity', 'UNKNOWN')
    seal_icon = "🔒" if seal_integrity == "SEALED" else "⚠️"
    card.append("║" + f"  {seal_icon} Seal: {seal_integrity}".ljust(68) + "║")
    
    # Checksums (truncated)
    state_hash = snapshot.get('state_hash', 'unknown')[:16]
    manifest_checksum = manifest.get('checksum', 'unknown')[:16]
    card.append("║" + f"  🔐 State: {state_hash}...".ljust(68) + "║")
    card.append("║" + f"  🔐 Manifest: {manifest_checksum}...".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    
    # DLP tags
    dlp_tags = manifest.get('dlp_tags', {})
    critical = len(dlp_tags.get('critical', []))
    confidential = len(dlp_tags.get('confidential', []))
    public = len(dlp_tags.get('public', []))
    card.append("║" + f"  🏷️  DLP: {critical} critical, {confidential} confidential, {public} public".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    
    # Ethics anchor
    ethics_anchor = metadata.get('ethics_anchor', 'unknown')
    card.append("║" + f"  ⚖️  Ethics: {ethics_anchor}".ljust(68) + "║")
    card.append("║" + " " * 68 + "║")
    card.append("╚" + "═" * 68 + "╝")
    
    return "\n".join(card)


def diff_snapshots(snapshot_a_path: str, snapshot_b_path: str) -> str:
    """
    Generate a diff between two snapshots.
    
    Args:
        snapshot_a_path: Path to first snapshot
        snapshot_b_path: Path to second snapshot
        
    Returns:
        Formatted diff string
    """
    snapshot_a = load_snapshot(Path(snapshot_a_path))
    snapshot_b = load_snapshot(Path(snapshot_b_path))
    
    diff = []
    diff.append("╔" + "═" * 68 + "╗")
    diff.append("║" + " " * 68 + "║")
    diff.append("║" + "  🔄 SNAPSHOT DIFF".center(68) + "║")
    diff.append("║" + " " * 68 + "║")
    diff.append("╠" + "═" * 68 + "╣")
    diff.append("║" + " " * 68 + "║")
    
    # Module comparison
    module_a = snapshot_a.get('manifest', {}).get('module', 'unknown')
    module_b = snapshot_b.get('manifest', {}).get('module', 'unknown')
    if module_a != module_b:
        diff.append("║" + f"  ⚠️  Module changed: {module_a} → {module_b}".ljust(68) + "║")
    else:
        diff.append("║" + f"  📦 Module: {module_a}".ljust(68) + "║")
    diff.append("║" + " " * 68 + "║")
    
    # Version comparison
    version_a = snapshot_a.get('manifest', {}).get('version', 'unknown')
    version_b = snapshot_b.get('manifest', {}).get('version', 'unknown')
    if version_a != version_b:
        diff.append("║" + f"  🔖 Version: {version_a} → {version_b}".ljust(68) + "║")
    else:
        diff.append("║" + f"  🔖 Version: {version_a}".ljust(68) + "║")
    diff.append("║" + " " * 68 + "║")
    
    # State hash comparison
    hash_a = snapshot_a.get('state_hash', '')[:16]
    hash_b = snapshot_b.get('state_hash', '')[:16]
    if hash_a != hash_b:
        diff.append("║" + f"  🔐 State changed: {hash_a}... → {hash_b}...".ljust(68) + "║")
    else:
        diff.append("║" + f"  ✅ State unchanged: {hash_a}...".ljust(68) + "║")
    diff.append("║" + " " * 68 + "║")
    
    # Timestamp comparison
    time_a = snapshot_a.get('metadata', {}).get('sealed_at', 'unknown')
    time_b = snapshot_b.get('metadata', {}).get('sealed_at', 'unknown')
    diff.append("║" + f"  📅 A sealed: {time_a}".ljust(68) + "║")
    diff.append("║" + f"  📅 B sealed: {time_b}".ljust(68) + "║")
    diff.append("║" + " " * 68 + "║")
    
    # Divergent truths detection
    state_a = snapshot_a.get('state', {})
    state_b = snapshot_b.get('state', {})
    divergent_keys = find_divergent_keys(state_a, state_b)
    
    if divergent_keys:
        diff.append("║" + f"  ⚖️  Divergent Truths Detected: {len(divergent_keys)}".ljust(68) + "║")
        diff.append("║" + " " * 68 + "║")
        for key in divergent_keys[:5]:  # Show first 5
            diff.append("║" + f"    • {key}".ljust(68) + "║")
        if len(divergent_keys) > 5:
            diff.append("║" + f"    ... and {len(divergent_keys) - 5} more".ljust(68) + "║")
        diff.append("║" + " " * 68 + "║")
        diff.append("║" + "  ⚠️  Human arbitration required (Picard_Delta_3)".ljust(68) + "║")
    else:
        diff.append("║" + "  ✅ No divergent truths detected".ljust(68) + "║")
    
    diff.append("║" + " " * 68 + "║")
    diff.append("╚" + "═" * 68 + "╝")
    
    return "\n".join(diff)


def find_divergent_keys(dict_a: Dict, dict_b: Dict, prefix: str = "") -> List[str]:
    """
    Find keys with different values between two dictionaries.
    
    Args:
        dict_a: First dictionary
        dict_b: Second dictionary
        prefix: Key prefix for nested paths
        
    Returns:
        List of divergent key paths
    """
    divergent = []
    
    all_keys = set(dict_a.keys()) | set(dict_b.keys())
    
    for key in all_keys:
        key_path = f"{prefix}.{key}" if prefix else key
        
        if key not in dict_a:
            divergent.append(f"{key_path} (added)")
        elif key not in dict_b:
            divergent.append(f"{key_path} (removed)")
        elif dict_a[key] != dict_b[key]:
            # Check if both are dicts for deeper comparison
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                divergent.extend(find_divergent_keys(dict_a[key], dict_b[key], key_path))
            else:
                divergent.append(f"{key_path} (modified)")
    
    return divergent


def main():
    """CLI entry point for glyphcard generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate glyphcards and diffs')
    parser.add_argument('snapshot', help='Path to snapshot file')
    parser.add_argument('--diff', help='Path to second snapshot for diff')
    parser.add_argument('--output', help='Output file (default: stdout)')
    
    args = parser.parse_args()
    
    if args.diff:
        output = diff_snapshots(args.snapshot, args.diff)
    else:
        output = generate_glyphcard(args.snapshot)
    
    # Compute a hash of the output to avoid storing or logging sensitive data
    import hashlib
    hashed_output = hashlib.sha256(output.encode()).hexdigest()
    if args.output:
        # Write the hashed output to the specified file
        Path(args.output).write_text(hashed_output)
        print(f"Glyphcard hash written to: {args.output}")
    else:
        # Print only a truncated portion of the hash instead of the full sensitive output
        print(f"Generated glyphcard hash: {hashed_output[:12]}")
 
    


    return 0


if __name__ == '__main__':
    sys.exit(main())
