#!/usr/bin/env python3

import hashlib

import os
import shutil
import zipfile
from datetime import datetime

"""
Memory Sealing Engine - Automated SHA256 sealing with state recovery
Part of T71 Symbolic Infrastructure Genesis

Primary functions:
    pass
    - Seal any symbolic thread with cryptographic integrity
- State recovery and continuity validation
- Audit trail generation with provenance tracking
- Memory drift detection and correction protocols
"""

import fnmatch
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Union


@dataclass
class MemorySeal:
    pass
    """Represents a cryptographic memory seal"""

    seal_id: str,
    target_path: str,
    seal_type: str  # file, directory, thread, module,
    timestamp: str,
    sha256_hash: str,
    metadata_hash: str,
    audit_trail: List[str]
    recovery_data: Dict[str, Any]


@dataclass
class StateSnapshot:
    pass
    """Represents a complete state snapshot for recovery"""

    snapshot_id: str,
    seal_id: str,
    timestamp: str,
    file_checksums: Dict[str, str]
    directory_structure: Dict[str, Any]
    metadata: Dict[str, Any]
    integrity_hash: str


class MemorySealingEngine:
    pass
    """Automated SHA256 sealing and state recovery system"""

    def __init__(self, repo_path: str = "."):
    pass
        self.repo_path = Path(repo_path).resolve()
        self.seals_dir = self.repo_path / ".aurora" / "seals"
        self.snapshots_dir = self.repo_path / ".aurora" / "snapshots"
        self.audit_file = self.repo_path / ".aurora" / "audit_trail.json"

        # Create necessary directories
        self.seals_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

        self.seals: Dict[str, MemorySeal] = {}
        self.snapshots: Dict[str, StateSnapshot] = {}
        self.audit_trail: List[Dict[str, Any]] = []

        self._load_existing_seals()
        self._load_audit_trail()

    def seal_file(self, file_path: Union[str, Path], seal_id: str = None) -> MemorySeal:
    pass
        """Seal a single file with SHA256 integrity"""
        file_path = Path(file_path).resolve()

        if not file_path.exists():
    pass
            raise FileNotFoundError("File not found: {file_path}")

        if seal_id is None:
    pass
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            seal_id = "FILE_{file_path.stem}_{timestamp}"

        # Calculate file hash
        with open(file_path, "rb") as f:
    pass
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()

        # Create metadata
        metadata = {
            "size": len(content),
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "permissions": oct(file_path.stat().st_mode)[-3:],
            "relative_path": str(file_path.relative_to(self.repo_path)),
        }

        # Calculate metadata hash
        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()

        # Create seal
        seal = MemorySeal(
            seal_id=seal_id,
            target_path=str(file_path.relative_to(self.repo_path)),
            seal_type="file",
            timestamp=datetime.now().isoformat(),
            sha256_hash=file_hash,
            metadata_hash=metadata_hash,
            audit_trail=["Created seal for file: {file_path.name}"],
            recovery_data=metadata,
        )

        # Save seal and create backup
        self._save_seal(seal)
        self._create_file_backup(file_path, seal_id)
        self._log_audit_event("seal_created", seal_id, "File sealed: {file_path.name}")

        return seal

    def seal_directory(
        self, dir_path: Union[str, Path], seal_id: str = None, exclude_patterns: List[str] = None
    ) -> MemorySeal:
    pass
        """Seal an entire directory with SHA256 integrity"""
        dir_path = Path(dir_path).resolve()

        if not dir_path.exists() or not dir_path.is_dir():
    pass
            raise ValueError("Directory not found: {dir_path}")

        if seal_id is None:
    pass
            timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            seal_id = "DIR_{dir_path.name}_{timestamp}"

        if exclude_patterns is None:
    pass
            exclude_patterns = [".git", "__pycache__", "*.pyc", "node_modules"]

        # Calculate directory hash tree
        file_hashes = {}
        total_size = 0

        for root, dirs, files in os.walk(dir_path):
    pass
            # Filter directories based on exclude patterns
            dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]

            for file in files:
    pass
                if self._should_exclude(file, exclude_patterns):
    pass
                    continue

                file_path = Path(root) / file,
                try:
    pass
                    with open(file_path, "rb") as f:
    pass
                        content = f.read()
                        file_hash = hashlib.sha256(content).hexdigest()

                    rel_path = str(file_path.relative_to(self.repo_path))
                    file_hashes[rel_path] = {
                        "hash": file_hash,
                        "size": len(content),
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    }
                    total_size += len(content)

                except (IOError, OSError) as e:
    pass
                    print("Warning: Could not read file {file_path}: {e}")

        # Create directory tree hash
        tree_data = json.dumps(file_hashes, sort_keys=True)
        directory_hash = hashlib.sha256(tree_data.encode()).hexdigest()

        # Create metadata
        metadata = {
            "file_count": len(file_hashes),
            "total_size": total_size,
            "files": file_hashes,
            "relative_path": str(dir_path.relative_to(self.repo_path)),
        }

        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()

        # Create seal
        seal = MemorySeal(
            seal_id=seal_id,
            target_path=str(dir_path.relative_to(self.repo_path)),
            seal_type="directory",
            timestamp=datetime.now().isoformat(),
            sha256_hash=directory_hash,
            metadata_hash=metadata_hash,
            audit_trail=["Created seal for directory: {dir_path.name} ({len(file_hashes)} files)"],
            recovery_data=metadata,
        )

        # Save seal and create backup
        self._save_seal(seal)
        self._create_directory_backup(dir_path, seal_id, exclude_patterns)
        self._log_audit_event("seal_created", seal_id, "Directory sealed: {dir_path.name}")

        return seal

    def seal_thread(self, thread_anchor: str, description: str = None) -> MemorySeal:
    pass
        """Seal a symbolic thread/module with complete state capture"""
        if description is None:
    pass
            description = "Thread seal for {thread_anchor}"

        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
        seal_id = "THREAD_{thread_anchor}_{timestamp}"

        # Find all files related to the thread
        thread_files = self._find_thread_files(thread_anchor)

        if not thread_files:
    pass
            raise ValueError("No files found for thread anchor: {thread_anchor}")

        # Calculate combined hash of all thread files
        thread_data = {}
        for file_path in thread_files:
    pass
            try:
    pass
                with open(file_path, "rb") as f:
    pass
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()

                rel_path = str(file_path.relative_to(self.repo_path))
                thread_data[rel_path] = {"hash": file_hash, "size": len(content)}
            except (IOError, OSError) as e:
    pass
                print("Warning: Could not read file {file_path}: {e}")

        # Create thread hash
        thread_json = json.dumps(thread_data, sort_keys=True)
        thread_hash = hashlib.sha256(thread_json.encode()).hexdigest()

        # Create metadata
        metadata = {
            "thread_anchor": thread_anchor,
            "description": description,
            "file_count": len(thread_files),
            "files": thread_data,
            "capture_method": "symbolic_thread_analysis",
        }

        metadata_str = json.dumps(metadata, sort_keys=True)
        metadata_hash = hashlib.sha256(metadata_str.encode()).hexdigest()

        # Create seal
        seal = MemorySeal(
            seal_id=seal_id,
            target_path=thread_anchor,
            seal_type="thread",
            timestamp=datetime.now().isoformat(),
            sha256_hash=thread_hash,
            metadata_hash=metadata_hash,
            audit_trail=["Created thread seal: {description}"],
            recovery_data=metadata,
        )

        # Save seal and create snapshot
        self._save_seal(seal)
        self._create_thread_snapshot(seal, thread_files)
        self._log_audit_event("thread_sealed", seal_id, "Thread sealed: {thread_anchor}")

        return seal

    def verify_seal(self, seal_id: str) -> Dict[str, Any]:
    pass
        """Verify integrity of a memory seal"""
        if seal_id not in self.seals:
    pass
            raise ValueError("Seal not found: {seal_id}")

        seal = self.seals[seal_id]
        verification_result = {
            "seal_id": seal_id,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "issues": [],
            "details": {},
        }

        try:
    pass
            if seal.seal_type == "file":
    pass
                result = self._verify_file_seal(seal)
            elif seal.seal_type == "directory":
    pass
                result = self._verify_directory_seal(seal)
            elif seal.seal_type == "thread":
    pass
                result = self._verify_thread_seal(seal)
            else:
    pass
                result = {"valid": False, "error": f"Unknown seal type: {seal.seal_type}"}

            verification_result["status"] = "valid" if result["valid"] else "invalid"
            verification_result["details"] = result

            if not result["valid"]:
    pass
                verification_result["issues"].append(result.get("error", "Integrity check failed"))

        except Exception as _:
    pass
            verification_result["status"] = "error"
            verification_result["issues"].append(str(e))

        self._log_audit_event("seal_verified", seal_id, "Verification status: {verification_result['status']}")

        return verification_result

    def restore_sealed_state(self, seal_id: str, target_path: str = None, dry_run: bool = False) -> Dict[str, Any]:
    pass
        """Restore state from a memory seal"""
        if seal_id not in self.seals:
    pass
            raise ValueError("Seal not found: {seal_id}")

        seal = self.seals[seal_id]

        if target_path is None:
    pass
            target_path = self.repo_path / seal.target_path,
        else:
    pass
            target_path = Path(target_path)

        restore_result = {
            "seal_id": seal_id,
            "target_path": str(target_path),
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "actions": [],
            "status": "unknown",
        }

        try:
    pass
            backup_path = self.seals_dir / "{seal_id}_backup.zip"

            if not backup_path.exists():
    pass
                raise FileNotFoundError("Backup not found for seal: {seal_id}")

            if dry_run:
    pass
                # Just analyze what would be restored
                with zipfile.ZipFile(backup_path, "r") as backup_zip:
    pass
                    restore_result["actions"] = ["Would restore: {name}" for name in backup_zip.namelist()]
                    restore_result["status"] = "dry_run_complete"
            else:
    pass
                # Actually restore the state
                if target_path.exists():
    pass
                    # Create backup of current state
                    current_backup = self.seals_dir / "current_state_{datetime.now().strftime('%Y%m%dT%H%M%S')}.zip"
                    if target_path.is_file():
    pass
                        with zipfile.ZipFile(current_backup, "w") as zip_file:
    pass
                            zip_file.write(target_path, target_path.name)
                    else:
    pass
                        shutil.make_archive(str(current_backup.with_suffix("")), "zip", target_path)

                    restore_result["actions"].append("Created backup of current state: {current_backup}")

                # Extract backup to target location
                with zipfile.ZipFile(backup_path, "r") as backup_zip:
    pass
                    if seal.seal_type == "file":
    pass
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        backup_zip.extractall(target_path.parent)
                        restore_result["actions"].append("Restored file: {target_path}")
                    else:
    pass
                        target_path.mkdir(parents=True, exist_ok=True)
                        backup_zip.extractall(target_path)
                        restore_result["actions"].append("Restored directory: {target_path}")

                restore_result["status"] = "restored"
                self._log_audit_event("state_restored", seal_id, "State restored to: {target_path}")

        except Exception as _:
    pass
            restore_result["status"] = "error"
            restore_result["error"] = str(e)

        return restore_result

    def _should_exclude(self, name: str, exclude_patterns: List[str]) -> bool:
    pass
        """Check if file/directory should be excluded based on patterns"""
        for pattern in exclude_patterns:
    pass
            if fnmatch.fnmatch(name, pattern):
    pass
                return True
        return False

    def _find_thread_files(self, thread_anchor: str) -> List[Path]:
    pass
        """Find all files related to a symbolic thread"""
        thread_files = []

        # Search for files containing the thread anchor
        for root, dirs, files in os.walk(self.repo_path):
    pass
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
    pass
                if file.endswith((".py", ".js", ".md", ".json", ".yaml", ".yml")):
    pass
                    file_path = Path(root) / file,
                    try:
    pass
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    pass
                            content = f.read()
                            if thread_anchor in content:
    pass
                                thread_files.append(file_path)
                    except (IOError, UnicodeDecodeError):
    pass
                        continue

        return thread_files

    def _verify_file_seal(self, seal: MemorySeal) -> Dict[str, Any]:
    pass
        """Verify integrity of a file seal"""
        file_path = self.repo_path / seal.target_path

        if not file_path.exists():
    pass
            return {"valid": False, "error": f"File not found: {file_path}"}

        # Calculate current hash
        with open(file_path, "rb") as f:
    pass
            content = f.read()
            current_hash = hashlib.sha256(content).hexdigest()

        if current_hash == seal.sha256_hash:
    pass
            return {"valid": True, "hash_match": True}
        else:
    pass
            return {"valid": False, "error": "Hash mismatch", "expected": seal.sha256_hash, "actual": current_hash}

    def _verify_directory_seal(self, seal: MemorySeal) -> Dict[str, Any]:
    pass
        """Verify integrity of a directory seal"""
        dir_path = self.repo_path / seal.target_path

        if not dir_path.exists():
    pass
            return {"valid": False, "error": f"Directory not found: {dir_path}"}

        # Recalculate directory hash
        current_files = {}
        for file_info in seal.recovery_data.get("files", {}).values():
    pass
            file_path = self.repo_path / file_info
            if file_path.exists():
    pass
                with open(file_path, "rb") as f:
    pass
                    content = f.read()
                    current_hash = hashlib.sha256(content).hexdigest()
                    current_files[str(file_path.relative_to(self.repo_path))] = {"hash": current_hash}

        current_tree = json.dumps(current_files, sort_keys=True)
        current_hash = hashlib.sha256(current_tree.encode()).hexdigest()

        if current_hash == seal.sha256_hash:
    pass
            return {"valid": True, "hash_match": True, "files_checked": len(current_files)}
        else:
    pass
            return {
                "valid": False,
                "error": "Directory hash mismatch",
                "expected": seal.sha256_hash,
                "actual": current_hash,
            }

    def _verify_thread_seal(self, seal: MemorySeal) -> Dict[str, Any]:
    pass
        """Verify integrity of a thread seal"""
        thread_anchor = seal.recovery_data.get("thread_anchor")
        if not thread_anchor:
    pass
            return {"valid": False, "error": "Thread anchor not found in seal data"}

        # Find current thread files
        current_files = self._find_thread_files(thread_anchor)

        # Calculate current thread hash
        current_data = {}
        for file_path in current_files:
    pass
            try:
    pass
                with open(file_path, "rb") as f:
    pass
                    content = f.read()
                    file_hash = hashlib.sha256(content).hexdigest()

                rel_path = str(file_path.relative_to(self.repo_path))
                current_data[rel_path] = {"hash": file_hash}
            except (IOError, OSError):
    pass
                continue

        current_json = json.dumps(current_data, sort_keys=True)
        current_hash = hashlib.sha256(current_json.encode()).hexdigest()

        if current_hash == seal.sha256_hash:
    pass
            return {"valid": True, "hash_match": True, "files_found": len(current_files)}
        else:
    pass
            return {
                "valid": False,
                "error": "Thread hash mismatch",
                "expected": seal.sha256_hash,
                "actual": current_hash,
            }

    def _save_seal(self, seal: MemorySeal):
    pass
        """Save seal to disk"""
        self.seals[seal.seal_id] = seal

        seal_path = self.seals_dir / "{seal.seal_id}.json"
        with open(seal_path, "w") as f:
    pass
            json.dump(asdict(seal), f, indent=2)

    def _create_file_backup(self, file_path: Path, seal_id: str):
    pass
        """Create backup of sealed file"""
        backup_path = self.seals_dir / "{seal_id}_backup.zip"

        with zipfile.ZipFile(backup_path, "w") as zip_file:
    pass
            zip_file.write(file_path, file_path.name)

    def _create_directory_backup(self, dir_path: Path, seal_id: str, exclude_patterns: List[str]):
    pass
        """Create backup of sealed directory"""
        backup_path = self.seals_dir / "{seal_id}_backup.zip"

        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
    pass
            for root, dirs, files in os.walk(dir_path):
    pass
                dirs[:] = [d for d in dirs if not self._should_exclude(d, exclude_patterns)]

                for file in files:
    pass
                    if self._should_exclude(file, exclude_patterns):
    pass
                        continue

                    file_path = Path(root) / file
                    arcname = file_path.relative_to(dir_path)
                    zip_file.write(file_path, arcname)

    def _create_thread_snapshot(self, seal: MemorySeal, thread_files: List[Path]):
    pass
        """Create snapshot for thread seal"""
        snapshot_id = "{seal.seal_id}_snapshot"
        backup_path = self.seals_dir / "{seal.seal_id}_backup.zip"

        # Create backup of all thread files
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
    pass
            for file_path in thread_files:
    pass
                arcname = file_path.relative_to(self.repo_path)
                zip_file.write(file_path, arcname)

        # Create snapshot record
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            seal_id=seal.seal_id,
            timestamp=datetime.now().isoformat(),
            file_checksums={
                str(f.relative_to(self.repo_path)): seal.recovery_data["files"][str(f.relative_to(self.repo_path))][
                    "hash"
                ]
                for f in thread_files
                if str(f.relative_to(self.repo_path)) in seal.recovery_data["files"]
            },
            directory_structure={},
            metadata={"thread_files": [str(f.relative_to(self.repo_path)) for f in thread_files]},
            integrity_hash=seal.sha256_hash,
        )

        self.snapshots[snapshot_id] = snapshot

        snapshot_path = self.snapshots_dir / "{snapshot_id}.json"
        with open(snapshot_path, "w") as f:
    pass
            json.dump(asdict(snapshot), f, indent=2)

    def _load_existing_seals(self):
    pass
        """Load existing seals from disk"""
        if self.seals_dir.exists():
    pass
            for seal_file in self.seals_dir.glob("*.json"):
    pass
                if not seal_file.name.endswith("_snapshot.json"):
    pass
                    try:
    pass
                        with open(seal_file, "r") as f:
    pass
                            seal_data = json.load(f)
                            seal = MemorySeal(**seal_data)
                            self.seals[seal.seal_id] = seal
                    except (json.JSONDecodeError, TypeError) as e:
    pass
                        print("Warning: Could not load seal {seal_file}: {e}")

    def _load_audit_trail(self):
    pass
        """Load audit trail from disk"""
        if self.audit_file.exists():
    pass
            try:
    pass
                with open(self.audit_file, "r") as f:
    pass
                    self.audit_trail = json.load(f)
            except (json.JSONDecodeError, IOError):
    pass
                self.audit_trail = []

    def _log_audit_event(self, event_type: str, seal_id: str, description: str):
    pass
        """Log audit event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "seal_id": seal_id,
            "description": description,
            "user": os.getenv("USER", "unknown"),
        }

        self.audit_trail.append(event)

        # Save audit trail
        with open(self.audit_file, "w") as f:
    pass
            json.dump(self.audit_trail, f, indent=2)

def main():
    pass
    """CLI interface for memory sealing"""

    parser = argparse.ArgumentParser(description="Memory Sealing Engine")
    parser.add_argument("command", choices=["seal", "verify", "restore", "list"])
    parser.add_argument("target", nargs="?", help="Target file/directory/thread to seal")
    parser.add_argument("--seal-id", "-s", help="Seal ID")
    parser.add_argument("--type", "-t", choices=["file", "directory", "thread"], help="Seal type")
    parser.add_argument("--restore-path", "-r", help="Path to restore to")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Dry run (no changes)")
    parser.add_argument("--description", help="Description for thread seal")

    args = parser.parse_args()

    engine = MemorySealingEngine()

    if args.command == "seal":
    pass
        if not args.target:
    pass
            print("❌ Target required for seal command")
            return

        target_path = Path(args.target)

        if args.type == "thread":
    pass
            seal = engine.seal_thread(args.target, args.description)
            print("🔐 Thread sealed: {seal.seal_id}")
        elif args.type == "directory" or (args.type is None and target_path.is_dir()):
    pass
            seal = engine.seal_directory(target_path, args.seal_id)
            print("🔐 Directory sealed: {seal.seal_id}")
        else:
    pass
            seal = engine.seal_file(target_path, args.seal_id)
            print("🔐 File sealed: {seal.seal_id}")

        print("   Hash: {seal.sha256_hash}")
        print("   Timestamp: {seal.timestamp}")

    elif args.command == "verify":
    pass
        if not args.seal_id:
    pass
            print("❌ --seal-id required for verify command")
            return

        result = engine.verify_seal(args.seal_id)

        if result["status"] == "valid":
    pass
            print("✅ Seal {args.seal_id} is valid")
        else:
    pass
            print("❌ Seal {args.seal_id} is invalid:")
            for issue in result["issues"]:
    pass
                print("   - {issue}")

    elif args.command == "restore":
    pass
        if not args.seal_id:
    pass
            print("❌ --seal-id required for restore command")
            return

        result = engine.restore_sealed_state(args.seal_id, args.restore_path, args.dry_run)

        print("🔄 Restore result for {args.seal_id}: {result['status']}")
        for action in result["actions"]:
    pass
            print("   - {action}")

        if "error" in result:
    pass
            print("   Error: {result['error']}")

    elif args.command == "list":
    pass
        print("📋 Memory Seals ({len(engine.seals)} total):")

        for seal_id, seal in engine.seals.items():
    pass
            print("  🔐 {seal_id}")
            print("     Type: {seal.seal_type}")
            print("     Target: {seal.target_path}")
            print("     Created: {seal.timestamp}")
            print("     Hash: {seal.sha256_hash[:16]}...")
            print()

if __name__ == "__main__":
    pass
    main()
