"""
Anchor Propagation Module - Thread Transfer Bridge v2
====================================================

Git notes-based anchor propagation for cross-repository thread continuity.

Features:
- Anchor storage in Git notes (refs/notes/aurora/anchors)
- Cross-repository anchor synchronization
- Anchor validation and verification
- Anchor history tracking
- Conflict resolution for anchor propagation

Thread: T1→BRIDGE_V2→ANCHOR_PROP
DLP: context_tag=bridge_v2_anchor_propagation
Anchor: EOS_SEED_ORION_v2
Ethics: Picard_Delta_3_Extended
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class AnchorRecord:
    """Anchor record for Git notes storage."""
    anchor_hash: str
    thread_id: str
    timestamp: datetime
    repo_id: str
    branch: str
    commit_sha: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "anchor_hash": self.anchor_hash,
            "thread_id": self.thread_id,
            "timestamp": self.timestamp.isoformat(),
            "repo_id": self.repo_id,
            "branch": self.branch,
            "commit_sha": self.commit_sha,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnchorRecord":
        """Create from dictionary."""
        return cls(
            anchor_hash=data["anchor_hash"],
            thread_id=data["thread_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            repo_id=data["repo_id"],
            branch=data["branch"],
            commit_sha=data["commit_sha"],
            metadata=data.get("metadata", {})
        )


class AnchorPropagationError(Exception):
    """Anchor propagation error."""
    pass


class AnchorPropagator:
    """
    Anchor propagation manager.
    
    Handles propagation of thread anchors across repositories using Git notes.
    Ensures anchor integrity and resolves conflicts.
    """
    
    NOTES_REF = "refs/notes/aurora/anchors"
    
    def __init__(self):
        """Initialize anchor propagator."""
        self._propagation_lock = asyncio.Lock()

    async def write_anchor(
        self,
        repo_path: str,
        anchor_hash: str,
        thread_id: str,
        repo_id: str,
        branch: str = "main",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnchorRecord:
        """
        Write anchor to Git notes.

        Args:
            repo_path: Repository path
            anchor_hash: Anchor hash to write
            thread_id: Thread identifier
            repo_id: Repository identifier
            branch: Git branch
            metadata: Optional metadata

        Returns:
            AnchorRecord

        Raises:
            AnchorPropagationError: If write fails
        """
        async with self._propagation_lock:
            try:
                # Get current commit SHA
                commit_sha = await self._get_commit_sha(repo_path, branch)
                
                # Create anchor record
                record = AnchorRecord(
                    anchor_hash=anchor_hash,
                    thread_id=thread_id,
                    timestamp=datetime.now(),
                    repo_id=repo_id,
                    branch=branch,
                    commit_sha=commit_sha,
                    metadata=metadata or {}
                )
                
                # Write to Git notes
                notes_data = json.dumps(record.to_dict(), indent=2)
                
                result = await self._run_git_command(
                    repo_path,
                    ["notes", "--ref", self.NOTES_REF, "add", "-f", "-m", notes_data, commit_sha]
                )
                
                if not result["success"]:
                    raise AnchorPropagationError(
                        f"Failed to write anchor: {result['error']}"
                    )
                
                logger.info(
                    f"Wrote anchor {anchor_hash} to {repo_id}:{branch} at {commit_sha}"
                )
                
                return record
                
            except Exception as e:
                raise AnchorPropagationError(f"Anchor write failed: {e}")

    async def read_anchor(
        self,
        repo_path: str,
        branch: str = "main",
        commit_sha: Optional[str] = None
    ) -> Optional[AnchorRecord]:
        """
        Read anchor from Git notes.

        Args:
            repo_path: Repository path
            branch: Git branch
            commit_sha: Optional specific commit SHA (defaults to HEAD)

        Returns:
            AnchorRecord if found, None otherwise
        """
        try:
            if not commit_sha:
                commit_sha = await self._get_commit_sha(repo_path, branch)
            
            result = await self._run_git_command(
                repo_path,
                ["notes", "--ref", self.NOTES_REF, "show", commit_sha]
            )
            
            if not result["success"] or not result["output"]:
                return None
            
            try:
                notes_data = json.loads(result["output"])
                return AnchorRecord.from_dict(notes_data)
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Invalid anchor notes data: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to read anchor: {e}")
            return None

    async def propagate_anchor(
        self,
        source_repo_path: str,
        target_repo_path: str,
        thread_id: str,
        target_repo_id: str,
        source_branch: str = "main",
        target_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Propagate anchor from source to target repository.

        Args:
            source_repo_path: Source repository path
            target_repo_path: Target repository path
            thread_id: Thread identifier
            target_repo_id: Target repository identifier
            source_branch: Source branch
            target_branch: Target branch

        Returns:
            Propagation result with status and details
        """
        try:
            # Read anchor from source
            source_anchor = await self.read_anchor(source_repo_path, source_branch)
            
            if not source_anchor:
                return {
                    "success": False,
                    "error": "No anchor found in source repository"
                }
            
            # Validate thread ID matches
            if source_anchor.thread_id != thread_id:
                return {
                    "success": False,
                    "error": f"Thread ID mismatch: expected {thread_id}, got {source_anchor.thread_id}"
                }
            
            # Check for existing anchor in target
            target_anchor = await self.read_anchor(target_repo_path, target_branch)
            
            if target_anchor:
                # Validate anchor compatibility
                if not await self._validate_anchor_compatibility(source_anchor, target_anchor):
                    return {
                        "success": False,
                        "error": "Anchor conflict detected",
                        "source_anchor": source_anchor.anchor_hash,
                        "target_anchor": target_anchor.anchor_hash
                    }
            
            # Write anchor to target
            new_anchor = await self.write_anchor(
                target_repo_path,
                source_anchor.anchor_hash,
                thread_id,
                target_repo_id,
                target_branch,
                metadata={
                    "propagated_from": source_anchor.repo_id,
                    "propagation_timestamp": datetime.now().isoformat(),
                    "source_commit": source_anchor.commit_sha
                }
            )
            
            logger.info(
                f"Propagated anchor {source_anchor.anchor_hash} from "
                f"{source_anchor.repo_id} to {target_repo_id}"
            )
            
            return {
                "success": True,
                "anchor_hash": new_anchor.anchor_hash,
                "source_repo": source_anchor.repo_id,
                "target_repo": target_repo_id,
                "propagation_time": new_anchor.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Anchor propagation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_anchor_history(
        self,
        repo_path: str,
        branch: str = "main",
        limit: int = 10
    ) -> List[AnchorRecord]:
        """
        List anchor history from Git notes.

        Args:
            repo_path: Repository path
            branch: Git branch
            limit: Maximum number of records to return

        Returns:
            List of AnchorRecord objects
        """
        try:
            # Get commit history
            result = await self._run_git_command(
                repo_path,
                ["log", f"--max-count={limit}", "--format=%H", branch]
            )
            
            if not result["success"] or not result["output"]:
                return []
            
            commit_shas = result["output"].strip().split("\n")
            
            # Read anchors for each commit
            anchors = []
            for commit_sha in commit_shas:
                anchor = await self.read_anchor(repo_path, branch, commit_sha)
                if anchor:
                    anchors.append(anchor)
            
            return anchors
            
        except Exception as e:
            logger.error(f"Failed to list anchor history: {e}")
            return []

    async def verify_anchor_integrity(
        self,
        repo_path: str,
        anchor_hash: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Verify anchor integrity.

        Args:
            repo_path: Repository path
            anchor_hash: Expected anchor hash
            branch: Git branch

        Returns:
            Verification result with status and details
        """
        try:
            # Read current anchor
            current_anchor = await self.read_anchor(repo_path, branch)
            
            if not current_anchor:
                return {
                    "valid": False,
                    "error": "No anchor found"
                }
            
            # Compare hashes
            if current_anchor.anchor_hash != anchor_hash:
                return {
                    "valid": False,
                    "error": "Anchor hash mismatch",
                    "expected": anchor_hash,
                    "actual": current_anchor.anchor_hash
                }
            
            # Verify anchor hash computation
            computed_hash = await self._compute_anchor_hash(current_anchor)
            
            if computed_hash != anchor_hash:
                return {
                    "valid": False,
                    "error": "Anchor hash verification failed",
                    "expected": anchor_hash,
                    "computed": computed_hash
                }
            
            return {
                "valid": True,
                "anchor_hash": anchor_hash,
                "thread_id": current_anchor.thread_id,
                "timestamp": current_anchor.timestamp.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Anchor verification failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }

    async def _validate_anchor_compatibility(
        self,
        source: AnchorRecord,
        target: AnchorRecord
    ) -> bool:
        """
        Validate that source and target anchors are compatible.
        
        Compatible means they can be merged or one supersedes the other.
        """
        # Same anchor hash - always compatible
        if source.anchor_hash == target.anchor_hash:
            return True
        
        # Same thread - check timestamps
        if source.thread_id == target.thread_id:
            # Newer anchor supersedes older
            return source.timestamp >= target.timestamp
        
        # Different threads - not compatible
        return False

    async def _compute_anchor_hash(self, anchor: AnchorRecord) -> str:
        """Compute anchor hash for verification."""
        hash_input = f"{anchor.thread_id}:{anchor.timestamp.isoformat()}:{anchor.commit_sha}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    async def _get_commit_sha(self, repo_path: str, branch: str) -> str:
        """Get current commit SHA for branch."""
        result = await self._run_git_command(
            repo_path,
            ["rev-parse", branch]
        )
        
        if not result["success"]:
            raise AnchorPropagationError(
                f"Failed to get commit SHA: {result['error']}"
            )
        
        return result["output"].strip()

    async def _run_git_command(
        self,
        repo_path: str,
        args: List[str]
    ) -> Dict[str, Any]:
        """Run a Git command."""
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


# Global propagator instance
_propagator = None


def get_anchor_propagator() -> AnchorPropagator:
    """Get global anchor propagator instance."""
    global _propagator
    if _propagator is None:
        _propagator = AnchorPropagator()
    return _propagator
