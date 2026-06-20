"""
HR System - Organizational Intelligence
========================================
Anchor: T1-HRS-ORG-INTEL-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Capacity planning and organizational intelligence derived from staffing analysis.
Provides a unified view of org-wide and per-department staffing health.
"""

from datetime import datetime, UTC
from typing import Any, Dict, List, Optional
import logging

from .staffing_analyzer import StaffingAnalyzer

logger = logging.getLogger(__name__)

_GROWTH_THRESHOLDS = {
    "expanding": 0.10,   # gap > 10% of capacity → growing faster than staff
    "stable": -0.05,     # gap between -5% and +10%
    "contracting": None, # gap < -5% → over-staffed
}


def _infer_growth_trajectory(total_gap: int, total_capacity: int) -> str:
    """Classify org growth trajectory from staffing gap ratio."""
    if total_capacity == 0:
        return "unknown"
    ratio = total_gap / total_capacity
    if ratio > _GROWTH_THRESHOLDS["expanding"]:
        return "expanding"
    if ratio >= _GROWTH_THRESHOLDS["stable"]:
        return "stable"
    return "contracting"


class OrganizationalIntelligence:
    """
    Provides org-wide and per-department capacity analysis.

    Delegates metric collection to StaffingAnalyzer and adds
    growth-trajectory inference and structured reporting.
    """

    def __init__(self) -> None:
        self._analyzer = StaffingAnalyzer()

    def get_capacity_analysis(
        self,
        department: Optional[str] = None,
        context_tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return capacity analysis for the org or a single department.

        Args:
            department: If provided, scope the analysis to that department.
            context_tag: Optional DLP context tag for lineage tracking.

        Returns:
            Structured capacity analysis dict.
        """
        ts = datetime.now(UTC).isoformat()
        ctx = context_tag or f"org_intel_{department or 'all'}_{ts}"

        if department:
            return self._department_analysis(department, ctx, ts)
        return self._org_analysis(ctx, ts)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _department_analysis(
        self, department: str, context_tag: str, timestamp: str
    ) -> Dict[str, Any]:
        result = self._analyzer.analyze_department_needs(
            department=department, context_tag=context_tag
        )
        current = result["current_staff"]
        recommended = result["recommended_staff"]
        gap = recommended - current
        trajectory = _infer_growth_trajectory(gap, max(1, recommended))

        logger.info(
            "OrganizationalIntelligence: department=%s current=%d recommended=%d",
            department,
            current,
            recommended,
        )

        return {
            "departments": [department],
            "total_capacity": recommended,
            "current_staff": current,
            "current_utilization": round(current / max(1, recommended), 4),
            "total_gap": gap,
            "gap_analysis": result.get("gap_analysis", {}),
            "priority": result.get("priority"),
            "rationale": result.get("rationale"),
            "growth_trajectory": trajectory,
            "context_tag": context_tag,
            "timestamp": timestamp,
        }

    def _org_analysis(self, context_tag: str, timestamp: str) -> Dict[str, Any]:
        summary = self._analyzer.get_organization_summary()
        dept_names = [d.title() for d in self._analyzer.get_department_list()]
        total_capacity = summary["total_recommended_staff"]
        total_gap = summary["total_gap"]
        trajectory = _infer_growth_trajectory(total_gap, max(1, total_capacity))

        logger.info(
            "OrganizationalIntelligence: org-wide total_current=%d total_recommended=%d",
            summary["total_current_staff"],
            total_capacity,
        )

        return {
            "departments": dept_names,
            "total_capacity": total_capacity,
            "current_staff": summary["total_current_staff"],
            "current_utilization": round(
                summary["organization_capacity_utilization"] / 100, 4
            ),
            "total_gap": total_gap,
            "high_priority_departments": summary["high_priority_departments"],
            "growth_trajectory": trajectory,
            "context_tag": context_tag,
            "timestamp": timestamp,
        }
