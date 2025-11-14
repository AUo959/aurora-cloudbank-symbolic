"""
Redaction Engine

Implements various redaction strategies for detected PII.

Anchor: T1-EDG-001-REDACTION
"""

import hashlib
import secrets
from enum import Enum
from typing import Dict, List, Optional


class RedactionStrategy(Enum):
    """Available redaction strategies."""
    MASK = "mask"              # Replace with asterisks: "john@example.com" -> "****@*******.***"
    HASH = "hash"              # Replace with hash: "john@example.com" -> "hash_abc123..."
    REMOVE = "remove"          # Remove completely: "john@example.com" -> ""
    PARTIAL = "partial"        # Show partial: "john@example.com" -> "j***@e******.com"
    TOKEN = "token"            # Replace with token: "john@example.com" -> "[EMAIL_1]"
    SYNTHETIC = "synthetic"    # Replace with fake data: "john@example.com" -> "user42@domain.com"


class RedactionEngine:
    """
    Handles redaction of detected PII using configurable strategies.
    """

    def __init__(self, default_strategy: RedactionStrategy = RedactionStrategy.MASK):
        """
        Initialize redaction engine.

        Args:
            default_strategy: Default strategy for redaction
        """
        self.default_strategy = default_strategy
        self.token_counter = 0
        self.redaction_map: Dict[str, str] = {}  # Original -> Redacted mapping for audit

    def redact_text(
        self,
        text: str,
        detections: List[Dict],
        strategy: Optional[RedactionStrategy] = None
    ) -> str:
        """
        Redact PII from text based on detections.

        Args:
            text: Original text
            detections: List of PII detections from PIIDetector
            strategy: Redaction strategy to use (or default)

        Returns:
            Redacted text
        """
        if not detections:
            return text

        strategy = strategy or self.default_strategy

        # Sort detections by position (reverse order to maintain indices)
        sorted_detections = sorted(detections, key=lambda x: x['start'], reverse=True)

        redacted_text = text
        for detection in sorted_detections:
            start = detection['start']
            end = detection['end']
            original = detection['match']
            pii_type = detection['type']

            redacted_value = self._apply_strategy(original, pii_type, strategy)

            # Track redaction for audit trail
            self.redaction_map[original] = redacted_value

            # Replace in text
            redacted_text = redacted_text[:start] + redacted_value + redacted_text[end:]

        return redacted_text

    def _apply_strategy(
        self,
        original: str,
        pii_type: str,
        strategy: RedactionStrategy
    ) -> str:
        """Apply specific redaction strategy to a value."""

        if strategy == RedactionStrategy.MASK:
            return self._mask(original)

        elif strategy == RedactionStrategy.HASH:
            return self._hash(original)

        elif strategy == RedactionStrategy.REMOVE:
            return ""

        elif strategy == RedactionStrategy.PARTIAL:
            return self._partial(original, pii_type)

        elif strategy == RedactionStrategy.TOKEN:
            return self._token(pii_type)

        elif strategy == RedactionStrategy.SYNTHETIC:
            return self._synthetic(pii_type)

        return original

    def _mask(self, value: str) -> str:
        """Replace with asterisks, preserving structure."""
        if '@' in value:  # Email
            parts = value.split('@')
            if len(parts) == 2:
                username = '*' * len(parts[0])
                domain_parts = parts[1].split('.')
                domain = '*' * len(domain_parts[0])
                tld = '*' * len(domain_parts[-1]) if len(domain_parts) > 1 else ''
                return f"{username}@{domain}.{tld}" if tld else f"{username}@{domain}"

        # Default: mask everything
        return '*' * len(value)

    def _hash(self, value: str) -> str:
        """Replace with deterministic hash."""
        hash_obj = hashlib.sha256(value.encode())
        return f"hash_{hash_obj.hexdigest()[:12]}"

    def _partial(self, value: str, pii_type: str) -> str:
        """Show partial information."""
        if pii_type == "email":
            parts = value.split('@')
            if len(parts) == 2:
                username = parts[0][:1] + '*' * (len(parts[0]) - 1)
                domain_parts = parts[1].split('.')
                domain = domain_parts[0][:1] + '*' * (len(domain_parts[0]) - 1)
                tld = domain_parts[-1] if len(domain_parts) > 1 else ''
                return f"{username}@{domain}.{tld}" if tld else f"{username}@{domain}"

        elif pii_type == "credit_card":
            # Show last 4 digits
            cleaned = value.replace('-', '').replace(' ', '')
            if len(cleaned) >= 4:
                return '*' * (len(cleaned) - 4) + cleaned[-4:]

        elif pii_type == "phone":
            # Show last 4 digits
            digits = ''.join(c for c in value if c.isdigit())
            if len(digits) >= 4:
                return '*' * (len(value) - 4) + value[-4:]

        # Default: show first and last character
        if len(value) > 2:
            return value[0] + '*' * (len(value) - 2) + value[-1]
        return '*' * len(value)

    def _token(self, pii_type: str) -> str:
        """Replace with numbered token."""
        self.token_counter += 1
        return f"[{pii_type.upper()}_{self.token_counter}]"

    def _synthetic(self, pii_type: str) -> str:
        """Generate synthetic replacement data."""
        if pii_type == "email":
            return f"user{secrets.randbelow(9999)}@example.com"
        elif pii_type == "phone":
            return f"555-{secrets.randbelow(899) + 100:03d}-{secrets.randbelow(9999):04d}"
        elif pii_type == "ssn":
            return (f"{secrets.randbelow(899) + 100:03d}-"
                    f"{secrets.randbelow(89) + 10:02d}-"
                    f"{secrets.randbelow(8999) + 1000:04d}")
        elif pii_type == "credit_card":
            # Generate fake number (not valid per Luhn algorithm)
            return f"{secrets.randbelow(8999) + 1000:04d}-****-****-{secrets.randbelow(8999) + 1000:04d}"
        else:
            return f"[REDACTED_{pii_type.upper()}]"

    def redact_dict(
        self,
        data: Dict,
        scan_results: Dict,
        strategy: Optional[RedactionStrategy] = None
    ) -> Dict:
        """
        Recursively redact PII from dictionary.

        Args:
            data: Original data dictionary
            scan_results: PII scan results from PIIDetector.scan_dict()
            strategy: Redaction strategy to use

        Returns:
            Redacted copy of data
        """
        import copy
        redacted = copy.deepcopy(data)
        strategy = strategy or self.default_strategy

        for key, detections in scan_results.items():
            if key not in redacted:
                continue

            value = redacted[key]

            if isinstance(detections, list) and detections and isinstance(detections[0], dict):
                if 'start' in detections[0]:  # Direct PII matches
                    redacted[key] = self.redact_text(value, detections, strategy)
                else:  # List results
                    for item in detections:
                        idx = item['index']
                        if isinstance(redacted[key][idx], str):
                            redacted[key][idx] = self.redact_text(
                                redacted[key][idx],
                                item['matches'],
                                strategy
                            )
            elif isinstance(detections, dict):
                # Nested dict results
                redacted[key] = self.redact_dict(redacted[key], detections, strategy)

        return redacted

    def get_audit_trail(self) -> Dict:
        """Get audit trail of all redactions performed."""
        return {
            'total_redactions': len(self.redaction_map),
            'redactions': [
                {
                    'original_hash': hashlib.sha256(orig.encode()).hexdigest()[:12],
                    'redacted': red,
                    'length': len(orig)
                }
                for orig, red in self.redaction_map.items()
            ]
        }

    def reset_audit_trail(self):
        """Clear the redaction audit trail."""
        self.redaction_map.clear()
        self.token_counter = 0
