"""
Repository Synchronization Module - Thread Transfer Bridge v2
=============================================================

Git-based repository synchronization for cross-repository thread continuity.

Features:
- Git repository management and validation
- Anchor propagation via Git notes
- Repository state synchronization
- Conflict detection and resolution
- Bidirectional sync support

Thread: T1→BRIDGE_V2→REPO_SYNC
DLP: context_tag=bridge_v2_repo_sync
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """Repository synchronization status."""
    SYNCED = "synced"
    SYNCING = "syncing"
    CONFLICT = "conflict"
    ERROR = "error"
    UNKNOWN = "unknown"


class SyncDirection(Enum):
    """Synchronization direction."""
    PUSH = "push"
    PULL = "pull"
    BIDIRECTIONAL = "bidirectional"


@dataclass
class RepositoryInfo:
    """Repository information for synchronization."""
    repo_id: str
    repo_path: str
    remote_url: Optional[str] = None
    branch: str = "main"
    last_sync: Optional[datetime] = None
    sync_status: SyncStatus = SyncStatus.UNKNOWN
    anchor_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "repo_id": self.repo_id,
            "repo_path": self.repo_path,
            "remote_url": self.remote_url,
            "branch": self.branch,
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "sync_status": self.sync_status.value,
            "anchor_hash": self.anchor_hash,
            "metadata": self.metadata
        }


class GitOperationError(Exception):
    """Git operation error."""
    pass


class RepositorySynchronizer:
    """
    Repository synchronization manager.
    
    Handles Git-based synchronization between repositories for thread continuity.
    Uses Git notes to propagate anchors and thread state.
    """

    def __init__(self):
        """Initialize repository synchronizer."""
        self.repositories: Dict[str, RepositoryInfo] = {}
        self._sync_lock = asyncio.Lock()

    async def register_repository(
        self,
        repo_id: str,
        repo_path: str,
        remote_url: Optional[str] = None,
        branch: str = "main"
    ) -> RepositoryInfo:
        """
        Register a repository for synchronization.

        Args:
            repo_id: Unique repository identifier
            repo_path: Local path to repository
            remote_url: Optional remote repository URL
            branch: Git branch to sync (default: main)

        Returns:
            RepositoryInfo object

        Raises:
            GitOperationError: If repository is invalid
        """
        repo_path_obj = Path(repo_path)
        
        if not repo_path_obj.exists():
            raise GitOperationError(f"Repository path does not exist: {repo_path}")
        
        if not (repo_path_obj / ".git").exists():
            raise GitOperationError(f"Not a Git repository: {repo_path}")
        
        # Validate branch exists
        try:
            result = await self._run_git_command(
                repo_path,
                ["rev-parse", "--verify", branch]
            )
            if not result["success"]:
                raise GitOperationError(f"Branch '{branch}' does not exist")
        except Exception as e:
            raise GitOperationError(f"Failed to validate branch: {e}")
        
        # Get current anchor hash from Git notes
        anchor_hash = await self._read_anchor_from_notes(repo_path, branch)
        
        repo_info = RepositoryInfo(
            repo_id=repo_id,
            repo_path=repo_path,
            remote_url=remote_url,
            branch=branch,
            anchor_hash=anchor_hash,
            sync_status=SyncStatus.SYNCED
        )
        
        self.repositories[repo_id] = repo_info
        logger.info(f"Registered repository: {repo_id} at {repo_path}")
        
        return repo_info

    async def unregister_repository(self, repo_id: str) -> bool:
        """
        Unregister a repository.

        Args:
            repo_id: Repository identifier

        Returns:
            True if unregistered, False if not found
        """
        if repo_id in self.repositories:
            del self.repositories[repo_id]
            logger.info(f"Unregistered repository: {repo_id}")
            return True
        return False

    async def sync_repository(
        self,
        repo_id: str,
        direction: SyncDirection = SyncDirection.BIDIRECTIONAL,
        auto_resolve_conflicts: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronize a repository.

        Args:
            repo_id: Repository identifier
            direction: Sync direction (push/pull/bidirectional)
            auto_resolve_conflicts: Automatically resolve conflicts if possible

        Returns:
            Sync result with status and details
        """
        if repo_id not in self.repositories:
            return {
                "success": False,
                "error": f"Repository not registered: {repo_id}"
            }
        
        repo = self.repositories[repo_id]
        
        async with self._sync_lock:
            try:
                repo.sync_status = SyncStatus.SYNCING
                
                # Fetch latest changes
                if direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
                    fetch_result = await self._fetch_remote(repo)
                    if not fetch_result["success"]:
                        repo.sync_status = SyncStatus.ERROR
                        return fetch_result
                
                # Check for conflicts
                conflicts = await self._check_conflicts(repo)
                if conflicts:
                    if auto_resolve_conflicts:
                        resolve_result = await self._resolve_conflicts(repo, conflicts)
                        if not resolve_result["success"]:
                            repo.sync_status = SyncStatus.CONFLICT
                            return resolve_result
                    else:
                        repo.sync_status = SyncStatus.CONFLICT
                        return {
                            "success": False,
                            "status": "conflict",
                            "conflicts": conflicts
                        }
                
                # Pull changes
                if direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
                    pull_result = await self._pull_changes(repo)
                    if not pull_result["success"]:
                        repo.sync_status = SyncStatus.ERROR
                        return pull_result
                
                # Push changes
                if direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
                    push_result = await self._push_changes(repo)
                    if not push_result["success"]:
                        repo.sync_status = SyncStatus.ERROR
                        return push_result
                
                # Update sync timestamp and status
                repo.last_sync = datetime.now()
                repo.sync_status = SyncStatus.SYNCED
                
                # Re-read anchor hash after sync
                repo.anchor_hash = await self._read_anchor_from_notes(
                    repo.repo_path,
                    repo.branch
                )
                
                logger.info(f"Successfully synced repository: {repo_id}")
                
                return {
                    "success": True,
                    "status": "synced",
                    "repo_id": repo_id,
                    "last_sync": repo.last_sync.isoformat(),
                    "anchor_hash": repo.anchor_hash
                }
                
            except Exception as e:
                repo.sync_status = SyncStatus.ERROR
                logger.error(f"Sync failed for {repo_id}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    async def _fetch_remote(self, repo: RepositoryInfo) -> Dict[str, Any]:
        """Fetch changes from remote."""
        if not repo.remote_url:
            return {"success": True}  # No remote to fetch from
        
        result = await self._run_git_command(
            repo.repo_path,
            ["fetch", "origin", repo.branch]
        )
        return result

    async def _pull_changes(self, repo: RepositoryInfo) -> Dict[str, Any]:
        """Pull changes from remote."""
        if not repo.remote_url:
            return {"success": True}  # No remote to pull from
        
        result = await self._run_git_command(
            repo.repo_path,
            ["pull", "origin", repo.branch]
        )
        return result

    async def _push_changes(self, repo: RepositoryInfo) -> Dict[str, Any]:
        """Push changes to remote."""
        if not repo.remote_url:
            return {"success": True}  # No remote to push to
        
        # Push commits
        result = await self._run_git_command(
            repo.repo_path,
            ["push", "origin", repo.branch]
        )
        
        if not result["success"]:
            return result
        
        # Push notes
        notes_result = await self._run_git_command(
            repo.repo_path,
            ["push", "origin", "refs/notes/aurora/*"]
        )
        
        return notes_result

    async def _check_conflicts(self, repo: RepositoryInfo) -> List[str]:
        """Check for merge conflicts."""
        result = await self._run_git_command(
            repo.repo_path,
            ["diff", "--name-only", "--diff-filter=U"]
        )
        
        if result["success"] and result["output"]:
            return result["output"].strip().split("\n")
        
        return []

    async def _resolve_conflicts(
        self,
        repo: RepositoryInfo,
        conflicts: List[str]
    ) -> Dict[str, Any]:
        """
        Attempt to resolve conflicts automatically.
        
        Uses "ours" strategy for anchor files, "theirs" for other files.
        """
        for conflict_file in conflicts:
            if "anchor" in conflict_file.lower() or "notes" in conflict_file.lower():
                # Use our version for anchor files
                strategy = "ours"
            else:
                # Use their version for other files
                strategy = "theirs"
            
            result = await self._run_git_command(
                repo.repo_path,
                ["checkout", f"--{strategy}", conflict_file]
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to resolve conflict in {conflict_file}"
                }
            
            # Stage resolved file
            await self._run_git_command(
                repo.repo_path,
                ["add", conflict_file]
            )
        
        return {"success": True}

    async def _read_anchor_from_notes(
        self,
        repo_path: str,
        branch: str
    ) -> Optional[str]:
        """Read anchor hash from Git notes."""
        result = await self._run_git_command(
            repo_path,
            ["notes", "--ref=aurora/anchors", "show", branch]
        )
        
        if result["success"] and result["output"]:
            try:
                notes_data = json.loads(result["output"])
                return notes_data.get("anchor_hash")
            except json.JSONDecodeError:
                return None
        
        return None

    async def _run_git_command(
        self,
        repo_path: str,
        args: List[str]
    ) -> Dict[str, Any]:
        """
        Run a Git command.

        Args:
            repo_path: Repository path
            args: Git command arguments

        Returns:
            Result dictionary with success, output, and error
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode("utf-8"),
                "error": stderr.decode("utf-8"),
                "returncode": process.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }

    def get_repository(self, repo_id: str) -> Optional[RepositoryInfo]:
        """Get repository information."""
        return self.repositories.get(repo_id)

    def list_repositories(
        self,
        status: Optional[SyncStatus] = None
    ) -> List[RepositoryInfo]:
        """
        List registered repositories.

        Args:
            status: Optional status filter

        Returns:
            List of repository information
        """
        repos = list(self.repositories.values())
        
        if status:
            repos = [r for r in repos if r.sync_status == status]
        
        return repos


# Global synchronizer instance
_synchronizer = None


def get_repository_synchronizer() -> RepositorySynchronizer:
    """Get global repository synchronizer instance."""
    global _synchronizer
    if _synchronizer is None:
        _synchronizer = RepositorySynchronizer()
    return _synchronizer
