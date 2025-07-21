#!/usr/bin/env python3
"""
Opal2 Modular System - Quantum Renderer
Advanced quantum-enhanced rendering with modular plugin support
"""

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np

from ...symbolic.geometric_algebra import GeometricAlgebra
from ...symbolic.quantum_symbolic_vector import QuantumSymbolicVector

class RenderMode(Enum):
    """Rendering mode enumeration"""

    STATIC = "static"
    ANIMATED = "animated"
    INTERACTIVE = "interactive"
    REALTIME = "realtime"

class QuantumState(Enum):
    """Quantum enhancement state"""

    DISABLED = "disabled"
    BASIC = "basic"
    ENHANCED = "enhanced"
    SUPERPOSITION = "superposition"

@dataclass
class RenderContext:
    """Render context containing all rendering parameters"""

    glyph_data: Dict[str, Any]
    dimensions: Dict[str, int] = field(
        default_factory=lambda: {"width": 800, "height": 600}
    )
    mode: RenderMode = RenderMode.STATIC
    quantum_state: QuantumState = QuantumState.ENHANCED
    quantum_params: Dict[str, float] = field(default_factory=dict)
    style_params: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default parameters"""
        if not self.quantum_params:
            self.quantum_params = {
                "coherence_factor": 0.8,
                "entanglement_strength": 0.6,
                "superposition_depth": 3,
                "decoherence_rate": 0.1,
            }

@dataclass
class RenderResult:
    """Render result containing output and metadata"""

    output: Union[str, bytes, Dict[str, Any]]
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    render_time: float = 0.0
    quantum_metrics: Dict[str, float] = field(default_factory=dict)
    cache_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "output": self.output,
            "format": self.format,
            "metadata": self.metadata,
            "render_time": self.render_time,
            "quantum_metrics": self.quantum_metrics,
            "cache_key": self.cache_key,
        }

class QuantumRenderer:
    """
    Advanced quantum-enhanced renderer with modular plugin support
    """

    def __init__(self):
        self.geometric_algebra = GeometricAlgebra()
        self.quantum_vector = QuantumSymbolicVector()
        self.active_contexts: Dict[str, RenderContext] = {}
        self.render_plugins: Dict[str, Callable] = {}
        self.performance_metrics: Dict[str, List[float]] = {}

        # Initialize default quantum parameters
        self.default_quantum_config = {
            "coherence_preservation": True,
            "entanglement_rendering": True,
            "superposition_visualization": True,
            "quantum_interference": True,
            "decoherence_simulation": False,
        }

        # Register built-in renderers
        self._register_builtin_renderers()

    def _register_builtin_renderers(self):
        """Register built-in rendering plugins"""
        self.render_plugins.update(
            {
                "webgl": self._render_webgl,
                "canvas": self._render_canvas,
                "svg": self._render_svg,
                "quantum_field": self._render_quantum_field,
                "holographic": self._render_holographic,
                "geometric_algebra": self._render_geometric_algebra,
            }
        )

    async def render_async(
        self,
        glyph_data: Dict[str, Any],
        renderer: str = "webgl",
        dimensions: Dict[str, int] = None,
        quantum_params: Dict[str, float] = None,
        **kwargs,
    ) -> RenderResult:
        """
        Asynchronously render a glyph with quantum enhancement

        Args:
            glyph_data: Glyph configuration data
            renderer: Renderer type to use
            dimensions: Render dimensions
            quantum_params: Quantum enhancement parameters
            **kwargs: Additional rendering parameters

        Returns:
            RenderResult containing the rendered output
        """
        start_time = asyncio.get_event_loop().time()

        # Create render context
        context = RenderContext(
            glyph_data=glyph_data,
            dimensions=dimensions or {"width": 800, "height": 600},
            quantum_params=quantum_params or {},
            **kwargs,
        )

        # Generate unique context ID
        context_id = f"render_{uuid.uuid4().hex[:8]}"
        self.active_contexts[context_id] = context

        try:
            # Apply quantum enhancement
            enhanced_data = await self._apply_quantum_enhancement(context)

            # Get renderer plugin
            if renderer not in self.render_plugins:
                raise ValueError(f"Renderer '{renderer}' not available")

            renderer_func = self.render_plugins[renderer]

            # Perform rendering
            if asyncio.iscoroutinefunction(renderer_func):
                output = await renderer_func(enhanced_data, context)
            else:
                output = renderer_func(enhanced_data, context)

            # Calculate render time
            render_time = asyncio.get_event_loop().time() - start_time

            # Generate quantum metrics
            quantum_metrics = await self._calculate_quantum_metrics(
                context, enhanced_data
            )

            # Create result
            result = RenderResult(
                output=output,
                format=renderer,
                metadata={
                    "context_id": context_id,
                    "dimensions": context.dimensions,
                    "quantum_state": context.quantum_state.value,
                    "timestamp": datetime.now().isoformat(),
                },
                render_time=render_time,
                quantum_metrics=quantum_metrics,
                cache_key=f"qrender_{context_id}",
            )

            # Update performance metrics
            self._update_performance_metrics(renderer, render_time)

            return result

        finally:
            # Clean up context
            if context_id in self.active_contexts:
                del self.active_contexts[context_id]

    async def _apply_quantum_enhancement(
        self, context: RenderContext
    ) -> Dict[str, Any]:
        """Apply quantum enhancement to glyph data"""
        enhanced_data = context.glyph_data.copy()

        if context.quantum_state == QuantumState.DISABLED:
            return enhanced_data

        # Apply coherence factor
        coherence = context.quantum_params.get("coherence_factor", 0.8)
        enhanced_data["coherence_matrix"] = self._generate_coherence_matrix(
            enhanced_data, coherence
        )

        # Apply entanglement
        if context.quantum_state in [QuantumState.ENHANCED, QuantumState.SUPERPOSITION]:
            entanglement = context.quantum_params.get("entanglement_strength", 0.6)
            enhanced_data["entanglement_data"] = self._generate_entanglement_data(
                enhanced_data, entanglement
            )

        # Apply superposition
        if context.quantum_state == QuantumState.SUPERPOSITION:
            superposition_depth = context.quantum_params.get("superposition_depth", 3)
            enhanced_data["superposition_states"] = self._generate_superposition_states(
                enhanced_data, superposition_depth
            )

        return enhanced_data

    def _generate_coherence_matrix(
        self, data: Dict[str, Any], factor: float
    ) -> np.ndarray:
        """Generate quantum coherence matrix"""
        # Extract dimensionality from data
        dims = data.get("dimensions", 3)

        # Create coherence matrix based on geometric algebra
        coherence_matrix = np.eye(dims, dtype=complex)

        # Apply coherence factor
        for i in range(dims):
            for j in range(dims):
                if i != j:
                    coherence_matrix[i, j] = factor * np.exp(
                        1j * np.pi * (i + j) / dims
                    )

        return coherence_matrix

    def _generate_entanglement_data(
        self, data: Dict[str, Any], strength: float
    ) -> Dict[str, Any]:
        """Generate quantum entanglement data"""
        # Create entangled pairs based on glyph structure
        entanglement_pairs = []

        # Extract vertices or key points from glyph data
        vertices = data.get("vertices", [])

        # Generate entanglement pairs
        for i in range(0, len(vertices), 2):
            if i + 1 < len(vertices):
                entanglement_pairs.append(
                    {
                        "pair": [i, i + 1],
                        "strength": strength,
                        "phase": np.random.uniform(0, 2 * np.pi),
                    }
                )

        return {
            "pairs": entanglement_pairs,
            "global_strength": strength,
            "correlation_matrix": self._generate_correlation_matrix(
                len(vertices), strength
            ),
        }

    def _generate_correlation_matrix(self, size: int, strength: float) -> np.ndarray:
        """Generate quantum correlation matrix"""
        matrix = np.eye(size, dtype=complex)

        for i in range(size):
            for j in range(i + 1, size):
                correlation = strength * np.exp(1j * np.random.uniform(0, 2 * np.pi))
                matrix[i, j] = correlation
                matrix[j, i] = np.conj(correlation)

        return matrix

    def _generate_superposition_states(
        self, data: Dict[str, Any], depth: int
    ) -> List[Dict[str, Any]]:
        """Generate quantum superposition states"""
        states = []

        for i in range(depth):
            # Create superposition state with varying amplitudes
            amplitude = 1.0 / np.sqrt(depth)
            phase = 2 * np.pi * i / depth

            state = {
                "amplitude": amplitude,
                "phase": phase,
                "state_data": self._modify_data_for_state(data, i, depth),
            }

            states.append(state)

        return states

    def _modify_data_for_state(
        self, data: Dict[str, Any], state_index: int, total_states: int
    ) -> Dict[str, Any]:
        """Modify glyph data for specific superposition state"""
        modified_data = data.copy()

        # Apply state-specific transformations
        if "vertices" in modified_data:
            vertices = np.array(modified_data["vertices"])

            # Apply rotation based on state
            angle = 2 * np.pi * state_index / total_states
            rotation_matrix = np.array(
                [[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]]
            )

            # Apply rotation to 2D vertices
            if vertices.shape[1] >= 2:
                vertices[:, :2] = vertices[:, :2] @ rotation_matrix.T

            modified_data["vertices"] = vertices.tolist()

        return modified_data

    async def _calculate_quantum_metrics(
        self, context: RenderContext, enhanced_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate quantum rendering metrics"""
        metrics = {}

        # Coherence metric
        if "coherence_matrix" in enhanced_data:
            coherence_matrix = enhanced_data["coherence_matrix"]
            metrics["coherence_score"] = (
                np.abs(np.trace(coherence_matrix)) / coherence_matrix.shape[0]
            )

        # Entanglement metric
        if "entanglement_data" in enhanced_data:
            entanglement_data = enhanced_data["entanglement_data"]
            metrics["entanglement_score"] = entanglement_data["global_strength"]

        # Superposition metric
        if "superposition_states" in enhanced_data:
            states = enhanced_data["superposition_states"]
            metrics["superposition_depth"] = len(states)
            metrics["superposition_uniformity"] = np.std(
                [s["amplitude"] for s in states]
            )

        # Quantum fidelity
        metrics["quantum_fidelity"] = self._calculate_quantum_fidelity(enhanced_data)

        return metrics

    def _calculate_quantum_fidelity(self, enhanced_data: Dict[str, Any]) -> float:
        """Calculate quantum fidelity metric"""
        # Simplified fidelity calculation
        fidelity = 1.0

        if "coherence_matrix" in enhanced_data:
            coherence_matrix = enhanced_data["coherence_matrix"]
            fidelity *= np.abs(np.linalg.det(coherence_matrix)) ** (
                1.0 / coherence_matrix.shape[0]
            )

        return min(fidelity, 1.0)

    def _update_performance_metrics(self, renderer: str, render_time: float):
        """Update performance metrics for renderer"""
        if renderer not in self.performance_metrics:
            self.performance_metrics[renderer] = []

        self.performance_metrics[renderer].append(render_time)

        # Keep only last 100 measurements
        if len(self.performance_metrics[renderer]) > 100:
            self.performance_metrics[renderer] = self.performance_metrics[renderer][
                -100:
            ]

    # Built-in renderer implementations

    async def _render_webgl(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> str:
        """WebGL renderer implementation"""
        # Generate WebGL shader code
        vertex_shader = self._generate_vertex_shader(enhanced_data, context)
        fragment_shader = self._generate_fragment_shader(enhanced_data, context)

        # Create WebGL scene
        webgl_scene = {
            "vertex_shader": vertex_shader,
            "fragment_shader": fragment_shader,
            "uniforms": self._generate_uniforms(enhanced_data, context),
            "vertices": enhanced_data.get("vertices", []),
            "indices": enhanced_data.get("indices", []),
            "quantum_data": {
                "coherence_matrix": enhanced_data.get("coherence_matrix", []),
                "entanglement_data": enhanced_data.get("entanglement_data", {}),
                "superposition_states": enhanced_data.get("superposition_states", []),
            },
        }

        return json.dumps(webgl_scene, default=str)

    def _generate_vertex_shader(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> str:
        """Generate WebGL vertex shader"""
        return """
        #version 300 es
        precision highp float

        in vec3 position
        in vec3 normal
        in vec2 texCoord
        in vec4 quantumState

        uniform mat4 modelMatrix
        uniform mat4 viewMatrix
        uniform mat4 projectionMatrix
        uniform mat4 coherenceMatrix
        uniform float time
        uniform float coherenceFactor

        out vec3 vPosition
        out vec3 vNormal
        out vec2 vTexCoord
        out vec4 vQuantumState
        out float vCoherence

        void main() {
            // Apply quantum coherence transformation
            vec4 quantumPosition = coherenceMatrix * vec4(position, 1.0)

            // Calculate coherence factor
            vCoherence = coherenceFactor * (0.5 + 0.5 * sin(time + quantumState.x))

            // Apply superposition effects
            vec3 modifiedPosition = position + 0.1 * sin(time + quantumState.y) * normal

            // Transform position
            vec4 worldPosition = modelMatrix * vec4(modifiedPosition, 1.0)
            vec4 viewPosition = viewMatrix * worldPosition
            gl_Position = projectionMatrix * viewPosition

            // Pass through attributes
            vPosition = worldPosition.xyz
            vNormal = normalize(mat3(modelMatrix) * normal)
            vTexCoord = texCoord
            vQuantumState = quantumState
        }
        """

    def _generate_fragment_shader(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> str:
        """Generate WebGL fragment shader"""
        return """
        #version 300 es
        precision highp float

        in vec3 vPosition
        in vec3 vNormal
        in vec2 vTexCoord
        in vec4 vQuantumState
        in float vCoherence

        uniform vec3 cameraPosition
        uniform float time
        uniform float entanglementStrength
        uniform int superpositionDepth

        out vec4 fragColor

        // Quantum color calculation
        vec3 quantumColor(vec4 quantumState, float coherence) {
            vec3 baseColor = vec3(0.3, 0.6, 0.9)

            // Apply quantum interference
            float interference = sin(quantumState.x * 10.0 + time) *
                               cos(quantumState.y * 10.0 + time) * coherence

            // Entanglement effects
            vec3 entanglementColor = vec3(
                0.5 + 0.5 * sin(time + quantumState.z),
                0.5 + 0.5 * cos(time + quantumState.w),
                0.5 + 0.5 * sin(time + quantumState.x + quantumState.y)
            )

            return mix(baseColor, entanglementColor, entanglementStrength * interference)
        }

        void main() {
            // Calculate quantum-enhanced color
            vec3 color = quantumColor(vQuantumState, vCoherence)

            // Apply superposition visualization
            float superpositionFactor = 1.0
            if (superpositionDepth > 1) {
                superpositionFactor = 0.5 + 0.5 * sin(time * float(superpositionDepth) + vQuantumState.x)
            }

            // Final color with quantum effects
            fragColor = vec4(color * superpositionFactor, 0.8 + 0.2 * vCoherence)
        }
        """

    def _generate_uniforms(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> Dict[str, Any]:
        """Generate WebGL uniforms"""
        uniforms = {
            "time": 0.0,
            "coherenceFactor": context.quantum_params.get("coherence_factor", 0.8),
            "entanglementStrength": context.quantum_params.get(
                "entanglement_strength", 0.6
            ),
            "superpositionDepth": context.quantum_params.get("superposition_depth", 3),
        }

        # Add coherence matrix if available
        if "coherence_matrix" in enhanced_data:
            coherence_matrix = enhanced_data["coherence_matrix"]
            uniforms["coherenceMatrix"] = coherence_matrix.tolist()

        return uniforms

    def _render_canvas(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> str:
        """Canvas 2D renderer implementation"""
        # Generate Canvas drawing commands
        canvas_commands = []

        # Set up canvas
        canvas_commands.append(f"canvas.width = {context.dimensions['width']};")
        canvas_commands.append(f"canvas.height = {context.dimensions['height']};")
        canvas_commands.append("const ctx = canvas.getContext('2d');")

        # Clear canvas
        canvas_commands.append("ctx.clearRect(0, 0, canvas.width, canvas.height);")

        # Apply quantum visualization
        vertices = enhanced_data.get("vertices", [])
        if vertices:
            canvas_commands.append("ctx.beginPath();")

            # Draw quantum-enhanced path
            for i, vertex in enumerate(vertices):
                x, y = vertex[0], vertex[1]

                # Apply quantum effects
                if "coherence_matrix" in enhanced_data:
                    coherence = enhanced_data["coherence_matrix"]
                    if i < len(coherence):
                        x += np.real(coherence[i, 0]) * 10
                        y += np.imag(coherence[i, 0]) * 10

                if i == 0:
                    canvas_commands.append(f"ctx.moveTo({x}, {y});")
                else:
                    canvas_commands.append(f"ctx.lineTo({x}, {y});")

            # Apply quantum styling
            coherence_factor = context.quantum_params.get("coherence_factor", 0.8)
            canvas_commands.append(
                f"ctx.strokeStyle = 'rgba(100, 150, 255, {coherence_factor})';"
            )
            canvas_commands.append("ctx.lineWidth = 2;")
            canvas_commands.append("ctx.stroke();")

        return "\n".join(canvas_commands)

    def _render_svg(self, enhanced_data: Dict[str, Any], context: RenderContext) -> str:
        """SVG renderer implementation"""
        width = context.dimensions["width"]
        height = context.dimensions["height"]

        svg_elements = []
        svg_elements.append(
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        )

        # Add quantum gradient definitions
        svg_elements.append("<defs>")
        svg_elements.append(
            '<linearGradient id="quantumGradient" x1="0%" y1="0%" x2="100%" y2="100%">'
        )
        svg_elements.append(
            '<stop offset="0%" style="stop-color:#3366FF;stop-opacity:0.8" />'
        )
        svg_elements.append(
            '<stop offset="50%" style="stop-color:#6699FF;stop-opacity:0.6" />'
        )
        svg_elements.append(
            '<stop offset="100%" style="stop-color:#99CCFF;stop-opacity:0.4" />'
        )
        svg_elements.append("</linearGradient>")
        svg_elements.append("</defs>")

        # Render quantum-enhanced shapes
        vertices = enhanced_data.get("vertices", [])
        if vertices:
            path_data = []

            for i, vertex in enumerate(vertices):
                x, y = vertex[0], vertex[1]

                # Apply quantum transformations
                if "superposition_states" in enhanced_data:
                    states = enhanced_data["superposition_states"]
                    if states:
                        # Blend superposition states
                        for j, state in enumerate(states):
                            state_vertices = state["state_data"].get("vertices", [])
                            if i < len(state_vertices):
                                sx, sy = state_vertices[i][0], state_vertices[i][1]
                                weight = state["amplitude"]
                                x += sx * weight * 0.1
                                y += sy * weight * 0.1

                if i == 0:
                    path_data.append(f"M {x} {y}")
                else:
                    path_data.append(f"L {x} {y}")

            path_string = " ".join(path_data)
            svg_elements.append(
                f'<path d="{path_string}" stroke="url(#quantumGradient)" stroke-width="2" fill="none" />'
            )

        svg_elements.append("</svg>")

        return "\n".join(svg_elements)

    def _render_quantum_field(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> Dict[str, Any]:
        """Quantum field renderer implementation"""
        # Generate quantum field visualization data
        field_data = {
            "type": "quantum_field",
            "dimensions": context.dimensions,
            "field_points": [],
            "coherence_field": [],
            "entanglement_connections": [],
        }

        # Generate field points
        width, height = context.dimensions["width"], context.dimensions["height"]
        grid_size = 20

        for i in range(0, width, grid_size):
            for j in range(0, height, grid_size):
                # Calculate quantum field value at this point
                field_value = self._calculate_quantum_field_value(i, j, enhanced_data)

                field_data["field_points"].append(
                    {
                        "x": i,
                        "y": j,
                        "value": field_value,
                        "phase": (
                            np.angle(field_value)
                            if isinstance(field_value, complex)
                            else 0
                        ),
                    }
                )

        return field_data

    def _calculate_quantum_field_value(
        self, x: int, y: int, enhanced_data: Dict[str, Any]
    ) -> complex:
        """Calculate quantum field value at specific point"""
        # Simplified quantum field calculation
        field_value = 0 + 0j

        # Contribution from coherence matrix
        if "coherence_matrix" in enhanced_data:
            coherence = enhanced_data["coherence_matrix"]
            field_value += np.sum(coherence) * np.exp(1j * (x + y) * 0.01)

        # Contribution from entanglement
        if "entanglement_data" in enhanced_data:
            entanglement = enhanced_data["entanglement_data"]
            field_value += entanglement["global_strength"] * np.exp(1j * (x - y) * 0.02)

        return field_value

    def _render_holographic(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> Dict[str, Any]:
        """Holographic renderer implementation"""
        # Generate holographic visualization data
        holographic_data = {
            "type": "holographic",
            "dimensions": context.dimensions,
            "interference_pattern": [],
            "hologram_layers": [],
        }

        # Generate interference pattern
        width, height = context.dimensions["width"], context.dimensions["height"]

        for i in range(0, width, 2):
            for j in range(0, height, 2):
                # Calculate holographic interference
                interference = self._calculate_holographic_interference(
                    i, j, enhanced_data
                )

                holographic_data["interference_pattern"].append(
                    {
                        "x": i,
                        "y": j,
                        "intensity": abs(interference),
                        "phase": np.angle(interference),
                    }
                )

        return holographic_data

    def _calculate_holographic_interference(
        self, x: int, y: int, enhanced_data: Dict[str, Any]
    ) -> complex:
        """Calculate holographic interference pattern"""
        # Reference wave
        reference_wave = np.exp(1j * 2 * np.pi * (x + y) * 0.01)

        # Object wave (from quantum data)
        object_wave = 0 + 0j

        if "coherence_matrix" in enhanced_data:
            coherence = enhanced_data["coherence_matrix"]
            object_wave += np.sum(coherence) * np.exp(1j * (x * 0.02 + y * 0.03))

        # Interference
        interference = reference_wave + object_wave

        return interference

    def _render_geometric_algebra(
        self, enhanced_data: Dict[str, Any], context: RenderContext
    ) -> Dict[str, Any]:
        """Geometric algebra renderer implementation"""
        # Generate geometric algebra visualization
        ga_data = {
            "type": "geometric_algebra",
            "dimensions": context.dimensions,
            "multivectors": [],
            "geometric_products": [],
        }

        # Process vertices as multivectors
        vertices = enhanced_data.get("vertices", [])

        for i, vertex in enumerate(vertices):
            # Create multivector from vertex
            multivector = self.geometric_algebra.create_multivector(vertex)

            ga_data["multivectors"].append(
                {
                    "index": i,
                    "coefficients": multivector.coefficients.tolist(),
                    "basis": multivector.basis_names,
                    "magnitude": abs(multivector),
                }
            )

        return ga_data

    async def test_render(self) -> Dict[str, Any]:
        """Test render functionality"""
        test_data = {
            "vertices": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "indices": [0, 1, 2, 3],
            "dimensions": 2,
        }

        result = await self.render_async(
            glyph_data=test_data,
            renderer="webgl",
            dimensions={"width": 400, "height": 400},
        )

        return {
            "success": True,
            "render_time": result.render_time,
            "quantum_metrics": result.quantum_metrics,
        }

    def get_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all renderers"""
        metrics = {}

        for renderer, times in self.performance_metrics.items():
            if times:
                metrics[renderer] = {
                    "average_time": np.mean(times),
                    "min_time": np.min(times),
                    "max_time": np.max(times),
                    "std_time": np.std(times),
                    "sample_count": len(times),
                }

        return metrics

    def register_plugin(self, name: str, renderer_func: Callable):
        """Register a custom renderer plugin"""
        self.render_plugins[name] = renderer_func

    def list_renderers(self) -> List[str]:
        """List available renderers"""
        return list(self.render_plugins.keys())
