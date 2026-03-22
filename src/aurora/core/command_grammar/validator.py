from __future__ import annotations

from typing import List, Tuple

from .ast import (
    AstNode,
    CommandArgumentMode,
    CommandInvocation,
    CommandSequence,
    IssueSeverity,
    RangeChain,
    ValidationIssue,
)
from .catalog import AuroraCommandCatalog


class AuroraCommandValidator:
    def __init__(self, catalog: AuroraCommandCatalog):
        self.catalog = catalog

    def validate(self, ast: AstNode) -> Tuple[ValidationIssue, ...]:
        if isinstance(ast, CommandInvocation):
            return tuple(self._validate_invocation(ast))
        if isinstance(ast, CommandSequence):
            issues: List[ValidationIssue] = []
            for invocation in ast.invocations:
                issues.extend(self._validate_invocation(invocation))
            return tuple(issues)
        if isinstance(ast, RangeChain):
            return tuple(self._validate_range(ast))
        return ()

    def _validate_invocation(self, invocation: CommandInvocation) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        definition = self.catalog.get(invocation.canonical_head)
        if definition is None:
            issues.append(
                ValidationIssue(
                    code="unknown_command",
                    message=f"Command head '{invocation.canonical_head}' is not present in the grammar catalog.",
                    severity=IssueSeverity.ERROR,
                    head=invocation.canonical_head,
                )
            )
            return issues

        if invocation.modifier and not definition.supports_modifiers:
            issues.append(
                ValidationIssue(
                    code="unsupported_modifier",
                    message=(
                        f"Command head '{invocation.canonical_head}' does not advertise modifier variants, "
                        f"but received '{invocation.modifier}'."
                    ),
                    severity=IssueSeverity.WARNING,
                    head=invocation.canonical_head,
                )
            )

        if invocation.arguments and definition.argument_mode == CommandArgumentMode.NONE:
            issues.append(
                ValidationIssue(
                    code="unexpected_arguments",
                    message=(
                        f"Command head '{invocation.canonical_head}' is documented as argument-free, "
                        "but arguments were supplied."
                    ),
                    severity=IssueSeverity.WARNING,
                    head=invocation.canonical_head,
                )
            )

        return issues

    def _validate_range(self, chain: RangeChain) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        if chain.start > chain.end:
            issues.append(
                ValidationIssue(
                    code="descending_range",
                    message="Range chains must advance forward; start is greater than end.",
                    severity=IssueSeverity.ERROR,
                    head=f"{chain.start:03d}//{chain.end:03d}",
                )
            )
            return issues

        for edge in (chain.start, chain.end):
            edge_head = f"{edge:03d}"
            if self.catalog.get(edge_head) is None:
                issues.append(
                    ValidationIssue(
                        code="unknown_range_edge",
                        message=f"Range edge '{edge_head}' is not present in the grammar catalog.",
                        severity=IssueSeverity.ERROR,
                        head=edge_head,
                    )
                )

        return issues
