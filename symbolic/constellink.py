"""CONSTELLINK Multi-Thread Relay Beacon

Binds multiple symbolic threads into a sealed, hash-verified mesh artifact
with anchor alignment, DLP awareness, and entropy/drift tracking.

This module implements the CONSTELLINK specification from the Aurora/GUMAS
symbolic runtime ecosystem.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from enum import Enum


DEFAULT_ANCHOR_SEED = "EOS_SEED_ORION"
DEFAULT_ETHICS_PROTOCOL = "Picard_Delta_3"
DEFAULT_SPEC_PATH = "symbolic_specs/Symbolic_Module_Specs_CONSTELLINK_ORACULITH.json"


class AnchorAlignment(str, Enum):
    """Anchor alignment status"""
    ALIGNED = "aligned"
    DIVERGENT = "divergent"
    UNKNOWN = "unknown"


class DriftFlag(str, Enum):
    """Overall drift assessment"""
    STABLE = "stable"
    WATCH = "watch"
    DIVERGENT = "divergent"


@dataclass
class ThreadDescriptor:
    """Descriptor for a single thread to be included in the mesh"""
    thread_id: str
    anchor_seed: Optional[str] = None
    dlp_tags: list[str] = field(default_factory=list)
    entropy_score: Optional[float] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DlpPolicy:
    """Data Lineage Protocol policy for mesh binding"""
    allow_cross_thread_content: bool = True
    allowed_dlp_tags: Optional[list[str]] = None


@dataclass
class MeshRequest:
    """Request to bind threads into a mesh"""
    request_id: str
    threads: list[ThreadDescriptor]
    target_anchor_seed: Optional[str] = None
    dlp_policy: Optional[DlpPolicy] = None
    caller_context: Optional[dict[str, Any]] = None


@dataclass
class MeshThreadView:
    """Thread view within the mesh with alignment metadata"""
    thread_id: str
    anchor_alignment: str
    drift_summary: str
    anchor_seed: Optional[str] = None
    dlp_tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EntropySummary:
    """Aggregated entropy metrics across all threads"""
    min_entropy: float
    max_entropy: float
    mean_entropy: float
    drift_flag: str


@dataclass
class DlpEffectivePolicy:
    """Effective DLP policy after processing the mesh request"""
    cross_thread_content_allowed: bool
    rejected_thread_count: int
    allowed_tags: Optional[list[str]] = None


@dataclass
class MeshManifest:
    """Manifest with version, export time, and cryptographic seal"""
    version: str
    export_time_utc: str
    anchor_seed: str
    ethics_protocol: str
    symbolic_tags: list[str]
    dlp_tags: list[str]
    state_hash: str


@dataclass
class ConstellinkMesh:
    """Resulting mesh artifact from binding threads"""
    mesh_id: str
    created_at_utc: str
    anchor_seed: str
    ethics_protocol: str
    threads: list[MeshThreadView]
    dlp_effective_policy: DlpEffectivePolicy
    entropy_summary: EntropySummary
    divergent_truths: list[dict[str, Any]]
    mesh_manifest: MeshManifest
    caller_context: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert mesh to dictionary for JSON export"""
        return asdict(self)

    def glyphcard(self) -> str:
        """Return a short human-readable summary of the mesh"""
        lines = [
            "═══ CONSTELLINK MESH GLYPHCARD ═══",
            f"Mesh ID: {self.mesh_id}",
            f"Anchor: {self.anchor_seed}",
            f"Ethics: {self.ethics_protocol}",
            f"Threads: {len(self.threads)}",
            f"Drift Flag: {self.entropy_summary.drift_flag}",
            f"Mean Entropy: {self.entropy_summary.mean_entropy:.3f}",
            f"DLP Rejections: {self.dlp_effective_policy.rejected_thread_count}",
        ]

        if self.divergent_truths:
            lines.append(f"\n⚠️  Divergent Truths ({len(self.divergent_truths)}):")
            for i, truth in enumerate(self.divergent_truths[:3], 1):
                lines.append(f"  {i}. {truth.get('type', 'unknown')}: {truth.get('message', 'N/A')}")
            if len(self.divergent_truths) > 3:
                lines.append(f"  ... and {len(self.divergent_truths) - 3} more")

        lines.append("═" * 35)
        return "\n".join(lines)


class ConstellinkRelay:
    """Stateless CONSTELLINK relay beacon for binding threads into meshes"""

    DEFAULT_ANCHOR_SEED = DEFAULT_ANCHOR_SEED
    DEFAULT_ETHICS_PROTOCOL = DEFAULT_ETHICS_PROTOCOL

    def bind(self, request: MeshRequest) -> ConstellinkMesh:
        """Bind threads into a mesh according to CONSTELLINK specification

        Args:
            request: MeshRequest containing threads and policies

        Returns:
            ConstellinkMesh: The resulting sealed mesh artifact

        Raises:
            ValueError: If no threads provided or other validation errors
        """
        # Validate at least one thread
        if not request.threads:
            raise ValueError("At least one thread is required to create a mesh")

        # Initialize tracking
        divergent_truths = []
        rejected_threads = []

        # Resolve effective DLP policy
        dlp_policy = request.dlp_policy or DlpPolicy()

        # Filter threads by DLP policy
        accepted_threads = []
        for thread in request.threads:
            if dlp_policy.allowed_dlp_tags is not None:
                # Check if thread's tags are subset of allowed tags
                thread_tags_set = set(thread.dlp_tags or [])
                allowed_tags_set = set(dlp_policy.allowed_dlp_tags)

                if not thread_tags_set.issubset(allowed_tags_set):
                    rejected_threads.append(thread)
                    rejected_tags_list = list(thread_tags_set - allowed_tags_set)
                    message = (
                        f"Thread DLP tags {list(thread_tags_set)} not subset of "
                        f"allowed {list(allowed_tags_set)}"
                    )
                    divergent_truths.append({
                        "type": "dlp_rejection",
                        "thread_id": thread.thread_id,
                        "message": message,
                        "rejected_tags": rejected_tags_list
                    })
                    continue

            accepted_threads.append(thread)

        # If no threads remain after DLP filtering, we still create a mesh but note it
        if not accepted_threads and request.threads:
            divergent_truths.append({
                "type": "all_threads_rejected",
                "message": "All threads were rejected due to DLP policy",
                "original_thread_count": len(request.threads)
            })

        # Resolve anchor seed
        anchor_seed = self._resolve_anchor_seed(
            request.target_anchor_seed,
            accepted_threads,
            divergent_truths
        )

        # Create mesh thread views with alignment and drift
        mesh_threads = []
        entropy_scores = []

        for thread in accepted_threads:
            # Determine anchor alignment
            if thread.anchor_seed is None:
                alignment = AnchorAlignment.UNKNOWN
            elif thread.anchor_seed == anchor_seed:
                alignment = AnchorAlignment.ALIGNED
            else:
                alignment = AnchorAlignment.DIVERGENT

            # Get entropy score
            entropy = thread.entropy_score if thread.entropy_score is not None else 0.0
            entropy_scores.append(entropy)

            # Create drift summary
            drift_summary = self._create_drift_summary(entropy, alignment)

            mesh_threads.append(MeshThreadView(
                thread_id=thread.thread_id,
                anchor_seed=thread.anchor_seed,
                dlp_tags=thread.dlp_tags or [],
                anchor_alignment=alignment.value,
                drift_summary=drift_summary,
                metadata=thread.metadata
            ))

        # Compute entropy summary
        if entropy_scores:
            min_entropy = min(entropy_scores)
            max_entropy = max(entropy_scores)
            mean_entropy = sum(entropy_scores) / len(entropy_scores)
        else:
            min_entropy = max_entropy = mean_entropy = 0.0

        # Determine drift flag
        drift_flag = self._determine_drift_flag(mean_entropy, max_entropy, mesh_threads)

        entropy_summary = EntropySummary(
            min_entropy=min_entropy,
            max_entropy=max_entropy,
            mean_entropy=mean_entropy,
            drift_flag=drift_flag.value
        )

        # Build effective DLP policy
        dlp_effective_policy = DlpEffectivePolicy(
            cross_thread_content_allowed=dlp_policy.allow_cross_thread_content,
            allowed_tags=dlp_policy.allowed_dlp_tags,
            rejected_thread_count=len(rejected_threads)
        )

        # Create mesh ID and timestamps
        mesh_id = _generate_mesh_id(request.request_id)
        created_at_utc = _utc_now_iso()

        # Build mesh payload (without manifest)
        mesh_payload = {
            "mesh_id": mesh_id,
            "created_at_utc": created_at_utc,
            "anchor_seed": anchor_seed,
            "ethics_protocol": self.DEFAULT_ETHICS_PROTOCOL,
            "threads": [asdict(t) for t in mesh_threads],
            "dlp_effective_policy": asdict(dlp_effective_policy),
            "entropy_summary": asdict(entropy_summary),
            "divergent_truths": divergent_truths,
            "caller_context": request.caller_context
        }

        # Compute state hash over payload
        state_hash = _sha256_of_json_payload(mesh_payload)

        # Build manifest
        mesh_manifest = MeshManifest(
            version="1.0.0",
            export_time_utc=created_at_utc,
            anchor_seed=anchor_seed,
            ethics_protocol=self.DEFAULT_ETHICS_PROTOCOL,
            symbolic_tags=["mesh", "relay", "multi-thread"],
            dlp_tags=["cross-thread", "symbolic_mesh"],
            state_hash=state_hash
        )

        # Create final mesh
        return ConstellinkMesh(
            mesh_id=mesh_id,
            created_at_utc=created_at_utc,
            anchor_seed=anchor_seed,
            ethics_protocol=self.DEFAULT_ETHICS_PROTOCOL,
            threads=mesh_threads,
            dlp_effective_policy=dlp_effective_policy,
            entropy_summary=entropy_summary,
            divergent_truths=divergent_truths,
            caller_context=request.caller_context,
            mesh_manifest=mesh_manifest
        )

    def _resolve_anchor_seed(
        self,
        target_anchor: Optional[str],
        threads: list[ThreadDescriptor],
        divergent_truths: list[dict]
    ) -> str:
        """Resolve the effective anchor seed for the mesh"""
        # Prefer explicit target
        if target_anchor:
            return target_anchor

        # Collect non-None anchor seeds from threads
        thread_anchors = [t.anchor_seed for t in threads if t.anchor_seed is not None]

        if not thread_anchors:
            # No anchors available, use default
            return self.DEFAULT_ANCHOR_SEED

        # Check if all threads share same anchor
        unique_anchors = set(thread_anchors)
        if len(unique_anchors) == 1:
            return thread_anchors[0]

        # Divergent anchors detected
        divergent_truths.append({
            "type": "anchor_divergence",
            "message": f"Threads have divergent anchor seeds: {list(unique_anchors)}",
            "anchors": list(unique_anchors),
            "resolution": f"Using default: {self.DEFAULT_ANCHOR_SEED}"
        })

        return self.DEFAULT_ANCHOR_SEED

    def _create_drift_summary(self, entropy: float, alignment: AnchorAlignment) -> str:
        """Create human-readable drift summary for a thread"""
        if entropy < 0.3:
            entropy_desc = "low entropy"
        elif entropy < 0.6:
            entropy_desc = "moderate entropy"
        else:
            entropy_desc = "high entropy"

        return f"{alignment.value} anchor, {entropy_desc} ({entropy:.2f})"

    def _determine_drift_flag(
        self,
        mean_entropy: float,
        max_entropy: float,
        threads: list[MeshThreadView]
    ) -> DriftFlag:
        """Determine overall drift flag based on entropy and alignment"""
        # Count divergent threads
        divergent_count = sum(1 for t in threads if t.anchor_alignment == AnchorAlignment.DIVERGENT.value)
        has_divergent_anchors = divergent_count > 0

        # Assess drift based on entropy and anchor alignment
        if mean_entropy < 0.3 and max_entropy < 0.5 and not has_divergent_anchors:
            return DriftFlag.STABLE
        elif mean_entropy < 0.6 and max_entropy < 0.8:
            return DriftFlag.WATCH
        else:
            return DriftFlag.DIVERGENT


# Helper functions

def _utc_now_iso() -> str:
    """Return current UTC timestamp in ISO8601 format with Z suffix"""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_of_json_payload(payload: dict) -> str:
    """Compute SHA256 hash of JSON payload with stable ordering"""
    json_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    return f"sha256::{hash_obj.hexdigest()}"


def _generate_mesh_id(request_id: str) -> str:
    """Generate mesh ID from request ID with timestamp"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"mesh_{request_id}_{timestamp}"


def mesh_request_from_dict(payload: dict) -> MeshRequest:
    """Construct a typed MeshRequest from raw JSON/dict input

    Args:
        payload: Dictionary representation of a mesh request

    Returns:
        MeshRequest: Typed mesh request object
    """
    # Convert threads
    threads = []
    for t in payload.get("threads", []):
        threads.append(ThreadDescriptor(
            thread_id=t["thread_id"],
            anchor_seed=t.get("anchor_seed"),
            dlp_tags=t.get("dlp_tags", []),
            entropy_score=t.get("entropy_score"),
            metadata=t.get("metadata", {})
        ))

    # Convert DLP policy if present
    dlp_policy = None
    if "dlp_policy" in payload and payload["dlp_policy"] is not None:
        dlp_policy = DlpPolicy(
            allow_cross_thread_content=payload["dlp_policy"].get("allow_cross_thread_content", True),
            allowed_dlp_tags=payload["dlp_policy"].get("allowed_dlp_tags")
        )

    return MeshRequest(
        request_id=payload["request_id"],
        threads=threads,
        target_anchor_seed=payload.get("target_anchor_seed"),
        dlp_policy=dlp_policy,
        caller_context=payload.get("caller_context")
    )


def load_constellink_spec(path: str = DEFAULT_SPEC_PATH) -> dict:
    """Load the CONSTELLINK JSON spec for tooling

    Args:
        path: Path to the spec file (relative to project root)

    Returns:
        dict: Parsed JSON spec

    Raises:
        FileNotFoundError: If spec file not found
        json.JSONDecodeError: If spec file is not valid JSON
    """
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"CONSTELLINK spec not found at: {path}")

    with open(spec_path, 'r', encoding='utf-8') as f:
        return json.load(f)
