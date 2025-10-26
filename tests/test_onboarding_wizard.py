#!/usr/bin/env python3
"""
Tests for Aurora CloudBank Onboarding Wizard
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add workspace root to Python path
WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKSPACE_ROOT))

from tools.cli.onboarding_wizard import OnboardingWizard


class TestOnboardingWizard:
    """Test suite for OnboardingWizard"""

    @pytest.fixture
    def wizard(self, tmp_path):
        """Create wizard instance with temp directory"""
        return OnboardingWizard(repo_path=str(tmp_path))

    def test_wizard_initialization(self, wizard, tmp_path):
        """Test wizard initializes correctly"""
        assert wizard.repo_path == tmp_path
        assert wizard.version == "1.0.0"
        assert isinstance(wizard.has_completed_steps, set)
        assert len(wizard.has_completed_steps) == 0

    def test_banner_display(self, wizard, capsys):
        """Test banner is displayed correctly"""
        wizard.print_banner()
        captured = capsys.readouterr()
        assert "AURORA CLOUDBANK ONBOARDING WIZARD" in captured.out
        assert "Welcome" in captured.out

    @patch('builtins.input', return_value='y')
    def test_confirm_yes(self, mock_input, wizard):
        """Test confirm returns True for 'y'"""
        result = wizard.confirm("Test prompt?")
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_confirm_no(self, mock_input, wizard):
        """Test confirm returns False for 'n'"""
        result = wizard.confirm("Test prompt?")
        assert result is False

    @patch('builtins.input', return_value='')
    def test_confirm_default(self, mock_input, wizard):
        """Test confirm uses default value"""
        result = wizard.confirm("Test prompt?", default=True)
        assert result is True
        
        result = wizard.confirm("Test prompt?", default=False)
        assert result is False

    @patch('subprocess.run')
    def test_run_command_success(self, mock_run, wizard):
        """Test successful command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        success, output = wizard.run_command(
            ["echo", "test"],
            "Test command"
        )
        
        assert success is True
        assert output == "Success output"

    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run, wizard):
        """Test failed command execution"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error output"
        mock_run.return_value = mock_result

        success, output = wizard.run_command(
            ["false"],
            "Test command"
        )
        
        assert success is False
        assert "Error output" in output

    @patch('builtins.input', return_value='n')
    def test_step_health_check_skipped(self, mock_input, wizard, capsys):
        """Test health check step can be skipped"""
        wizard.step_health_check()
        captured = capsys.readouterr()
        assert "STEP 1: ENVIRONMENT HEALTH CHECK" in captured.out
        assert "Skipping health check" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_environment_setup_skipped(self, mock_input, wizard, capsys):
        """Test setup step can be skipped"""
        wizard.step_environment_setup()
        captured = capsys.readouterr()
        assert "STEP 2: ENVIRONMENT SETUP" in captured.out
        assert "Skipping setup" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_makefile_commands_skipped(self, mock_input, wizard, capsys):
        """Test makefile commands step can be skipped"""
        wizard.step_makefile_commands()
        captured = capsys.readouterr()
        assert "STEP 3: AVAILABLE MAKEFILE COMMANDS" in captured.out
        assert "Skipping" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_symbolic_anchors_skipped(self, mock_input, wizard, capsys):
        """Test symbolic anchors step can be skipped"""
        wizard.step_symbolic_anchors()
        captured = capsys.readouterr()
        assert "STEP 4: SYMBOLIC ANCHOR TRACKING" in captured.out
        assert "Skipping" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_memory_sealing_skipped(self, mock_input, wizard, capsys):
        """Test memory sealing step can be skipped"""
        wizard.step_memory_sealing()
        captured = capsys.readouterr()
        assert "STEP 5: MEMORY SEALING" in captured.out
        assert "Skipping" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_quicksave_skipped(self, mock_input, wizard, capsys):
        """Test quicksave step can be skipped"""
        wizard.step_quicksave()
        captured = capsys.readouterr()
        assert "STEP 6: QUICKSAVE WORKFLOW" in captured.out
        assert "Skipping" in captured.out

    @patch('builtins.input', return_value='n')
    def test_step_demos_and_api_skipped(self, mock_input, wizard, capsys):
        """Test demos and API step can be skipped"""
        wizard.step_demos_and_api()
        captured = capsys.readouterr()
        assert "STEP 7: DEMOS AND API SERVER" in captured.out

    def test_step_next_steps(self, wizard, capsys):
        """Test final next steps display"""
        wizard.has_completed_steps.add("health_check")
        wizard.has_completed_steps.add("setup")
        wizard.step_next_steps()
        
        captured = capsys.readouterr()
        assert "CONGRATULATIONS" in captured.out
        assert "NEXT STEPS" in captured.out
        assert "Environment health checking" in captured.out
        assert "Development environment setup" in captured.out

    @patch('builtins.input', side_effect=['n'] * 10)  # Skip all interactive prompts
    def test_full_wizard_run(self, mock_input, wizard, tmp_path):
        """Test complete wizard execution"""
        result = wizard.run()
        assert result == 0
        
        # Check completion record was created
        record_file = tmp_path / ".aurora" / "onboarding" / "completion_record.json"
        assert record_file.exists()
        
        # Verify record content
        record = json.loads(record_file.read_text())
        assert "completed_at" in record
        assert record["version"] == "1.0.0"
        assert "completed_steps" in record

    @patch('builtins.input', side_effect=KeyboardInterrupt())
    def test_wizard_interrupt(self, mock_input, wizard, capsys):
        """Test wizard handles keyboard interrupt gracefully"""
        result = wizard.run()
        assert result == 130  # Standard exit code for SIGINT
        
        captured = capsys.readouterr()
        assert "interrupted" in captured.out.lower()

    def test_save_completion_record(self, wizard, tmp_path):
        """Test completion record saving"""
        wizard.has_completed_steps.add("health_check")
        wizard.has_completed_steps.add("setup")
        wizard._save_completion_record()
        
        record_file = tmp_path / ".aurora" / "onboarding" / "completion_record.json"
        assert record_file.exists()
        
        record = json.loads(record_file.read_text())
        assert "health_check" in record["completed_steps"]
        assert "setup" in record["completed_steps"]
        assert record["wizard_version"] == "1.0.0"

    @patch('subprocess.run')
    @patch('builtins.input', return_value='y')
    def test_health_check_with_execution(self, mock_input, mock_run, wizard):
        """Test health check step with actual command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Health check passed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        wizard.step_health_check()
        
        assert "health_check" in wizard.has_completed_steps
        mock_run.assert_called_once()

    @patch('subprocess.run')
    @patch('builtins.input', return_value='y')
    def test_setup_with_execution(self, mock_input, mock_run, wizard):
        """Test setup step with actual command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Setup complete"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        wizard.step_environment_setup()
        
        assert "setup" in wizard.has_completed_steps
        mock_run.assert_called_once()


@pytest.mark.unit
class TestOnboardingWizardUnit:
    """Unit tests for OnboardingWizard helper methods"""

    @pytest.fixture
    def wizard(self, tmp_path):
        """Create wizard instance"""
        return OnboardingWizard(repo_path=str(tmp_path))

    def test_version_attribute(self, wizard):
        """Test wizard has correct version"""
        assert wizard.version == "1.0.0"

    def test_repo_path_is_path_object(self, wizard, tmp_path):
        """Test repo_path is converted to Path object"""
        assert isinstance(wizard.repo_path, Path)
        assert wizard.repo_path == tmp_path

    def test_completed_steps_tracking(self, wizard):
        """Test completed steps are tracked correctly"""
        assert len(wizard.has_completed_steps) == 0
        
        wizard.has_completed_steps.add("test_step")
        assert "test_step" in wizard.has_completed_steps
        assert len(wizard.has_completed_steps) == 1


@pytest.mark.integration
class TestOnboardingWizardIntegration:
    """Integration tests for OnboardingWizard"""

    @pytest.fixture
    def wizard(self, tmp_path):
        """Create wizard instance in temp directory"""
        return OnboardingWizard(repo_path=str(tmp_path))

    def test_completion_record_structure(self, wizard, tmp_path):
        """Test completion record has correct structure"""
        wizard.has_completed_steps.add("health_check")
        wizard.has_completed_steps.add("setup")
        wizard.has_completed_steps.add("makefile")
        wizard._save_completion_record()
        
        record_file = tmp_path / ".aurora" / "onboarding" / "completion_record.json"
        record = json.loads(record_file.read_text())
        
        # Verify all required fields
        assert "completed_at" in record
        assert "version" in record
        assert "completed_steps" in record
        assert "wizard_version" in record
        
        # Verify data types
        assert isinstance(record["completed_steps"], list)
        assert isinstance(record["version"], str)
        assert isinstance(record["wizard_version"], str)
        
        # Verify content
        assert len(record["completed_steps"]) == 3
        assert set(record["completed_steps"]) == {"health_check", "setup", "makefile"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
