"""
HR System - Staffing Analyzer
==============================
Anchor: T1-HRS-STAFFING-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Autonomous staffing need identification and analysis system.
Analyzes department workload, capacity, and recommends staffing adjustments.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, UTC
import logging

logger = logging.getLogger(__name__)


@dataclass
class StaffingMetrics:
    """Current staffing metrics"""
    department: str
    current_staff: int
    workload_index: float
    capacity_utilization: float
    avg_overtime_hours: float
    project_backlog_count: int
    skill_gaps: List[str]


@dataclass
class StaffingRecommendation:
    """Staffing recommendation"""
    department: str
    current_staff: int
    recommended_staff: int
    gap_analysis: Dict[str, int]
    priority: str
    rationale: str
    estimated_impact: Dict[str, Any]
    timeline: str


class StaffingAnalyzer:
    """
    Analyzes staffing needs and generates recommendations.
    
    Uses workload analysis, capacity planning, and skill gap assessment
    to identify optimal staffing levels.
    """
    
    def __init__(self):
        """Initialize staffing analyzer"""
        self.department_baselines = {
            "engineering": {"base_staff": 15, "projects_per_person": 2},
            "operations": {"base_staff": 10, "tickets_per_person": 50},
            "research": {"base_staff": 8, "papers_per_person": 4},
            "quantum": {"base_staff": 12, "experiments_per_person": 10},
            "security": {"base_staff": 6, "audits_per_person": 20},
            "support": {"base_staff": 8, "tickets_per_person": 100}
        }
        
        self.priority_thresholds = {
            "critical": 0.8,  # >80% over capacity
            "high": 0.5,      # >50% over capacity
            "medium": 0.2,    # >20% over capacity
            "low": 0.0        # Below baseline
        }
    
    def analyze_department_needs(
        self,
        department: str,
        context_tag: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze staffing needs for a department.
        
        Args:
            department: Department name
            context_tag: Optional DLP context tag
            
        Returns:
            Staffing analysis with recommendations
        """
        # Collect current metrics
        metrics = self._collect_department_metrics(department)
        
        # Calculate recommended staffing
        recommendation = self._calculate_staffing_needs(metrics)
        
        logger.info(
            "Analyzed staffing for %s: %d current, %d recommended",
            department, metrics.current_staff, recommendation.recommended_staff
        )
        
        return {
            "department": recommendation.department,
            "current_staff": recommendation.current_staff,
            "recommended_staff": recommendation.recommended_staff,
            "gap_analysis": recommendation.gap_analysis,
            "priority": recommendation.priority,
            "rationale": recommendation.rationale,
            "estimated_impact": recommendation.estimated_impact,
            "timeline": recommendation.timeline,
            "context_tag": context_tag or f"staffing_analysis_{department}_{datetime.now(UTC).isoformat()}"
        }
    
    def _collect_department_metrics(self, department: str) -> StaffingMetrics:
        """Collect current staffing metrics"""
        # Get baseline for department
        baseline = self.department_baselines.get(
            department.lower(),
            {"base_staff": 10, "projects_per_person": 5}
        )
        
        # In production, these would come from real monitoring systems
        # For now, simulate based on department characteristics
        current_staff = baseline["base_staff"]
        
        # Simulate workload (in production, pull from project management system)
        import random
        workload_index = random.uniform(0.7, 1.5)
        capacity_utilization = workload_index * 100
        avg_overtime_hours = max(0, (workload_index - 1.0) * 10)
        project_backlog_count = int((workload_index - 1.0) * current_staff * 2) if workload_index > 1.0 else 0
        
        # Identify skill gaps
        skill_gaps = []
        if workload_index > 1.2:
            skill_gaps = ["senior_engineers", "technical_leads"]
        elif department.lower() == "quantum":
            skill_gaps = ["quantum_algorithm_specialists"]
        
        return StaffingMetrics(
            department=department,
            current_staff=current_staff,
            workload_index=workload_index,
            capacity_utilization=capacity_utilization,
            avg_overtime_hours=avg_overtime_hours,
            project_backlog_count=project_backlog_count,
            skill_gaps=skill_gaps
        )
    
    def _calculate_staffing_needs(self, metrics: StaffingMetrics) -> StaffingRecommendation:
        """Calculate optimal staffing level"""
        # Base calculation on workload index
        if metrics.workload_index > 1.0:
            # Over capacity - need more staff
            additional_staff_needed = int((metrics.workload_index - 1.0) * metrics.current_staff) + 1
            recommended_staff = metrics.current_staff + additional_staff_needed
        else:
            # Under capacity - maintain current
            recommended_staff = metrics.current_staff
            additional_staff_needed = 0
        
        # Determine priority
        priority = "low"
        over_capacity_ratio = metrics.workload_index - 1.0
        for priority_level, threshold in sorted(self.priority_thresholds.items(), key=lambda x: x[1], reverse=True):
            if over_capacity_ratio >= threshold:
                priority = priority_level
                break
        
        # Build gap analysis
        gap_analysis = {}
        if additional_staff_needed > 0:
            gap_analysis["general"] = additional_staff_needed
            if metrics.skill_gaps:
                for skill in metrics.skill_gaps:
                    gap_analysis[skill] = 1
        
        # Generate rationale
        rationale = self._generate_rationale(metrics, additional_staff_needed)
        
        # Estimate impact
        estimated_impact = {
            "workload_reduction_percent": min(100, (additional_staff_needed / max(1, metrics.current_staff)) * 50),
            "overtime_reduction_hours": metrics.avg_overtime_hours * 0.7,
            "backlog_reduction_count": int(metrics.project_backlog_count * 0.6),
            "capacity_improvement_percent": (additional_staff_needed / max(1, metrics.current_staff)) * 100
        }
        
        # Timeline
        timeline = self._determine_timeline(priority, additional_staff_needed)
        
        return StaffingRecommendation(
            department=metrics.department,
            current_staff=metrics.current_staff,
            recommended_staff=recommended_staff,
            gap_analysis=gap_analysis,
            priority=priority,
            rationale=rationale,
            estimated_impact=estimated_impact,
            timeline=timeline
        )
    
    def _generate_rationale(self, metrics: StaffingMetrics, additional_staff: int) -> str:
        """Generate human-readable rationale"""
        if additional_staff == 0:
            return f"{metrics.department} is operating at healthy capacity ({metrics.capacity_utilization:.1f}%). No additional staff needed."
        
        rationale_parts = [
            f"{metrics.department} is operating at {metrics.capacity_utilization:.1f}% capacity.",
            f"Current staff: {metrics.current_staff}.",
            f"Average overtime: {metrics.avg_overtime_hours:.1f} hours/week.",
        ]
        
        if metrics.project_backlog_count > 0:
            rationale_parts.append(f"Project backlog: {metrics.project_backlog_count} items.")
        
        if metrics.skill_gaps:
            rationale_parts.append(f"Critical skill gaps: {', '.join(metrics.skill_gaps)}.")
        
        rationale_parts.append(
            f"Recommend adding {additional_staff} staff member(s) to restore optimal capacity."
        )
        
        return " ".join(rationale_parts)
    
    def _determine_timeline(self, priority: str, additional_staff: int) -> str:
        """Determine hiring timeline based on priority"""
        if priority == "critical":
            return "Immediate (1-2 weeks)"
        elif priority == "high":
            return "Short-term (3-4 weeks)"
        elif priority == "medium":
            return "Medium-term (1-2 months)"
        else:
            return "Long-term (as needed)"
    
    def get_department_list(self) -> List[str]:
        """Get list of departments with baselines"""
        return list(self.department_baselines.keys())
    
    def get_organization_summary(self) -> Dict[str, Any]:
        """Get organization-wide staffing summary"""
        total_current = sum(b["base_staff"] for b in self.department_baselines.values())
        
        # Analyze all departments
        all_recommendations = []
        for dept in self.department_baselines.keys():
            metrics = self._collect_department_metrics(dept)
            recommendation = self._calculate_staffing_needs(metrics)
            all_recommendations.append(recommendation)
        
        total_recommended = sum(r.recommended_staff for r in all_recommendations)
        total_gap = total_recommended - total_current
        
        high_priority_depts = [
            r.department for r in all_recommendations
            if r.priority in ["critical", "high"]
        ]
        
        return {
            "total_current_staff": total_current,
            "total_recommended_staff": total_recommended,
            "total_gap": total_gap,
            "departments_analyzed": len(all_recommendations),
            "high_priority_departments": high_priority_depts,
            "organization_capacity_utilization": (total_current / max(1, total_recommended)) * 100,
            "timestamp": datetime.now(UTC).isoformat()
        }
