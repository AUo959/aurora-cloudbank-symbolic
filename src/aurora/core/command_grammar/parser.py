from __future__ import annotations

import re
import shlex
from typing import List, Optional, Tuple

from .ast import (
    AstNode,
    CommandArgument,
    CommandArgumentKind,
    CommandInvocation,
    CommandKind,
    CommandSequence,
    ParseResult,
    ParseWarning,
    RangeChain,
    WarningCode,
)
from .catalog import AuroraCommandCatalog
from .normalizer import NormalizationResult, normalize_command_text
from .validator import AuroraCommandValidator

_EXECUTION_PATTERN = re.compile(r"^(?P<body>.*?)(?P<sigil>//\.)(?P<modifier>[A-Za-z0-9_-]+)?$")
_INLINE_RANGE_PATTERN = re.compile(r"^(?P<start>#?\d{3})//(?P<end>#?\d{3})$")
_FUNCTION_PATTERN = re.compile(r"^(?P<head>[A-Za-z0-9_.:#-]+)\((?P<arguments>.*)\)$")


class CommandParseError(ValueError):
    pass


class AuroraCommandGrammar:
    def __init__(self, catalog: Optional[AuroraCommandCatalog] = None):
        self.catalog = catalog or AuroraCommandCatalog()
        self.validator = AuroraCommandValidator(self.catalog)

    def normalize(self, text: str) -> NormalizationResult:
        return normalize_command_text(text)

    def parse(self, text: str, validate: bool = True) -> ParseResult:
        normalization = self.normalize(text)
        ast, parse_warnings = self._parse_normalized(normalization.text)
        warnings = tuple(normalization.warnings) + tuple(parse_warnings)
        validation_issues = self.validate_ast(ast) if validate else ()
        return ParseResult(
            raw_text=text,
            normalized_text=self._canonical_notation(ast),
            ast=ast,
            warnings=warnings,
            validation_issues=validation_issues,
        )

    def validate_ast(self, ast: AstNode):
        return self.validator.validate(ast)

    def _parse_normalized(self, normalized_text: str) -> Tuple[AstNode, Tuple[ParseWarning, ...]]:
        match = _EXECUTION_PATTERN.match(normalized_text.strip())
        if match is None:
            raise CommandParseError("Command text must terminate with '//.' before parsing.")

        body = match.group("body").strip()
        modifier = match.group("modifier")
        if not body:
            raise CommandParseError("Command text is empty after removing the execution sigil.")

        if modifier and _INLINE_RANGE_PATTERN.match(body):
            raise CommandParseError("Range chains do not support command modifiers.")

        range_match = _INLINE_RANGE_PATTERN.match(body)
        if range_match is not None:
            return (
                RangeChain(
                    raw=normalized_text,
                    start=int(range_match.group("start").lstrip("#")),
                    end=int(range_match.group("end").lstrip("#")),
                ),
                (),
            )

        segments = self._split_top_level(body, "//")
        if len(segments) > 1:
            if modifier:
                raise CommandParseError("Explicit multi-command chains do not support trailing modifiers.")

            invocations = []
            warnings: List[ParseWarning] = []
            for segment in segments:
                invocation, invocation_warnings = self._parse_invocation(segment)
                invocations.append(invocation)
                warnings.extend(invocation_warnings)
            return CommandSequence(raw=normalized_text, invocations=tuple(invocations)), tuple(warnings)

        invocation, invocation_warnings = self._parse_invocation(body, modifier=modifier)
        return invocation, tuple(invocation_warnings)

    def _parse_invocation(
        self, segment: str, modifier: Optional[str] = None
    ) -> Tuple[CommandInvocation, Tuple[ParseWarning, ...]]:
        raw_segment = segment.strip()
        if not raw_segment:
            raise CommandParseError("Encountered an empty command segment inside a chain.")

        warnings = []
        legacy_prefix = None

        if raw_segment.startswith("#"):
            legacy_prefix = "#"
            raw_segment = raw_segment[1:].lstrip()
            warnings.append(
                ParseWarning(
                    code=WarningCode.LEGACY_HASH_PREFIX,
                    message="Removed legacy leading '#' command prefix.",
                )
            )

        function_match = _FUNCTION_PATTERN.match(raw_segment)
        if function_match is not None and self.catalog.resolve(function_match.group("head")) is not None:
            head = function_match.group("head")
            arguments = self._parse_argument_list(function_match.group("arguments"), delimiter=",")
        else:
            head, arguments = self._parse_space_delimited_segment(raw_segment)

        definition = self.catalog.resolve(head)
        canonical_head = definition.canonical_head if definition is not None else head
        kind = definition.kind if definition is not None else CommandKind.UNKNOWN

        invocation = CommandInvocation(
            raw=segment.strip(),
            head=head,
            canonical_head=canonical_head,
            kind=kind,
            arguments=arguments,
            modifier=modifier,
            legacy_prefix=legacy_prefix,
        )
        return invocation, tuple(warnings)

    def _parse_space_delimited_segment(self, segment: str) -> Tuple[str, Tuple[CommandArgument, ...]]:
        try:
            tokens = shlex.split(segment)
        except ValueError as error:
            raise CommandParseError(f"Unable to parse command segment '{segment}': {error}") from error

        if not tokens:
            raise CommandParseError("Command segment did not contain a head token.")

        head_token = tokens[0]
        argument_tokens = list(tokens[1:])

        resolved_definition = self.catalog.resolve(head_token)
        if resolved_definition is None and "::" in head_token:
            candidate_head, inline_argument = head_token.split("::", 1)
            candidate_definition = self.catalog.resolve(candidate_head)
            if candidate_definition is not None:
                head_token = candidate_head
                if inline_argument:
                    argument_tokens.insert(0, inline_argument)
                resolved_definition = candidate_definition

        if resolved_definition is None and head_token.endswith(":"):
            candidate_head = head_token[:-1]
            candidate_definition = self.catalog.resolve(candidate_head)
            if candidate_definition is not None:
                head_token = candidate_head
                resolved_definition = candidate_definition

        arguments = self._parse_argument_tokens(argument_tokens)
        return head_token, arguments

    def _parse_argument_list(self, raw_arguments: str, delimiter: str) -> Tuple[CommandArgument, ...]:
        if not raw_arguments.strip():
            return ()
        items = self._split_top_level(raw_arguments, delimiter)
        return self._parse_argument_tokens(items)

    def _parse_argument_tokens(self, tokens: List[str]) -> Tuple[CommandArgument, ...]:
        arguments = []
        for token in tokens:
            raw_token = token.strip()
            if not raw_token:
                continue
            if "=" in raw_token:
                name, value = raw_token.split("=", 1)
                arguments.append(
                    CommandArgument(
                        raw=raw_token,
                        value=self._strip_wrapping_quotes(value.strip()),
                        kind=CommandArgumentKind.KEYWORD,
                        name=name.strip(),
                    )
                )
                continue

            arguments.append(
                CommandArgument(
                    raw=raw_token,
                    value=self._strip_wrapping_quotes(raw_token),
                    kind=CommandArgumentKind.POSITIONAL,
                )
            )

        return tuple(arguments)

    def _canonical_notation(self, ast: AstNode) -> str:
        return ast.canonical_notation

    def _split_top_level(self, text: str, delimiter: str) -> List[str]:
        parts = []
        current = []
        quote: Optional[str] = None
        depth = 0
        index = 0

        while index < len(text):
            character = text[index]

            if quote is not None:
                current.append(character)
                if character == quote:
                    quote = None
                index += 1
                continue

            if character in ('"', "'"):
                quote = character
                current.append(character)
                index += 1
                continue

            if character in "([{":
                depth += 1
                current.append(character)
                index += 1
                continue

            if character in ")]}":
                depth = max(depth - 1, 0)
                current.append(character)
                index += 1
                continue

            if depth == 0 and text.startswith(delimiter, index):
                parts.append("".join(current).strip())
                current = []
                index += len(delimiter)
                continue

            current.append(character)
            index += 1

        parts.append("".join(current).strip())
        return [part for part in parts if part]

    def _strip_wrapping_quotes(self, value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
            return value[1:-1]
        return value
