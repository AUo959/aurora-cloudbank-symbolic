"""
Aurora NeMo Service — Configuration Management
# Symbolic Anchor: T1
# SRB: NEMO_SERVICE_v1
# DLP: [nemo, config, gpu, models]
# Chain Notation: #SERVICES//NEMO//CONFIG//
# Ethics Protocol: Picard_Delta_3
# Anchor Seed: EOS_SEED_ORION
"""

from enum import Enum
from functools import lru_cache
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DLPClassification(str, Enum):
    """Data Lineage Protocol classification levels."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class NeMoModelType(str, Enum):
    """Supported NeMo model categories."""

    ASR = "asr"
    NLU = "nlu"
    TTS = "tts"
    LLM = "llm"


class NeMoConfig(BaseSettings):
    """
    NeMo service configuration, loaded from environment variables.

    All settings follow Aurora symbolic conventions with DLP tagging,
    SRB anchors, and ethics protocol references.
    """

    # ---------------------------------------------------------------------------
    # Symbolic / Aurora metadata
    # ---------------------------------------------------------------------------
    aurora_module_id: str = Field(
        default="AURORA_NEMO_SERVICE",
        description="Aurora module identifier",
        validation_alias=AliasChoices("AURORA_MODULE_ID", "NEMO_AURORA_MODULE_ID"),
    )
    aurora_ethics_protocol: str = Field(
        default="Picard_Delta_3",
        description="Active ethics protocol",
        validation_alias=AliasChoices("AURORA_ETHICS_PROTOCOL", "NEMO_AURORA_ETHICS_PROTOCOL"),
    )
    nemo_anchor_seed: str = Field(
        default="EOS_SEED_ORION",
        description="Symbolic anchor seed for continuity verification",
        validation_alias=AliasChoices("NEMO_ANCHOR_SEED", "NEMO_NEMO_ANCHOR_SEED"),
    )
    aurora_chain_notation: str = Field(
        default="#SERVICES//NEMO//RUNTIME//",
        description="Chain notation for this runtime context",
        validation_alias=AliasChoices("AURORA_CHAIN_NOTATION", "NEMO_AURORA_CHAIN_NOTATION"),
    )
    dlp_classification: DLPClassification = Field(
        default=DLPClassification.INTERNAL,
        description="DLP classification level for model data",
    )

    # ---------------------------------------------------------------------------
    # Server settings
    # ---------------------------------------------------------------------------
    host: str = Field(default="127.0.0.1", description="Bind host")
    port: int = Field(default=8090, description="Bind port")
    workers: int = Field(default=1, description="Number of uvicorn workers")
    log_level: str = Field(default="info", description="Uvicorn log level")

    # ---------------------------------------------------------------------------
    # GPU / hardware settings
    # ---------------------------------------------------------------------------
    nvidia_visible_devices: str = Field(
        default="all",
        description="NVIDIA_VISIBLE_DEVICES value",
    )
    cuda_device: int = Field(default=0, description="Primary CUDA device index")
    mixed_precision: bool = Field(default=True, description="Enable AMP mixed precision")

    # ---------------------------------------------------------------------------
    # Model paths
    # ---------------------------------------------------------------------------
    models_dir: str = Field(
        default="/models",
        description="Root directory containing NeMo model checkpoints",
    )
    snapshots_dir: str = Field(
        default="/var/lib/nemo_snapshots",
        description=(
            "Directory for state snapshots. "
            "PRODUCTION: override with a persistent path (e.g. /var/lib/nemo_snapshots) "
            "or set NEMO_SNAPSHOTS_DIR to a mounted PVC path so snapshots survive restarts."
        ),
    )
    default_model_path: Optional[str] = Field(
        default=None,
        description="Optional default .nemo checkpoint path",
    )
    default_model_type: NeMoModelType = Field(
        default=NeMoModelType.LLM,
        description="Default model type when no path is specified",
    )

    # ---------------------------------------------------------------------------
    # Inference settings
    # ---------------------------------------------------------------------------
    max_batch_size: int = Field(default=8, description="Maximum inference batch size")
    max_sequence_length: int = Field(
        default=512,
        description="Maximum token sequence length for generation",
    )
    temperature: float = Field(default=1.0, description="Sampling temperature")
    top_k: int = Field(default=50, description="Top-k sampling parameter")
    top_p: float = Field(default=0.95, description="Top-p (nucleus) sampling parameter")

    # ---------------------------------------------------------------------------
    # Entropy / drift monitoring
    # ---------------------------------------------------------------------------
    entropy_log_interval: int = Field(
        default=100,
        description="Log entropy state every N inference calls",
    )
    drift_threshold: float = Field(
        default=0.15,
        description="Entropy drift threshold triggering a warning",
    )

    model_config = SettingsConfigDict(
        env_prefix="NEMO_",
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_config() -> NeMoConfig:
    """Return a singleton NeMoConfig instance populated from the environment.

    The configuration is instantiated on first use and cached for subsequent calls.
    """
    return NeMoConfig()
