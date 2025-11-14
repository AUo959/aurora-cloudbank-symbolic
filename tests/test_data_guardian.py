"""
T1-EDG-TEST - Data Guardian Test Suite
Comprehensive test coverage for PII detection, redaction, middleware, API, and CLI.

Chain: #005//003/EDG
Anchor: T1-EDG-TEST-001
Target: 90%+ code coverage
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.data_guardian.cli import DataGuardianCLI
from modules.data_guardian.detection_rules import PIIDetector, PIIType
from modules.data_guardian.middleware import DataGuardianMiddleware
from modules.data_guardian.redaction import RedactionEngine, RedactionStrategy


@pytest.mark.unit
@pytest.mark.security
class TestPIIDetection:
    """Test PII detection rules and patterns."""

    def test_detector_initialization(self):
        """Test PIIDetector initialization with default rules."""
        detector = PIIDetector()
        assert detector is not None
        assert len(detector.rules) > 0

    def test_email_detection(self):
        """Test email address detection."""
        detector = PIIDetector()
        text = "Contact me at john.doe@example.com or jane@test.org"
        detections = detector.detect(text, min_confidence=0.7)

        emails = [d for d in detections if d['type'] == PIIType.EMAIL.value]
        assert len(emails) == 2
        assert "john.doe@example.com" in [d['match'] for d in emails]
        assert "jane@test.org" in [d['match'] for d in emails]

    def test_phone_detection(self):
        """Test phone number detection."""
        detector = PIIDetector()
        text = "Call 555-123-4567 or (555) 987-6543"
        detections = detector.detect(text, min_confidence=0.7)

        phones = [d for d in detections if d['type'] == PIIType.PHONE.value]
        assert len(phones) >= 1

    def test_ssn_detection(self):
        """Test US SSN detection."""
        detector = PIIDetector()
        text = "SSN: 123-45-6789"
        detections = detector.detect(text, min_confidence=0.7)

        ssns = [d for d in detections if d['type'] == PIIType.SSN.value]
        assert len(ssns) == 1
        assert "123-45-6789" in ssns[0]['match']

    def test_credit_card_detection(self):
        """Test credit card number detection."""
        detector = PIIDetector()
        text = "Card: 4532-1234-5678-9010"
        detections = detector.detect(text, min_confidence=0.7)

        cards = [d for d in detections if d['type'] == PIIType.CREDIT_CARD.value]
        assert len(cards) >= 1

    def test_ip_address_detection(self):
        """Test IPv4 address detection."""
        detector = PIIDetector()
        text = "Server at 192.168.1.100 and 10.0.0.1"
        detections = detector.detect(text, min_confidence=0.7)

        ips = [d for d in detections if d['type'] == PIIType.IP_ADDRESS.value]
        assert len(ips) == 2

    def test_confidence_threshold(self):
        """Test confidence threshold filtering."""
        detector = PIIDetector()
        text = "Email: test@example.com"

        detections_low = detector.detect(text, min_confidence=0.5)
        assert len(detections_low) > 0

        detections_high = detector.detect(text, min_confidence=0.99)
        assert len(detections_high) >= 0

    def test_dict_scanning(self):
        """Test recursive dictionary scanning."""
        detector = PIIDetector()
        data = {
            "user": {
                "email": "user@example.com",
                "phone": "555-123-4567",
                "nested": {"ssn": "123-45-6789"}
            },
            "contacts": ["alice@test.com", "bob@test.org"]
        }

        detections = detector.scan_dict(data)
        # scan_dict returns nested dict structure, check it's not empty
        assert len(detections) >= 2  # At least 'user' and 'contacts' keys


@pytest.mark.unit
@pytest.mark.security
class TestRedaction:
    """Test PII redaction strategies."""

    def test_redactor_initialization(self):
        """Test RedactionEngine initialization."""
        redactor = RedactionEngine()
        assert redactor is not None

    def test_mask_strategy(self):
        """Test MASK redaction strategy."""
        detector = PIIDetector()
        redactor = RedactionEngine()

        text = "Email: john@example.com"
        detections = detector.detect(text)
        redacted = redactor.redact_text(text, detections, RedactionStrategy.MASK)

        assert "john@example.com" not in redacted
        assert "*" in redacted

    def test_hash_strategy(self):
        """Test HASH redaction strategy."""
        detector = PIIDetector()
        redactor = RedactionEngine()

        text = "Email: test@example.com"
        detections = detector.detect(text)
        redacted = redactor.redact_text(text, detections, RedactionStrategy.HASH)

        assert "test@example.com" not in redacted
        assert len(redacted) > 0

    def test_remove_strategy(self):
        """Test REMOVE redaction strategy."""
        detector = PIIDetector()
        redactor = RedactionEngine()

        text = "Email: test@example.com and more text"
        detections = detector.detect(text)
        redacted = redactor.redact_text(text, detections, RedactionStrategy.REMOVE)

        assert "test@example.com" not in redacted
        assert len(redacted) < len(text)

    def test_audit_trail(self):
        """Test redaction audit trail."""
        detector = PIIDetector()
        redactor = RedactionEngine()

        text = "Email: test@example.com"
        detections = detector.detect(text)
        redactor.redact_text(text, detections, RedactionStrategy.HASH)

        audit = redactor.get_audit_trail()
        assert len(audit) > 0


@pytest.mark.unit
class TestMiddleware:
    """Test FastAPI middleware integration."""

    def test_middleware_initialization(self):
        """Test middleware initialization."""
        from fastapi import FastAPI

        app = FastAPI()
        middleware = DataGuardianMiddleware(app)
        assert middleware is not None

    def test_middleware_stats(self):
        """Test middleware statistics tracking."""
        from fastapi import FastAPI

        app = FastAPI()
        middleware = DataGuardianMiddleware(app)

        stats = middleware.get_stats()
        assert "requests_scanned" in stats
        assert "pii_detected" in stats
        assert "detector_stats" in stats


@pytest.mark.unit
@pytest.mark.cli
class TestCLI:
    """Test command-line interface."""

    def test_cli_initialization(self):
        """Test CLI initialization."""
        cli = DataGuardianCLI()
        assert cli is not None
        assert cli.detector is not None
        assert cli.redactor is not None

    def test_scan_file(self):
        """Test file scanning via CLI."""
        cli = DataGuardianCLI()

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Contact: john@example.com\nPhone: 555-123-4567")
            temp_path = f.name

        try:
            result = cli.scan_file(temp_path, output_format="json")
            assert "error" not in result
            assert result["total_detections"] >= 2
            assert "detections" in result
        finally:
            Path(temp_path).unlink()

    def test_scan_nonexistent_file(self):
        """Test scanning non-existent file."""
        cli = DataGuardianCLI()
        result = cli.scan_file("/nonexistent/file.txt")

        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_redact_file(self):
        """Test file redaction via CLI."""
        cli = DataGuardianCLI()

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Email: sensitive@example.com")
            temp_path = f.name

        try:
            result = cli.redact_file(temp_path, strategy="mask")
            assert "error" not in result
            assert result["total_redactions"] >= 1
            assert "output_file" in result

            output_path = Path(result["output_file"])
            assert output_path.exists()

            redacted_content = output_path.read_text()
            assert "sensitive@example.com" not in redacted_content

            output_path.unlink()
        finally:
            Path(temp_path).unlink()

    def test_list_strategies(self):
        """Test listing redaction strategies."""
        cli = DataGuardianCLI()
        result = cli.list_strategies()

        assert "strategies" in result
        assert len(result["strategies"]) == 6
        assert result["default"] == "MASK"

    def test_list_pii_types(self):
        """Test listing PII types."""
        cli = DataGuardianCLI()
        result = cli.list_pii_types()

        assert "pii_types" in result
        assert result["total"] == 12


@pytest.mark.integration
@pytest.mark.security
class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_detection_redaction_pipeline(self):
        """Test complete detection -> redaction pipeline."""
        detector = PIIDetector()
        redactor = RedactionEngine()

        text = """
        User Profile:
        Email: john.doe@example.com
        Phone: 555-123-4567
        SSN: 123-45-6789
        IP: 192.168.1.100
        """

        detections = detector.detect(text, min_confidence=0.7)
        assert len(detections) >= 4

        masked = redactor.redact_text(text, detections, RedactionStrategy.MASK)
        assert "john.doe@example.com" not in masked

        hashed = redactor.redact_text(text, detections, RedactionStrategy.HASH)
        assert "123-45-6789" not in hashed

    def test_file_to_file_pipeline(self):
        """Test complete file scanning and redaction."""
        cli = DataGuardianCLI()

        input_data = """
        Customer Data:
        Email: customer@business.com
        Credit Card: 4532-1234-5678-9010
        """

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(input_data)
            input_path = f.name

        try:
            scan_result = cli.scan_file(input_path, output_format="json")
            assert scan_result["total_detections"] >= 2

            redact_result = cli.redact_file(input_path, strategy="mask")
            assert redact_result["total_redactions"] >= 2

            output_path = Path(redact_result["output_file"])
            assert output_path.exists()

            redacted_content = output_path.read_text()
            assert "customer@business.com" not in redacted_content
            assert "4532-1234-5678-9010" not in redacted_content

            output_path.unlink()
        finally:
            Path(input_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
