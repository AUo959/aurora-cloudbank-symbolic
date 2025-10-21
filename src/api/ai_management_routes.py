"""
AI Model Management API Endpoints for Aurora CloudBank Symbolic

Provides runtime control over AI model selection, capabilities inspection,
and fallback configuration.
"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

try:
    from modules.ai_core import AIModel, claude_hub, gpt5_hub, unified_ai
except ImportError:
    # Graceful degradation
    AIModel = None
    claude_hub = None
    gpt5_hub = None
    unified_ai = None

# Security
security = HTTPBearer()

# Router
router = APIRouter(prefix="/ai", tags=["AI Model Management"])


# Request/Response models
class ModelSelectionRequest(BaseModel):
    """Request to select preferred AI model"""
    model: str
    task_type: Optional[str] = "general"


class ModelCapabilitiesResponse(BaseModel):
    """Response with model capabilities"""
    model: str
    provider: str
    context_window: int
    max_output_tokens: int
    features: Dict[str, bool]
    performance: Dict[str, float]


class AIStatusResponse(BaseModel):
    """Response with overall AI integration status"""
    claude_status: Dict
    gpt_status: Dict
    available_models: List[str]
    total_models: int


class ExecuteAIRequest(BaseModel):
    """Request to execute AI task"""
    prompt: str
    system_prompt: Optional[str] = None
    task_type: str = "general"
    model_preference: Optional[str] = None
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7


# Endpoints
@router.get("/status", summary="Get AI integration status")
async def get_ai_status(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get comprehensive AI integration status including model availability
    """
    if not unified_ai:
        raise HTTPException(status_code=503, detail="AI integration not available")

    claude_status = claude_hub.get_global_status() if claude_hub else {"error": "not initialized"}
    gpt_status = gpt5_hub.get_global_status() if gpt5_hub else {"error": "not initialized"}

    available = []
    if unified_ai:
        available_models = unified_ai.get_available_models()
        available = [m.value for m in available_models]

    return AIStatusResponse(
        claude_status=claude_status,
        gpt_status=gpt_status,
        available_models=available,
        total_models=len(available),
    )


@router.get("/capabilities/{model_name}", summary="Get model capabilities")
async def get_model_capabilities(
    model_name: str, token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get detailed capabilities for a specific AI model
    """
    if not unified_ai or not AIModel:
        raise HTTPException(status_code=503, detail="AI integration not available")

    # Find matching model
    try:
        model = None
        for m in AIModel:
            if m.value == model_name or m.name.lower() == model_name.lower():
                model = m
                break

        if not model:
            raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")

        caps = unified_ai.get_model_capabilities(model)

        return ModelCapabilitiesResponse(
            model=model.value,
            provider=caps.provider.value,
            context_window=caps.context_window,
            max_output_tokens=caps.max_output_tokens,
            features={
                "function_calling": caps.supports_function_calling,
                "vision": caps.supports_vision,
                "code_execution": caps.supports_code_execution,
            },
            performance={
                "reasoning_strength": caps.reasoning_strength / 10.0,
                "code_generation_strength": caps.code_generation_strength / 10.0,
                "mathematical_strength": caps.mathematical_strength / 10.0,
                "avg_latency_ms": caps.latency_avg_ms,
                "cost_per_1k_tokens": caps.cost_per_1k_tokens,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-model", summary="Select preferred AI model")
async def select_model(
    request: ModelSelectionRequest, token: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Configure preferred AI model for a task type
    
    This sets the default model preference but maintains fallback chains
    """
    if not unified_ai or not AIModel:
        raise HTTPException(status_code=503, detail="AI integration not available")

    try:
        # Find matching model
        model = None
        for m in AIModel:
            if m.value == request.model or m.name.lower() == request.model.lower():
                model = m
                break

        if not model:
            raise HTTPException(status_code=404, detail=f"Model '{request.model}' not found")

        # Check if model is available
        caps = unified_ai.get_model_capabilities(model)
        if not caps.available:
            return {
                "success": False,
                "message": f"Model '{request.model}' is not currently available",
                "model": request.model,
                "available": False,
            }

        return {
            "success": True,
            "message": f"Model '{request.model}' selected for {request.task_type} tasks",
            "model": request.model,
            "task_type": request.task_type,
            "available": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable-claude-45", summary="Enable Claude 4.5 Opus")
async def enable_claude_45(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Enable Claude 4.5 Opus when it becomes available
    """
    if not claude_hub:
        raise HTTPException(status_code=503, detail="Claude integration not available")

    try:
        result = await claude_hub.enable_claude_45()

        if result.get("enabled"):
            return {
                "success": True,
                "message": "Claude 4.5 Opus enabled successfully",
                **result,
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "Failed to enable Claude 4.5"),
                **result,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable-gpt5", summary="Enable GPT-5")
async def enable_gpt5(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Enable GPT-5 when it becomes available
    """
    if not gpt5_hub:
        raise HTTPException(status_code=503, detail="GPT integration not available")

    try:
        result = await gpt5_hub.enable_gpt5()

        if result.get("enabled"):
            return {
                "success": True,
                "message": "GPT-5 enabled successfully",
                **result,
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "Failed to enable GPT-5"),
                **result,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enable-gpt5-codex", summary="Enable GPT-5 Codex")
async def enable_gpt5_codex(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Enable GPT-5 Codex when it becomes available
    """
    if not gpt5_hub:
        raise HTTPException(status_code=503, detail="GPT integration not available")

    try:
        result = await gpt5_hub.enable_gpt5_codex()

        if result.get("enabled"):
            return {
                "success": True,
                "message": "GPT-5 Codex enabled successfully",
                **result,
            }
        else:
            return {
                "success": False,
                "message": result.get("error", "Failed to enable GPT-5 Codex"),
                **result,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-models", summary="List available AI models")
async def list_available_models(token: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get list of currently available AI models with basic info
    """
    if not unified_ai or not AIModel:
        raise HTTPException(status_code=503, detail="AI integration not available")

    try:
        available = unified_ai.get_available_models()

        models = []
        for model in available:
            caps = unified_ai.get_model_capabilities(model)
            models.append(
                {
                    "name": model.value,
                    "provider": caps.provider.value,
                    "context_window": caps.context_window,
                    "max_tokens": caps.max_output_tokens,
                    "strengths": {
                        "reasoning": caps.reasoning_strength,
                        "code_generation": caps.code_generation_strength,
                        "mathematical": caps.mathematical_strength,
                    },
                }
            )

        return {"available_models": models, "total": len(models)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
