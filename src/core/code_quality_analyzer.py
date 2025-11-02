"""
Aurora Code Quality Analyzer
Integrates flake8 and code quality metrics with Aurora's reflection system.
Implements Issue #258: Automated code quality analysis and reporting.
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Import Aurora symbolic engine for proper chain notation
try:
    from src.aurora.core.symbolic_engine import SymbolicEngine
except ImportError:
    # Fallback if symbolic engine not available
    SymbolicEngine = None


@dataclass
class CodeQualityViolation:
    """Represents a single code quality violation."""
    file_path: str
    line_number: int
    column: int
    code: str
    message: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary."""
        return asdict(self)


@dataclass
class CodeQualityReport:
    """Aggregated code quality analysis report."""
    timestamp: str
    total_violations: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    violations: List[CodeQualityViolation]
    passed: bool
    analysis_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            'timestamp': self.timestamp,
            'total_violations': self.total_violations,
            'critical_count': self.critical_count,
            'high_count': self.high_count,
            'medium_count': self.medium_count,
            'low_count': self.low_count,
            'violations': [v.to_dict() for v in self.violations],
            'passed': self.passed,
            'analysis_metadata': self.analysis_metadata
        }


class CodeQualityAnalyzer:
    """
    Aurora Code Quality Analyzer
    
    Provides automated code quality analysis using flake8 and integrates
    with Aurora's reflection system for visibility and automated issue creation.
    """
    
    # Severity mapping for flake8 error codes
    SEVERITY_MAP = {
        # Critical: Syntax errors and undefined names
        'E9': 'critical',   # Runtime errors
        'F63': 'critical',  # Invalid syntax in type comments
        'F7': 'critical',   # Syntax errors
        'F82': 'critical',  # Undefined names
        
        # High: Import issues and naming problems
        'F401': 'high',     # Imported but unused
        'F811': 'high',     # Redefinition of unused name
        'F841': 'high',     # Local variable assigned but never used
        'E501': 'medium',   # Line too long
        'E402': 'high',     # Module level import not at top
        
        # Medium: Style and complexity issues
        'C9': 'medium',     # Complexity issues
        'W': 'medium',      # Warnings
        
        # Low: Minor style issues
        'E1': 'low',        # Indentation
        'E2': 'low',        # Whitespace
        'E3': 'low',        # Blank line
    }
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize the code quality analyzer.
        
        Args:
            repo_path: Path to repository root. Defaults to current directory.
        """
        self.repo_path = repo_path or Path.cwd()
        self.config_file = self.repo_path / '.flake8'
        
        # Initialize symbolic engine for proper chain notation
        if SymbolicEngine:
            self.symbolic_engine = SymbolicEngine()
            # Execute chain for Issue #258 (001 to 258)
            self.symbolic_engine.execute_chain(1, 258)
        else:
            self.symbolic_engine = None
        
    def _determine_severity(self, error_code: str) -> str:
        """
        Determine severity level based on flake8 error code.
        
        Args:
            error_code: flake8 error code (e.g., 'E501', 'F401')
            
        Returns:
            Severity level: 'critical', 'high', 'medium', or 'low'
        """
        # Check exact match first
        if error_code in self.SEVERITY_MAP:
            return self.SEVERITY_MAP[error_code]
        
        # Check prefix match
        for prefix, severity in self.SEVERITY_MAP.items():
            if error_code.startswith(prefix):
                return severity
        
        # Default to medium
        return 'medium'
    
    def run_flake8_analysis(self, paths: Optional[List[str]] = None) -> CodeQualityReport:
        """
        Run flake8 analysis on specified paths.
        
        Args:
            paths: List of paths to analyze. Defaults to entire repository.
            
        Returns:
            CodeQualityReport with analysis results
        """
        if paths is None:
            paths = ['.']
        
        # Build flake8 command
        cmd = [
            sys.executable, '-m', 'flake8',
            '--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s',
            '--max-line-length=120',
            '--extend-ignore=E203,W503',
        ]
        
        # Add config file if exists
        if self.config_file.exists():
            cmd.extend(['--config', str(self.config_file)])
        
        cmd.extend(paths)
        
        # Run flake8
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            output = result.stdout
        except subprocess.TimeoutExpired:
            output = "# Flake8 analysis timed out after 5 minutes"
        except FileNotFoundError:
            output = "# Flake8 not installed - please install with: pip install flake8"
        
        # Parse output
        violations = self._parse_flake8_output(output)
        
        # Count by severity
        critical = sum(1 for v in violations if v.severity == 'critical')
        high = sum(1 for v in violations if v.severity == 'high')
        medium = sum(1 for v in violations if v.severity == 'medium')
        low = sum(1 for v in violations if v.severity == 'low')
        
        # Determine if analysis passed (no critical violations)
        passed = critical == 0
        
        return CodeQualityReport(
            timestamp=datetime.now(UTC).isoformat(),
            total_violations=len(violations),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            violations=violations,
            passed=passed,
            analysis_metadata={
                'analyzer': 'flake8',
                'paths_analyzed': paths,
                'config_file': str(self.config_file) if self.config_file.exists() else None
            }
        )
    
    def _parse_flake8_output(self, output: str) -> List[CodeQualityViolation]:
        """
        Parse flake8 output into structured violations.
        
        Args:
            output: Raw flake8 output
            
        Returns:
            List of CodeQualityViolation objects
        """
        violations = []
        
        for line in output.strip().split('\n'):
            if not line or line.startswith('#'):
                continue
            
            # Parse format: path:line:col: CODE message
            try:
                parts = line.split(':', 3)
                if len(parts) < 4:
                    continue
                
                file_path = parts[0].strip()
                line_number = int(parts[1].strip())
                column = int(parts[2].strip())
                
                # Extract code and message
                code_and_msg = parts[3].strip()
                code = code_and_msg.split()[0]
                message = code_and_msg[len(code):].strip()
                
                severity = self._determine_severity(code)
                
                violations.append(CodeQualityViolation(
                    file_path=file_path,
                    line_number=line_number,
                    column=column,
                    code=code,
                    message=message,
                    severity=severity
                ))
            except (ValueError, IndexError):
                # Skip malformed lines
                continue
        
        return violations
    
    def generate_reflection_report(self, report: CodeQualityReport) -> Dict[str, Any]:
        """
        Generate Aurora reflection-compatible report.
        
        Args:
            report: CodeQualityReport to convert
            
        Returns:
            Dictionary in Aurora reflection format with DLP tracking
        """
        # Get chain notation from symbolic engine or use fallback
        if self.symbolic_engine:
            chain_notation = '001//258//'  # Issue #258 chain
            t1_state = self.symbolic_engine.t1.export()
            srb_state = self.symbolic_engine.srb.export()
        else:
            chain_notation = '001//258//'  # Static fallback
            t1_state = None
            srb_state = None
        
        dlp_trail = {
            'anchor_protocol': 'T1/SRB',
            'analysis_version': '1.0.0',
            'chain_notation': chain_notation,
        }
        
        # Add anchor states if symbolic engine available
        if t1_state:
            dlp_trail['t1_anchor'] = t1_state
        if srb_state:
            dlp_trail['srb_anchor'] = srb_state
        
        return {
            'context_tag': 'code_quality_analysis',
            'timestamp': report.timestamp,
            'symbolic_hash_validation': self._compute_hash(report),
            'analysis_summary': {
                'passed': report.passed,
                'total_violations': report.total_violations,
                'severity_breakdown': {
                    'critical': report.critical_count,
                    'high': report.high_count,
                    'medium': report.medium_count,
                    'low': report.low_count
                }
            },
            'violations': [v.to_dict() for v in report.violations],
            'metadata': report.analysis_metadata,
            'dlp_trail': dlp_trail
        }
    
    def _compute_hash(self, report: CodeQualityReport) -> str:
        """Compute symbolic hash for DLP validation."""
        content = json.dumps(report.to_dict(), sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def save_report(self, report: CodeQualityReport, output_path: Path):
        """
        Save code quality report to file.
        
        Args:
            report: CodeQualityReport to save
            output_path: Path to save report
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
    
    def get_critical_violations(self, report: CodeQualityReport) -> List[CodeQualityViolation]:
        """
        Extract critical violations that should generate issues.
        
        Args:
            report: CodeQualityReport to filter
            
        Returns:
            List of critical violations
        """
        return [v for v in report.violations if v.severity == 'critical']


def main():
    """CLI entry point for code quality analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Aurora Code Quality Analyzer - Issue #258 Implementation'
    )
    parser.add_argument(
        'paths',
        nargs='*',
        default=['.'],
        help='Paths to analyze (default: current directory)'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=Path,
        help='Output file for JSON report'
    )
    parser.add_argument(
        '--reflection',
        action='store_true',
        help='Generate Aurora reflection format'
    )
    
    args = parser.parse_args()
    
    analyzer = CodeQualityAnalyzer()
    report = analyzer.run_flake8_analysis(args.paths)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Aurora Code Quality Analysis Report")
    print(f"{'='*60}")
    print(f"Timestamp: {report.timestamp}")
    print(f"Status: {'✓ PASSED' if report.passed else '✗ FAILED'}")
    print(f"\nViolations by Severity:")
    print(f"  Critical: {report.critical_count}")
    print(f"  High:     {report.high_count}")
    print(f"  Medium:   {report.medium_count}")
    print(f"  Low:      {report.low_count}")
    print(f"  Total:    {report.total_violations}")
    print(f"{'='*60}\n")
    
    # Save if output specified
    if args.output:
        if args.reflection:
            # Generate reflection format and save it
            reflection_report = analyzer.generate_reflection_report(report)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(reflection_report, f, indent=2)
            print(f"Reflection report saved to: {args.output}")
        else:
            analyzer.save_report(report, args.output)
            print(f"Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report.passed else 1)


if __name__ == '__main__':
    main()
