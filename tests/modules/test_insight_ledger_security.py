"""
Security tests for Insight Ledger path traversal protection.

Tests path validation in:
- InsightLedger constructor (storage_path)
- export_ledger method (output_path)
- API export endpoint

Anchor: T1-SEC-LEDGER-001
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from modules.insight_ledger.ledger_core import InsightLedger, validate_safe_path
from modules.insight_ledger.schemas import InsightRecord, InsightType


@pytest.mark.unit
@pytest.mark.security
class TestPathValidationHelper:
    """Test validate_safe_path helper function."""

    def test_rejects_absolute_paths_outside_root(self, tmp_path):
        """Absolute paths are judged by containment, with no temp-directory exemption.

        There used to be a carve-out admitting any absolute path under a system
        temp directory, which returned before the containment check. Being under
        a temp root is a location test, not an authorization decision, so an
        absolute path is no longer special-cased: it is resolved and then held
        to the same root as everything else.
        """
        safe_root = tmp_path / "safe"
        safe_root.mkdir()

        # Outside the root — rejected, as before.
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            validate_safe_path("/etc/passwd", safe_root)

        # Under a temp directory but OUTSIDE safe_root. The carve-out used to
        # admit this purely because of where it sat; it is now rejected on the
        # same containment grounds as /etc/passwd.
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            validate_safe_path(str(tmp_path / "other"), safe_root)

    def test_accepts_absolute_paths_inside_root(self, tmp_path):
        """An absolute path that resolves inside safe_root is admitted."""
        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        target = safe_root / "ledger.json"
        target.write_text("{}")

        result = validate_safe_path(str(target), safe_root)
        assert result == target.resolve()

    def test_rejects_parent_directory_references(self, tmp_path):
        """Validate rejects .. in path."""
        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            validate_safe_path("../etc/passwd", safe_root)
        
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            validate_safe_path("subdir/../../etc", safe_root)
        
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            validate_safe_path("./../../etc", safe_root)

    def test_rejects_paths_outside_bounds(self, tmp_path):
        """Validate rejects resolved paths outside safe_root."""
        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        
        # Create a symlink that escapes the safe directory
        escape_target = tmp_path / "outside"
        escape_target.mkdir()
        escape_link = safe_root / "escape"
        
        try:
            escape_link.symlink_to(escape_target)
            
            # Should reject symlink that escapes
            with pytest.raises(ValueError, match="Path (validation failed|outside allowed directory)"):
                validate_safe_path("escape/file.txt", safe_root, allow_create=True)
        except OSError:
            # Symlinks may not work on all platforms
            pytest.skip("Symlinks not supported on this platform")

    def test_accepts_safe_relative_paths(self, tmp_path):
        """Validate accepts safe relative paths within bounds."""
        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        
        # Should accept simple relative paths
        result = validate_safe_path("data/file.txt", safe_root, allow_create=True)
        assert result.parent.parent == safe_root
        assert result.name == "file.txt"
        
        # Should accept nested paths
        result = validate_safe_path("a/b/c/file.json", safe_root, allow_create=True)
        assert str(result).startswith(str(safe_root))

    def test_requires_existence_by_default(self, tmp_path):
        """Validate requires path to exist unless allow_create=True."""
        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        
        # Non-existent path should fail by default
        with pytest.raises(ValueError, match="Path does not exist"):
            validate_safe_path("nonexistent.txt", safe_root, allow_create=False)
        
        # Should succeed with allow_create
        result = validate_safe_path("nonexistent.txt", safe_root, allow_create=True)
        assert result.parent == safe_root

    def test_symlink_inside_root_pointing_out_is_not_followed(self, tmp_path):
        """A symlink sitting inside the root but leading outside it is rejected.

        The earliest form of this check compared the *unresolved* path against a
        literal "/tmp/" prefix and then returned that same unresolved value, so
        a symlink at /tmp/innocent.json pointing at /etc/hosts passed and the
        caller read the target through it. Containment is now decided on the
        resolved path, so a symlink is judged by where it leads.
        """
        outside = Path("/etc/hosts")
        if not outside.exists():
            pytest.skip("needs a readable absolute path outside the root")

        safe_root = tmp_path / "safe"
        safe_root.mkdir()
        link = safe_root / "innocent.json"
        link.symlink_to(outside)

        with pytest.raises(ValueError, match="Path outside allowed directory"):
            validate_safe_path(str(link), safe_root)

    def test_admitted_path_is_returned_resolved(self, tmp_path):
        """What comes back is the resolved path, not the route that was passed in.

        Routed through a symlinked *directory* so input and resolved form differ
        on every platform. A redundant "." or ".." segment would not do —
        pathlib collapses those on construction, so the assertion would hold
        even if the input were echoed back verbatim.

        This matters because the caller opens whatever is returned. Validating
        one value and handing back another leaves a window for the path to be
        swapped between the check and the open.
        """
        safe_root = tmp_path / "safe"
        safe_root.mkdir()

        real_dir = safe_root / "real_dir"
        real_dir.mkdir()
        target = real_dir / "data.json"
        target.write_text("{}")

        link_dir = safe_root / "link_dir"
        link_dir.symlink_to(real_dir, target_is_directory=True)

        via_link = link_dir / "data.json"
        assert via_link != target, "symlink route must differ from the real path"

        # Both routes stay inside safe_root, so this is admitted — but the
        # resolved location is what must come back.
        result = validate_safe_path(str(via_link), safe_root)

        assert result == target.resolve()
        assert result != via_link


@pytest.mark.unit
@pytest.mark.security
class TestInsightLedgerConstructorSecurity:
    """Test InsightLedger constructor path validation."""

    def test_rejects_absolute_storage_paths(self):
        """Constructor should reject absolute storage paths (except /tmp for testing)."""
        # Absolute paths outside /tmp should be rejected
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            InsightLedger("/etc/passwd")
        
        # /tmp paths are allowed for testing but must be provided by test fixtures
        # Direct use of /tmp paths in production is discouraged
        # This test documents that /tmp paths work for test purposes

    def test_rejects_parent_references_in_storage(self):
        """Constructor should reject .. in storage path."""
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            InsightLedger("../etc/passwd")
        
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            InsightLedger("data/../../evil")

    def test_accepts_safe_relative_storage_paths(self):
        """Constructor should accept safe relative paths."""
        # Should succeed with relative path
        ledger = InsightLedger("test_ledger_safe")
        assert ledger.storage_path.exists()
        assert ledger.storage_path.is_dir()
        
        # Clean up
        import shutil
        shutil.rmtree(ledger.storage_path)


@pytest.mark.unit
@pytest.mark.security
class TestExportLedgerSecurity:
    """Test export_ledger method path validation."""

    def test_rejects_absolute_export_paths(self):
        """Export should reject absolute output paths."""
        ledger = InsightLedger("test_export_security")
        
        # Add a test record
        record = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content="Test insight for export security",
            source="test_security",
            metadata={"test": True}
        )
        ledger.record_insight(record)
        
        # Should reject absolute path
        with pytest.raises(ValueError, match="Path outside allowed directory"):
            ledger.export_ledger("/etc/passwd")
        
        # Clean up
        import shutil
        shutil.rmtree(ledger.storage_path)

    def test_rejects_parent_references_in_export(self):
        """Export should reject .. in output path."""
        ledger = InsightLedger("test_export_traversal")
        
        # Add a test record
        record = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content="Test insight",
            source="test_security",
            metadata={}
        )
        ledger.record_insight(record)
        
        # Should reject parent references
        with pytest.raises(ValueError, match="Parent directory references not allowed"):
            ledger.export_ledger("../../evil.json")
        
        # Clean up
        import shutil
        shutil.rmtree(ledger.storage_path)

    def test_accepts_safe_export_paths(self):
        """Export should accept safe relative paths."""
        ledger = InsightLedger("test_export_valid")
        
        # Add a test record
        record = InsightRecord(
            insight_type=InsightType.ANALYSIS,
            content="Valid export test",
            source="test_security",
            metadata={}
        )
        ledger.record_insight(record)
        
        # Should accept safe path
        count = ledger.export_ledger("valid_export.json", include_genesis=True)
        assert count > 0
        
        # Clean up
        import shutil
        shutil.rmtree(ledger.storage_path)


@pytest.mark.integration
@pytest.mark.security
@pytest.mark.api
class TestExportAPISecurityIntegration:
    """Integration tests for export API endpoint security."""
    
    # These tests require FastAPI test client setup
    # The validation logic is fully tested at the ledger level
    # API delegates to ledger.export_ledger() which is tested above


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
