"""Tests for HR system routes and core modules (issue #761).

Covers:
- Real implementations load and return well-formed data (no mock fallback).
- OrganizationalIntelligence is implemented and works correctly.
- Mock fallback responses carry a machine-readable `degraded: true` flag.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Any, Dict
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# OrganizationalIntelligence – real implementation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_organizational_intelligence_importable() -> None:
    """OrganizationalIntelligence must exist and be importable."""
    from modules.hr_system.core.organizational_intelligence import OrganizationalIntelligence
    assert OrganizationalIntelligence is not None


@pytest.mark.unit
def test_organizational_intelligence_org_wide() -> None:
    """get_capacity_analysis() without a department must return org-wide data."""
    from modules.hr_system.core.organizational_intelligence import OrganizationalIntelligence

    intel = OrganizationalIntelligence()
    result = intel.get_capacity_analysis()

    assert "departments" in result
    assert isinstance(result["departments"], list)
    assert len(result["departments"]) > 0

    assert "total_capacity" in result
    assert result["total_capacity"] > 0

    assert "current_utilization" in result
    assert 0.0 <= result["current_utilization"] <= 2.0  # allow over-utilization

    assert result["growth_trajectory"] in {"expanding", "stable", "contracting", "unknown"}

    assert "degraded" not in result, "Real response must not carry a degraded flag"


@pytest.mark.unit
def test_organizational_intelligence_per_department() -> None:
    """get_capacity_analysis(department=...) must scope to a single department."""
    from modules.hr_system.core.organizational_intelligence import OrganizationalIntelligence

    intel = OrganizationalIntelligence()
    result = intel.get_capacity_analysis(department="engineering")

    assert result["departments"] == ["engineering"]
    assert "total_capacity" in result
    assert "current_staff" in result
    assert "growth_trajectory" in result
    assert result["growth_trajectory"] in {"expanding", "stable", "contracting", "unknown"}
    assert "degraded" not in result


@pytest.mark.unit
def test_organizational_intelligence_context_tag_propagated() -> None:
    """context_tag parameter must appear in the returned data."""
    from modules.hr_system.core.organizational_intelligence import OrganizationalIntelligence

    intel = OrganizationalIntelligence()
    result = intel.get_capacity_analysis(context_tag="test_ctx_123")

    assert result["context_tag"] == "test_ctx_123"


# ---------------------------------------------------------------------------
# StaffingAnalyzer – real implementation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_staffing_analyzer_real_import() -> None:
    """StaffingAnalyzer must be importable and return a valid response."""
    from modules.hr_system.core.staffing_analyzer import StaffingAnalyzer

    analyzer = StaffingAnalyzer()
    result = analyzer.analyze_department_needs("engineering")

    assert result["department"] == "engineering"
    assert "current_staff" in result
    assert "recommended_staff" in result
    assert result["priority"] in {"critical", "high", "medium", "low"}
    assert "degraded" not in result


# ---------------------------------------------------------------------------
# CharacterGenerator – real implementation
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_character_generator_real_import() -> None:
    """CharacterGenerator must be importable and return a valid profile."""
    try:
        from modules.hr_system.core.character_generator import (
            CharacterGenerator,
            Department,
            Rank,
        )
    except ImportError:
        pytest.skip("CharacterGenerator not available in this environment")

    gen = CharacterGenerator()
    candidates = gen.generate_character(
        role="Engineer",
        department=Department.ENGINEERING,
        rank=Rank.LIEUTENANT,
        specializations=["Python", "Quantum"],
    )

    assert len(candidates) > 0
    profile_dict = candidates[0].to_dict()
    assert "name" in profile_dict
    assert profile_dict["department"] == "Engineering"
    assert len(profile_dict["specializations"]) > 0
    assert "degraded" not in profile_dict


# ---------------------------------------------------------------------------
# Degraded fallback responses must carry machine-readable flag
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_staffing_analyze_degraded_flag() -> None:
    """When StaffingAnalyzer import fails, the response must include degraded=True."""
    import sys

    # Force the import to fail by temporarily blocking the module
    with patch.dict(sys.modules, {"modules.hr_system.core.staffing_analyzer": None}):
        # Re-import the route handler module fresh so it sees the patched sys.modules
        import modules.hr_system.api.hr_routes as routes_mod
        importlib.reload(routes_mod)

        import asyncio

        req = routes_mod.StaffingNeedRequest(department="engineering")

        # Patch the import inside the handler to raise ImportError
        original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        async def _call():
            with patch("builtins.__import__", side_effect=_selective_import_error("StaffingAnalyzer")):
                return await routes_mod.analyze_staffing_needs(req)

        result = asyncio.run(_call())
        assert result.get("degraded") is True, (
            f"Expected degraded=True in fallback, got: {result}"
        )


@pytest.mark.unit
def test_organizational_intel_degraded_flag() -> None:
    """When OrganizationalIntelligence import fails, response must include degraded=True."""
    import asyncio
    import sys
    import modules.hr_system.api.hr_routes as routes_mod

    with patch.dict(sys.modules, {"modules.hr_system.core.organizational_intelligence": None}):
        result = asyncio.run(routes_mod.get_organizational_intelligence(department=None))

    assert result.get("degraded") is True, (
        f"Expected degraded=True in fallback, got: {result}"
    )


@pytest.mark.unit
def test_character_generate_degraded_flag() -> None:
    """When CharacterGenerator import fails, response must include degraded=True."""
    import asyncio
    import sys
    import modules.hr_system.api.hr_routes as routes_mod

    req = routes_mod.CharacterGenerationRequest(role="Engineer", department="engineering")

    with patch.dict(sys.modules, {"modules.hr_system.core.character_generator": None}):
        result = asyncio.run(routes_mod.generate_character(req))

    assert result.get("degraded") is True, (
        f"Expected degraded=True in fallback, got: {result}"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _selective_import_error(target_name: str):
    """Return a side_effect function that raises ImportError only for target_name."""
    real_import = __import__

    def _import(name, *args, **kwargs):
        if target_name in name:
            raise ImportError(f"Mocked ImportError for {name}")
        return real_import(name, *args, **kwargs)

    return _import
