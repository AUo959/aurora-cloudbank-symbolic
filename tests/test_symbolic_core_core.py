"""
Test Suite for Symbolic Core - Expression Parsing and Evaluation

Comprehensive test coverage for the SymbolicCore class including:
- Basic expression parsing
- Evaluation of mathematical operations
- Error handling for invalid expressions
- Edge cases and security considerations

DLP: T1-SYMBOLIC-CORE-TEST
Chain: #test/symbolic_core/001
Target: 95%+ code coverage
"""

import sys
from pathlib import Path

import pytest

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.symbolic_core.symbolic_core import SymbolicCore


@pytest.mark.unit
@pytest.mark.critical
class TestSymbolicCoreInitialization:
    """Test SymbolicCore initialization."""

    def test_initialization(self):
        """Test symbolic core initializes correctly."""
        core = SymbolicCore()
        assert core is not None
        assert hasattr(core, '_supported_operators')
        assert len(core._supported_operators) > 0

    def test_supported_operators_present(self):
        """Test that all expected operators are supported."""
        core = SymbolicCore()
        import ast

        expected_ops = [ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.USub, ast.UAdd]
        for op in expected_ops:
            assert op in core._supported_operators


@pytest.mark.unit
@pytest.mark.critical
class TestSymbolicCoreBasicParsing:
    """Test basic expression parsing functionality."""

    def test_parse_simple_number(self):
        """Test parsing a simple number."""
        core = SymbolicCore()
        result = core.parse_expression("42")

        assert result["success"] is True
        assert result["expression"] == "42"
        assert result["result"] == 42

    def test_parse_addition(self):
        """Test parsing simple addition."""
        core = SymbolicCore()
        result = core.parse_expression("5 + 3")

        assert result["success"] is True
        assert result["result"] == 8

    def test_parse_subtraction(self):
        """Test parsing simple subtraction."""
        core = SymbolicCore()
        result = core.parse_expression("10 - 4")

        assert result["success"] is True
        assert result["result"] == 6

    def test_parse_multiplication(self):
        """Test parsing simple multiplication."""
        core = SymbolicCore()
        result = core.parse_expression("6 * 7")

        assert result["success"] is True
        assert result["result"] == 42

    def test_parse_division(self):
        """Test parsing simple division."""
        core = SymbolicCore()
        result = core.parse_expression("20 / 4")

        assert result["success"] is True
        assert result["result"] == 5.0

    def test_parse_power(self):
        """Test parsing exponentiation."""
        core = SymbolicCore()
        result = core.parse_expression("2 ** 3")

        assert result["success"] is True
        assert result["result"] == 8


@pytest.mark.unit
@pytest.mark.critical
class TestSymbolicCoreComplexExpressions:
    """Test complex mathematical expressions."""

    def test_parse_compound_expression(self):
        """Test parsing expression with multiple operations."""
        core = SymbolicCore()
        result = core.parse_expression("2 + 3 * 4")

        assert result["success"] is True
        # Should respect operator precedence: 2 + (3 * 4) = 14
        assert result["result"] == 14

    def test_parse_parentheses(self):
        """Test parsing expression with parentheses."""
        core = SymbolicCore()
        result = core.parse_expression("(2 + 3) * 4")

        assert result["success"] is True
        assert result["result"] == 20

    def test_parse_nested_operations(self):
        """Test parsing nested mathematical operations."""
        core = SymbolicCore()
        result = core.parse_expression("((5 + 3) * 2) - 4")

        assert result["success"] is True
        assert result["result"] == 12

    def test_parse_power_with_operations(self):
        """Test parsing power operations combined with others."""
        core = SymbolicCore()
        result = core.parse_expression("2 ** 3 + 1")

        assert result["success"] is True
        assert result["result"] == 9

    def test_parse_floating_point(self):
        """Test parsing floating point numbers."""
        core = SymbolicCore()
        result = core.parse_expression("3.14 * 2")

        assert result["success"] is True
        assert abs(result["result"] - 6.28) < 0.001


@pytest.mark.unit
@pytest.mark.critical
class TestSymbolicCoreUnaryOperators:
    """Test unary operators."""

    def test_parse_negative_number(self):
        """Test parsing negative numbers."""
        core = SymbolicCore()
        result = core.parse_expression("-5")

        assert result["success"] is True
        assert result["result"] == -5

    def test_parse_positive_sign(self):
        """Test parsing explicit positive sign."""
        core = SymbolicCore()
        result = core.parse_expression("+10")

        assert result["success"] is True
        assert result["result"] == 10

    def test_parse_negative_expression(self):
        """Test parsing negation of expression."""
        core = SymbolicCore()
        result = core.parse_expression("-(3 + 2)")

        assert result["success"] is True
        assert result["result"] == -5


@pytest.mark.unit
@pytest.mark.critical
class TestSymbolicCoreErrorHandling:
    """Test error handling for invalid expressions."""

    def test_parse_invalid_syntax(self):
        """Test handling of syntax errors."""
        core = SymbolicCore()
        result = core.parse_expression("2 +")

        assert result["success"] is False
        assert "error" in result
        assert "Syntax error" in result["error"]

    def test_parse_empty_string(self):
        """Test handling of empty expression."""
        core = SymbolicCore()
        result = core.parse_expression("")

        assert result["success"] is False
        assert "error" in result

    def test_parse_invalid_characters(self):
        """Test handling of invalid characters."""
        core = SymbolicCore()
        result = core.parse_expression("2 & 3")

        assert result["success"] is False

    def test_parse_unmatched_parentheses(self):
        """Test handling of unmatched parentheses."""
        core = SymbolicCore()
        result = core.parse_expression("(2 + 3")

        assert result["success"] is False
        assert "error" in result

    def test_division_by_zero(self):
        """Test handling of division by zero."""
        core = SymbolicCore()
        result = core.parse_expression("5 / 0")

        assert result["success"] is True
        # Should return infinity for division by zero
        assert result["result"] == float('inf')


@pytest.mark.unit
class TestSymbolicCoreEvaluateMethod:
    """Test the evaluate convenience method."""

    def test_evaluate_valid_expression(self):
        """Test evaluate method with valid expression."""
        core = SymbolicCore()
        result = core.evaluate("10 + 5")

        assert result == 15

    def test_evaluate_invalid_expression(self):
        """Test evaluate method with invalid expression."""
        core = SymbolicCore()
        result = core.evaluate("invalid expression")

        assert result is None

    def test_evaluate_returns_none_on_error(self):
        """Test evaluate returns None on parse error."""
        core = SymbolicCore()
        result = core.evaluate("2 +")

        assert result is None


@pytest.mark.unit
class TestSymbolicCoreEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_parse_very_large_number(self):
        """Test parsing very large numbers."""
        core = SymbolicCore()
        result = core.parse_expression("999999999999999")

        assert result["success"] is True
        assert result["result"] == 999999999999999

    def test_parse_very_small_number(self):
        """Test parsing very small decimal numbers."""
        core = SymbolicCore()
        result = core.parse_expression("0.00000001")

        assert result["success"] is True
        assert result["result"] == 0.00000001

    def test_parse_zero(self):
        """Test parsing zero."""
        core = SymbolicCore()
        result = core.parse_expression("0")

        assert result["success"] is True
        assert result["result"] == 0

    def test_parse_negative_zero(self):
        """Test parsing negative zero."""
        core = SymbolicCore()
        result = core.parse_expression("-0")

        assert result["success"] is True
        assert result["result"] == 0


@pytest.mark.unit
@pytest.mark.security
class TestSymbolicCoreSecurityConsiderations:
    """Test security considerations and limitations."""

    def test_no_variable_access(self):
        """Test that variables are not accessible."""
        core = SymbolicCore()
        result = core.parse_expression("x + 5")

        # Parsing succeeds, but evaluation fails (result is None) because variables are not supported
        assert result["success"] is True
        assert result["result"] is None  # Evaluation should fail

    def test_no_function_calls(self):
        """Test that function calls are not allowed."""
        core = SymbolicCore()
        result = core.parse_expression("print('hello')")

        # Should fail or return None for evaluation
        assert result["result"] is None

    def test_no_attribute_access(self):
        """Test that attribute access is not allowed."""
        core = SymbolicCore()
        result = core.parse_expression("obj.attr")

        # Should fail evaluation
        assert result["result"] is None


@pytest.mark.integration
class TestSymbolicCoreIntegration:
    """Integration tests for symbolic core."""

    def test_multiple_evaluations(self):
        """Test multiple sequential evaluations."""
        core = SymbolicCore()

        results = [
            core.evaluate("2 + 2"),
            core.evaluate("3 * 3"),
            core.evaluate("10 - 5"),
        ]

        assert results == [4, 9, 5]

    def test_stateless_evaluation(self):
        """Test that evaluations are stateless."""
        core = SymbolicCore()

        # Same expression should always give same result
        result1 = core.evaluate("5 + 5")
        result2 = core.evaluate("5 + 5")

        assert result1 == result2 == 10

    def test_parse_returns_complete_metadata(self):
        """Test that parse_expression returns all expected metadata."""
        core = SymbolicCore()
        result = core.parse_expression("2 + 3")

        # Check all expected keys are present
        assert "success" in result
        assert "expression" in result
        assert "parsed" in result
        assert "result" in result
        assert "type" in result
