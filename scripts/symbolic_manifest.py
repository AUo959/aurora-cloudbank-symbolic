#!/usr/bin/env python3
"""
Aurora CloudBank Symbolic Manifest Generator
============================================

Generates scan manifests with symbolic anchors, DLP tags, and memory sealing
for CodeQL security analysis workflows. Follows Aurora/GUMAS conventions.

Symbolic Anchor: T1-MANIFEST-GENERATOR
Ethics Protocol: Picard_Delta_3
"""

import os
import sys
import argparse
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


class SymbolicManifestGenerator:
    """Generate security scan manifests with symbolic anchoring"""
    
    def __init__(self):
        self.repo_path = Path.cwd()
        self.anchor = "T1-MANIFEST-GENERATOR"
        self.ethics_protocol = "Picard_Delta_3"
        
    def compute_file_checksums(self, paths: List[str], ignored_patterns: List[str]) -> Dict[str, str]:
        """Compute SHA256 checksums for all files in specified paths"""
        checksums = {}
        
        for path_str in paths:
            path = self.repo_path / path_str
            if not path.exists():
                continue
                
            if path.is_file():
                # Single file
                if not self._should_ignore_file(str(path), ignored_patterns):
                    checksums[str(path)] = self._compute_file_hash(path)
            elif path.is_dir():
                # Directory - walk recursively
                for file_path in path.rglob('*'):
                    if file_path.is_file() and not self._should_ignore_file(str(file_path), ignored_patterns):
                        relative_path = file_path.relative_to(self.repo_path)
                        checksums[str(relative_path)] = self._compute_file_hash(file_path)
                        
        return checksums
    
    def _should_ignore_file(self, file_path: str, ignored_patterns: List[str]) -> bool:
        """Check if file should be ignored based on patterns"""
        import fnmatch
        
        for pattern in ignored_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False
    
    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file"""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, OSError):
            return "error_reading_file"
    
    def compute_tree_hash(self, checksums: Dict[str, str]) -> str:
        """Compute overall tree hash for memory sealing"""
        if not checksums:
            return "empty_tree"
            
        # Sort by filename for deterministic hash
        sorted_items = sorted(checksums.items())
        combined_data = ""
        for filename, checksum in sorted_items:
            combined_data += f"{filename}:{checksum}\n"
            
        return hashlib.sha256(combined_data.encode('utf-8')).hexdigest()
    
    def get_codeql_config_paths(self) -> tuple[List[str], List[str]]:
        """Extract paths from CodeQL config file"""
        config_path = self.repo_path / ".github" / "codeql" / "codeql-config.yml"
        
        # Default paths if config doesn't exist
        default_paths = ["src", "modules", "scripts"]
        default_ignore = [
            "tests", "**/*_test.py", "node_modules", "venv", ".venv", 
            "__pycache__", "*.pyc", "CASK_Assets.zip", "**/*.zip", 
            "**/*.gz", "**/*.tar"
        ]
        
        if not config_path.exists():
            return default_paths, default_ignore
            
        try:
            import yaml
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            paths = config.get('paths', default_paths)
            ignore_patterns = config.get('paths-ignore', default_ignore)
            
            return paths, ignore_patterns
        except ImportError:
            # Fallback if PyYAML not available
            return default_paths, default_ignore
        except Exception:
            return default_paths, default_ignore
    
    def generate_manifest(self, 
                         language: str,
                         anchor: str,
                         team: str,
                         ethics_protocol: str,
                         dlp_tag: str,
                         symbolic_tags: List[str],
                         version: str = "1.1",
                         output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate symbolic manifest with Aurora conventions"""
        
        # Get paths from CodeQL config
        scan_paths, ignore_patterns = self.get_codeql_config_paths()
        
        # Compute file checksums
        checksums = self.compute_file_checksums(scan_paths, ignore_patterns)
        
        # Generate tree hash for memory sealing
        tree_hash = self.compute_tree_hash(checksums)
        
        # Get Git info if available
        git_info = self._get_git_info()
        
        # Build manifest following Aurora/GUMAS conventions
        manifest = {
            # Core symbolic anchoring
            "anchor": anchor,
            "symbolic_anchor": f"T1-SCAN-{language.upper()}",
            "export_time": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "version": version,
            
            # Team and governance
            "team": team,
            "ethics_protocol": ethics_protocol,
            
            # DLP and security classification
            "dlp_tags": [dlp_tag],
            "dlp_level": "DLP_L1_OK",
            "symbolic_hash_validation": True,
            "context_tag": f"codeql_scan_{language}",  # REQUIRED for continuity
            
            # Symbolic tags and protocols
            "symbolic_tags": symbolic_tags,
            "anchor_protocols": ["T1", "SRB_TICK", "ANCHOR_LOCKED"],
            "t1_srb_anchors": [f"T1_TEMPORAL_ANCHOR_{language.upper()}"],
            
            # Scan metadata
            "language": language,
            "scan_type": "security_analysis",
            "tool": "github_codeql",
            
            # Git context
            **git_info,
            
            # File integrity data
            "included_paths": scan_paths,
            "ignored_patterns": ignore_patterns,
            "file_count": len(checksums),
            "file_checksums": checksums,
            
            # Memory sealing
            "memory_seal": {
                "tree_hash": tree_hash,
                "seal_algorithm": "SHA256",
                "sealed_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            },
            
            # Audit trail
            "audit_trail": {
                "generator": "symbolic_manifest.py",
                "generator_anchor": self.anchor,
                "generation_timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }
        }
        
        # Output to file
        if not output_file:
            output_file = f"scan_manifest_{language}.json"
            
        output_path = self.repo_path / output_file
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            
        print(f"✅ Generated symbolic manifest: {output_file}")
        print(f"   Anchor: {anchor}")
        print(f"   Language: {language}")
        print(f"   Files scanned: {len(checksums)}")
        print(f"   Tree hash: {tree_hash[:16]}...")
        
        return manifest
    
    def _get_git_info(self) -> Dict[str, Any]:
        """Get Git context information"""
        git_info = {}
        
        try:
            import subprocess
            
            # Get commit SHA
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                git_info['commit_sha'] = result.stdout.strip()
            
            # Get branch name
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()
                
            # Get repository URL
            result = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], 
                                  capture_output=True, text=True, cwd=self.repo_path)
            if result.returncode == 0:
                git_info['repository_url'] = result.stdout.strip()
                
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        return git_info


def main():
    """CLI entry point"""
    # Handle Aurora help before setting up other required args
    if '--help-aurora' in sys.argv:
        print_aurora_help()
        return
        
    parser = argparse.ArgumentParser(description='Generate Aurora CloudBank symbolic manifests')
    
    parser.add_argument('--language', required=True, 
                       help='Language being scanned (e.g., python, javascript)')
    parser.add_argument('--anchor', required=True,
                       help='Symbolic anchor (e.g., T1-SCAN-PYTHON)')
    parser.add_argument('--team', default='Aurora Dev',
                       help='Team name')
    parser.add_argument('--ethics-protocol', default='Picard_Delta_3',
                       help='Ethics protocol identifier')
    parser.add_argument('--dlp-tag', required=True,
                       help='DLP classification tag')
    parser.add_argument('--symbolic-tags', nargs='+', required=True,
                       help='Symbolic tags for the scan')
    parser.add_argument('--version', default='1.1',
                       help='Manifest version')
    parser.add_argument('--output', 
                       help='Output filename (default: scan_manifest_<language>.json)')
    
    args = parser.parse_args()
    
    generator = SymbolicManifestGenerator()
    
    try:
        manifest = generator.generate_manifest(
            language=args.language,
            anchor=args.anchor,
            team=args.team,
            ethics_protocol=args.ethics_protocol,
            dlp_tag=args.dlp_tag,
            symbolic_tags=args.symbolic_tags,
            version=args.version,
            output_file=args.output
        )
        
        print("\n🔒 Memory seal generated successfully")
        print(f"   Ethics protocol: {args.ethics_protocol}")
        print(f"   DLP classification: {args.dlp_tag}")
        
    except Exception as e:
        print(f"❌ Error generating manifest: {e}", file=sys.stderr)
        sys.exit(1)


def print_aurora_help():
    """Print Aurora/GUMAS specific help"""
    help_text = """
Aurora CloudBank Symbolic Manifest Generator
==========================================

Examples:
  
  # Python security scan
  python3 scripts/symbolic_manifest.py \\
    --language python \\
    --anchor "T1-SCAN-PYTHON" \\
    --team "Aurora Dev" \\
    --ethics-protocol "Picard_Delta_3" \\
    --dlp-tag "SECURITY_SCAN" \\
    --symbolic-tags SRB-CodeQL SECURITY_SCAN

  # JavaScript security scan  
  python3 scripts/symbolic_manifest.py \\
    --language javascript \\
    --anchor "T1-SCAN-JAVASCRIPT" \\
    --team "Aurora Dev" \\
    --ethics-protocol "Picard_Delta_3" \\
    --dlp-tag "SECURITY_SCAN" \\
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


if __name__ == "__main__":
    main()