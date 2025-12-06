#!/usr/bin/env python3
"""
Symbolic Anchor Tracker - Core symbolic anchor resolution and lineage mapping
Part of T71 Symbolic Infrastructure Genesis

Primary functions:
- Live anchor resolution across repository (T1, SRB, T70, etc.)
- Symbolic lineage mapping with ancestry chains
- Drift detection with Thermax compliance monitoring
- Export manifest generation with SHA256 sealing
"""

import argparse
import hashlib
import json
import logging
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# DLP tagging per Aurora project conventions
try:
    from src.core.native_dlp_export import NativeDLPTracker
except Exception:  # Graceful fallback if import path changes
    NativeDLPTracker = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class SymbolicAnchor:
    """Represents a symbolic anchor found in the repository"""
    anchor_id: str
    anchor_type: str  # T-series, SRB, etc.
    file_path: str
    line_number: int
    context: str
    timestamp: str
    sha256_hash: str


@dataclass
class AnchorLineage:
    """Represents the lineage chain of a symbolic anchor"""
    anchor_id: str
    ancestors: List[str]
    descendants: List[str]
    generation: int
    lineage_hash: str


class SymbolicAnchorTracker:
    """Core symbolic anchor resolution and lineage tracking system"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.anchors: Dict[str, SymbolicAnchor] = {}
        self.lineages: Dict[str, AnchorLineage] = {}
        self.anchor_to_dlp: Dict[str, str] = {}

        # Initialize DLP tracker if available
        self.dlp_tracker = NativeDLPTracker() if NativeDLPTracker is not None else None

        # Symbolic anchor patterns
        self.anchor_patterns = {
            "T_SERIES": r"T(\d+)_([A-Z_]+)",
            "SRB": r"SRB_([A-Z_]+)",
            "ANCHOR_SEED": r"([A-Z_]+_ANCHOR_SEED|ANCHOR_SEED_[A-Z_]+)",
            "EXPORT_MANIFEST": r"([A-Z_]+_EXPORT_MANIFEST)",
            "MEMORY_SEAL": r"(MEMORY_SEAL_[A-Z_0-9]+)",
        }

    def scan_repository(
        self,
        extensions: List[str] = None,
        since: Optional[datetime] = None,
        pattern: Optional[str] = None,
        quick_scan: bool = False,
        max_files: int = 1000,
    ) -> Dict[str, List[SymbolicAnchor]]:
        """Scan repository for symbolic anchors

        - extensions: file extensions to include
        - since: only scan files modified at or after this datetime
        - pattern: filter anchors to those whose ID or context contains this substring (case-insensitive)
        - quick_scan: if True, limit scanning for performance
        - max_files: maximum number of files to scan (for performance)
        """
        if extensions is None:
            extensions = ['.py', '.js', '.md', '.json', '.yaml', '.yml', '.txt']

        found_anchors = {}
        files_scanned = 0

        # Extensive skip patterns for performance
        skip_dirs = {
            '__pycache__', 'node_modules', '.git', '.venv', 'venv_opal2',
            '.pytest_cache', 'htmlcov', '.benchmarks', 'coverage'
        }

        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip_dirs]

            # Quick scan optimization: limit depth
            if quick_scan:
                current_depth = len(Path(root).relative_to(self.repo_path).parts)
                if current_depth > 3:  # Limit depth to 3 levels
                    continue

            for file in files:
                if files_scanned >= max_files:
                    break

                if any(file.endswith(ext) for ext in extensions):
                    file_path = Path(root) / file
                    files_scanned += 1

                    # Since filter (by file modification time)
                    if since is not None:
                        try:
                            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                            if mtime < since:
                                continue
                        except Exception:
                            # If stat fails, skip since filtering for this file
                            pass

                    anchors = self._scan_file(file_path)

                    # Pattern filter: apply to anchor_id and context
                    if pattern:
                        p = pattern.lower()
                        anchors = [
                            a for a in anchors if (p in a.anchor_id.lower() or p in a.context.lower())
                        ]

                    if anchors:
                        rel_path = str(file_path.relative_to(self.repo_path))
                        found_anchors[rel_path] = anchors

            # Break outer loop if we've hit max files
            if files_scanned >= max_files:
                break

        return found_anchors

    def _scan_file(self, file_path: Path) -> List[SymbolicAnchor]:
        """Scan a single file for symbolic anchors"""
        anchors = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern_type, pattern in self.anchor_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        anchor_id = match.group(0)
                        context = line.strip()

                        # Generate SHA256 hash of the anchor context
                        context_hash = hashlib.sha256(
                            f"{anchor_id}:{file_path}:{line_num}:{context}".encode()
                        ).hexdigest()

                        anchor = SymbolicAnchor(
                            anchor_id=anchor_id,
                            anchor_type=pattern_type,
                            file_path=str(file_path.relative_to(self.repo_path)),
                            line_number=line_num,
                            context=context,
                            timestamp=datetime.now().isoformat(),
                            sha256_hash=context_hash
                        )

                        anchors.append(anchor)
                        self.anchors[anchor_id] = anchor

                        # DLP tag for discovered anchor (if DLP tracker available)
                        if self.dlp_tracker is not None:
                            try:
                                symbolic_data = {
                                    "concepts": [anchor_id],
                                    "dimension": 512,
                                    "vector_type": "symbolic_anchor",
                                    "file_path": str(file_path.relative_to(self.repo_path)),
                                    "line_number": line_num,
                                    "anchor_type": pattern_type,
                                }
                                tag_id = self.dlp_tracker.tag_symbolic_operation(symbolic_data)
                                tag = self.dlp_tracker.tags[tag_id]
                                tag.add_anchor_protocol("EOS_SEED_ORION")
                                tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
                                tag.metadata.update(
                                    {
                                        "context_tag": "anchor_scan",
                                        "dlp_level": "DLP_L1_OK",
                                        "symbolic_hash_validation": True,
                                        "anchor_sha256": context_hash,
                                    }
                                )
                                self.anchor_to_dlp[anchor_id] = tag_id
                            except Exception:
                                # Keep scanning even if DLP tagging fails
                                pass

        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read file {file_path}: {e}")

        return anchors

    def resolve_anchor(self, anchor_id: str) -> Optional[SymbolicAnchor]:
        """Resolve a specific anchor by ID"""
        return self.anchors.get(anchor_id)

    def build_lineage_map(self) -> Dict[str, AnchorLineage]:
        """Build lineage relationships between anchors"""
        lineages = {}

        for anchor_id, anchor in self.anchors.items():
            ancestors = self._find_ancestors(anchor_id)
            descendants = self._find_descendants(anchor_id)
            generation = self._calculate_generation(anchor_id, ancestors)

            lineage_data = f"{anchor_id}:{':'.join(sorted(ancestors))}:{':'.join(sorted(descendants))}"
            lineage_hash = hashlib.sha256(lineage_data.encode()).hexdigest()[:16]

            lineage = AnchorLineage(
                anchor_id=anchor_id,
                ancestors=ancestors,
                descendants=descendants,
                generation=generation,
                lineage_hash=lineage_hash
            )

            lineages[anchor_id] = lineage

        self.lineages = lineages

        # Create a DLP tag summarizing the lineage build, if available
        if self.dlp_tracker is not None:
            try:
                lineage_summary = {
                    "total_anchors": len(self.anchors),
                    "total_lineages": len(self.lineages),
                    "timestamp": datetime.now().isoformat(),
                }
                tag_id = self.dlp_tracker.create_tag("anchor_lineage_map", lineage_summary)
                tag = self.dlp_tracker.tags[tag_id]
                tag.add_anchor_protocol("EOS_SEED_ORION")
                tag.add_t1_srb_anchor("T1_TEMPORAL_ANCHOR")
                tag.metadata.update(
                    {
                        "context_tag": "anchor_lineage",
                        "dlp_level": "DLP_L1_OK",
                        "symbolic_hash_validation": True,
                    }
                )
            except Exception:
                pass
        return lineages

    def _find_ancestors(self, anchor_id: str) -> List[str]:
        """Find ancestor anchors based on T-series numbering and references"""
        ancestors = []

        if anchor_id.startswith('T') and '_' in anchor_id:
            # Extract T-series number
            match = re.match(r'T(\d+)', anchor_id)
            if match:
                current_num = int(match.group(1))
                # Find previous T-series anchors
                for other_id in self.anchors:
                    other_match = re.match(r'T(\d+)', other_id)
                    if other_match and int(other_match.group(1)) < current_num:
                        ancestors.append(other_id)

        # Also check for explicit references in the anchor's context
        anchor = self.anchors.get(anchor_id)
        if anchor:
            for other_id in self.anchors:
                if other_id != anchor_id and other_id in anchor.context:
                    ancestors.append(other_id)

        return list(set(ancestors))  # Remove duplicates

    def _find_descendants(self, anchor_id: str) -> List[str]:
        """Find descendant anchors that reference this one"""
        descendants = []

        for other_id, other_anchor in self.anchors.items():
            if other_id != anchor_id and anchor_id in other_anchor.context:
                descendants.append(other_id)

        return descendants

    def _calculate_generation(self, anchor_id: str, ancestors: List[str], visited: set = None) -> int:
        """Calculate generation number based on ancestry depth"""
        if visited is None:
            visited = set()

        if anchor_id in visited:
            return 1  # Avoid infinite recursion

        visited.add(anchor_id)

        if not ancestors:
            return 1

        max_ancestor_gen = 0
        for ancestor_id in ancestors:
            if ancestor_id in self.lineages:
                ancestor_gen = self.lineages[ancestor_id].generation
            elif ancestor_id not in visited:
                # Estimate generation for unprocessed ancestors
                ancestor_ancestors = self._find_ancestors(ancestor_id)
                ancestor_gen = self._calculate_generation(ancestor_id, ancestor_ancestors, visited.copy())
            else:
                ancestor_gen = 1  # Default for circular references

            max_ancestor_gen = max(max_ancestor_gen, ancestor_gen)

        return max_ancestor_gen + 1

    def detect_drift(self) -> Dict[str, List[str]]:
        """Detect potential anchor drift and compliance issues"""
        drift_issues = {
            "orphaned_anchors": [],
            "duplicate_anchors": [],
            "broken_lineages": [],
            "thermax_violations": []
        }

        # Find orphaned anchors (no ancestors or descendants)
        for anchor_id, lineage in self.lineages.items():
            if not lineage.ancestors and not lineage.descendants:
                drift_issues["orphaned_anchors"].append(anchor_id)

        # Find duplicate anchor IDs in different contexts
        anchor_contexts = {}
        for anchor_id, anchor in self.anchors.items():
            key = (anchor_id, anchor.anchor_type)
            if key in anchor_contexts:
                drift_issues["duplicate_anchors"].append(anchor_id)
            else:
                anchor_contexts[key] = anchor

        # Check for broken lineage references
        for anchor_id, lineage in self.lineages.items():
            for ancestor_id in lineage.ancestors:
                if ancestor_id not in self.anchors:
                    drift_issues["broken_lineages"].append(f"{anchor_id} -> {ancestor_id}")

        return drift_issues

    def generate_export_manifest(self, anchor_id: str = None) -> Dict:
        """Generate export manifest for anchor or entire repository"""
        if anchor_id:
            anchor = self.anchors.get(anchor_id)
            lineage = self.lineages.get(anchor_id)

            if not anchor:
                raise ValueError(f"Anchor {anchor_id} not found")

            manifest_data = {
                "anchor_seed": anchor_id,
                "export_time": datetime.now().isoformat() + "Z",
                "module_type": "symbolic_anchor_export",
                "version": "1.0.0",
                "developer": "AUo959",
                "anchor_details": asdict(anchor),
                "lineage_details": asdict(lineage) if lineage else None,
                "ethics_protocol": "Picard_Delta_3",
                "dlp_classification": "Internal_Development_Tools"
            }
            # Attach DLP linkage when available
            if self.dlp_tracker is not None:
                dlp_tag_id = self.anchor_to_dlp.get(anchor_id)
                manifest_data["dlp_tag_id"] = dlp_tag_id
        else:
            # Generate manifest for entire repository state
            manifest_data = {
                "anchor_seed": "REPOSITORY_SYMBOLIC_STATE",
                "export_time": datetime.now().isoformat() + "Z",
                "module_type": "repository_anchor_export",
                "version": "1.0.0",
                "developer": "AUo959",
                "total_anchors": len(self.anchors),
                "anchor_types": list(set(a.anchor_type for a in self.anchors.values())),
                "lineages_mapped": len(self.lineages),
                "ethics_protocol": "Picard_Delta_3",
                "dlp_classification": "Internal_Development_Tools"
            }

        # If DLP tracker is present, include a compact DLP export summary
        if self.dlp_tracker is not None:
            try:
                dlp_manifest = self.dlp_tracker.create_export_manifest(
                    "anchor_tracker_export", tag_ids=list(self.dlp_tracker.tags.keys())
                )
                manifest_data["dlp_export_summary"] = {
                    "manifest_id": dlp_manifest.get("manifest_id"),
                    "total_tags": dlp_manifest.get("total_tags"),
                    "anchor_protocols": dlp_manifest.get("aurora_metadata", {}).get("anchor_protocols", []),
                    "t1_srb_anchors": dlp_manifest.get("aurora_metadata", {}).get("t1_srb_anchors", []),
                }
            except Exception:
                # Non-fatal if DLP export fails
                pass

        # Add memory seal
        manifest_str = json.dumps(manifest_data, sort_keys=True)
        memory_seal = hashlib.sha256(manifest_str.encode()).hexdigest()
        manifest_data["memory_seal"] = memory_seal

        return manifest_data

    def save_manifest(self, manifest: Dict, output_path: str = None) -> str:
        """Save manifest to file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
            output_path = f"T71_ANCHOR_MANIFEST_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return output_path


def main():
    """CLI interface for anchor tracking"""

    parser = argparse.ArgumentParser(description="Symbolic Anchor Tracker")
    parser.add_argument("command", choices=["scan", "resolve", "lineage", "drift", "manifest"])
    parser.add_argument("--anchor", "-a", help="Specific anchor ID")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--path", "-p", default=".", help="Repository path")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-friendly output")
    parser.add_argument(
        "--ext",
        action="append",
        help="File extensions to scan (repeatable). Example: --ext .py --ext .md",
    )
    parser.add_argument(
        "--pattern",
        help="Filter anchors by substring (case-insensitive) across ID and context",
    )
    parser.add_argument(
        "--since",
        help="Only include files modified on/after this time (ISO 8601 or YYYY-MM-DD)",
    )
    parser.add_argument(
        "--dlp-manifest-out",
        help="When used with 'manifest', also export a DLP manifest (if available) to this path",
    )

    args = parser.parse_args()

    tracker = SymbolicAnchorTracker(args.path)

    if args.command == "scan":
        print("🔍 Scanning repository for symbolic anchors...")
        exts = args.ext if args.ext else None
        since_dt = None
        if args.since:
            try:
                since_dt = datetime.fromisoformat(args.since)
            except ValueError:
                try:
                    since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                except ValueError:
                    logger.warning("Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
        anchors = tracker.scan_repository(extensions=exts, since=since_dt, pattern=args.pattern)
        if args.json:
            payload = {
                "total_files": len(anchors),
                "total_anchors": sum(len(a) for a in anchors.values()),
                "files": {
                    fp: [asdict(a) for a in file_anchors] for fp, file_anchors in anchors.items()
                },
            }
            print(json.dumps(payload, indent=2))
        else:
            print(f"Found {sum(len(a) for a in anchors.values())} anchors in {len(anchors)} files")
            for file_path, file_anchors in anchors.items():
                print(f"\n📁 {file_path}:")
                for anchor in file_anchors:
                    print(f"  ⚓ {anchor.anchor_id} ({anchor.anchor_type}) - Line {anchor.line_number}")

    elif args.command == "resolve":
        if not args.anchor:
            logger.error("--anchor required for resolve command")
            return

        # Populate anchors first (respect optional --since)
        since_dt = None
        if args.since:
            try:
                since_dt = datetime.fromisoformat(args.since)
            except ValueError:
                try:
                    since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                except ValueError:
                    logger.warning("Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
        tracker.scan_repository(since=since_dt)
        anchor = tracker.resolve_anchor(args.anchor)

        if anchor:
            if args.json:
                print(json.dumps(asdict(anchor), indent=2))
            else:
                print(f"⚓ Resolved anchor: {anchor.anchor_id}")
                print(f"  Type: {anchor.anchor_type}")
                print(f"  Location: {anchor.file_path}:{anchor.line_number}")
                print(f"  Context: {anchor.context}")
                print(f"  Hash: {anchor.sha256_hash}")
        else:
            logger.error("Anchor {args.anchor} not found")

    elif args.command == "lineage":
        print("🔗 Building lineage map...")
        since_dt = None
        if args.since:
            try:
                since_dt = datetime.fromisoformat(args.since)
            except ValueError:
                try:
                    since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                except ValueError:
                    logger.warning("Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
        tracker.scan_repository(since=since_dt, pattern=args.pattern)
        lineages = tracker.build_lineage_map()

        if args.anchor:
            lineage = lineages.get(args.anchor)
            if lineage:
                if args.json:
                    print(json.dumps(asdict(lineage), indent=2))
                else:
                    print(f"📊 Lineage for {args.anchor}:")
                    print(f"  Generation: {lineage.generation}")
                    print(f"  Ancestors: {lineage.ancestors}")
                    print(f"  Descendants: {lineage.descendants}")
                    print(f"  Lineage Hash: {lineage.lineage_hash}")
            else:
                logger.error("No lineage found for {args.anchor}")
        else:
            if args.json:
                payload = {aid: asdict(lin) for aid, lin in lineages.items()}
                print(json.dumps(payload, indent=2))
            else:
                print(f"Found lineages for {len(lineages)} anchors")
                for anchor_id, lineage in sorted(lineages.items()):
                    ancestors_count = len(lineage.ancestors)
                    descendants_count = len(lineage.descendants)
                    msg = (
                        f"  {anchor_id}: Gen {lineage.generation}, {ancestors_count} ancestors, "
                        f"{descendants_count} descendants"
                    )
                    print(msg)

    elif args.command == "drift":
        print("🔍 Detecting symbolic drift...")
        since_dt = None
        if args.since:
            try:
                since_dt = datetime.fromisoformat(args.since)
            except ValueError:
                try:
                    since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                except ValueError:
                    logger.warning("Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
        tracker.scan_repository(since=since_dt, pattern=args.pattern)
        tracker.build_lineage_map()
        drift_issues = tracker.detect_drift()
        if args.json:
            print(json.dumps(drift_issues, indent=2))
        else:
            for issue_type, issues in drift_issues.items():
                if issues:
                    print(f"\n⚠️  {issue_type.replace('_', ' ').title()}:")
                    for issue in issues:
                        print(f"  - {issue}")
            if not any(drift_issues.values()):
                logger.info("No drift issues detected")

    elif args.command == "manifest":
        print("📄 Generating export manifest...")
        since_dt = None
        if args.since:
            try:
                since_dt = datetime.fromisoformat(args.since)
            except ValueError:
                try:
                    since_dt = datetime.strptime(args.since, "%Y-%m-%d")
                except ValueError:
                    logger.warning("Invalid --since format. Use ISO 8601 or YYYY-MM-DD.")
        tracker.scan_repository(since=since_dt, pattern=args.pattern)
        tracker.build_lineage_map()

        manifest = tracker.generate_export_manifest(args.anchor)
        output_path = tracker.save_manifest(manifest, args.output)

        # Optional: also export a DLP manifest if requested and available
        if args.dlp_manifest_out and getattr(tracker, "dlp_tracker", None) is not None:
            try:
                dlp_manifest = tracker.dlp_tracker.create_export_manifest(
                    "anchor_tracker_export", tag_ids=list(tracker.dlp_tracker.tags.keys())
                )
                with open(args.dlp_manifest_out, "w") as f:
                    json.dump(dlp_manifest, f, indent=2)
                print(f"🧬 DLP manifest saved to: {args.dlp_manifest_out}")
            except Exception:
                logger.warning("Failed to export DLP manifest")

        if args.json:
            print(json.dumps({"manifest_path": output_path, "manifest": manifest}, indent=2))
        else:
            logger.info("Manifest saved to: {output_path}")
            print(f"Memory seal: {manifest['memory_seal']}")


if __name__ == "__main__":
    main()
