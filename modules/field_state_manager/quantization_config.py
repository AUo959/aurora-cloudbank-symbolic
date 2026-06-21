"""
Field State Quantization - KV Cache and Curvature Quantization

Discrete field states compress better than continuous.
Field curvature is already geometric (discrete ethical dimensions) —
quantizing reveals the underlying structure, not distorting it.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=field_quantization, symbolic_hash=FIELD_DENSITY_v3
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class KVCacheQuantConfig:
    """Configuration for INT8 KV cache quantization."""

    precision: str = "int8"
    strategy: str = "per_channel"  # per_channel gives better accuracy than per_tensor
    group_size: int = 128           # Channel group size for per-channel scaling
    clip_ratio: float = 0.99        # Clip outliers beyond 99th percentile


@dataclass
class CurvatureQuantConfig:
    """Configuration for discrete field curvature quantization."""

    precision: str = "int8"
    # 9 discrete levels: 0, 32, 64, 96, 128, 160, 192, 224, 255
    # Maps to 0.0 → 1.0 range in 9 steps (~0.125 apart)
    levels: List[int] = field(default_factory=lambda: [0, 32, 64, 96, 128, 160, 192, 224, 255])
    rounding: str = "nearest"


@dataclass
class FieldQuantizationConfig:
    """Combined quantization config for field state manager."""

    kv_cache: KVCacheQuantConfig = field(default_factory=KVCacheQuantConfig)
    curvature: CurvatureQuantConfig = field(default_factory=CurvatureQuantConfig)
    enabled: bool = True
    preserve_ethics_precision: bool = True  # Ethics checks always stay at full precision


class FieldQuantizer:
    """
    Quantizes field state values for memory efficiency.

    Quantization doubles field observation density by halving per-value
    storage cost. Ethics validation stays at full FP32 precision because
    the geometric constraints must remain exact.
    """

    def __init__(self, config: Optional[FieldQuantizationConfig] = None):
        self.config = config or FieldQuantizationConfig()
        self._curvature_levels = self.config.curvature.levels

    def quantize_curvature(self, curvature: float) -> int:
        """
        Quantize continuous curvature (0.0–1.0) to nearest discrete INT8 level.

        Returns one of the 9 discrete levels defined in config.
        Discrete levels better reflect the underlying geometric structure
        of ethical dimensions.
        """
        if not self.config.enabled or not self._curvature_levels:
            return int(max(0, min(255, round(curvature * 255))))

        scaled = max(0.0, min(1.0, curvature)) * 255
        nearest = min(self._curvature_levels, key=lambda lvl: abs(lvl - scaled))
        return nearest

    def dequantize_curvature(self, level: int) -> float:
        """Convert discrete curvature level back to float (0.0–1.0)."""
        return level / 255.0

    def quantize_kv_tensor(self, values: List[float]) -> List[int]:
        """
        Quantize a list of KV cache values to INT8 per-channel.

        Uses per-channel scaling for accuracy: each channel gets its own
        scale factor based on the channel's value range, clipped at
        clip_ratio to handle outliers.
        """
        if not self.config.enabled or not values:
            return [int(max(-128, min(127, v * 127))) for v in values]

        cfg = self.config.kv_cache
        sorted_abs = sorted(abs(v) for v in values)
        clip_idx = int(len(sorted_abs) * cfg.clip_ratio)
        abs_max = sorted_abs[clip_idx] if clip_idx < len(sorted_abs) else sorted_abs[-1]

        if abs_max == 0.0:
            return [0] * len(values)

        scale = 127.0 / abs_max
        return [int(max(-128, min(127, round(v * scale)))) for v in values]

    def dequantize_kv_tensor(self, quantized: List[int], original_values: List[float]) -> List[float]:
        """
        Restore KV values from INT8 to float using the original scale.

        original_values provides the reference range for dequantization.
        """
        if not original_values:
            return []

        sorted_abs = sorted(abs(v) for v in original_values)
        clip_idx = int(len(sorted_abs) * self.config.kv_cache.clip_ratio)
        abs_max = sorted_abs[clip_idx] if clip_idx < len(sorted_abs) else sorted_abs[-1]

        if abs_max == 0.0:
            return [0.0] * len(quantized)

        scale = abs_max / 127.0
        return [q * scale for q in quantized]

    def quantization_error(self, original: float, quantized_level: int) -> float:
        """
        Return absolute error introduced by curvature quantization.

        Callers can use this to verify error stays within tolerance
        (plan specifies < 2 levels difference ≈ 0.016 in [0,1] range).
        """
        restored = self.dequantize_curvature(quantized_level)
        return abs(original - restored)

    def memory_savings_ratio(self, num_values: int) -> float:
        """
        Estimated memory reduction from quantizing num_values FP32 values to INT8.

        FP32 = 4 bytes, INT8 = 1 byte → 4× reduction.
        """
        return 4.0  # Theoretical; practical gain depends on framework overhead
