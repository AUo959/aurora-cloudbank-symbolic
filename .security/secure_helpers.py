#!/usr/bin/env python3
"""
Aurora CloudBank security helpers.

Repo-owned helpers for safer command execution, input sanitization, and
bounded expression evaluation used by security tooling and remediation flows.
"""

from __future__ import annotations

import ast
import html
import operator
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


class SecureHelpers:
    """Provide safer alternatives to common utility operations."""

    _BINARY_OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    _UNARY_OPERATORS = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    @staticmethod
    def secure_run_command(
        cmd: str | Sequence[str],
        timeout: int = 30,
        cwd: Optional[str | Path] = None,
        capture_output: bool = True,
    ) -> tuple[str, str, int]:
        """Execute a command without invoking a shell."""

        try:
            cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else list(cmd)
            result = subprocess.run(
                cmd_parts,
                timeout=timeout,
                cwd=str(cwd) if cwd is not None else None,
                capture_output=capture_output,
                text=True,
                check=False,
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", 124
        except (OSError, ValueError) as exc:
            return "", f"Command execution error: {exc}", 1

    @staticmethod
    def sanitize_input(user_input: str, max_length: int = 1000) -> str:
        """Sanitize free-form text for safe display or logging."""

        if not isinstance(user_input, str):
            return ""

        normalized = user_input[:max_length]
        normalized = re.sub(r"(?i)javascript:", "", normalized)
        normalized = re.sub(r"(?i)on[a-z]+\s*=", "", normalized)
        normalized = re.sub(r"(?is)<script[^>]*>.*?</script>", "", normalized)
        return html.escape(normalized, quote=True).strip()

    @staticmethod
    def validate_file_path(file_path: str, allowed_dirs: Optional[Sequence[str | Path]] = None) -> bool:
        """Reject traversal paths and optionally constrain paths to known roots."""

        if not isinstance(file_path, str) or not file_path.strip():
            return False

        raw_path = Path(file_path)
        if ".." in raw_path.parts:
            return False

        try:
            candidate = raw_path.resolve(strict=False)
        except (OSError, RuntimeError):
            return False

        if not allowed_dirs:
            return not raw_path.is_absolute()

        for allowed_dir in allowed_dirs:
            try:
                allowed_root = Path(allowed_dir).resolve(strict=False)
                candidate.relative_to(allowed_root)
                return True
            except ValueError:
                continue
            except (OSError, RuntimeError):
                continue
        return False

    def secure_eval_alternative(
        self,
        expression: str,
        allowed_functions: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """Safely evaluate simple arithmetic expressions and approved helpers."""

        if not isinstance(expression, str) or not expression.strip():
            raise ValueError("Expression must be a non-empty string")

        names = dict(
            allowed_functions
            or {
                "abs": abs,
                "min": min,
                "max": max,
                "sum": sum,
                "len": len,
            }
        )

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Expression contains invalid syntax: {exc}") from exc

        return self._evaluate_node(tree.body, names)

    def _evaluate_node(self, node: ast.AST, names: Mapping[str, Any]) -> Any:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.List):
            return [self._evaluate_node(element, names) for element in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(self._evaluate_node(element, names) for element in node.elts)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self._UNARY_OPERATORS:
            return self._UNARY_OPERATORS[type(node.op)](self._evaluate_node(node.operand, names))

        if isinstance(node, ast.BinOp) and type(node.op) in self._BINARY_OPERATORS:
            left = self._evaluate_node(node.left, names)
            right = self._evaluate_node(node.right, names)
            return self._BINARY_OPERATORS[type(node.op)](left, right)

        if isinstance(node, ast.Name) and node.id in names:
            return names[node.id]

        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in names:
            if node.keywords:
                raise ValueError("Keyword arguments are not allowed in safe expressions")
            function = names[node.func.id]
            args = [self._evaluate_node(argument, names) for argument in node.args]
            return function(*args)

        raise ValueError(f"Unsafe expression node: {type(node).__name__}")


secure = SecureHelpers()

__all__ = ["SecureHelpers", "secure"]
