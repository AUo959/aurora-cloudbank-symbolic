"""
Narrative Firewall for Aurora CloudBank Symbolic

Translates symbolic L3 messages to safe, concrete L2 representations or rejects them.
Prevents metaphorical/symbolic content from leaking into L2/L1 layers.

DLP: narrative_firewall_l3_l2
Anchors: T1, SRB
Symbolic tags: NARRATIVE_FIREWALL, L3_L2_TRANSLATION, METAPHOR_FILTERING
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MetaphorTranslationError(Exception):
    """Raised when metaphor cannot be safely translated"""

    def __init__(self, message: str, metaphor: str, reason: str):
        self.message = message
        self.metaphor = metaphor
        self.reason = reason
        super().__init__(f"Metaphor translation failed: {message}")


class NarrativeFirewall:
    """
    Narrative firewall for L3→L2 boundary enforcement.

    Classifies messages as symbolic vs literal and translates or rejects them.
    """

    def __init__(self):
        """Initialize narrative firewall with translation rules"""
        self.translation_rules: Dict[str, str] = {}
        self.quarantined_messages: List[Dict[str, Any]] = []
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default metaphor-to-concrete translation rules"""
        # Pattern: metaphor -> concrete L2 event_type
        self.translation_rules = {
            # Celestial/weather metaphors
            "the stars weep": "solar_storm",
            "stellar tears": "solar_storm",
            "cosmic storm": "solar_storm",
            "heavens darken": "anomaly_event",
            "void opens": "anomaly_event",

            # Emotional/abstract metaphors
            "system trembles": "drift_measurement",
            "memory fades": "memory_operation",
            "consciousness shifts": "entity_interaction",
            "wisdom flows": "symbolic_computation",
            "truth emerges": "architecture_validation",

            # Narrative metaphors
            "the fleet gathers": "faction_event",
            "shadows lengthen": "anomaly_event",
            "light fades": "scenario_execution",
            "hope rises": "entity_interaction",
            "danger looms": "scenario_execution"
        }

    def add_translation_rule(self, metaphor: str, concrete_event: str):
        """
        Add a new metaphor-to-concrete translation rule.

        Args:
            metaphor: Symbolic/metaphorical phrase
            concrete_event: Concrete L2 event_type to translate to
        """
        self.translation_rules[metaphor.lower()] = concrete_event
        logger.info(f"Added translation rule: '{metaphor}' -> '{concrete_event}'")

    def classify_message(self, message: Dict[str, Any]) -> str:
        """
        Classify message as 'symbolic', 'literal', or 'mixed'.

        Args:
            message: Message to classify

        Returns:
            Classification: 'symbolic', 'literal', or 'mixed'
        """
        # Check content_type for symbolic indicators first
        content_type = message.get("content_type", "")
        symbolic_types = [
            "symbolic_metaphor",
            "narrative_expression",
            "abstract_concept",
            "poetic_insight",
            "philosophical_query"
        ]

        if content_type in symbolic_types:
            return "symbolic"

        # Check payload for symbolic content
        payload = message.get("payload", {})
        if "metaphor_mapping" in payload:
            return "mixed"

        # Check text content for poetic/metaphorical language
        text = payload.get("text", "")
        if text:
            # Simple heuristics for symbolic language
            symbolic_indicators = [
                "metaphor", "symbol", "represent", "embody",
                "essence", "meaning", "spirit", "soul",
                "weep", "whisper", "dream", "cosmic", "void"
            ]
            if any(indicator in text.lower() for indicator in symbolic_indicators):
                return "mixed"

        # If content_type is lore_fragment or similar non-symbolic types, 
        # and no symbolic content detected, classify as literal
        literal_types = ["lore_fragment", "ethics_consideration", "axiom_evaluation"]
        if content_type in literal_types:
            return "literal"

        # Check message_type - but only after checking content
        if message.get("message_type") == "l3_symbolic":
            # If it's L3 but no symbolic indicators found, treat as literal
            return "literal"

        return "literal"

    def translate_l3_to_l2(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Translate L3 symbolic message to L2 concrete simulation event.

        Args:
            message: L3 symbolic message
            context: Optional context for translation

        Returns:
            Translated L2 message

        Raises:
            MetaphorTranslationError: If translation fails or is unsafe
        """
        classification = self.classify_message(message)

        if classification == "literal":
            # Already literal, just repackage as L2
            return self._repackage_as_l2(message)

        # Extract symbolic content
        payload = message.get("payload", {})
        text = payload.get("text", "").lower().strip()
        symbols = payload.get("symbols", [])

        # Attempt translation via rules
        concrete_event = self._find_translation(text, symbols)

        if concrete_event:
            # Successfully translated
            l2_message = {
                "schema_version": "1.0.0",
                "message_type": "l2_simulation_event",
                "event_type": concrete_event,
                "parameters": self._extract_parameters(message, context),
                "context_tag": message.get("context_tag", "translated_from_l3"),
                "anchor_id": message.get("anchor_id"),
                "lore_id": self._extract_lore_id(message),
                "translation_metadata": {
                    "original_content_type": message.get("content_type"),
                    "symbolic_text": text,
                    "translation_applied": True
                }
            }

            logger.info(f"Translated L3 message to L2: {text[:50]} -> {concrete_event}")
            return l2_message
        else:
            # Cannot translate - quarantine
            self._quarantine_message(message, "No translation rule found")
            raise MetaphorTranslationError(
                f"Cannot translate symbolic content: {text[:100]}",
                text,
                "No matching translation rule found"
            )

    def _find_translation(self, text: str, symbols: List[str]) -> Optional[str]:
        """Find translation rule for text or symbols"""
        # Check exact match first
        if text in self.translation_rules:
            return self.translation_rules[text]

        # Check partial matches
        for metaphor, concrete in self.translation_rules.items():
            if metaphor in text:
                return concrete

        # Check symbols
        for symbol in symbols:
            symbol_lower = symbol.lower()
            if symbol_lower in self.translation_rules:
                return self.translation_rules[symbol_lower]

        return None

    def _repackage_as_l2(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Repackage literal message as L2 format"""
        payload = message.get("payload", {})
        
        return {
            "schema_version": message.get("schema_version", "1.0.0"),
            "message_type": "l2_simulation_event",
            "event_type": "symbolic_computation",  # Default event type
            "parameters": payload if isinstance(payload, dict) else {"data": payload},
            "context_tag": message.get("context_tag", "literal_from_l3"),
            "anchor_id": message.get("anchor_id"),
            "timestamp": message.get("timestamp"),
            "request_id": message.get("request_id"),
            "relay_metadata": message.get("relay_metadata")
        }

    def _extract_parameters(
        self,
        message: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract parameters for L2 event from L3 message"""
        payload = message.get("payload", {})
        params = {}

        # Include relevant payload fields
        if "symbols" in payload:
            params["symbolic_elements"] = payload["symbols"]

        # Include context if provided
        if context:
            params["translation_context"] = context

        # Include original text as description
        if "text" in payload:
            params["description"] = payload["text"]

        return params

    def _extract_lore_id(self, message: Dict[str, Any]) -> Optional[str]:
        """Extract lore_id from L3 message if present"""
        payload = message.get("payload", {})
        return payload.get("narrative_context")

    def _quarantine_message(self, message: Dict[str, Any], reason: str):
        """Quarantine untranslatable message for review"""
        quarantine_entry = {
            "message": message,
            "reason": reason,
            "timestamp": message.get("timestamp"),
            "context_tag": message.get("context_tag")
        }
        self.quarantined_messages.append(quarantine_entry)
        logger.warning(f"Quarantined message: {reason}")

    def get_quarantined_messages(self) -> List[Dict[str, Any]]:
        """Get all quarantined messages"""
        return self.quarantined_messages.copy()

    def clear_quarantine(self):
        """Clear quarantined messages"""
        count = len(self.quarantined_messages)
        self.quarantined_messages.clear()
        logger.info(f"Cleared {count} quarantined messages")

    def is_safe_for_l2(self, message: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Check if message is safe for L2 layer.

        Returns:
            Tuple of (is_safe, reason_if_not_safe)
        """
        classification = self.classify_message(message)

        if classification == "literal":
            return True, None

        # Check if translation is possible
        payload = message.get("payload", {})
        text = payload.get("text", "").lower().strip()
        symbols = payload.get("symbols", [])

        concrete_event = self._find_translation(text, symbols)

        if concrete_event:
            return True, None
        else:
            return False, f"No translation rule for symbolic content: {text[:50]}"

    def get_translation_rules(self) -> Dict[str, str]:
        """Get all translation rules"""
        return self.translation_rules.copy()


# Global firewall instance
_firewall: Optional[NarrativeFirewall] = None


def get_firewall() -> NarrativeFirewall:
    """Get global narrative firewall instance"""
    global _firewall
    if _firewall is None:
        _firewall = NarrativeFirewall()
    return _firewall
