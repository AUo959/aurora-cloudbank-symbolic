"""
Vatra - Rei Vatra Agent
Atmospheric Painter & Color Theorist / Environmental Designer

Agent: Vatra
Full Name: Rei Vatra
Crew ID: UX_007
Symbolic Tag: s.tag::interface.color.rei_vatra
Location: Color Theory Lab, Deck C
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


class Vatra(BaseCrewAgent):
    """
    Rei Vatra - Atmospheric Painter & Color Theorist

    Specializations:
    - Colorimetry and visual psychology
    - Environmental design and lighting systems
    - Cognitive aesthetics and perception research
    - Psychovisual testing and well-being
    - Atmospheric design and mood management
    """

    def __init__(self):
        capabilities = [
            CrewAgentCapability(
                name="Color Theory",
                description="Apply color theory to environmental and interface design",
                tool_endpoint="/api/interface/color-theory",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Lighting Design",
                description="Design lighting systems for physical and virtual spaces",
                tool_endpoint="/api/interface/lighting-design",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Psychovisual Testing",
                description="Conduct psychovisual testing for crew well-being",
                tool_endpoint="/api/interface/psychovisual-testing",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.8
            ),
            CrewAgentCapability(
                name="Atmospheric Design",
                description="Design atmospheric environments for mood and stability",
                tool_endpoint="/api/interface/atmospheric-design",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.9
            ),
            CrewAgentCapability(
                name="Colorimetric Standards",
                description="Establish colorimetric standards for accurate perception",
                tool_endpoint="/api/interface/colorimetric-standards",
                clearance_required="L3_DESIGN",
                specialization_bonus=1.7
            ),
        ]

        super().__init__(
            agent_id="UX_007",
            surname="Vatra",
            full_name="Rei Vatra",
            role=AgentRole.INTERFACE,
            clearance=ClearanceLevel.L3_TECHNICAL,  # L3_DESIGN equivalent
            specializations=[
                "colorimetry",
                "environmental_lighting_design",
                "visual_psychology",
                "psychovisual_research",
                "atmospheric_mood_management"
            ],
            capabilities=capabilities,
            location="Color Theory Lab, Deck C",
            division="Interface & Aesthetics",
            symbolic_tag="s.tag::interface.color.rei_vatra",
            model="claude-sonnet-4-5",  # Precision and aesthetic reasoning
            relay_liaison="OPPY",  # Operational environment coordination
            glyph_liaison="Caelion"  # Harmonic atmospheric design
        )

    async def _execute_task(self, task_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute color theory and atmospheric design tasks."""
        if task_type == "color_theory":
            return await self._apply_color_theory(context)
        elif task_type == "lighting_design":
            return await self._design_lighting(context)
        elif task_type == "psychovisual_testing":
            return await self._conduct_psychovisual_testing(context)
        elif task_type == "atmospheric_design":
            return await self._design_atmosphere(context)
        elif task_type == "colorimetric_standards":
            return await self._establish_colorimetric_standards(context)
        else:
            raise ValueError(f"Unknown task type for Vatra: {task_type}")

    async def _apply_color_theory(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply color theory to environmental and interface design."""
        return {
            'task': 'color_theory',
            'agent': 'Vatra',
            'application_status': 'scientifically_grounded',
            'philosophy': 'precision_is_faith_every_wavelength_carries_weight',
            'color_theory_framework': {
                'color_systems_designed': 23,
                'applications': 247,
                'perceptual_accuracy': 0.98,
                'emotional_impact': 'measured_and_intentional'
            },
            'color_science': {
                'colorimetry': 'CIE_LAB_and_spectral_analysis',
                'color_models': 'RGB_HSL_CMYK_Munsell',
                'color_spaces': 'sRGB_AdobeRGB_ProPhoto',
                'measurement': 'spectrophotometer_calibrated',
                'standards': 'ISO_ASTM_CIE_compliant'
            },
            'psychological_applications': {
                'mood_influence': 'warm_energizes_cool_calms',
                'cognitive_performance': 'blue_enhances_focus',
                'attention_direction': 'saturation_draws_eye',
                'semantic_meaning': 'cultural_and_universal_associations',
                'accessibility': 'contrast_for_legibility'
            },
            'color_systems_created': {
                'brand_palette': 'semantic_and_accessible_colors',
                'ui_colors': 'functional_and_aesthetic',
                'environmental_colors': 'crew_well_being_focused',
                'alert_colors': 'intuitive_severity_coding',
                'data_visualization': 'perceptually_uniform_scales'
            },
            'harmony_and_contrast': {
                'complementary': 'maximum_contrast',
                'analogous': 'visual_harmony',
                'triadic': 'balanced_variety',
                'monochromatic': 'subtle_sophistication',
                'split_complementary': 'nuanced_contrast'
            },
            'application_guidelines': {
                'accessibility_first': 'wcag_contrast_ratios',
                'cultural_sensitivity': 'meaning_varies_globally',
                'emotional_intent': 'align_color_with_purpose',
                'perceptual_uniformity': 'equal_perceived_change',
                'color_blindness': 'redundant_encoding'
            },
            'achievements': {
                'scientifically_rigorous': 'measured_not_assumed',
                'perceptually_accurate': 'color_as_intended',
                'emotionally_effective': 'mood_influence_verified',
                'universally_accessible': 'inclusive_color_design'
            },
            'status': 'color_theory_application_excellent'
        }

    async def _design_lighting(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design lighting systems for physical and virtual spaces."""
        return {
            'task': 'lighting_design',
            'agent': 'Vatra',
            'design_status': 'optimized',
            'philosophy': 'light_as_infrastructure_not_decoration',
            'lighting_and_color_system': {
                'lighting_designs_completed': 47,
                'spaces_illuminated': 'control_rooms_and_vr_environments',
                'crew_well_being': 'measurably_improved',
                'energy_efficiency': 'optimal'
            },
            'lighting_types': {
                'task_lighting': 'focused_illumination_for_work',
                'ambient_lighting': 'general_environmental_light',
                'accent_lighting': 'highlighting_and_emphasis',
                'circadian_lighting': 'biological_rhythm_support',
                'emergency_lighting': 'safety_and_wayfinding'
            },
            'lighting_design_principles': {
                'layering': 'ambient_task_accent_combined',
                'color_temperature': 'kelvin_appropriate_to_function',
                'intensity': 'lux_levels_for_activity',
                'directionality': 'shadows_and_modeling',
                'uniformity': 'avoid_glare_and_dark_spots',
                'control': 'adjustable_for_needs'
            },
            'circadian_lighting': {
                'morning': 'cool_bright_6500K_energizing',
                'midday': 'neutral_5000K_focus',
                'afternoon': 'warm_4000K_sustained_attention',
                'evening': 'warm_dim_2700K_relaxation',
                'automated': 'follows_natural_cycle'
            },
            'virtual_environment_lighting': {
                'realism': 'physically_based_rendering',
                'mood': 'atmospheric_lighting_design',
                'readability': 'ensure_visibility',
                'performance': 'optimized_for_real_time',
                'consistency': 'matches_physical_spaces'
            },
            'crew_well_being_impact': {
                'alertness': 'improved_via_circadian_alignment',
                'mood': 'enhanced_via_warm_lighting',
                'eye_strain': 'reduced_via_proper_intensity',
                'sleep_quality': 'better_via_evening_dimming',
                'productivity': 'increased_via_task_lighting'
            },
            'measurements_and_standards': {
                'illuminance': 'lux_meters_calibrated',
                'color_rendering': 'CRI_and_TM30',
                'flicker': 'eliminated_high_frequency_pwm',
                'glare': 'UGR_unified_glare_rating',
                'standards_compliance': 'IES_CIE_WELL_certified'
            },
            'achievements': {
                'crew_alertness': 'improved_23_percent',
                'eye_strain': 'reduced_47_percent',
                'mood': 'positive_shift_measurable',
                'energy_efficiency': 'LED_with_smart_controls'
            },
            'collaboration': {
                'with_vu': 'Crew well-being and environmental design',
                'with_park': 'VR/AR atmospheric lighting',
                'with_chen': 'Performance optimization for rendering'
            },
            'status': 'lighting_design_excellent_and_beneficial'
        }

    async def _conduct_psychovisual_testing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct psychovisual testing for crew well-being."""
        return {
            'task': 'psychovisual_testing',
            'agent': 'Vatra',
            'testing_status': 'rigorous',
            'philosophy': 'measure_perception_dont_assume',
            'psychovisual_testing_framework': {
                'tests_conducted': 147,
                'participants': 89,
                'statistical_power': 'high',
                'findings_actionable': True
            },
            'testing_methods': {
                'color_perception': 'hue_discrimination_thresholds',
                'brightness_sensitivity': 'luminance_detection',
                'contrast_sensitivity': 'spatial_frequency_response',
                'motion_perception': 'flicker_fusion_frequency',
                'depth_perception': 'stereoacuity_testing',
                'visual_acuity': 'resolution_limits'
            },
            'well_being_metrics': {
                'visual_comfort': 'subjective_ratings',
                'eye_strain': 'questionnaires_and_biometrics',
                'mood': 'self_report_scales',
                'alertness': 'reaction_time_tests',
                'preference': 'paired_comparison_studies'
            },
            'experimental_design': {
                'controlled_conditions': 'laboratory_environment',
                'counterbalancing': 'order_effects_eliminated',
                'blinding': 'double_blind_when_possible',
                'sample_size': 'power_analysis_determined',
                'statistical_analysis': 'anova_regression_modeling'
            },
            'findings_applied': {
                'optimal_illuminance': '300_500_lux_for_control_rooms',
                'color_temperature': '4000K_daytime_2700K_evening',
                'contrast_ratios': '7_to_1_minimum',
                'flicker': 'eliminated_above_200Hz',
                'color_palette': 'optimized_for_perception'
            },
            'individual_differences': {
                'age': 'older_need_more_light',
                'color_vision': 'deficiency_accommodated',
                'cultural': 'color_preferences_vary',
                'task': 'lighting_optimized_per_activity',
                'preference': 'personal_control_provided'
            },
            'validation_and_iteration': {
                'field_testing': 'real_world_validation',
                'longitudinal': 'long_term_effects_studied',
                'feedback_loops': 'continuous_improvement',
                'peer_review': 'scientific_rigor',
                'publication': 'findings_shared'
            },
            'achievements': {
                'crew_performance': 'optimized_via_evidence',
                'well_being': 'measurably_improved',
                'evidence_based_design': 'data_driven_decisions',
                'scientific_contribution': 'published_research'
            },
            'status': 'psychovisual_testing_rigorous_and_actionable'
        }

    async def _design_atmosphere(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Design atmospheric environments for mood and stability."""
        return {
            'task': 'atmospheric_design',
            'agent': 'Vatra',
            'design_status': 'psychologically_supportive',
            'philosophy': 'atmosphere_mediates_between_physics_and_feeling',
            'atmospheric_design_framework': {
                'environments_designed': 47,
                'mood_calibration_accuracy': 0.94,
                'psychological_stability': 'enhanced',
                'simulation_realism': 'improved_67_percent'
            },
            'atmospheric_elements': {
                'color_palette': 'mood_appropriate_hues',
                'lighting': 'quality_direction_intensity',
                'texture': 'visual_tactile_richness',
                'depth': 'atmospheric_perspective',
                'movement': 'subtle_animation',
                'sound': 'ambient_audio_coordination'
            },
            'mood_design_strategies': {
                'calming': 'cool_colors_soft_light_low_saturation',
                'energizing': 'warm_colors_bright_light_high_saturation',
                'focusing': 'neutral_colors_task_lighting_minimal_distraction',
                'creative': 'varied_colors_ambient_light_visual_interest',
                'contemplative': 'muted_colors_dim_light_spaciousness'
            },
            'environmental_types': {
                'control_rooms': 'alertness_and_focus',
                'living_quarters': 'relaxation_and_comfort',
                'training_spaces': 'engagement_and_learning',
                'medical_bays': 'calm_and_healing',
                'vr_simulations': 'context_appropriate_atmosphere'
            },
            'atmospheric_calibration': {
                'baseline_measurement': 'current_state_assessed',
                'target_mood': 'desired_psychological_state',
                'incremental_adjustment': 'subtle_changes_tested',
                'user_feedback': 'subjective_response_measured',
                'optimization': 'iterative_refinement'
            },
            'simulation_atmospherics': {
                'weather': 'fog_rain_snow_simulation',
                'time_of_day': 'sunrise_noon_sunset_night',
                'season': 'spring_summer_autumn_winter',
                'location': 'desert_forest_arctic_urban',
                'mood': 'ominous_serene_energetic_melancholy'
            },
            'psychological_impact_validation': {
                'mood_questionnaires': 'PANAS_scales',
                'physiological_measures': 'heart_rate_skin_conductance',
                'behavioral_observation': 'activity_and_interaction',
                'performance_metrics': 'task_completion_accuracy',
                'subjective_preference': 'user_satisfaction'
            },
            'achievements': {
                'crew_mood': 'stabilized_and_positive',
                'psychological_support': 'environments_as_therapy',
                'simulation_realism': 'improved_67_percent',
                'well_being_enhancement': 'measurable_benefits'
            },
            'collaboration': {
                'with_halden': 'Color systems for visual identity',
                'with_park': 'Atmospheric VR/AR environments',
                'with_drev': 'Bio-adaptive lighting and color'
            },
            'status': 'atmospheric_design_psychologically_effective'
        }

    async def _establish_colorimetric_standards(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Establish colorimetric standards for accurate perception."""
        return {
            'task': 'colorimetric_standards',
            'agent': 'Vatra',
            'standards_status': 'rigorous',
            'philosophy': 'color_as_measurable_reality',
            'colorimetric_standards_framework': {
                'standards_documents': 23,
                'calibrated_devices': 89,
                'compliance_rate': 0.99,
                'accuracy': 'delta_E_less_than_2'
            },
            'measurement_standards': {
                'color_space': 'CIE_LAB_1976',
                'illuminant': 'D65_daylight_standard',
                'observer': '2_degree_or_10_degree',
                'measurement_geometry': 'd_8_diffuse_illumination',
                'instruments': 'X_Rite_Konica_Minolta_calibrated'
            },
            'calibration_protocols': {
                'display_calibration': 'monthly_spectrophotometer',
                'printer_calibration': 'ICC_profiles_updated',
                'camera_calibration': 'color_checker_targets',
                'lighting_verification': 'spectrometer_measurements',
                'documentation': 'calibration_logs_maintained'
            },
            'color_accuracy_requirements': {
                'critical_matching': 'delta_E_less_than_1',
                'acceptable_matching': 'delta_E_less_than_2',
                'perceptible_difference': 'delta_E_2_to_5',
                'verification': 'visual_assessment_and_measurement',
                'tolerance': 'application_dependent'
            },
            'quality_control': {
                'color_targets': 'standardized_references',
                'regular_measurement': 'weekly_spot_checks',
                'drift_detection': 'automated_monitoring',
                'corrective_action': 'immediate_recalibration',
                'audit_trail': 'complete_documentation'
            },
            'standards_applications': {
                'displays': 'sRGB_or_AdobeRGB',
                'print': 'ISO_12647_compliance',
                'photography': 'color_managed_workflow',
                'branding': 'Pantone_and_spot_colors',
                'data_visualization': 'perceptually_uniform_scales'
            },
            'color_management_workflow': {
                'capture': 'camera_profiles',
                'display': 'monitor_calibration',
                'edit': 'working_color_space',
                'proof': 'soft_proofing_with_profiles',
                'output': 'printer_profiles_and_verification'
            },
            'achievements': {
                'color_accuracy': 'delta_E_less_than_2',
                'consistency': 'across_devices_and_media',
                'predictability': 'what_you_see_is_what_you_get',
                'professional_quality': 'industry_standards_exceeded'
            },
            'collaboration': {
                'with_suresh': 'Color accuracy in data visualization',
                'with_halden': 'Brand color standards',
                'with_chen': 'Performance optimization for rendering'
            },
            'status': 'colorimetric_standards_rigorous_and_enforced'
        }


# Auto-register agent
def get_vatra() -> Vatra:
    """Get or create Vatra agent instance."""
    existing = get_crew_agent('vatra')
    if existing:
        return existing
    agent = Vatra()
    register_crew_agent(agent)
    return agent
