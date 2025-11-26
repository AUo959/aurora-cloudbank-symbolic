"""
ORACULITH - Symbolic Forecast Engine

Anchored, DLP-aware symbolic forecasting over multi-thread CONSTELLINK meshes.
Produces structured SymbolicForecast objects with metaphors, risk/entropy analysis,
and hash-sealed manifests for reliquary indexing.

Anchors: EOS_SEED_ORION
Ethics: Picard_Delta_3
"""

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from symbolic.constellink import ConstellinkMesh, mesh_from_dict


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
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    hash_bytes = hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()
    return f"sha256:{hash_bytes}"


@dataclass
class EchoDescriptor:
    """Additional reflective context for forecasting."""

    source: str
    echo_text: str
    thread_id: Optional[str] = None
    entropy_hint: Optional[float] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate entropy_hint range."""
        if self.entropy_hint is not None:
            if not (0.0 <= self.entropy_hint <= 1.0):
                raise ValueError("entropy_hint must be between 0.0 and 1.0")


@dataclass
class OraculithDlpPolicy:
    """DLP policy controls for forecast generation."""

    allow_explicit_failure_modes: bool = False
    allow_cross_thread_attribution: bool = False
    sensitive_tags: Optional[List[str]] = None


@dataclass
class OraculithForecastContext:
    """Input context for forecast generation."""

    request_id: str
    mesh: ConstellinkMesh
    echoes: Optional[List[EchoDescriptor]] = None
    forecast_horizon: Optional[str] = None
    forecast_focus: Optional[List[str]] = None
    dlp_policy: Optional[OraculithDlpPolicy] = None
    caller_context: Optional[Dict[str, Any]] = None


@dataclass
class SupportingSignals:
    """Evidence and signals supporting the forecast."""

    mesh_entropy_snapshot: Dict[str, Any]
    dominant_threads: List[str] = field(default_factory=list)
    dominant_echoes: List[str] = field(default_factory=list)


@dataclass
class OraculithDlpEffectivePolicy:
    """Effective DLP policy applied during forecast."""

    allow_explicit_failure_modes: bool
    allow_cross_thread_attribution: bool
    sensitive_tags: Optional[List[str]] = None
    policy_notes: str = ""


@dataclass
class MeshReference:
    """Reference to source mesh with integrity validation."""

    mesh_id: str
    mesh_state_hash: str
    anchor_seed: str
    drift_flag: str


@dataclass
class ForecastManifest:
    """DLP manifest for forecast integrity and traceability."""

    version: str
    export_time_utc: str
    anchor_seed: str
    ethics_protocol: str
    symbolic_tags: List[str]
    dlp_tags: List[str]
    state_hash: str


@dataclass
class SymbolicForecast:
    """Complete symbolic forecast with DLP compliance and hash sealing."""

    forecast_id: str
    created_at_utc: str
    anchor_seed: str
    ethics_protocol: str
    metaphor: str
    risk_level: str  # low, medium, high, unknown
    entropy_trend: str  # rising, falling, stable, unknown
    supporting_signals: SupportingSignals
    dlp_effective_policy: OraculithDlpEffectivePolicy
    mesh_reference: MeshReference
    forecast_manifest: ForecastManifest
    summary: Optional[str] = None
    anchor_alignment: Optional[float] = None
    focus: Optional[List[str]] = None
    divergent_truths: Optional[List[str]] = None
    caller_context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert forecast to dictionary for JSON export."""
        result = {
            "forecast_id": self.forecast_id,
            "created_at_utc": self.created_at_utc,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "metaphor": self.metaphor,
            "risk_level": self.risk_level,
            "entropy_trend": self.entropy_trend,
            "supporting_signals": asdict(self.supporting_signals),
            "dlp_effective_policy": asdict(self.dlp_effective_policy),
            "mesh_reference": asdict(self.mesh_reference),
            "forecast_manifest": asdict(self.forecast_manifest)
        }

        # Add optional fields if present
        if self.summary:
            result["summary"] = self.summary
        if self.anchor_alignment is not None:
            result["anchor_alignment"] = self.anchor_alignment
        if self.focus:
            result["focus"] = self.focus
        if self.divergent_truths:
            result["divergent_truths"] = self.divergent_truths
        if self.caller_context:
            result["caller_context"] = self.caller_context

        return result

    def glyphcard(self) -> str:
        """
        Generate a short, human-readable summary of the forecast.

        Returns:
            Multi-line string with key forecast details
        """
        lines = [
            "=== ORACULITH Forecast Glyphcard ===",
            f"ID: {self.forecast_id}",
            f"Risk: {self.risk_level.upper()} | Entropy: {self.entropy_trend.upper()}",
            f"Anchor Alignment: {self.anchor_alignment if self.anchor_alignment is not None else 'N/A'}",
            "",
            f"Metaphor: {self.metaphor[:80]}{'...' if len(self.metaphor) > 80 else ''}",
        ]

        if self.divergent_truths:
            lines.append("")
            lines.append(f"⚠️  Divergent Truths: {len(self.divergent_truths)}")
            for dt in self.divergent_truths[:3]:  # Show first 3
                lines.append(f"  - {dt[:70]}{'...' if len(dt) > 70 else ''}")

        lines.append("")
        lines.append(f"Mesh: {self.mesh_reference.mesh_id} (drift={self.mesh_reference.drift_flag})")
        lines.append("=================================")

        return "\n".join(lines)


class OraculithEngine:
    """
    Symbolic forecast engine that consumes CONSTELLINK meshes.

    Produces DLP-aware forecasts with metaphorical analysis, risk assessment,
    and hash-sealed manifests.
    """

    def __init__(
        self,
        anchor_seed: str = DEFAULT_ANCHOR_SEED,
        ethics_protocol: str = DEFAULT_ETHICS_PROTOCOL
    ):
        """
        Initialize the ORACULITH engine.

        Args:
            anchor_seed: Default anchor seed for forecasts
            ethics_protocol: Default ethics protocol
        """
        self.anchor_seed = anchor_seed
        self.ethics_protocol = ethics_protocol

    def forecast(self, context: OraculithForecastContext) -> SymbolicForecast:
        """
        Generate a symbolic forecast from the provided context.

        Args:
            context: OraculithForecastContext with mesh and optional echoes

        Returns:
            SymbolicForecast with metaphor, risk/entropy analysis, and sealed manifest
        """
        forecast_id = f"forecast_{uuid.uuid4().hex[:12]}"
        created_at = _utc_now_iso()

        mesh = context.mesh
        dlp_policy = context.dlp_policy or OraculithDlpPolicy()

        # Extract entropy info from mesh
        entropy_summary = mesh.entropy_summary
        entropy_mean = entropy_summary.entropy_mean
        drift_flag = entropy_summary.drift_flag

        # Derive entropy trend
        if drift_flag == "divergent" or entropy_mean > 0.7:
            entropy_trend = "rising"
        elif drift_flag == "stable" or entropy_mean < 0.3:
            entropy_trend = "stable"
        elif entropy_mean < 0.5:
            entropy_trend = "falling"
        else:
            entropy_trend = "unknown"

        # Derive risk level
        if drift_flag == "divergent" and entropy_mean > 0.6:
            risk_level = "high"
        elif drift_flag == "moderate" or entropy_mean > 0.5:
            risk_level = "medium"
        elif drift_flag == "stable" and entropy_mean < 0.4:
            risk_level = "low"
        else:
            risk_level = "unknown"

        # Compute anchor alignment heuristic
        thread_alignments = [
            t.anchor_alignment for t in mesh.threads
            if t.anchor_alignment is not None
        ]
        if thread_alignments:
            anchor_alignment = sum(thread_alignments) / len(thread_alignments)
        else:
            # Default based on drift flag
            if drift_flag == "stable":
                anchor_alignment = 0.85
            elif drift_flag == "moderate":
                anchor_alignment = 0.6
            else:
                anchor_alignment = 0.3

        # Select dominant threads and echoes
        dominant_threads = []
        dominant_echoes = []

        if dlp_policy.allow_cross_thread_attribution:
            # Include thread IDs if policy allows
            # Select threads with highest entropy or specific tags
            sorted_threads = sorted(
                mesh.threads,
                key=lambda t: t.entropy_hint if t.entropy_hint else 0.0,
                reverse=True
            )
            dominant_threads = [t.thread_id for t in sorted_threads[:3]]

        if context.echoes:
            # Select echoes with high entropy or matching focus
            sorted_echoes = sorted(
                context.echoes,
                key=lambda e: e.entropy_hint if e.entropy_hint else 0.0,
                reverse=True
            )
            dominant_echoes = [e.source for e in sorted_echoes[:3]]

        # Check for sensitive tags
        policy_notes = []
        if dlp_policy.sensitive_tags:
            mesh_tags = set()
            for thread in mesh.threads:
                mesh_tags.update(thread.tags)

            sensitive_found = set(dlp_policy.sensitive_tags) & mesh_tags
            if sensitive_found:
                policy_notes.append(
                    f"Sensitive tags detected: {', '.join(sensitive_found)}. "
                    "Specificity reduced in supporting signals."
                )
                # Redact dominant threads/echoes
                dominant_threads = []
                dominant_echoes = []

        # Generate metaphor based on risk and entropy
        metaphor = self._generate_metaphor(risk_level, entropy_trend, drift_flag)

        # Generate summary if policy allows explicit failure modes
        summary = None
        if dlp_policy.allow_explicit_failure_modes and risk_level in ["high", "medium"]:
            summary = self._generate_summary(risk_level, entropy_trend, entropy_mean)
        elif not dlp_policy.allow_explicit_failure_modes and risk_level == "high":
            policy_notes.append(
                "Explicit failure modes suppressed per DLP policy. Favor metaphor interpretation."
            )

        # Detect divergent truths (inconsistencies)
        divergent_truths = []

        # Check for drift vs. entropy inconsistency
        if drift_flag == "divergent" and entropy_mean < 0.3:
            divergent_truths.append(
                "Mesh marked as divergent but entropy_mean is low. Possible stale flag."
            )
        elif drift_flag == "stable" and entropy_mean > 0.7:
            divergent_truths.append(
                "Mesh marked as stable but entropy_mean is high. Possible drift underestimation."
            )

        # Check for missing mesh state hash
        if not mesh.mesh_manifest.state_hash or mesh.mesh_manifest.state_hash == "":
            divergent_truths.append("Mesh manifest missing state_hash. Integrity cannot be verified.")

        # Check for conflicting echoes (if provided)
        if context.echoes:
            echo_entropies = [e.entropy_hint for e in context.echoes if e.entropy_hint is not None]
            if echo_entropies and len(echo_entropies) > 1:
                echo_mean = sum(echo_entropies) / len(echo_entropies)
                echo_variance = sum((e - echo_mean)**2 for e in echo_entropies) / len(echo_entropies)
                echo_std = echo_variance ** 0.5
                if echo_std > 0.3:
                    divergent_truths.append(
                        f"High variance in echo entropies (std={echo_std:.2f}). Conflicting signals."
                    )

        # Build supporting signals
        supporting_signals = SupportingSignals(
            mesh_entropy_snapshot={
                "entropy_mean": entropy_mean,
                "entropy_std": entropy_summary.entropy_std,
                "drift_flag": drift_flag,
                "thread_count": entropy_summary.thread_count
            },
            dominant_threads=dominant_threads,
            dominant_echoes=dominant_echoes
        )

        # Build effective DLP policy
        dlp_effective_policy = OraculithDlpEffectivePolicy(
            allow_explicit_failure_modes=dlp_policy.allow_explicit_failure_modes,
            allow_cross_thread_attribution=dlp_policy.allow_cross_thread_attribution,
            sensitive_tags=dlp_policy.sensitive_tags,
            policy_notes=" ".join(policy_notes) if policy_notes else ""
        )

        # Build mesh reference
        mesh_reference = MeshReference(
            mesh_id=mesh.mesh_id,
            mesh_state_hash=mesh.mesh_manifest.state_hash,
            anchor_seed=mesh.anchor_seed,
            drift_flag=drift_flag
        )

        # Build forecast payload (excluding manifest for hashing)
        forecast_payload = {
            "forecast_id": forecast_id,
            "created_at_utc": created_at,
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "metaphor": metaphor,
            "risk_level": risk_level,
            "entropy_trend": entropy_trend,
            "anchor_alignment": anchor_alignment,
            "supporting_signals": asdict(supporting_signals),
            "dlp_effective_policy": asdict(dlp_effective_policy),
            "mesh_reference": asdict(mesh_reference)
        }

        if summary:
            forecast_payload["summary"] = summary
        if context.forecast_focus:
            forecast_payload["focus"] = context.forecast_focus
        if divergent_truths:
            forecast_payload["divergent_truths"] = divergent_truths
        if context.caller_context:
            forecast_payload["caller_context"] = context.caller_context

        # Compute state hash
        state_hash = _sha256_of_json_payload(forecast_payload)

        # Build forecast manifest
        forecast_manifest = ForecastManifest(
            version="1.0.0",
            export_time_utc=_utc_now_iso(),
            anchor_seed=self.anchor_seed,
            ethics_protocol=self.ethics_protocol,
            symbolic_tags=["oraculith", "symbolic-forecast", "metaphor-generation"],
            dlp_tags=["forecast", "mesh-consumer", "risk-analysis"],
            state_hash=state_hash
        )

        # Build final forecast
        return SymbolicForecast(
            forecast_id=forecast_id,
            created_at_utc=created_at,
            anchor_seed=self.anchor_seed,
            ethics_protocol=self.ethics_protocol,
            metaphor=metaphor,
            summary=summary,
            risk_level=risk_level,
            entropy_trend=entropy_trend,
            anchor_alignment=anchor_alignment,
            focus=context.forecast_focus,
            supporting_signals=supporting_signals,
            dlp_effective_policy=dlp_effective_policy,
            divergent_truths=divergent_truths if divergent_truths else None,
            caller_context=context.caller_context,
            mesh_reference=mesh_reference,
            forecast_manifest=forecast_manifest
        )

    def _generate_metaphor(self, risk_level: str, entropy_trend: str, drift_flag: str) -> str:
        """
        Generate a symbolic metaphor based on risk and entropy.

        Args:
            risk_level: low, medium, high, unknown
            entropy_trend: rising, falling, stable, unknown
            drift_flag: stable, moderate, divergent, unknown

        Returns:
            Metaphorical string
        """
        # Metaphor templates keyed on risk + entropy
        if risk_level == "low" and entropy_trend == "stable":
            return "The river has found its channel, flowing clear and steady."
        elif risk_level == "low" and entropy_trend == "falling":
            return "The storm passes; calm waters emerge beneath clearing skies."
        elif risk_level == "medium" and entropy_trend == "stable":
            return "The ship sails through familiar fog, vigilant but confident."
        elif risk_level == "medium" and entropy_trend == "rising":
            return "Clouds gather on the horizon; the wise captain checks the sails."
        elif risk_level == "high" and entropy_trend == "rising":
            return "Lightning splits the sky; the reef ahead demands immediate course correction."
        elif risk_level == "high" and entropy_trend == "stable":
            return "The eye of the hurricane: deceptive calm masking surrounding chaos."
        elif drift_flag == "divergent":
            return "The compass spins wildly; multiple truths compete for navigation."
        else:
            return "The path ahead shrouded in mist; proceed with caution and symbolic awareness."

    def _generate_summary(self, risk_level: str, entropy_trend: str, entropy_mean: float) -> str:
        """
        Generate a literal summary (only when DLP policy allows explicit failure modes).

        Args:
            risk_level: low, medium, high, unknown
            entropy_trend: rising, falling, stable, unknown
            entropy_mean: Numerical entropy value

        Returns:
            Summary string
        """
        if risk_level == "high":
            return (
                f"High risk detected with {entropy_trend} entropy trend "
                f"(mean={entropy_mean:.2f}). Immediate attention recommended. "
                f"Review mesh threads for divergent patterns and consider mitigation strategies."
            )
        elif risk_level == "medium":
            return (
                f"Moderate risk with {entropy_trend} entropy trend "
                f"(mean={entropy_mean:.2f}). Monitor situation closely. "
                f"Ensure alignment protocols are active and drift indicators are tracked."
            )
        else:
            return (
                f"Risk level {risk_level} with {entropy_trend} trend. "
                f"Maintain standard operational awareness."
            )


def forecast_context_from_dict(
    payload: Dict[str, Any],
    *,
    validate_mesh: bool = True
) -> OraculithForecastContext:
    """
    Build an OraculithForecastContext from raw JSON/dict.

    Args:
        payload: Dictionary with context data
        validate_mesh: Whether to validate mesh hash

    Returns:
        OraculithForecastContext instance

    Raises:
        ValueError: If required fields are missing or mesh is invalid
    """
    if "request_id" not in payload:
        raise ValueError("Missing required field: request_id")
    if "mesh" not in payload:
        raise ValueError("Missing required field: mesh")

    # Reconstruct mesh
    mesh = mesh_from_dict(payload["mesh"], validate_hash=validate_mesh)

    # Reconstruct echoes if present
    echoes = None
    if "echoes" in payload and payload["echoes"]:
        echoes = [
            EchoDescriptor(
                source=e["source"],
                echo_text=e["echo_text"],
                thread_id=e.get("thread_id"),
                entropy_hint=e.get("entropy_hint"),
                tags=e.get("tags", [])
            )
            for e in payload["echoes"]
        ]

    # Reconstruct DLP policy if present
    dlp_policy = None
    if "dlp_policy" in payload:
        p = payload["dlp_policy"]
        dlp_policy = OraculithDlpPolicy(
            allow_explicit_failure_modes=p.get("allow_explicit_failure_modes", False),
            allow_cross_thread_attribution=p.get("allow_cross_thread_attribution", False),
            sensitive_tags=p.get("sensitive_tags")
        )

    return OraculithForecastContext(
        request_id=payload["request_id"],
        mesh=mesh,
        echoes=echoes,
        forecast_horizon=payload.get("forecast_horizon"),
        forecast_focus=payload.get("forecast_focus"),
        dlp_policy=dlp_policy,
        caller_context=payload.get("caller_context")
    )
