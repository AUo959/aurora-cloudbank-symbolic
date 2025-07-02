#!/usr/bin/env python3
"""
ZIPWiz - Advanced Archive Management Integration
Part of the GITWiz Enhanced ecosystem

Provides intelligent ZIP file analysis, optimization, and reorganization
capabilities with deep integration into repository stewardship workflows.

Author: Aurora/ORION Core
Built for consistency, clarity, and care.
"""

import hashlib
import json
import logging
import os
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ArchiveAnalysis:
    """Comprehensive analysis of an archive file."""
    path: str
    file_count: int
    total_size: int
    compressed_size: int
    compression_ratio: float
    file_types: Dict[str, int]
    nested_archives: List[str]
    duplicate_files: List[tuple]
    large_files: List[tuple]
    structure_depth: int
    potential_issues: List[str]
    recommendations: List[str]


class ZIPWiz:
    """Advanced ZIP archive management and optimization."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.temp_dir = Path(tempfile.mkdtemp(prefix="zipwiz_"))
        self.analysis_cache: Dict[str, ArchiveAnalysis] = {}

        # File type categories for intelligent organization
        self.file_categories = {
            'documentation': {'.md', '.txt', '.pd', '.doc', '.docx', '.rst'},
            'code': {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go', '.rs'},
            'config': {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'},
            'data': {'.csv', '.json', '.xml', '.sql', '.db', '.sqlite'},
            'images': {'.png', '.jpg', '.jpeg', '.gi', '.bmp', '.svg', '.ico'},
            'archives': {'.zip', '.tar', '.gz', '.7z', '.rar', '.bz2'},
            'web': {'.html', '.css', '.scss', '.less'},
            'scripts': {'.sh', '.bat', '.ps1', '.cmd'}
        }

    def analyze_archive(self, archive_path: Path) -> ArchiveAnalysis:
        """Perform comprehensive analysis of a ZIP archive."""
        logger.info(f"Analyzing archive: {archive_path}")

        # Check cache first
        cache_key = f"{archive_path}_{archive_path.stat().st_mtime}"
        if cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]

        analysis = ArchiveAnalysis(
            path=str(archive_path),
            file_count=0,
            total_size=0,
            compressed_size=archive_path.stat().st_size,
            compression_ratio=0.0,
            file_types={},
            nested_archives=[],
            duplicate_files=[],
            large_files=[],
            structure_depth=0,
            potential_issues=[],
            recommendations=[]
        )

        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                file_hashes: Dict[str, List[str]] = {}
                max_depth = 0

                for info in zf.infolist():
                    if info.is_dir():
                        continue

                    analysis.file_count += 1
                    analysis.total_size += info.file_size

                    # Track file types
                    ext = Path(info.filename).suffix.lower()
                    analysis.file_types[ext] = analysis.file_types.get(ext, 0) + 1

                    # Check for nested archives
                    if ext in self.file_categories['archives']:
                        analysis.nested_archives.append(info.filename)

                    # Track large files (>10MB)
                    if info.file_size > 10 * 1024 * 1024:
                        analysis.large_files.append((info.filename, info.file_size))

                    # Calculate structure depth
                    depth = len(Path(info.filename).parts)
                    max_depth = max(max_depth, depth)

                    # Check for duplicates by content hash
                    try:
                        content = zf.read(info.filename)
                        content_hash = hashlib.md5(content).hexdigest()
                        if content_hash not in file_hashes:
                            file_hashes[content_hash] = []
                        file_hashes[content_hash].append(info.filename)
                    except (OSError, ValueError, RuntimeError) as e:
                        logger.warning(f"Could not read {info.filename}: {e}")

                analysis.structure_depth = max_depth

                # Find duplicates
                for content_hash, files in file_hashes.items():
                    if len(files) > 1:
                        analysis.duplicate_files.append(tuple(files))

                # Calculate compression ratio
                if analysis.total_size > 0:
                    analysis.compression_ratio = analysis.compressed_size / analysis.total_size

                # Generate issues and recommendations
                analysis.potential_issues = self._identify_issues(analysis)
                analysis.recommendations = self._generate_recommendations(analysis)

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error analyzing {archive_path}: {e}")
            analysis.potential_issues.append(f"Analysis error: {e}")

        # Cache the analysis
        self.analysis_cache[cache_key] = analysis
        return analysis

    def _identify_issues(self, analysis: ArchiveAnalysis) -> List[str]:
        """Identify potential issues with the archive."""
        issues = []

        if analysis.compression_ratio > 0.9:
            issues.append("Poor compression ratio - files may already be compressed")

        if analysis.structure_depth > 8:
            issues.append("Very deep directory structure - may be difficult to navigate")

        if len(analysis.duplicate_files) > 0:
            issues.append(f"Found {len(analysis.duplicate_files)} sets of duplicate files")

        if len(analysis.large_files) > 0:
            issues.append(f"Contains {len(analysis.large_files)} large files (>10MB)")

        if len(analysis.nested_archives) > 0:
            issues.append(f"Contains {len(analysis.nested_archives)} nested archives")

        # Check for potentially obsolete files
        obsolete_patterns = [
            '.tmp', '.temp', '.cache', '.log', '.bak', '.old', '~'
        ]
        for ext in analysis.file_types:
            if any(pattern in ext for pattern in obsolete_patterns):
                issues.append(f"Contains potentially obsolete files: {ext}")

        return issues

    def _generate_recommendations(self, analysis: ArchiveAnalysis) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        if len(analysis.duplicate_files) > 0:
            recommendations.append("Remove duplicate files to reduce archive size")

        if analysis.structure_depth > 6:
            recommendations.append("Consider flattening directory structure")

        if len(analysis.nested_archives) > 0:
            recommendations.append("Extract and organize nested archives")

        if analysis.file_count > 1000:
            recommendations.append("Consider splitting into smaller, topic-specific archives")

        # Suggest organization by file type
        type_count = len(analysis.file_types)
        if type_count > 10:
            recommendations.append("Organize files by type into subdirectories")

        return recommendations

    def extract_with_optimization(self, archive_path: Path, target_dir: Path) -> Dict[str, Any]:
        """Extract archive with intelligent optimization and organization."""
        logger.info(f"Extracting and optimizing: {archive_path}")

        analysis = self.analyze_archive(archive_path)
        extract_dir = self.temp_dir / f"extract_{archive_path.stem}"
        extract_dir.mkdir(exist_ok=True)

        optimization_log = {
            "extracted_files": 0,
            "duplicates_removed": 0,
            "files_reorganized": 0,
            "space_saved": 0,
            "nested_archives_processed": 0
        }

        try:
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # Extract all files first
                zf.extractall(extract_dir)
                optimization_log["extracted_files"] = analysis.file_count

                # Remove duplicates
                for duplicate_set in analysis.duplicate_files:
                    # Keep the first file, remove others
                    for duplicate_file in duplicate_set[1:]:
                        duplicate_path = extract_dir / duplicate_file
                        if duplicate_path.exists():
                            size = duplicate_path.stat().st_size
                            duplicate_path.unlink()
                            optimization_log["duplicates_removed"] += 1
                            optimization_log["space_saved"] += size

                # Process nested archives
                for nested_archive in analysis.nested_archives:
                    nested_path = extract_dir / nested_archive
                    if nested_path.exists():
                        nested_extract_dir = nested_path.parent / f"{nested_path.stem}_extracted"
                        try:
                            if nested_path.suffix.lower() == '.zip':
                                with zipfile.ZipFile(nested_path, 'r') as nested_zf:
                                    nested_zf.extractall(nested_extract_dir)
                                nested_path.unlink()  # Remove original nested archive
                                optimization_log["nested_archives_processed"] += 1
                        except (OSError, ValueError, RuntimeError) as e:
                            logger.warning(f"Could not extract nested archive {nested_archive}: {e}")

                # Intelligent reorganization
                self._reorganize_by_type(extract_dir, optimization_log)

                # Move optimized structure to target
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.move(str(extract_dir), str(target_dir))

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error extracting {archive_path}: {e}")
            optimization_log["error"] = str(e)

        return optimization_log

    def _reorganize_by_type(self, directory: Path, optimization_log: Dict[str, Any]):
        """Reorganize files by type within the directory."""
        type_dirs = {}

        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            category = self._get_file_category(ext)

            if category != 'other':  # Only reorganize known file types
                category_dir = directory / category
                category_dir.mkdir(exist_ok=True)

                new_path = category_dir / file_path.name
                counter = 1
                while new_path.exists():
                    stem = file_path.stem
                    new_path = category_dir / f"{stem}_{counter}{file_path.suffix}"
                    counter += 1

                try:
                    file_path.rename(new_path)
                    optimization_log["files_reorganized"] += 1
                except (OSError, ValueError, RuntimeError) as e:
                    logger.warning(f"Could not move {file_path}: {e}")

    def _get_file_category(self, extension: str) -> str:
        """Determine the category of a file based on its extension."""
        for category, extensions in self.file_categories.items():
            if extension in extensions:
                return category
        return 'other'

    def create_optimized_archive(self, source_dir: Path, output_path: Path,
                                 compression_level: int = 6) -> Dict[str, Any]:
        """Create an optimized ZIP archive from a directory."""
        logger.info(f"Creating optimized archive: {output_path}")

        stats = {
            "files_added": 0,
            "total_size": 0,
            "compressed_size": 0,
            "compression_ratio": 0.0,
            "skipped_files": []
        }

        # Files to skip in archives
        skip_patterns = {
            '.DS_Store', 'Thumbs.db', '.git', '__pycache__',
            '*.tmp', '*.temp', '*.log', '*.cache'
        }

        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED,
                                 compresslevel=compression_level) as zf:

                for file_path in source_dir.rglob("*"):
                    if not file_path.is_file():
                        continue

                    # Check if file should be skipped
                    if any(pattern.replace('*', '') in file_path.name for pattern in skip_patterns):
                        stats["skipped_files"].append(str(file_path.relative_to(source_dir)))
                        continue

                    relative_path = file_path.relative_to(source_dir)
                    zf.write(file_path, relative_path)

                    stats["files_added"] += 1
                    stats["total_size"] += file_path.stat().st_size

            stats["compressed_size"] = output_path.stat().st_size
            if stats["total_size"] > 0:
                stats["compression_ratio"] = stats["compressed_size"] / stats["total_size"]

        except (OSError, ValueError, RuntimeError) as e:
            logger.error(f"Error creating archive: {e}")
            stats["error"] = str(e)

        return stats

    def audit_repository_archives(self) -> Dict[str, Any]:
        """Audit all ZIP files in the repository and provide recommendations."""
        logger.info("Auditing repository archives...")

        audit_report = {
            "total_archives": 0,
            "total_size": 0,
            "analyses": [],
            "overall_recommendations": [],
            "potential_savings": 0
        }

        zip_files = list(self.project_root.rglob("*.zip"))
        audit_report["total_archives"] = len(zip_files)

        for zip_file in zip_files:
            analysis = self.analyze_archive(zip_file)
            audit_report["analyses"].append(analysis)
            audit_report["total_size"] += zip_file.stat().st_size

            # Calculate potential space savings from removing duplicates
            for duplicate_set in analysis.duplicate_files:
                # Estimate savings (excluding the first file in each duplicate set)
                for duplicate_file in duplicate_set[1:]:
                    # This is a rough estimate; actual savings would need file extraction
                    estimated_size = analysis.total_size / analysis.file_count  # Average file size
                    audit_report["potential_savings"] += estimated_size

        # Generate overall recommendations
        if audit_report["total_archives"] > 20:
            audit_report["overall_recommendations"].append(
                "Consider consolidating related archives"
            )

        if audit_report["potential_savings"] > 50 * 1024 * 1024:  # 50MB
            audit_report["overall_recommendations"].append(
                f"Potential space savings of ~{audit_report['potential_savings'] / (1024*1024):.1f}MB by removing duplicates"
            )

        return audit_report

    def cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


def main():
    """CLI interface for ZIPWiz."""
    import argparse

    parser = argparse.ArgumentParser(description="ZIPWiz - Advanced Archive Management")
    parser.add_argument("archive", help="Path to ZIP archive")
    parser.add_argument("--analyze", action="store_true", help="Analyze archive")
    parser.add_argument("--extract", help="Extract to directory")
    parser.add_argument("--optimize", action="store_true", help="Extract with optimization")
    parser.add_argument("--audit", action="store_true", help="Audit all archives in repository")

    args = parser.parse_args()

    project_root = Path.cwd()
    zipwiz = ZIPWiz(project_root)

    try:
        if args.audit:
            report = zipwiz.audit_repository_archives()
            print(json.dumps(report, indent=2, default=str))
        elif args.analyze:
            analysis = zipwiz.analyze_archive(Path(args.archive))
            print(json.dumps(analysis, indent=2, default=str))
        elif args.extract:
            if args.optimize:
                result = zipwiz.extract_with_optimization(Path(args.archive), Path(args.extract))
                print(f"Optimization complete: {result}")
            else:
                # Standard extraction
                with zipfile.ZipFile(args.archive, 'r') as zf:
                    zf.extractall(args.extract)
                print(f"Extracted to {args.extract}")
        else:
            parser.print_help()

    finally:
        zipwiz.cleanup()


if __name__ == "__main__":
    main()
