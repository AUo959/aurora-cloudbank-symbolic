"""
Schema Validation for Aurora CloudBank Symbolic L1-L3 Layers

Validates messages against layer-specific schemas to enforce boundary constraints.

DLP: schema_validation_l1_l3
Anchors: T1, SRB
Symbolic tags: SCHEMA_VALIDATION, L1_L3_BOUNDARY
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from jsonschema import validate, ValidationError as JsonSchemaValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    JsonSchemaValidationError = Exception

logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when message fails schema validation"""

    def __init__(self, message: str, layer: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.layer = layer
        self.details = details or {}
        super().__init__(f"Schema validation failed for {layer}: {message}")


class SchemaValidator:
    """Validates messages against L1/L2/L3 layer schemas"""

    def __init__(self):
        """Initialize schema validator with layer schemas"""
        self.schemas: Dict[str, Dict[str, Any]] = {}
        self.schema_dir = Path(__file__).parent.parent / "relays" / "schemas"
        self._load_schemas()

    def _load_schemas(self):
        """Load all layer schemas from disk"""
        schema_files = {
            "L1": "l1_schema.json",
            "L2": "l2_schema.json",
            "L3": "l3_schema.json"
        }

        for layer, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            try:
                if schema_path.exists():
                    with open(schema_path, 'r') as f:
                        self.schemas[layer] = json.load(f)
                    logger.info(f"Loaded schema for {layer} from {schema_path}")
                else:
                    logger.warning(f"Schema file not found for {layer}: {schema_path}")
                    # Provide minimal fallback schema
                    self.schemas[layer] = self._get_fallback_schema(layer)
            except Exception as e:
                logger.error(f"Error loading schema for {layer}: {e}")
                self.schemas[layer] = self._get_fallback_schema(layer)

    def _get_fallback_schema(self, layer: str) -> Dict[str, Any]:
        """Provide minimal fallback schema if file cannot be loaded"""
        return {
            "type": "object",
            "required": ["schema_version", "message_type", "context_tag"],
            "properties": {
                "schema_version": {"type": "string"},
                "message_type": {"type": "string"},
                "context_tag": {"type": "string"}
            }
        }

    def validate(self, message: Dict[str, Any], target_layer: str) -> Dict[str, Any]:
        """
        Validate message against target layer schema.

        Args:
            message: Message payload to validate
            target_layer: Target layer ("L1", "L2", or "L3")

        Returns:
            Validated and normalized message

        Raises:
            SchemaValidationError: If validation fails
        """
        if target_layer not in self.schemas:
            raise SchemaValidationError(
                f"Unknown target layer: {target_layer}",
                target_layer,
                {"available_layers": list(self.schemas.keys())}
            )

        # Add schema version if not present (before validation)
        if "schema_version" not in message:
            message["schema_version"] = "1.0.0"

        # Add timestamp if not present (before validation)
        if "timestamp" not in message:
            import time
            message["timestamp"] = time.time()

        schema = self.schemas[target_layer]

        # If jsonschema is available, use it for validation
        if JSONSCHEMA_AVAILABLE:
            try:
                validate(instance=message, schema=schema)
            except JsonSchemaValidationError as e:
                raise SchemaValidationError(
                    str(e.message),
                    target_layer,
                    {
                        "path": list(e.path),
                        "schema_path": list(e.schema_path),
                        "validator": e.validator
                    }
                )
        else:
            # Fallback: basic validation without jsonschema
            self._basic_validation(message, schema, target_layer)

        logger.info(f"Message validated successfully for {target_layer}")
        return message

    def _basic_validation(self, message: Dict[str, Any], schema: Dict[str, Any], layer: str):
        """Basic validation when jsonschema is not available"""
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in message:
                raise SchemaValidationError(
                    f"Missing required field: {field}",
                    layer,
                    {"required_fields": required_fields}
                )

    def get_schema(self, layer: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific layer"""
        return self.schemas.get(layer)

    def get_available_layers(self) -> list:
        """Get list of available layers"""
        return list(self.schemas.keys())

    def is_l1_compliant(self, message: Dict[str, Any]) -> bool:
        """
        Check if message is L1 compliant (no symbolic/metaphorical content).

        L1 messages must not contain:
        - symbolic_metaphor content_type
        - metaphor_mapping fields
        - narrative_expression
        """
        try:
            self.validate(message, "L1")
            # Additional check: ensure no symbolic content leaked through
            if "content_type" in message:
                symbolic_types = ["symbolic_metaphor", "narrative_expression", "abstract_concept"]
                if message["content_type"] in symbolic_types:
                    return False
            return True
        except SchemaValidationError:
            return False

    def is_l2_compliant(self, message: Dict[str, Any]) -> bool:
        """Check if message is L2 compliant"""
        try:
            self.validate(message, "L2")
            return True
        except SchemaValidationError:
            return False

    def is_l3_compliant(self, message: Dict[str, Any]) -> bool:
        """Check if message is L3 compliant"""
        try:
            self.validate(message, "L3")
            return True
        except SchemaValidationError:
            return False


# Global validator instance
_validator: Optional[SchemaValidator] = None


def get_validator() -> SchemaValidator:
    """Get global schema validator instance"""
    global _validator
    if _validator is None:
        _validator = SchemaValidator()
    return _validator
