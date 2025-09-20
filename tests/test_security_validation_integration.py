#!/usr/bin/env python3
"""
🧪 Test Suite for Security and Validation Integration

Tests security enhancements and symbolic validation system integration.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add paths for testing
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(project_root, '.security'))
sys.path.insert(0, os.path.join(project_root, 'src', 'core'))

from secure_helpers import secure
from symbolic_validation import symbolic_validator


class TestSecurityAndValidationIntegration(unittest.TestCase):
    """Test security and validation integration with Aurora symbolic anchoring."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_files = {}
    
    def tearDown(self):
        """Clean up test environment."""
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(self.test_dir)
    
    def create_test_file(self, name: str, content: str, extension: str = '.py') -> str:
        """Create a test file with given content."""
        file_path = os.path.join(self.test_dir, f"{name}{extension}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.test_files[name] = file_path
        return file_path
    
    def test_secure_error_sanitization_safe(self):
        """Test error sanitization for safe errors."""
        error = ValueError("Invalid input format")
        response = secure.sanitize_error_response(error, preserve_diagnostics=True)
        
        self.assertTrue(response["error"])
        self.assertEqual(response["classification"], "safe")
        self.assertIn("anchor_id", response)
        self.assertIn("EOS_SEED_ORION", response["anchor_id"])
        self.assertEqual(response["ethics_protocol"], "Picard_Delta_3")
        self.assertIn("details", response)
        self.assertEqual(response["details"]["type"], "ValueError")
        self.assertIn("context_tag", response["details"])
    
    def test_secure_error_sanitization_sensitive(self):
        """Test error sanitization for sensitive errors."""
        error = OSError("File path /sensitive/system/file not accessible")
        response = secure.sanitize_error_response(error, preserve_diagnostics=True)
        
        self.assertTrue(response["error"])
        self.assertEqual(response["classification"], "sensitive")
        self.assertIn("anchor_id", response)
        self.assertIn("details", response)
        self.assertEqual(response["details"]["message"], "Sensitive information filtered for security")
        self.assertIn("hint", response["details"])
    
    def test_secure_error_sanitization_critical(self):
        """Test error sanitization for critical security errors."""
        error = Exception("Authentication failed: invalid password for user")
        response = secure.sanitize_error_response(error, preserve_diagnostics=True)
        
        self.assertTrue(response["error"])
        self.assertEqual(response["classification"], "critical")
        self.assertIn("anchor_id", response)
        self.assertIn("details", response)
        self.assertEqual(response["details"]["type"], "SecurityError")
        self.assertEqual(response["details"]["message"], "Critical security error - details withheld")
    
    def test_symbolic_anchor_validation_user_input(self):
        """Test symbolic anchor validation for user input."""
        test_input = "Hello Aurora CloudBank"
        validation = secure.validate_with_symbolic_anchor(test_input, "user_input")
        
        self.assertIn("validation_id", validation)
        self.assertIn("VAL_EOS_SEED_ORION", validation["validation_id"])
        self.assertEqual(validation["type"], "user_input")
        self.assertEqual(validation["anchor_seed"], "EOS_SEED_ORION")
        self.assertEqual(validation["ethics_protocol"], "Picard_Delta_3")
        self.assertTrue(validation["valid"])
        self.assertIn("metadata", validation)
        self.assertIn("sanitized_length", validation["metadata"])
        self.assertEqual(validation["context_tag"], "validation_user_input")
    
    def test_symbolic_anchor_validation_api_request(self):
        """Test symbolic anchor validation for API requests."""
        test_request = {"tool_name": "geometric_algebra", "parameters": {"x": 1, "y": 2}}
        validation = secure.validate_with_symbolic_anchor(test_request, "api_request")
        
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["metadata"]["keys_count"], 2)
        self.assertEqual(validation["context_tag"], "validation_api_request")
    
    def test_secure_api_response_success(self):
        """Test secure API response creation for success case."""
        test_data = {"result": "success", "value": 42}
        response = secure.create_secure_api_response(data=test_data)
        
        self.assertIn("anchor_id", response)
        self.assertIn("API_EOS_SEED_ORION", response["anchor_id"])
        self.assertEqual(response["status"], "success")
        self.assertEqual(response["ethics_protocol"], "Picard_Delta_3")
        self.assertEqual(response["data"], test_data)
        self.assertEqual(response["context_tag"], "secure_api_response")
    
    def test_secure_api_response_error(self):
        """Test secure API response creation for error case."""
        error = ValueError("Test validation error")
        response = secure.create_secure_api_response(error=error)
        
        self.assertIn("anchor_id", response)
        self.assertEqual(response["status"], "error")
        self.assertTrue(response["error"])
        self.assertEqual(response["classification"], "safe")
    
    def test_symbolic_file_validation_python_valid(self):
        """Test symbolic file validation for valid Python file."""
        python_content = '''#!/usr/bin/env python3
"""
Aurora CloudBank test module with symbolic anchoring.
"""

# Aurora Symbolic Anchoring
ANCHOR_SEED = "EOS_SEED_ORION"
ETHICS_PROTOCOL = "Picard_Delta_3"

def test_function():
    """Test function with Aurora patterns."""
    return {"anchor": ANCHOR_SEED, "ethics": ETHICS_PROTOCOL}

if __name__ == "__main__":
    print("Aurora CloudBank symbolic test")
'''
        file_path = self.create_test_file("test_aurora", python_content, '.py')
        validation = symbolic_validator.validate_file_with_anchoring(file_path)
        
        self.assertTrue(validation["valid"])
        self.assertIn("validation_id", validation)
        self.assertIn("VAL_EOS_SEED_ORION", validation["validation_id"])
        self.assertEqual(validation["anchor_seed"], "EOS_SEED_ORION")
        self.assertEqual(validation["ethics_protocol"], "Picard_Delta_3")
        self.assertIn("t1_state", validation)
        self.assertIn("srb_resolution", validation)
        self.assertIn("chain_id", validation)
        self.assertEqual(validation["context_tag"], "symbolic_file_validation")
        
        # Check for Aurora-specific validations
        checks = {check["check"]: check for check in validation["checks"]}
        self.assertIn("python_syntax", checks)
        self.assertTrue(checks["python_syntax"]["result"])
        
        if "aurora_anchor_seed" in checks:
            self.assertTrue(checks["aurora_anchor_seed"]["result"])
        
        if "aurora_ethics_protocol" in checks:
            self.assertTrue(checks["aurora_ethics_protocol"]["result"])
    
    def test_symbolic_file_validation_python_syntax_error(self):
        """Test symbolic file validation for Python file with syntax error."""
        python_content = '''#!/usr/bin/env python3
"""
Invalid Python syntax test.
"""

def broken_function(
    # Missing closing parenthesis and colon
    return "broken"
'''
        file_path = self.create_test_file("test_broken", python_content, '.py')
        validation = symbolic_validator.validate_file_with_anchoring(file_path)
        
        self.assertFalse(validation["valid"])
        self.assertEqual(validation["workflow_impact"], "blocking")
        
        errors = {error["type"]: error for error in validation["errors"]}
        self.assertIn("syntax_error", errors)
        self.assertEqual(errors["syntax_error"]["severity"], "high")
        self.assertEqual(errors["syntax_error"]["workflow_impact"], "blocking")
    
    def test_symbolic_file_validation_json_valid(self):
        """Test symbolic file validation for valid JSON file."""
        json_content = json.dumps({
            "anchor_seed": "EOS_SEED_ORION",
            "ethics_protocol": "Picard_Delta_3",
            "system": "aurora-cloudbank-symbolic",
            "data": {"test": True}
        }, indent=2)
        
        file_path = self.create_test_file("test_config", json_content, '.json')
        validation = symbolic_validator.validate_file_with_anchoring(file_path)
        
        self.assertTrue(validation["valid"])
        
        checks = {check["check"]: check for check in validation["checks"]}
        self.assertIn("json_syntax", checks)
        self.assertTrue(checks["json_syntax"]["result"])
        
        if "aurora_anchor_seed" in checks:
            self.assertTrue(checks["aurora_anchor_seed"]["result"])
    
    def test_symbolic_file_validation_json_invalid(self):
        """Test symbolic file validation for invalid JSON file."""
        json_content = '{"incomplete": "json", "missing": }'
        
        file_path = self.create_test_file("test_broken_json", json_content, '.json')
        validation = symbolic_validator.validate_file_with_anchoring(file_path)
        
        self.assertFalse(validation["valid"])
        self.assertEqual(validation["workflow_impact"], "blocking")
        
        errors = {error["type"]: error for error in validation["errors"]}
        self.assertIn("json_syntax_error", errors)
        self.assertEqual(errors["json_syntax_error"]["severity"], "high")
    
    def test_symbolic_file_validation_security_warnings(self):
        """Test symbolic file validation for files with security warnings."""
        python_content = '''#!/usr/bin/env python3
"""
Python file with security patterns.
"""
import subprocess
import os

def risky_function(user_input):
    """Function with potentially dangerous patterns."""
    # This would trigger security warnings
    result = eval(user_input)  # Dangerous pattern
    subprocess.call(["echo", result])  # Another security pattern
    return result
'''
        file_path = self.create_test_file("test_security", python_content, '.py')
        validation = symbolic_validator.validate_file_with_anchoring(file_path)
        
        # Should be valid but with security warnings
        self.assertTrue(validation["valid"])
        self.assertEqual(validation["workflow_impact"], "security")
        
        security_warnings = [w for w in validation["warnings"] if w["type"] == "security_pattern"]
        self.assertGreater(len(security_warnings), 0)
        
        # Check for specific dangerous patterns
        warning_messages = [w["message"] for w in security_warnings]
        eval_warning = any("eval(" in msg for msg in warning_messages)
        subprocess_warning = any("subprocess.call" in msg for msg in warning_messages)
        self.assertTrue(eval_warning or subprocess_warning)
    
    def test_symbolic_file_validation_nonexistent(self):
        """Test symbolic file validation for nonexistent file."""
        fake_path = "/fake/nonexistent/file.py"
        validation = symbolic_validator.validate_file_with_anchoring(fake_path)
        
        self.assertFalse(validation["valid"])
        self.assertEqual(validation["workflow_impact"], "blocking")
        
        errors = {error["type"]: error for error in validation["errors"]}
        self.assertIn("file_not_found", errors)
        self.assertEqual(errors["file_not_found"]["severity"], "high")
    
    def test_validation_manifest_export(self):
        """Test validation manifest export with symbolic anchoring."""
        # Run some validations first
        python_content = 'print("Hello Aurora")'
        file_path = self.create_test_file("test_manifest", python_content, '.py')
        symbolic_validator.validate_file_with_anchoring(file_path)
        
        manifest = symbolic_validator.export_validation_manifest()
        
        self.assertEqual(manifest["system"], "aurora-cloudbank-symbolic-validation")
        self.assertEqual(manifest["anchor_seed"], "EOS_SEED_ORION")
        self.assertEqual(manifest["ethics_protocol"], "Picard_Delta_3")
        self.assertIn("t1_anchor", manifest)
        self.assertIn("srb_anchor", manifest)
        self.assertEqual(manifest["t1_anchor"]["type"], "T1")
        self.assertEqual(manifest["srb_anchor"]["type"], "SRB")
        self.assertIn("validation_chains", manifest)
        self.assertIn("timestamp", manifest)
        self.assertEqual(manifest["context_tag"], "symbolic_validation_manifest")


def run_tests():
    """Run the test suite."""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests()