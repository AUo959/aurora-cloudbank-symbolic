#!/usr/bin/env python3
"""
GITWiz Repository Organizer
Advanced repository structure analysis and optimization engine

Analyzes repository content, identifies optimization opportunities,
and provides intelligent reorganization recommendations.
"""

import hashlib
import json
import logging
import os
import re
import shutil
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RepositoryOrganizer:
    """Intelligent repository organization and optimization engine."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.analysis_cache = {}
        self.duplicate_files = {}
        self.file_categories = defaultdict(list)
        self.optimization_recommendations = []

    def analyze_repository_structure(self) -> Dict[str, Any]:
        """Comprehensive repository structure analysis."""
        logger.info("Starting comprehensive repository analysis...")

        analysis = {
            "total_files": 0,
            "total_size": 0,
            "file_types": defaultdict(int),
            "directories": defaultdict(int),
            "zip_archives": [],
            "documentation_files": [],
            "duplicate_files": [],
            "large_files": [],
            "security_issues": [],
            "organization_score": 0.0,
            "recommendations": []
        }

        # Analyze all files
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                self._analyze_single_file(file_path, analysis)

        # Generate optimization recommendations
        self._generate_recommendations(analysis)

        # Calculate organization score
        analysis["organization_score"] = self._calculate_organization_score(analysis)

        return analysis

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored in analysis."""
        ignore_patterns = ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv']
        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def _analyze_single_file(self, file_path: Path, analysis: Dict[str, Any]):
        """Analyze a single file and update analysis."""
        try:
            stat = file_path.stat()
            size = stat.st_size

            analysis["total_files"] += 1
            analysis["total_size"] += size

            # File type analysis
            suffix = file_path.suffix.lower()
            analysis["file_types"][suffix] += 1

            # Directory analysis
            parent_name = file_path.parent.name
            analysis["directories"][parent_name] += 1

            # Large files (>5MB)
            if size > 5 * 1024 * 1024:
                analysis["large_files"].append({
                    "path": str(file_path.relative_to(self.project_root)),
                    "size": size,
                    "size_mb": round(size / (1024 * 1024), 2)
                })

            # ZIP archives
            if suffix == '.zip':
                zip_info = self._analyze_zip_file(file_path)
                analysis["zip_archives"].append(zip_info)

            # Documentation files
            if self._is_documentation_file(file_path):
                analysis["documentation_files"].append({
                    "path": str(file_path.relative_to(self.project_root)),
                    "type": self._classify_documentation(file_path),
                    "size": size
                })

            # Duplicate detection
            self._check_for_duplicates(file_path, analysis)

            # Security analysis
            if suffix in ['.py', '.js', '.yml', '.yaml', '.json']:
                security_issues = self._scan_file_security(file_path)
                if security_issues:
                    analysis["security_issues"].extend(security_issues)

        except (OSError, ValueError, RuntimeError) as e:
            logger.warning(f"Error analyzing file {file_path}: {e}")

    def _analyze_zip_file(self, zip_path: Path) -> Dict[str, Any]:
        """Analyze ZIP file contents."""
        info = {
            "path": str(zip_path.relative_to(self.project_root)),
            "size": zip_path.stat().st_size,
            "file_count": 0,
            "nested_archives": [],
            "file_types": defaultdict(int),
            "total_uncompressed": 0,
            "compression_ratio": 0.0,
            "duplicate_candidates": []
        }

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                for zip_info in zf.infolist():
                    if not zip_info.is_dir():
                        info["file_count"] += 1
                        info["total_uncompressed"] += zip_info.file_size

                        # File type analysis
                        suffix = Path(zip_info.filename).suffix.lower()
                        info["file_types"][suffix] += 1

                        # Nested archives
                        if suffix in ['.zip', '.tar', '.gz', '.7z']:
                            info["nested_archives"].append(zip_info.filename)

                # Calculate compression ratio
                if info["total_uncompressed"] > 0:
                    info["compression_ratio"] = round(
                        (1 - info["size"] / info["total_uncompressed"]) * 100, 2
                    )

        except (OSError, ValueError, RuntimeError) as e:
            logger.warning(f"Error analyzing ZIP {zip_path}: {e}")
            info["error"] = str(e)

        return info

    def _is_documentation_file(self, file_path: Path) -> bool:
        """Check if file is documentation."""
        doc_patterns = [
            r'README', r'CHANGELOG', r'LICENSE', r'CONTRIBUTING',
            r'DEPLOYMENT', r'INTEGRATION', r'MISSION', r'STATUS',
            r'COMPLETE', r'GUIDE', r'INSTRUCTIONS'
        ]

        name_upper = file_path.name.upper()
        return any(re.search(pattern, name_upper) for pattern in doc_patterns)

    def _classify_documentation(self, file_path: Path) -> str:
        """Classify documentation type."""
        name_upper = file_path.name.upper()

        if 'README' in name_upper:
            return 'readme'
        elif 'CHANGELOG' in name_upper:
            return 'changelog'
        elif 'DEPLOYMENT' in name_upper or 'DEPLOY' in name_upper:
            return 'deployment'
        elif 'INTEGRATION' in name_upper:
            return 'integration'
        elif 'STATUS' in name_upper or 'COMPLETE' in name_upper:
            return 'status'
        elif 'GUIDE' in name_upper or 'INSTRUCTIONS' in name_upper:
            return 'guide'
        else:
            return 'other'

    def _check_for_duplicates(self, file_path: Path, analysis: Dict[str, Any]):
        """Check for duplicate files based on content hash."""
        try:
            with open(file_path, 'rb') as f:
                content_hash = hashlib.md5(f.read()).hexdigest()

            if content_hash in self.duplicate_files:
                # Found duplicate
                original = self.duplicate_files[content_hash]
                duplicate_info = {
                    "original": str(original.relative_to(self.project_root)),
                    "duplicate": str(file_path.relative_to(self.project_root)),
                    "size": file_path.stat().st_size,
                    "hash": content_hash
                }
                analysis["duplicate_files"].append(duplicate_info)
            else:
                self.duplicate_files[content_hash] = file_path

        except (OSError, ValueError, RuntimeError) as e:
            logger.debug(f"Error checking duplicates for {file_path}: {e}")

    def _scan_file_security(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan file for potential security issues."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Security patterns to check
            security_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', 'hardcoded_password'),
                (r'api_key\s*=\s*["\'][^"\']+["\']', 'hardcoded_api_key'),
                (r'secret\s*=\s*["\'][^"\']+["\']', 'hardcoded_secret'),
                (r'token\s*=\s*["\'][^"\']+["\']', 'hardcoded_token'),
                (r'eval\s*\(', 'eval_usage'),
                (r'exec\s*\(', 'exec_usage'),
            ]

            for pattern, issue_type in security_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    issues.append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "type": issue_type,
                        "line": content[:match.start()].count('\n') + 1,
                        "severity": "high" if issue_type.startswith('hardcoded') else "medium"
                    })

        except (OSError, ValueError, RuntimeError) as e:
            logger.debug(f"Error scanning security for {file_path}: {e}")

        return issues

    def _generate_recommendations(self, analysis: Dict[str, Any]):
        """Generate optimization recommendations."""
        recommendations = []

        # ZIP file optimization
        if len(analysis["zip_archives"]) > 10:
            recommendations.append({
                "type": "archive_consolidation",
                "priority": "high",
                "description": f"Consider consolidating {len(analysis['zip_archives'])} ZIP files",
                "action": "Review and merge related archives",
                "impact": "Reduce file count and improve organization"
            })

        # Documentation organization
        doc_files = analysis["documentation_files"]
        if len(doc_files) > 15:
            recommendations.append({
                "type": "documentation_organization",
                "priority": "medium",
                "description": f"Many documentation files ({len(doc_files)}) could be organized",
                "action": "Create docs/ directory and categorize files",
                "impact": "Improve repository navigation"
            })

        # Duplicate file cleanup
        if analysis["duplicate_files"]:
            total_duplicate_size = sum(d["size"] for d in analysis["duplicate_files"])
            recommendations.append({
                "type": "duplicate_cleanup",
                "priority": "medium",
                "description": f"Remove {len(analysis['duplicate_files'])} duplicate files",
                "action": "Delete duplicate files",
                "impact": f"Save {total_duplicate_size / (1024*1024):.1f}MB of space"
            })

        # Large file optimization
        if analysis["large_files"]:
            recommendations.append({
                "type": "large_file_optimization",
                "priority": "low",
                "description": f"Review {len(analysis['large_files'])} large files",
                "action": "Consider Git LFS or external storage",
                "impact": "Improve repository performance"
            })

        # Security issues
        if analysis["security_issues"]:
            high_severity = [s for s in analysis["security_issues"] if s["severity"] == "high"]
            if high_severity:
                recommendations.append({
                    "type": "security_fixes",
                    "priority": "critical",
                    "description": f"Fix {len(high_severity)} high-severity security issues",
                    "action": "Remove hardcoded credentials and sensitive data",
                    "impact": "Critical security improvement"
                })

        analysis["recommendations"] = recommendations

    def _calculate_organization_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate repository organization score (0-100)."""
        score = 100.0

        # Penalize for too many files in root
        root_files = sum(1 for f in self.project_root.iterdir() if f.is_file())
        if root_files > 20:
            score -= min(30, (root_files - 20) * 2)

        # Penalize for too many ZIP files
        if len(analysis["zip_archives"]) > 5:
            score -= min(20, (len(analysis["zip_archives"]) - 5) * 2)

        # Penalize for duplicates
        score -= min(15, len(analysis["duplicate_files"]) * 2)

        # Penalize for security issues
        high_security = [s for s in analysis["security_issues"] if s["severity"] == "high"]
        score -= len(high_security) * 5

        # Bonus for good structure
        if (self.project_root / "docs").exists():
            score += 5
        if (self.project_root / "scripts").exists():
            score += 5
        if (self.project_root / ".gitignore").exists():
            score += 5

        return max(0.0, min(100.0, score))

    def generate_reorganization_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed reorganization plan."""
        plan = {
            "overview": {
                "current_score": analysis["organization_score"],
                "target_score": min(100.0, analysis["organization_score"] + 25),
                "estimated_improvement": min(25.0, 100.0 - analysis["organization_score"])
            },
            "phases": []
        }

        # Phase 1: Critical fixes
        if any(r["priority"] == "critical" for r in analysis["recommendations"]):
            plan["phases"].append({
                "phase": 1,
                "name": "Critical Security Fixes",
                "priority": "critical",
                "actions": [r for r in analysis["recommendations"] if r["priority"] == "critical"],
                "estimated_time": "1-2 hours"
            })

        # Phase 2: Archive consolidation
        zip_recommendations = [r for r in analysis["recommendations"] if r["type"] == "archive_consolidation"]
        if zip_recommendations:
            plan["phases"].append({
                "phase": 2,
                "name": "Archive Organization",
                "priority": "high",
                "actions": zip_recommendations,
                "estimated_time": "2-4 hours",
                "details": {
                    "zip_files_to_review": len(analysis["zip_archives"]),
                    "consolidation_strategy": "Group by content type and purpose"
                }
            })

        # Phase 3: Documentation organization
        doc_recommendations = [r for r in analysis["recommendations"] if r["type"] == "documentation_organization"]
        if doc_recommendations:
            plan["phases"].append({
                "phase": 3,
                "name": "Documentation Restructure",
                "priority": "medium",
                "actions": doc_recommendations,
                "estimated_time": "1-3 hours",
                "details": {
                    "doc_files_count": len(analysis["documentation_files"]),
                    "suggested_structure": {
                        "docs/": "Main documentation",
                        "docs/deployment/": "Deployment guides",
                        "docs/status/": "Status and completion reports",
                        "docs/integration/": "Integration documentation"
                    }
                }
            })

        # Phase 4: Cleanup
        cleanup_recommendations = [r for r in analysis["recommendations"]
                                   if r["type"] in ["duplicate_cleanup", "large_file_optimization"]]
        if cleanup_recommendations:
            plan["phases"].append({
                "phase": 4,
                "name": "Repository Cleanup",
                "priority": "low",
                "actions": cleanup_recommendations,
                "estimated_time": "1-2 hours"
            })

        return plan


def main():
    """Main function for repository organization analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="GITWiz Repository Organizer")
    parser.add_argument("--analyze", action="store_true", help="Analyze repository structure")
    parser.add_argument("--plan", action="store_true", help="Generate reorganization plan")
    parser.add_argument("--output", help="Output file for results (JSON)")

    args = parser.parse_args()

    organizer = RepositoryOrganizer(Path.cwd())

    if args.analyze or args.plan:
        print("🔍 Analyzing repository structure...")
        analysis = organizer.analyze_repository_structure()

        if args.plan:
            print("📋 Generating reorganization plan...")
            plan = organizer.generate_reorganization_plan(analysis)
            result = {"analysis": analysis, "reorganization_plan": plan}
        else:
            result = analysis

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"✅ Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2, default=str))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
