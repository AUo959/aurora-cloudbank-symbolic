"""
Relay Manager API Routes (Updated for Ethics Gate Integration)

Provides HTTP endpoints for the Relay Manager with ethics gate integration.
Compatible with merged RelayManager from PR #342.

DLP: relay_manager_api_routes_v2
Anchors: T1, SRB, EOS_SEED_ORION
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.aurora.relays.relay_manager import RelayManager, RelayMessage
from src.aurora.ethics.ethics_gate import EthicsViolation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/relay", tags=["relay-manager"])

# Singleton relay manager instance
_relay_manager_instance: Optional[RelayManager] = None


def get_relay_manager() -> RelayManager:
    """Get or create singleton relay manager instance"""
    global _relay_manager_instance
    if _relay_manager_instance is None:
        _relay_manager_instance = RelayManager()
    return _relay_manager_instance


# Pydantic models for API requests/responses
class SendMessageRequest(BaseModel):
    """Request to send a cross-layer message"""
    source_layer: str = Field(..., description="Source layer (L1, L2, or L3)")
    target_layer: str = Field(..., description="Target layer (L1, L2, or L3)")
    payload: Dict[str, Any] = Field(..., description="Message payload")
    message_type: str = Field(default="api_relay", description="Message type")
    requires_ethics_check: bool = Field(
        default=False, description="Whether ethics check is required"
    )
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context")


class SendMessageResponse(BaseModel):
    """Response from sending a cross-layer message"""
    success: bool
    request_id: str
    source_layer: str
    target_layer: str
    message_type: str
    verdict: Optional[Dict[str, Any]] = None
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str = "Relay Manager"
    available: bool
    timestamp: str


class StatisticsResponse(BaseModel):
    """Relay manager statistics"""
    messages_processed: int
    messages_blocked: int
    success_rate: float
    ethics_checks_performed: int


# API routes
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint for relay manager.

    DLP: relay_manager_health_check
    """
    try:
        relay = get_relay_manager()
        available = relay is not None

        return HealthResponse(
            status="healthy" if available else "unavailable",
            available=available,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return HealthResponse(
            status="unhealthy",
            available=False,
            timestamp=datetime.now(timezone.utc).isoformat()
        )


@router.post("/send", response_model=SendMessageResponse)
async def send_cross_layer_message(
    request: SendMessageRequest
) -> SendMessageResponse:
    """
    Send a message across layers with ethics evaluation.

    DLP: relay_send_message
    Anchors: T1, SRB
    """
    import time

    start = time.time()
    relay = get_relay_manager()

    try:
        # Create RelayMessage from request
        message = RelayMessage(
            message_id=f"msg_{uuid.uuid4().hex[:8]}",
            source_layer=request.source_layer,
            target_layer=request.target_layer,
            message_type=request.message_type,
            payload=request.payload,
            requires_ethics_check=request.requires_ethics_check,
            context_tag=f"api_{request.source_layer}_to_{request.target_layer}"
        )

        # Send message through relay manager
        result = await relay.send_message(message)

        processing_time = (time.time() - start) * 1000

        return SendMessageResponse(
            success=result.get("success", True),
            request_id=message.message_id,
            source_layer=message.source_layer,
            target_layer=message.target_layer,
            message_type=message.message_type,
            verdict=result.get("verdict"),
            processing_time_ms=processing_time
        )

    except EthicsViolation as e:
        logger.warning("Ethics violation: %s", str(e))
        raise HTTPException(
            status_code=403,
            detail={
                "error": True,
                "error_type": "EthicsViolation",
                "message": str(e),
                "details": {}
            }
        )
    except Exception as e:
        logger.error("Unexpected error in relay: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_type": "InternalError",
                "message": str(e),
                "details": {}
            }
        )


@router.get("/stats", response_model=StatisticsResponse)
async def get_statistics() -> StatisticsResponse:
    """
    Get relay manager statistics.

    DLP: relay_statistics
    """
    try:
        relay = get_relay_manager()

        # Calculate success rate
        total = max(relay.messages_processed, 1)
        success_rate = 1.0 - (relay.messages_blocked / total)

        return StatisticsResponse(
            messages_processed=relay.messages_processed,
            messages_blocked=relay.messages_blocked,
            success_rate=success_rate,
            ethics_checks_performed=relay.messages_blocked
        )
    except Exception as e:
        logger.error("Failed to get statistics: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get detailed relay manager status.

    DLP: relay_status
    """
    try:
        relay = get_relay_manager()

        return {
            "status": "operational",
            "messages_processed": relay.messages_processed,
            "messages_blocked": relay.messages_blocked,
            "ethics_gate_active": relay.ethics_gate is not None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error("Failed to get status: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
