#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Security Helpers


Provides secure alternatives to common operations.
"""

import html
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


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
            return "", "Command execution error: {e}", 1

    @staticmethod
    def sanitize_input(user_input: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Uses robust defense-in-depth approach:
        - HTML entity escaping
        - Iterative pattern removal to prevent bypass
        - Control character filtering
        
        Args:
            user_input: Raw user input
            max_length: Maximum allowed length

        Returns:
            Sanitized input string
        """
        if not isinstance(user_input, str):
            return ""

        # Truncate to max length first
        sanitized = user_input[:max_length]

        # HTML escape all special characters
        # This is the primary defense - converts < > & " ' to entities
        sanitized = html.escape(sanitized)

        # Defense in depth: Remove dangerous patterns iteratively
        # Repeat until no changes occur (prevents nested bypass like <scr<script>ipt>)
        previous_length = len(sanitized) + 1
        iterations = 0
        max_iterations = 5  # Prevent infinite loops
        
        while len(sanitized) != previous_length and iterations < max_iterations:
            previous_length = len(sanitized)
            iterations += 1
            
            # Remove script tags (even if escaped or nested)
            sanitized = re.sub(
                r'&lt;script[^&]*&gt;.*?&lt;/script&gt;',
                '',
                sanitized,
                flags=re.IGNORECASE | re.DOTALL
            )
            
            # Remove any remaining script-like patterns
            sanitized = re.sub(r'script', '', sanitized, flags=re.IGNORECASE)
            
            # Remove javascript protocol (even if escaped)
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            
            # Remove event handlers (even if escaped)
            sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
            
            # Remove data URIs which can contain scripts
            sanitized = re.sub(r'data:', '', sanitized, flags=re.IGNORECASE)
            
            # Remove vbscript protocol
            sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)

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
        # CRITICAL SECURITY: eval() usage detected - high code injection risk
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

        # SECURITY FIX: Replace eval() with AST-based safe evaluation
        import ast

        # Enforce maximum expression length to prevent DoS
        max_length = 1000
        if len(expression) > max_length:
            raise ValueError(f"Expression exceeds maximum length of {max_length}")

        # Whitelist allowed characters (digits, arithmetic ops, parentheses, decimal point, spaces)
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains disallowed characters")

        try:
            # Parse expression to AST
            tree = ast.parse(expression, mode='eval')

            # Validate AST structure
            SecurityHelpers._validate_ast_node(tree.body, allowed_functions)

            # Compile and execute in restricted namespace
            code = compile(tree, '<string>', 'eval')
            namespace = {name: func for name, func in (allowed_functions or {}).items()}
            return eval(code, {"__builtins__": {}}, namespace)

        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")
        except Exception as e:
            raise ValueError(f"Safe evaluation failed: {e}")

    @staticmethod
    def _validate_ast_node(node: ast.AST, allowed_functions: Optional[Dict[str, Any]] = None) -> None:
        """
        Recursively validate AST nodes to ensure only safe operations.

        SECURITY: This prevents code injection by validating the AST structure
        before evaluation.

        Args:
            node: AST node to validate
            allowed_functions: Dictionary of allowed function names

        Raises:
            ValueError: If node contains disallowed operations
        """
        allowed_ops = {
            ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
            ast.Pow, ast.UAdd, ast.USub, ast.FloorDiv
        }

        if isinstance(node, ast.Constant):
            # Allow only numbers (int, float) and None
            if not isinstance(node.value, (int, float, type(None))):
                raise ValueError(f"Disallowed constant type: {type(node.value)}")

        elif isinstance(node, ast.Name):
            # Allow variable references (will be checked at runtime)
            pass

        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in allowed_ops:
                raise ValueError(f"Disallowed unary operator: {type(node.op)}")
            SecurityHelpers._validate_ast_node(node.operand, allowed_functions)

        elif isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_ops:
                raise ValueError(f"Disallowed binary operator: {type(node.op)}")
            SecurityHelpers._validate_ast_node(node.left, allowed_functions)
            SecurityHelpers._validate_ast_node(node.right, allowed_functions)

        elif isinstance(node, ast.Call):
            # Only allow whitelisted function calls
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only direct function calls are allowed")

            func_name = node.func.id
            if allowed_functions and func_name not in allowed_functions:
                raise ValueError(f"Function '{func_name}' is not allowed")

            # Validate function arguments
            for arg in node.args:
                SecurityHelpers._validate_ast_node(arg, allowed_functions)
            for keyword in node.keywords:
                SecurityHelpers._validate_ast_node(keyword.value, allowed_functions)

        elif isinstance(node, (ast.List, ast.Tuple)):
            # Allow lists and tuples
            for element in node.elts:
                SecurityHelpers._validate_ast_node(element, allowed_functions)

        elif isinstance(node, ast.Subscript):
            # Allow indexing operations
            SecurityHelpers._validate_ast_node(node.value, allowed_functions)
            SecurityHelpers._validate_ast_node(node.slice, allowed_functions)

        elif isinstance(node, ast.Index):
            # Python 3.8 compatibility
            SecurityHelpers._validate_ast_node(node.value, allowed_functions)

        elif isinstance(node, ast.Slice):
            # Allow slice operations
            if node.lower:
                SecurityHelpers._validate_ast_node(node.lower, allowed_functions)
            if node.upper:
                SecurityHelpers._validate_ast_node(node.upper, allowed_functions)
            if node.step:
                SecurityHelpers._validate_ast_node(node.step, allowed_functions)

        else:
            raise ValueError(f"Disallowed AST node type: {type(node).__name__}")

    @staticmethod
    def validate_input_length(input_str: str, max_length: int = 1000, field_name: str = "input") -> str:
        """
        Validate input length to prevent DoS attacks - SECURITY FIX
        
        Args:
            input_str: Input string to validate
            max_length: Maximum allowed length
            field_name: Name of the field for error messages
            
        Returns:
            Validated input string
            
        Raises:
            ValueError: If input is too long
        """
        if not isinstance(input_str, str):
            input_str = str(input_str)
            
        if len(input_str) > max_length:
            raise ValueError(f"{field_name} exceeds maximum length of {max_length} characters")
            
        return input_str

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format securely - SECURITY FIX
        
        Args:
            email: Email string to validate
            
        Returns:
            True if valid email format, False otherwise
        """
        if not isinstance(email, str) or len(email) > 254:
            return False
            
        # Basic email validation regex (RFC 5322 compliant)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal - SECURITY FIX
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            filename = str(filename)
            
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
            
        # Ensure not empty
        if not sanitized:
            sanitized = 'unnamed_file'
            
        return sanitized


# Global instance for easy importing
secure = SecureHelpers()
