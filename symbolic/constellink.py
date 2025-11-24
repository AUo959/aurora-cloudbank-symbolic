"""
CONSTELLINK - Multi-thread mesh creation and entropy tracking system

This module provides the foundational ConstellinkMesh data structure that
ORACULITH forecasting engine consumes for symbolic analysis.

Anchors: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


DEFAULT_ANCHOR_SEED = "EOS_SEED_ORION"
DEFAULT_ETHICS_PROTOCOL = "Picard_Delta_3"


def _utc_now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha256_of_json_payload(payload: Dict[str, Any]) -> str:
    """
    Compute SHA256 hash of a JSON-serializable payload with stable ordering.

    Args:
        payload: Dictionary to hash

    Returns:
        Hash string prefixed with 'sha256:'
    """
    # Sort keys for deterministic hashing
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    return f"sha256:{hash_bytes}"


@dataclass
class ThreadDescriptor:
    """Descriptor for a single logical thread within a mesh."""

    thread_id: str
    source: str
    entropy_hint: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    anchor_alignment: Optional[float] = None

    def __post_init__(self):
        """Validate entropy_hint and anchor_alignment ranges."""
        if self.entropy_hint is not None:
            if not (0.0 <= self.entropy_hint <= 1.0):
                raise ValueError("entropy_hint must be between 0.0 and 1.0")
        if self.anchor_alignment is not None:
            if not (0.0 <= self.anchor_alignment <= 1.0):
                raise ValueError("anchor_alignment must be between 0.0 and 1.0")


@dataclass
class EntropySummary:
    """Aggregate entropy and drift metrics for a mesh."""

    entropy_mean: float
    drift_flag: str  # stable, moderate, divergent, unknown
    thread_count: int
    entropy_std: Optional[float] = None

    def __post_init__(self):
        """Validate drift_flag."""
        valid_flags = ["stable", "moderate", "divergent", "unknown"]
        if self.drift_flag not in valid_flags:
            raise ValueError(f"drift_flag must be one of {valid_flags}")


@dataclass
class MeshManifest:
    """DLP-aware manifest for mesh identity and integrity."""

    version: str
    export_time_utc: str
    anchor_seed: str
    ethics_protocol: str
    symbolic_tags: List[str]
    dlp_tags: List[str]
    state_hash: str


@dataclass
class ConstellinkMesh:
    """A multi-thread symbolic mesh with entropy tracking and DLP compliance."""

    mesh_id: str
    created_at_utc: str
    anchor_seed: str
    ethics_protocol: str
    threads: List[ThreadDescriptor]
    entropy_summary: EntropySummary
    mesh_manifest: MeshManifest

    def to_dict(self) -> Dict[str, Any]:
        """Convert mesh to dictionary for JSON export."""
        return {
            "mesh_id": self.mesh_id,
            "created_at_utc": self.created_at_utc,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "threads": [asdict(t) for t in self.threads],
            "entropy_summary": asdict(self.entropy_summary),
            "mesh_manifest": asdict(self.mesh_manifest)
        }


def create_mesh(
    threads: List[ThreadDescriptor],
    *,
    mesh_id: Optional[str] = None,
    anchor_seed: str = DEFAULT_ANCHOR_SEED,
    ethics_protocol: str = DEFAULT_ETHICS_PROTOCOL,
    symbolic_tags: Optional[List[str]] = None,
    dlp_tags: Optional[List[str]] = None
) -> ConstellinkMesh:
    """
    Create a ConstellinkMesh from a list of threads.

    Args:
        threads: List of ThreadDescriptor objects
        mesh_id: Optional mesh identifier (auto-generated if not provided)
        anchor_seed: Anchor seed for symbolic operations
        ethics_protocol: Ethics protocol identifier
        symbolic_tags: Optional symbolic tags for categorization
        dlp_tags: Optional DLP tags for governance

    Returns:
        ConstellinkMesh with computed entropy and sealed manifest
    """
    if not threads:
        raise ValueError("Cannot create mesh with empty thread list")

    mesh_id = mesh_id or f"mesh_{uuid.uuid4().hex[:12]}"
    created_at = _utc_now_iso()

    # Compute entropy summary from threads
    entropy_hints = [t.entropy_hint for t in threads if t.entropy_hint is not None]
    if entropy_hints:
        entropy_mean = sum(entropy_hints) / len(entropy_hints)
        if len(entropy_hints) > 1:
            variance = sum((e - entropy_mean) ** 2 for e in entropy_hints) / len(entropy_hints)
            entropy_std = variance ** 0.5
        else:
            entropy_std = 0.0

        # Determine drift flag based on entropy
        if entropy_mean < 0.3:
            drift_flag = "stable"
        elif entropy_mean < 0.6:
            drift_flag = "moderate"
        else:
            drift_flag = "divergent"
    else:
        # No entropy hints provided
        entropy_mean = 0.0
        entropy_std = 0.0
        drift_flag = "unknown"

    entropy_summary = EntropySummary(
        entropy_mean=entropy_mean,
        entropy_std=entropy_std,
        drift_flag=drift_flag,
        thread_count=len(threads)
    )

    # Build mesh payload for hashing (excluding manifest)
    mesh_payload = {
        "mesh_id": mesh_id,
        "created_at_utc": created_at,
        "anchor_seed": anchor_seed,
        "ethics_protocol": ethics_protocol,
        "threads": [asdict(t) for t in threads],
        "entropy_summary": asdict(entropy_summary)
    }

    # Compute state hash
    state_hash = _sha256_of_json_payload(mesh_payload)

    # Create manifest
    manifest = MeshManifest(
        version="1.0.0",
        export_time_utc=_utc_now_iso(),
        anchor_seed=anchor_seed,
        ethics_protocol=ethics_protocol,
        symbolic_tags=symbolic_tags or ["multi-thread", "symbolic-weave"],
        dlp_tags=dlp_tags or ["constellink", "mesh-threading"],
        state_hash=state_hash
    )

    return ConstellinkMesh(
        mesh_id=mesh_id,
        created_at_utc=created_at,
        anchor_seed=anchor_seed,
        ethics_protocol=ethics_protocol,
        threads=threads,
        entropy_summary=entropy_summary,
        mesh_manifest=manifest
    )


def mesh_from_dict(data: Dict[str, Any], *, validate_hash: bool = True) -> ConstellinkMesh:
    """
    Reconstruct a ConstellinkMesh from a dictionary.

    Args:
        data: Dictionary representation of a mesh
        validate_hash: Whether to validate the state_hash

    Returns:
        ConstellinkMesh instance

    Raises:
        ValueError: If hash validation fails or required fields are missing
    """
    required_fields = [
        "mesh_id", "created_at_utc", "anchor_seed", "ethics_protocol",
        "threads", "entropy_summary", "mesh_manifest"
    ]
    for field_name in required_fields:
        if field_name not in data:
            raise ValueError(f"Missing required field: {field_name}")

    # Reconstruct threads
    threads = [
        ThreadDescriptor(
            thread_id=t["thread_id"],
            source=t["source"],
            entropy_hint=t.get("entropy_hint"),
            tags=t.get("tags", []),
            anchor_alignment=t.get("anchor_alignment")
        )
        for t in data["threads"]
    ]

    # Reconstruct entropy summary
    es_data = data["entropy_summary"]
    entropy_summary = EntropySummary(
        entropy_mean=es_data["entropy_mean"],
        entropy_std=es_data.get("entropy_std"),
        drift_flag=es_data["drift_flag"],
        thread_count=es_data["thread_count"]
    )

    # Reconstruct manifest
    m_data = data["mesh_manifest"]
    manifest = MeshManifest(
        version=m_data["version"],
        export_time_utc=m_data["export_time_utc"],
        anchor_seed=m_data["anchor_seed"],
        ethics_protocol=m_data["ethics_protocol"],
        symbolic_tags=m_data["symbolic_tags"],
        dlp_tags=m_data["dlp_tags"],
        state_hash=m_data["state_hash"]
    )

    mesh = ConstellinkMesh(
        mesh_id=data["mesh_id"],
        created_at_utc=data["created_at_utc"],
        anchor_seed=data["anchor_seed"],
        ethics_protocol=data["ethics_protocol"],
        threads=threads,
        entropy_summary=entropy_summary,
        mesh_manifest=manifest
    )

    # Validate hash if requested
    if validate_hash:
        mesh_payload = {
            "mesh_id": mesh.mesh_id,
            "created_at_utc": mesh.created_at_utc,
            "anchor_seed": mesh.anchor_seed,
            "ethics_protocol": mesh.ethics_protocol,
            "threads": [asdict(t) for t in mesh.threads],
            "entropy_summary": asdict(mesh.entropy_summary)
        }
        expected_hash = _sha256_of_json_payload(mesh_payload)
        if expected_hash != manifest.state_hash:
            raise ValueError(
                f"Hash validation failed. Expected {expected_hash}, got {manifest.state_hash}"
            )

    return mesh
