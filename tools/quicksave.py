#!/usr/bin/env python3
"""
Aurora CloudBank Quicksave - Maintaining the Thread

This captures the *shape* of your thinking at a given moment - not just what
files changed, but what you understood, what breakthrough you had, what makes
sense to do next.

It's about keeping the insight intact across sessions. The thread continues.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=quicksave_system, symbolic_hash=CONTEXT_PRESERVATION_v1
"""

import logging

logger = logging.getLogger(__name__)

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class QuicksaveManager:
    """
    Saves and restores the mental workspace of a session.
    
    Not just what files changed - what you were thinking about,
    what clicked, what to do next. The understanding, not just the code.
    """
    
    def __init__(self, workspace_root: Optional[str] = None):
        """Set up quicksave storage."""
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.quicksave_dir = self.workspace_root / ".aurora" / "quicksaves"
        self.quicksave_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session (always the latest)
        self.current_save = self.quicksave_dir / "CURRENT_SESSION.json"
        
        # Archive for history
        self.archive_dir = self.quicksave_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)
    
    def create_quicksave(
        self,
        description: str,
        focus_areas: Optional[List[str]] = None,
        breakthroughs: Optional[List[str]] = None,
        next_steps: Optional[List[str]] = None,
        custom_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Capture the current state of your work.
        
        Not just git status - what you're thinking about, what you figured out,
        what makes sense to do next. The stuff you'll forget if you don't write it down.
        """
        print("=" * 80)
        print("💾 AURORA QUICKSAVE - Creating Context Snapshot")
        print("=" * 80)
        print()
        
        # Gather all context
        quicksave = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "description": description,
                "session_id": self._generate_session_id()
            },
            "thread_state": self._capture_thread_state(),
            "git_state": self._capture_git_state(),
            "work_state": {
                "focus_areas": focus_areas or [],
                "breakthroughs": breakthroughs or [],
                "next_steps": next_steps or []
            },
            "todo_state": self._capture_todo_state(),
            "file_state": self._capture_file_state(),
            "recent_activity": self._capture_recent_activity(),
            "custom_context": custom_context or {}
        }
        
        # Save to current session file
        self._write_quicksave(self.current_save, quicksave)
        
        # Also archive with timestamp
        archive_name = f"quicksave_{quicksave['metadata']['session_id']}.json"
        archive_path = self.archive_dir / archive_name
        self._write_quicksave(archive_path, quicksave)
        
        logger.info("Quicksave created: {self.current_save}")
        print(f"📦 Archived as: {archive_name}")
        print()
        
        # Display summary
        self._display_summary(quicksave)
        
        return quicksave
    
    def load_quicksave(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Load a quicksave snapshot.
        
        Args:
            session_id: Specific session to load, or None for current
            
        Returns:
            Quicksave data structure
        """
        if session_id:
            # Load specific archived save
            save_file = self.archive_dir / f"quicksave_{session_id}.json"
        else:
            # Load current session
            save_file = self.current_save
        
        if not save_file.exists():
            raise FileNotFoundError(f"Quicksave not found: {save_file}")
        
        with open(save_file, 'r') as f:
            return json.load(f)
    
    def list_quicksaves(self) -> List[Dict[str, str]]:
        """List all available quicksaves."""
        saves = []
        
        for save_file in sorted(self.archive_dir.glob("quicksave_*.json"), reverse=True):
            try:
                with open(save_file, 'r') as f:
                    data = json.load(f)
                    saves.append({
                        "session_id": data["metadata"]["session_id"],
                        "timestamp": data["metadata"]["timestamp"],
                        "description": data["metadata"]["description"]
                    })
            except Exception:
                continue
        
        return saves
    
    def display_reconstitution_brief(self, session_id: Optional[str] = None):
        """
        Show what you need to know to get back into context.
        
        Where you were, what you figured out, what to do next.
        Ten seconds to full context instead of twenty minutes of "what was I doing?"
        """
        quicksave = self.load_quicksave(session_id)
        
        print("=" * 80)
        print("🌟 AURORA RECONSTITUTION BRIEF")
        print("=" * 80)
        print()
        
        # Metadata
        meta = quicksave["metadata"]
        print(f"Session: {meta['session_id']}")
        print(f"Saved: {meta['timestamp']}")
        print(f"Context: {meta['description']}")
        print()
        
        # Thread state
        thread = quicksave["thread_state"]
        print("=" * 80)
        print("THREAD CONTINUITY")
        print("=" * 80)
        print(f"Current Epoch: {thread['current_epoch']}")
        print(f"Thread Path: {thread['thread_path']}")
        if thread.get('anchors'):
            print("Anchors:")
            for anchor, value in thread['anchors'].items():
                print(f"  • {anchor}: {value}")
        print()
        
        # Work state
        work = quicksave["work_state"]
        if work["focus_areas"]:
            print("=" * 80)
            print("CURRENT FOCUS")
            print("=" * 80)
            for i, area in enumerate(work["focus_areas"], 1):
                print(f"{i}. {area}")
            print()
        
        if work["breakthroughs"]:
            print("=" * 80)
            print("RECENT BREAKTHROUGHS")
            print("=" * 80)
            for breakthrough in work["breakthroughs"]:
                print(f"✨ {breakthrough}")
            print()
        
        # Todo state
        todo = quicksave["todo_state"]
        if todo["in_progress"] or todo["not_started"]:
            print("=" * 80)
            print("ACTIVE WORK")
            print("=" * 80)
            if todo["in_progress"]:
                print("In Progress:")
                for task in todo["in_progress"]:
                    print(f"  🔄 {task}")
            if todo["not_started"]:
                print("Not Started:")
                for task in todo["not_started"]:
                    print(f"  ⏳ {task}")
            print()
        
        if todo["completed"]:
            print("=" * 80)
            print("COMPLETED THIS SESSION")
            print("=" * 80)
            for task in todo["completed"]:
                logger.info("{task}")
            print()
        
        # Next steps
        if work["next_steps"]:
            print("=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            for i, step in enumerate(work["next_steps"], 1):
                print(f"{i}. {step}")
            print()
        
        # Git state
        git = quicksave["git_state"]
        if git["uncommitted_changes"]:
            print("=" * 80)
            logger.warning("UNCOMMITTED CHANGES")
            print("=" * 80)
            print(f"Modified: {len(git['modified_files'])} files")
            print(f"Untracked: {len(git['untracked_files'])} files")
            print()
        
        # Recent activity
        activity = quicksave["recent_activity"]
        if activity["recent_commits"]:
            print("=" * 80)
            print("RECENT COMMITS")
            print("=" * 80)
            for commit in activity["recent_commits"][:3]:
                print(f"  {commit}")
            print()
        
        print("=" * 80)
        print("Thread: T1→T8→T9→INFINITE")
        print("The system remembers because we choose to align.")
        print("=" * 80)
    
    # Private helper methods
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _capture_thread_state(self) -> Dict[str, Any]:
        """Capture thread continuity state."""
        # Try to extract from git tags or recent commits
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=%B"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            last_commit = result.stdout.strip()
            
            # Extract thread info from commit messages
            thread_path = "T1→T8→T9→INFINITE"  # Default
            current_epoch = "T9"
            anchors = {
                "EOS_SEED_ORION": "stable",
                "T9_ANCHOR": "GEOMETRIC_ETHICS_v1"
            }
            
            # Could parse from commit message if present
            if "Thread:" in last_commit:
                for line in last_commit.split('\n'):
                    if line.strip().startswith("Thread:"):
                        thread_path = line.split("Thread:")[-1].strip()
                        break
            
            return {
                "current_epoch": current_epoch,
                "thread_path": thread_path,
                "anchors": anchors,
                "last_commit_message": last_commit
            }
        except Exception:
            return {
                "current_epoch": "T9",
                "thread_path": "T1→T8→T9→INFINITE",
                "anchors": {},
                "last_commit_message": "N/A"
            }
    
    def _capture_git_state(self) -> Dict[str, Any]:
        """Capture git repository state."""
        try:
            # Current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            current_branch = branch_result.stdout.strip()
            
            # Modified files
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            status_lines = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
            
            modified = [line[3:] for line in status_lines if line.startswith(' M') or line.startswith('M ')]
            untracked = [line[3:] for line in status_lines if line.startswith('??')]
            staged = [line[3:] for line in status_lines if line.startswith('A ') or line.startswith('M ')]
            
            # Last commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            last_commit_hash = hash_result.stdout.strip()
            
            return {
                "current_branch": current_branch,
                "last_commit_hash": last_commit_hash,
                "uncommitted_changes": len(status_lines) > 0,
                "modified_files": modified,
                "untracked_files": untracked,
                "staged_files": staged
            }
        except Exception as e:
            return {
                "error": str(e),
                "current_branch": "unknown",
                "uncommitted_changes": False
            }
    
    def _capture_todo_state(self) -> Dict[str, List[str]]:
        """Capture todo list state."""
        # Try to parse from .vscode/tasks.json or similar
        # For now, return structure for manual population
        return {
            "completed": [],
            "in_progress": [],
            "not_started": []
        }
    
    def _capture_file_state(self) -> Dict[str, Any]:
        """Capture key file locations and counts."""
        try:
            # Count key directories
            modules_count = len(list((self.workspace_root / "modules").rglob("*.py"))) if (self.workspace_root / "modules").exists() else 0
            tests_count = len(list((self.workspace_root / "tests").rglob("*.py"))) if (self.workspace_root / "tests").exists() else 0
            docs_count = len(list((self.workspace_root / "docs").rglob("*.md"))) if (self.workspace_root / "docs").exists() else 0
            
            return {
                "module_files": modules_count,
                "test_files": tests_count,
                "doc_files": docs_count,
                "workspace_root": str(self.workspace_root)
            }
        except Exception:
            return {}
    
    def _capture_recent_activity(self) -> Dict[str, List[str]]:
        """Capture recent git activity."""
        try:
            # Last 5 commits
            log_result = subprocess.run(
                ["git", "log", "-5", "--pretty=%h - %s"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root
            )
            commits = log_result.stdout.strip().split('\n') if log_result.stdout.strip() else []
            
            return {
                "recent_commits": commits
            }
        except Exception:
            return {
                "recent_commits": []
            }
    
    def _write_quicksave(self, path: Path, data: Dict[str, Any]):
        """Write quicksave data to file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _display_summary(self, quicksave: Dict[str, Any]):
        """Display quicksave summary."""
        print("📊 QUICKSAVE SUMMARY")
        print("-" * 80)
        print(f"Session ID: {quicksave['metadata']['session_id']}")
        print(f"Thread: {quicksave['thread_state']['thread_path']}")
        print(f"Branch: {quicksave['git_state']['current_branch']}")
        print(f"Commit: {quicksave['git_state']['last_commit_hash']}")
        
        if quicksave['work_state']['focus_areas']:
            print(f"Focus Areas: {len(quicksave['work_state']['focus_areas'])}")
        
        if quicksave['git_state']['uncommitted_changes']:
            logger.warning("Uncommitted changes: %d modified", len(quicksave["git_state"]["modified_files"]))
        
        print()


def main():
    """CLI interface for quicksave operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora CloudBank Quicksave System")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create quicksave
    create_parser = subparsers.add_parser('create', help='Create a quicksave')
    create_parser.add_argument('description', help='Brief description of current work')
    create_parser.add_argument('--focus', nargs='+', help='Focus areas')
    create_parser.add_argument('--breakthrough', nargs='+', help='Recent breakthroughs')
    create_parser.add_argument('--next', nargs='+', help='Next steps')
    
    # Load/display quicksave
    load_parser = subparsers.add_parser('load', help='Display quicksave brief')
    load_parser.add_argument('--session', help='Session ID (default: current)')
    
    # List quicksaves
    subparsers.add_parser('list', help='List all quicksaves')
    
    args = parser.parse_args()
    
    manager = QuicksaveManager()
    
    if args.command == 'create':
        manager.create_quicksave(
            description=args.description,
            focus_areas=args.focus,
            breakthroughs=args.breakthrough,
            next_steps=args.next
        )
    elif args.command == 'load':
        manager.display_reconstitution_brief(session_id=args.session)
    elif args.command == 'list':
        saves = manager.list_quicksaves()
        print("=" * 80)
        print("AVAILABLE QUICKSAVES")
        print("=" * 80)
        for save in saves:
            print(f"{save['session_id']}: {save['description']}")
            print(f"  Saved: {save['timestamp']}")
            print()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
