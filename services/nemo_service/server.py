"""
Aurora NeMo Service — FastAPI Inference Server
# Symbolic Anchor: T1
# SRB: NEMO_SERVICE_v1
# DLP: [nemo, inference, gpu, models, api]
# Chain Notation: #SERVICES//NEMO//SERVER//
# Ethics Protocol: Picard_Delta_3
# Anchor Seed: EOS_SEED_ORION

Endpoints:
  POST /nemo/infer      — ASR / NLU / TTS inference
  POST /nemo/generate   — LLM text generation
  GET  /nemo/health     — Health + entropy-state + memory-drift
  GET  /nemo/status     — Detailed status (model, GPU, symbolic anchor)
  POST /nemo/snapshot   — Create a SHA256-sealed simulation snapshot
  POST /nemo/restore    — Restore NeMo state from a snapshot
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import NeMoModelType, get_config
from .state_manager import StateManager
from .symbolic_bridge import SymbolicBridge

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nemo_service.server")

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------
config = get_config()

app = FastAPI(
    title="Aurora NeMo Inference Service",
    version="1.0.0",
    description=(
        "NVIDIA NeMo inference service integrated with the Aurora/GUMAS "
        "symbolic simulation ecosystem.  Ethics Protocol: Picard_Delta_3."
    ),
)

# Shared service-level singletons
_bridge = SymbolicBridge(
    anchor_seed=config.nemo_anchor_seed,
    drift_threshold=config.drift_threshold,
)
_state_manager = StateManager(snapshots_dir=config.snapshots_dir)

# Inference call counter (used for entropy logging)
_infer_counter: int = 0

# ---------------------------------------------------------------------------
# NeMo model handle (lazy-loaded to avoid hard import dependency)
# ---------------------------------------------------------------------------
_nemo_model: Optional[Any] = None


def _load_nemo_model() -> Optional[Any]:
    """
    Attempt to load the default NeMo model checkpoint.

    Returns the model object on success, or None if NeMo is not installed
    or no model path is configured (graceful degradation).
    """
    global _nemo_model  # noqa: PLW0603

    if _nemo_model is not None:
        return _nemo_model

    model_path = config.default_model_path
    if not model_path:
        logger.warning("No default_model_path configured — NeMo model not loaded")
        return None

    try:
        import nemo.collections.nlp as nemo_nlp  # type: ignore[import]

        _nemo_model = nemo_nlp.models.language_modeling.MegatronGPTModel.restore_from(
            model_path,
            map_location="cuda" if os.environ.get("NVIDIA_VISIBLE_DEVICES") else "cpu",
        )
        logger.info("NeMo model loaded from %s", model_path)
    except Exception as exc:  # noqa: BLE001
        logger.warning("NeMo model load failed (continuing without model): %s", exc)
        _nemo_model = None

    return _nemo_model


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class InferRequest(BaseModel):
    """Payload for POST /nemo/infer."""

    audio_bytes: Optional[str] = Field(
        default=None,
        description="Base64-encoded audio for ASR/TTS tasks",
    )
    text: Optional[str] = Field(
        default=None,
        description="Input text for NLU tasks",
    )
    model_type: NeMoModelType = Field(
        default=NeMoModelType.LLM,
        description="Model type to use for this inference call",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional symbolic context to inject",
    )


class InferResponse(BaseModel):
    """Response from POST /nemo/infer."""

    result: Any
    model_type: str
    anchor_context: Dict[str, Any]
    entropy: Optional[float] = None
    drift_flagged: bool = False
    latency_ms: float


class GenerateRequest(BaseModel):
    """Payload for POST /nemo/generate."""

    prompt: str = Field(description="Text prompt for LLM generation")
    max_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    top_k: int = Field(default=50, ge=1)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = Field(default=None)


class GenerateResponse(BaseModel):
    """Response from POST /nemo/generate."""

    generated_text: str
    tokens_generated: int
    anchor_context: Dict[str, Any]
    entropy: Optional[float] = None
    latency_ms: float


class SnapshotRequest(BaseModel):
    """Payload for POST /nemo/snapshot."""

    description: str = Field(default="", description="Human-readable snapshot description")


class SnapshotResponse(BaseModel):
    """Response from POST /nemo/snapshot."""

    snapshot_id: str
    seal: str
    timestamp: float
    description: str
    anchor_context: Dict[str, Any]


class RestoreRequest(BaseModel):
    """Payload for POST /nemo/restore."""

    snapshot_id: str = Field(description="ID of the snapshot to restore")


class RestoreResponse(BaseModel):
    """Response from POST /nemo/restore."""

    snapshot_id: str
    restored: bool
    seal: str
    message: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_current_state() -> Dict[str, Any]:
    """
    Collect a serialisable representation of the current service state.

    Used for snapshot creation.
    """
    return {
        "config": {
            "aurora_module_id": config.aurora_module_id,
            "aurora_ethics_protocol": config.aurora_ethics_protocol,
            "nemo_anchor_seed": config.nemo_anchor_seed,
            "default_model_type": config.default_model_type,
            "default_model_path": config.default_model_path,
        },
        "bridge_summary": _bridge.summary(),
        "model_loaded": _nemo_model is not None,
        "infer_counter": _infer_counter,
        "snapshot_count": len(_state_manager.list_snapshots()),
        "t1_anchor": _bridge.get_anchor_state().get("t1"),
    }


def _gpu_utilisation() -> Optional[float]:
    """
    Return current GPU memory utilisation (0–100 %) or None if unavailable.

    Requires the nvidia-ml-py3 (pynvml) package.  Degrades gracefully.
    """
    try:
        import pynvml  # type: ignore[import]

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(config.cuda_device)
        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return round(mem_info.used / mem_info.total * 100, 2)
    except ImportError:
        return None
    except Exception as exc:  # noqa: BLE001 — pynvml errors are non-fatal
        logger.debug("GPU utilisation unavailable: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/nemo/health")
async def nemo_health() -> Dict[str, Any]:
    """
    Health check with entropy-state and memory-drift reporting.

    # Entropy logging: Log entropy state on health checks
    """
    latest_entropy = _bridge.get_latest_entropy()
    anchor = _bridge.get_anchor_state()

    drift_flagged = False
    if latest_entropy:
        drift_flagged = latest_entropy.get("drift_flagged", False)

    return {
        "status": "ok",
        "service": "aurora-nemo-service",
        "version": "1.0.0",
        "ethics_protocol": config.aurora_ethics_protocol,
        "anchor_seed": config.nemo_anchor_seed,
        "srb": "NEMO_SERVICE_v1",
        "t1": anchor.get("t1"),
        "model_loaded": _nemo_model is not None,
        "entropy_state": latest_entropy,
        "memory_drift": drift_flagged,
        "chain_notation": "#SERVICES//NEMO//HEALTH//",
        "timestamp": time.time(),
    }


@app.get("/nemo/status")
async def nemo_status() -> Dict[str, Any]:
    """
    Detailed status including model info, GPU utilisation, and symbolic anchor state.
    """
    gpu_util = _gpu_utilisation()
    bridge_summary = _bridge.summary()
    snapshots = _state_manager.list_snapshots()

    return {
        "service": "aurora-nemo-service",
        "version": "1.0.0",
        "module_id": config.aurora_module_id,
        "ethics_protocol": config.aurora_ethics_protocol,
        "anchor_seed": config.nemo_anchor_seed,
        "chain_notation": "#SERVICES//NEMO//STATUS//",
        "model": {
            "loaded": _nemo_model is not None,
            "type": config.default_model_type,
            "path": config.default_model_path,
        },
        "gpu": {
            "visible_devices": config.nvidia_visible_devices,
            "cuda_device": config.cuda_device,
            "utilisation_pct": gpu_util,
        },
        "symbolic_anchor": bridge_summary,
        "snapshots": {
            "count": len(snapshots),
            "current_id": _state_manager.get_current_snapshot_id(),
        },
        "inference": {
            "call_counter": _infer_counter,
            "max_batch_size": config.max_batch_size,
            "max_sequence_length": config.max_sequence_length,
        },
        "timestamp": time.time(),
    }


@app.post("/nemo/infer", response_model=InferResponse)
async def nemo_infer(request: InferRequest) -> InferResponse:
    """
    Run NeMo model inference (ASR, NLU, or TTS depending on loaded model).

    # Entropy logging: Log entropy state on inference operations
    """
    global _infer_counter  # noqa: PLW0603

    start = time.time()
    _infer_counter += 1

    anchor_ctx = _bridge.resolve_anchor_context(model_type=request.model_type.value)

    model = _load_nemo_model()

    # -----------------------------------------------------------------------
    # Mock result when no model is loaded (graceful degradation)
    # -----------------------------------------------------------------------
    if model is None:
        result = {
            "mock": True,
            "message": "NeMo model not loaded — returning mock result",
            "input_received": {
                "text": request.text,
                "model_type": request.model_type.value,
                "has_audio": request.audio_bytes is not None,
            },
        }
        entropy_value = 0.0
        drift_flagged = False
    else:
        try:
            if request.model_type == NeMoModelType.ASR:
                result = {"transcript": model.transcribe([request.audio_bytes])}
            elif request.model_type == NeMoModelType.NLU:
                result = {"intent": model.predict([request.text])}
            elif request.model_type == NeMoModelType.TTS:
                result = {"audio": model.generate([request.text])}
            else:
                result = {"output": model.generate([request.text])}
        except Exception as exc:  # noqa: BLE001
            logger.error("Inference error: %s", exc)
            raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

        # Compute dummy entropy from the call counter as a placeholder
        entropy_value = _bridge.compute_entropy([float(_infer_counter % 10)])
        reading = _bridge.log_entropy(
            call_index=_infer_counter,
            entropy=entropy_value,
            model_type=request.model_type.value,
        )
        drift_flagged = reading.drift_flagged

    latency_ms = (time.time() - start) * 1000

    return InferResponse(
        result=result,
        model_type=request.model_type.value,
        anchor_context=anchor_ctx,
        entropy=entropy_value,
        drift_flagged=drift_flagged,
        latency_ms=round(latency_ms, 2),
    )


@app.post("/nemo/generate", response_model=GenerateResponse)
async def nemo_generate(request: GenerateRequest) -> GenerateResponse:
    """
    Text generation endpoint for NeMo LLM models.

    # Entropy logging: Log entropy state on inference operations
    """
    global _infer_counter  # noqa: PLW0603

    start = time.time()
    _infer_counter += 1

    anchor_ctx = _bridge.resolve_anchor_context(model_type="llm")
    model = _load_nemo_model()

    if model is None:
        generated_text = (
            f"[MOCK] Generated response for prompt: {request.prompt[:50]}..."
        )
        tokens_generated = len(generated_text.split())
        entropy_value = None
    else:
        try:
            output = model.generate(
                [request.prompt],
                tokens_to_generate=request.max_tokens,
                temperature=request.temperature,
                top_k=request.top_k,
                top_p=request.top_p,
            )
            generated_text = output[0] if output else ""
            tokens_generated = len(generated_text.split())
            entropy_value = _bridge.compute_entropy(
                [float(i) for i in range(min(tokens_generated, 20))]
            )
            _bridge.log_entropy(
                call_index=_infer_counter,
                entropy=entropy_value,
                model_type="llm",
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Generation error: %s", exc)
            raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    latency_ms = (time.time() - start) * 1000

    return GenerateResponse(
        generated_text=generated_text,
        tokens_generated=tokens_generated,
        anchor_context=anchor_ctx,
        entropy=entropy_value,
        latency_ms=round(latency_ms, 2),
    )


@app.post("/nemo/snapshot", response_model=SnapshotResponse)
async def nemo_snapshot(request: SnapshotRequest) -> SnapshotResponse:
    """
    Create a SHA256-sealed simulation snapshot of the current NeMo state.

    # Memory sealing: SHA256 hash sealing on all state exports
    """
    anchor_ctx = _bridge.resolve_anchor_context(model_type="snapshot")
    state_data = _collect_current_state()
    state_data["anchor_context"] = anchor_ctx

    snapshot_id = _state_manager.create_snapshot(
        state_data=state_data,
        description=request.description,
        anchor_seed=config.nemo_anchor_seed,
    )

    snapshot = _state_manager.get_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=500, detail="Snapshot creation failed")

    return SnapshotResponse(
        snapshot_id=snapshot_id,
        seal=snapshot["seal"],
        timestamp=snapshot["timestamp"],
        description=request.description,
        anchor_context=anchor_ctx,
    )


@app.post("/nemo/restore", response_model=RestoreResponse)
async def nemo_restore(request: RestoreRequest) -> RestoreResponse:
    """
    Restore NeMo state from a snapshot with checksum validation.

    # Hash verification: All snapshot operations include SHA256 checksums
    """
    try:
        restored_data = _state_manager.restore_snapshot(request.snapshot_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    snapshot = _state_manager.get_snapshot(request.snapshot_id)
    seal = snapshot["seal"] if snapshot else ""

    return RestoreResponse(
        snapshot_id=request.snapshot_id,
        restored=True,
        seal=seal,
        message=f"State restored from snapshot {request.snapshot_id}",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "services.nemo_service.server:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        log_level=config.log_level,
    )
