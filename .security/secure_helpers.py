#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Security Helpers


Provides secure alternatives to common operations.
"""

import shlex


import subprocess


import re


import html


from typing import List, Dict, Any, Optional, Union


from pathlib import Path


class SecureHelpers:
    """Secure helper functions for Aurora CloudBank."""

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
            return "", f"Command execution error: {e}", 1

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
            return "r"

        # Truncate to max length
        sanitized = user_input[:max_length]

        # Remove or escape dangerous characters
        sanitized = html.escape(sanitized)

        # Remove potential script tags and javascript
        sanitized = (


            re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        )


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

            # Check for directory traversal
            if '..' in file_path or file_path.startswith('/'):
                return False

            # Check against allowed directories if specified
            if allowed_dirs:
                return any(str(path).startswith(allowed_dir) for allowed_dir in allowed_dirs)


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
            raise ValueError(f"Safe evaluation failed: {e}")

# Global instance for easy importing
secure = SecureHelpers()
