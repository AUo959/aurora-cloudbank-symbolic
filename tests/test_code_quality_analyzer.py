"""
Tests for Aurora Code Quality Analyzer
Part of Issue #258: Automated code quality analysis
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timezone

# Import the modules we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.code_quality_analyzer import (
    CodeQualityAnalyzer,
    CodeQualityViolation,
    CodeQualityReport
)


class TestCodeQualityViolation:
    """Test CodeQualityViolation dataclass."""
    
    def test_violation_creation(self):
        """Test creating a violation object."""
        violation = CodeQualityViolation(
            file_path="src/test.py",
            line_number=10,
            column=5,
            code="E501",
            message="line too long",
            severity="medium"
        )
        
        assert violation.file_path == "src/test.py"
        assert violation.line_number == 10
        assert violation.code == "E501"
        assert violation.severity == "medium"
    
    def test_violation_to_dict(self):
        """Test converting violation to dictionary."""
        violation = CodeQualityViolation(
            file_path="src/test.py",
            line_number=10,
            column=5,
            code="E501",
            message="line too long",
            severity="medium"
        )
        
        result = violation.to_dict()
        
        assert isinstance(result, dict)
        assert result['file_path'] == "src/test.py"
        assert result['code'] == "E501"
        assert result['severity'] == "medium"


class TestCodeQualityReport:
    """Test CodeQualityReport dataclass."""
    
    def test_report_creation(self):
        """Test creating a report object."""
        violations = [
            CodeQualityViolation("test.py", 1, 1, "E501", "msg", "medium")
        ]
        
        report = CodeQualityReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_violations=1,
            critical_count=0,
            high_count=0,
            medium_count=1,
            low_count=0,
            violations=violations,
            passed=True,
            analysis_metadata={}
        )
        
        assert report.total_violations == 1
        assert report.medium_count == 1
        assert report.passed is True
    
    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        violations = [
            CodeQualityViolation("test.py", 1, 1, "E501", "msg", "medium")
        ]
        
        report = CodeQualityReport(
            timestamp="2025-01-01T00:00:00Z",
            total_violations=1,
            critical_count=0,
            high_count=0,
            medium_count=1,
            low_count=0,
            violations=violations,
            passed=True,
            analysis_metadata={"test": "data"}
        )
        
        result = report.to_dict()
        
        assert isinstance(result, dict)
        assert result['total_violations'] == 1
        assert len(result['violations']) == 1
        assert result['analysis_metadata']['test'] == "data"


class TestCodeQualityAnalyzer:
    """Test CodeQualityAnalyzer class."""
    
    def test_analyzer_initialization(self, tmp_path):
        """Test analyzer initialization."""
        analyzer = CodeQualityAnalyzer(repo_path=tmp_path)
        
        assert analyzer.repo_path == tmp_path
        assert analyzer.config_file == tmp_path / '.flake8'
    
    def test_determine_severity_critical(self):
        """Test severity determination for critical errors."""
        analyzer = CodeQualityAnalyzer()
        
        assert analyzer._determine_severity('E9') == 'critical'
        assert analyzer._determine_severity('F82') == 'critical'
        assert analyzer._determine_severity('F7') == 'critical'
    
    def test_determine_severity_high(self):
        """Test severity determination for high errors."""
        analyzer = CodeQualityAnalyzer()
        
        assert analyzer._determine_severity('F401') == 'high'
        assert analyzer._determine_severity('F811') == 'high'
        assert analyzer._determine_severity('E402') == 'high'
    
    def test_determine_severity_medium(self):
        """Test severity determination for medium errors."""
        analyzer = CodeQualityAnalyzer()
        
        assert analyzer._determine_severity('E501') == 'medium'
        assert analyzer._determine_severity('C901') == 'medium'
        assert analyzer._determine_severity('W503') == 'medium'
    
    def test_determine_severity_low(self):
        """Test severity determination for low errors."""
        analyzer = CodeQualityAnalyzer()
        
        assert analyzer._determine_severity('E101') == 'low'
        assert analyzer._determine_severity('E201') == 'low'
        assert analyzer._determine_severity('E301') == 'low'
    
    def test_parse_flake8_output_single_violation(self):
        """Test parsing single flake8 violation."""
        analyzer = CodeQualityAnalyzer()
        
        output = "src/test.py:10:5: E501 line too long (121 > 120 characters)"
        violations = analyzer._parse_flake8_output(output)
        
        assert len(violations) == 1
        assert violations[0].file_path == "src/test.py"
        assert violations[0].line_number == 10
        assert violations[0].column == 5
        assert violations[0].code == "E501"
        assert "line too long" in violations[0].message
        assert violations[0].severity == "medium"
    
    def test_parse_flake8_output_multiple_violations(self):
        """Test parsing multiple flake8 violations."""
        analyzer = CodeQualityAnalyzer()
        
        output = """src/test.py:10:5: E501 line too long
src/test.py:20:1: F401 module imported but unused
src/test.py:30:10: E9 SyntaxError"""
        
        violations = analyzer._parse_flake8_output(output)
        
        assert len(violations) == 3
        assert violations[0].code == "E501"
        assert violations[1].code == "F401"
        assert violations[2].code == "E9"
        assert violations[2].severity == "critical"
    
    def test_parse_flake8_output_ignores_comments(self):
        """Test that parser ignores comment lines."""
        analyzer = CodeQualityAnalyzer()
        
        output = """# This is a comment
src/test.py:10:5: E501 line too long
# Another comment"""
        
        violations = analyzer._parse_flake8_output(output)
        
        assert len(violations) == 1
    
    def test_parse_flake8_output_handles_malformed_lines(self):
        """Test that parser handles malformed lines gracefully."""
        analyzer = CodeQualityAnalyzer()
        
        output = """src/test.py:10:5: E501 line too long
malformed line without proper format
src/test.py:20:1: F401 unused import"""
        
        violations = analyzer._parse_flake8_output(output)
        
        # Should only parse the valid lines
        assert len(violations) == 2
    
    def test_generate_reflection_report(self):
        """Test generating Aurora reflection report."""
        analyzer = CodeQualityAnalyzer()
        
        violations = [
            CodeQualityViolation("test.py", 1, 1, "E501", "msg", "medium")
        ]
        
        report = CodeQualityReport(
            timestamp="2025-01-01T00:00:00Z",
            total_violations=1,
            critical_count=0,
            high_count=0,
            medium_count=1,
            low_count=0,
            violations=violations,
            passed=True,
            analysis_metadata={"analyzer": "flake8"}
        )
        
        reflection = analyzer.generate_reflection_report(report)
        
        assert reflection['context_tag'] == 'code_quality_analysis'
        assert 'symbolic_hash_validation' in reflection
        assert reflection['analysis_summary']['passed'] is True
        assert reflection['analysis_summary']['total_violations'] == 1
        assert reflection['dlp_trail']['chain_notation'] == '001//258//'
    
    def test_get_critical_violations(self):
        """Test filtering critical violations."""
        analyzer = CodeQualityAnalyzer()
        
        violations = [
            CodeQualityViolation("test.py", 1, 1, "E501", "msg", "medium"),
            CodeQualityViolation("test.py", 2, 1, "F82", "msg", "critical"),
            CodeQualityViolation("test.py", 3, 1, "F401", "msg", "high"),
        ]
        
        report = CodeQualityReport(
            timestamp="2025-01-01T00:00:00Z",
            total_violations=3,
            critical_count=1,
            high_count=1,
            medium_count=1,
            low_count=0,
            violations=violations,
            passed=False,
            analysis_metadata={}
        )
        
        critical = analyzer.get_critical_violations(report)
        
        assert len(critical) == 1
        assert critical[0].severity == "critical"
        assert critical[0].code == "F82"
    
    def test_save_report(self, tmp_path):
        """Test saving report to file."""
        analyzer = CodeQualityAnalyzer()
        
        violations = [
            CodeQualityViolation("test.py", 1, 1, "E501", "msg", "medium")
        ]
        
        report = CodeQualityReport(
            timestamp="2025-01-01T00:00:00Z",
            total_violations=1,
            critical_count=0,
            high_count=0,
            medium_count=1,
            low_count=0,
            violations=violations,
            passed=True,
            analysis_metadata={}
        )
        
        output_path = tmp_path / "reports" / "test_report.json"
        analyzer.save_report(report, output_path)
        
        assert output_path.exists()
        
        # Verify content
        with open(output_path) as f:
            saved_data = json.load(f)
        
        assert saved_data['total_violations'] == 1
        assert saved_data['passed'] is True
    
    @patch('subprocess.run')
    def test_run_flake8_analysis_success(self, mock_run, tmp_path):
        """Test running flake8 analysis successfully."""
        mock_run.return_value = Mock(
            stdout="src/test.py:10:5: E501 line too long",
            returncode=0
        )
        
        analyzer = CodeQualityAnalyzer(repo_path=tmp_path)
        report = analyzer.run_flake8_analysis(['src'])
        
        assert report.total_violations == 1
        assert report.medium_count == 1
        assert report.passed is True  # No critical violations
    
    @patch('subprocess.run')
    def test_run_flake8_analysis_with_critical(self, mock_run, tmp_path):
        """Test running flake8 analysis with critical violations."""
        mock_run.return_value = Mock(
            stdout="src/test.py:10:5: F82 undefined name 'x'",
            returncode=1
        )
        
        analyzer = CodeQualityAnalyzer(repo_path=tmp_path)
        report = analyzer.run_flake8_analysis(['src'])
        
        assert report.total_violations == 1
        assert report.critical_count == 1
        assert report.passed is False  # Has critical violations
    
    @patch('subprocess.run')
    def test_run_flake8_analysis_timeout(self, mock_run, tmp_path):
        """Test handling flake8 timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='flake8', timeout=300)
        
        analyzer = CodeQualityAnalyzer(repo_path=tmp_path)
        report = analyzer.run_flake8_analysis()
        
        # Should handle timeout gracefully
        assert report is not None


@pytest.mark.unit
class TestCodeQualityIntegration:
    """Integration tests for code quality analysis."""
    
    def test_full_analysis_workflow(self, tmp_path):
        """Test complete analysis workflow."""
        # Create test Python file with violations
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
import sys

def test():
    x = 1  # F841: local variable assigned but never used
    print("This is a very long line that exceeds the 120 character limit and should trigger an E501 violation")
""")
        
        analyzer = CodeQualityAnalyzer(repo_path=tmp_path)
        
        # Note: This test would require flake8 to be installed
        # For unit testing, we'll just verify the analyzer can be instantiated
        assert analyzer.repo_path == tmp_path


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
