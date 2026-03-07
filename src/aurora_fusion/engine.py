"""Composable fusion engine built from high-value Aurora modules."""

from typing import Any, Dict, List, Optional

from modules.reflective_autonomy.symbolic_tagging_engine import classify_thread_content
from modules.reflective_autonomy.threadcore_tagging import tag_thread_context
from src.core.native_symbolic_anchor import NativeSymbolicCPUAnchor
from src.core.native_vsa import NativeSymbolicVector
from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration

from .memory import AuroraMemoryOptimizer
from .module_map import get_high_value_module_matrix
from .profiles import resolve_profile

try:
    from modules.symbolic_core.vsa import SymbolicVector
except Exception:  # pragma: no cover - exercised only in dependency-constrained envs
    class SymbolicVector:  # type: ignore[override]
        """Fallback adapter around the native symbolic vector implementation."""

        @classmethod
        def from_symbol(cls, symbol: str, dim: int = 512) -> NativeSymbolicVector:
            return NativeSymbolicVector.from_symbol(symbol, dim=dim)


try:
    from modules.opal2.glyph_core import GlyphCore
except Exception:  # pragma: no cover - exercised only in dependency-constrained envs
    class GlyphCore:  # type: ignore[override]
        """Fallback glyph core used when optional Opal2 deps are unavailable."""

        def __init__(self, dim: int = 8, config_path: Optional[str] = None):
            self.dim = dim
            self.config_path = config_path

        async def generate_async(
            self,
            expression: Dict[str, Any],
            style_params: Optional[Dict[str, Any]] = None,
            quantum_enhancement: bool = True,
        ) -> Dict[str, Any]:
            return {
                "symbol": expression.get("symbol", str(expression)),
                "vector": [],
                "multivector": "fallback_glyph",
                "style": style_params or {},
                "quantum_enhanced": quantum_enhancement,
                "version": "fallback",
                "type": "quantum_glyph",
            }


class AuroraFusionEngine:
    """New composition runtime that reuses proven Aurora components."""

    def __init__(self, profile: str = "balanced"):
        self.profile = resolve_profile(profile)
        self.module_matrix = get_high_value_module_matrix()

        self.anchor = NativeSymbolicCPUAnchor(
            num_qubits=self.profile.num_qubits,
            symbolic_dim=self.profile.symbolic_dim,
        )
        self.memory_optimizer = AuroraMemoryOptimizer(anchor=self.anchor, symbolic_dim=self.profile.symbolic_dim)
        self.glyph_core = GlyphCore(dim=min(8, self.profile.num_qubits)) if self.profile.glyph_enabled else None
        self.agent_tools = ChatGPTAgentModeIntegration() if self.profile.chat_tooling_enabled else None

    def _derive_concepts(self, prompt: str, limit: int = 6) -> List[str]:
        words = [token.strip(".,:;!?()[]{}\"'").lower() for token in prompt.split()]
        words = [word for word in words if word and len(word) > 2]
        deduped: List[str] = []
        for word in words:
            if word not in deduped:
                deduped.append(word)
            if len(deduped) >= limit:
                break
        return deduped or ["aurora", "symbolic", "anchor"]

    def _build_symbolic_vectors(self, concepts: List[str]) -> Dict[str, Any]:
        typed_vectors = {
            concept: SymbolicVector.from_symbol(concept, dim=self.profile.symbolic_dim).vector for concept in concepts
        }
        native_vectors = {
            concept: NativeSymbolicVector.from_symbol(concept, dim=self.profile.symbolic_dim).vector for concept in concepts
        }
        return {
            "typed_vectors": typed_vectors,
            "native_vectors": native_vectors,
            "vector_count": len(concepts),
            "dimension": self.profile.symbolic_dim,
        }

    async def compose(self, prompt: str, concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run a complete fusion pass and return a structured build artifact."""
        concept_set = concepts or self._derive_concepts(prompt)
        symbolic_classification = classify_thread_content(prompt)
        threadcore_classification = tag_thread_context(prompt)
        memory_owner = "AuroraFusionEngine"

        quantum_operations = [
            {"type": "hadamard", "qubit": 0},
            {"type": "cnot", "qubit": 0, "target": 1 if self.profile.num_qubits > 1 else 0},
            {"type": "rotation", "qubit": 0, "angle": 0.78539816339},
        ]

        anchored = self.anchor.anchor_quantum_symbolic_state(
            {"symbolic_concepts": concept_set, "quantum_operations": quantum_operations}
        )
        symbolic_vectors = self._build_symbolic_vectors(concept_set)
        stored_prompt = self.memory_optimizer.remember(
            owner=memory_owner,
            content=prompt,
            importance=min(10.0, 6.0 + (len(concept_set) / 2.0)),
            layer="L2",
            source="fusion.compose.prompt",
            tags=concept_set,
            anchor_ids=[self.anchor.anchor_protocols[0], symbolic_classification["primary_folder"].upper()],
            metadata={"profile": self.profile.name},
        )
        self.memory_optimizer.remember(
            owner=memory_owner,
            content=(
                "THREADSYNC classification snapshot "
                f"symbolic={symbolic_classification['primary_folder']} "
                f"threadcore={threadcore_classification['primary_folder']} "
                f"priority={threadcore_classification['priority']}"
            ),
            importance=7.5,
            layer="L3",
            source="fusion.compose.classification",
            tags=[
                symbolic_classification["primary_folder"],
                threadcore_classification["primary_folder"],
                threadcore_classification["priority"],
            ],
            anchor_ids=[self.anchor.anchor_protocols[0], threadcore_classification["primary_folder"].upper()],
            metadata={
                "symbolic": symbolic_classification,
                "threadcore": threadcore_classification,
            },
        )
        memory_hits = self.memory_optimizer.retrieve_context(memory_owner, prompt, top_k=4)
        continuity_snapshot = self.memory_optimizer.build_continuity_snapshot(memory_owner)

        glyph_payload: Optional[Dict[str, Any]] = None
        if self.glyph_core is not None:
            glyph_payload = await self.glyph_core.generate_async({"symbol": threadcore_classification["primary_folder"]})

        tool_manifest: Optional[Dict[str, Any]] = None
        if self.agent_tools is not None:
            tool_manifest = await self.agent_tools.discover_tools()

        return {
            "profile": self.profile.name,
            "prompt": prompt,
            "concepts": concept_set,
            "classification": {
                "symbolic_tagging_engine": symbolic_classification,
                "threadcore_tagger": threadcore_classification,
            },
            "symbolic_vectors": symbolic_vectors,
            "hybrid_anchor": anchored,
            "memory_optimization": {
                "doctrine": self.memory_optimizer.doctrine.to_dict(),
                "stored_prompt": stored_prompt.to_dict(),
                "retrieved_context": [hit.to_dict() for hit in memory_hits],
                "continuity_snapshot": continuity_snapshot,
            },
            "glyph_payload": glyph_payload,
            "agent_tool_manifest": tool_manifest,
            "recommended_modules": [
                {
                    "module_path": module.module_path,
                    "capability": module.capability,
                    "composite_score": module.composite_score,
                    "evidence": module.evidence,
                }
                for module in self.module_matrix[:8]
            ],
        }
