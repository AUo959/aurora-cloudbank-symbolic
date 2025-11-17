#!/usr/bin/env python3
"""
Tests for Artifact Manager
===========================
Anchor: TEST-CMD-CHAIN-ARTIFACT-MGR-001
Team: AUo959-team
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL

Tests for post-commit artifact management during sync operations.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
from tools.command_chain.artifact_manager import ArtifactManager


class TestArtifactManager:
    """Test suite for ArtifactManager"""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
            subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ['git', 'config', 'user.email', 'test@example.com'],
                cwd=repo_path,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ['git', 'config', 'user.name', 'Test User'],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            # Create initial commit
            (repo_path / 'README.md').write_text('# Test Repo\n')
            subprocess.run(['git', 'add', '.'], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit'],
                cwd=repo_path,
                check=True,
                capture_output=True
            )

            yield repo_path

    def test_initialization(self):
        """Test ArtifactManager initializes correctly"""
        am = ArtifactManager()
        assert am.workspace_path is not None
        assert isinstance(am.KNOWN_ARTIFACTS, list)
        assert len(am.KNOWN_ARTIFACTS) > 0

    def test_detect_no_artifacts(self, temp_git_repo):
        """Test detection when no artifacts are modified"""
        am = ArtifactManager(workspace_path=temp_git_repo)
        artifacts = am.detect_generated_artifacts()
        assert artifacts == []

    def test_detect_modified_artifacts(self, temp_git_repo):
        """Test detection of modified artifact files"""
        am = ArtifactManager(workspace_path=temp_git_repo)

        # Create tracked artifact first
        artifact_path = temp_git_repo / '.aurora'
        artifact_path.mkdir(exist_ok=True)
        artifact_file = artifact_path / 'audit_trail.json'
        artifact_file.write_text('{"test": "initial"}')

        # Track the file
        subprocess.run(['git', 'add', '.aurora/audit_trail.json'], cwd=temp_git_repo)
        subprocess.run(['git', 'commit', '-m', 'Add artifact'], cwd=temp_git_repo)

        # Now modify it
        artifact_file.write_text('{"test": "modified"}')

        # Detect should find the modified file
        artifacts = am.detect_generated_artifacts(['.aurora/audit_trail.json'])
        assert '.aurora/audit_trail.json' in artifacts

    def test_stash_no_artifacts(self, temp_git_repo):
        """Test stashing with no artifacts returns None"""
        am = ArtifactManager(workspace_path=temp_git_repo)
        stash_index = am.stash_artifacts([])
        assert stash_index is None

    def test_stash_and_restore_artifacts(self, temp_git_repo):
        """Test full stash and restore cycle"""
        am = ArtifactManager(workspace_path=temp_git_repo)

        # Create tracked artifact first
        artifact_path = temp_git_repo / '.aurora'
        artifact_path.mkdir(exist_ok=True)
        artifact_file = artifact_path / 'audit_trail.json'
        test_content = '{"test": "initial"}'
        artifact_file.write_text(test_content)

        # Track the file
        subprocess.run(['git', 'add', '.aurora/audit_trail.json'], cwd=temp_git_repo)
        subprocess.run(['git', 'commit', '-m', 'Add artifact'], cwd=temp_git_repo)

        # Modify it
        test_content = '{"test": "modified", "timestamp": "2025-11-15"}'
        artifact_file.write_text(test_content)

        # Stash the artifact
        stash_index = am.stash_artifacts(['.aurora/audit_trail.json'])
        assert stash_index is not None
        assert stash_index == 0  # Most recent stash is index 0

        # Verify file is removed from working tree
        artifacts = am.detect_generated_artifacts(['.aurora/audit_trail.json'])
        assert len(artifacts) == 0

        # Restore the artifact
        success = am.restore_stashed_artifacts(stash_index)
        assert success is True

        # Verify file is restored
        assert artifact_file.exists()
        assert artifact_file.read_text() == test_content

    def test_handle_sync_artifacts_no_artifacts(self, temp_git_repo):
        """Test sync handler when no artifacts exist"""
        am = ArtifactManager(workspace_path=temp_git_repo)

        sync_called = False

        def mock_sync():
            nonlocal sync_called
            sync_called = True
            return {'success': True, 'message': 'Sync completed'}

        result, artifact_info = am.handle_sync_artifacts(mock_sync)

        assert sync_called is True
        assert result['success'] is True
        assert artifact_info['artifacts_detected'] == 0
        assert artifact_info['stash_index'] is None
        assert artifact_info.get('restore_success') is None

    def test_handle_sync_artifacts_with_artifacts(self, temp_git_repo):
        """Test sync handler with artifact management"""
        am = ArtifactManager(workspace_path=temp_git_repo)

        # Create tracked artifact first
        artifact_path = temp_git_repo / '.aurora'
        artifact_path.mkdir(exist_ok=True)
        artifact_file = artifact_path / 'audit_trail.json'
        artifact_file.write_text('{"test": "initial"}')

        # Track the file
        subprocess.run(['git', 'add', '.aurora/audit_trail.json'], cwd=temp_git_repo)
        subprocess.run(['git', 'commit', '-m', 'Add artifact'], cwd=temp_git_repo)

        # Modify it
        artifact_file.write_text('{"test": "modified"}')

        sync_called = False

        def mock_sync():
            nonlocal sync_called
            sync_called = True
            # During sync, artifact should be stashed
            artifacts = am.detect_generated_artifacts(['.aurora/audit_trail.json'])
            assert len(artifacts) == 0, "Artifacts should be stashed during sync"
            return {'success': True, 'message': 'Sync completed'}

        result, artifact_info = am.handle_sync_artifacts(mock_sync)

        assert sync_called is True
        assert result['success'] is True
        assert artifact_info['artifacts_detected'] > 0
        assert artifact_info['stash_index'] == 0
        assert artifact_info['restore_success'] is True

        # Verify artifact is restored after sync
        assert artifact_file.exists()

    def test_handle_sync_artifacts_with_failure(self, temp_git_repo):
        """Test sync handler restores artifacts even on failure"""
        am = ArtifactManager(workspace_path=temp_git_repo)

        # Create tracked artifact first
        artifact_path = temp_git_repo / '.aurora'
        artifact_path.mkdir(exist_ok=True)
        artifact_file = artifact_path / 'audit_trail.json'
        artifact_file.write_text('{"test": "initial"}')

        # Track the file
        subprocess.run(['git', 'add', '.aurora/audit_trail.json'], cwd=temp_git_repo)
        subprocess.run(['git', 'commit', '-m', 'Add artifact'], cwd=temp_git_repo)

        # Modify it
        artifact_file.write_text('{"test": "modified"}')

        def mock_sync_failure():
            raise Exception("Sync failed")

        with pytest.raises(Exception, match="Sync failed"):
            am.handle_sync_artifacts(mock_sync_failure)

        # Verify artifact is restored even after failure
        # After restore, file should be back
        assert artifact_file.read_text() == '{"test": "modified"}'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
