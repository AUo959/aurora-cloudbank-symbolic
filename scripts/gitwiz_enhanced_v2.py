#!/usr/bin/env python3
"""

    import argparse

GitWiz Enhanced v2.0 - Intelligent Git Repository Management
Created for Aurora CloudBank Symbolic - July 2025
"""


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GitWizEnhanced')

@dataclass
class RepositoryMetrics:
    """Repository health and optimization metrics."""
    total_files: int = 0
    total_size_mb: float = 0.0
    git_size_mb: float = 0.0
    branch_count: int = 0
    stale_branches: int = 0
    commit_count: int = 0
    contributors: int = 0
    optimization_score: float = 0.0
    security_score: float = 0.0
    last_commit: Optional[str] = None
    issues_detected: List[str] = None

    def __post_init__(self):
        if self.issues_detected is None:
            self.issues_detected = []

@dataclass
class FileAnalysis:
    """Analysis of file patterns and types."""
    large_files: List[Dict[str, Any]] = None
    duplicate_candidates: List[Dict[str, Any]] = None
    cache_files: List[str] = None
    temp_files: List[str] = None
    archive_files: List[Dict[str, Any]] = None
    file_types: Dict[str, int] = None

    def __post_init__(self):
        if self.large_files is None:
            self.large_files = []
        if self.duplicate_candidates is None:
            self.duplicate_candidates = []
        if self.cache_files is None:
            self.cache_files = []
        if self.temp_files is None:
            self.temp_files = []
        if self.archive_files is None:
            self.archive_files = []
        if self.file_types is None:
            self.file_types = {}

class GitWizEnhanced:
    """Enhanced Git repository management and optimization tool."""

        """Initialize GitWiz with repository path."""
        self.repo_path = Path(repo_path).resolve()
        self.git_dir = self.repo_path / ".git"
        self.gitwiz_dir = self.repo_path / ".gitwiz"

        # Ensure .gitwiz directory exists
        self.gitwiz_dir.mkdir(exist_ok=True)

        # Configuration
        self.config = self._load_config()
        self.thresholds = self.config.get("thresholds", {})

        # Validate git repository
        if not self.git_dir.exists():
            raise ValueError(f"Not a git repository: {self.repo_path}")

        logger.info(f"GitWiz Enhanced initialized for: {self.repo_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Load GitWiz configuration."""
        config_file = self.gitwiz_dir / "config.json"

        default_config = {
            "thresholds": {
                "large_file_mb": 10,
                "repo_size_mb": 500,
                "stale_branch_days": 30,
                "max_branches": 20,
                "cache_file_count": 100
            },
            "auto_cleanup": {
                "enabled": False,
                "dry_run": True,
                "backup_before_cleanup": True
            },
            "monitoring": {
                "enabled": True,
                "check_interval_hours": 24
            },
            "ignore_patterns": [
                "*.pyc", "__pycache__", "*.so", "*.dylib",
                "node_modules", ".DS_Store", "Thumbs.db"
            ]
        }

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding="utf-8") as f:
                    user_config = json.load(f)
                # Merge with defaults
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")

        # Save current config
        with open(config_file, 'w', encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def run_git_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute git command safely."""
        full_command = ["git", "-C", str(self.repo_path)] + command
        try:
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(full_command)}")
            logger.error(f"Error: {e.stderr}")
            raise

    def analyze_repository(self) -> RepositoryMetrics:
        """Comprehensive repository analysis."""
        logger.info("Starting comprehensive repository analysis...")

        metrics = RepositoryMetrics()

        # Basic file statistics
        total_size = 0
        file_count = 0

        for file_path in self.repo_path.rglob("*"):
            if file_path.is_file() and not self._should_ignore_file(file_path):
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                except (OSError, PermissionError):
                    continue

        metrics.total_files = file_count
        metrics.total_size_mb = total_size / (1024 * 1024)

        # Git-specific metrics
        try:
            # Git directory size
            git_size = sum(
                f.stat().st_size for f in self.git_dir.rglob("*")
                if f.is_file()
            )
            metrics.git_size_mb = git_size / (1024 * 1024)

            # Branch information
            branches_result = self.run_git_command(["branch", "-r"])
            metrics.branch_count = len(branches_result.stdout.strip().split('\n'))

            # Commit count
            commits_result = self.run_git_command(["rev-list", "--count", "HEAD"])
            metrics.commit_count = int(commits_result.stdout.strip())

            # Contributors
            contributors_result = self.run_git_command(["shortlog", "-sn", "--all"])
            metrics.contributors = len(contributors_result.stdout.strip().split('\n'))

            # Last commit
            last_commit_result = self.run_git_command(["log", "-1", "--format=%H"])
            metrics.last_commit = last_commit_result.stdout.strip()

            # Stale branches
            metrics.stale_branches = self._count_stale_branches()

        except Exception as e:
            logger.error(f"Error collecting git metrics: {e}")
            metrics.issues_detected.append(f"Git metrics collection failed: {e}")

        # Calculate scores
        metrics.optimization_score = self._calculate_optimization_score(metrics)
        metrics.security_score = self._calculate_security_score()

        logger.info(f"Repository analysis complete: {metrics.total_files} files, {metrics.total_size_mb:.1f}MB")
        return metrics

    def analyze_files(self) -> FileAnalysis:
        """Detailed file analysis for optimization opportunities."""
        logger.info("Analyzing files for optimization opportunities...")

        analysis = FileAnalysis()
        file_hashes = {}
        file_sizes = {}

        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file() or self._should_ignore_file(file_path):
                continue

            try:
                rel_path = file_path.relative_to(self.repo_path)
                size = file_path.stat().st_size
                file_sizes[str(rel_path)] = size

                # Track file types
                suffix = file_path.suffix.lower()
                analysis.file_types[suffix] = analysis.file_types.get(suffix, 0) + 1

                # Large files
                if size > self.thresholds.get("large_file_mb", 10) * 1024 * 1024:
                    analysis.large_files.append({
                        "path": str(rel_path),
                        "size_mb": round(size / (1024 * 1024), 2),
                        "type": suffix or "no extension"
                    })

                # Cache and temp files
                if self._is_cache_file(file_path):
                    analysis.cache_files.append(str(rel_path))
                elif self._is_temp_file(file_path):
                    analysis.temp_files.append(str(rel_path))
                elif suffix in ['.zip', '.tar', '.gz', '.7z', '.rar']:
                    analysis.archive_files.append({
                        "path": str(rel_path),
                        "size_mb": round(size / (1024 * 1024), 2)
                    })

                # Calculate hash for duplicate detection
                if size > 1024:  # Only for files > 1KB
                    _file_hash = self._calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        file_hashes[file_hash].append(str(rel_path))
                    else:
                        file_hashes[file_hash] = [str(rel_path)]

            except (OSError, PermissionError) as e:
                logger.warning(f"Could not analyze {file_path}: {e}")

        # Find duplicates
        for file_hash, paths in file_hashes.items():
            if len(paths) > 1:
                total_size = sum(file_sizes.get(p, 0) for p in paths)
                analysis.duplicate_candidates.append({
                    "hash": file_hash,
                    "files": paths,
                    "count": len(paths),
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "potential_savings_mb": round((total_size * (len(paths) - 1)) / (1024 * 1024), 2)
                })

        logger.info(f"File analysis complete: {len(analysis.large_files)} large files, "
                    f"{len(analysis.duplicate_candidates)} duplicate groups found")
        return analysis

    def optimize_repository(self, dry_run: bool = True) -> Dict[str, Any]:
        """Optimize repository with various cleanup operations."""
        logger.info(f"Starting repository optimization (dry_run={dry_run})...")

        optimization_report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "operations": [],
            "space_saved_mb": 0.0,
            "files_processed": 0,
            "errors": []
        }

        try:
            # Git cleanup operations
            git_operations = [
                (["gc", "--aggressive"], "Aggressive garbage collection"),
                (["prune"], "Remove unreachable objects"),
                (["reflog", "expire", "--expire=now", "--all"], "Clean reflog"),
                (["remote", "prune", "origin"], "Prune remote references")
            ]

            for git_cmd, description in git_operations:
                try:
                    if not dry_run:
                        self.run_git_command(git_cmd)
                    optimization_report["operations"].append({
                        "type": "git",
                        "command": " ".join(git_cmd),
                        "description": description,
                        "status": "executed" if not dry_run else "simulated"
                    })
                except Exception as e:
                    error_msg = f"Git operation failed: {description} - {e}"
                    optimization_report["errors"].append(error_msg)
                    logger.error(error_msg)

            # File cleanup operations
            file_analysis = self.analyze_files()

            # Clean cache files
            if file_analysis.cache_files:
                cache_size = self._calculate_files_size(file_analysis.cache_files)
                if not dry_run:
                    self._remove_files(file_analysis.cache_files)
                optimization_report["operations"].append({
                    "type": "cache_cleanup",
                    "files_count": len(file_analysis.cache_files),
                    "size_mb": round(cache_size / (1024 * 1024), 2),
                    "status": "executed" if not dry_run else "simulated"
                })
                optimization_report["space_saved_mb"] += cache_size / (1024 * 1024)
                optimization_report["files_processed"] += len(file_analysis.cache_files)

            # Clean temp files
            if file_analysis.temp_files:
                temp_size = self._calculate_files_size(file_analysis.temp_files)
                if not dry_run:
                    self._remove_files(file_analysis.temp_files)
                optimization_report["operations"].append({
                    "type": "temp_cleanup",
                    "files_count": len(file_analysis.temp_files),
                    "size_mb": round(temp_size / (1024 * 1024), 2),
                    "status": "executed" if not dry_run else "simulated"
                })
                optimization_report["space_saved_mb"] += temp_size / (1024 * 1024)
                optimization_report["files_processed"] += len(file_analysis.temp_files)

        except Exception as e:
            error_msg = f"Optimization failed: {e}"
            optimization_report["errors"].append(error_msg)
            logger.error(error_msg)

        # Save report
        report_file = self.gitwiz_dir / f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding="utf-8") as f:
            json.dump(optimization_report, f, indent=2)

        logger.info(f"Optimization complete. Report saved to: {report_file}")
        return optimization_report

    def manage_branches(self, action: str = "analyze") -> Dict[str, Any]:
        """Manage repository branches."""
        logger.info(f"Managing branches: {action}")

        result = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "branches": {},
            "recommendations": []
        }

        try:
            # Get all branches
            local_branches = self.run_git_command(["branch"])
            remote_branches = self.run_git_command(["branch", "-r"])

            current_branch_result = self.run_git_command(["branch", "--show-current"])
            current_branch = current_branch_result.stdout.strip()

            # Analyze local branches
            for line in local_branches.stdout.strip().split('\n'):
                branch_name = line.strip().lstrip('* ')
                if not branch_name:
                    continue

                # Get last commit date
                try:
                    last_commit_result = self.run_git_command([
                        "log", "-1", "--format=%ci", branch_name
                    ])
                    last_commit_date = datetime.fromisoformat(
                        last_commit_result.stdout.strip().replace(' +', '+')
                    )
                    days_since_commit = (datetime.now() - last_commit_date.replace(tzinfo=None)).days

                    result["branches"][branch_name] = {
                        "type": "local",
                        "is_current": branch_name == current_branch,
                        "last_commit_date": last_commit_date.isoformat(),
                        "days_since_commit": days_since_commit,
                        "is_stale": days_since_commit > self.thresholds.get("stale_branch_days", 30)
                    }

                    # Add recommendations
                    if days_since_commit > self.thresholds.get("stale_branch_days",
                        30) and branch_name != current_branch:
                        result["recommendations"].append({
                            "type": "delete_stale_branch",
                            "branch": branch_name,
                            "reason": f"No commits in {days_since_commit} days",
                            "command": f"git branch -d {branch_name}"
                        })

                except Exception as e:
                    logger.warning(f"Could not analyze branch {branch_name}: {e}")

            # Execute actions if requested
            if action == "cleanup_stale" and result["recommendations"]:
                cleanup_result = []
                for rec in result["recommendations"]:
                    if rec["type"] == "delete_stale_branch":
                        try:
                            cleanup_result.append(f"Deleted stale branch: {rec['branch']}")
                        except Exception as e:
                            cleanup_result.append(f"Failed to delete {rec['branch']}: {e}")
                result["cleanup_result"] = cleanup_result

        except Exception as e:
            logger.error(f"Branch management failed: {e}")
            result["error"] = str(e)

        return result

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive repository health report."""
        logger.info("Generating comprehensive repository report...")

        metrics = self.analyze_repository()
        file_analysis = self.analyze_files()
        branch_info = self.manage_branches("analyze")

        report = {
            "timestamp": datetime.now().isoformat(),
            "repository_path": str(self.repo_path),
            "gitwiz_version": "2.0.0",
            "summary": {
                "total_files": metrics.total_files,
                "total_size_mb": round(metrics.total_size_mb, 2),
                "git_size_mb": round(metrics.git_size_mb, 2),
                "health_status": self._determine_health_status(metrics)
            },
            "metrics": asdict(metrics),
            "file_analysis": asdict(file_analysis),
            "branch_analysis": branch_info,
            "recommendations": self._generate_recommendations(metrics, file_analysis),
            "config": self.config
        }

        # Save report
        report_file = self.gitwiz_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report generated: {report_file}")
        return report

    # Helper methods

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns."""
        rel_path = str(file_path.relative_to(self.repo_path))

        # Git directory
        if '.git/' in rel_path:
            return True

        # Check ignore patterns
        for pattern in self.config.get("ignore_patterns", []):
            if file_path.match(pattern) or rel_path.endswith(pattern.lstrip('*')):
                return True

        return False

    def _is_cache_file(self, file_path: Path) -> bool:
        """Check if file is a cache file."""
        cache_patterns = ['*.pyc', '__pycache__', '*.so', '*.dylib', '.DS_Store', 'Thumbs.db']
        for pattern in cache_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _is_temp_file(self, file_path: Path) -> bool:
        """Check if file is a temporary file."""
        temp_patterns = ['*.tmp', '*.temp', '*~', '*.bak', '*.swp']
        for pattern in temp_patterns:
            if file_path.match(pattern):
                return True
        return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb", encoding="utf-8") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (OSError, PermissionError):
            return "error"

    def _calculate_files_size(self, file_paths: List[str]) -> int:
        """Calculate total size of files."""
        total_size = 0
        for file_path in file_paths:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    total_size += full_path.stat().st_size
            except (OSError, PermissionError):
                continue
        return total_size

    def _remove_files(self, file_paths: List[str]) -> None:
        """Safely remove files."""
        for file_path in file_paths:
            try:
                full_path = self.repo_path / file_path
                if full_path.exists():
                    if full_path.is_file():
                        full_path.unlink()
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not remove {file_path}: {e}")

    def _count_stale_branches(self) -> int:
        """Count stale branches."""
        try:
            branch_info = self.manage_branches("analyze")
            stale_count = 0
            for branch_data in branch_info.get("branches", {}).values():
                if branch_data.get("is_stale", False):
                    stale_count += 1
            return stale_count
        except Exception:
            return 0

    def _calculate_optimization_score(self, metrics: RepositoryMetrics) -> float:
        """Calculate repository optimization score (0-1)."""
        score = 1.0

        # Size penalty
        if metrics.total_size_mb > self.thresholds.get("repo_size_mb", 500):
            score -= 0.2

        # Branch penalty
        if metrics.branch_count > self.thresholds.get("max_branches", 20):
            score -= 0.2

        # Stale branch penalty
        if metrics.stale_branches > 0:
            score -= min(0.3, metrics.stale_branches * 0.1)

        # Git size ratio
        if metrics.total_size_mb > 0:
            git_ratio = metrics.git_size_mb / metrics.total_size_mb
            if git_ratio > 0.5:  # Git directory is too large
                score -= 0.2

        return max(0.0, score)

    def _calculate_security_score(self) -> float:
        """Calculate basic security score."""
        score = 1.0

        # Check for common security issues
        security_files = ['.env', '.env.local', 'config.json', 'secrets.json']
        for sec_file in security_files:
            if (self.repo_path / sec_file).exists():
                score -= 0.2

        # Check for committed credentials (basic)
        try:
            result = self.run_git_command([
                "log", "--all", "-S", "password", "--oneline"
            ], check=False)
            if result.stdout.strip():
                score -= 0.3
        except Exception:
            pass

        return max(0.0, score)

    def _determine_health_status(self, metrics: RepositoryMetrics) -> str:
        """Determine overall health status."""
        if metrics.optimization_score >= 0.8:
            return "excellent"
        elif metrics.optimization_score >= 0.6:
            return "good"
        elif metrics.optimization_score >= 0.4:
            return "fair"
        else:
            return "needs_attention"

    def _generate_recommendations(self,
        metrics: RepositoryMetrics,
        file_analysis: FileAnalysis) -> List[Dict[str,
        Any]]:
        """Generate optimization recommendations."""
        recommendations = []

        # Large files
        if file_analysis.large_files:
            recommendations.append({
                "type": "large_files",
                "priority": "high",
                "description": f"Found {len(file_analysis.large_files)} large files",
                "action": "Consider using Git LFS for large files",
                "files": file_analysis.large_files[:5]  # Show first 5
            })

        # Duplicates
        if file_analysis.duplicate_candidates:
            total_savings = sum(d["potential_savings_mb"] for d in file_analysis.duplicate_candidates)
            recommendations.append({
                "type": "duplicates",
                "priority": "medium",
                "description": f"Found {len(file_analysis.duplicate_candidates)} duplicate groups",
                "action": f"Remove duplicates to save {total_savings:.1f}MB",
                "potential_savings_mb": total_savings
            })

        # Cache files
        if file_analysis.cache_files:
            recommendations.append({
                "type": "cache_cleanup",
                "priority": "low",
                "description": f"Found {len(file_analysis.cache_files)} cache files",
                "action": "Run cleanup to remove cache files"
            })

        # Stale branches
        if metrics.stale_branches > 0:
            recommendations.append({
                "type": "stale_branches",
                "priority": "medium",
                "description": f"Found {metrics.stale_branches} stale branches",
                "action": "Consider removing unused branches"
            })

        return recommendations

def main():
    """Main CLI interface."""

    parser = argparse.ArgumentParser(description="GitWiz Enhanced v2.0 - Intelligent Git Repository Management")
    parser.add_argument("--repo", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--action", choices=["analyze", "optimize", "branches", "report"],
                        default="report", help="Action to perform")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run (no changes)")

    args = parser.parse_args()

    try:
        gitwiz = GitWizEnhanced(args.repo)

        if args.action == "analyze":
            metrics = gitwiz.analyze_repository()
            print(json.dumps(asdict(metrics), indent=2))

        elif args.action == "optimize":
            result = gitwiz.optimize_repository(dry_run=args.dry_run)
            print(json.dumps(result, indent=2))

        elif args.action == "branches":
            result = gitwiz.manage_branches("analyze")
            print(json.dumps(result, indent=2))

        elif args.action == "report":
            report = gitwiz.generate_report()
            print(f"✅ Report generated: {gitwiz.gitwiz_dir}/health_report_*.json")
            print(f"📊 Health Status: {report['summary']['health_status']}")
            print(f"🗂️  Files: {report['summary']['total_files']}")
            print(f"💾 Size: {report['summary']['total_size_mb']:.1f}MB")
            print(f"⭐ Optimization Score: {report['summary']['optimization_score']:.2f}")

    except Exception as e:
        logger.error(f"GitWiz operation failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
