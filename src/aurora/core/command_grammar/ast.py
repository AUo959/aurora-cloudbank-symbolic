from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Union


class CommandArgumentMode(str, Enum):
    NONE = "none"
    OPTIONAL = "optional"
    VARIADIC = "variadic"


class CommandArgumentKind(str, Enum):
    POSITIONAL = "positional"
    KEYWORD = "keyword"


class CommandKind(str, Enum):
    CHAIN = "chain"
    CODE = "code"
    DIRECTIVE = "directive"
    UNKNOWN = "unknown"
    VERB = "verb"


class IssueSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class WarningCode(str, Enum):
    LEGACY_HASH_PREFIX = "legacy_hash_prefix"
    LEGACY_PARTIAL_TERMINATOR = "legacy_partial_terminator"
    LEGACY_PLUS_PREFIX = "legacy_plus_prefix"
    MISSING_EXECUTION_SIGIL = "missing_execution_sigil"


@dataclass(frozen=True)
class ParseWarning:
    code: WarningCode
    message: str


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: IssueSeverity
    head: Optional[str] = None


@dataclass(frozen=True)
class CommandArgument:
    raw: str
    value: str
    kind: CommandArgumentKind = CommandArgumentKind.POSITIONAL
    name: Optional[str] = None

    def render(self) -> str:
        return self.raw


@dataclass(frozen=True)
class CommandInvocation:
    raw: str
    head: str
    canonical_head: str
    kind: CommandKind
    arguments: Tuple[CommandArgument, ...] = field(default_factory=tuple)
    modifier: Optional[str] = None
    legacy_prefix: Optional[str] = None

    @property
    def canonical_body(self) -> str:
        rendered_arguments = " ".join(argument.render() for argument in self.arguments)
        if rendered_arguments:
            return f"{self.canonical_head} {rendered_arguments}"
        return self.canonical_head

    @property
    def canonical_notation(self) -> str:
        modifier = self.modifier or ""
        return f"{self.canonical_body}//.{modifier}"


@dataclass(frozen=True)
class CommandSequence:
    raw: str
    invocations: Tuple[CommandInvocation, ...]

    @property
    def canonical_notation(self) -> str:
        return " // ".join(invocation.canonical_body for invocation in self.invocations) + " //."


@dataclass(frozen=True)
class RangeChain:
    raw: str
    start: int
    end: int

    @property
    def canonical_notation(self) -> str:
        return f"{self.start:03d}//{self.end:03d}//."


AstNode = Union[CommandInvocation, CommandSequence, RangeChain]


@dataclass(frozen=True)
class ParseResult:
    raw_text: str
    normalized_text: str
    ast: AstNode
    warnings: Tuple[ParseWarning, ...] = field(default_factory=tuple)
    validation_issues: Tuple[ValidationIssue, ...] = field(default_factory=tuple)

    @property
    def is_valid(self) -> bool:
        return all(issue.severity != IssueSeverity.ERROR for issue in self.validation_issues)
