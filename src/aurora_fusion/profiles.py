"""Fusion runtime profiles for recomposing Aurora subsystems."""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class FusionProfile:
    name: str
    symbolic_dim: int
    num_qubits: int
    glyph_enabled: bool
    chat_tooling_enabled: bool
    description: str


FUSION_PROFILES: Dict[str, FusionProfile] = {
    "stability": FusionProfile(
        name="stability",
        symbolic_dim=256,
        num_qubits=4,
        glyph_enabled=False,
        chat_tooling_enabled=False,
        description="Lowest runtime risk. Native engines only.",
    ),
    "balanced": FusionProfile(
        name="balanced",
        symbolic_dim=512,
        num_qubits=8,
        glyph_enabled=True,
        chat_tooling_enabled=False,
        description="Recommended default. Native core + glyph synthesis.",
    ),
    "extended": FusionProfile(
        name="extended",
        symbolic_dim=512,
        num_qubits=8,
        glyph_enabled=True,
        chat_tooling_enabled=True,
        description="Adds agent-mode tool orchestration on top of balanced profile.",
    ),
}


def resolve_profile(profile_name: str) -> FusionProfile:
    """Resolve a profile name with a safe default."""
    return FUSION_PROFILES.get(profile_name, FUSION_PROFILES["balanced"])

