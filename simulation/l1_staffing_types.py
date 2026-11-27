#!/usr/bin/env python3
"""Typed demand inputs for deterministic Orion L1 staffing decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from l1_staffing_validation import (
    require_nonnegative_integers,
    require_nonnegative_numeric,
)


@dataclass(frozen=True)
class StaffingDemand:
    """Evidence-backed demand signal; it is not itself authority to hire."""

    demand_id: str
    department: str
    role: str
    staffing_seat: str
    provenance: str
    required_capabilities: Tuple[str, ...] = ()
    workload_utilization: float = 0.0
    sustained_overtime_hours: float = 0.0
    uncovered_shifts: int = 0
    program_expansion: bool = False
    new_capability_requirement: bool = False
    attrition_or_leave: int = 0
    safety_constraint: bool = False
    separation_of_duties: bool = False
    succession_risk: bool = False
    engagement_class: str = "employee"

    def validate(self) -> None:
        strings = (
            self.demand_id,
            self.department,
            self.role,
            self.staffing_seat,
            self.provenance,
        )
        if not all(isinstance(value, str) and value.strip() for value in strings):
            raise ValueError(
                "staffing demand identity fields must be non-empty strings"
            )
        if self.engagement_class not in {"employee", "contractor", "visitor"}:
            raise ValueError("unsupported staffing engagement class")
        if not all(
            isinstance(value, str) and value.strip()
            for value in self.required_capabilities
        ):
            raise ValueError("required staffing capabilities must be non-empty strings")
        self._validate_numeric_signals()
        self._validate_boolean_signals()

    def _validate_numeric_signals(self) -> None:
        require_nonnegative_numeric(
            (self.workload_utilization, self.sustained_overtime_hours),
            "staffing workload signals",
        )
        require_nonnegative_integers(
            (self.uncovered_shifts, self.attrition_or_leave),
            "staffing demand counts",
        )

    def _validate_boolean_signals(self) -> None:
        signals = (
            self.program_expansion,
            self.new_capability_requirement,
            self.safety_constraint,
            self.separation_of_duties,
            self.succession_risk,
        )
        if not all(type(value) is bool for value in signals):
            raise ValueError("staffing constraint signals must be booleans")

    def reasons(self) -> Tuple[str, ...]:
        """Return deterministic institutional reasons that justify HR review."""
        signals = (
            (self.workload_utilization > 1.0, "workload_over_capacity"),
            (self.sustained_overtime_hours >= 8.0, "sustained_overtime"),
            (self.uncovered_shifts > 0, "uncovered_shifts"),
            (self.program_expansion, "program_expansion"),
            (
                self.new_capability_requirement,
                "new_technical_capability_requirement",
            ),
            (self.attrition_or_leave > 0, "attrition_or_leave"),
            (self.safety_constraint, "safety_or_ethics_constraint"),
            (self.separation_of_duties, "separation_of_duties"),
            (self.succession_risk, "succession_or_coverage_risk"),
        )
        return tuple(reason for active, reason in signals if active)


__all__ = ["StaffingDemand"]
