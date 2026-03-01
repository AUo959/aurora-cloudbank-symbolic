#!/usr/bin/env python3
"""

    import datetime

Aurora CloudBank - Memory Compression and Optimization System
Advanced repository optimization with intelligent compression and deduplication
"""


import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import shutil
import hashlib
import gzip


class MemoryCompressionOptimizer:
    """Advanced memory and storage optimization system"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.compression_config = {
            "compress_extensions": {".log", ".txt", ".md", ".json", ".csv", ".sql"},
            "exclude_paths": {".git", ".venv", "node_modules", "__pycache__"},
            "min_file_size_kb": 10,  # Only compress files > 10KB
            "compression_ratio_threshold": 0.7,  # Only keep if compression saves >30%
        }
        self.deduplication_config = {
            "check_extensions": {".zip", ".pd", ".png", ".jpg", ".jpeg", ".md", ".txt"},
            "min_file_size_kb": 1,  # Check all files > 1KB for duplicates
            "hash_chunk_size": 8192,
        }

    def analyze_repository(self) -> Dict:
        """Comprehensive repository analysis for optimization opportunities"""
        print("🔍 Analyzing repository for optimization opportunities...")

        analysis = {
            "total_files": 0,
            "total_size_mb": 0.0,
            "compressible_files": [],
            "duplicate_files": [],
            "large_files": [],
            "cache_files": [],
            "optimization_potential_mb": 0.0,
        }

        # Walk through all files
        file_hashes = defaultdict(list)

        for root, dirs, files in os.walk("."):
            # Skip excluded directories
            dirs[:] = [
                d for d in dirs if not any(ex in str(Path(root) / d) for ex in self.compression_config["exclude_paths"])
            ]

            for file in files:
                file_path = Path(root) / file

                try:
                    if not file_path.is_file():
                        continue

                    file_size = file_path.stat().st_size
                    analysis["total_files"] += 1
                    analysis["total_size_mb"] += file_size / (1024 * 1024)

                    # Check for compressible files
                    if file_path.suffix.lower() in self.compression_config["compress_extensions"]:
                        if file_size > self.compression_config["min_file_size_kb"] * 1024:
                            compression_potential = self._estimate_compression_savings(file_path)
                            if compression_potential > 0:
                                analysis["compressible_files"].append(
                                    {
                                        "path": str(file_path),
                                        "size_kb": file_size / 1024,
                                        "estimated_savings_kb": compression_potential / 1024,
                                    }
                                )
                                analysis["optimization_potential_mb"] += compression_potential / (1024 * 1024)

                    # Check for duplicates
                    if file_path.suffix.lower() in self.deduplication_config["check_extensions"]:
                        if file_size > self.deduplication_config["min_file_size_kb"] * 1024:
                            self._calculate_file_hash(file_path)
                            if file_hash:
                                file_hashes[file_hash].append(
                                    {
                                        "path": str(file_path),
                                        "size_kb": file_size / 1024,
                                    }
                                )

                    # Check for large files
                    if file_size > 50 * 1024 * 1024:  # > 50MB
                        analysis["large_files"].append(
                            {
                                "path": str(file_path),
                                "size_mb": file_size / (1024 * 1024),
                            }
                        )

                    # Check for cache files
                    if any(pattern in str(file_path) for pattern in ["cache", ".pyc", "__pycache__", ".tmp"]):
                        analysis["cache_files"].append({"path": str(file_path), "size_kb": file_size / 1024})

                except (OSError, PermissionError):
                    continue

        # Identify duplicate files
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                # Calculate potential savings (keep largest, remove others)
                files.sort(key=lambda x: x["size_kb"], reverse=True)
                savings_kb = sum(f["size_kb"] for f in files[1:])

                analysis["duplicate_files"].append({"hash": file_hash, "files": files, "savings_kb": savings_kb})
                analysis["optimization_potential_mb"] += savings_kb / 1024

        return analysis

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb", encoding="utf-8") as f:
                for chunk in iter(lambda: f.read(self.deduplication_config["hash_chunk_size"]), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (OSError, PermissionError):
            return None

    def _estimate_compression_savings(self, file_path: Path) -> int:
        """Estimate compression savings for a file"""
        try:
            original_size = file_path.stat().st_size

            # Sample compression on first 64KB to estimate
            sample_size = min(64 * 1024, original_size)

            with open(file_path, "rb", encoding="utf-8") as f:
                sample_data = f.read(sample_size)

            compressed_sample = gzip.compress(sample_data)
            compression_ratio = len(compressed_sample) / len(sample_data)

            if compression_ratio < self.compression_config["compression_ratio_threshold"]:
                estimated_compressed_size = int(original_size * compression_ratio)
                return original_size - estimated_compressed_size

            return 0

        except (OSError, PermissionError):
            return 0

    def compress_files(self, compressible_files: List[Dict]) -> Dict:
        """Compress identified files"""
        results = {
            "compressed_files": [],
            "failed_compressions": [],
            "total_savings_mb": 0.0,
        }

        for file_info in compressible_files:
            file_path = Path(file_info["path"])

            if self.dry_run:
                print(f"  Would compress: {file_path} (est. {file_info['estimated_savings_kb']:.1f}KB saved)")
                results["compressed_files"].append(file_info["path"])
                results["total_savings_mb"] += file_info["estimated_savings_kb"] / 1024
                continue

            try:
                # Create compressed version
                compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

                with open(file_path, "rb", encoding="utf-8") as f_in:
                    with gzip.open(compressed_path, "wb", encoding="utf-8") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # Check actual compression ratio
                original_size = file_path.stat().st_size
                compressed_size = compressed_path.stat().st_size
                actual_ratio = compressed_size / original_size

                if actual_ratio < self.compression_config["compression_ratio_threshold"]:
                    # Good compression, replace original
                    file_path.unlink()
                    actual_savings = original_size - compressed_size

                    results["compressed_files"].append(str(file_path))
                    results["total_savings_mb"] += actual_savings / (1024 * 1024)

                    print(f"✅ Compressed: {file_path} ({actual_savings / 1024:.1f}KB saved)")
                else:
                    # Poor compression, remove compressed version
                    compressed_path.unlink()
                    print(f"⚠️  Skipped: {file_path} (poor compression ratio)")

            except (OSError, PermissionError) as e:
                results["failed_compressions"].append({"path": str(file_path), "error": str(e)})
                print(f"❌ Failed to compress: {file_path} - {e}")

        return results

    def deduplicate_files(self, duplicate_groups: List[Dict]) -> Dict:
        """Remove duplicate files, keeping the best copy"""
        results = {"removed_files": [], "failed_removals": [], "total_savings_mb": 0.0}

        for group in duplicate_groups:
            files = group["files"]
            if len(files) < 2:
                continue

            # Sort by size (descending) and path (for consistency)
            files.sort(key=lambda x: (-x["size_kb"], x["path"]))

            # Keep the first (largest) file, remove others
            keep_file = files[0]
            remove_files = files[1:]

            print(f"🔄 Duplicate group (keeping {keep_file['path']}):")

            for file_info in remove_files:
                file_path = Path(file_info["path"])

                if self.dry_run:
                    print(f"  Would remove: {file_path} ({file_info['size_kb']:.1f}KB)")
                    results["removed_files"].append(str(file_path))
                    results["total_savings_mb"] += file_info["size_kb"] / 1024
                    continue

                try:
                    file_path.unlink()
                    results["removed_files"].append(str(file_path))
                    results["total_savings_mb"] += file_info["size_kb"] / (1024)
                    print(f"✅ Removed duplicate: {file_path}")

                except (OSError, PermissionError) as e:
                    results["failed_removals"].append({"path": str(file_path), "error": str(e)})
                    print(f"❌ Failed to remove: {file_path} - {e}")

        return results

    def optimize_large_files(self, large_files: List[Dict]) -> Dict:
        """Optimize large files through various techniques"""
        results = {
            "optimized_files": [],
            "archive_candidates": [],
            "total_potential_savings_mb": 0.0,
        }

        for file_info in large_files:
            file_path = Path(file_info["path"])

            # Skip if it's a known binary that shouldn't be optimized
            if file_path.suffix.lower() in {
                ".zip",
                ".gz",
                ".bz2",
                ".xz",
                ".7z",
                ".rar",
            }:
                continue

            # Check if it's a PDF that might be compressed
            if file_path.suffix.lower() == ".pd":
                results["archive_candidates"].append(
                    {
                        "path": str(file_path),
                        "size_mb": file_info["size_mb"],
                        "recommendation": "Consider external archival for large PDF",
                    }
                )
                results["total_potential_savings_mb"] += file_info["size_mb"]

            # Check if it's a log file that could be compressed
            elif file_path.suffix.lower() in {".log", ".txt"}:
                compression_savings = self._estimate_compression_savings(file_path)
                if compression_savings > 0:
                    results["optimized_files"].append(
                        {
                            "path": str(file_path),
                            "optimization": "compression",
                            "potential_savings_mb": compression_savings / (1024 * 1024),
                        }
                    )
                    results["total_potential_savings_mb"] += compression_savings / (1024 * 1024)

        return results

    def clean_cache_files(self, cache_files: List[Dict]) -> Dict:
        """Clean up cache files"""
        results = {"removed_files": [], "failed_removals": [], "total_savings_mb": 0.0}

        for file_info in cache_files:
            file_path = Path(file_info["path"])

            if self.dry_run:
                print(f"  Would remove cache file: {file_path}")
                results["removed_files"].append(str(file_path))
                results["total_savings_mb"] += file_info["size_kb"] / 1024
                continue

            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    shutil.rmtree(file_path)

                results["removed_files"].append(str(file_path))
                results["total_savings_mb"] += file_info["size_kb"] / 1024
                print(f"✅ Removed cache: {file_path}")

            except (OSError, PermissionError) as e:
                results["failed_removals"].append({"path": str(file_path), "error": str(e)})
                print(f"❌ Failed to remove cache: {file_path} - {e}")

        return results

    def generate_optimization_report(self, analysis: Dict, optimization_results: Dict = None) -> str:
        """Generate comprehensive optimization report"""
        report_lines = [
            "# Memory Compression and Optimization Report",
            f"**Generated:** {analysis.get('timestamp', 'Unknown')}",
            "",
            "## Repository Analysis Summary",
            "",
            f"- **Total Files**: {analysis['total_files']:,}",
            f"- **Total Size**: {analysis['total_size_mb']:.1f}MB",
            f"- **Optimization Potential**: {analysis['optimization_potential_mb']:.1f}MB",
            "",
            "## Optimization Opportunities",
            "",
        ]

        # Compressible files
        if analysis["compressible_files"]:
            total_compressible = sum(f["estimated_savings_kb"] for f in analysis["compressible_files"])
            report_lines.extend(
                [
                    f"### Compressible Files ({len(analysis['compressible_files'])} files)",
                    f"**Potential Savings**: {total_compressible / 1024:.1f}MB",
                    "",
                ]
            )

            for file_info in analysis["compressible_files"][:10]:
                report_lines.append(
                    f"- `{file_info['path']}` - {file_info['size_kb']:.1f}KB "
                    f"(save ~{file_info['estimated_savings_kb']:.1f}KB)"
                )

            if len(analysis["compressible_files"]) > 10:
                report_lines.append(f"- ... and {len(analysis['compressible_files']) - 10} more")

            report_lines.append("")

        # Duplicate files
        if analysis["duplicate_files"]:
            total_duplicate_savings = sum(g["savings_kb"] for g in analysis["duplicate_files"])
            report_lines.extend(
                [
                    f"### Duplicate Files ({len(analysis['duplicate_files'])} groups)",
                    f"**Potential Savings**: {total_duplicate_savings / 1024:.1f}MB",
                    "",
                ]
            )

            for group in analysis["duplicate_files"][:5]:
                report_lines.append(f"- {len(group['files'])} duplicates, save {group['savings_kb'] / 1024:.1f}MB")

            report_lines.append("")

        # Large files
        if analysis["large_files"]:
            report_lines.extend([f"### Large Files ({len(analysis['large_files'])} files)", ""])

            for file_info in analysis["large_files"][:5]:
                report_lines.append(f"- `{file_info['path']}` - {file_info['size_mb']:.1f}MB")

            report_lines.append("")

        # Cache files
        if analysis["cache_files"]:
            total_cache_size = sum(f["size_kb"] for f in analysis["cache_files"])
            report_lines.extend(
                [
                    f"### Cache Files ({len(analysis['cache_files'])} files)",
                    f"**Total Size**: {total_cache_size / 1024:.1f}MB",
                    "",
                ]
            )

        # Optimization results
        if optimization_results:
            report_lines.extend(["## Optimization Results", ""])

            total_savings = 0.0
            for result_type, results in optimization_results.items():
                if isinstance(results, dict) and "total_savings_mb" in results:
                    total_savings += results["total_savings_mb"]

            report_lines.append(f"**Total Space Saved**: {total_savings:.1f}MB")
            report_lines.append("")

        return "\n".join(report_lines)

    def run_full_optimization(self) -> Dict:
        """Run complete optimization process"""
        print("🚀 Starting full repository optimization...")

        # Analyze repository
        analysis = self.analyze_repository()

        # Run optimizations
        optimization_results = {}

        if analysis["compressible_files"]:
            print("\n📦 Compressing files...")
            optimization_results["compression"] = self.compress_files(analysis["compressible_files"])

        if analysis["duplicate_files"]:
            print("\n🔄 Removing duplicates...")
            optimization_results["deduplication"] = self.deduplicate_files(analysis["duplicate_files"])

        if analysis["cache_files"]:
            print("\n🧹 Cleaning cache files...")
            optimization_results["cache_cleanup"] = self.clean_cache_files(analysis["cache_files"])

        if analysis["large_files"]:
            print("\n📊 Analyzing large files...")
            optimization_results["large_file_optimization"] = self.optimize_large_files(analysis["large_files"])

        # Generate report
        report = self.generate_optimization_report(analysis, optimization_results)

        # Save report
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/memory_optimization_report_{timestamp}.md"

        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Optimization report saved to: {report_file}")

        return {
            "analysis": analysis,
            "optimization_results": optimization_results,
            "report_file": report_file,
        }


def main():
    """Main optimization function"""
    parser = argparse.ArgumentParser(description="Memory compression and optimization")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute optimizations (default is dry-run)",
    )
    parser.add_argument("--compress-only", action="store_true", help="Only run compression optimization")
    parser.add_argument("--dedupe-only", action="store_true", help="Only run deduplication")
    parser.add_argument("--cache-only", action="store_true", help="Only clean cache files")

    args = parser.parse_args()

    optimizer = MemoryCompressionOptimizer(dry_run=not args.execute)

    print("🔧 Aurora CloudBank - Memory Compression & Optimization")
    print("=" * 60)

    if args.compress_only or args.dedupe_only or args.cache_only:
        # Run specific optimization
        analysis = optimizer.analyze_repository()

        if args.compress_only and analysis["compressible_files"]:
            optimizer.compress_files(analysis["compressible_files"])
        elif args.dedupe_only and analysis["duplicate_files"]:
            optimizer.deduplicate_files(analysis["duplicate_files"])
        elif args.cache_only and analysis["cache_files"]:
            optimizer.clean_cache_files(analysis["cache_files"])
    else:
        # Run full optimization
        optimizer.run_full_optimization()


if __name__ == "__main__":

    main()
