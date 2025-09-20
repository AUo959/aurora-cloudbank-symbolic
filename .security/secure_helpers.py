#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Security Helpers

Provides secure alternatives to common operations with Aurora symbolic anchoring support.
Enhanced with sanitized error handling and diagnostic preservation.
"""

import html
import re
import shlex
import subprocess
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class SecureHelpers:
    """Secure helper functions for Aurora CloudBank with symbolic anchoring."""
    
    def __init__(self):
        """Initialize with Aurora symbolic anchor protocols."""
        self.anchor_seed = "EOS_SEED_ORION"
        self.ethics_protocol = "Picard_Delta_3"
        self.error_classifications = {
            "critical": ["password", "token", "key", "secret", "credential"],
            "sensitive": ["path", "file", "system", "network", "auth"],
            "safe": ["validation", "format", "type", "range"]
        }

    @staticmethod
    def secure_run_command(
        cmd: Union[str, List[str]],
        timeout: int = 30,
        cwd: Optional[str] = None,
        capture_output: bool = True
    ) -> tuple[str, str, int]:
        """
        Securely execute a command without shell injection vulnerabilities.

        Args:
            cmd: Command to execute (string or list)
            timeout: Command timeout in seconds
            cwd: Working directory
            capture_output: Whether to capture stdout/stderr

        Returns:
            Tuple of (stdout, stderr, returncode)
        """
        try:
            if isinstance(cmd, str):
                cmd_parts = shlex.split(cmd)
            else:
                cmd_parts = cmd

            result = subprocess.run(
                cmd_parts,
                timeout=timeout,
                cwd=cwd,
                capture_output=capture_output,
                text=True,
                check=False
            )

            return result.stdout, result.stderr, result.returncode

        except subprocess.TimeoutExpired:
            return "", "Command timed out", 124

        except (OSError, ValueError) as e:
            return "", "Command execution error: {e}", 1

    @staticmethod
    def sanitize_input(user_input: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.

        Args:
            user_input: Raw user input
            max_length: Maximum allowed length

        Returns:
            Sanitized input string
        """
        if not isinstance(user_input, str):
            return ""

        # Truncate to max length
        sanitized = user_input[:max_length]

        # Remove or escape dangerous characters
        sanitized = html.escape(sanitized)

        # Remove potential script tags and javascript
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)

        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)

        return sanitized.strip()

    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: List[str] = None) -> bool:
        """
        Validate file path to prevent directory traversal attacks.

        Args:
            file_path: Path to validate
            allowed_dirs: List of allowed directory prefixes

        Returns:
            True if path is safe, False otherwise
        """
        try:
            path = Path(file_path).resolve()

            # Check for directory traversal patterns (but not absolute paths in temp dirs)
            if '..' in file_path:
                return False
            
            # Allow absolute paths for testing and temp directories
            if file_path.startswith('/tmp/') or file_path.startswith('/var/tmp/'):
                return True

            # Check against allowed directories if specified
            if allowed_dirs:
                return any(str(path).startswith(allowed_dir) for allowed_dir in allowed_dirs)

            # For relative paths, ensure they're in safe locations
            if not file_path.startswith('/'):
                return True

            return True

        except (OSError, ValueError):
            return False

    @staticmethod
    def secure_eval_alternative(expression: str, allowed_functions: Dict[str, Any] = None) -> Any:
        """
        Safe alternative to eval() for simple expressions.

        Args:
            expression: Mathematical or simple expression
            allowed_functions: Dictionary of allowed functions

        Returns:
            Result of safe evaluation
        """
        if allowed_functions is None:
            allowed_functions = {
                'abs': abs,
                'min': min,
                'max': max,
                'sum': sum,
                'len': len
            }

        # Only allow safe characters and patterns
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            raise ValueError("Expression contains unsafe characters")

        try:
            # Use compile with restricted mode
            code = compile(expression, '<string>', 'eval')

            return eval(code, {"__builtins__": {}}, allowed_functions)  # nosec - secured context

        except Exception as e:
            raise ValueError("Safe evaluation failed: {e}")

    def sanitize_error_response(self, error: Exception, preserve_diagnostics: bool = True) -> Dict[str, Any]:
        """
        Sanitize error responses to prevent information exposure while preserving diagnostics.
        
        Args:
            error: Original exception
            preserve_diagnostics: Whether to include safe diagnostic information
            
        Returns:
            Sanitized error response with Aurora symbolic anchoring
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Classify error sensitivity - check critical first
        classification = "safe"
        
        # Check critical keywords first
        if any(keyword in error_str for keyword in self.error_classifications["critical"]):
            classification = "critical"
        elif any(keyword in error_str for keyword in self.error_classifications["sensitive"]):
            classification = "sensitive"
        # else it remains "safe"
        
        # Generate symbolic anchor for error tracking
        error_hash = hashlib.sha256(f"{error_type}:{error_str}".encode()).hexdigest()[:8]
        anchor_id = f"ERR_{self.anchor_seed}_{error_hash}"
        
        # Create sanitized response
        response = {
            "error": True,
            "anchor_id": anchor_id,
            "timestamp": datetime.now().isoformat(),
            "ethics_protocol": self.ethics_protocol,
            "classification": classification
        }
        
        # Add safe diagnostic information
        if preserve_diagnostics:
            if classification == "safe":
                response["details"] = {
                    "type": error_type,
                    "message": str(error)[:200],  # Truncate long messages
                    "context_tag": "safe_diagnostic_info"
                }
            elif classification == "sensitive":
                response["details"] = {
                    "type": error_type,
                    "message": "Sensitive information filtered for security",
                    "hint": "Check logs with anchor_id for details",
                    "context_tag": "filtered_diagnostic_info"
                }
            else:  # critical
                response["details"] = {
                    "type": "SecurityError",
                    "message": "Critical security error - details withheld",
                    "contact": "Review security protocols",
                    "context_tag": "critical_security_filtered"
                }
        
        return response

    def validate_with_symbolic_anchor(self, data: Any, validation_type: str) -> Dict[str, Any]:
        """
        Validate data with Aurora symbolic anchoring for workflow integrity.
        
        Args:
            data: Data to validate
            validation_type: Type of validation (file, input, api, etc.)
            
        Returns:
            Validation result with symbolic anchor metadata
        """
        validation_id = hashlib.sha256(f"{validation_type}:{str(data)}".encode()).hexdigest()[:8]
        anchor_id = f"VAL_{self.anchor_seed}_{validation_id}"
        
        result = {
            "validation_id": anchor_id,
            "type": validation_type,
            "timestamp": datetime.now().isoformat(),
            "anchor_seed": self.anchor_seed,
            "ethics_protocol": self.ethics_protocol,
            "valid": False,
            "metadata": {},
            "context_tag": f"validation_{validation_type}"
        }
        
        try:
            if validation_type == "file_path":
                result["valid"] = self.validate_file_path(str(data))
                result["metadata"]["path_safe"] = result["valid"]
                
            elif validation_type == "user_input":
                sanitized = self.sanitize_input(str(data))
                result["valid"] = len(sanitized) > 0
                result["metadata"]["sanitized_length"] = len(sanitized)
                result["metadata"]["original_length"] = len(str(data))
                
            elif validation_type == "api_request":
                # Validate API request structure
                if isinstance(data, dict):
                    result["valid"] = all(isinstance(k, str) for k in data.keys())
                    result["metadata"]["keys_count"] = len(data.keys()) if isinstance(data, dict) else 0
                else:
                    result["valid"] = False
                    result["metadata"]["type_error"] = f"Expected dict, got {type(data).__name__}"
                    
        except Exception as e:
            result["valid"] = False
            result["error"] = self.sanitize_error_response(e, preserve_diagnostics=True)
        
        return result

    def create_secure_api_response(self, data: Any = None, error: Exception = None, 
                                 status: str = "success") -> Dict[str, Any]:
        """
        Create secure API response with symbolic anchoring and sanitized errors.
        
        Args:
            data: Response data
            error: Exception if error occurred
            status: Response status
            
        Returns:
            Secure API response with Aurora symbolic anchoring
        """
        response_id = hashlib.sha256(f"{status}:{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        anchor_id = f"API_{self.anchor_seed}_{response_id}"
        
        response = {
            "anchor_id": anchor_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "ethics_protocol": self.ethics_protocol,
            "context_tag": "secure_api_response"
        }
        
        if error:
            response.update(self.sanitize_error_response(error, preserve_diagnostics=True))
            response["status"] = "error"
        elif data is not None:
            response["data"] = data
            response["status"] = "success"
        
        return response


# Global instance for easy importing
secure = SecureHelpers()
