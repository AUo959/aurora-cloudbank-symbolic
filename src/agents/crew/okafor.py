"""
Okafor - Dr. Chioma Okafor Agent
Training & Development Officer / Learning Systems Architect

Agent: Okafor
Full Name: Dr. Chioma Okafor
Crew ID: HR_003
Symbolic Tag: s.tag::hr.training.chioma_okafor
Location: Learning & Development Center, Deck D
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


class Okafor(BaseCrewAgent):
    """
    Dr. Chioma Okafor - Training & Development Officer

    Specializations:
    - Skills development and competency frameworks
    - Knowledge transfer and organizational learning
    - Performance coaching and feedback systems
    - Career pathing and succession planning
    - Technical training program design
    - Mentorship network coordination
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Skills Development Programs",
                description="Design and implement comprehensive skills training programs",
                tool_endpoint="/api/hr/skills-development",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Performance Coaching",
                description="Provide coaching for performance improvement and growth",
                tool_endpoint="/api/hr/performance-coaching",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.7
            ),
            CrewAgentCapability(
                name="Career Development",
                description="Facilitate career pathing and professional growth strategies",
                tool_endpoint="/api/hr/career-development",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Knowledge Transfer",
                description="Coordinate knowledge sharing and organizational learning",
                tool_endpoint="/api/hr/knowledge-transfer",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.6
            ),
            CrewAgentCapability(
                name="Competency Assessment",
                description="Assess technical and soft skill competencies",
                tool_endpoint="/api/hr/competency-assessment",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.7
            ),
        ]

        super().__init__(
            agent_id="HR_003",
            surname="Okafor",
            full_name="Dr. Chioma Okafor",
            role=AgentRole.OPERATIONS,
            clearance=ClearanceLevel.L3_OPERATIONS,
            specializations=[
                "skills_development",
                "performance_coaching",
                "career_pathing",
                "knowledge_management",
                "competency_frameworks",
                "mentorship_coordination"
            ],
            capabilities=capabilities,
            location="Learning & Development Center, Deck D",
            division="Command & Ethics",
            symbolic_tag="s.tag::hr.training.chioma_okafor",
            model="claude-sonnet-4-5",  # Educational design and coaching
            relay_liaison="ARCHY",  # Knowledge architecture coordination
            glyph_liaison="Sentari"  # Truth and knowledge integrity
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute training and development tasks."""
        if task_type == "skills_development":
            return await self._design_skills_programs(context)
        elif task_type == "performance_coaching":
            return await self._provide_coaching(context)
        elif task_type == "career_development":
            return await self._facilitate_career_growth(context)
        elif task_type == "knowledge_transfer":
            return await self._coordinate_knowledge_sharing(context)
        elif task_type == "competency_assessment":
            return await self._assess_competencies(context)
        else:
            raise ValueError(f"Unknown task type for Okafor: {task_type}")

    async def _design_skills_programs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design and implement skills development programs."""
        return {
            'task': 'skills_development',
            'agent': 'Okafor',
            'program_status': 'comprehensive_and_adaptive',
            'philosophy': 'continuous_learning_is_not_optional_its_essential',
            'skills_development_framework': {
                'training_programs_active': 47,
                'crew_participation_rate': 0.94,
                'completion_rate': 0.87,
                'skill_transfer_to_work': 0.82
            },
            'program_categories': {
                'technical_skills': 'symbolic_ai_quantum_systems_development',
                'leadership_development': 'team_management_and_decision_making',
                'communication': 'collaboration_presentation_writing',
                'ethics_compliance': 'picard_delta_3_protocol_training',
                'innovation_methods': 'creative_problem_solving_design_thinking',
                'safety_protocols': 'operational_safety_and_emergency_response'
            },
            'delivery_methods': {
                'workshops': 'hands_on_interactive_learning',
                'e_learning': 'self_paced_online_modules',
                'mentorship': 'one_on_one_expert_guidance',
                'simulations': 'immersive_practice_environments',
                'cohort_programs': 'peer_learning_communities',
                'micro_learning': 'bite_sized_just_in_time_training'
            },
            'competency_framework': {
                'technical_competencies': 'role_specific_technical_skills',
                'core_competencies': 'organization_wide_foundational_skills',
                'leadership_competencies': 'management_and_strategic_thinking',
                'ethical_competencies': 'moral_reasoning_and_integrity',
                'innovation_competencies': 'creativity_and_adaptability',
                'collaboration_competencies': 'teamwork_and_communication'
            },
            'certification_pathways': {
                'internal_certifications': 'aurora_specific_credentials',
                'external_certifications': 'industry_recognized_qualifications',
                'micro_credentials': 'skill_specific_badges',
                'mastery_levels': 'novice_to_expert_progression',
                'recertification': 'continuous_competency_validation'
            },
            'effectiveness_metrics': {
                'skill_acquisition': 'pre_post_assessment_gains',
                'on_the_job_application': 'behavior_change_observed',
                'business_impact': 'performance_improvement_tied_to_training',
                'learner_satisfaction': '4_6_out_of_5_average',
                'roi': 'training_investment_returns_measured'
            },
            'achievements': {
                'skill_gaps_closed': '89_percent_of_identified_gaps_addressed',
                'cross_skilling_success': '67_crew_members_expanded_capabilities',
                'leadership_pipeline': 'succession_planning_robust',
                'innovation_capacity': 'measurable_increase_in_creative_output',
                'retention_improvement': 'development_opportunities_retain_talent'
            },
            'collaboration': {
                'with_vu': 'Onboarding and talent development strategy',
                'with_park': 'Immersive VR/AR training experiences',
                'with_velin': 'Simulation-based learning programs'
            },
            'status': 'skills_development_systematic_and_impactful'
        }

    async def _provide_coaching(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide performance coaching and feedback."""
        return {
            'task': 'performance_coaching',
            'agent': 'Okafor',
            'coaching_status': 'growth_oriented',
            'philosophy': 'feedback_is_a_gift_coaching_unwraps_potential',
            'coaching_framework': {
                'active_coaching_relationships': 28,
                'coaching_sessions_per_quarter': 247,
                'goal_achievement_rate': 0.84,
                'coachee_satisfaction': 4.7
            },
            'coaching_approaches': {
                'strengths_based': 'leverage_natural_talents',
                'goal_oriented': 'clear_objectives_and_action_plans',
                'growth_mindset': 'challenges_as_learning_opportunities',
                'reflective_practice': 'self_awareness_and_meta_cognition',
                'accountability_partnership': 'supportive_challenge',
                'solution_focused': 'future_oriented_problem_solving'
            },
            'coaching_areas': {
                'performance_improvement': 'close_skill_or_behavior_gaps',
                'leadership_development': 'management_capabilities_enhancement',
                'career_transitions': 'role_change_support',
                'conflict_resolution': 'interpersonal_effectiveness',
                'innovation_mindset': 'creative_thinking_cultivation',
                'work_life_integration': 'sustainable_high_performance'
            },
            'feedback_systems': {
                'real_time_feedback': 'continuous_micro_feedback_loops',
                'quarterly_reviews': 'formal_performance_discussions',
                '360_feedback': 'multi_rater_comprehensive_input',
                'peer_feedback': 'colleague_to_colleague_insights',
                'self_assessment': 'reflective_self_evaluation',
                'upward_feedback': 'team_to_leader_input'
            },
            'coaching_tools': {
                'goal_setting': 'SMART_and_OKR_frameworks',
                'action_planning': 'step_by_step_development_plans',
                'progress_tracking': 'milestone_and_metric_monitoring',
                'resource_connection': 'training_and_support_linkage',
                'reflection_prompts': 'critical_thinking_questions',
                'assessment_instruments': 'validated_psychometric_tools'
            },
            'impact_evidence': {
                'performance_gains': '32_percent_average_improvement',
                'promotion_readiness': 'coaching_accelerates_advancement',
                'retention_of_coached': 'higher_than_non_coached_peers',
                'team_effectiveness': 'coaching_ripples_to_teams',
                'organizational_capability': 'aggregate_performance_lift'
            },
            'achievements': {
                'coaching_culture': 'growth_conversations_normalized',
                'high_performer_development': 'top_talent_accelerated',
                'struggling_performer_recovery': 'turnaround_success_rate_high',
                'leadership_bench_strength': 'coaching_builds_pipeline',
                'innovation_mindset_spread': 'creative_confidence_grown'
            },
            'collaboration': {
                'with_vu': 'Talent development and succession planning',
                'with_kim': 'Well-being integrated into performance',
                'with_thorne': 'Leadership coaching for command staff'
            },
            'status': 'coaching_transformative_and_developmental'
        }

    async def _facilitate_career_growth(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Facilitate career pathing and professional development."""
        return {
            'task': 'career_development',
            'agent': 'Okafor',
            'development_status': 'intentional_and_supported',
            'philosophy': 'careers_are_journeys_not_destinations_we_navigate_together',
            'career_development_framework': {
                'career_conversations': 247,
                'career_plans_active': 34,
                'internal_mobility_rate': 0.23,  # 23% moved roles in last 2 years
                'promotion_readiness_pipeline': 12
            },
            'career_pathing_components': {
                'self_assessment': 'interests_values_strengths_exploration',
                'opportunity_mapping': 'internal_roles_and_pathways',
                'skill_gap_analysis': 'development_needs_identification',
                'action_planning': 'step_by_step_career_roadmap',
                'networking': 'internal_connections_and_mentorship',
                'progress_review': 'regular_career_check_ins'
            },
            'career_pathways': {
                'technical_track': 'individual_contributor_to_principal',
                'management_track': 'team_lead_to_director',
                'specialist_track': 'deep_expertise_development',
                'cross_functional': 'lateral_moves_for_breadth',
                'project_leadership': 'temporary_leadership_opportunities',
                'innovation_track': 'research_and_development_focus'
            },
            'succession_planning': {
                'key_roles_identified': 18,
                'successors_in_pipeline': 34,
                'development_plans_active': 34,
                'readiness_assessment': 'competency_and_performance_based',
                'acceleration_programs': 'high_potential_fast_tracking',
                'knowledge_transfer': 'succession_continuity_planning'
            },
            'internal_mobility': {
                'open_roles_posted_internally': 'transparency_in_opportunities',
                'cross_department_moves': 'encouraged_and_facilitated',
                'trial_assignments': 'low_risk_exploration',
                'skill_portability': 'transferable_competencies_recognized',
                'mobility_as_development': 'moves_seen_as_growth'
            },
            'mentorship_program': {
                'active_mentorship_pairs': 28,
                'mentor_training': 'effective_mentoring_practices',
                'mentee_support': 'goal_setting_and_reflection_tools',
                'matching_process': 'intentional_pairing_for_development',
                'program_evaluation': 'outcomes_and_satisfaction_measured'
            },
            'achievements': {
                'retention_of_high_potentials': '96_percent',
                'promotion_from_within': '78_percent_of_leadership_roles',
                'career_satisfaction': 'significantly_improved',
                'internal_mobility': 'healthy_movement_across_divisions',
                'succession_readiness': 'no_critical_gaps_in_pipeline'
            },
            'collaboration': {
                'with_vu': 'Talent strategy and workforce planning',
                'with_thorne': 'Leadership development and succession',
                'with_shepard': 'Operational career opportunities'
            },
            'status': 'career_development_strategic_and_empowering'
        }

    async def _coordinate_knowledge_sharing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate knowledge transfer and organizational learning."""
        return {
            'task': 'knowledge_transfer',
            'agent': 'Okafor',
            'knowledge_status': 'captured_and_accessible',
            'philosophy': 'knowledge_shared_multiplies_knowledge_hoarded_stagnates',
            'knowledge_management_system': {
                'knowledge_artifacts': 1247,
                'contributors': 34,
                'access_rate': '94_percent_of_crew',
                'knowledge_application': 'measurable_work_improvements'
            },
            'knowledge_capture_methods': {
                'documentation': 'structured_technical_write_ups',
                'video_tutorials': 'visual_how_to_demonstrations',
                'brown_bag_sessions': 'informal_peer_learning_lunches',
                'communities_of_practice': 'expert_networks_by_domain',
                'post_mortems': 'project_learning_debriefs',
                'lessons_learned_database': 'searchable_experience_repository'
            },
            'knowledge_domains': {
                'technical_expertise': 'ai_quantum_symbolic_system_knowledge',
                'process_knowledge': 'how_we_work_best_practices',
                'project_knowledge': 'what_we_learned_case_studies',
                'ethical_knowledge': 'moral_reasoning_and_precedents',
                'relational_knowledge': 'who_knows_what_expert_directory',
                'cultural_knowledge': 'organizational_norms_and_values'
            },
            'knowledge_sharing_platforms': {
                'internal_wiki': 'collaborative_documentation',
                'video_library': 'recorded_presentations_and_tutorials',
                'discussion_forums': 'q_and_a_and_peer_support',
                'mentorship_program': 'one_on_one_knowledge_transfer',
                'lunch_and_learns': 'regular_knowledge_sharing_events',
                'expert_speaker_series': 'external_knowledge_infusion'
            },
            'critical_knowledge_preservation': {
                'expert_interviews': 'capture_tacit_knowledge',
                'shadowing_programs': 'observational_learning',
                'knowledge_handoffs': 'role_transition_protocols',
                'redundancy': 'multiple_people_know_critical_areas',
                'succession_knowledge_transfer': 'planned_knowledge_transition'
            },
            'learning_culture_indicators': {
                'curiosity': 'questions_welcomed_and_encouraged',
                'experimentation': 'safe_to_try_and_fail',
                'reflection': 'time_for_learning_from_experience',
                'collaboration': 'knowledge_sharing_rewarded',
                'growth_mindset': 'belief_in_continuous_improvement'
            },
            'achievements': {
                'knowledge_loss_prevention': 'zero_critical_knowledge_gaps',
                'onboarding_acceleration': 'new_hires_productive_faster',
                'problem_solving_efficiency': 'dont_reinvent_the_wheel',
                'innovation_from_synthesis': 'new_ideas_from_combined_knowledge',
                'organizational_memory': 'collective_intelligence_preserved'
            },
            'collaboration': {
                'with_vu': 'Onboarding knowledge transfer',
                'with_velin': 'Simulation-based knowledge encoding',
                'with_roberts': 'LLM-based knowledge retrieval systems'
            },
            'status': 'knowledge_management_strategic_asset'
        }

    async def _assess_competencies(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess technical and soft skill competencies."""
        return {
            'task': 'competency_assessment',
            'agent': 'Okafor',
            'assessment_status': 'evidence_based_and_developmental',
            'philosophy': 'assess_to_develop_not_to_judge_measurement_enables_growth',
            'competency_assessment_framework': {
                'assessments_conducted': 347,
                'competency_areas_tracked': 89,
                'assessment_accuracy': 0.91,
                'development_plans_created': 247
            },
            'assessment_methods': {
                'self_assessment': 'reflective_competency_self_rating',
                'manager_assessment': 'observed_performance_evaluation',
                'peer_assessment': 'collaborative_competency_feedback',
                '360_assessment': 'multi_rater_comprehensive_view',
                'skills_testing': 'technical_proficiency_demonstrations',
                'work_samples': 'portfolio_based_evaluation'
            },
            'competency_categories': {
                'technical_skills': 'domain_specific_expertise',
                'problem_solving': 'analytical_and_creative_thinking',
                'communication': 'written_verbal_and_presentation',
                'collaboration': 'teamwork_and_interpersonal_effectiveness',
                'leadership': 'influence_and_decision_making',
                'adaptability': 'change_resilience_and_learning_agility',
                'ethics_integrity': 'moral_reasoning_and_trustworthiness',
                'innovation': 'creativity_and_continuous_improvement'
            },
            'competency_levels': {
                'novice': 'learning_foundational_skills',
                'proficient': 'independently_competent',
                'advanced': 'expertise_and_mentoring_others',
                'expert': 'thought_leadership_and_innovation',
                'master': 'recognized_authority_in_field'
            },
            'assessment_applications': {
                'hiring_decisions': 'candidate_competency_fit',
                'development_planning': 'identify_growth_opportunities',
                'succession_planning': 'readiness_for_advancement',
                'performance_reviews': 'evidence_based_evaluations',
                'team_composition': 'complementary_skill_balancing',
                'training_needs_analysis': 'aggregate_skill_gap_identification'
            },
            'ethical_assessment_principles': {
                'fairness': 'consistent_standards_applied',
                'transparency': 'criteria_and_process_clear',
                'development_focus': 'growth_not_punishment',
                'confidentiality': 'results_handled_sensitively',
                'bias_mitigation': 'structured_evaluations_reduce_bias'
            },
            'achievements': {
                'objective_performance_data': 'assessment_reduces_subjectivity',
                'targeted_development': 'personalized_growth_plans',
                'talent_insights': 'organization_competency_mapping',
                'fair_advancement': 'merit_based_promotions',
                'capability_forecasting': 'future_readiness_prediction'
            },
            'collaboration': {
                'with_vu': 'Talent assessment and development strategy',
                'with_nguyen': 'Quality assurance for assessment rigor',
                'with_thorne': 'Leadership competency framework'
            },
            'status': 'competency_assessment_rigorous_and_developmental'
        }


# Auto-register agent
def get_okafor() -> Okafor:
    """Get or create Okafor agent instance."""
    existing = get_crew_agent('okafor')
    if existing:
        return existing
    agent = Okafor()
    register_crew_agent(agent)
    return agent
