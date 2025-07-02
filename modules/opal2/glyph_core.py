"""Opal2 Glyph Core
===================

This module provides glyph generation utilities that combine geometric algebra
and quantum symbolic vectors. It acts as a lightweight "graphics card" for the
hybrid quantum symbolic processor.
"""

from typing import Dict, Any
from pathlib import Path
import yaml

from modules.symbolic_core.geometric_algebra import GeometricAlgebra
from modules.symbolic_core.quantum_vsa import QuantumSymbolicVector


DEFAULT_CONFIG = Path(__file__).resolve().parents[2] / "config" / "opal2_graphics.yaml"


class GlyphGenerator:
    """Generate glyph structures using geometric algebra and quantum vectors."""

    def __init__(self, dim: int = 8, config_path: str | None = None):
        if config_path is None:
            path = DEFAULT_CONFIG
        else:
            path = Path(config_path)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                cfg: Dict[str, Any] = yaml.safe_load(f) or {}
            dim = cfg.get("opal2", {}).get("graphics_card", {}).get("default_dim", dim)
        self.dim = dim
        self.ga = GeometricAlgebra()

    def generate(self, symbol: str) -> Dict[str, object]:
        """Generate a glyph representation for ``symbol``.

        Returns a dictionary with the quantum symbolic vector and a textual
        representation of the geometric multivector.
        """
        qvec = QuantumSymbolicVector(symbol, dim=self.dim)

        # Build a simple multivector pattern using ASCII codes
        mv = 0
        blades = [self.ga.blades["e1"], self.ga.blades["e2"], self.ga.blades["e3"]]
        for idx, ch in enumerate(symbol):
            blade = blades[idx % 3]
            mv = mv + (1 + (ord(ch) % 3)) * blade
        mv = self.ga.mult(mv, blades[0])

        return {
            "symbol": symbol,
            "vector": qvec.vector.tolist(),
            "multivector": self.ga.pretty(mv),
        }
