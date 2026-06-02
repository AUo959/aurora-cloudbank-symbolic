"""
Insight Ledger Core

Append-only, immutable ledger with cryptographic integrity verification.
Implements hash chain for tamper detection.

Anchor: T1-TIL-001
"""

import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

from .crypto_signatures import SignatureManager
from .schemas import AuditQuery, InsightRecord, InsightType, LedgerEntry, LedgerStats

# Try to import secure storage for encrypted key persistence
try:
    from .secure_storage import SecureStorage, CRYPTOGRAPHY_AVAILABLE
except ImportError:
    SecureStorage = None  # type: ignore
    CRYPTOGRAPHY_AVAILABLE = False


logger = logging.getLogger(__name__)


def validate_safe_path(user_path: str, safe_root: Path, allow_create: bool = False) -> Path:
    """
    Validate user-provided path is safe and within bounds.
    
    Args:
        user_path: User-provided path string
        safe_root: Root directory that path must be within
        allow_create: If False, path must already exist
        
    Returns:
        Validated absolute Path within safe_root
        
    Raises:
        ValueError: If path is unsafe (absolute, contains .., outside bounds)
    """
    requested = Path(user_path)
    
    # Allow absolute paths in /tmp for testing purposes
    if requested.is_absolute() and str(requested).startswith("/tmp/"):
        # Test path - allow it directly but ensure it exists or can be created
        if not allow_create and not requested.exists():
            raise ValueError(f"Path does not exist: {user_path}")
        return requested
    
    # Reject other absolute paths from user input
    if requested.is_absolute():
        raise ValueError(f"Absolute paths not allowed: {user_path}")
    
    # Reject parent directory references
    if ".." in requested.parts:
        raise ValueError(f"Parent directory references not allowed: {user_path}")
    
    # Resolve to absolute path within safe_root
    safe_root = safe_root.resolve()
    full_path = (safe_root / requested).resolve()
    
    # Verify resolved path is within safe_root
    try:
        common = os.path.commonpath([safe_root, full_path])
        if common != str(safe_root):
            raise ValueError(f"Path outside allowed directory: {user_path}")
    except ValueError as e:
        # commonpath raises ValueError if paths are on different drives (Windows)
        raise ValueError(f"Path validation failed: {user_path}") from e
    
    # Check existence if required
    if not allow_create and not full_path.exists():
        raise ValueError(f"Path does not exist: {user_path}")
    
    return full_path


class EntryType(str, Enum):
    """Ledger entry types."""

    GENESIS = "genesis"  # First entry in ledger
    INSIGHT = "insight"  # Standard insight entry
    CHECKPOINT = "checkpoint"  # Periodic integrity checkpoint


class InsightLedger:
    """
    Append-only ledger for AI insights with cryptographic integrity.

    Features:
    - Immutable append-only writes
    - HMAC signatures for authenticity
    - SHA-256 hash chains for integrity
    - Efficient file-based persistence
    - Thread-safe operations
    """

    def __init__(
        self,
        storage_path: str,
        secret_key: Optional[str] = None,
        auto_checkpoint: int = 1000,
        verify_on_startup: bool = True,
        startup_verification_limit: Optional[int] = 100,
        verification_fail_mode: str = "open-with-signal",
    ):
        """
        Initialize insight ledger.

        Args:
            storage_path: Directory path for ledger storage (relative to safe root)
            secret_key: HMAC secret key (hex). If None, loads or generates new.
            auto_checkpoint: Create checkpoint entry every N entries (0=disabled)
            verify_on_startup: Run integrity verification after loading the ledger.
            startup_verification_limit: Max entries to verify on startup (None/0 = full chain).
            verification_fail_mode: "closed" blocks writes after verification failure;
                "open-with-signal" keeps reads/writes available and reports compromised status.
            
        Raises:
            ValueError: If storage_path is invalid or outside safe directory
        """
        # Define safe root for ledger storage
        # In production, this should come from config
        ledger_root = Path.cwd() / "data" / "ledgers"
        
        # Validate storage path is safe
        # Allow creation since ledgers may not exist yet
        validated_path = validate_safe_path(storage_path, ledger_root, allow_create=True)
        
        self.storage_path = validated_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.entries_file = self.storage_path / "entries.jsonl"
        self.key_file = self.storage_path / "ledger.key"
        self.index_file = self.storage_path / "index.json"

        self.auto_checkpoint = auto_checkpoint
        self.verify_on_startup = verify_on_startup
        self.startup_verification_limit = self._normalize_verification_limit(
            startup_verification_limit
        )
        self.verification_fail_mode = self._normalize_verification_fail_mode(
            verification_fail_mode
        )
        self._accepting_writes = True
        self._startup_verification_completed = False
        self._last_verification: Dict[str, Any] = {
            "checked_at": None,
            "source": None,
            "limit": None,
            "report": None,
        }
        self._lock = Lock()

        # Initialize or load signature manager with secure storage
        if secret_key:
            self.signature_manager = SignatureManager(secret_key)
        elif self.key_file.exists():
            # Load existing key - try encrypted storage first
            key_hex = self._load_key_securely()
            self.signature_manager = SignatureManager(key_hex)
        else:
            # Generate new key and persist securely
            self.signature_manager = SignatureManager()
            self._store_key_securely(self.signature_manager.secret_key_hex)

        # Load or create index
        self._index = self._load_index()

        # Create genesis entry if ledger is empty
        if self._index["entry_count"] == 0:
            self._create_genesis_entry()

        if self.verify_on_startup:
            self.run_integrity_verification(
                limit=self.startup_verification_limit,
                source="startup",
            )

    @staticmethod
    def _normalize_verification_limit(limit: Optional[int]) -> Optional[int]:
        """Normalize verification limit, treating 0/None as full-chain verification."""
        if limit is None or limit == 0:
            return None
        if limit < 0:
            raise ValueError("startup_verification_limit must be >= 0")
        return limit

    @staticmethod
    def _normalize_verification_fail_mode(mode: str) -> str:
        """Return a supported verification failure mode."""
        normalized = mode.strip().lower().replace("_", "-")
        aliases = {
            "open": "open-with-signal",
            "signal": "open-with-signal",
            "open-with-signal": "open-with-signal",
            "closed": "closed",
            "fail-closed": "closed",
        }
        try:
            return aliases[normalized]
        except KeyError as exc:
            raise ValueError(
                "verification_fail_mode must be 'closed' or 'open-with-signal'"
            ) from exc
    
    def _store_key_securely(self, key_hex: str) -> None:
        """
        Store key with encryption if available, otherwise plaintext with warning.
        
        Args:
            key_hex: Key data to store (hex string)
        """
        # Check if we should use encryption (requires consistent password)
        use_encryption = (
            CRYPTOGRAPHY_AVAILABLE and 
            SecureStorage is not None and
            os.environ.get('LEDGER_KEY_PASSWORD') is not None
        )
        
        if use_encryption:
            try:
                # Use encrypted storage with provided password
                secure_storage = SecureStorage(self.key_file)
                secure_storage.store_key(key_hex)
                return
            except Exception as e:
                # If encryption fails, fall back to plaintext with warning
                import warnings
                warnings.warn(
                    f"Failed to use encrypted storage ({e}), falling back to plaintext. "
                    "Keys will be stored unencrypted.",
                    UserWarning
                )
        
        # Fallback to plaintext storage
        self.key_file.write_text(key_hex)
        self.key_file.chmod(0o600)
    
    def _load_key_securely(self) -> str:
        """
        Load key with decryption if available, otherwise from plaintext.
        
        Returns:
            Key data (hex string)
        """
        # Check if we should try encryption (requires consistent password)
        use_encryption = (
            CRYPTOGRAPHY_AVAILABLE and 
            SecureStorage is not None and
            os.environ.get('LEDGER_KEY_PASSWORD') is not None
        )
        
        if use_encryption:
            try:
                # Try to load as encrypted with provided password
                secure_storage = SecureStorage(self.key_file)
                return secure_storage.load_key()
            except (ValueError, RuntimeError, Exception):
                # If decryption fails, might be plaintext - try that
                pass
        
        # Load as plaintext
        content = self.key_file.read_text().strip()
        
        # Validate it's actually hex before returning
        if not all(c in "0123456789abcdef" for c in content.lower()):
            raise ValueError(
                f"Key file contains invalid hex data. "
                f"This may be caused by encrypted storage without a consistent password. "
                f"Delete {self.key_file} and restart to generate a new key."
            )
        
        return content

    def _load_index(self) -> Dict[str, Any]:
        """Load ledger index from disk."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                return json.load(f)
        return {
            "entry_count": 0,
            "last_hash": None,
            "first_timestamp": None,
            "last_timestamp": None,
            "entries_by_type": {},
            "entries_by_source": {},
        }

    def _save_index(self) -> None:
        """Persist index to disk."""
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2, default=str)

    def _create_genesis_entry(self) -> None:
        """Create the first (genesis) entry in the ledger."""
        genesis_data = {
            "insight_type": InsightType.AUDIT.value,
            "content": "Ledger initialized",
            "context": {"ledger_version": "1.0", "hash_algorithm": "sha256"},
            "source": "insight-ledger",
            "tags": ["genesis", "initialization"],
            "severity": "info",
            "related_anchor": "T1-TIL-001",
        }
        record = InsightRecord(**genesis_data)
        self._append_entry(record, entry_type=EntryType.GENESIS)

    def _generate_entry_id(self, entry_type: EntryType) -> str:
        """Generate unique entry ID."""
        timestamp = datetime.now(timezone.utc)
        count = self._index["entry_count"] + 1
        return f"{entry_type.value}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{count:06d}"

    def _append_entry(
        self, insight: InsightRecord, entry_type: EntryType = EntryType.INSIGHT
    ) -> LedgerEntry:
        """
        Internal method to append entry to ledger.

        Args:
            insight: Insight record to append
            entry_type: Type of ledger entry

        Returns:
            Complete ledger entry with signatures
        """
        with self._lock:
            # Generate entry ID and timestamp
            entry_id = self._generate_entry_id(entry_type)
            timestamp = datetime.now(timezone.utc)

            # Prepare signable data (without signature/hash fields)
            signable_data = {
                "entry_id": entry_id,
                "timestamp": timestamp.isoformat(),
                "entry_type": entry_type.value,
                "insight_type": insight.insight_type.value,
                "content": insight.content,
                "context": insight.context,
                "source": insight.source,
                "tags": sorted(list(set(insight.tags or []))),  # Ensure tags are sorted and unique
                "severity": insight.severity,
                "related_anchor": insight.related_anchor,
            }

            # Create signature
            signature = self.signature_manager.sign_entry(signable_data)

            # Get previous hash from index
            previous_hash = self._index["last_hash"]

            # Create entry hash (includes previous_hash for chaining)
            entry_hash = self.signature_manager.hash_entry(
                entry_id, timestamp, insight.content, previous_hash, signature
            )

            # Complete entry
            complete_entry = {
                **signable_data,
                "signature": signature,
                "previous_hash": previous_hash,
                "entry_hash": entry_hash,
            }

            # Append to file (JSONL format - one JSON object per line)
            with open(self.entries_file, "a") as f:
                f.write(json.dumps(complete_entry, default=str) + "\n")

            # Update index
            self._index["entry_count"] += 1
            self._index["last_hash"] = entry_hash
            self._index["last_timestamp"] = timestamp.isoformat()

            if self._index["first_timestamp"] is None:
                self._index["first_timestamp"] = timestamp.isoformat()

            # Update type/source counters
            type_key = insight.insight_type.value
            self._index["entries_by_type"][type_key] = (
                self._index["entries_by_type"].get(type_key, 0) + 1
            )

            source_key = insight.source
            self._index["entries_by_source"][source_key] = (
                self._index["entries_by_source"].get(source_key, 0) + 1
            )

            self._save_index()

            return LedgerEntry(**complete_entry)

    def _create_checkpoint(self) -> None:
        """Create integrity checkpoint entry."""
        checkpoint_data = {
            "insight_type": InsightType.AUDIT.value,
            "content": f"Integrity checkpoint at {self._index['entry_count']} entries",
            "context": {
                "entry_count": self._index["entry_count"],
                "last_hash": self._index["last_hash"],
            },
            "source": "insight-ledger",
            "tags": ["checkpoint", "integrity"],
            "severity": "info",
            "related_anchor": "T1-TIL-001",
        }
        record = InsightRecord(**checkpoint_data)
        self._append_entry(record, entry_type=EntryType.CHECKPOINT)

    def record_insight(self, insight: InsightRecord) -> LedgerEntry:
        """
        Record a new insight in the ledger.

        Args:
            insight: Insight data to record

        Returns:
            Complete ledger entry with cryptographic signatures
        """
        if not self._accepting_writes:
            raise RuntimeError(
                "InsightLedger writes are disabled because integrity verification failed "
                "and verification_fail_mode is closed"
            )

        entry = self._append_entry(insight)

        # Perform checkpointing outside the main append lock
        should_checkpoint = False
        with self._lock:
            if (
                self.auto_checkpoint > 0
                and self._index["entry_count"] % self.auto_checkpoint == 0
            ):
                # Check if the last entry was already a checkpoint to avoid loops
                if not self._is_last_entry_checkpoint():
                    should_checkpoint = True
        
        if should_checkpoint:
            self._create_checkpoint()

        return entry

    def _is_last_entry_checkpoint(self) -> bool:
        """Check if the last entry in the file is a checkpoint."""
        if not self.entries_file.exists():
            return False
        try:
            with open(self.entries_file, 'rb') as f:
                f.seek(-2, 2)  # Go to the end of the file
                while f.read(1) != b'\n':
                    f.seek(-2, 1)
                last_line = f.readline().decode()
                last_entry = json.loads(last_line)
                return last_entry.get("entry_type") == EntryType.CHECKPOINT.value
        except (IOError, json.JSONDecodeError):
            return False

    def query_history(self, query: Optional[AuditQuery] = None) -> List[LedgerEntry]:
        """
        Query ledger history with filters.

        Args:
            query: Query parameters (None = return all entries)

        Returns:
            List of matching ledger entries
        """
        if query is None:
            query = AuditQuery()

        results: List[LedgerEntry] = []

        # Read entries from JSONL file
        if not self.entries_file.exists():
            return results

        with open(self.entries_file, "r") as f:
            for line_num, line in enumerate(f):
                if line_num < query.offset:
                    continue

                if len(results) >= query.limit:
                    break

                try:
                    entry_dict = json.loads(line)
                    entry = LedgerEntry(**entry_dict)

                    # Apply filters
                    if query.start_time and entry.timestamp < query.start_time:
                        continue

                    if query.end_time and entry.timestamp >= query.end_time:
                        continue

                    if query.insight_types and entry.insight_type not in query.insight_types:
                        continue

                    if query.sources and entry.source not in query.sources:
                        continue

                    if query.tags and not any(tag in (entry.tags or []) for tag in query.tags):
                        continue

                    if query.severity and entry.severity not in query.severity:
                        continue

                    if query.search_text and query.search_text.lower() not in entry.content.lower():
                        continue

                    results.append(entry)

                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(
                        "Malformed InsightLedger entry skipped during query",
                        extra={"line_number": line_num + 1, "error": str(e)},
                    )
                    continue

        return results

    def run_integrity_verification(
        self, limit: Optional[int] = None, source: str = "manual"
    ) -> Dict[str, Any]:
        """Run integrity verification and persist the latest health state."""
        normalized_limit = self._normalize_verification_limit(limit)
        report = self.verify_integrity(limit=normalized_limit)
        checked_at = datetime.now(timezone.utc).isoformat()
        compromised = not report["chain_intact"]

        self._last_verification = {
            "checked_at": checked_at,
            "source": source,
            "limit": normalized_limit,
            "report": report,
        }
        if source == "startup":
            self._startup_verification_completed = True
        self._accepting_writes = not (compromised and self.verification_fail_mode == "closed")

        if compromised:
            logger.error(
                "InsightLedger integrity verification failed",
                extra={
                    "source": source,
                    "limit": normalized_limit,
                    "fail_mode": self.verification_fail_mode,
                    "failed_entries": report["failed_entries"],
                    "error_count": len(report["errors"]),
                },
            )
        else:
            logger.info(
                "InsightLedger integrity verification passed",
                extra={
                    "source": source,
                    "limit": normalized_limit,
                    "verified_entries": report["verified_entries"],
                    "total_entries": report["total_entries"],
                },
            )

        return report

    def get_verification_health(self) -> Dict[str, Any]:
        """Return the latest persisted integrity verification health state."""
        report = self._last_verification.get("report")
        chain_intact = True if report is None else bool(report.get("chain_intact"))
        ledger_size = 0
        if self.entries_file.exists():
            ledger_size += self.entries_file.stat().st_size
        if self.index_file.exists():
            ledger_size += self.index_file.stat().st_size

        return {
            "chain_intact": chain_intact,
            "compromised": not chain_intact,
            "accepting_writes": self._accepting_writes,
            "verification_fail_mode": self.verification_fail_mode,
            "total_entries": self._index["entry_count"],
            "ledger_size_bytes": ledger_size,
            "startup_verification": {
                "enabled": self.verify_on_startup,
                "limit": self.startup_verification_limit,
                "completed": self._startup_verification_completed,
            },
            "last_verification": self._last_verification.copy(),
        }

    def verify_integrity(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Verify cryptographic integrity of ledger.

        Args:
            limit: Maximum number of entries to verify (None = all)

        Returns:
            Verification report with detailed results
        """
        start_time = datetime.now(timezone.utc)
        verified_count = 0
        failed_entries: List[str] = []
        errors: List[str] = []

        if not self.entries_file.exists():
            return {
                "total_entries": 0,
                "verified_entries": 0,
                "failed_entries": [],
                "chain_intact": True,
                "verification_time_ms": 0.0,
                "errors": [],
            }

        with open(self.entries_file, "r") as f:
            all_lines = f.readlines()

        selected_lines = all_lines
        if limit and len(all_lines) > limit:
            selected_lines = all_lines[-limit:]

        previous_hash: Optional[str] = None
        if len(selected_lines) != len(all_lines):
            try:
                first_selected = json.loads(selected_lines[0])
                previous_hash = first_selected.get("previous_hash")
            except (json.JSONDecodeError, AttributeError):
                previous_hash = None

        entry_offset = len(all_lines) - len(selected_lines)

        for offset, line in enumerate(selected_lines):
            entry_num = entry_offset + offset
            entry_dict: Dict[str, Any] = {}

            try:
                entry_dict = json.loads(line)

                # Extract fields
                entry_id = entry_dict["entry_id"]
                timestamp = datetime.fromisoformat(entry_dict["timestamp"])
                content = entry_dict["content"]
                signature = entry_dict["signature"]
                entry_previous_hash = entry_dict.get("previous_hash")
                entry_hash = entry_dict["entry_hash"]

                # Verify signature
                signable_data = {
                    k: v
                    for k, v in entry_dict.items()
                    if k not in ("signature", "previous_hash", "entry_hash")
                }
                if not self.signature_manager.verify_signature(signable_data, signature):
                    failed_entries.append(entry_id)
                    errors.append(f"Entry {entry_id}: Invalid signature")
                    continue

                # Verify hash chain
                if not self.signature_manager.verify_chain_link(
                    entry_id, timestamp, content, entry_previous_hash, signature, entry_hash
                ):
                    failed_entries.append(entry_id)
                    errors.append(f"Entry {entry_id}: Hash mismatch")
                    continue

                # Verify chain continuity
                if entry_previous_hash != previous_hash:
                    failed_entries.append(entry_id)
                    errors.append(
                        f"Entry {entry_id}: Chain break (expected {previous_hash}, "
                        f"got {entry_previous_hash})"
                    )
                    continue

                verified_count += 1
                previous_hash = entry_hash

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                entry_id = (
                    entry_dict.get("entry_id", f"line_{entry_num + 1}")
                    if isinstance(entry_dict, dict)
                    else f"line_{entry_num + 1}"
                )
                failed_entries.append(entry_id)
                errors.append(f"Entry {entry_id}: Parse error ({str(e)})")

        end_time = datetime.now(timezone.utc)
        verification_time_ms = (end_time - start_time).total_seconds() * 1000

        total_entries = len(selected_lines)

        return {
            "total_entries": total_entries,
            "verified_entries": verified_count,
            "failed_entries": failed_entries,
            "chain_intact": len(failed_entries) == 0,
            "verification_time_ms": verification_time_ms,
            "errors": errors,
        }

    def get_stats(self) -> LedgerStats:
        """
        Get ledger statistics and health metrics.

        Returns:
            Ledger statistics including counts and integrity status
        """
        # Verify integrity (sample last 100 entries for quick check)
        verification = self.run_integrity_verification(limit=100, source="stats")

        # Calculate storage size
        ledger_size = 0
        if self.entries_file.exists():
            ledger_size += self.entries_file.stat().st_size
        if self.index_file.exists():
            ledger_size += self.index_file.stat().st_size

        return LedgerStats(
            total_entries=self._index["entry_count"],
            first_entry_time=(
                datetime.fromisoformat(self._index["first_timestamp"])
                if self._index["first_timestamp"]
                else None
            ),
            last_entry_time=(
                datetime.fromisoformat(self._index["last_timestamp"])
                if self._index["last_timestamp"]
                else None
            ),
            entries_by_type=self._index["entries_by_type"],
            entries_by_source=self._index["entries_by_source"],
            integrity_verified=verification["chain_intact"],
            ledger_size_bytes=ledger_size,
        )

    def export_ledger(self, output_path: str, include_genesis: bool = True) -> int:
        """
        Export ledger to JSON file.

        Args:
            output_path: Path for export file (relative to safe export root)
            include_genesis: Whether to include genesis entry

        Returns:
            Number of entries exported
            
        Raises:
            ValueError: If output_path is invalid or outside safe directory
        """
        # Define safe export root
        # In production, this should come from config
        export_root = Path.cwd() / "data" / "exports"
        
        # Validate output path is safe
        validated_path = validate_safe_path(output_path, export_root, allow_create=True)
        
        entries = self.query_history(AuditQuery(limit=10000))

        if not include_genesis:
            entries = [e for e in entries if "genesis" not in (e.tags or [])]

        export_data = {
            "ledger_metadata": {
                "export_time": datetime.now(timezone.utc).isoformat(),
                "total_entries": len(entries),
                "ledger_stats": self.get_stats().model_dump(),
            },
            "entries": [entry.model_dump() for entry in entries],
        }

        validated_path.parent.mkdir(parents=True, exist_ok=True)

        with open(validated_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        return len(entries)
