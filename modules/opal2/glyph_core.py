"""Opal2 Glyph Core
from pathlib import Path
import time
===================

This module provides glyph generation utilities that combine geometric algebra
and quantum symbolic vectors. It acts as a lightweight "graphics card" for the
hybrid quantum symbolic processor.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

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
            "quantum_vector": qvec,  # Include the full qvec object for backward compatibility
            "vector": qvec.vector,  # Retain the vector attribute for new functionality
            "multivector": str(mv),
        }


class GlyphCore:
    """Enhanced glyph core with async support for the Opal2 API"""

    def __init__(self, dim: int = 8, config_path: str | None = None):
        self.logger = logging.getLogger(__name__)
        
        self.generator = GlyphGenerator(dim=dim, config_path=config_path)
        
        self.dim = dim

    async def generate_async(
        self,
        expression: Dict[str, Any],
        style_params: Dict[str, Any] | None = None,
        quantum_enhancement: bool = True,
    ) -> Dict[str, Any]:
        """Async glyph generation with quantum enhancement"""
        try:
            # Extract symbol from expression
        symbol = expression.get("symbol", str(expression))

            # Generate base glyph
            base_glyph = await asyncio.to_thread(self.generator.generate, symbol)

            # Apply style parameters
            if style_params:
                base_glyph["style"] = style_params

            # Apply quantum enhancement
            if quantum_enhancement:
                base_glyph["quantum_enhanced"] = True
                enhancement_factor = 1.5
                if style_params:
        enhancement_factor = style_params.get("enhancement_factor", 1.5)
                
        base_glyph["enhancement_factor"] = enhancement_factor

            # Add metadata
            base_glyph.update(
                {
                    "generated_at": asyncio.get_event_loop().time(),
                    "version": "2.0.0",
                    "type": "quantum_glyph",
                }
            )

            
        return base_glyph

        except Exception as e:
            self.logger.error(f"Error generating glyph: {e}")
            
        raise

    async def test_generation(self) -> Dict[str, Any]:
        """Test glyph generation functionality"""
        try:
            test_expression = {"symbol": "test"}
        result = await self.generate_async(test_expression)            
        return {
                "success": True,
                "test_symbol": "test",
                "generated_keys": list(result.keys()),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get glyph core capabilities"""
        return {
            "dimension": self.dim,
            "quantum_support": True,
            "async_support": True,
            "supported_types": ["quantum_glyph", "geometric_glyph", "symbolic_glyph"],
        }
