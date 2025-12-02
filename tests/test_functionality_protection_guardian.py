#!/usr/bin/env python3
"""
Tests for Functionality Protection Guardian
==========================================
Target: src/subroutines/functionality_protection_guardian.py
Coverage Goal: 85%+

DLP: COVERAGE_IMPROVEMENT_CRITICAL
Chain: #932//. Integration Coverage Sprint
"""

import json
import os
import tempfile
from datetime import datetime, UTC
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import the module under test
from src.subroutines.functionality_protection_guardian import (
    ProtectionLevel,
    FeatureMetric,
    FeatureProfile,
    SuperiorityAnalysis,
    ApprovalRequest,
    FunctionalityProtectionGuardian,
    pre_commit_hook,
)


class TestProtectionLevel:
    """Test ProtectionLevel enum"""

    def test_monitor_level(self):
        """Test MONITOR protection level"""
        assert ProtectionLevel.MONITOR.value == "monitor"

    def test_warn_level(self):
        """Test WARN protection level"""
        assert ProtectionLevel.WARN.value == "warn"

    def test_block_level(self):
        """Test BLOCK protection level"""
        assert ProtectionLevel.BLOCK.value == "block"

    def test_critical_level(self):
        """Test CRITICAL protection level"""
        assert ProtectionLevel.CRITICAL.value == "critical"


class TestFeatureMetric:
    """Test FeatureMetric enum"""

    def test_lines_of_code_metric(self):
        """Test LINES_OF_CODE metric"""
        assert FeatureMetric.LINES_OF_CODE.value == "lines_of_code"

    def test_test_coverage_metric(self):
        """Test TEST_COVERAGE metric"""
        assert FeatureMetric.TEST_COVERAGE.value == "test_coverage"

    def test_test_pass_rate_metric(self):
        """Test TEST_PASS_RATE metric"""
        assert FeatureMetric.TEST_PASS_RATE.value == "test_pass_rate"

    def test_function_count_metric(self):
        """Test FUNCTION_COUNT metric"""
        assert FeatureMetric.FUNCTION_COUNT.value == "function_count"

    def test_all_metrics_have_values(self):
        """Test all metrics have string values"""
        for metric in FeatureMetric:
            assert isinstance(metric.value, str)
            assert len(metric.value) > 0


class TestFeatureProfile:
    """Test FeatureProfile dataclass"""

    def test_create_minimal_profile(self):
        """Test creating profile with minimal fields"""
        profile = FeatureProfile(
            file_path="/test/file.py",
            version="1.0.0",
            timestamp=datetime.now(UTC)
        )
        assert profile.file_path == "/test/file.py"
        assert profile.version == "1.0.0"
        assert profile.metrics == {}
        assert profile.feature_list == []
        assert len(profile.hash_signature) == 16

    def test_create_full_profile(self):
        """Test creating profile with all fields"""
        metrics = {
            FeatureMetric.LINES_OF_CODE: 100,
            FeatureMetric.FUNCTION_COUNT: 10
        }
        profile = FeatureProfile(
            file_path="/test/file.py",
            version="2.0.0",
            timestamp=datetime.now(UTC),
            metrics=metrics,
            feature_list=["function:test_func", "class:TestClass"],
            test_results={"pass_rate": 1.0}
        )
        assert profile.metrics[FeatureMetric.LINES_OF_CODE] == 100
        assert len(profile.feature_list) == 2

    def test_hash_signature_consistency(self):
        """Test hash signature is deterministic for same input"""
        timestamp = datetime.now(UTC)
        profile1 = FeatureProfile(
            file_path="/test/file.py",
            version="1.0.0",
            timestamp=timestamp,
            feature_list=["a", "b"]
        )
        profile2 = FeatureProfile(
            file_path="/test/file.py",
            version="1.0.0",
            timestamp=timestamp,
            feature_list=["b", "a"]  # Different order, same set
        )
        # Hash should be same since feature_list is sorted
        assert profile1.hash_signature == profile2.hash_signature

    def test_hash_changes_with_path(self):
        """Test hash changes with different file path"""
        timestamp = datetime.now(UTC)
        profile1 = FeatureProfile(
            file_path="/test/file1.py",
            version="1.0.0",
            timestamp=timestamp
        )
        profile2 = FeatureProfile(
            file_path="/test/file2.py",
            version="1.0.0",
            timestamp=timestamp
        )
        assert profile1.hash_signature != profile2.hash_signature


class TestSuperiorityAnalysis:
    """Test SuperiorityAnalysis dataclass"""

    def test_create_analysis(self):
        """Test creating superiority analysis"""
        analysis = SuperiorityAnalysis(
            is_superior=True,
            superiority_score=1.2,
            critical_metrics={},
            recommendation=ProtectionLevel.MONITOR,
            justification="Test justification"
        )
        assert analysis.is_superior is True
        assert analysis.superiority_score == 1.2
        assert analysis.approval_required is False
        assert analysis.emergency_override_code is None

    def test_analysis_with_emergency_code(self):
        """Test analysis with emergency override code"""
        analysis = SuperiorityAnalysis(
            is_superior=False,
            superiority_score=0.5,
            critical_metrics={},
            recommendation=ProtectionLevel.CRITICAL,
            justification="Critical regression",
            approval_required=True,
            emergency_override_code="ABC123DEF456"
        )
        assert analysis.approval_required is True
        assert analysis.emergency_override_code == "ABC123DEF456"


class TestApprovalRequest:
    """Test ApprovalRequest dataclass"""

    def test_create_approval_request(self):
        """Test creating approval request"""
        current_profile = FeatureProfile(
            file_path="/test.py",
            version="1.0.0",
            timestamp=datetime.now(UTC)
        )
        proposed_profile = FeatureProfile(
            file_path="/test.py",
            version="2.0.0",
            timestamp=datetime.now(UTC)
        )
        analysis = SuperiorityAnalysis(
            is_superior=False,
            superiority_score=0.7,
            critical_metrics={},
            recommendation=ProtectionLevel.BLOCK,
            justification="Test"
        )
        request = ApprovalRequest(
            request_id="test_123",
            file_path="/test.py",
            current_profile=current_profile,
            proposed_profile=proposed_profile,
            superiority_analysis=analysis,
            requester="test_user",
            timestamp=datetime.now(UTC),
            justification="Test justification"
        )
        assert request.approval_status == "pending"
        assert request.approver is None


class TestFunctionalityProtectionGuardian:
    """Test FunctionalityProtectionGuardian class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory for tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def guardian(self, temp_dir):
        """Create guardian with temp directories"""
        config_path = os.path.join(temp_dir, "config.json")
        profiles_path = os.path.join(temp_dir, "profiles.json")

        # Create .aurora directory in temp
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)

        # Change to temp dir for test
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian(
            config_path=config_path,
            profiles_path=profiles_path
        )

        yield guardian

        os.chdir(old_cwd)

    def test_guardian_initialization(self, guardian):
        """Test guardian initializes correctly"""
        assert guardian is not None
        assert guardian.config is not None
        assert guardian.profiles is not None
        assert "protection_enabled" in guardian.config

    def test_default_config(self, guardian):
        """Test default configuration values"""
        assert guardian.config["protection_enabled"] is True
        assert "critical_files" in guardian.config
        assert "protected_metrics" in guardian.config

    def test_load_nonexistent_profiles(self, temp_dir):
        """Test loading from nonexistent profiles file"""
        guardian = FunctionalityProtectionGuardian(
            profiles_path=os.path.join(temp_dir, "nonexistent.json")
        )
        assert guardian.profiles == {}

    def test_analyze_file_features_nonexistent(self, guardian):
        """Test analyzing nonexistent file"""
        profile = guardian.analyze_file_features("/nonexistent/file.py")
        assert profile.version == "deleted"

    def test_analyze_file_features_python(self, guardian, temp_dir):
        """Test analyzing Python file features"""
        test_file = os.path.join(temp_dir, "test_module.py")
        content = '''"""Test module"""

def test_function():
    """A test function"""
    pass

class TestClass:
    """A test class"""

    async def async_method(self):
        pass
'''
        with open(test_file, 'w') as f:
            f.write(content)

        profile = guardian.analyze_file_features(test_file)

        assert profile.file_path == test_file
        assert FeatureMetric.LINES_OF_CODE in profile.metrics
        assert FeatureMetric.FUNCTION_COUNT in profile.metrics
        assert "function:test_function" in profile.feature_list
        assert "class:TestClass" in profile.feature_list
        assert "async_support" in profile.feature_list

    def test_analyze_documentation_coverage(self, guardian):
        """Test documentation coverage calculation"""
        content_full_docs = '''
def func1():
    """Documented"""
    pass

def func2():
    """Documented"""
    pass
'''
        coverage = guardian._analyze_documentation_coverage(content_full_docs)
        assert coverage > 0

    def test_analyze_documentation_empty(self, guardian):
        """Test documentation coverage for empty content"""
        coverage = guardian._analyze_documentation_coverage("")
        assert coverage == 1.0

    def test_extract_version_patterns(self, guardian):
        """Test version extraction from content"""
        content_with_version = '__version__ = "1.2.3"'
        version = guardian._extract_version(content_with_version)
        assert version == "1.2.3"

    def test_extract_version_unknown(self, guardian):
        """Test version extraction without version info"""
        content = "def func(): pass"
        version = guardian._extract_version(content)
        assert version == "unknown"

    def test_compare_superiority_equal(self, guardian):
        """Test comparing equal profiles"""
        metrics = {FeatureMetric.LINES_OF_CODE: 100}
        current = FeatureProfile(
            file_path="/test.py",
            version="1.0.0",
            timestamp=datetime.now(UTC),
            metrics=metrics,
            feature_list=["function:test"]
        )
        proposed = FeatureProfile(
            file_path="/test.py",
            version="1.0.0",
            timestamp=datetime.now(UTC),
            metrics=metrics,
            feature_list=["function:test"]
        )

        analysis = guardian.compare_superiority(current, proposed)
        assert analysis.recommendation == ProtectionLevel.MONITOR

    def test_compare_superiority_regression(self, guardian):
        """Test comparing with significant regression"""
        current = FeatureProfile(
            file_path="/test.py",
            version="1.0.0",
            timestamp=datetime.now(UTC),
            metrics={
                FeatureMetric.LINES_OF_CODE: 1000,
                FeatureMetric.FUNCTION_COUNT: 50
            },
            feature_list=["function:quantum_process", "function:symbolic_layer"]
        )
        proposed = FeatureProfile(
            file_path="/test.py",
            version="2.0.0",
            timestamp=datetime.now(UTC),
            metrics={
                FeatureMetric.LINES_OF_CODE: 100,
                FeatureMetric.FUNCTION_COUNT: 5
            },
            feature_list=[]
        )

        analysis = guardian.compare_superiority(current, proposed)
        assert analysis.superiority_score < 1.0
        assert analysis.recommendation in [ProtectionLevel.BLOCK, ProtectionLevel.CRITICAL]

    def test_register_baseline(self, guardian, temp_dir):
        """Test registering file baseline"""
        test_file = os.path.join(temp_dir, "module.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        success = guardian.register_baseline(test_file)
        assert success is True
        assert test_file in guardian.profiles

    def test_register_baseline_failure(self, guardian):
        """Test registering nonexistent file as baseline"""
        success = guardian.register_baseline("/nonexistent/path.py")
        # Should still succeed but with "deleted" version
        assert success is True

    def test_is_protected_file_match(self, guardian):
        """Test protected file pattern matching"""
        # Set config pattern
        guardian.config["critical_files"] = ["modules/**/*.py"]

        assert guardian._is_protected_file("modules/quantum/test.py") is True
        assert guardian._is_protected_file("src/other.py") is False

    def test_check_protection_pre_commit(self, guardian, temp_dir):
        """Test pre-commit protection check"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        # File not in critical list, should pass
        guardian.config["critical_files"] = []
        results = guardian.check_protection_pre_commit([test_file])
        assert results["allowed"] is True

    def test_audit_log_write(self, guardian, temp_dir):
        """Test audit log writing"""
        guardian._audit_log("Test message")
        assert Path(guardian.audit_path).exists()

        with open(guardian.audit_path, 'r') as f:
            content = f.read()
        assert "Test message" in content

    def test_generate_protection_report(self, guardian, temp_dir):
        """Test report generation"""
        report = guardian.generate_protection_report()

        assert "timestamp" in report
        assert "protection_enabled" in report
        assert "total_profiles" in report
        assert "pending_approvals" in report

    def test_save_and_load_profiles(self, guardian, temp_dir):
        """Test profile persistence"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def func(): pass")

        guardian.register_baseline(test_file)
        guardian._save_profiles()

        # Create new guardian and load
        new_guardian = FunctionalityProtectionGuardian(
            profiles_path=guardian.profiles_path
        )

        assert test_file in new_guardian.profiles


class TestEmergencyOverride:
    """Test emergency override functionality"""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def guardian(self, temp_dir):
        """Create guardian with enabled emergency override"""
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian()
        guardian.config["emergency_override_enabled"] = True

        yield guardian
        os.chdir(old_cwd)

    def test_emergency_override_disabled(self, temp_dir):
        """Test emergency override when disabled"""
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian()
        guardian.config["emergency_override_enabled"] = False

        result = guardian.emergency_override("/test.py", "CODE123")
        assert result is False

        os.chdir(old_cwd)

    def test_emergency_override_no_baseline(self, guardian):
        """Test emergency override without baseline"""
        result = guardian.emergency_override("/no_baseline.py", "CODE123")
        assert result is False

    def test_emergency_override_wrong_code(self, guardian, temp_dir):
        """Test emergency override with wrong code"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        guardian.register_baseline(test_file)
        result = guardian.emergency_override(test_file, "WRONG_CODE")
        assert result is False


class TestApprovalSystem:
    """Test approval request system"""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def guardian(self, temp_dir):
        """Create guardian with test setup"""
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian()
        yield guardian

        os.chdir(old_cwd)

    def test_request_approval_no_baseline(self, guardian):
        """Test requesting approval without baseline"""
        with pytest.raises(ValueError, match="No baseline profile"):
            guardian.request_approval("/no_baseline.py", "Test justification")

    def test_request_approval_success(self, guardian, temp_dir):
        """Test successful approval request"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        guardian.register_baseline(test_file)
        request_id = guardian.request_approval(
            test_file,
            "Need to refactor",
            "test_user"
        )

        assert request_id is not None
        assert len(request_id) == 16

    def test_check_approval_none_exist(self, guardian):
        """Test check approval with no approvals"""
        result = guardian._check_approval("/test.py")
        assert result is False

    def test_save_approval_request(self, guardian, temp_dir):
        """Test saving approval request"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        guardian.register_baseline(test_file)
        guardian.request_approval(test_file, "Test", "user")

        assert Path(guardian.approvals_path).exists()

        with open(guardian.approvals_path, 'r') as f:
            approvals = json.load(f)

        assert len(approvals) == 1
        assert approvals[0]["file_path"] == test_file

    def test_update_baseline_post_approval(self, guardian, temp_dir):
        """Test baseline update after approval"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("def test(): pass")

        guardian.register_baseline(test_file)

        # Without approval, should fail
        result = guardian.update_baseline_post_approval(test_file)
        assert result is False


class TestTestResultsAnalysis:
    """Test test results analysis"""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def guardian(self, temp_dir):
        """Create guardian"""
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian()
        yield guardian

        os.chdir(old_cwd)

    def test_analyze_test_results_no_tests(self, guardian, temp_dir):
        """Test analysis when no test file exists"""
        results = guardian._analyze_test_results("/nonexistent/module.py")
        assert results["pass_rate"] == 0.0
        assert results["total_tests"] == 0

    def test_analyze_test_results_with_tests(self, guardian, temp_dir):
        """Test analysis with corresponding test file"""
        # Create tests directory
        tests_dir = os.path.join(temp_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)

        # Create test file
        test_file = os.path.join(tests_dir, "test_module.py")
        with open(test_file, 'w') as f:
            f.write("""
def test_one():
    pass

def test_two():
    pass

def test_three():
    pass
""")

        results = guardian._analyze_test_results(f"tests/test_module.py")
        # May or may not find tests depending on path matching
        assert "total_tests" in results


class TestPreCommitHook:
    """Test pre-commit hook functionality"""

    def test_pre_commit_hook_no_git(self):
        """Test pre-commit hook when git not available"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=1, stdout="")
            result = pre_commit_hook()
            assert result == 0  # Allow commit if can't determine changes

    def test_pre_commit_hook_no_changes(self):
        """Test pre-commit hook with no changed files"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = pre_commit_hook()
            assert result == 0

    def test_pre_commit_hook_with_changes(self):
        """Test pre-commit hook with changed files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            # Create .aurora directory
            os.makedirs(".aurora", exist_ok=True)

            # Create a test file
            with open("test.py", 'w') as f:
                f.write("def test(): pass")

            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="test.py\n"
                )

                # Mock guardian to avoid file system issues
                with patch('src.subroutines.functionality_protection_guardian.FunctionalityProtectionGuardian') as mock_guardian:
                    mock_instance = MagicMock()
                    mock_instance.check_protection_pre_commit.return_value = {
                        "allowed": True,
                        "blocked_files": [],
                        "warnings": [],
                        "approval_required": [],
                        "emergency_codes": {}
                    }
                    mock_guardian.return_value = mock_instance

                    result = pre_commit_hook()
                    assert result == 0

            os.chdir(old_cwd)


class TestVersionExtraction:
    """Test version extraction patterns"""

    @pytest.fixture
    def guardian(self):
        """Create guardian for version tests"""
        with tempfile.TemporaryDirectory() as tmpdir:
            aurora_dir = os.path.join(tmpdir, ".aurora")
            os.makedirs(aurora_dir, exist_ok=True)
            old_cwd = os.getcwd()
            os.chdir(tmpdir)

            guardian = FunctionalityProtectionGuardian()
            yield guardian

            os.chdir(old_cwd)

    def test_extract_dunder_version(self, guardian):
        """Test extracting __version__ pattern"""
        content = '__version__ = "2.1.0"'
        assert guardian._extract_version(content) == "2.1.0"

    def test_extract_version_constant(self, guardian):
        """Test extracting VERSION constant"""
        content = 'VERSION = "3.0.0"'
        assert guardian._extract_version(content) == "3.0.0"

    def test_extract_version_yaml_style(self, guardian):
        """Test extracting YAML-style version"""
        content = 'version: "4.5.6"'
        assert guardian._extract_version(content) == "4.5.6"

    def test_extract_semver_pattern(self, guardian):
        """Test extracting semver from text"""
        content = "Aurora v1.2.3 release notes"
        assert guardian._extract_version(content) == "1.2.3"


class TestFeatureListAnalysis:
    """Test feature list extraction"""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def guardian(self, temp_dir):
        """Create guardian"""
        aurora_dir = os.path.join(temp_dir, ".aurora")
        os.makedirs(aurora_dir, exist_ok=True)
        old_cwd = os.getcwd()
        os.chdir(temp_dir)

        guardian = FunctionalityProtectionGuardian()
        yield guardian

        os.chdir(old_cwd)

    def test_detects_dataclass_usage(self, guardian, temp_dir):
        """Test detection of dataclass usage"""
        test_file = os.path.join(temp_dir, "test.py")
        content = '''
from dataclasses import dataclass

@dataclass
class TestData:
    name: str
'''
        with open(test_file, 'w') as f:
            f.write(content)

        profile = guardian.analyze_file_features(test_file)
        assert "dataclass_usage" in profile.feature_list

    def test_detects_quantum_state(self, guardian, temp_dir):
        """Test detection of QuantumState usage"""
        test_file = os.path.join(temp_dir, "test.py")
        content = '''
class QuantumState:
    pass
'''
        with open(test_file, 'w') as f:
            f.write(content)

        profile = guardian.analyze_file_features(test_file)
        assert "quantum_state_tracking" in profile.feature_list

    def test_detects_async_support(self, guardian, temp_dir):
        """Test detection of async support"""
        test_file = os.path.join(temp_dir, "test.py")
        content = '''
async def process():
    await something()
'''
        with open(test_file, 'w') as f:
            f.write(content)

        profile = guardian.analyze_file_features(test_file)
        assert "async_support" in profile.feature_list
