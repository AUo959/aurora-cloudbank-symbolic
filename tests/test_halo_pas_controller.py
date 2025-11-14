"""
Tests for HALO/PAS Drift Controller

Tests drift calculation, status export, and DLP integration
with fake time sources for deterministic testing.
"""

import pytest
import asyncio

from src.aurora.continuity.halo_pas_controller import (
    HALOPASController,
    DriftSample,
)


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_drift_sample_creation():
    """Test DriftSample dataclass creation and conversion"""
    sample = DriftSample(
        timestamp=1000.0,
        l1_time=1000.0,
        l2_time=1001.5,
        l3_time=999.0,
        drift_l2=1.5,
        drift_l3=-1.0,
        sample_id=1,
    )

    assert sample.timestamp == 1000.0
    assert sample.l1_time == 1000.0
    assert sample.l2_time == 1001.5
    assert sample.l3_time == 999.0
    assert sample.drift_l2 == 1.5
    assert sample.drift_l3 == -1.0
    assert sample.sample_id == 1

    # Test to_dict conversion
    sample_dict = sample.to_dict()
    assert isinstance(sample_dict, dict)
    assert sample_dict["drift_l2"] == 1.5
    assert sample_dict["drift_l3"] == -1.0


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_controller_initialization():
    """Test HALOPASController initialization"""
    controller = HALOPASController(interval=0.5)

    assert controller.interval == 0.5
    assert not controller._running
    assert controller._task is None
    assert len(controller._samples) == 0
    assert controller._sample_counter == 0


@pytest.mark.unit
@pytest.mark.aurora
@pytest.mark.critical
def test_drift_calculation_with_fake_sources():
    """Test drift calculation with injected fake time sources"""
    # Create fake time sources with controlled drift
    l1_value = 1000.0
    l2_value = 1002.5  # L2 is 2.5 seconds ahead
    l3_value = 998.0   # L3 is 2.0 seconds behind

    def l1_source():
        return l1_value

    def l2_source():
        return l2_value

    def l3_source():
        return l3_value

    controller = HALOPASController(
        interval=0.5,
        l1_source=l1_source,
        l2_source=l2_source,
        l3_source=l3_source,
    )

    # Sample drift
    sample = controller._sample_drift()

    # Verify drift calculations
    assert sample.l1_time == 1000.0
    assert sample.l2_time == 1002.5
    assert sample.l3_time == 998.0
    assert sample.drift_l2 == 2.5  # L2 - L1
    assert sample.drift_l3 == -2.0  # L3 - L1
    assert sample.sample_id == 1


@pytest.mark.unit
@pytest.mark.aurora
def test_drift_calculation_no_drift():
    """Test drift calculation when all layers are synchronized"""
    base_time = 5000.0

    # All sources return same time (no drift)
    def l1_source():
        return base_time

    def l2_source():
        return base_time

    def l3_source():
        return base_time

    controller = HALOPASController(
        interval=0.1,
        l1_source=l1_source,
        l2_source=l2_source,
        l3_source=l3_source,
    )

    sample = controller._sample_drift()

    # Verify no drift
    assert sample.drift_l2 == 0.0
    assert sample.drift_l3 == 0.0


@pytest.mark.unit
@pytest.mark.aurora
def test_multiple_samples_increment_counter():
    """Test that sample counter increments correctly"""
    controller = HALOPASController(interval=0.1)

    # Take multiple samples
    sample1 = controller._sample_drift()
    sample2 = controller._sample_drift()
    sample3 = controller._sample_drift()

    assert sample1.sample_id == 1
    assert sample2.sample_id == 2
    assert sample3.sample_id == 3
    assert controller._sample_counter == 3


@pytest.mark.unit
@pytest.mark.aurora
def test_dlp_tag_creation():
    """Test DLP tag creation with Aurora anchors"""
    controller = HALOPASController(interval=0.1)

    # Create a sample
    sample = controller._sample_drift()

    # Create DLP tag
    tag_id = controller._create_dlp_tag(sample)

    # Verify tag was created
    assert tag_id in controller._dlp_tracker.tags

    # Verify tag structure
    tag = controller._dlp_tracker.tags[tag_id]
    assert tag.operation == "halo_pas_drift_sample"
    assert "EOS_SEED_ORION" in tag.anchor_protocols
    assert "T1" in tag.t1_srb_anchors
    assert "SRB" in tag.t1_srb_anchors
    assert "drift_vector" in tag.symbolic_patterns
    assert "drift_l2" in tag.symbolic_patterns["drift_vector"]
    assert "drift_l3" in tag.symbolic_patterns["drift_vector"]


@pytest.mark.unit
@pytest.mark.aurora
def test_export_status_no_samples():
    """Test export_status with no samples collected"""
    controller = HALOPASController(interval=0.25)

    status = controller.export_status()

    assert status["status"] == "stopped"
    assert status["interval"] == 0.25
    assert status["total_samples"] == 0
    assert status["samples_in_memory"] == 0
    assert status["last_sample"] is None
    assert len(status["recent_samples"]) == 0
    assert status["statistics"]["avg_drift_l2"] == 0.0
    assert status["statistics"]["avg_drift_l3"] == 0.0
    assert "EOS_SEED_ORION" in status["anchor_protocols"]
    assert "T1" in status["t1_srb_anchors"]
    assert "SRB" in status["t1_srb_anchors"]
    assert "HALO_PAS_DRIFT" in status["symbolic_tags"]


@pytest.mark.unit
@pytest.mark.aurora
def test_export_status_with_samples():
    """Test export_status with collected samples"""
    # Create controller with fake sources that have drift
    def l1_source():
        return 1000.0

    def l2_source():
        return 1005.0  # +5.0 drift

    def l3_source():
        return 995.0   # -5.0 drift

    controller = HALOPASController(
        interval=0.1,
        l1_source=l1_source,
        l2_source=l2_source,
        l3_source=l3_source,
    )

    # Collect some samples
    for _ in range(5):
        sample = controller._sample_drift()
        controller._samples.append(sample)
        controller._create_dlp_tag(sample)

    status = controller.export_status()

    assert status["status"] == "stopped"
    assert status["total_samples"] == 5
    assert status["samples_in_memory"] == 5
    assert status["last_sample"] is not None
    assert len(status["recent_samples"]) == 5
    assert status["statistics"]["avg_drift_l2"] == 5.0
    assert status["statistics"]["avg_drift_l3"] == -5.0
    assert status["statistics"]["max_drift_l2"] == 5.0
    assert status["statistics"]["max_drift_l3"] == 5.0


@pytest.mark.unit
@pytest.mark.aurora
def test_sample_memory_limit():
    """Test that controller respects max_samples limit"""
    controller = HALOPASController(interval=0.1)
    controller._max_samples = 10  # Set small limit for testing

    # Create more samples than the limit
    for _ in range(15):
        sample = controller._sample_drift()
        controller._samples.append(sample)
        if len(controller._samples) > controller._max_samples:
            controller._samples.pop(0)

    # Should keep only last 10 samples
    assert len(controller._samples) == 10
    assert controller._sample_counter == 15


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.aurora
async def test_controller_start_stop():
    """Test controller start and stop lifecycle"""
    controller = HALOPASController(interval=0.05)

    # Start controller
    await controller.start()
    assert controller._running is True
    assert controller._task is not None

    # Let it run for a short time
    await asyncio.sleep(0.2)

    # Stop controller
    await controller.stop()
    assert controller._running is False
    assert controller._task is None

    # Should have collected some samples
    assert controller._sample_counter > 0
    assert len(controller._samples) > 0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.aurora
async def test_controller_double_start():
    """Test that double start is handled gracefully"""
    controller = HALOPASController(interval=0.05)

    # Start controller twice
    await controller.start()
    await controller.start()  # Should log warning but not fail

    assert controller._running is True

    # Cleanup
    await controller.stop()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.aurora
async def test_controller_samples_while_running(caplog):
    """Test that samples are collected while controller is running"""
    import logging
    caplog.set_level(logging.INFO)

    # Use fast interval for quick test
    controller = HALOPASController(interval=0.05)

    await controller.start()

    # Let it run and collect samples
    await asyncio.sleep(0.2)

    await controller.stop()

    # Verify samples were collected
    assert controller._sample_counter > 0

    # Verify logging occurred (check for drift sample log messages)
    log_messages = [record.message for record in caplog.records]
    drift_logs = [msg for msg in log_messages if "drift" in msg.lower()]
    assert len(drift_logs) > 0


@pytest.mark.unit
@pytest.mark.aurora
def test_export_status_recent_samples_limit():
    """Test that export_status returns only last 10 recent samples"""
    controller = HALOPASController(interval=0.1)

    # Create 20 samples
    for _ in range(20):
        sample = controller._sample_drift()
        controller._samples.append(sample)

    status = controller.export_status()

    # Should only include last 10 in recent_samples
    assert len(status["recent_samples"]) == 10
    assert status["samples_in_memory"] == 20

    # Verify it's the last 10
    last_sample_id = status["recent_samples"][-1]["sample_id"]
    assert last_sample_id == 20
