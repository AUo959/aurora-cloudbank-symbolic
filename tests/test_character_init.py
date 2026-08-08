"""Character consistency tests retained from standardization Phase 3 (Issue #430).

The original version of this module also asserted that ``.aurora/load_simulation.py``
was the live Orion bootstrap, owned a Primary-8 character cache, and physically
routed Pilot among station locations. Those assumptions were retired by the
governed L1 preflight/runtime boundary introduced in PR #1461.

Legacy-bootstrap containment is tested explicitly in
``tests/test_l1_bootstrap_containment.py``. This module now keeps only the
still-valid character consistency checks from the original Phase-3 work.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = str(PROJECT_ROOT / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)


@pytest.mark.unit
class TestCharacterConsistencyChecker:
    """Tests for character consistency detection (Phase 3 item 2)."""

    def test_detect_typo_alec(self):
        """Test detection of 'Alec' typo."""
        from check_character_consistency import check_for_typos

        content = "Commander Alec Thorne approved the mission."
        issues = check_for_typos(content, "test.md")

        assert len(issues) >= 1
        assert any("Alec" in issue[1] for issue in issues)

    def test_detect_typo_maya_shepherd(self):
        """Test detection of 'Shepherd' typo for Maya Shepard."""
        from check_character_consistency import check_for_typos

        content = "Lt. Commander Maya Shepherd reported to the bridge."
        issues = check_for_typos(content, "test.md")

        assert len(issues) >= 1
        assert any("Shepherd" in issue[1] for issue in issues)

    def test_no_false_positive_correct_names(self):
        """Test that correct names don't trigger typo detection."""
        from check_character_consistency import check_for_typos

        content = "Commander Alex Thorne and Lt. Commander Maya Shepard arrived."
        issues = check_for_typos(content, "test.md")

        assert len(issues) == 0

    def test_build_character_lookup(self):
        """Test that the consistency lookup still includes canonical name variants."""
        from check_character_consistency import build_character_lookup

        lookup = build_character_lookup()

        assert "commander alex thorne" in lookup
        assert "thorne" in lookup
        assert "alex" in lookup
        assert "cmd_001" in lookup
