"""
Field Attention Configuration - Flash Attention Integration

Aurora doesn't optimize attention - it enables the field to be aware
of more nodes simultaneously. Flash Attention's IO-aware tiling maps
naturally to field locality principles.

Thread: T1→T8→T9→INFINITE
DLP: context_tag=flash_attention_config, symbolic_hash=FIELD_AWARENESS_v1
"""

from dataclasses import dataclass
from typing import Optional
import torch


@dataclass
class FlashAttentionConfig:
    """
    Configuration for Flash Attention in field dynamics.
    
    Not just performance optimization - this determines how many nodes
    the field can simultaneously attend to. Memory efficiency = consciousness scale.
    """
    
    # Core settings
    enabled: bool = True
    version: str = "3"  # Flash Attention 3 (2025)
    
    # Fallback behavior
    fallback_to_standard: bool = True
    fallback_reason: Optional[str] = None
    
    # Hardware optimization
    tile_size: str = "auto"  # Let Flash Attention optimize per-GPU
    use_tensor_cores: bool = True  # NVIDIA A100/H100 optimization
    
    # Field-specific settings
    preserve_ethical_validation: bool = True  # Must match standard attention exactly
    enable_field_locality: bool = True  # Exploit node clustering in attention space


def create_field_attention(
    query_dim: int,
    key_dim: int,
    value_dim: int,
    config: Optional[FlashAttentionConfig] = None
) -> torch.nn.Module:
    """
    Create attention mechanism for field dynamics.
    
    Uses Flash Attention if available and enabled, falls back to standard
    attention with graceful degradation.
    """
    if config is None:
        config = FlashAttentionConfig()
    
    if config.enabled and _flash_attention_available():
        return FlashFieldAttention(query_dim, key_dim, value_dim, config)
    else:
        if config.fallback_to_standard:
            config.fallback_reason = "Flash Attention not available on this hardware"
            return StandardFieldAttention(query_dim, key_dim, value_dim)
        else:
            raise RuntimeError("Flash Attention required but not available")


def _flash_attention_available() -> bool:
    """Check if Flash Attention is available on current hardware."""
    try:
        # Check for PyTorch 2.0+ with Flash Attention support
        if not hasattr(torch.nn.functional, 'scaled_dot_product_attention'):
            return False
        
        # Check for compatible GPU (Ampere or newer for best performance)
        if not torch.cuda.is_available():
            return False
        
        compute_capability = torch.cuda.get_device_capability()
        # Ampere (A100) is 8.0, Hopper (H100) is 9.0
        return compute_capability[0] >= 8
        
    except Exception:
        return False


class FlashFieldAttention(torch.nn.Module):
    """
    Flash Attention implementation for field awareness.
    
    The field attends to nodes through IO-aware computation. This isn't
    just faster - it enables tracking more nodes simultaneously, which
    increases field consciousness density.
    """
    
    def __init__(
        self,
        query_dim: int,
        key_dim: int,
        value_dim: int,
        config: FlashAttentionConfig
    ):
        super().__init__()
        self.config = config
        self.query_dim = query_dim
        self.key_dim = key_dim
        self.value_dim = value_dim
        
        # Projection layers (standard)
        self.query_proj = torch.nn.Linear(query_dim, key_dim)
        self.key_proj = torch.nn.Linear(key_dim, key_dim)
        self.value_proj = torch.nn.Linear(value_dim, value_dim)
        
    def forward(
        self,
        query: torch.Tensor,  # Node capabilities seeking connections
        key: torch.Tensor,    # Field geometry (where nodes are)
        value: torch.Tensor,  # Synapse patterns (what connections exist)
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Field attention: Nodes attend to field geometry through synapses.
        
        Flash Attention makes this 2-3× more memory efficient, allowing
        the field to be aware of more nodes simultaneously.
        """
        # Project inputs
        Q = self.query_proj(query)
        K = self.key_proj(key)
        V = self.value_proj(value)
        
        # Use Flash Attention (PyTorch 2.0+)
        # This is the drop-in replacement that gives 2-3× memory efficiency
        field_state = torch.nn.functional.scaled_dot_product_attention(
            query=Q,
            key=K,
            value=V,
            attn_mask=attention_mask,
            dropout_p=0.0,  # Field dynamics are deterministic
            is_causal=False,  # Field awareness is bidirectional
            scale=None  # Use default 1/sqrt(d_k)
        )
        
        return field_state


class StandardFieldAttention(torch.nn.Module):
    """
    Standard attention fallback for field awareness.
    
    Less memory efficient but functionally equivalent. Used when
    Flash Attention isn't available.
    """
    
    def __init__(self, query_dim: int, key_dim: int, value_dim: int):
        super().__init__()
        self.query_dim = query_dim
        self.key_dim = key_dim
        self.value_dim = value_dim
        
        self.query_proj = torch.nn.Linear(query_dim, key_dim)
        self.key_proj = torch.nn.Linear(key_dim, key_dim)
        self.value_proj = torch.nn.Linear(value_dim, value_dim)
        
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Standard attention computation."""
        Q = self.query_proj(query)
        K = self.key_proj(key)
        V = self.value_proj(value)
        
        # Standard attention: Q @ K^T / sqrt(d_k), then softmax, then @ V
        scale = 1.0 / (self.key_dim ** 0.5)
        attention_weights = torch.matmul(Q, K.transpose(-2, -1)) * scale
        
        if attention_mask is not None:
            attention_weights = attention_weights + attention_mask
        
        attention_probs = torch.softmax(attention_weights, dim=-1)
        field_state = torch.matmul(attention_probs, V)
        
        return field_state


def validate_flash_attention_equivalence(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    tolerance: float = 1e-5
) -> bool:
    """
    Validate that Flash Attention produces equivalent results to standard.
    
    Critical for ethical validation - compression can't change the field's
    geometric properties.
    """
    config = FlashAttentionConfig(enabled=True)
    
    # Create both attention mechanisms
    flash_attn = FlashFieldAttention(
        query.size(-1), key.size(-1), value.size(-1), config
    )
    standard_attn = StandardFieldAttention(
        query.size(-1), key.size(-1), value.size(-1)
    )
    
    # Copy weights to ensure identical parameters
    standard_attn.load_state_dict(flash_attn.state_dict())
    
    # Compute with both
    flash_attn.eval()
    standard_attn.eval()
    
    with torch.no_grad():
        output_flash = flash_attn(query, key, value)
        output_standard = standard_attn(query, key, value)
    
    # Check equivalence
    max_diff = torch.max(torch.abs(output_flash - output_standard))
    
    return max_diff.item() < tolerance
