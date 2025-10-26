"""
PII Detection Rules Engine

Implements pattern-based and ML-assisted detection of personally identifiable
information (PII) across various data formats.

Anchor: T1-EDG-001-DETECTION
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Pattern


class PIIType(Enum):
    """Categories of PII that can be detected."""
    EMAIL = "email"
    SSN = "ssn"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DRIVER_LICENSE = "driver_license"
    PASSPORT = "passport"
    BANK_ACCOUNT = "bank_account"
    DATE_OF_BIRTH = "date_of_birth"
    FULL_NAME = "full_name"
    ADDRESS = "address"
    CUSTOM = "custom"


@dataclass
class DetectionRule:
    """
    Represents a single PII detection rule.

    Attributes:
        pii_type: Type of PII this rule detects
        pattern: Regex pattern for detection
        confidence: Confidence score (0.0-1.0)
        region: Optional region-specific rule (e.g., 'US', 'EU')
        description: Human-readable description
    """
    pii_type: PIIType
    pattern: Pattern[str]
    confidence: float
    region: Optional[str] = None
    description: str = ""

    def matches(self, text: str) -> List[Dict[str, any]]:
        """
        Find all matches of this rule in the given text.

        Returns:
            List of dicts with keys: 'start', 'end', 'match', 'type', 'confidence'
        """
        matches = []
        for match in self.pattern.finditer(text):
            matches.append({
                'start': match.start(),
                'end': match.end(),
                'match': match.group(),
                'type': self.pii_type.value,
                'confidence': self.confidence,
                'region': self.region
            })
        return matches


class PIIDetector:
    """
    Main PII detection engine using configurable rules.
    """

    def __init__(self, region: str = "US"):
        """
        Initialize detector with default rules for specified region.

        Args:
            region: Region code for region-specific detection rules
        """
        self.region = region
        self.rules: List[DetectionRule] = []
        self._load_default_rules()

    def _load_default_rules(self):
        """Load default detection rules for common PII types."""

        # Email address (RFC 5322 simplified)
        self.rules.append(DetectionRule(
            pii_type=PIIType.EMAIL,
            pattern=re.compile(
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ),
            confidence=0.95,
            description="Email address detection"
        ))

        # US Social Security Number (XXX-XX-XXXX)
        if self.region == "US":
            self.rules.append(DetectionRule(
                pii_type=PIIType.SSN,
                pattern=re.compile(
                    r'\b\d{3}-\d{2}-\d{4}\b'
                ),
                confidence=0.90,
                region="US",
                description="US Social Security Number (XXX-XX-XXXX)"
            ))

            # US Phone Number (various formats)
            self.rules.append(DetectionRule(
                pii_type=PIIType.PHONE,
                pattern=re.compile(
                    r'\b(\+1[-.\s]?)?'
                    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
                ),
                confidence=0.85,
                region="US",
                description="US phone number"
            ))

        # Credit Card Number (Luhn algorithm check needed for higher confidence)
        self.rules.append(DetectionRule(
            pii_type=PIIType.CREDIT_CARD,
            pattern=re.compile(
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
            ),
            confidence=0.70,  # Lower confidence without Luhn validation
            description="Credit card number pattern"
        ))

        # IPv4 Address
        self.rules.append(DetectionRule(
            pii_type=PIIType.IP_ADDRESS,
            pattern=re.compile(
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            ),
            confidence=0.80,
            description="IPv4 address"
        ))

        # Date of Birth (various formats)
        self.rules.append(DetectionRule(
            pii_type=PIIType.DATE_OF_BIRTH,
            pattern=re.compile(
                r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|'
                r'\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
            ),
            confidence=0.60,  # Lower confidence - could be any date
            description="Date pattern (potential DOB)"
        ))

    def add_rule(self, rule: DetectionRule):
        """Add a custom detection rule."""
        self.rules.append(rule)

    def detect(self, text: str, min_confidence: float = 0.5) -> List[Dict]:
        """
        Scan text for PII using all loaded rules.

        Args:
            text: Text to scan
            min_confidence: Minimum confidence threshold (0.0-1.0)

        Returns:
            List of detected PII instances with metadata
        """
        all_matches = []

        for rule in self.rules:
            if rule.confidence >= min_confidence:
                matches = rule.matches(text)
                all_matches.extend(matches)

        # Sort by position in text
        all_matches.sort(key=lambda x: x['start'])

        return all_matches

    def scan_dict(self, data: Dict, min_confidence: float = 0.5) -> Dict:
        """
        Recursively scan dictionary for PII.

        Args:
            data: Dictionary to scan
            min_confidence: Minimum confidence threshold

        Returns:
            Dict mapping keys to detected PII
        """
        results = {}

        for key, value in data.items():
            if isinstance(value, str):
                matches = self.detect(value, min_confidence)
                if matches:
                    results[key] = matches
            elif isinstance(value, dict):
                nested_results = self.scan_dict(value, min_confidence)
                if nested_results:
                    results[key] = nested_results
            elif isinstance(value, list):
                list_results = []
                for idx, item in enumerate(value):
                    if isinstance(item, str):
                        matches = self.detect(item, min_confidence)
                        if matches:
                            list_results.append({'index': idx, 'matches': matches})
                    elif isinstance(item, dict):
                        nested = self.scan_dict(item, min_confidence)
                        if nested:
                            list_results.append({'index': idx, 'matches': nested})
                if list_results:
                    results[key] = list_results

        return results

    def get_stats(self) -> Dict:
        """Get statistics about loaded detection rules."""
        return {
            'total_rules': len(self.rules),
            'region': self.region,
            'pii_types': list(set(rule.pii_type.value for rule in self.rules)),
            'avg_confidence': sum(r.confidence for r in self.rules) / len(self.rules)
        }
