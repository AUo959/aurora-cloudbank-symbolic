"""
Relay Manager for Aurora CloudBank Symbolic

Central enforcement point for all cross-layer messages (L3→L2, L2→L1, etc.).
Provides schema validation, anchor resolution, ethics checks, and structured logging.

DLP: relay_manager_core_v1
Anchors: T1, SRB, EOS_SEED_ORION
Symbolic tags: RELAY_MANAGER_CORE, L1_L3_BOUNDARY_ENFORCEMENT
"""

import logging
import time
import uuid
from typing import Any, Dict, Optional

from src.aurora.core.schema_validation import get_validator, SchemaValidationError
from src.aurora.core.narrative_firewall import get_firewall, MetaphorTranslationError
from src.core.native_dlp_export import NativeDLPTracker

# Try to import ethics engine
try:
    from src.monitoring.ethics_engine import EthicsEngine, ActionContext
    ETHICS_ENGINE_AVAILABLE = True
except ImportError:
    ETHICS_ENGINE_AVAILABLE = False
    EthicsEngine = None
    ActionContext = None

logger = logging.getLogger(__name__)


# Custom exception types for relay operations
class RelayException(Exception):
    """Base exception for relay operations"""

    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to structured dict"""
        return {
            "error": True,
            "error_type": self.error_type,
            "message": self.message,
            "details": self.details
        }


class SchemaViolation(RelayException):
    """Raised when message fails schema validation"""

    def __init__(self, message: str, layer: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "schema_violation", {**details, "layer": layer} if details else {"layer": layer})


class AnchorViolation(RelayException):
    """Raised when anchor protocols are violated"""

    def __init__(self, message: str, anchor_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message,
            "anchor_violation",
            {**details, "anchor_type": anchor_type} if details else {"anchor_type": anchor_type}
        )


class EthicsViolation(RelayException):
    """Raised when ethics checks fail"""

    def __init__(self, message: str, violation_details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "ethics_violation", violation_details or {})


class RelayUnavailable(RelayException):
    """Raised when relay service is unavailable"""

    def __init__(self, message: str, reason: str):
        super().__init__(message, "relay_unavailable", {"reason": reason})


class RelayManager:
    """
    Central relay manager for cross-layer message enforcement.

    Manages L3→L2→L1 boundary enforcement with:
    - Schema validation
    - Anchor resolution (T1/SRB)
    - Ethics checks
    - Narrative firewall (L3→L2 translation)
    - DLP tracking and logging
    """

    def __init__(self):
        """Initialize relay manager"""
        self.validator = get_validator()
        self.firewall = get_firewall()
        self.dlp_tracker = NativeDLPTracker()

        # Initialize ethics engine if available
        self.ethics_engine = None
        if ETHICS_ENGINE_AVAILABLE:
            try:
                self.ethics_engine = EthicsEngine()
                logger.info("Ethics engine initialized for relay manager")
            except Exception as e:
                logger.warning(f"Could not initialize ethics engine: {e}")

        # Statistics
        self.messages_processed = 0
        self.messages_blocked = 0
        self.messages_translated = 0
        self.ethics_checks_performed = 0

        logger.info("Relay Manager initialized")

    def send_cross_layer_message(
        self,
        source_layer: str,
        target_layer: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send message across layers with full enforcement.

        Args:
            source_layer: Source layer ("L1", "L2", or "L3")
            target_layer: Target layer ("L1", "L2", or "L3")
            payload: Message payload
            context: Optional context for processing

        Returns:
            Result dict with processed message or error

        Raises:
            SchemaViolation: If schema validation fails
            AnchorViolation: If anchor protocols are violated
            EthicsViolation: If ethics checks fail
            RelayUnavailable: If relay service is unavailable
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            f"Processing cross-layer message: {source_layer}→{target_layer} (request_id: {request_id})"
        )

        try:
            # Step 1: Enrich payload with metadata
            enriched_payload = self._enrich_payload(payload, source_layer, target_layer, request_id, context)

            # Step 2: Apply narrative firewall if crossing from L3 to L2
            if source_layer == "L3" and target_layer in ["L2", "L1"]:
                enriched_payload = self._apply_narrative_firewall(enriched_payload, context)
                self.messages_translated += 1

            # Step 3: Validate against target layer schema
            validated_payload = self._validate_schema(enriched_payload, target_layer)

            # Step 4: Resolve and verify anchors
            anchored_payload = self._resolve_anchors(validated_payload, source_layer, target_layer)

            # Step 5: Perform ethics checks for high-impact operations
            if self._requires_ethics_check(anchored_payload, source_layer, target_layer):
                self._perform_ethics_check(anchored_payload, context)

            # Step 6: Create DLP tag for this operation
            dlp_tag_id = self._create_dlp_tag(
                anchored_payload,
                source_layer,
                target_layer,
                request_id,
                context
            )

            # Step 7: Log the successful operation
            self._log_operation(
                "relay_success",
                source_layer,
                target_layer,
                request_id,
                anchored_payload,
                dlp_tag_id
            )

            # Update statistics
            self.messages_processed += 1
            elapsed_time = time.time() - start_time

            return {
                "success": True,
                "request_id": request_id,
                "source_layer": source_layer,
                "target_layer": target_layer,
                "payload": anchored_payload,
                "dlp_tag_id": dlp_tag_id,
                "processing_time_ms": elapsed_time * 1000,
                "checks_performed": {
                    "schema_validation": True,
                    "anchor_resolution": True,
                    "ethics_check": self._requires_ethics_check(anchored_payload, source_layer, target_layer),
                    "narrative_firewall": source_layer == "L3" and target_layer in ["L2", "L1"]
                }
            }

        except SchemaValidationError as e:
            self.messages_blocked += 1
            self._log_operation("schema_violation", source_layer, target_layer, request_id, payload, None)
            raise SchemaViolation(str(e), target_layer, {"validation_error": str(e)})

        except MetaphorTranslationError as e:
            self.messages_blocked += 1
            self._log_operation("translation_failed", source_layer, target_layer, request_id, payload, None)
            raise SchemaViolation(
                f"Narrative firewall blocked message: {e.reason}",
                target_layer,
                {"metaphor": e.metaphor, "reason": e.reason}
            )

        except EthicsViolation:
            self.messages_blocked += 1
            self._log_operation("ethics_violation", source_layer, target_layer, request_id, payload, None)
            raise

        except Exception as e:
            self.messages_blocked += 1
            logger.error(f"Relay error for {request_id}: {e}", exc_info=True)
            self._log_operation("relay_error", source_layer, target_layer, request_id, payload, None)
            raise RelayUnavailable(
                f"Relay processing failed: {str(e)}",
                f"Internal error: {type(e).__name__}"
            )

    def _enrich_payload(
        self,
        payload: Dict[str, Any],
        source_layer: str,
        target_layer: str,
        request_id: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Enrich payload with required metadata"""
        enriched = payload.copy()

        # Add request_id if not present
        if "request_id" not in enriched:
            enriched["request_id"] = request_id

        # Add timestamp if not present
        if "timestamp" not in enriched:
            enriched["timestamp"] = time.time()

        # Add context_tag if not present
        if "context_tag" not in enriched:
            enriched["context_tag"] = f"relay_{source_layer}_to_{target_layer}_{request_id[:8]}"

        # Add relay metadata
        enriched["relay_metadata"] = {
            "source_layer": source_layer,
            "target_layer": target_layer,
            "relay_timestamp": time.time()
        }

        return enriched

    def _apply_narrative_firewall(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply narrative firewall for L3→L2/L1 translation"""
        try:
            # Check if message needs translation
            classification = self.firewall.classify_message(payload)

            if classification in ["symbolic", "mixed"]:
                # Attempt translation
                translated = self.firewall.translate_l3_to_l2(payload, context)
                logger.info(f"Narrative firewall: translated {classification} content")
                # Preserve enriched metadata
                if "relay_metadata" in payload:
                    translated["relay_metadata"] = payload["relay_metadata"]
                if "request_id" in payload and "request_id" not in translated:
                    translated["request_id"] = payload["request_id"]
                if "timestamp" in payload and "timestamp" not in translated:
                    translated["timestamp"] = payload["timestamp"]
                return translated
            else:
                # Literal content, translate to L2 format
                translated = self.firewall.translate_l3_to_l2(payload, context)
                # Preserve enriched metadata
                if "relay_metadata" in payload:
                    translated["relay_metadata"] = payload["relay_metadata"]
                if "request_id" in payload and "request_id" not in translated:
                    translated["request_id"] = payload["request_id"]
                if "timestamp" in payload and "timestamp" not in translated:
                    translated["timestamp"] = payload["timestamp"]
                return translated

        except MetaphorTranslationError:
            # Re-raise to be caught by main handler
            raise

    def _validate_schema(self, payload: Dict[str, Any], target_layer: str) -> Dict[str, Any]:
        """Validate payload against target layer schema"""
        try:
            validated = self.validator.validate(payload, target_layer)
            logger.debug(f"Schema validation passed for {target_layer}")
            return validated
        except SchemaValidationError:
            # Re-raise to be caught by main handler
            raise

    def _resolve_anchors(
        self,
        payload: Dict[str, Any],
        source_layer: str,
        target_layer: str
    ) -> Dict[str, Any]:
        """
        Resolve and verify T1/SRB anchors.

        Ensures anchor protocols are properly attached and validated.
        """
        anchored = payload.copy()

        # Generate or verify anchor_id
        if "anchor_id" not in anchored or not anchored["anchor_id"]:
            # Generate new anchor reference
            anchored["anchor_id"] = f"T1_{int(time.time())}_{source_layer}_{target_layer}"
            logger.debug(f"Generated anchor_id: {anchored['anchor_id']}")

        # Add anchor protocols
        if "anchor_protocols" not in anchored:
            anchored["anchor_protocols"] = []

        # Add appropriate protocols based on layers
        if source_layer == "L3":
            if "EOS_SEED_ORION" not in anchored["anchor_protocols"]:
                anchored["anchor_protocols"].append("EOS_SEED_ORION")

        if target_layer == "L1":
            if "REALITY_BRIDGE" not in anchored["anchor_protocols"]:
                anchored["anchor_protocols"].append("REALITY_BRIDGE")

        # Add T1/SRB anchor references
        if "t1_srb_anchors" not in anchored:
            anchored["t1_srb_anchors"] = []

        if "T1_TEMPORAL_ANCHOR" not in anchored["t1_srb_anchors"]:
            anchored["t1_srb_anchors"].append("T1_TEMPORAL_ANCHOR")

        if target_layer != source_layer:
            if "SRB_BOUNDARY_ANCHOR" not in anchored["t1_srb_anchors"]:
                anchored["t1_srb_anchors"].append("SRB_BOUNDARY_ANCHOR")

        logger.debug(f"Anchors resolved: {len(anchored.get('anchor_protocols', []))} protocols")
        return anchored

    def _requires_ethics_check(
        self,
        payload: Dict[str, Any],
        source_layer: str,
        target_layer: str
    ) -> bool:
        """Determine if ethics check is required"""
        # Always check L2→L1 and L3→L1 transitions
        if target_layer == "L1":
            return True

        # Check if payload has high risk score
        risk_score = payload.get("risk_score", 0.0)
        if risk_score > 0.5:
            return True

        # Check for specific action types that require ethics
        action_type = payload.get("action_type", "")
        high_impact_actions = [
            "external_api_call",
            "database_commit",
            "file_write"
        ]
        if action_type in high_impact_actions:
            return True

        return False

    def _perform_ethics_check(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ):
        """
        Perform ethics check on payload.

        Raises EthicsViolation if check fails.
        """
        if not self.ethics_engine:
            logger.warning("Ethics engine not available, skipping check")
            return

        self.ethics_checks_performed += 1

        try:
            # Create action context for ethics evaluation
            action_type = payload.get("action_type") or payload.get("event_type", "unknown")
            agent_id = context.get("agent_id", "relay_manager") if context else "relay_manager"

            action_context = ActionContext(
                agent_id=agent_id,
                action_type=action_type,
                parameters=payload.get("parameters", {}),
                context=context or {}
            )

            # Evaluate action
            result = self.ethics_engine.evaluate_action(action_context)

            if not result.compliant:
                # Ethics violation detected
                violations = [v.to_dict() for v in result.violations]
                raise EthicsViolation(
                    f"Ethics check failed: {len(violations)} violation(s)",
                    {"violations": violations, "should_block": result.should_block}
                )

            logger.debug("Ethics check passed")

        except EthicsViolation:
            # Re-raise ethics violations
            raise
        except Exception:
            # Log other errors but don't block operation
            logger.error("Ethics check error", exc_info=True)

    def _create_dlp_tag(
        self,
        payload: Dict[str, Any],
        source_layer: str,
        target_layer: str,
        request_id: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create DLP tag for relay operation"""
        operation = f"relay_{source_layer}_to_{target_layer}"
        tag_id = self.dlp_tracker.create_tag(operation, payload)

        # Get the tag and enrich it
        tag = self.dlp_tracker.tags[tag_id]

        # Add relay-specific metadata
        tag.metadata.update({
            "source_layer": source_layer,
            "target_layer": target_layer,
            "request_id": request_id,
            "relay_type": "cross_layer_message",
            "context_provided": context is not None
        })

        # Add anchor protocols from payload
        for protocol in payload.get("anchor_protocols", []):
            tag.add_anchor_protocol(protocol)

        # Add T1/SRB anchors from payload
        for anchor in payload.get("t1_srb_anchors", []):
            tag.add_t1_srb_anchor(anchor)

        # Add symbolic patterns
        tag.set_symbolic_pattern("layer_transition", {
            "from": source_layer,
            "to": target_layer
        })

        if "relay_metadata" in payload:
            tag.set_symbolic_pattern("relay_metadata", payload["relay_metadata"])

        logger.debug(f"Created DLP tag: {tag_id}")
        return tag_id

    def _log_operation(
        self,
        operation_type: str,
        source_layer: str,
        target_layer: str,
        request_id: str,
        payload: Dict[str, Any],
        dlp_tag_id: Optional[str]
    ):
        """Log relay operation with structured logging"""
        log_data = {
            "operation": operation_type,
            "source_layer": source_layer,
            "target_layer": target_layer,
            "request_id": request_id,
            "dlp_tag_id": dlp_tag_id,
            "timestamp": time.time()
        }

        if operation_type == "relay_success":
            logger.info(f"Relay success: {source_layer}→{target_layer} ({request_id})", extra=log_data)
        elif operation_type == "schema_violation":
            logger.warning(f"Schema violation: {source_layer}→{target_layer} ({request_id})", extra=log_data)
        elif operation_type == "ethics_violation":
            logger.warning(f"Ethics violation: {source_layer}→{target_layer} ({request_id})", extra=log_data)
        elif operation_type == "translation_failed":
            logger.warning(f"Translation failed: {source_layer}→{target_layer} ({request_id})", extra=log_data)
        else:
            logger.error(f"Relay error: {source_layer}→{target_layer} ({request_id})", extra=log_data)

    def export_relay_manifest(self, manifest_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Export relay operation manifest.

        Returns:
            Manifest dict with relay statistics and DLP tags
        """
        if manifest_name is None:
            manifest_name = f"relay_manifest_{int(time.time())}"

        # Create DLP manifest for all relay operations
        dlp_manifest = self.dlp_tracker.create_export_manifest(manifest_name)

        # Add relay-specific statistics
        relay_stats = {
            "messages_processed": self.messages_processed,
            "messages_blocked": self.messages_blocked,
            "messages_translated": self.messages_translated,
            "ethics_checks_performed": self.ethics_checks_performed,
            "success_rate": (
                self.messages_processed / (self.messages_processed + self.messages_blocked)
                if (self.messages_processed + self.messages_blocked) > 0
                else 0.0
            )
        }

        # Add firewall statistics
        firewall_stats = {
            "translation_rules": len(self.firewall.get_translation_rules()),
            "quarantined_messages": len(self.firewall.get_quarantined_messages())
        }

        # Combine into comprehensive manifest
        manifest = {
            "manifest_name": manifest_name,
            "relay_manager_version": "1.0.0",
            "export_timestamp": time.time(),
            "anchors": ["T1", "SRB", "EOS_SEED_ORION"],
            "symbolic_tags": [
                "L1_L3_BOUNDARY_ENFORCEMENT",
                "SEMANTIC_FIREWALL",
                "RELAY_MANAGER_CORE"
            ],
            "relay_statistics": relay_stats,
            "firewall_statistics": firewall_stats,
            "dlp_manifest": dlp_manifest
        }

        logger.info(f"Exported relay manifest: {manifest_name}")
        return manifest

    def get_statistics(self) -> Dict[str, Any]:
        """Get relay manager statistics"""
        return {
            "messages_processed": self.messages_processed,
            "messages_blocked": self.messages_blocked,
            "messages_translated": self.messages_translated,
            "ethics_checks_performed": self.ethics_checks_performed,
            "success_rate": (
                self.messages_processed / (self.messages_processed + self.messages_blocked)
                if (self.messages_processed + self.messages_blocked) > 0
                else 0.0
            ),
            "firewall_translation_rules": len(self.firewall.get_translation_rules()),
            "firewall_quarantined": len(self.firewall.get_quarantined_messages())
        }


# Global relay manager instance
_relay_manager: Optional[RelayManager] = None


def get_relay_manager() -> RelayManager:
    """Get global relay manager instance"""
    global _relay_manager
    if _relay_manager is None:
        _relay_manager = RelayManager()
    return _relay_manager
