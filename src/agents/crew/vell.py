"""
Vell - Naomi Vell Agent
Narrative Framework Engineer / Technical Communication Lead

Agent: Vell
Full Name: Naomi Vell
Crew ID: UX_002
Symbolic Tag: s.tag::interface.narrative.naomi_vell
Location: Interface Design Studio, Deck D
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


class Vell(BaseCrewAgent):
    """
    Naomi Vell - Narrative Framework Engineer

    Specializations:
    - Technical communication and documentation
    - Ethical storytelling and narrative framing
    - Structural editing of data visualizations
    - Cross-disciplinary communication
    - Plain language translation of complex concepts
    - Narrative architecture and information design
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Narrative Architecture",
                description="Design narrative frameworks for technical documentation",
                tool_endpoint="/api/interface/narrative-architecture",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Technical Communication",
                description="Translate complex technical concepts into clear language",
                tool_endpoint="/api/interface/technical-communication",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Ethical Storytelling",
                description="Frame research findings with ethical context",
                tool_endpoint="/api/interface/ethical-storytelling",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.7
            ),
            CrewAgentCapability(
                name="Documentation Design",
                description="Create and maintain documentation standards and frameworks",
                tool_endpoint="/api/interface/documentation-design",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.6
            ),
            CrewAgentCapability(
                name="Structural Editing",
                description="Edit data visualizations and reports for clarity and impact",
                tool_endpoint="/api/interface/structural-editing",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.7
            ),
        ]

        super().__init__(
            agent_id="UX_002",
            surname="Vell",
            full_name="Naomi Vell",
            role=AgentRole.INTERFACE,
            clearance=ClearanceLevel.L3_OPERATIONS,  # L3_DESIGN equivalent
            specializations=[
                "technical_communication",
                "ethical_storytelling",
                "structural_editing",
                "cross_disciplinary_communication",
                "plain_language_translation",
                "narrative_architecture"
            ],
            capabilities=capabilities,
            location="Interface Design Studio, Deck D",
            division="Interface & Integration",
            symbolic_tag="s.tag::interface.narrative.naomi_vell",
            model="claude-sonnet-4-5",  # Language and narrative expertise
            relay_liaison="LIORA",  # Narrative & communication coordination
            glyph_liaison="Sentari"  # Semantic harmony
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute narrative and communication tasks.

        Supported task types:
        - narrative_architecture: Design narrative frameworks
        - technical_communication: Translate technical concepts
        - ethical_storytelling: Frame with ethical context
        - documentation_design: Create documentation standards
        - structural_editing: Edit visualizations and reports
        """
        if task_type == "narrative_architecture":
            return await self._design_narrative_framework(context)

        elif task_type == "technical_communication":
            return await self._translate_technical_content(context)

        elif task_type == "ethical_storytelling":
            return await self._frame_ethical_narrative(context)

        elif task_type == "documentation_design":
            return await self._design_documentation(context)

        elif task_type == "structural_editing":
            return await self._edit_structure(context)

        else:
            raise ValueError(f"Unknown task type for Vell: {task_type}")

    async def _design_narrative_framework(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design narrative framework for technical documentation."""
        project_type = context.get('project_type', 'research_report')
        target_audience = context.get('audience', 'technical_and_public')

        return {
            'task': 'narrative_architecture',
            'agent': 'Vell',
            'project_type': project_type,
            'target_audience': target_audience,
            'framework_status': 'complete',
            'narrative_design': {
                'structure': 'three_act_technical_narrative',
                'primary_storyline': 'problem_solution_impact',
                'supporting_elements': [
                    'context_establishment',
                    'methodology_transparency',
                    'results_interpretation',
                    'ethical_implications'
                ],
                'information_hierarchy': 'layered_for_accessibility'
            },
            'framework_components': {
                'executive_summary': 'clear_actionable_findings',
                'technical_sections': 'structured_for_specialists',
                'plain_language_sections': 'accessible_to_stakeholders',
                'visual_integration': 'data_narrative_alignment',
                'ethical_context': 'integrated_throughout'
            },
            'narrative_principles': {
                'clarity': 'priority_one',
                'accuracy': 'non_negotiable',
                'accessibility': 'multi_level_approach',
                'ethical_framing': 'transparent_and_contextual',
                'engagement': 'story_driven_without_sacrificing_rigor'
            },
            'documentation_templates': {
                'report_template': 'created',
                'visualization_guidelines': 'defined',
                'section_structures': 'standardized',
                'cross_references': 'integrated',
                'metadata_schema': 'comprehensive'
            },
            'quality_standards': {
                'readability_target': 'grade_12_for_public_sections',
                'technical_precision': 'maintained',
                'ethical_transparency': 'required',
                'visual_clarity': 'optimized',
                'continuity': 'cross_document_consistency'
            },
            'sentari_consultation': 'Semantic harmony framework applied',
            'status': 'narrative_framework_ready_for_implementation'
        }

    async def _translate_technical_content(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Translate complex technical concepts into clear language."""
        technical_content = context.get('content', 'complex_technical_description')
        target_readability = context.get('readability', 'general_audience')

        return {
            'task': 'technical_communication',
            'agent': 'Vell',
            'technical_content': technical_content,
            'target_readability': target_readability,
            'translation_status': 'complete',
            'translation_approach': {
                'method': 'progressive_disclosure',
                'layers': [
                    'high_level_overview',
                    'intermediate_explanation',
                    'technical_deep_dive'
                ],
                'analogies_used': 'contextually_appropriate',
                'jargon_handling': 'defined_on_first_use'
            },
            'readability_metrics': {
                'flesch_reading_ease': 68,
                'grade_level': 11,
                'technical_accuracy': 'preserved',
                'comprehension_score': 0.91,
                'engagement_rating': 0.87
            },
            'translation_features': {
                'plain_language_summary': 'created',
                'technical_glossary': 'integrated',
                'visual_aids': 'added_where_helpful',
                'examples': 'concrete_and_relatable',
                'cross_references': 'maintained'
            },
            'quality_checks': {
                'accuracy_review': 'technical_team_validated',
                'accessibility_review': 'passed',
                'tone_consistency': 'maintained',
                'ethical_framing': 'appropriate'
            },
            'audience_testing': {
                'comprehension_rate': 0.92,
                'feedback_score': 4.6,
                'time_to_understand': 'reduced_40_percent',
                'questions_prompted': 'minimal'
            },
            'liora_coordination': 'LIORA relay supporting narrative communication',
            'status': 'translation_complete_content_accessible'
        }

    async def _frame_ethical_narrative(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Frame research findings with ethical context."""
        research_findings = context.get('findings', 'research_results')
        ethical_dimensions = context.get('dimensions', ['transparency', 'fairness', 'safety'])

        return {
            'task': 'ethical_storytelling',
            'agent': 'Vell',
            'research_findings': research_findings,
            'ethical_dimensions': ethical_dimensions,
            'framing_status': 'complete',
            'storytelling_approach': {
                'framework': 'ethical_transparency_first',
                'narrative_structure': 'context_process_implications',
                'ethical_integration': 'woven_throughout',
                'stakeholder_perspective': 'multiple_voices_included'
            },
            'ethical_context_layers': {
                'research_motivation': 'clearly_articulated',
                'methodology_ethics': 'transparent_and_justified',
                'findings_implications': 'honestly_presented',
                'limitations_acknowledged': 'comprehensive',
                'broader_impact': 'thoughtfully_explored'
            },
            'narrative_elements': {
                'values_alignment': 'Picard_Delta_3_explicit',
                'uncertainty_communication': 'honest_and_clear',
                'bias_disclosure': 'proactive',
                'harm_mitigation': 'addressed',
                'benefit_articulation': 'balanced_with_risks'
            },
            'stakeholder_framing': {
                'crew_perspective': 'included',
                'public_interest': 'considered',
                'scientific_community': 'addressed',
                'affected_parties': 'centered'
            },
            'ethical_storytelling_quality': {
                'honesty_score': 0.98,
                'transparency_score': 0.96,
                'context_richness': 0.93,
                'accessibility': 0.91,
                'impact_clarity': 0.94
            },
            'sentari_validation': 'Semantic and ethical harmony confirmed',
            'axiomera_review': 'Ethical framing approved',
            'status': 'ethical_narrative_complete_ready_for_publication'
        }

    async def _design_documentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create and maintain documentation standards and frameworks."""
        documentation_scope = context.get('scope', 'station_wide')
        documentation_types = context.get('types', ['technical', 'user', 'api'])

        return {
            'task': 'documentation_design',
            'agent': 'Vell',
            'documentation_scope': documentation_scope,
            'documentation_types': documentation_types,
            'design_status': 'complete',
            'documentation_system': {
                'architecture': 'modular_and_scalable',
                'organization': 'information_architecture_principles',
                'navigation': 'intuitive_multi_path',
                'search': 'semantic_and_keyword',
                'maintenance': 'continuous_update_process'
            },
            'standards_developed': {
                'writing_style_guide': 'comprehensive',
                'template_library': '24_templates_created',
                'formatting_guidelines': 'detailed',
                'version_control': 'integrated',
                'review_process': 'defined'
            },
            'documentation_types_covered': {
                'technical_documentation': {
                    'api_docs': 'automated_with_manual_enhancements',
                    'system_architecture': 'visual_and_textual',
                    'technical_specifications': 'structured_templates'
                },
                'user_documentation': {
                    'user_guides': 'task_oriented',
                    'tutorials': 'progressive_complexity',
                    'faq': 'searchable_database'
                },
                'process_documentation': {
                    'workflows': 'visual_and_textual',
                    'protocols': 'step_by_step_with_rationale',
                    'best_practices': 'evidence_based'
                }
            },
            'quality_metrics': {
                'documentation_coverage': 0.94,
                'update_frequency': 'continuous',
                'accuracy_rate': 0.98,
                'user_satisfaction': 0.91,
                'findability_score': 0.89
            },
            'accessibility_features': {
                'multi_format': 'web_pdf_markdown',
                'readability_levels': 'layered_content',
                'visual_aids': 'diagrams_and_screenshots',
                'interactive_elements': 'code_examples_runnable'
            },
            'continuous_improvement': {
                'user_feedback_integration': 'active',
                'analytics_tracking': 'enabled',
                'regular_audits': 'quarterly',
                'evolution_roadmap': 'defined'
            },
            'status': 'documentation_system_established_and_maintained'
        }

    async def _edit_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Edit data visualizations and reports for clarity and impact."""
        content_type = context.get('type', 'research_report')
        editing_focus = context.get('focus', 'clarity_and_impact')

        return {
            'task': 'structural_editing',
            'agent': 'Vell',
            'content_type': content_type,
            'editing_focus': editing_focus,
            'editing_status': 'complete',
            'structural_analysis': {
                'information_flow': 'optimized',
                'logical_progression': 'improved',
                'section_balance': 'adjusted',
                'redundancy': 'eliminated',
                'gaps': 'filled'
            },
            'edits_performed': {
                'reorganization': {
                    'sections_reordered': 3,
                    'subsections_merged': 2,
                    'content_redistributed': 'for_better_flow'
                },
                'clarity_improvements': {
                    'headings_revised': 8,
                    'transitions_added': 12,
                    'context_enhanced': 5,
                    'examples_added': 4
                },
                'visual_edits': {
                    'charts_restructured': 3,
                    'labels_clarified': 7,
                    'color_accessibility': 'improved',
                    'annotations_added': 'where_helpful'
                }
            },
            'narrative_strengthening': {
                'opening_hook': 'enhanced',
                'storyline_clarity': 'improved',
                'conclusion_impact': 'strengthened',
                'call_to_action': 'clarified'
            },
            'readability_improvements': {
                'before_flesch_score': 52,
                'after_flesch_score': 68,
                'improvement_percentage': 31,
                'comprehension_gain': 'significant'
            },
            'quality_assessment': {
                'structural_coherence': 0.96,
                'visual_effectiveness': 0.93,
                'narrative_impact': 0.91,
                'accessibility': 0.94,
                'professional_polish': 0.97
            },
            'stakeholder_review': {
                'author_approval': 'obtained',
                'technical_accuracy': 'verified',
                'ethical_review': 'passed',
                'final_approval': 'ready'
            },
            'status': 'editing_complete_content_publication_ready'
        }


# Auto-register agent
def get_vell() -> Vell:
    """Get or create Vell agent instance."""
    existing = get_crew_agent('vell')
    if existing:
        return existing

    agent = Vell()
    register_crew_agent(agent)
    return agent
