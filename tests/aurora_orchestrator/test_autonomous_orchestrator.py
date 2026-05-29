"""
Tests for Aurora Autonomous Orchestrator

Tests Aurora's continuous consciousness loop and orchestration capabilities.
"""

import pytest
import asyncio
from datetime import datetime

from src.aurora_orchestrator.autonomous_orchestrator import (
    AuroraOrchestrator,
    OrchestrationMode,
    OrchestrationConfig
)


@pytest.fixture
def config():
    """Test configuration"""
    return OrchestrationConfig(
        enabled=True,
        initial_mode=OrchestrationMode.ACTIVE,
        observation_interval_seconds=1,  # Fast for testing
        min_sleep_seconds=0.1,
        max_sleep_seconds=2,
        enable_triplex_validation=True,
        mock_mode=True
    )


@pytest.fixture
async def orchestrator(config):
    """Create orchestrator instance"""
    orch = AuroraOrchestrator(config=config)
    yield orch
    # Cleanup
    if orch.running:
        await orch.stop_orchestration()


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initializes correctly"""
    assert orchestrator is not None
    assert orchestrator.mode == OrchestrationMode.ACTIVE
    assert not orchestrator.running
    assert orchestrator.config.enabled


@pytest.mark.asyncio
@pytest.mark.slow  # #792: integration test sleeps 2s while orchestrator loop runs
async def test_orchestrator_start_stop(orchestrator):
    """Test orchestrator can start and stop"""
    await orchestrator.start_orchestration()
    assert orchestrator.running
    assert orchestrator.stats['orchestration_started_at'] is not None

    # Let it run for a bit
    await asyncio.sleep(2)

    # Should have completed some loops
    assert orchestrator.stats['total_loops'] > 0

    await orchestrator.stop_orchestration()
    assert not orchestrator.running


@pytest.mark.asyncio
async def test_system_observation(orchestrator):
    """Test system state observation"""
    state = await orchestrator._observe_system_state()

    assert state is not None
    assert 'timestamp' in state
    assert 'overall_health' in state
    assert 0.0 <= state['overall_health'] <= 1.0


@pytest.mark.asyncio
@pytest.mark.slow  # #792: decision-loop test sleeps 3s
async def test_decision_making(orchestrator):
    """Test Aurora can make decisions"""
    await orchestrator.start_orchestration()

    # Let it run and make decisions
    await asyncio.sleep(3)

    # Should have made at least one observation and thought
    assert orchestrator.stats['total_observations'] > 0
    assert orchestrator.stats['total_thoughts'] > 0

    await orchestrator.stop_orchestration()


@pytest.mark.asyncio
async def test_orchestrator_status(orchestrator):
    """Test getting orchestrator status"""
    status = orchestrator.get_status()

    assert 'orchestrator' in status
    assert 'aurora' in status
    assert 'statistics' in status
    assert 'components' in status


@pytest.mark.asyncio
async def test_adaptive_sleep(orchestrator):
    """Test adaptive sleep functionality"""
    # Should calculate sleep duration
    await orchestrator._adaptive_sleep()
    # If it completes, it's working


@pytest.mark.asyncio
async def test_focus_area_determination(orchestrator):
    """Test focus area determination"""
    state = {
        'drift_level': 0.06,  # High drift
        'quantum_coherence': 0.9,
        'bottlenecks': [],
        'anomalies': []
    }

    focus = orchestrator._determine_focus_area(state)
    assert focus == 'drift_management'

    state['drift_level'] = 0.02
    state['quantum_coherence'] = 0.65  # Low coherence

    focus = orchestrator._determine_focus_area(state)
    assert focus == 'quantum_health'


@pytest.mark.asyncio
async def test_urgency_calculation(orchestrator):
    """Test urgency score calculation"""
    state = {
        'overall_health': 0.4,  # Critical health
        'drift_level': 0.02,
        'anomalies': []
    }

    urgency = orchestrator._calculate_urgency(state)
    assert urgency > 0.5  # Should be high urgency


@pytest.mark.asyncio
async def test_action_requirement_assessment(orchestrator):
    """Test action requirement assessment"""
    # Healthy state - no action needed
    state = {
        'overall_health': 0.9,
        'drift_level': 0.01,
        'bottlenecks': [],
        'anomalies': []
    }

    requires_action = orchestrator._assess_action_requirement(state)
    assert not requires_action

    # Unhealthy state - action needed
    state['overall_health'] = 0.6
    requires_action = orchestrator._assess_action_requirement(state)
    assert requires_action


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
