#!/usr/bin/env python3
"""
Aurora CloudBank Symbolic Manifest Generator
============================================

Generates scan manifests with symbolic anchors, DLP tags, and memory sealing
for CodeQL security analysis workflows. Follows Aurora/GUMAS conventions.

Symbolic Anchor: T1-MANIFEST-GENERATOR
Ethics Protocol: Picard_Delta_3
"""

import logging

logger = logging.getLogger(__name__)

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class SymbolicManifestGenerator:
    """Generate security scan manifests with symbolic anchoring"""

    def __init__(self) -> None:
        self.repo_path = Path.cwd()
        self.anchor = "T1-MANIFEST-GENERATOR"
        self.ethics_protocol = "Picard_Delta_3"

    def compute_file_checksums(self, paths: List[str], ignored_patterns: List[str]) -> Dict[str, str]:
        """Compute SHA256 checksums for all files in specified paths"""

        checksums: Dict[str, str] = {}

        for path_str in paths:
            candidate = (self.repo_path / path_str).resolve()
            if not candidate.exists():
                continue

            if candidate.is_file():
                rel_path = self._relative_path(candidate)
                if not self._should_ignore_file(rel_path, ignored_patterns):
                    checksums[rel_path] = self._compute_file_hash(candidate)
                continue

            if candidate.is_dir():
                for file_path in candidate.rglob("*"):
                    if not file_path.is_file():
                        continue

                    rel_path = self._relative_path(file_path)
                    if not self._should_ignore_file(rel_path, ignored_patterns):
                        checksums[rel_path] = self._compute_file_hash(file_path)

        return checksums

    def _relative_path(self, file_path: Path) -> str:
        """Return repository-relative POSIX path"""

        try:
            rel = file_path.relative_to(self.repo_path)
        except ValueError:
            rel = file_path
        return rel.as_posix()

    def _should_ignore_file(self, relative_path: str, ignored_patterns: List[str]) -> bool:
        """Check if file should be ignored based on patterns"""

        import fnmatch

        for pattern in ignored_patterns:
            if fnmatch.fnmatch(relative_path, pattern) or fnmatch.fnmatch(Path(relative_path).name, pattern):
                return True
        return False

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA256 hash of a file"""

        try:
            sha256_hash = hashlib.sha256()
            with file_path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except (IOError, OSError):
            return "error_reading_file"

    @staticmethod
    def compute_tree_hash(checksums: Dict[str, str]) -> str:
        """Compute overall tree hash for memory sealing"""

        if not checksums:
            return "empty_tree"

        combined = "".join(f"{filename}:{checksum}\n" for filename, checksum in sorted(checksums.items()))
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    def get_codeql_config_paths(self) -> Tuple[List[str], List[str]]:
        """Extract paths from CodeQL config file"""

        config_path = self.repo_path / ".github" / "codeql" / "codeql-config.yml"

        default_paths = ["src", "modules", "scripts"]
        default_ignore = [
            "tests",
            "**/*_test.py",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__",
            "*.pyc",
            "CASK_Assets.zip",
            "**/*.zip",
            "**/*.gz",
            "**/*.tar",
        ]

        if not config_path.exists():
            return default_paths, default_ignore

        try:
            import yaml  # type: ignore

            with config_path.open("r", encoding="utf-8") as handle:
                config = yaml.safe_load(handle)

            paths = config.get("paths", default_paths) if isinstance(config, dict) else default_paths
            ignore_patterns = config.get("paths-ignore", default_ignore) if isinstance(config, dict) else default_ignore
            return list(paths), list(ignore_patterns)
        except ImportError:
            return default_paths, default_ignore
        except Exception:
            return default_paths, default_ignore

    def generate_manifest(
        self,
        *,
        language: str,
        anchor: str,
        team: str,
        ethics_protocol: str,
        dlp_tag: str,
        symbolic_tags: List[str],
        version: str = "1.1",
        output_file: Optional[str] = None,
    ) -> Dict[str, object]:
        """Generate symbolic manifest with Aurora conventions"""

        scan_paths, ignore_patterns = self.get_codeql_config_paths()
        checksums = self.compute_file_checksums(scan_paths, ignore_patterns)
        tree_hash = self.compute_tree_hash(checksums)
        git_info = self._get_git_info()

        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        manifest: Dict[str, object] = {
            "anchor": anchor,
            "symbolic_anchor": f"T1-SCAN-{language.upper()}",
            "export_time": now,
            "version": version,
            "team": team,
            "ethics_protocol": ethics_protocol,
            "dlp_tags": [dlp_tag],
            "dlp_level": "DLP_L1_OK",
            "symbolic_hash_validation": True,
            "context_tag": f"codeql_scan_{language}",
            "symbolic_tags": symbolic_tags,
            "anchor_protocols": ["T1", "SRB_TICK", "ANCHOR_LOCKED"],
            "t1_srb_anchors": [f"T1_TEMPORAL_ANCHOR_{language.upper()}"],
            "language": language,
            "scan_type": "security_analysis",
            "tool": "github_codeql",
            **git_info,
            "included_paths": scan_paths,
            "ignored_patterns": ignore_patterns,
            "file_count": len(checksums),
            "file_checksums": checksums,
            "memory_seal": {
                "tree_hash": tree_hash,
                "seal_algorithm": "SHA256",
                "sealed_at": now,
            },
            "audit_trail": {
                "generator": "symbolic_manifest.py",
                "generator_anchor": self.anchor,
                "generation_timestamp": now,
            },
        }

        output_path = self.repo_path / (output_file or f"scan_manifest_{language}.json")
        with output_path.open("w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, sort_keys=True)

        logger.info("Generated symbolic manifest: {output_path.name}")
        print(f"   Anchor: {anchor}")
        print(f"   Language: {language}")
        print(f"   Files scanned: {len(checksums)}")
        print(f"   Tree hash: {tree_hash[:16]}...")

        return manifest

    def _get_git_info(self) -> Dict[str, str]:
        """Get Git context information"""

        git_info: Dict[str, str] = {}

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                git_info["commit_sha"] = result.stdout.strip()

            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                git_info["branch"] = result.stdout.strip()

            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=False,
                cwd=self.repo_path,
            )
            if result.returncode == 0:
                git_info["repository_url"] = result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return git_info


def print_aurora_help() -> None:
    """Print Aurora/GUMAS specific help"""

    help_text = """
Aurora CloudBank Symbolic Manifest Generator
==========================================

Examples:
  python3 scripts/symbolic_manifest.py \
    --language python \
    --anchor "T1-SCAN-PYTHON" \
    --team "Aurora Dev" \
    --ethics-protocol "Picard_Delta_3" \
    --dlp-tag "SECURITY_SCAN" \
    --symbolic-tags SRB-CodeQL SECURITY_SCAN

  python3 scripts/symbolic_manifest.py \
    --language javascript \
    --anchor "T1-SCAN-JAVASCRIPT" \
    --team "Aurora Dev" \
    --ethics-protocol "Picard_Delta_3" \
    --dlp-tag "SECURITY_SCAN" \
    --symbolic-tags SRB-CodeQL SECURITY_SCAN

Symbolic Conventions:
  - Anchors: Use T1-SCAN-<LANGUAGE> format
  - DLP Tags: SECURITY_SCAN, DLP_L1_OK, DLP_L2_LOCKED
  - Ethics: Always use Picard_Delta_3 for security scans
  - Context Tags: Required for continuity support
  - Memory Sealing: SHA256 tree hashes for integrity

Output includes:
  - File checksums for integrity verification
  - Memory sealing with SHA256 tree hash
  - Symbolic anchor protocols (T1, SRB_TICK, ANCHOR_LOCKED)
  - DLP classification and context tags
  - Git metadata and audit trails
"""
    print(help_text)


def main() -> None:
    """CLI entry point"""

    if "--help-aurora" in sys.argv:
        print_aurora_help()
        return

    parser = argparse.ArgumentParser(description="Generate Aurora CloudBank symbolic manifests")
    parser.add_argument("--language", required=True, help="Language being scanned (e.g., python, javascript)")
    parser.add_argument("--anchor", required=True, help="Symbolic anchor (e.g., T1-SCAN-PYTHON)")
    parser.add_argument("--team", default="Aurora Dev", help="Team name")
    parser.add_argument("--ethics-protocol", default="Picard_Delta_3", help="Ethics protocol identifier")
    parser.add_argument("--dlp-tag", required=True, help="DLP classification tag")
    parser.add_argument("--symbolic-tags", nargs="+", required=True, help="Symbolic tags for the scan")
    parser.add_argument("--version", default="1.1", help="Manifest version")
    parser.add_argument("--output", help="Output filename (default: scan_manifest_<language>.json)")

    args = parser.parse_args()

    generator = SymbolicManifestGenerator()

    try:
        generator.generate_manifest(
            language=args.language,
            anchor=args.anchor,
            team=args.team,
            ethics_protocol=args.ethics_protocol,
            dlp_tag=args.dlp_tag,
            symbolic_tags=args.symbolic_tags,
            version=args.version,
            output_file=args.output,
        )

        print("\n🔒 Memory seal generated successfully")
        print(f"   Ethics protocol: {args.ethics_protocol}")
        print(f"   DLP classification: {args.dlp_tag}")
    except Exception as exc:
        logger.error("Error generating manifest: {exc}", file=sys.stderr)
        sys.exit(1)




if __name__ == "__main__":
    main()
