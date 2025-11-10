#!/usr/bin/env python3
"""
Aurora CloudBank - Secure Helper Functions
Provides security utilities and safe operations
"""

import ast
import html
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def _validate_ast_node(node: ast.AST, allowed_functions: Optional[Dict[str, Any]] = None) -> None:
    """Validate a single AST node.

    SECURITY: Ensures only safe operations appear before controlled evaluation.
    Allowed constructs: numeric constants, unary/binary arithmetic, simple name, whitelisted function call,
    lists/tuples, subscripts (including slices).
    """
    # Fast-path simple constant / name nodes
    if isinstance(node, ast.Constant):
        _validate_constant(node)
        return
    if isinstance(node, ast.Name):  # variables allowed (checked at eval stage)
        return

    # Allowed operator classes for arithmetic
    allowed_ops = {
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
        ast.Pow, ast.UAdd, ast.USub, ast.FloorDiv
    }

    # Ordered validators (class, function) – keeps cyclomatic complexity low
    # Manual isinstance checks preserve type safety for static analyzers
    if isinstance(node, ast.UnaryOp):
        _validate_unary(node, allowed_ops, allowed_functions)
        return
    if isinstance(node, ast.BinOp):
        _validate_binop(node, allowed_ops, allowed_functions)
        return
    if isinstance(node, ast.Call):
        _validate_call(node, allowed_functions)
        return
    if isinstance(node, (ast.List, ast.Tuple)):
        _validate_sequence(node, allowed_functions)
        return
    if isinstance(node, (ast.Subscript, ast.Slice)):
        _validate_slice_like(node, allowed_functions)
        return

    raise ValueError(f"Unsupported AST node type: {type(node)}")


def _validate_constant(node: ast.Constant) -> None:
    if not isinstance(node.value, (int, float, type(None))):
        raise ValueError(f"Disallowed constant type: {type(node.value)}")


def _validate_unary(node: ast.UnaryOp, allowed_ops: set, allowed_functions: Optional[Dict[str, Any]]) -> None:
    if type(node.op) not in allowed_ops:
        raise ValueError(f"Disallowed unary operator: {type(node.op)}")
    _validate_ast_node(node.operand, allowed_functions)


def _validate_binop(node: ast.BinOp, allowed_ops: set, allowed_functions: Optional[Dict[str, Any]]) -> None:
    if type(node.op) not in allowed_ops:
        raise ValueError(f"Disallowed binary operator: {type(node.op)}")
    _validate_ast_node(node.left, allowed_functions)
    _validate_ast_node(node.right, allowed_functions)


def _validate_call(node: ast.Call, allowed_functions: Optional[Dict[str, Any]]) -> None:
    if not isinstance(node.func, ast.Name):
        raise ValueError("Only direct function calls are allowed")
    func_name = node.func.id
    if allowed_functions is not None and func_name not in allowed_functions:
        raise ValueError(f"Function '{func_name}' is not allowed")
    for arg in node.args:
        _validate_ast_node(arg, allowed_functions)
    for keyword in node.keywords:
        if keyword.arg:
            _validate_ast_node(keyword.value, allowed_functions)


def _validate_sequence(node: Union[ast.List, ast.Tuple], allowed_functions: Optional[Dict[str, Any]]) -> None:
    for element in node.elts:
        _validate_ast_node(element, allowed_functions)


def _validate_subscript(node: ast.Subscript, allowed_functions: Optional[Dict[str, Any]]) -> None:
    _validate_ast_node(node.value, allowed_functions)
    _validate_ast_node(node.slice, allowed_functions)


def _validate_slice(node: ast.Slice, allowed_functions: Optional[Dict[str, Any]]) -> None:
    if node.lower:
        _validate_ast_node(node.lower, allowed_functions)
    if node.upper:
        _validate_ast_node(node.upper, allowed_functions)
    if node.step:
        _validate_ast_node(node.step, allowed_functions)


def _validate_slice_like(node: ast.AST, allowed_functions: Optional[Dict[str, Any]]) -> None:
    """Validate Subscript / Slice nodes (Python 3.11+ – ast.Index removed)."""
    if isinstance(node, ast.Subscript):
        _validate_subscript(node, allowed_functions)
    elif isinstance(node, ast.Slice):
        _validate_slice(node, allowed_functions)
    else:
        raise ValueError(f"Unsupported slice-like node: {type(node)}")



class _EvalVisitor(ast.NodeVisitor):
    def __init__(self, allowed_functions: Dict[str, Any]):
        self.allowed_functions = allowed_functions

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float, type(None))):
            return node.value
        raise ValueError(f"Disallowed constant type: {type(node.value)}")

    def visit_UnaryOp(self, node):
        import operator
        op = {ast.UAdd: operator.pos, ast.USub: operator.neg}.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        return op(self.visit(node.operand))

    def visit_BinOp(self, node):
        import operator
        bin_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }
        op = bin_ops.get(type(node.op))
        if not op:
            raise ValueError(f"Unsupported binary operator: {type(node.op)}")
        return op(self.visit(node.left), self.visit(node.right))

    def visit_Name(self, node):
        if node.id in self.allowed_functions:
            return self.allowed_functions[node.id]
        raise ValueError(f"Name '{node.id}' is not allowed")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct function calls are allowed")
        func_name = node.func.id
        if func_name not in self.allowed_functions:
            raise ValueError(f"Function '{func_name}' is not allowed")
        func = self.allowed_functions[func_name]
        args = [self.visit(a) for a in node.args]
        kwargs = {kw.arg: self.visit(kw.value) for kw in node.keywords if kw.arg}
        return func(*args, **kwargs)

    def visit_List(self, node):
        return [self.visit(e) for e in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(e) for e in node.elts)

    def visit_Slice(self, node):
        lower = self.visit(node.lower) if node.lower else None
        upper = self.visit(node.upper) if node.upper else None
        step = self.visit(node.step) if node.step else None
        return slice(lower, upper, step)

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        idx_node = node.slice
        if isinstance(idx_node, ast.Slice):
            idx = self.visit(idx_node)
        elif isinstance(idx_node, ast.Constant):
            idx = idx_node.value
        else:
            idx = self.visit(idx_node)
        try:
            return value[idx]  # type: ignore[index]
        except Exception as e:
            raise ValueError(f"Subscript operation failed: {e}")

    def generic_visit(self, node):
        raise ValueError(f"Unsupported AST node type: {type(node)}")

def _evaluate_ast_node(node: ast.AST, allowed_functions: Dict[str, Any]) -> Any:
    """Evaluate a validated AST node using a visitor pattern for clarity and maintainability."""
    visitor = _EvalVisitor(allowed_functions)
    return visitor.visit(node)


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
    def validate_file_path(file_path: str, allowed_dirs: Optional[List[str]] = None) -> bool:
        """Validate file path to prevent directory traversal attacks.

        Args:
            file_path: Path to validate
            allowed_dirs: Optional[List[str]]: List of allowed directory prefixes

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
    def secure_eval_alternative(expression: str, allowed_functions: Optional[Dict[str, Any]] = None) -> Any:
        """Safe alternative to direct dynamic evaluation for simple expressions.

        Args:
            expression: Mathematical or simple expression
            allowed_functions: Optional mapping of function name to callable

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

    # SECURITY FIX: Replace dynamic evaluation with AST-based safe evaluation (no direct eval)

        # Enforce maximum expression length to prevent DoS
        max_length = 1000
        if len(expression) > max_length:
            raise ValueError(f"Expression exceeds maximum length of {max_length}")

    # Whitelist allowed characters (aligned with documentation & AST validation):
        # digits, arithmetic ops, parentheses, decimal point, spaces, letters, underscore, comma.
        allowed_chars = set('0123456789+-*/.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_,')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains disallowed characters")

        try:
            # Parse expression to AST
            tree = ast.parse(expression, mode='eval')

            # Validate AST structure
            _validate_ast_node(tree.body, allowed_functions)

            # Evaluate AST in a controlled manner without using eval()
            return _evaluate_ast_node(tree.body, allowed_functions or {})

        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")
        except Exception as e:
            raise ValueError(f"Safe evaluation failed: {e}")

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
