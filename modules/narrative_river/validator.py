"""Advisory, explainable prose checks for the Narrative River Adapter."""

from __future__ import annotations

import re

from .models import (
    NarrativeRiverFrame,
    ValidationFinding,
    ValidationReport,
    ValidationSeverity,
)

_SELF_AWARE_PATTERNS = (
    re.compile(r"\bneither of them (?:made|turned|treated)\b", re.IGNORECASE),
    re.compile(r"\bthe exchange remained\b", re.IGNORECASE),
    re.compile(r"\bthere was no banter\b", re.IGNORECASE),
    re.compile(r"\bthe moment did not become\b", re.IGNORECASE),
    re.compile(r"\bwithout turning (?:it|the moment) into\b", re.IGNORECASE),
)

_TRAILER_PATTERNS = (
    re.compile(r"\bwhat you came to find\b", re.IGNORECASE),
    re.compile(r"\byou have no idea what(?:'s| is) coming\b", re.IGNORECASE),
    re.compile(r"\bthis changes everything\b", re.IGNORECASE),
)

_INTERNAL_TERMS = ("sediment", "reservoir", "nutrient", "salmon return", "rivercycle")


def _dialogue_word_count(line: str) -> int | None:
    match = re.search(r"[\"“](.+?)[\"”]", line)
    if not match:
        return None
    return len(re.findall(r"\b[\w'-]+\b", match.group(1)))


def _finding(
    *,
    rule_id: str,
    severity: ValidationSeverity,
    message: str,
    line: str,
    line_number: int,
) -> ValidationFinding:
    return ValidationFinding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        passage=line.strip(),
        line_number=line_number,
    )


def validate_draft(frame: NarrativeRiverFrame, draft_text: str) -> ValidationReport:
    """Run passive heuristics and return cited findings without mutating text."""

    findings: list[ValidationFinding] = []
    lines = draft_text.splitlines()
    short_dialogue_run: list[tuple[int, str]] = []

    for line_number, line in enumerate(lines, start=1):
        findings.extend(_line_findings(line, line_number))
        if _is_short_dialogue(line):
            short_dialogue_run.append((line_number, line))
        else:
            findings.extend(_short_dialogue_findings(short_dialogue_run))
            short_dialogue_run = []

    findings.extend(_short_dialogue_findings(short_dialogue_run))
    findings.extend(_whole_draft_findings(frame, draft_text))

    return ValidationReport(frame_id=frame.frame_id, findings=findings)


def _line_findings(line: str, line_number: int) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    self_aware = _first_pattern_finding(
        _SELF_AWARE_PATTERNS,
        line,
        line_number,
        rule_id="AXIOM_2_SELF_AWARE_NARRATION",
        severity=ValidationSeverity.ERROR,
        message="Narration appears to comment on its own style or editorial behavior.",
    )
    trailer = _first_pattern_finding(
        _TRAILER_PATTERNS,
        line,
        line_number,
        rule_id="AXIOM_10_TRAILER_LINE",
        severity=ValidationSeverity.WARNING,
        message=(
            "The line reads as a generic dramatic reveal rather than a material "
            "state change."
        ),
    )
    findings.extend(item for item in (self_aware, trailer) if item is not None)
    if re.search(r"\bnot\s+.{1,60}\s+but\s+", line, re.IGNORECASE):
        findings.append(
            _finding(
                rule_id="AXIOM_10_CONTRAST_TEMPLATE",
                severity=ValidationSeverity.WARNING,
                message=(
                    "Repeated 'not X, but Y' construction may create compressed "
                    "rhetorical prose."
                ),
                line=line,
                line_number=line_number,
            )
        )
    return findings


def _first_pattern_finding(
    patterns: tuple[re.Pattern[str], ...],
    line: str,
    line_number: int,
    *,
    rule_id: str,
    severity: ValidationSeverity,
    message: str,
) -> ValidationFinding | None:
    if not any(pattern.search(line) for pattern in patterns):
        return None
    return _finding(
        rule_id=rule_id,
        severity=severity,
        message=message,
        line=line,
        line_number=line_number,
    )


def _is_short_dialogue(line: str) -> bool:
    word_count = _dialogue_word_count(line)
    return word_count is not None and word_count <= 5


def _short_dialogue_findings(
    run: list[tuple[int, str]],
) -> list[ValidationFinding]:
    if len(run) < 4:
        return []
    start_line, start_passage = run[0]
    return [
        _finding(
            rule_id="AXIOM_10_SHORT_DIALOGUE_RUN",
            severity=ValidationSeverity.WARNING,
            message=(
                "Four or more consecutive clipped dialogue turns may sound mechanical "
                "unless action requires it."
            ),
            line=start_passage,
            line_number=start_line,
        )
    ]


def _whole_draft_findings(
    frame: NarrativeRiverFrame,
    draft_text: str,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    leaked_terms = [
        term
        for term in _INTERNAL_TERMS
        if re.search(rf"\b{re.escape(term)}\b", draft_text.lower())
    ]
    if len(leaked_terms) >= 2:
        findings.append(_symbolic_bleed_finding(leaked_terms))
    if frame.required_downstream_effects and len(draft_text.strip()) < 200:
        findings.append(_coverage_finding())
    return findings


def _symbolic_bleed_finding(leaked_terms: list[str]) -> ValidationFinding:
    return ValidationFinding(
        rule_id="SURFACE_LANGUAGE_SYMBOLIC_BLEED",
        severity=ValidationSeverity.WARNING,
        message=(
            "Multiple internal RiverCycle terms appear in surface prose. Confirm each "
            "is natural in-world language: " + ", ".join(leaked_terms)
        ),
        passage=", ".join(leaked_terms),
    )


def _coverage_finding() -> ValidationFinding:
    return ValidationFinding(
        rule_id="FRAME_REQUIRED_EFFECTS_COVERAGE",
        severity=ValidationSeverity.INFO,
        message=(
            "The draft is very short relative to the frame's required downstream "
            "effects; manual coverage review is needed."
        ),
    )
