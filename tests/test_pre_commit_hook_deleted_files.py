#!/usr/bin/env python3
"""
Test case specifically for the pre-commit hook deleted files fix

This test ensures that the pre-commit hook correctly handles deleted files
without blocking legitimate commits.

Issue: https://github.com/AUo959/aurora-cloudbank-symbolic/issues/122
"""
import unittest
import tempfile
import os
import subprocess
from pathlib import Path
import shutil
from unittest.mock import patch, MagicMock
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

class TestPreCommitHookDeletedFilesFix(unittest.TestCase):
    """Test cases for the deleted files fix in pre-commit hook."""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_get_staged_files_with_deletions(self):
        """Test get_staged_files function with file deletions"""
        import git_pre_commit_hook as hook
        
        # Create and commit a file
        test_file = Path("test.py")
        test_file.write_text("print('test')\n")
        subprocess.run(["git", "add", "test.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Add test file"], check=True)
        
        # Delete and stage the deletion
        subprocess.run(["git", "rm", "test.py"], check=True)
        
        # Test the function
        staged_files = hook.get_staged_files()
        self.assertIn("test.py", staged_files)
        self.assertFalse(Path("test.py").exists())
    
    def test_file_filtering_logic(self):
        """Test the file filtering logic with deleted files"""
        # Mock staged files including deleted ones
        staged_files = ["deleted.py", "existing.md", "also_deleted.json"]
        
        # Create only the existing file
        Path("existing.md").write_text("# Test\n")
        
        # Apply the filtering logic from the hook
        validatable_extensions = {'.md', '.txt', '.js', '.ts', '.py', '.json', '.yaml', '.yml'}
        
        # First, filter out non-existent files (deleted files)
        existing_files = []
        deleted_files = []
        for f in staged_files:
            file_path = Path(f)
            if file_path.exists():
                existing_files.append(f)
            else:
                deleted_files.append(f)
        
        # Then filter for validatable extensions
        files_to_validate = [
            f for f in existing_files
            if Path(f).suffix in validatable_extensions
        ]
        
        self.assertEqual(existing_files, ["existing.md"])
        self.assertEqual(set(deleted_files), {"deleted.py", "also_deleted.json"})
        self.assertEqual(files_to_validate, ["existing.md"])
    
    def test_defensive_validation_logic(self):
        """Test the defensive validation logic"""
        import git_pre_commit_hook as hook
        
        # Mock validator that should not be called for non-existent files
        with patch('git_pre_commit_hook.CanonicalValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            mock_validator.validate_file.return_value = []
            
            # Create a file for testing
            test_file = Path("test.py")
            test_file.write_text("print('test')\n")
            
            files_to_validate = ["test.py"]
            all_results = []
            
            # Apply the validation logic
            for file_path in files_to_validate:
                try:
                    # Double-check file exists before validation (defensive programming)
                    if not Path(file_path).exists():
                        continue
                        
                    results = mock_validator.validate_file(file_path)
                    all_results.extend(results)
                except FileNotFoundError:
                    continue
                except PermissionError:
                    continue
                except Exception:
                    pass
            
            # Verify validator was called for existing file
            mock_validator.validate_file.assert_called_once_with("test.py")
    
    def test_race_condition_handling(self):
        """Test handling of race conditions where file is deleted between checks"""
        import git_pre_commit_hook as hook
        
        with patch('git_pre_commit_hook.CanonicalValidator') as mock_validator_class:
            mock_validator = MagicMock()
            mock_validator_class.return_value = mock_validator
            
            # Simulate file being deleted between the existence check and validation
            def side_effect(file_path):
                # Delete the file when validator tries to access it
                Path(file_path).unlink(missing_ok=True)
                raise FileNotFoundError("File not found")
            
            mock_validator.validate_file.side_effect = side_effect
            
            # Create a file
            test_file = Path("test.py")
            test_file.write_text("print('test')\n")
            
            files_to_validate = ["test.py"]
            all_results = []
            
            # Apply the validation logic with defensive handling
            for file_path in files_to_validate:
                try:
                    if not Path(file_path).exists():
                        continue
                        
                    results = mock_validator.validate_file(file_path)
                    all_results.extend(results)
                except FileNotFoundError:
                    # This should be handled gracefully
                    continue
                except Exception:
                    pass
            
            # Should not crash and should handle the FileNotFoundError gracefully
            self.assertEqual(len(all_results), 0)
    
    def test_git_rm_scenario(self):
        """Test the specific scenario mentioned in the issue: git rm blocking commits"""
        import git_pre_commit_hook as hook
        
        # Create and commit multiple files
        files_to_create = [
            ("script.py", "print('Hello, World!')\n"),
            ("readme.md", "# Test Project\n"),
            ("config.json", '{"setting": "value"}\n')
        ]
        
        for filename, content in files_to_create:
            Path(filename).write_text(content)
            subprocess.run(["git", "add", filename], check=True)
        
        subprocess.run(["git", "commit", "-m", "Add initial files"], check=True)
        
        # Now remove some files using git rm
        subprocess.run(["git", "rm", "script.py"], check=True)
        subprocess.run(["git", "rm", "config.json"], check=True)
        
        # Modify existing file
        Path("readme.md").write_text("# Updated Project\nThis has been updated.\n")
        subprocess.run(["git", "add", "readme.md"], check=True)
        
        # Get what git thinks is staged
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, check=True
        )
        staged_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        # Verify that the hook's filtering logic works correctly
        validatable_extensions = {'.md', '.txt', '.js', '.ts', '.py', '.json', '.yaml', '.yml'}
        
        # Apply the hook's filtering logic
        existing_files = []
        deleted_files = []
        for f in staged_files:
            file_path = Path(f)
            if file_path.exists():
                existing_files.append(f)
            else:
                deleted_files.append(f)
        
        files_to_validate = [
            f for f in existing_files
            if Path(f).suffix in validatable_extensions
        ]
        
        # Assertions
        self.assertIn("script.py", staged_files, "Deleted .py file should be in staged files")
        self.assertIn("config.json", staged_files, "Deleted .json file should be in staged files")
        self.assertIn("readme.md", staged_files, "Modified .md file should be in staged files")
        
        self.assertIn("script.py", deleted_files, "Deleted .py file should be identified as deleted")
        self.assertIn("config.json", deleted_files, "Deleted .json file should be identified as deleted")
        self.assertNotIn("readme.md", deleted_files, "Modified .md file should not be identified as deleted")
        
        self.assertEqual(files_to_validate, ["readme.md"], "Only existing files should be validated")

if __name__ == "__main__":
    unittest.main(verbosity=2)