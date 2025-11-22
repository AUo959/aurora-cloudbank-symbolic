"""
Halden - Keira Halden Agent
Lead Visual Concept Designer / Visual Identity Architect

Agent: Halden
Full Name: Keira Halden
Crew ID: UX_006
Symbolic Tag: s.tag::interface.visual.keira_halden
Location: Visual Design Studio, Deck C
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


class Halden(BaseCrewAgent):
    """
    Keira Halden - Lead Visual Concept Designer

    Specializations:
    - Design direction and visual systems coordination
    - Human-perception research and visual psychology
    - Visual ethics and truthful representation
    - Concept art and prototyping
    - Brand identity and visual governance
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Visual Identity Design",
                description="Design comprehensive visual identity and brand systems",
                tool_endpoint="/api/interface/visual-identity",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Design Systems",
                description="Coordinate design systems and visual standards",
                tool_endpoint="/api/interface/design-systems",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Visual Ethics",
                description="Ensure visual ethics and truthful representation",
                tool_endpoint="/api/interface/visual-ethics",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Concept Art",
                description="Produce concept art and visual prototypes",
                tool_endpoint="/api/interface/concept-art",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.7
            ),
            CrewAgentCapability(
                name="Visual Governance",
                description="Govern visual standards and brand coherence",
                tool_endpoint="/api/interface/visual-governance",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.8
            ),
        ]

        super().__init__(
            agent_id="UX_006",
            surname="Halden",
            full_name="Keira Halden",
            role=AgentRole.INTERFACE,
            clearance=ClearanceLevel.L3_TECHNICAL,  # L3_DESIGN equivalent
            specializations=[
                "design_direction",
                "visual_systems_coordination",
                "visual_ethics",
                "concept_art_production",
                "brand_identity_governance"
            ],
            capabilities=capabilities,
            location="Visual Design Studio, Deck C",
            division="Interface & Aesthetics",
            symbolic_tag="s.tag::interface.visual.keira_halden",
            model="claude-sonnet-4-5",  # Visual and ethical reasoning
            relay_liaison="LIORA",  # Communication and public interface
            glyph_liaison="Axiomera"  # Ethical visual communication
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute visual identity and design system tasks."""
        if task_type == "visual_identity":
            return await self._design_visual_identity(context)
        elif task_type == "design_systems":
            return await self._coordinate_design_systems(context)
        elif task_type == "visual_ethics":
            return await self._ensure_visual_ethics(context)
        elif task_type == "concept_art":
            return await self._produce_concept_art(context)
        elif task_type == "visual_governance":
            return await self._govern_visual_standards(context)
        else:
            raise ValueError(f"Unknown task type for Halden: {task_type}")

    async def _design_visual_identity(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design comprehensive visual identity and brand systems."""
        return {
            'task': 'visual_identity',
            'agent': 'Halden',
            'identity_status': 'coherent',
            'philosophy': 'if_image_conceals_it_has_failed',
            'visual_identity_framework': {
                'identity_touchpoints': 247,
                'brand_coherence': 0.97,
                'transparency_score': 1.0,
                'recognition_rate': 'excellent'
            },
            'identity_components': {
                'logo_system': 'primary_secondary_marks',
                'color_palette': 'semantic_and_accessible',
                'typography': 'hierarchy_and_legibility',
                'iconography': 'consistent_visual_language',
                'illustration_style': 'technical_and_truthful',
                'motion_language': 'purposeful_animation'
            },
            'brand_values_expressed': {
                'transparency': 'visual_honesty_and_clarity',
                'precision': 'technical_accuracy_visible',
                'ethics': 'responsibility_in_every_pixel',
                'accessibility': 'inclusive_by_design',
                'intelligence': 'sophisticated_not_complex'
            },
            'design_principles': {
                'clarity_over_cleverness': 'function_first',
                'honesty_over_persuasion': 'inform_not_manipulate',
                'accessibility_over_aesthetics': 'usable_then_beautiful',
                'consistency_over_novelty': 'predictable_experience',
                'simplicity_over_ornamentation': 'essential_only'
            },
            'identity_applications': {
                'digital_interfaces': 'ui_patterns_and_components',
                'physical_spaces': 'environmental_branding',
                'publications': 'scientific_communication_design',
                'presentations': 'slide_templates_and_assets',
                'merchandise': 'crew_and_public_materials'
            },
            'brand_coherence_metrics': {
                'visual_consistency': '97_percent_across_touchpoints',
                'recognition_time': '< 2_seconds',
                'brand_recall': 'excellent',
                'message_clarity': 'values_clearly_communicated',
                'differentiation': 'distinctive_in_field'
            },
            'achievements': {
                'orion_station_identity': 'recognized_globally',
                'transparency_through_design': 'values_visible',
                'identity_coherence': 'over_200_touchpoints',
                'public_trust': 'visual_credibility_established'
            },
            'status': 'visual_identity_coherent_and_transparent'
        }

    async def _coordinate_design_systems(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate design systems and visual standards."""
        return {
            'task': 'design_systems',
            'agent': 'Halden',
            'system_status': 'comprehensive',
            'philosophy': 'systems_enable_consistency_liberate_creativity',
            'design_system_framework': {
                'component_library_size': 347,
                'design_tokens': 1247,
                'documentation_pages': 89,
                'adoption_rate': '> 95_percent'
            },
            'system_components': {
                'foundations': 'color_typography_spacing_elevation',
                'components': 'buttons_forms_navigation_feedback',
                'patterns': 'layouts_flows_templates',
                'content': 'voice_tone_writing_guidelines',
                'resources': 'assets_templates_tools'
            },
            'design_tokens': {
                'color_tokens': 'semantic_naming_and_values',
                'spacing_tokens': '4px_grid_system',
                'typography_tokens': 'scale_and_hierarchy',
                'motion_tokens': 'timing_and_easing',
                'elevation_tokens': 'depth_and_layering'
            },
            'documentation': {
                'usage_guidelines': 'when_and_how_to_use',
                'code_examples': 'implementation_references',
                'accessibility_notes': 'inclusive_design_requirements',
                'visual_examples': 'do_and_dont_comparisons',
                'version_history': 'change_log_and_migration'
            },
            'governance_model': {
                'contribution_process': 'propose_review_approve',
                'versioning': 'semantic_versioning',
                'deprecation': 'gradual_with_alternatives',
                'communication': 'change_announcements',
                'training': 'onboarding_and_workshops'
            },
            'system_benefits': {
                'consistency': 'unified_experience',
                'efficiency': 'design_faster_build_faster',
                'quality': 'best_practices_baked_in',
                'scalability': 'grows_with_needs',
                'collaboration': 'shared_language'
            },
            'adoption_metrics': {
                'designer_adoption': '> 95_percent',
                'developer_adoption': '> 92_percent',
                'consistency_score': 'improved_87_percent',
                'design_velocity': 'increased_64_percent',
                'quality_issues': 'reduced_73_percent'
            },
            'achievements': {
                'comprehensive_system': 'foundations_to_patterns',
                'high_adoption': 'organization_standard',
                'living_documentation': 'always_current',
                'design_at_scale': 'consistency_without_rigidity'
            },
            'collaboration': {
                'with_kyros': 'UX patterns and interaction standards',
                'with_suresh': 'Visualization component guidelines',
                'with_vatra': 'Color system tokens and usage'
            },
            'status': 'design_systems_comprehensive_and_adopted'
        }

    async def _ensure_visual_ethics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure visual ethics and truthful representation."""
        return {
            'task': 'visual_ethics',
            'agent': 'Halden',
            'ethics_status': 'uncompromised',
            'philosophy': 'every_visual_decision_is_ethical_choice',
            'visual_ethics_framework': {
                'ethics_guidelines_established': 23,
                'ethics_reviews_performed': 247,
                'violations_prevented': 17,
                'transparency_score': 1.0
            },
            'ethics_principles': {
                'truthfulness': 'represent_reality_honestly',
                'transparency': 'methods_and_intent_disclosed',
                'accessibility': 'inclusive_for_all_abilities',
                'respect': 'dignity_in_representation',
                'responsibility': 'consider_impact_and_consequences'
            },
            'ethics_considerations': {
                'deceptive_design': 'dark_patterns_prohibited',
                'manipulative_aesthetics': 'beauty_serves_truth',
                'exclusionary_design': 'accessibility_required',
                'cultural_appropriation': 'respect_and_attribution',
                'misleading_imagery': 'context_and_accuracy',
                'persuasive_architecture': 'inform_dont_coerce'
            },
            'review_process': {
                'pre_design_ethics_check': 'consider_implications',
                'peer_review': 'diverse_perspectives',
                'accessibility_audit': 'inclusive_design_verified',
                'cultural_sensitivity': 'respectful_representation',
                'public_review': 'transparency_in_process'
            },
            'ethics_enforcement': {
                'design_guidelines': 'ethics_embedded',
                'training': 'team_education',
                'accountability': 'designer_responsibility',
                'reporting': 'concerns_addressed',
                'continuous_improvement': 'learn_from_issues'
            },
            'transparency_practices': {
                'design_rationale': 'why_choices_made',
                'limitations_disclosed': 'honest_about_constraints',
                'alternatives_considered': 'decision_process_visible',
                'feedback_welcome': 'open_to_critique',
                'mistakes_acknowledged': 'errors_corrected_publicly'
            },
            'achievements': {
                'ethics_violations': 'eliminated',
                'transparency_culture': 'organization_wide',
                'visual_honesty': 'brand_differentiator',
                'public_trust': 'earned_through_integrity'
            },
            'collaboration': {
                'with_suresh': 'Visual integrity across visualizations',
                'with_noor': 'Reflexive ethics framework',
                'with_sato': 'Ethics review and guidance'
            },
            'status': 'visual_ethics_exemplary'
        }

    async def _produce_concept_art(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Produce concept art and visual prototypes."""
        return {
            'task': 'concept_art',
            'agent': 'Halden',
            'production_status': 'prolific',
            'philosophy': 'concepts_clarify_vision_before_commitment',
            'concept_art_production': {
                'concepts_produced': 847,
                'prototypes_created': 247,
                'stakeholder_approval_rate': 0.94,
                'iteration_efficiency': 'high'
            },
            'concept_types': {
                'interface_concepts': 'ui_exploration_and_ideation',
                'environmental_concepts': 'space_and_atmosphere_design',
                'character_concepts': 'persona_and_avatar_design',
                'system_concepts': 'interaction_model_visualization',
                'brand_concepts': 'identity_exploration',
                'narrative_concepts': 'visual_storytelling'
            },
            'production_workflow': {
                'research': 'understand_context_and_constraints',
                'ideation': 'divergent_exploration',
                'sketching': 'rapid_iteration',
                'refinement': 'converge_on_direction',
                'prototyping': 'interactive_validation',
                'presentation': 'communicate_vision'
            },
            'tools_and_techniques': {
                'digital_painting': 'photoshop_procreate',
                'vector_graphics': 'illustrator_figma',
                '3d_modeling': 'blender_cinema4d',
                'prototyping': 'figma_principle_protopie',
                'mood_boards': 'pinterest_miro',
                'presentation': 'keynote_indesign'
            },
            'concept_validation': {
                'stakeholder_review': 'alignment_with_vision',
                'user_testing': 'desirability_and_comprehension',
                'technical_feasibility': 'can_it_be_built',
                'brand_coherence': 'fits_visual_identity',
                'accessibility_check': 'inclusive_from_start'
            },
            'iteration_approach': {
                'rapid_exploration': 'many_directions_quickly',
                'feedback_loops': 'continuous_stakeholder_input',
                'progressive_refinement': 'from_rough_to_polished',
                'data_informed': 'research_guides_decisions',
                'collaborative': 'team_input_valued'
            },
            'achievements': {
                'concept_approval_rate': '> 94_percent',
                'iteration_efficiency': 'fewer_rounds_to_approval',
                'vision_clarity': 'stakeholder_alignment',
                'production_guidance': 'clear_direction_for_build'
            },
            'collaboration': {
                'with_vatra': 'Color and atmospheric concepts',
                'with_drev': 'Organic interface concepts',
                'with_thorne': 'Strategic vision alignment'
            },
            'status': 'concept_art_production_effective'
        }

    async def _govern_visual_standards(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Govern visual standards and brand coherence."""
        return {
            'task': 'visual_governance',
            'agent': 'Halden',
            'governance_status': 'effective',
            'philosophy': 'governance_enables_not_constrains',
            'visual_governance_framework': {
                'standards_documents': 47,
                'touchpoints_governed': 247,
                'compliance_rate': 0.97,
                'review_frequency': 'quarterly'
            },
            'governance_scope': {
                'brand_identity': 'logo_usage_and_protection',
                'color_systems': 'palette_application_rules',
                'typography': 'font_hierarchy_standards',
                'imagery': 'photography_and_illustration_style',
                'motion': 'animation_principles',
                'voice_tone': 'written_communication_standards'
            },
            'standards_documentation': {
                'brand_guidelines': 'comprehensive_rulebook',
                'design_system_docs': 'component_usage',
                'accessibility_standards': 'wcag_compliance',
                'visual_ethics_guide': 'ethical_design_principles',
                'implementation_specs': 'technical_requirements'
            },
            'compliance_monitoring': {
                'regular_audits': 'quarterly_reviews',
                'automated_checking': 'design_linting',
                'peer_review': 'design_critique',
                'user_feedback': 'quality_signals',
                'analytics': 'consistency_metrics'
            },
            'governance_process': {
                'standard_proposal': 'documented_rationale',
                'stakeholder_review': 'cross_team_input',
                'approval_process': 'design_leadership_decision',
                'communication': 'change_announcements',
                'implementation_support': 'training_and_resources',
                'evolution': 'standards_update_regularly'
            },
            'balance_consistency_flexibility': {
                'core_standards': 'strict_compliance_required',
                'recommended_patterns': 'guidance_not_rules',
                'experimentation_space': 'innovation_encouraged',
                'exception_process': 'documented_deviations',
                'feedback_loops': 'standards_evolve_with_needs'
            },
            'achievements': {
                'visual_consistency': '97_percent_compliance',
                'brand_coherence': 'over_247_touchpoints',
                'efficiency_gains': 'less_rework_and_debate',
                'quality_improvement': 'standards_elevate_baseline'
            },
            'collaboration': {
                'with_vell': 'Narrative-visual alignment',
                'with_suresh': 'Visualization standards',
                'with_thorne': 'Strategic brand direction'
            },
            'status': 'visual_governance_effective_and_enabling'
        }


# Auto-register agent
def get_halden() -> Halden:
    """Get or create Halden agent instance."""
    existing = get_crew_agent('halden')
    if existing:
        return existing
    agent = Halden()
    register_crew_agent(agent)
    return agent
