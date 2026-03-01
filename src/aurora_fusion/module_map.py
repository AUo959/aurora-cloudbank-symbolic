"""High-value Aurora module matrix for fusion composition."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ModuleSignal:
    module_path: str
    capability: str
    value_score: int
    stability_score: int
    evidence: str

    @property
    def composite_score(self) -> int:
        return self.value_score + self.stability_score


def get_high_value_module_matrix() -> List[ModuleSignal]:
    """Curated module list biased toward tested and dependency-safe components."""
    matrix = [
        ModuleSignal(
            module_path="src.core.native_quantum",
            capability="dependency-free quantum simulation",
            value_score=10,
            stability_score=10,
            evidence="covered by native implementation test suite",
        ),
        ModuleSignal(
            module_path="src.core.native_vsa",
            capability="deterministic symbolic vectors + memory",
            value_score=10,
            stability_score=10,
            evidence="covered by native implementation test suite",
        ),
        ModuleSignal(
            module_path="src.core.native_symbolic_anchor",
            capability="hybrid quantum-symbolic anchoring and sealing",
            value_score=10,
            stability_score=9,
            evidence="covered by native implementation test suite",
        ),
        ModuleSignal(
            module_path="modules.symbolic_core.vsa",
            capability="pydantic-backed symbolic vector model",
            value_score=9,
            stability_score=9,
            evidence="covered by VSA tests",
        ),
        ModuleSignal(
            module_path="modules.reflective_autonomy.symbolic_tagging_engine",
            capability="semantic thread classification",
            value_score=8,
            stability_score=9,
            evidence="covered by tagging tests",
        ),
        ModuleSignal(
            module_path="modules.reflective_autonomy.threadcore_tagging",
            capability="priority-aware thread routing",
            value_score=8,
            stability_score=9,
            evidence="covered by threadcore tagging tests",
        ),
        ModuleSignal(
            module_path="modules.opal2.glyph_core",
            capability="symbolic + geometric glyph synthesis",
            value_score=8,
            stability_score=8,
            evidence="covered by Opal2 tests",
        ),
        ModuleSignal(
            module_path="src.integrations.chatgpt_agent_mode",
            capability="tool/agent orchestration interface",
            value_score=9,
            stability_score=8,
            evidence="covered by chatgpt agent mode tests",
        ),
        ModuleSignal(
            module_path="services.aif_hub",
            capability="real-time websocket broadcast fabric",
            value_score=7,
            stability_score=8,
            evidence="covered by AIF hub tests",
        ),
        ModuleSignal(
            module_path="modules.cask.analysis",
            capability="structured system analysis output",
            value_score=7,
            stability_score=8,
            evidence="covered by CASK analysis tests",
        ),
    ]

    return sorted(matrix, key=lambda item: item.composite_score, reverse=True)

