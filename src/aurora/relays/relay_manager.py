"""
Relay Manager with Ethics Gate Integration

Manages cross-layer message relay with ethics evaluation before state changes.
Replaces placeholder EthicsAdapter with full EthicsGate integration (PR #340).

DLP: relay_manager_v1
Anchors: T1, SRB, EOS_SEED_ORION
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.aurora.ethics.ethics_gate import (
    EthicsGate,
    GUMASEthicsClient,
    EthicsViolation
)

logger = logging.getLogger(__name__)


@dataclass
class RelayMessage:
    """
    Cross-layer relay message.
    
    Attributes:
        message_id: Unique message identifier
        source_layer: Source layer (e.g., "L1", "L2", "L3")
        target_layer: Target layer
        message_type: Type of message (e.g., "state_change", "query", "notification")
        payload: Message payload
        requires_ethics_check: Whether this message requires ethics evaluation
        context_tag: DLP context tag
        timestamp: Message timestamp
    """
    message_id: str
    source_layer: str
    target_layer: str
    message_type: str
    payload: Dict[str, Any]
    requires_ethics_check: bool = False
    context_tag: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "message_id": self.message_id,
            "source_layer": self.source_layer,
            "target_layer": self.target_layer,
            "message_type": self.message_type,
            "payload": self.payload,
            "requires_ethics_check": self.requires_ethics_check,
            "context_tag": self.context_tag,
            "timestamp": self.timestamp
        }


class RelayManager:
    """
    Cross-layer relay manager with ethics gate integration.
    
    This manager handles message passing between system layers (L1/L2/L3)
    and enforces ethics checks for state-changing operations.
    
    Integration replaces placeholder EthicsAdapter from PR #340.
    
    Usage:
        manager = RelayManager(ethics_gate=ethics_gate)
        
        message = RelayMessage(
            message_id="msg_001",
            source_layer="L1",
            target_layer="L2",
            message_type="state_change",
            payload={"action": "update_config", "key": "threshold", "value": 0.8},
            requires_ethics_check=True
        )
        
        result = await manager.send_message(message)
    """
    
    def __init__(
        self,
        ethics_gate: Optional[EthicsGate] = None,
        base_url: str = "http://localhost:8000"
    ):
        """
        Initialize relay manager.
        
        Args:
            ethics_gate: Ethics gate for evaluation (creates default if None)
            base_url: Base URL for GUMAS API
        """
        if ethics_gate is None:
            client = GUMASEthicsClient(base_url=base_url)
            self.ethics_gate = EthicsGate(client=client, threshold=0.7)
        else:
            self.ethics_gate = ethics_gate
        
        self.messages_processed = 0
        self.messages_blocked = 0
        
        logger.info(
            "Relay manager initialized with ethics gate",
            extra={
                "anchors": ["EOS_SEED_ORION"],
                "aurora_module": "relay_manager"
            }
        )
    
    async def send_message(self, message: RelayMessage) -> Dict[str, Any]:
        """
        Send cross-layer message with ethics check if required.
        
        If the message requires ethics check and is state-changing,
        evaluates through ethics gate before allowing transmission.
        
        Args:
            message: Relay message to send
        
        Returns:
            Result dictionary with success, message, verdict, etc.
        
        Raises:
            EthicsViolation: If message is blocked by ethics evaluation
        """
        self.messages_processed += 1
        
        logger.info(
            "Processing relay message: %s (%s -> %s)",
            message.message_id,
            message.source_layer,
            message.target_layer,
            extra={
                "relay_message": message.to_dict(),
                "aurora_module": "relay_manager"
            }
        )
        
        # Check if ethics evaluation is required
        if message.requires_ethics_check:
            try:
                # Construct action for ethics evaluation
                action = {
                    "type": f"relay_{message.message_type}",
                    "source_layer": message.source_layer,
                    "target_layer": message.target_layer,
                    "payload": message.payload
                }
                
                context = {
                    "agent_id": "relay_manager",
                    "source": "relay_system",
                    "message_id": message.message_id,
                    "context_tag": message.context_tag
                }
                
                # Evaluate through ethics gate
                verdict = await self.ethics_gate.evaluate(action, context)
                
                # Block if not allowed
                if not verdict.allowed:
                    self.messages_blocked += 1
                    
                    logger.warning(
                        "Relay message blocked by ethics gate: %s (score=%.2f, reason=%s)",
                        message.message_id,
                        verdict.score,
                        verdict.reason,
                        extra={
                            "relay_message": message.to_dict(),
                            "verdict": verdict.to_dict(),
                            "aurora_module": "relay_manager"
                        }
                    )
                    
                    raise EthicsViolation(
                        f"Relay message blocked: {verdict.reason}",
                        verdict
                    )
                
                logger.info(
                    "Relay message passed ethics check: %s (score=%.2f)",
                    message.message_id,
                    verdict.score,
                    extra={
                        "relay_message": message.to_dict(),
                        "verdict": verdict.to_dict(),
                        "aurora_module": "relay_manager"
                    }
                )
                
            except EthicsViolation:
                raise
            except Exception as e:
                logger.error(
                    "Ethics evaluation failed for relay message: %s",
                    e,
                    extra={
                        "relay_message": message.to_dict(),
                        "aurora_module": "relay_manager"
                    },
                    exc_info=True
                )
                # Fail safe: block on error
                self.messages_blocked += 1
                raise EthicsViolation(
                    f"Ethics evaluation error: {str(e)}",
                    None
                )
        
        # Message passed (or didn't require ethics check)
        # In real implementation, would actually transmit message here
        result = {
            "success": True,
            "message_id": message.message_id,
            "status": "delivered",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            "Relay message delivered: %s",
            message.message_id,
            extra={
                "result": result,
                "aurora_module": "relay_manager"
            }
        )
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get relay manager statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "messages_processed": self.messages_processed,
            "messages_blocked": self.messages_blocked,
            "block_rate": (
                self.messages_blocked / self.messages_processed
                if self.messages_processed > 0
                else 0.0
            )
        }
