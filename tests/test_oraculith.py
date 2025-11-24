"""
Tests for ORACULITH Symbolic Forecast Engine
"""

import sys
from pathlib import Path

import pytest

# Add symbolic to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from symbolic.constellink import (  # noqa: E402
    create_mesh,
    ThreadDescriptor
)
from symbolic.oraculith import (  # noqa: E402
    OraculithEngine,
    OraculithForecastContext,
    OraculithDlpPolicy,
    EchoDescriptor,
    forecast_context_from_dict
)


@pytest.mark.unit
@pytest.mark.aurora
def test_stable_mesh_low_risk_forecast():
    """Test forecast generation with stable, low-entropy mesh."""
    # Create a stable mesh with low entropy
    threads = [
        ThreadDescriptor(
            thread_id='t1',
            source='stability_analysis',
            entropy_hint=0.15,
            tags=['stable', 'verified'],
            anchor_alignment=0.9
        ),
        ThreadDescriptor(
            thread_id='t2',
            source='trend_monitor',
            entropy_hint=0.2,
            tags=['stable', 'monitored'],
            anchor_alignment=0.85
        )
    ]

    mesh = create_mesh(threads)

    # Verify mesh properties
    assert mesh.entropy_summary.drift_flag == 'stable'
    assert mesh.entropy_summary.entropy_mean < 0.3

    # Generate forecast
    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_stable_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Assertions
    assert forecast.forecast_id.startswith('forecast_')
    assert forecast.risk_level == 'low'
    assert forecast.entropy_trend == 'stable'
    assert forecast.anchor_seed == 'EOS_SEED_ORION'
    assert forecast.ethics_protocol == 'Picard_Delta_3'

    # Metaphor should be benign for low risk + stable entropy
    assert 'river' in forecast.metaphor.lower() or 'steady' in forecast.metaphor.lower()

    # Anchor alignment should be high for stable mesh
    assert forecast.anchor_alignment >= 0.8

    # Should have mesh reference
    assert forecast.mesh_reference.mesh_id == mesh.mesh_id
    assert forecast.mesh_reference.drift_flag == 'stable'
    assert forecast.mesh_reference.mesh_state_hash == mesh.mesh_manifest.state_hash

    # Forecast manifest should have hash
    assert forecast.forecast_manifest.state_hash.startswith('sha256:')
    assert len(forecast.forecast_manifest.state_hash) > 10


@pytest.mark.unit
@pytest.mark.aurora
def test_divergent_mesh_high_risk_forecast():
    """Test forecast generation with divergent, high-entropy mesh."""
    # Create a divergent mesh with high entropy
    threads = [
        ThreadDescriptor(
            thread_id='t1',
            source='chaos_detector',
            entropy_hint=0.85,
            tags=['divergent', 'alert'],
            anchor_alignment=0.25
        ),
        ThreadDescriptor(
            thread_id='t2',
            source='risk_sensor',
            entropy_hint=0.75,
            tags=['divergent', 'warning'],
            anchor_alignment=0.3
        ),
        ThreadDescriptor(
            thread_id='t3',
            source='anomaly_tracker',
            entropy_hint=0.9,
            tags=['divergent', 'critical']
        )
    ]

    mesh = create_mesh(threads)

    # Verify mesh properties
    assert mesh.entropy_summary.drift_flag == 'divergent'
    assert mesh.entropy_summary.entropy_mean > 0.6

    # Generate forecast with DLP policy allowing explicit failure modes
    engine = OraculithEngine()
    dlp_policy = OraculithDlpPolicy(allow_explicit_failure_modes=True)
    context = OraculithForecastContext(
        request_id='test_divergent_001',
        mesh=mesh,
        dlp_policy=dlp_policy
    )
    forecast = engine.forecast(context)

    # Assertions
    assert forecast.risk_level == 'high'
    assert forecast.entropy_trend == 'rising'

    # Metaphor should be cautionary for high risk
    assert any(word in forecast.metaphor.lower() for word in ['storm', 'lightning', 'reef', 'chaos', 'compass'])

    # Anchor alignment should be low for divergent mesh
    assert forecast.anchor_alignment < 0.5

    # Summary should be present (allow_explicit_failure_modes=True)
    assert forecast.summary is not None
    assert 'high risk' in forecast.summary.lower() or 'risk detected' in forecast.summary.lower()

    # Divergent truths might be present
    if forecast.divergent_truths:
        assert len(forecast.divergent_truths) > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_forecast_manifest_hash_validation():
    """Test that forecast manifest state_hash is valid SHA256."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.3)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_hash_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Validate hash format
    state_hash = forecast.forecast_manifest.state_hash
    assert state_hash.startswith('sha256:')

    # Hash should be 64 hex chars after prefix
    hex_part = state_hash.split('sha256:')[1]
    assert len(hex_part) == 64
    assert all(c in '0123456789abcdef' for c in hex_part)


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_cross_thread_attribution_disabled():
    """Test that dominant_threads is empty when allow_cross_thread_attribution=False."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='s1', entropy_hint=0.4),
        ThreadDescriptor(thread_id='t2', source='s2', entropy_hint=0.5),
        ThreadDescriptor(thread_id='t3', source='s3', entropy_hint=0.6)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    dlp_policy = OraculithDlpPolicy(allow_cross_thread_attribution=False)
    context = OraculithForecastContext(
        request_id='test_dlp_001',
        mesh=mesh,
        dlp_policy=dlp_policy
    )
    forecast = engine.forecast(context)

    # Should be empty or redacted
    assert len(forecast.supporting_signals.dominant_threads) == 0


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_cross_thread_attribution_enabled():
    """Test that dominant_threads is populated when allow_cross_thread_attribution=True."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='s1', entropy_hint=0.4),
        ThreadDescriptor(thread_id='t2', source='s2', entropy_hint=0.5),
        ThreadDescriptor(thread_id='t3', source='s3', entropy_hint=0.6)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    dlp_policy = OraculithDlpPolicy(allow_cross_thread_attribution=True)
    context = OraculithForecastContext(
        request_id='test_dlp_002',
        mesh=mesh,
        dlp_policy=dlp_policy
    )
    forecast = engine.forecast(context)

    # Should include thread IDs (up to 3)
    assert len(forecast.supporting_signals.dominant_threads) > 0
    assert len(forecast.supporting_signals.dominant_threads) <= 3


@pytest.mark.unit
@pytest.mark.aurora
def test_sensitive_tags_redaction():
    """Test that sensitive tags trigger redaction."""
    threads = [
        ThreadDescriptor(
            thread_id='t1',
            source='s1',
            entropy_hint=0.3,
            tags=['classified', 'report']
        ),
        ThreadDescriptor(
            thread_id='t2',
            source='s2',
            entropy_hint=0.4,
            tags=['internal']
        )
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    dlp_policy = OraculithDlpPolicy(
        allow_cross_thread_attribution=True,  # Would normally show threads
        sensitive_tags=['classified', 'internal']
    )
    context = OraculithForecastContext(
        request_id='test_sensitive_001',
        mesh=mesh,
        dlp_policy=dlp_policy
    )
    forecast = engine.forecast(context)

    # Even though allow_cross_thread_attribution=True, sensitive tags should redact
    assert len(forecast.supporting_signals.dominant_threads) == 0

    # Policy notes should mention sensitive tags
    assert 'sensitive tags' in forecast.dlp_effective_policy.policy_notes.lower()


@pytest.mark.unit
@pytest.mark.aurora
def test_forecast_with_echoes():
    """Test forecast generation with echo descriptors."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='base', entropy_hint=0.3)
    ]
    mesh = create_mesh(threads)

    echoes = [
        EchoDescriptor(
            source='expert_panel',
            echo_text='Stability indicators strong',
            entropy_hint=0.2,
            tags=['expert', 'verified']
        ),
        EchoDescriptor(
            source='sensor_grid',
            echo_text='Noise levels nominal',
            thread_id='t1',
            entropy_hint=0.15
        )
    ]

    engine = OraculithEngine()
    context = OraculithForecastContext(
        request_id='test_echoes_001',
        mesh=mesh,
        echoes=echoes
    )
    forecast = engine.forecast(context)

    # Should include dominant echoes
    assert len(forecast.supporting_signals.dominant_echoes) > 0
    assert 'expert_panel' in forecast.supporting_signals.dominant_echoes or \
           'sensor_grid' in forecast.supporting_signals.dominant_echoes


@pytest.mark.unit
@pytest.mark.aurora
def test_forecast_to_dict():
    """Test that forecast can be converted to dict for JSON export."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.3)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_dict_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Convert to dict
    forecast_dict = forecast.to_dict()

    # Validate structure
    assert 'forecast_id' in forecast_dict
    assert 'metaphor' in forecast_dict
    assert 'risk_level' in forecast_dict
    assert 'entropy_trend' in forecast_dict
    assert 'forecast_manifest' in forecast_dict
    assert 'mesh_reference' in forecast_dict
    assert forecast_dict['forecast_manifest']['state_hash'].startswith('sha256:')


@pytest.mark.unit
@pytest.mark.aurora
def test_forecast_glyphcard():
    """Test that glyphcard generates readable output."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.3)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_glyph_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Get glyphcard
    glyphcard = forecast.glyphcard()

    # Validate structure
    assert 'ORACULITH Forecast Glyphcard' in glyphcard
    assert forecast.forecast_id in glyphcard
    assert forecast.risk_level.upper() in glyphcard
    assert forecast.entropy_trend.upper() in glyphcard
    assert forecast.metaphor[:50] in glyphcard


@pytest.mark.unit
@pytest.mark.aurora
def test_forecast_context_from_dict():
    """Test reconstruction of OraculithForecastContext from dict."""
    # Create original context
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.3)
    ]
    mesh = create_mesh(threads)

    echoes = [
        EchoDescriptor(source='echo1', echo_text='test echo', entropy_hint=0.25)
    ]

    dlp_policy = OraculithDlpPolicy(
        allow_explicit_failure_modes=True,
        allow_cross_thread_attribution=True
    )

    context_dict = {
        'request_id': 'test_recon_001',
        'mesh': mesh.to_dict(),
        'echoes': [
            {
                'source': 'echo1',
                'echo_text': 'test echo',
                'entropy_hint': 0.25,
                'tags': []
            }
        ],
        'forecast_horizon': 'near-term',
        'forecast_focus': ['stability'],
        'dlp_policy': {
            'allow_explicit_failure_modes': True,
            'allow_cross_thread_attribution': True
        },
        'caller_context': {'test': 'data'}
    }

    # Reconstruct
    context = forecast_context_from_dict(context_dict, validate_mesh=True)

    # Validate
    assert context.request_id == 'test_recon_001'
    assert context.mesh.mesh_id == mesh.mesh_id
    assert len(context.echoes) == 1
    assert context.echoes[0].source == 'echo1'
    assert context.dlp_policy.allow_explicit_failure_modes is True
    assert context.forecast_horizon == 'near-term'


@pytest.mark.unit
@pytest.mark.aurora
def test_divergent_truth_detection():
    """Test detection of inconsistencies in divergent_truths."""
    # Create mesh marked as divergent but with low entropy (inconsistent)
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.8)
    ]
    mesh = create_mesh(threads)

    # Manually mark as stable to create inconsistency
    mesh.entropy_summary.drift_flag = 'stable'
    mesh.entropy_summary.entropy_mean = 0.8  # High entropy but stable flag

    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_divergent_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Should detect inconsistency
    assert forecast.divergent_truths is not None
    assert len(forecast.divergent_truths) > 0

    # Check for specific inconsistency message
    found_inconsistency = any(
        'stable' in dt.lower() and 'high' in dt.lower()
        for dt in forecast.divergent_truths
    )
    assert found_inconsistency


@pytest.mark.unit
@pytest.mark.aurora
def test_mesh_entropy_snapshot():
    """Test that mesh entropy snapshot is correctly populated."""
    threads = [
        ThreadDescriptor(thread_id='t1', source='test', entropy_hint=0.4),
        ThreadDescriptor(thread_id='t2', source='test', entropy_hint=0.5)
    ]
    mesh = create_mesh(threads)

    engine = OraculithEngine()
    context = OraculithForecastContext(request_id='test_snapshot_001', mesh=mesh)
    forecast = engine.forecast(context)

    # Validate snapshot
    snapshot = forecast.supporting_signals.mesh_entropy_snapshot
    assert 'entropy_mean' in snapshot
    assert 'drift_flag' in snapshot
    assert 'thread_count' in snapshot
    assert snapshot['thread_count'] == 2
    assert snapshot['drift_flag'] == mesh.entropy_summary.drift_flag


@pytest.mark.integration
@pytest.mark.aurora
def test_end_to_end_forecast_workflow():
    """Integration test: full workflow from mesh creation to forecast export."""
    # Step 1: Create mesh
    threads = [
        ThreadDescriptor(
            thread_id='integration_t1',
            source='system_monitor',
            entropy_hint=0.35,
            tags=['production', 'monitored'],
            anchor_alignment=0.75
        ),
        ThreadDescriptor(
            thread_id='integration_t2',
            source='health_check',
            entropy_hint=0.3,
            tags=['production', 'verified'],
            anchor_alignment=0.8
        )
    ]

    mesh = create_mesh(
        threads,
        symbolic_tags=['integration-test', 'production'],
        dlp_tags=['test-suite', 'e2e']
    )

    # Step 2: Create echoes
    echoes = [
        EchoDescriptor(
            source='operations_team',
            echo_text='System performance nominal',
            entropy_hint=0.2,
            tags=['ops', 'status']
        )
    ]

    # Step 3: Configure DLP policy
    dlp_policy = OraculithDlpPolicy(
        allow_explicit_failure_modes=True,
        allow_cross_thread_attribution=True
    )

    # Step 4: Create context
    context = OraculithForecastContext(
        request_id='integration_test_001',
        mesh=mesh,
        echoes=echoes,
        forecast_horizon='operational',
        forecast_focus=['stability', 'performance'],
        dlp_policy=dlp_policy,
        caller_context={'test_suite': 'oraculith_integration'}
    )

    # Step 5: Generate forecast
    engine = OraculithEngine(
        anchor_seed='EOS_SEED_ORION',
        ethics_protocol='Picard_Delta_3'
    )
    forecast = engine.forecast(context)

    # Step 6: Validate all components
    assert forecast.forecast_id is not None
    assert forecast.risk_level in ['low', 'medium', 'high', 'unknown']
    assert forecast.entropy_trend in ['rising', 'falling', 'stable', 'unknown']
    assert forecast.metaphor is not None
    assert forecast.forecast_manifest.state_hash.startswith('sha256:')
    assert forecast.mesh_reference.mesh_id == mesh.mesh_id

    # Step 7: Export to dict
    forecast_dict = forecast.to_dict()
    assert 'forecast_id' in forecast_dict
    assert 'forecast_manifest' in forecast_dict

    # Step 8: Generate glyphcard
    glyphcard = forecast.glyphcard()
    assert len(glyphcard) > 0
    assert 'ORACULITH' in glyphcard
