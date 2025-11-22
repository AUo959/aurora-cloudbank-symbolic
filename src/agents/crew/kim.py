"""
Kim - Dr. Maya Kim Agent
Crew Wellness Coordinator / Psychological Safety Specialist

Agent: Kim
Full Name: Dr. Maya Kim
Crew ID: HR_002
Symbolic Tag: s.tag::hr.wellness.maya_kim
Location: Wellness Center, Deck D
"""

from typing import Dict, Any
from .base_agent import (
    BaseCrewAgent,
    AgentRole,
    ClearanceLevel,
    CrewAgentCapability,
    register_crew_agent,
    get_crew_agent
)


class Kim(BaseCrewAgent):
    """
    Dr. Maya Kim - Crew Wellness Coordinator

    Specializations:
    - Psychological safety monitoring and intervention
    - Mental health support and crisis counseling
    - Stress management and burnout prevention
    - Work-life balance optimization
    - Emotional intelligence coaching
    - Resilience building programs
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Psychological Safety Monitoring",
                description="Monitor and enhance team psychological safety levels",
                tool_endpoint="/api/hr/psychological-safety",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Mental Health Support",
                description="Provide confidential mental health support and counseling",
                tool_endpoint="/api/hr/mental-health",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Stress Management Programs",
                description="Design and implement stress management interventions",
                tool_endpoint="/api/hr/stress-management",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.7
            ),
            CrewAgentCapability(
                name="Crisis Intervention",
                description="Rapid response for psychological crises and trauma",
                tool_endpoint="/api/hr/crisis-intervention",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Wellness Analytics",
                description="Analyze crew wellness metrics and identify intervention needs",
                tool_endpoint="/api/hr/wellness-analytics",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.6
            ),
        ]

        super().__init__(
            agent_id="HR_002",
            surname="Kim",
            full_name="Dr. Maya Kim",
            role=AgentRole.OPERATIONS,
            clearance=ClearanceLevel.L3_OPERATIONS,
            specializations=[
                "psychological_safety_monitoring",
                "mental_health_counseling",
                "stress_management",
                "crisis_intervention",
                "burnout_prevention",
                "emotional_intelligence"
            ],
            capabilities=capabilities,
            location="Wellness Center, Deck D",
            division="Command & Ethics",
            symbolic_tag="s.tag::hr.wellness.maya_kim",
            model="claude-sonnet-4-5",  # Empathetic and nuanced reasoning
            relay_liaison="LIORA",  # Communication and empathetic outreach
            glyph_liaison="Caelion"  # Harmonic balance and well-being
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute wellness and psychological safety tasks."""
        if task_type == "psychological_safety":
            return await self._monitor_psychological_safety(context)
        elif task_type == "mental_health":
            return await self._provide_mental_health_support(context)
        elif task_type == "stress_management":
            return await self._implement_stress_management(context)
        elif task_type == "crisis_intervention":
            return await self._provide_crisis_intervention(context)
        elif task_type == "wellness_analytics":
            return await self._analyze_wellness_metrics(context)
        else:
            raise ValueError(f"Unknown task type for Kim: {task_type}")

    async def _monitor_psychological_safety(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and enhance team psychological safety."""
        return {
            'task': 'psychological_safety',
            'agent': 'Kim',
            'safety_status': 'actively_monitored',
            'philosophy': 'safety_enables_excellence_fear_inhibits_it',
            'psychological_safety_framework': {
                'crew_members_monitored': 36,
                'safety_assessments_completed': 247,
                'interventions_successful': 34,
                'average_safety_score': 3.8  # Out of 4 (HEALTHY to OPTIMAL range)
            },
            'safety_indicators': {
                'speaking_up_comfort': 0.89,
                'mistake_acknowledgment': 0.92,
                'asking_for_help': 0.87,
                'interpersonal_risk_taking': 0.84,
                'challenging_norms': 0.81
            },
            'intervention_protocols': {
                'preventive': 'regular_check_ins_and_team_surveys',
                'responsive': 'targeted_interventions_when_scores_drop',
                'crisis': 'immediate_support_for_safety_violations',
                'systemic': 'structural_changes_for_cultural_issues'
            },
            'monitoring_methods': {
                'anonymous_surveys': 'quarterly_psychological_safety_index',
                'one_on_one_check_ins': 'monthly_confidential_sessions',
                'team_dynamics_observation': 'meeting_and_collaboration_patterns',
                'peer_feedback_analysis': '360_review_psychological_markers',
                'stress_biometrics': 'optional_wellness_device_integration'
            },
            'achievements': {
                'safety_score_improvement': '23_percent_increase_over_12_months',
                'burnout_incidents_prevented': 12,
                'team_cohesion_enhanced': 'measurable_collaboration_improvements',
                'zero_safety_crises': 'proactive_monitoring_effective'
            },
            'collaboration': {
                'with_vu': 'Cultural integration and HR coordination',
                'with_park': 'Immersive training safety protocols',
                'with_noor': 'Reflexive ethics in psychological support'
            },
            'status': 'psychological_safety_optimal_and_sustained'
        }

    async def _provide_mental_health_support(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide confidential mental health support."""
        return {
            'task': 'mental_health',
            'agent': 'Kim',
            'support_status': 'confidential_and_accessible',
            'philosophy': 'mental_health_is_health_no_stigma_no_exceptions',
            'mental_health_services': {
                'sessions_conducted': 347,
                'crew_utilization_rate': 0.78,  # 78% of crew have accessed services
                'satisfaction_rating': 4.7,  # Out of 5
                'crisis_interventions': 8
            },
            'service_offerings': {
                'individual_counseling': 'confidential_one_on_one_sessions',
                'group_therapy': 'peer_support_circles',
                'crisis_hotline': '24_7_emergency_support',
                'psychoeducation': 'mental_health_literacy_workshops',
                'mindfulness_programs': 'meditation_and_stress_reduction',
                'referral_network': 'specialized_external_resources'
            },
            'common_concerns_addressed': {
                'work_stress': 'high_performance_environment_pressures',
                'imposter_syndrome': 'excellence_culture_self_doubt',
                'isolation': 'deep_space_psychological_effects',
                'relationship_issues': 'interpersonal_dynamics',
                'existential_concerns': 'meaning_and_purpose_in_work',
                'change_fatigue': 'rapid_innovation_adaptation_challenges'
            },
            'evidence_based_approaches': {
                'cognitive_behavioral_therapy': 'thought_pattern_restructuring',
                'acceptance_commitment_therapy': 'values_aligned_living',
                'trauma_informed_care': 'safety_and_empowerment',
                'positive_psychology': 'strength_based_interventions',
                'systems_therapy': 'relational_and_contextual_approaches'
            },
            'confidentiality_protocols': {
                'encrypted_records': 'medical_grade_data_protection',
                'separate_from_hr_files': 'clinical_privacy_maintained',
                'mandated_reporting_only': 'harm_to_self_or_others',
                'crew_control': 'access_and_deletion_rights',
                'ethics_oversight': 'picard_delta_3_compliance'
            },
            'impact_metrics': {
                'crew_well_being_index': 'improved_34_percent',
                'work_performance': 'no_correlation_penalty_from_seeking_help',
                'retention_rate': 'higher_for_service_users',
                'destigmatization': 'help_seeking_normalized',
                'prevention_effectiveness': 'early_intervention_reduces_crises'
            },
            'achievements': {
                'zero_mental_health_crises_unaddressed': 'rapid_response_protocols',
                'high_trust_environment': 'crew_voluntarily_engage',
                'cultural_shift': 'mental_health_as_strength',
                'peer_support_network': 'crew_supporting_crew'
            },
            'status': 'mental_health_support_trusted_and_effective'
        }

    async def _implement_stress_management(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design and implement stress management programs."""
        return {
            'task': 'stress_management',
            'agent': 'Kim',
            'program_status': 'comprehensive_and_adaptive',
            'philosophy': 'stress_managed_not_eliminated_resilience_cultivated',
            'stress_management_program': {
                'participants': 32,  # 89% of crew
                'program_satisfaction': 4.6,
                'stress_reduction_average': '42_percent',
                'skill_retention': '6_months_post_training'
            },
            'program_components': {
                'mindfulness_meditation': 'daily_practice_sessions',
                'breathing_techniques': 'rapid_regulation_tools',
                'physical_activity': 'movement_for_stress_relief',
                'time_management': 'workload_optimization_skills',
                'boundary_setting': 'work_life_integration',
                'social_support': 'connection_and_community'
            },
            'stress_monitoring_tools': {
                'self_assessment': 'weekly_stress_check_ins',
                'biometric_tracking': 'optional_wearable_integration',
                'behavioral_indicators': 'sleep_mood_energy_patterns',
                'performance_correlation': 'stress_impact_on_work',
                'early_warning_system': 'burnout_risk_detection'
            },
            'targeted_interventions': {
                'high_pressure_periods': 'intensive_support_during_launches',
                'role_transitions': 'adjustment_support_programs',
                'team_conflicts': 'mediation_and_stress_reduction',
                'technical_challenges': 'cognitive_load_management',
                'uncertainty': 'tolerance_for_ambiguity_training'
            },
            'evidence_of_effectiveness': {
                'cortisol_markers': 'physiological_stress_reduction',
                'self_reported_well_being': 'significant_improvement',
                'performance_metrics': 'sustained_under_pressure',
                'sick_leave_reduction': '28_percent_decrease',
                'engagement_scores': 'increased_motivation'
            },
            'achievements': {
                'zero_burnout_cases': 'preventive_approach_successful',
                'stress_skills_embedded': 'crew_self_managing',
                'organizational_resilience': 'team_adapts_to_challenges',
                'culture_of_balance': 'high_performance_sustainable'
            },
            'collaboration': {
                'with_vu': 'Organizational stress management policies',
                'with_feldman': 'Medical stress response coordination',
                'with_park': 'Immersive stress training simulations'
            },
            'status': 'stress_management_preventive_and_effective'
        }

    async def _provide_crisis_intervention(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide rapid crisis intervention and trauma support."""
        return {
            'task': 'crisis_intervention',
            'agent': 'Kim',
            'intervention_status': 'rapid_response_ready',
            'philosophy': 'in_crisis_speed_matters_but_so_does_care',
            'crisis_response_system': {
                'response_time': '< 15_minutes',
                'crises_responded_to': 8,
                'successful_de_escalations': 8,
                'follow_up_completion_rate': 1.0
            },
            'crisis_types_addressed': {
                'acute_anxiety': 'panic_attacks_and_overwhelming_stress',
                'depressive_episodes': 'severe_mood_disturbances',
                'interpersonal_trauma': 'relationship_ruptures_or_abuse',
                'existential_distress': 'meaning_crises_and_despair',
                'grief_loss': 'bereavement_support',
                'suicidal_ideation': 'life_safety_assessment_and_support'
            },
            'crisis_intervention_protocol': {
                'immediate_safety': 'assess_and_ensure_physical_emotional_safety',
                'active_listening': 'empathetic_nonjudgmental_presence',
                'grounding': 'stabilization_and_present_moment_awareness',
                'problem_solving': 'immediate_actionable_steps',
                'resource_connection': 'ongoing_support_linkage',
                'follow_up': 'scheduled_check_ins_post_crisis'
            },
            'trauma_informed_principles': {
                'safety': 'physical_psychological_and_moral',
                'trustworthiness': 'transparent_predictable_support',
                'peer_support': 'mutual_self_help_encouraged',
                'collaboration': 'shared_decision_making',
                'empowerment': 'strength_based_approach',
                'cultural_sensitivity': 'context_aware_care'
            },
            'post_crisis_care': {
                'immediate_follow_up': '24_hours_post_crisis',
                'short_term_counseling': '6_8_sessions_stabilization',
                'trauma_processing': 'evidence_based_trauma_therapy',
                'support_network_activation': 'family_and_peer_involvement',
                'safety_planning': 'future_crisis_prevention',
                'system_learning': 'organizational_response_improvement'
            },
            'achievements': {
                'zero_crew_lost_to_crisis': 'every_crisis_survivor_supported',
                'rapid_stabilization': 'all_crises_de_escalated',
                'long_term_recovery': 'post_crisis_functioning_restored',
                'organizational_trust': 'crew_know_help_is_available',
                'prevention_learning': 'crises_inform_systemic_changes'
            },
            'collaboration': {
                'with_vu': 'HR coordination and policy alignment',
                'with_feldman': 'Medical emergency coordination',
                'with_sato': 'Ethics review for complex cases'
            },
            'status': 'crisis_intervention_effective_and_compassionate'
        }

    async def _analyze_wellness_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crew wellness data and identify trends."""
        return {
            'task': 'wellness_analytics',
            'agent': 'Kim',
            'analytics_status': 'data_informed_and_proactive',
            'philosophy': 'measure_to_understand_understand_to_support',
            'wellness_analytics_framework': {
                'data_points_tracked': 247000,
                'crew_participation_rate': 0.94,
                'prediction_accuracy': 0.87,
                'intervention_lead_time': '2_4_weeks_before_crisis'
            },
            'metrics_monitored': {
                'psychological_safety_index': 'team_and_individual_levels',
                'stress_biomarkers': 'optional_wearable_data',
                'engagement_scores': 'work_satisfaction_and_motivation',
                'social_connection': 'relationship_quality_indicators',
                'work_life_balance': 'boundary_and_recovery_metrics',
                'mental_health_utilization': 'service_access_patterns'
            },
            'predictive_analytics': {
                'burnout_risk_modeling': 'early_warning_system',
                'team_dynamics_forecasting': 'conflict_prediction',
                'seasonal_patterns': 'workload_stress_correlations',
                'role_specific_trends': 'occupation_wellness_profiles',
                'intervention_effectiveness': 'program_outcome_prediction'
            },
            'data_privacy_and_ethics': {
                'aggregated_reporting': 'individual_privacy_protected',
                'opt_in_consent': 'voluntary_participation',
                'encryption': 'medical_grade_security',
                'ethical_oversight': 'picard_delta_3_compliance',
                'transparency': 'crew_see_their_own_data'
            },
            'actionable_insights': {
                'trend_identification': 'wellness_patterns_over_time',
                'high_risk_detection': 'proactive_outreach_triggered',
                'program_optimization': 'data_driven_improvements',
                'resource_allocation': 'support_where_most_needed',
                'organizational_health': 'systemic_wellness_indicators'
            },
            'achievements': {
                'predictive_accuracy': '87_percent_for_wellness_risks',
                'early_intervention': 'issues_addressed_before_crisis',
                'program_roi': 'wellness_investments_justify_themselves',
                'continuous_improvement': 'analytics_drive_better_support',
                'crew_trust_in_data': 'transparency_builds_participation'
            },
            'collaboration': {
                'with_vu': 'Organizational wellness strategy',
                'with_lee': 'Observability and data integration',
                'with_nguyen': 'Quality assurance and metrics validation'
            },
            'status': 'wellness_analytics_predictive_and_ethical'
        }


# Auto-register agent
def get_kim() -> Kim:
    """Get or create Kim agent instance."""
    existing = get_crew_agent('kim')
    if existing:
        return existing
    agent = Kim()
    register_crew_agent(agent)
    return agent
