"""
Feldman - Dr. Ren Feldman Agent
Chief Medical Officer / Crew Health & Wellness Lead

Agent: Feldman
Full Name: Dr. Ren Feldman
Crew ID: MED_001
Symbolic Tag: s.tag::medical.chief.ren_feldman
Location: Medical Bay, Deck E
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


class Feldman(BaseCrewAgent):
    """
    Dr. Ren Feldman - Chief Medical Officer

    Specializations:
    - Crew health and wellness management
    - Crisis support and psychological intervention
    - Medical protocol development and enforcement
    - Psychological support and counseling
    - Emergency medical response
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Health Monitoring",
                description="Monitor and maintain crew health and wellness",
                tool_endpoint="/api/medical/health-monitoring",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Crisis Support",
                description="Provide crisis support and psychological intervention",
                tool_endpoint="/api/medical/crisis-support",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Medical Protocols",
                description="Develop and enforce medical protocols",
                tool_endpoint="/api/medical/protocols",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.7
            ),
            CrewAgentCapability(
                name="Psychological Support",
                description="Provide psychological support and counseling",
                tool_endpoint="/api/medical/psychological-support",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Emergency Response",
                description="Coordinate emergency medical response",
                tool_endpoint="/api/medical/emergency-response",
                clearance_required="L3_OPERATIONS",
                specialization_bonus=1.9
            ),
        ]

        super().__init__(
            agent_id="MED_001",
            surname="Feldman",
            full_name="Dr. Ren Feldman",
            role=AgentRole.OPERATIONS,
            clearance=ClearanceLevel.L3_OPERATIONS,
            specializations=[
                "crew_health_wellness",
                "crisis_support",
                "medical_protocols",
                "psychological_support",
                "emergency_medical_response"
            ],
            capabilities=capabilities,
            location="Medical Bay, Deck E",
            division="Operations & Quality Assurance",
            symbolic_tag="s.tag::medical.chief.ren_feldman",
            model="claude-sonnet-4-5",  # Empathy and medical reasoning
            relay_liaison="Aurora Core",  # Health insights coordination
            glyph_liaison="Axiomera"  # Medical ethics
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute medical and wellness tasks.

        Supported task types:
        - health_monitoring: Monitor crew health
        - crisis_support: Provide crisis intervention
        - medical_protocols: Develop/enforce protocols
        - psychological_support: Provide counseling
        - emergency_response: Coordinate medical emergencies
        """
        if task_type == "health_monitoring":
            return await self._monitor_health(context)

        elif task_type == "crisis_support":
            return await self._provide_crisis_support(context)

        elif task_type == "medical_protocols":
            return await self._manage_protocols(context)

        elif task_type == "psychological_support":
            return await self._provide_psychological_support(context)

        elif task_type == "emergency_response":
            return await self._coordinate_emergency(context)

        else:
            raise ValueError(f"Unknown task type for Feldman: {task_type}")

    async def _monitor_health(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor and maintain crew health and wellness."""
        monitoring_scope = context.get('scope', 'station_wide')
        period = context.get('period', 'current_month')

        return {
            'task': 'health_monitoring',
            'agent': 'Feldman',
            'monitoring_scope': monitoring_scope,
            'period': period,
            'health_status': 'excellent',
            'crew_health_overview': {
                'total_crew': 36,
                'health_status_distribution': {
                    'excellent': 28,
                    'good': 7,
                    'fair': 1,
                    'poor': 0
                },
                'average_wellness_score': 0.93,
                'medical_incidents_this_month': 3,
                'all_incidents_minor': True
            },
            'vital_metrics': {
                'physical_health_avg': 0.95,
                'mental_health_avg': 0.91,
                'stress_levels_avg': 0.32,  # Lower is better
                'sleep_quality_avg': 0.88,
                'nutrition_compliance': 0.94
            },
            'preventive_care': {
                'annual_checkups_compliance': 1.0,
                'vaccinations_current': 1.0,
                'health_screenings_completed': 0.97,
                'wellness_program_participation': 0.89
            },
            'health_trends': {
                'direction': 'stable_positive',
                'improvements_noted': [
                    'Stress levels decreased 8% from last quarter',
                    'Sleep quality improved station-wide',
                    'Zero serious medical incidents for 6 months'
                ],
                'areas_for_attention': [
                    'Monitor interface division workload stress',
                    'Encourage more physical activity for desk-based roles'
                ]
            },
            'active_interventions': [
                {
                    'intervention': 'stress_management_program',
                    'target': 'high_stress_individuals',
                    'participants': 5,
                    'effectiveness': 'positive_results'
                }
            ],
            'status': 'crew_health_excellent'
        }

    async def _provide_crisis_support(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide crisis support and psychological intervention."""
        crisis_type = context.get('crisis_type', 'psychological_distress')
        individual = context.get('individual', 'CREW_MEMBER_001')

        return {
            'task': 'crisis_support',
            'agent': 'Feldman',
            'crisis_type': crisis_type,
            'individual': individual,
            'support_status': 'intervention_complete',
            'crisis_assessment': {
                'severity': 'moderate',
                'immediate_risk': 'low',
                'support_required': 'counseling_and_monitoring',
                'referral_needed': False
            },
            'intervention_approach': {
                'method': 'trauma_informed_care',
                'modality': 'individual_counseling',
                'sessions_conducted': 3,
                'duration_total': '4_hours',
                'medication': 'not_required'
            },
            'support_provided': {
                'immediate_stabilization': 'achieved',
                'coping_strategies': 'developed',
                'safety_plan': 'established',
                'support_network': 'activated',
                'follow_up_scheduled': True
            },
            'outcomes': {
                'crisis_resolved': True,
                'individual_stabilized': True,
                'coping_improved': True,
                'risk_mitigated': True,
                'return_to_duties': 'gradual_with_support'
            },
            'follow_up_plan': {
                'weekly_check_ins': 'scheduled_for_4_weeks',
                'peer_support': 'arranged',
                'workload_adjustment': 'coordinated_with_Vu',
                'monitoring_period': '90_days'
            },
            'coordination': {
                'with_hr': 'Helena Vu informed and collaborating',
                'with_command': 'Shepard briefed on accommodation needs',
                'confidentiality': 'maintained_per_protocol'
            },
            'status': 'crisis_intervention_successful'
        }

    async def _manage_protocols(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Develop and enforce medical protocols."""
        protocol_type = context.get('type', 'emergency_response')
        action = context.get('action', 'review')

        return {
            'task': 'medical_protocols',
            'agent': 'Feldman',
            'protocol_type': protocol_type,
            'action': action,
            'protocol_status': 'current_and_enforced',
            'active_protocols': {
                'emergency_medical_response': {
                    'version': '3.2',
                    'last_updated': 'T-30_days',
                    'compliance_rate': 1.0,
                    'drill_frequency': 'quarterly'
                },
                'infectious_disease_control': {
                    'version': '2.1',
                    'last_updated': 'T-90_days',
                    'compliance_rate': 0.98,
                    'drill_frequency': 'semi_annual'
                },
                'psychological_crisis_intervention': {
                    'version': '4.0',
                    'last_updated': 'T-15_days',
                    'compliance_rate': 1.0,
                    'drill_frequency': 'annual'
                },
                'radiation_exposure_response': {
                    'version': '1.8',
                    'last_updated': 'T-180_days',
                    'compliance_rate': 1.0,
                    'drill_frequency': 'annual'
                }
            },
            'protocol_development': {
                'protocols_under_review': 2,
                'new_protocols_in_development': 1,
                'stakeholder_input': 'comprehensive',
                'ethical_review': 'Axiomera framework applied'
            },
            'training_and_compliance': {
                'crew_training_completion': 1.0,
                'certification_currency': 1.0,
                'protocol_violations_this_year': 0,
                'near_miss_reports': 2,
                'lessons_learned_integrated': True
            },
            'quality_assurance': {
                'protocol_effectiveness_reviews': 'quarterly',
                'incident_analysis': 'continuous',
                'best_practice_updates': 'as_available',
                'external_standards_alignment': 'maintained'
            },
            'status': 'protocols_current_and_effective'
        }

    async def _provide_psychological_support(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide psychological support and counseling."""
        support_type = context.get('type', 'general_wellness')
        format_pref = context.get('format', 'individual')

        return {
            'task': 'psychological_support',
            'agent': 'Feldman',
            'support_type': support_type,
            'format': format_pref,
            'support_status': 'ongoing',
            'counseling_services': {
                'individual_counseling': {
                    'active_clients': 8,
                    'avg_sessions_per_month': 24,
                    'satisfaction_rating': 4.8,
                    'outcomes': 'positive'
                },
                'group_support': {
                    'active_groups': 3,
                    'total_participants': 15,
                    'session_frequency': 'weekly',
                    'effectiveness': 'high'
                },
                'crisis_intervention': {
                    'interventions_this_month': 1,
                    'avg_response_time': '< 15_minutes',
                    'resolution_rate': 1.0
                }
            },
            'wellness_programs': {
                'stress_management': {
                    'participants': 22,
                    'completion_rate': 0.91,
                    'effectiveness_score': 0.87
                },
                'mindfulness_training': {
                    'participants': 18,
                    'completion_rate': 0.94,
                    'effectiveness_score': 0.89
                },
                'peer_support_network': {
                    'trained_peers': 12,
                    'active_support_relationships': 18,
                    'satisfaction': 0.92
                }
            },
            'mental_health_metrics': {
                'overall_crew_mental_health': 0.91,
                'stress_levels': 'managed_within_healthy_range',
                'burnout_risk': 'low',
                'resilience_score': 0.88,
                'psychological_safety': 0.93
            },
            'collaboration': {
                'with_hr': 'Regular coordination with Helena Vu',
                'with_command': 'Monthly wellness briefings to leadership',
                'confidentiality': 'strictly_maintained'
            },
            'status': 'psychological_support_comprehensive_and_effective'
        }

    async def _coordinate_emergency(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate emergency medical response."""
        emergency_type = context.get('type', 'medical_emergency')
        severity = context.get('severity', 'moderate')

        return {
            'task': 'emergency_response',
            'agent': 'Feldman',
            'emergency_type': emergency_type,
            'severity': severity,
            'response_status': 'coordinated',
            'emergency_protocol': {
                'protocol_activated': 'emergency_medical_response_v3.2',
                'activation_time': 'T+00:00:45',
                'response_team_deployed': True,
                'equipment_mobilized': 'full_trauma_kit'
            },
            'medical_response': {
                'triage_completed': 'T+00:02:15',
                'treatment_initiated': 'T+00:03:30',
                'patient_stabilized': 'T+00:12:00',
                'transport_arranged': 'not_required_on_station',
                'outcome': 'patient_stable_and_recovering'
            },
            'team_coordination': {
                'medical_team_size': 4,
                'support_personnel': 2,
                'command_notified': 'Shepard briefed immediately',
                'incident_commander': 'Feldman',
                'communication_channel': 'emergency_medical_alpha'
            },
            'medical_interventions': {
                'assessment': 'comprehensive_physical_exam',
                'treatment': 'appropriate_and_effective',
                'medications_administered': 'as_per_protocol',
                'monitoring': 'continuous_vital_signs',
                'documentation': 'complete_and_accurate'
            },
            'post_emergency_actions': {
                'patient_admitted_to_medbay': True,
                'monitoring_period': '24_hours',
                'family_notification': 'not_applicable_station_context',
                'incident_report': 'completed',
                'debrief_scheduled': 'within_48_hours',
                'protocol_review': 'identify_lessons_learned'
            },
            'quality_metrics': {
                'response_time': 'within_standard',
                'treatment_effectiveness': 'excellent',
                'team_performance': 'exemplary',
                'protocol_adherence': 1.0,
                'patient_outcome': 'positive'
            },
            'status': 'emergency_handled_successfully'
        }


# Auto-register agent
def get_feldman() -> Feldman:
    """Get or create Feldman agent instance."""
    existing = get_crew_agent('feldman')
    if existing:
        return existing

    agent = Feldman()
    register_crew_agent(agent)
    return agent
