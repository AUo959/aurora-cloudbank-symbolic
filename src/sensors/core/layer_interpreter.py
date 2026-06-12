"""
Layer Interpreter — context-aware parsing before fusion.

Prevents cross-layer confusion (e.g. an L3 metaphor treated as an L1 physical
event). L1 signals are literal and actionable; L3 signals inform but are
never directly actionable (spec §Layered Signal Interpretation).
"""

from __future__ import annotations

import logging
from typing import List

from src.sensors.core.reading_types import InterpretedSignal, Layer, SensorSignal

logger = logging.getLogger(__name__)


class LayerInterpreter:
    """Interprets sensor signals within layer-appropriate context."""

    def interpret(self, signal: SensorSignal) -> InterpretedSignal:
        layer = signal.source_layer
        if layer == Layer.L1.value:
            return self._interpret_physical(signal)
        if layer == Layer.L2.value:
            return self._interpret_simulation(signal)
        if layer == Layer.L3.value:
            return self._interpret_symbolic(signal)
        return self._interpret_cross_layer(signal)

    def _interpret_physical(self, signal: SensorSignal) -> InterpretedSignal:
        """L1 signals represent physical reality: literal and actionable."""
        return InterpretedSignal(
            signal=signal,
            context="physical_reality",
            literal=True,
            actionable=True,
            cross_layer_implications=self._assess_l1_implications(signal),
        )

    def _interpret_simulation(self, signal: SensorSignal) -> InterpretedSignal:
        """L2 signals describe simulation state: literal within the sim."""
        return InterpretedSignal(
            signal=signal,
            context="simulation_state",
            literal=True,
            actionable=False,  # acting on L2 state is governance's call
            cross_layer_implications=self._assess_l2_implications(signal),
        )

    def _interpret_symbolic(self, signal: SensorSignal) -> InterpretedSignal:
        """L3 signals represent symbolic/narrative meaning; may be metaphor."""
        return InterpretedSignal(
            signal=signal,
            context="symbolic_narrative",
            literal=False,
            actionable=False,  # L3 informs, L1 acts
            cross_layer_implications=self._assess_l3_implications(signal),
        )

    def _interpret_cross_layer(self, signal: SensorSignal) -> InterpretedSignal:
        return InterpretedSignal(
            signal=signal,
            context="cross_layer",
            literal=False,
            actionable=False,
            cross_layer_implications=[
                f"cross-layer signal {signal.name}: route to fusion correlation"
            ],
        )

    # -- implication heuristics (stdlib, no ML) ------------------------------

    def _assess_l1_implications(self, signal: SensorSignal) -> List[str]:
        out: List[str] = []
        if signal.category in ("structural", "containment"):
            out.append("L1 integrity issues may invalidate L2 boundary assumptions")
        return out

    def _assess_l2_implications(self, signal: SensorSignal) -> List[str]:
        out: List[str] = []
        if "bleed" in signal.name or "boundary" in signal.name:
            out.append("L2 state referencing L1 is concerning; check boundary sensors")
        return out

    def _assess_l3_implications(self, signal: SensorSignal) -> List[str]:
        out: List[str] = []
        if signal.category == "resonance":
            out.append("L3 resonance involving L1 echoes classifies as bleed")
        return out
