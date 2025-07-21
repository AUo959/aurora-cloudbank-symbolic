#!/usr/bin/env python3
"""

    import argparse

Aurora CloudBank Memory Compression Optimizer
Advanced memory optimization and compression techniques
"""


class MemoryOptimizer:
    """Advanced memory compression and optimization system"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.compression_cache = {}
        self.optimization_log = []

    def analyze_file_patterns(self) -> Dict[str, Any]:
        """Analyze file patterns for optimization opportunities"""
        analysis = {
            "file_types": {},
            "large_files": [],
            "duplicate_candidates": [],
            "compression_opportunities": [],
            "total_size": 0,
            "optimization_potential": 0,
        }

        # Analyze all files
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden directories and common excludes
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["node_modules", "__pycache__"]
            ]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = os.path.join(root, file)
                try:
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    analysis["total_size"] += file_size

                    # Categorize by extension
                    ext = Path(file).suffix.lower()
                    if ext not in analysis["file_types"]:
                        analysis["file_types"][ext] = {"count": 0, "total_size": 0}

                    analysis["file_types"][ext]["count"] += 1
                    analysis["file_types"][ext]["total_size"] += file_size

                    # Identify large files (>1MB)
                    if file_size > 1024 * 1024:
                        analysis["large_files"].append(
                            {
                                "path": file_path,
                                "size": file_size,
                                "size_mb": round(file_size / (1024 * 1024), 2),
                            }
                        )

                    # Check compression opportunities
                    if self._is_compressible(file_path, ext):
                        potential_savings = self._estimate_compression_savings(
                            file_path, file_size
                        )
                        if potential_savings > 1024:  # Only if we can save >1KB
                            analysis["compression_opportunities"].append(
                                {
                                    "path": file_path,
                                    "current_size": file_size,
                                    "estimated_savings": potential_savings,
                                }
                            )
                            analysis["optimization_potential"] += potential_savings

                except (OSError, IOError):
                    continue

        return analysis

    def _is_compressible(self, file_path: str, ext: str) -> bool:
        """Determine if a file type is suitable for compression"""
        compressible_extensions = {
            ".json",
            ".csv",
            ".txt",
            ".md",
            ".py",
            ".js",
            ".css",
            ".html",
            ".xml",
            ".yaml",
            ".yml",
            ".log",
            ".sql",
            ".sh",
            ".bat",
        }

        # Skip already compressed files
        compressed_extensions = {".zip", ".gz", ".bz2", ".xz", ".7z", ".rar", ".tar"}

        return ext in compressible_extensions and ext not in compressed_extensions

    def _estimate_compression_savings(self, file_path: str, file_size: int) -> int:
        """Estimate potential compression savings for a file"""
        if file_size < 1024:  # Skip very small files
            return 0

        try:
            # Sample-based compression estimation
            sample_size = min(4096, file_size)  # Sample first 4KB

            with open(file_path, "rb", encoding="utf-8") as f:
                sample_data = f.read(sample_size)

            # Compress sample
            compressed_sample = gzip.compress(sample_data)
            compression_ratio = len(compressed_sample) / len(sample_data)

            # Estimate full file compression
            estimated_compressed_size = int(file_size * compression_ratio)
            potential_savings = file_size - estimated_compressed_size

            return max(0, potential_savings)

        except (OSError, ValueError, RuntimeError):
            return 0

    def optimize_json_files(self) -> Dict[str, Any]:
        """Optimize JSON files by removing whitespace and compressing"""
        results = {"processed": 0, "space_saved": 0, "errors": 0, "details": []}

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.endswith(".json") and not file.startswith("."):
                    file_path = os.path.join(root, file)
                    try:
                        original_size = os.path.getsize(file_path)

                        # Read and minify JSON
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)

                        # Write back in compact format
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(
                                data, f, separators=(",", ":"), ensure_ascii=False
                            )

                        new_size = os.path.getsize(file_path)
                        space_saved = original_size - new_size

                        if space_saved > 0:
                            results["space_saved"] += space_saved
                            results["details"].append(
                                {
                                    "file": file_path,
                                    "original_size": original_size,
                                    "new_size": new_size,
                                    "saved": space_saved,
                                }
                            )

                        results["processed"] += 1

                    except (OSError, ValueError, RuntimeError) as e:
                        results["errors"] += 1
                        results["details"].append({"file": file_path, "error": str(e)})

        return results

    def compress_large_logs(self) -> Dict[str, Any]:
        """Compress large log files"""
        results = {"compressed": 0, "space_saved": 0, "errors": 0, "details": []}

        log_extensions = {".log", ".out", ".err"}

        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file).suffix.lower()

                if ext in log_extensions:
                    try:
                        file_size = os.path.getsize(file_path)

                        # Only compress files larger than 1MB
                        if file_size > 1024 * 1024:
                            compressed_path = file_path + ".gz"

                            # Compress the file
                            with open(file_path, "rb", encoding="utf-8") as f_in:
                                with gzip.open(
                                    compressed_path, "wb", encoding="utf-8"
                                ) as f_out:
                                    f_out.writelines(f_in)

                            compressed_size = os.path.getsize(compressed_path)
                            space_saved = file_size - compressed_size

                            # Remove original file
                            os.remove(file_path)

                            results["compressed"] += 1
                            results["space_saved"] += space_saved
                            results["details"].append(
                                {
                                    "file": file_path,
                                    "original_size": file_size,
                                    "compressed_size": compressed_size,
                                    "saved": space_saved,
                                }
                            )

                    except (OSError, ValueError, RuntimeError) as e:
                        results["errors"] += 1
                        results["details"].append({"file": file_path, "error": str(e)})

        return results

    def find_duplicate_files(self) -> Dict[str, List[str]]:
        """Find potential duplicate files using size and hash"""
        size_groups = {}
        duplicates = {}

        # Group files by size first (quick filter)
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                if file.startswith("."):
                    continue

                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)

                    if file_size not in size_groups:
                        size_groups[file_size] = []
                    size_groups[file_size].append(file_path)

                except OSError:
                    continue

        # For files with same size, check hash
        for size, files in size_groups.items():
            if len(files) > 1 and size > 0:  # Skip empty files
                hash_groups = {}

                for file_path in files:
                    try:
                        _file_hash = self._calculate_file_hash(file_path)

                        if file_hash not in hash_groups:
                            hash_groups[file_hash] = []
                        hash_groups[file_hash].append(file_path)

                    except (OSError, ValueError, RuntimeError):
                        continue

                # Report actual duplicates
                for file_hash, duplicate_files in hash_groups.items():
                    if len(duplicate_files) > 1:
                        duplicates[file_hash] = duplicate_files

        return duplicates

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        hash_obj = hashlib.sha256()

        with open(file_path, "rb", encoding="utf-8") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()

    def optimize_git_objects(self) -> Dict[str, Any]:
        """Optimize git objects and reduce repository size"""
        results = {
            "before_size": 0,
            "after_size": 0,
            "space_saved": 0,
            "operations": [],
        }

        try:
            # Get initial .git size
            git_path = os.path.join(self.repo_path, ".git")
            if os.path.exists(git_path):
                results["before_size"] = self._get_directory_size(git_path)

                # Run git garbage collection
                subprocess.run(
                    ["git", "gc", "--aggressive", "--prune=now"],
                    cwd=self.repo_path,
                    check=True,
                )
                results["operations"].append("git gc --aggressive --prune=now")

                # Run git repack
                subprocess.run(["git", "repack", "-ad"], cwd=self.repo_path, check=True)
                results["operations"].append("git repack -ad")

                # Get final size
                results["after_size"] = self._get_directory_size(git_path)
                results["space_saved"] = results["before_size"] - results["after_size"]

        except (OSError, ValueError, RuntimeError) as e:
            results["error"] = str(e)

        return results

    def _get_directory_size(self, directory: str) -> int:
        """Calculate total size of a directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(file_path)
                except OSError:
                    continue
        return total_size

    def generate_optimization_report(self) -> str:
        """Generate comprehensive optimization report"""
        analysis = self.analyze_file_patterns()
        duplicates = self.find_duplicate_files()

        report = """# Memory Compression & Optimization Report
Generated: {datetime.datetime.now().isoformat()}

## Repository Analysis
- **Total Size**: {analysis['total_size'] / (1024*1024):.1f} MB
- **Total Files**: {sum(info['count'] for info in analysis['file_types'].values())}
- **Optimization Potential**: {analysis['optimization_potential'] / 1024:.1f} KB

## File Type Distribution
"""

        # Sort file types by size
        sorted_types = sorted(
            analysis["file_types"].items(),
            key=lambda x: x[1]["total_size"],
            reverse=True,
        )

        for ext, info in sorted_types[:10]:  # Top 10
            size_mb = info["total_size"] / (1024 * 1024)
            report += f"- **{ext or 'no extension'}**: {info['count']} files, {size_mb:.1f}MB\n"

        report += """
## Large Files (>1MB)
Found {len(analysis['large_files'])} large files:
"""

        for large_file in sorted(
            analysis["large_files"], key=lambda x: x["size"], reverse=True
        )[:5]:
            report += f"- `{large_file['path']}`: {large_file['size_mb']}MB\n"

        report += """
## Compression Opportunities
Found {len(analysis['compression_opportunities'])} files suitable for compression:
"""

        total_savings = sum(
            opp["estimated_savings"] for opp in analysis["compression_opportunities"]
        )
        report += f"- **Potential Space Savings**: {total_savings / 1024:.1f} KB\n"

        report += """
## Duplicate Files
Found {len(duplicates)} sets of duplicate files:
"""

        duplicate_savings = 0
        for file_hash, files in list(duplicates.items())[:5]:  # Show first 5 sets
            if len(files) > 1:
                file_size = os.path.getsize(files[0]) if os.path.exists(files[0]) else 0
                savings = file_size * (len(files) - 1)
                duplicate_savings += savings

                report += (
                    f"- {len(files)} identical files ({file_size/1024:.1f}KB each):\n"
                )
                for file_path in files[:3]:  # Show first 3
                    report += f"  - `{file_path}`\n"
                if len(files) > 3:
                    report += f"  - ... and {len(files)-3} more\n"

        report += f"\n**Total Duplicate Savings Potential**: {duplicate_savings / 1024:.1f} KB\n"

        report += """
## Optimization Recommendations

### High Priority
1. **JSON Minification**: Optimize {len([f for f in analysis['file_types'] if f == '.json'])} JSON files
2. **Log Compression**: Compress large log files
3. **Git Optimization**: Run git gc and repack

### Medium Priority
1. **Duplicate Removal**: Review and remove duplicate files
2. **Large File Analysis**: Consider external storage for large assets
3. **Cache Cleanup**: Regular cleanup of temporary files

### Low Priority
1. **File Format Optimization**: Consider more efficient formats
2. **Archive Old Versions**: Move old exports to external storage
"""

        return report

    def run_optimization_suite(self, dry_run: bool = True) -> Dict[str, Any]:
        """Run the complete optimization suite"""
        results = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dry_run": dry_run,
            "json_optimization": None,
            "log_compression": None,
            "git_optimization": None,
            "total_space_saved": 0,
        }

        if not dry_run:
            # JSON optimization
            results["json_optimization"] = self.optimize_json_files()
            results["total_space_saved"] += results["json_optimization"]["space_saved"]

            # Log compression
            results["log_compression"] = self.compress_large_logs()
            results["total_space_saved"] += results["log_compression"]["space_saved"]

            # Git optimization
            results["git_optimization"] = self.optimize_git_objects()
            results["total_space_saved"] += results["git_optimization"].get(
                "space_saved", 0
            )

        return results

def main():

    parser = argparse.ArgumentParser(description="Aurora CloudBank Memory Optimizer")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze optimization opportunities"
    )
    parser.add_argument(
        "--optimize", action="store_true", help="Run optimization suite"
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Dry run mode (default)"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute actual optimization"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate optimization report"
    )

    args = parser.parse_args()

    optimizer = MemoryOptimizer()

    if args.analyze or args.report:
        report = optimizer.generate_optimization_report()
        print(report)

        if args.report:
            with open("memory_optimization_report.md", "w", encoding="utf-8") as f:
                f.write(report)
            print("\n📄 Report saved to memory_optimization_report.md")

    if args.optimize:
        dry_run = not args.execute
        print(
            f"🔧 Running optimization suite {'(DRY RUN)' if dry_run else '(EXECUTING)'}"
        )

        results = optimizer.run_optimization_suite(dry_run=dry_run)

        if not dry_run:
            print("\n✅ Optimization complete!")
            print(f"📊 Total space saved: {results['total_space_saved'] / 1024:.1f} KB")

            if results["json_optimization"]:
                json_results = results["json_optimization"]
                print(
                    f"📄 JSON files: {json_results['processed']} processed, {json_results['space_saved']} bytes saved"
                )

            if results["log_compression"]:
                log_results = results["log_compression"]
                print(
                    f"📜 Log files: {log_results['compressed']} compressed, {log_results['space_saved']} bytes saved"
                )

        else:
            print("🔍 Analysis complete. Use --execute to run actual optimization.")

if __name__ == "__main__":
    main()
