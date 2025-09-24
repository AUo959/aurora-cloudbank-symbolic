#!/usr/bin/env python3
"""
Aurora Developer CLI - Unified command interface for all symbolic operations
Part of T71 Symbolic Infrastructure Genesis

Primary functions:
- Automated manifest generation for any module/export
- Thread sealing and resume capabilities
- Integration with existing Aurora/GUMAS infrastructure
- State snapshot and restore commands
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add workspace root to Python path so 'tools' is importable
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(WORKSPACE_ROOT))

from tools.symbolic.memory_sealer import MemorySealingEngine  # noqa: E402
from tools.symbolic.anchor_tracker import SymbolicAnchorTracker  # noqa: E402


class AuroraDeveloperCLI:
    """Unified command interface for Aurora symbolic operations"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.anchor_tracker = SymbolicAnchorTracker(repo_path)
        self.memory_sealer = MemorySealingEngine(repo_path)
        self.version = "1.0.0"

    def print_banner(self):
        """Print Aurora Developer CLI banner"""
        banner = """
╔═══════════════════════════════════════════════════╗
║              Aurora Developer CLI                 ║
║        T71 Symbolic Infrastructure Genesis        ║
║              Version {self.version}                       ║
╚═══════════════════════════════════════════════════╝

🌟 Symbolic Operations Toolkit
⚓ Anchor Tracking & Resolution
🔐 Memory Sealing & Recovery
📄 Automated Manifest Generation

"""
        print(banner)

    def cmd_anchor(self, args) -> int:
        """Handle anchor tracking commands"""
        if args.anchor_cmd == "track":
            return self._anchor_track(args)
        elif args.anchor_cmd == "resolve":
            return self._anchor_resolve(args)
        elif args.anchor_cmd == "seal":
            return self._anchor_seal(args)
        else:
            print(f"❌ Unknown anchor command: {args.anchor_cmd}")
            return 1

    def _anchor_track(self, args) -> int:
        """Track symbolic anchors across repository"""
        if not getattr(args, "json", False):
            print("🔍 Tracking symbolic anchors...")

        try:
            # Unified track flow with built-in filtering in tracker
            exts = args.ext if getattr(args, "ext", None) else None
            since_dt = None
            if getattr(args, "since", None):
                try:
                    since_dt = datetime.fromisoformat(args.since)
                except ValueError:
                    try:
                        since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                    except ValueError:
                        print("⚠️  Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
            found_anchors = self.anchor_tracker.scan_repository(
                extensions=exts, since=since_dt, pattern=getattr(args, "pattern", None)
            )
            total_anchors = sum(len(a) for a in found_anchors.values())

            if args.json:
                payload = {
                    "pattern": getattr(args, "pattern", None),
                    "since": getattr(args, "since", None),
                    "total_files": len(found_anchors),
                    "total_anchors": total_anchors,
                    "files": {fp: [a.__dict__ for a in anns] for fp, anns in found_anchors.items()},
                }
                print(json.dumps(payload, separators=(",", ":")))
            else:
                if args.pattern:
                    print(
                        f"Found {total_anchors} anchors matching '{args.pattern}' in {len(found_anchors)} files:"
                    )
                else:
                    print(f"Found {total_anchors} anchors in {len(found_anchors)} files:")

                # Group by anchor type
                by_type = {}
                for file_anchors in found_anchors.values():
                    for anchor in file_anchors:
                        if anchor.anchor_type not in by_type:
                            by_type[anchor.anchor_type] = []
                        by_type[anchor.anchor_type].append(anchor)

                for anchor_type, anchors in by_type.items():
                    print(f"\n{anchor_type}: {len(anchors)} anchors")
                    for anchor in anchors[:5]:  # Show first 5
                        print(f"  ⚓ {anchor.anchor_id} in {anchor.file_path}")
                    if len(anchors) > 5:
                        print(f"    ... and {len(anchors) - 5} more")

            return 0

        except Exception as e:
            print(f"❌ Error tracking anchors: {e}")
            return 1

    def _anchor_resolve(self, args) -> int:
        """Resolve specific anchor lineage"""
        if not args.anchor_id:
            print("❌ --anchor required for resolve command")
            return 1

        if not getattr(args, "json", False):
            print(f"🔍 Resolving anchor: {args.anchor_id}")

        try:
            # First scan to populate anchors (respect optional --since)
            since_dt = None
            if getattr(args, "since", None):
                try:
                    since_dt = datetime.fromisoformat(args.since)
                except ValueError:
                    try:
                        since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                    except ValueError:
                        print("⚠️  Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
            self.anchor_tracker.scan_repository(since=since_dt)

            # Resolve the specific anchor
            anchor = self.anchor_tracker.resolve_anchor(args.anchor_id)

            if anchor:
                # Build lineage
                lineages = self.anchor_tracker.build_lineage_map()
                lineage = lineages.get(args.anchor_id)

                if getattr(args, "json", False):
                    payload = {
                        "anchor": anchor.__dict__,
                        "lineage": lineage.__dict__ if lineage else None,
                    }
                    print(json.dumps(payload, separators=(",", ":")))
                else:
                    print("\n⚓ Anchor Details:")
                    print(f"  ID: {anchor.anchor_id}")
                    print(f"  Type: {anchor.anchor_type}")
                    print(f"  Location: {anchor.file_path}:{anchor.line_number}")
                    print(f"  Context: {anchor.context}")
                    print(f"  Hash: {anchor.sha256_hash}")
                    print(f"  Timestamp: {anchor.timestamp}")

                    if lineage:
                        print("\n🔗 Lineage Information:")
                        print(f"  Generation: {lineage.generation}")
                        print(f"  Ancestors: {lineage.ancestors if lineage.ancestors else 'None'}")
                        print(f"  Descendants: {lineage.descendants if lineage.descendants else 'None'}")
                        print(f"  Lineage Hash: {lineage.lineage_hash}")
                    else:
                        print("  No lineage information available")
            else:
                print(f"❌ Anchor {args.anchor_id} not found")
                return 1

            return 0

        except Exception as e:
            print(f"❌ Error resolving anchor: {e}")
            return 1

    def _anchor_seal(self, args) -> int:
        """Seal anchor thread with memory protection"""
        if not args.anchor_id:
            print("❌ --anchor required for seal command")
            return 1

        print(f"🔐 Sealing anchor thread: {args.anchor_id}")

        try:
            description = f"Thread seal for {args.anchor_id}"
            seal = self.memory_sealer.seal_thread(args.anchor_id, description)

            print("✅ Thread sealed successfully:")
            print(f"  Seal ID: {seal.seal_id}")
            print(f"  Hash: {seal.sha256_hash}")
            print(f"  Files: {seal.recovery_data.get('file_count', 'Unknown')}")
            print(f"  Timestamp: {seal.timestamp}")

            return 0

        except Exception as e:
            print(f"❌ Error sealing anchor thread: {e}")
            return 1

    def cmd_seal(self, args) -> int:
        """Handle memory sealing commands"""
        if not args.target:
            print("❌ Target required for seal command")
            return 1

        try:
            target_path = Path(args.target)

            if args.verify:
                # Verify existing seal
                if not args.seal_id:
                    print("❌ --seal-id required for verification")
                    return 1

                result = self.memory_sealer.verify_seal(args.seal_id)

                if result["status"] == "valid":
                    print(f"✅ Seal {args.seal_id} is valid")
                else:
                    print(f"❌ Seal {args.seal_id} is invalid:")
                    for issue in result["issues"]:
                        print(f"   - {issue}")

                return 0 if result["status"] == "valid" else 1
            else:
                # Create new seal
                print(f"🔐 Sealing: {args.target}")

                if target_path.is_file():
                    seal = self.memory_sealer.seal_file(target_path, args.seal_id)
                    print(f"✅ File sealed: {seal.seal_id}")
                elif target_path.is_dir():
                    seal = self.memory_sealer.seal_directory(target_path, args.seal_id)
                    print(f"✅ Directory sealed: {seal.seal_id}")
                else:
                    # Assume it's a thread anchor
                    seal = self.memory_sealer.seal_thread(args.target, f"Manual seal of {args.target}")
                    print(f"✅ Thread sealed: {seal.seal_id}")

                print(f"   Hash: {seal.sha256_hash}")
                print(f"   Timestamp: {seal.timestamp}")

                return 0

        except Exception as e:
            print(f"❌ Error in seal operation: {e}")
            return 1

    def cmd_restore(self, args) -> int:
        """Handle state restoration"""
        if not args.anchor_or_seal_id:
            print("❌ Anchor or seal ID required for restore command")
            return 1

        try:
            print(f"🔄 Restoring state: {args.anchor_or_seal_id}")

            result = self.memory_sealer.restore_sealed_state(
                args.anchor_or_seal_id,
                args.target_path,
                args.dry
            )

            if result["status"] == "dry_run_complete":
                print("🔍 Dry run - would perform these actions:")
            elif result["status"] == "restored":
                print("✅ State restored successfully:")
            elif result["status"] == "error":
                print("❌ Restore failed:")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                return 1

            for action in result["actions"]:
                print(f"   - {action}")

            return 0

        except Exception as e:
            print(f"❌ Error restoring state: {e}")
            return 1

    def cmd_manifest(self, args) -> int:
        """Generate export manifest"""
        try:
            if not getattr(args, "json", False):
                print("📄 Generating manifest...")

            # Scan repository first
            since_dt = None
            if getattr(args, "since", None):
                try:
                    since_dt = datetime.fromisoformat(args.since)
                except ValueError:
                    try:
                        since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                    except ValueError:
                        print("⚠️  Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
            self.anchor_tracker.scan_repository(
                since=since_dt, 
                pattern=getattr(args, "pattern", None),
                quick_scan=True,
                max_files=800
            )
            self.anchor_tracker.build_lineage_map()

            if args.target:
                # Generate manifest for specific anchor
                manifest = self.anchor_tracker.generate_export_manifest(args.target)
                if not getattr(args, "json", False):
                    print(f"✅ Manifest generated for anchor: {args.target}")
            else:
                # Generate repository-wide manifest
                manifest = self.anchor_tracker.generate_export_manifest()
                if not getattr(args, "json", False):
                    print("✅ Repository manifest generated")

            # Save manifest
            output_path = args.output or f"T71_MANIFEST_{datetime.now().strftime('%Y%m%dT%H%M%SZ')}.json"
            saved_path = self.anchor_tracker.save_manifest(manifest, output_path) or output_path

            # Optional: also export DLP manifest
            dlp_saved = None
            if getattr(args, "dlp_manifest_out", None) and getattr(self.anchor_tracker, "dlp_tracker", None):
                try:
                    dlp_manifest = self.anchor_tracker.dlp_tracker.create_export_manifest(
                        "anchor_tracker_export", tag_ids=list(self.anchor_tracker.dlp_tracker.tags.keys())
                    )
                    dlp_path = Path(args.dlp_manifest_out)
                    dlp_path.write_text(json.dumps(dlp_manifest, indent=2), encoding="utf-8")
                    dlp_saved = str(dlp_path)
                except Exception as e:
                    print(f"⚠️  Failed to export DLP manifest: {e}")

            if getattr(args, "json", False):
                print(
                    json.dumps(
                        {"manifest_path": saved_path, "dlp_manifest_path": dlp_saved, "manifest": manifest},
                        separators=(",", ":"),
                    )
                )
            else:
                print(f"📄 Saved to: {saved_path}")
                print(f"🔐 Memory seal: {manifest['memory_seal']}")

            # Display key information
            if not getattr(args, "json", False) and "anchor_details" in manifest:
                anchor = manifest["anchor_details"]
                print(f"📍 Anchor: {anchor['anchor_id']} ({anchor['anchor_type']})")
                print(f"📁 Location: {anchor['file_path']}:{anchor['line_number']}")
            elif not getattr(args, "json", False):
                print(f"📊 Total anchors: {manifest.get('total_anchors', 0)}")
                print(f"🔗 Lineages mapped: {manifest.get('lineages_mapped', 0)}")

            return 0

        except Exception as e:
            print(f"❌ Error generating manifest: {e}")
            return 1

    def cmd_diff(self, args) -> int:
        """Compare states between anchors"""
        if not args.anchor1 or not args.anchor2:
            print("❌ Two anchors required for diff command")
            return 1

        try:
            print(f"📊 Comparing {args.anchor1} vs {args.anchor2}")

            # Scan and resolve both anchors
            self.anchor_tracker.scan_repository()
            self.anchor_tracker.build_lineage_map()

            anchor1 = self.anchor_tracker.resolve_anchor(args.anchor1)
            anchor2 = self.anchor_tracker.resolve_anchor(args.anchor2)

            if not anchor1:
                print(f"❌ Anchor not found: {args.anchor1}")
                return 1

            if not anchor2:
                print(f"❌ Anchor not found: {args.anchor2}")
                return 1

            # Compare basic properties
            print("\n📍 Anchor Comparison:")
            print(f"  {args.anchor1}:")
            print(f"    Type: {anchor1.anchor_type}")
            print(f"    Location: {anchor1.file_path}:{anchor1.line_number}")
            print(f"    Hash: {anchor1.sha256_hash[:16]}...")

            print(f"  {args.anchor2}:")
            print(f"    Type: {anchor2.anchor_type}")
            print(f"    Location: {anchor2.file_path}:{anchor2.line_number}")
            print(f"    Hash: {anchor2.sha256_hash[:16]}...")

            # Compare lineages
            lineage1 = self.anchor_tracker.lineages.get(args.anchor1)
            lineage2 = self.anchor_tracker.lineages.get(args.anchor2)

            if lineage1 and lineage2:
                print("\n🔗 Lineage Comparison:")
                print(f"  {args.anchor1}: Gen {lineage1.generation}, "
                      f"{len(lineage1.ancestors)} ancestors, "
                      f"{len(lineage1.descendants)} descendants")
                print(f"  {args.anchor2}: Gen {lineage2.generation}, "
                      f"{len(lineage2.ancestors)} ancestors, "
                      f"{len(lineage2.descendants)} descendants")

                # Find common ancestors
                common_ancestors = set(lineage1.ancestors) & set(lineage2.ancestors)
                if common_ancestors:
                    print(f"  Common ancestors: {list(common_ancestors)}")
                else:
                    print("  No common ancestors found")

            return 0

        except Exception as e:
            print(f"❌ Error comparing anchors: {e}")
            return 1

    def cmd_status(self, args) -> int:
        """Show system status"""
        if not getattr(args, "json", False):
            print("📊 Aurora Symbolic Infrastructure Status")
            print("=" * 50)

        try:
            # Scan repository
            exts = args.ext if getattr(args, "ext", None) else None
            since_dt = None
            if getattr(args, "since", None):
                try:
                    since_dt = datetime.fromisoformat(args.since)
                except ValueError:
                    try:
                        since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                    except ValueError:
                        print("⚠️  Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
            anchors = self.anchor_tracker.scan_repository(
                extensions=exts,
                since=since_dt,
                pattern=getattr(args, "pattern", None),
                quick_scan=True,  # Enable quick scan for status command
                max_files=500,    # Limit files for performance
            )
            total_anchors = sum(len(a) for a in anchors.values())
            if not getattr(args, "json", False):
                print(f"⚓ Anchors: {total_anchors} found in {len(anchors)} files")

            # Build lineages
            lineages = self.anchor_tracker.build_lineage_map()
            if not getattr(args, "json", False):
                print(f"🔗 Lineages: {len(lineages)} mapped")

            # Check for drift
            drift_issues = self.anchor_tracker.detect_drift()
            drift_count = sum(len(issues) for issues in drift_issues.values())
            if getattr(args, "json", False):
                payload = {
                    "total_files": len(anchors),
                    "total_anchors": total_anchors,
                    "lineages_mapped": len(lineages),
                    "drift": {k: len(v) for k, v in drift_issues.items()},
                    "repo": str(self.repo_path),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "version": self.version,
                }
                print(json.dumps(payload, separators=(",", ":")))
            else:
                if drift_count == 0:
                    print("✅ Drift Status: No issues detected")
                else:
                    print(f"⚠️  Drift Status: {drift_count} issues detected")
                    for issue_type, issues in drift_issues.items():
                        if issues:
                            print(f"   {issue_type}: {len(issues)}")

                # Memory seals status
                seals_count = len(self.memory_sealer.seals)
                print(f"🔐 Memory Seals: {seals_count} active")

                # Repository info
                print(f"\n📁 Repository: {self.repo_path}")
                print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🔢 CLI Version: {self.version}")

            return 0

        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return 1


def create_parser():
    """Create argument parser for Aurora CLI"""
    parser = argparse.ArgumentParser(
        description="Aurora Developer CLI - Symbolic Infrastructure Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    aurora-cli anchor track T70                       # Track T70-related anchors
    aurora-cli anchor track --ext .md --json          # Track anchors in markdown, JSON output
    aurora-cli anchor track --pattern INFRA --since 2025-09-01
    aurora-cli anchor resolve T70_DOC_REORG           # Resolve specific anchor
    aurora-cli seal tools/symbolic --verify           # Seal and verify directory
    aurora-cli restore T70_SEAL_123 --dry             # Dry run restore
    aurora-cli manifest --target T71_INFRA            # Generate manifest for T71
    aurora-cli manifest --json --since 2025-09-01T00:00:00
    aurora-cli diff T70_DOC_REORG T71_INFRA           # Compare two anchors
    aurora-cli status                                 # Show system status
    aurora-cli status --json --since 2025-09-15       # Machine-readable status since a date
"""
    )

    parser.add_argument("--version", action="version", version="Aurora CLI 1.0.0")
    parser.add_argument("--repo", "-r", default=".", help="Repository path")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Anchor tracking commands
    anchor_parser = subparsers.add_parser("anchor", help="Anchor tracking operations")
    anchor_subparsers = anchor_parser.add_subparsers(dest="anchor_cmd")

    # anchor track
    track_parser = anchor_subparsers.add_parser("track", help="Track symbolic anchors")
    track_parser.add_argument("pattern", nargs="?", help="Pattern to search for")
    track_parser.add_argument("--json", action="store_true", help="Emit JSON output for machine parsing")
    track_parser.add_argument(
        "--ext",
        action="append",
        help="File extensions to scan (repeatable). Example: --ext .py --ext .md",
    )
    track_parser.add_argument("--since", help="Only include files modified on/after this time (ISO 8601 or YYYY-MM-DD)")

    # anchor resolve
    resolve_parser = anchor_subparsers.add_parser("resolve", help="Resolve anchor lineage")
    resolve_parser.add_argument("anchor_id", help="Anchor ID to resolve")
    resolve_parser.add_argument("--json", action="store_true", help="Emit JSON output for machine parsing")
    resolve_parser.add_argument(
        "--since",
        help="Only include files modified on/after this time (ISO 8601 or YYYY-MM-DD)",
    )

    # anchor seal
    seal_anchor_parser = anchor_subparsers.add_parser("seal", help="Seal anchor thread")
    seal_anchor_parser.add_argument("anchor_id", help="Anchor ID to seal")

    # Memory sealing commands
    seal_parser = subparsers.add_parser("seal", help="Memory sealing operations")
    seal_parser.add_argument("target", help="Target to seal")
    seal_parser.add_argument("--seal-id", "-s", help="Custom seal ID")
    seal_parser.add_argument("--verify", "-v", action="store_true", help="Verify existing seal")

    # State restoration
    restore_parser = subparsers.add_parser("restore", help="Restore sealed state")
    restore_parser.add_argument("anchor_or_seal_id", help="Anchor or seal ID to restore")
    restore_parser.add_argument("--target-path", "-t", help="Target path for restoration")
    restore_parser.add_argument("--dry", "-d", action="store_true", help="Dry run")

    # Manifest generation
    manifest_parser = subparsers.add_parser("manifest", help="Generate export manifest")
    manifest_parser.add_argument("--target", "-t", help="Specific anchor target")
    manifest_parser.add_argument("--output", "-o", help="Output file path")
    manifest_parser.add_argument("--json", action="store_true", help="Emit JSON output for machine parsing")
    manifest_parser.add_argument(
        "--dlp-manifest-out",
        help="Also export a DLP manifest (if available) to this path",
    )
    manifest_parser.add_argument("--pattern", help="Filter anchors by substring across ID and context")
    manifest_parser.add_argument(
        "--since",
        help="Only include files modified on/after this time (ISO 8601 or YYYY-MM-DD)",
    )

    # State comparison
    diff_parser = subparsers.add_parser("diff", help="Compare anchor states")
    diff_parser.add_argument("anchor1", help="First anchor to compare")
    diff_parser.add_argument("anchor2", help="Second anchor to compare")

    # System status
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--json", action="store_true", help="Emit JSON output for machine parsing")
    status_parser.add_argument(
        "--ext",
        action="append",
        help="File extensions to scan (repeatable). Example: --ext .py --ext .md",
    )
    status_parser.add_argument("--pattern", help="Filter anchors by substring across ID and context")
    status_parser.add_argument(
        "--since",
        help="Only include files modified on/after this time (ISO 8601 or YYYY-MM-DD)",
    )

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    cli = AuroraDeveloperCLI(args.repo)

    # Route commands to appropriate handlers
    if args.command == "anchor":
        return cli.cmd_anchor(args)
    elif args.command == "seal":
        return cli.cmd_seal(args)
    elif args.command == "restore":
        return cli.cmd_restore(args)
    elif args.command == "manifest":
        return cli.cmd_manifest(args)
    elif args.command == "diff":
        return cli.cmd_diff(args)
    elif args.command == "status":
        return cli.cmd_status(args)
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
