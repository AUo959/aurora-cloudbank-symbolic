#!/usr/bin/env python3
"""
Test Suite for Git Pre-Commit Hook
Anchor: T1_TEST_VALIDATOR
Team: Aurora/GUMAS
Version: 1.0.0
"""

import unittest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

import git_pre_commit_hook as hook

class TestPreCommitHook(unittest.TestCase):
    """Test cases for symbolic pre-commit validation"""

    def test_entropy_logging(self):
        with patch('sys.stderr') as _:
            hook.log_entropy_state("Test message")
            # Smoke test: ensure no exceptions and basic call path works

    def test_seal_validation_state(self):
        files = ["file1.py", "file2.md", "file3.yaml"]
        sealed = hook.seal_validation_state(files, True)
        self.assertIn("timestamp", sealed)
        self.assertIn("anchor", sealed)
        self.assertIn("seal", sealed)
        self.assertEqual(sealed["files_count"], 3)
        self.assertTrue(sealed["validation_result"])
        self.assertEqual(len(sealed["seal"]), 64)

    def test_get_staged_files(self):
        mock_result = MagicMock()
        mock_result.stdout = "file1.py\nfile2.md\n"
        with patch('subprocess.run', return_value=mock_result):
            files = hook.get_staged_files()
            self.assertEqual(files, ["file1.py", "file2.md"])

    def test_validator_stub_path(self):
        # Simulate absence by reloading module with failing imports
        with patch.dict('sys.modules', {'canonical_validator': None, 'validation': None}):
            # Re-import module source code into a new namespace by executing file
            src = Path(__file__).parent / 'git_pre_commit_hook.py'
            code = src.read_text(encoding='utf-8')
            ns = {"__name__": "__test__", "__file__": str(src)}
            # Execution should sys.exit(0) due to stub path early exit
            with self.assertRaises(SystemExit) as cm:
                exec(compile(code, str(src), 'exec'), ns)
            self.assertEqual(cm.exception.code, 0)

if __name__ == "__main__":
    print(f"[TEST] Starting validation tests @ {datetime.now(timezone.utc).isoformat()}")
    unittest.main(verbosity=2)