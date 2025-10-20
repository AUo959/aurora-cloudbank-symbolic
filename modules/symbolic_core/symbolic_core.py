#!/usr/bin/env python3
"""Symbolic Core - Expression parsing and evaluation engine.

This module provides the SymbolicCore class for parsing and evaluating
symbolic expressions in the Aurora CloudBank Symbolic system.
"""

from __future__ import annotations

import ast
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SymbolicCore:
    """Core symbolic expression parser and evaluator.

    Provides safe parsing and evaluation of symbolic expressions using
    Python's AST for secure evaluation of mathematical expressions.
    """

    def __init__(self):
        """Initialize the symbolic core engine."""
        self._supported_operators = {
            ast.Add: lambda a, b: a + b,
            ast.Sub: lambda a, b: a - b,
            ast.Mult: lambda a, b: a * b,
            ast.Div: lambda a, b: a / b if b != 0 else float('inf'),
            ast.Pow: lambda a, b: a ** b,
            ast.USub: lambda a: -a,
            ast.UAdd: lambda a: +a,
        }
        logger.info("SymbolicCore initialized")

    def parse_expression(self, expression: str) -> Dict[str, Any]:
        """Parse a symbolic expression and return its structure.

        Args:
            expression: String representation of the expression

        Returns:
            Dictionary containing:
                - success: bool indicating if parsing succeeded
                - expression: original expression string
                - parsed: parsed AST representation
                - result: evaluated result (if evaluable)
                - error: error message (if parsing failed)
        """
        try:
            # Parse the expression into an AST
            tree = ast.parse(expression, mode='eval')

            # Try to safely evaluate the expression
            result = None
            try:
                result = self._eval_node(tree.body)
            except Exception as eval_error:
                logger.debug(f"Expression evaluation failed: {eval_error}")

            return {
                "success": True,
                "expression": expression,
                "parsed": ast.dump(tree),
                "result": result,
                "type": type(tree.body).__name__,
            }

        except SyntaxError as e:
            logger.warning(f"Failed to parse expression '{expression}': {e}")
            return {
                "success": False,
                "expression": expression,
                "error": f"Syntax error: {str(e)}",
            }
        except Exception as e:
            logger.error(f"Unexpected error parsing expression '{expression}': {e}")
            return {
                "success": False,
                "expression": expression,
                "error": f"Parse error: {str(e)}",
            }

    def _eval_node(self, node: ast.AST) -> Any:
        """Recursively evaluate an AST node.

        Args:
            node: AST node to evaluate

        Returns:
            Evaluated result

        Raises:
            ValueError: If node type is not supported
        """
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Num):  # For older Python versions
            return node.n
        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_type = type(node.op)
            if op_type in self._supported_operators:
                return self._supported_operators[op_type](left, right)
            else:
                raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            op_type = type(node.op)
            if op_type in self._supported_operators:
                return self._supported_operators[op_type](operand)
            else:
                raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        else:
            raise ValueError(f"Unsupported node type: {type(node).__name__}")

    def evaluate(self, expression: str) -> Optional[Any]:
        """Evaluate an expression and return only the result.

        Args:
            expression: String representation of the expression

        Returns:
            Evaluated result or None if evaluation failed
        """
        parsed = self.parse_expression(expression)
        return parsed.get("result") if parsed.get("success") else None
