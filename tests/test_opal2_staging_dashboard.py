"""Focused tests for the repaired OPAL2 staging dashboard."""

import builtins

import pytest

from modules.opal2.staging.staging_dashboard import StagingDashboard, _read_input


@pytest.mark.unit
@pytest.mark.opal2
@pytest.mark.asyncio
async def test_staging_input_is_read_without_blocking_the_event_loop(monkeypatch):
    """Interactive input must flow through the dashboard async helper."""

    monkeypatch.setattr(builtins, "input", lambda _prompt: "  component-1  ")

    assert await _read_input("Component ID: ") == "component-1"  # nosec B101 - pytest assertion


@pytest.mark.unit
@pytest.mark.opal2
def test_staging_candidate_selection_is_fail_closed():
    """Invalid selections must not resolve to a staged candidate."""

    candidates = [{"id": "candidate-1", "name": "Candidate", "score": 95.0}]

    assert (  # nosec B101 - pytest assertion
        StagingDashboard._selected_candidate(candidates, "1") == candidates[0]
    )
    assert StagingDashboard._selected_candidate(  # nosec B101 - pytest assertion
        candidates, "0"
    ) is None
    assert StagingDashboard._selected_candidate(  # nosec B101 - pytest assertion
        candidates, "not-a-number"
    ) is None


@pytest.mark.unit
@pytest.mark.opal2
def test_warning_section_keeps_its_heading_visible(capsys):
    """Interactive warning values must retain a visible stdout heading."""

    StagingDashboard._print_named_values(
        "Blocking Issues", ["Missing approval"], warning=True
    )

    output = capsys.readouterr().out
    assert "Blocking Issues:" in output  # nosec B101 - pytest assertion
    assert "  • Missing approval" in output  # nosec B101 - pytest assertion
