import pytest

from src.aurora_fusion import AuroraFusionEngine, get_high_value_module_matrix


def test_module_matrix_has_core_native_modules():
    matrix = get_high_value_module_matrix()
    paths = [item.module_path for item in matrix]
    assert "src.core.native_quantum" in paths
    assert "src.core.native_vsa" in paths
    assert "src.core.native_symbolic_anchor" in paths


@pytest.mark.asyncio
async def test_balanced_fusion_compose():
    engine = AuroraFusionEngine(profile="balanced")
    artifact = await engine.compose("Threadcore symbolic anchor routing for agent workflow integrity")

    assert artifact["profile"] == "balanced"
    assert artifact["classification"]["threadcore_tagger"]["primary_folder"] != "Unsorted"
    assert artifact["hybrid_anchor"]["memory_sealed"]["integrity_verified"] is True
    assert artifact["glyph_payload"] is not None
    assert artifact["recommended_modules"]


@pytest.mark.asyncio
async def test_extended_profile_exposes_agent_tools():
    engine = AuroraFusionEngine(profile="extended")
    artifact = await engine.compose("Enable agent tools for symbolic and session operations")

    manifest = artifact["agent_tool_manifest"]
    assert manifest is not None
    assert "tools" in manifest
    assert "symbolic_processing" in manifest["tools"]

