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
        for pattern in _SELF_AWARE_PATTERNS:
            if pattern.search(line):
                findings.append(
                    _finding(
                        rule_id="AXIOM_2_SELF_AWARE_NARRATION",
                        severity=ValidationSeverity.ERROR,
                        message="Narration appears to comment on its own style or editorial behavior.",
                        line=line,
                        line_number=line_number,
                    )
                )
                break

        for pattern in _TRAILER_PATTERNS:
            if pattern.search(line):
                findings.append(
                    _finding(
                        rule_id="AXIOM_10_TRAILER_LINE",
                        severity=ValidationSeverity.WARNING,
                        message="The line reads as a generic dramatic reveal rather than a material state change.",
                        line=line,
                        line_number=line_number,
                    )
                )
                break

        if re.search(r"\bnot\s+.{1,60}\s+but\s+", line, re.IGNORECASE):
            findings.append(
                _finding(
                    rule_id="AXIOM_10_CONTRAST_TEMPLATE",
                    severity=ValidationSeverity.WARNING,
                    message="Repeated 'not X, but Y' construction may create compressed rhetorical prose.",
                    line=line,
                    line_number=line_number,
                )
            )

        word_count = _dialogue_word_count(line)
        if word_count is not None and word_count <= 5:
            short_dialogue_run.append((line_number, line))
        else:
            if len(short_dialogue_run) >= 4:
                start_line, start_passage = short_dialogue_run[0]
                findings.append(
                    _finding(
                        rule_id="AXIOM_10_SHORT_DIALOGUE_RUN",
                        severity=ValidationSeverity.WARNING,
                        message="Four or more consecutive clipped dialogue turns may sound mechanical unless action requires it.",
                        line=start_passage,
                        line_number=start_line,
                    )
                )
            short_dialogue_run = []

    if len(short_dialogue_run) >= 4:
        start_line, start_passage = short_dialogue_run[0]
        findings.append(
            _finding(
                rule_id="AXIOM_10_SHORT_DIALOGUE_RUN",
                severity=ValidationSeverity.WARNING,
                message="Four or more consecutive clipped dialogue turns may sound mechanical unless action requires it.",
                line=start_passage,
                line_number=start_line,
            )
        )

    lowered = draft_text.lower()
    leaked_terms = [term for term in _INTERNAL_TERMS if re.search(rf"\b{re.escape(term)}\b", lowered)]
    if len(leaked_terms) >= 2:
        findings.append(
            ValidationFinding(
                rule_id="SURFACE_LANGUAGE_SYMBOLIC_BLEED",
                severity=ValidationSeverity.WARNING,
                message=(
                    "Multiple internal RiverCycle terms appear in surface prose. Confirm each is natural in-world language: "
                    + ", ".join(leaked_terms)
                ),
                passage=", ".join(leaked_terms),
            )
        )

    if frame.required_downstream_effects and len(draft_text.strip()) < 200:
        findings.append(
            ValidationFinding(
                rule_id="FRAME_REQUIRED_EFFECTS_COVERAGE",
                severity=ValidationSeverity.INFO,
                message="The draft is very short relative to the frame's required downstream effects; manual coverage review is needed.",
            )
        )

    return ValidationReport(frame_id=frame.frame_id, findings=findings)
