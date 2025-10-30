"""
Aurora Code Improvement Engine

Automated code quality enhancement system with:
- Pattern-based improvement detection
- Refactoring suggestion engine
- Performance optimization detection
- Integration with existing quality tools
- Safe automated improvements with human oversight

Architecture: Builds on existing quality analysis infrastructure
"""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class ImprovementCategory(str, Enum):
    """Categories of code improvements"""
    REFACTORING = "refactoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    READABILITY = "readability"
    MAINTAINABILITY = "maintainability"
    TESTING = "testing"


class ImprovementSeverity(str, Enum):
    """Severity levels for improvements"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ImprovementSuggestion:
    """A single code improvement suggestion"""
    file_path: str
    line_number: int
    category: ImprovementCategory
    severity: ImprovementSeverity
    description: str
    rationale: str
    suggested_fix: Optional[str] = None
    automated_fix_available: bool = False
    safe_to_auto_apply: bool = False
    confidence_score: float = 0.0
    context_lines: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "category": self.category.value,
            "severity": self.severity.value,
            "description": self.description,
            "rationale": self.rationale,
            "suggested_fix": self.suggested_fix,
            "automated_fix_available": self.automated_fix_available,
            "safe_to_auto_apply": self.safe_to_auto_apply,
            "confidence_score": self.confidence_score
        }


class ImprovementPattern:
    """Base class for improvement detection patterns"""
    
    def __init__(self, name: str, category: ImprovementCategory, severity: ImprovementSeverity):
        self.name = name
        self.category = category
        self.severity = severity
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        """Detect improvement opportunities in file content"""
        raise NotImplementedError


class ComplexityPattern(ImprovementPattern):
    """Detect functions with high complexity"""
    
    def __init__(self):
        super().__init__(
            "high_complexity",
            ImprovementCategory.REFACTORING,
            ImprovementSeverity.MEDIUM
        )
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        suggestions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Simple heuristic: multiple nested if/for/while
            if line.strip().startswith(('if ', 'for ', 'while ')):
                indent_level = len(line) - len(line.lstrip())
                if indent_level >= 16:  # 4+ levels of nesting
                    suggestions.append(ImprovementSuggestion(
                        file_path=file_path,
                        line_number=i,
                        category=self.category,
                        severity=self.severity,
                        description="High nesting complexity detected",
                        rationale="Deep nesting reduces readability. Consider extracting to separate functions.",
                        suggested_fix="Extract nested logic into well-named helper functions",
                        automated_fix_available=False,
                        safe_to_auto_apply=False,
                        confidence_score=0.8,
                        context_lines=lines[max(0, i-2):min(len(lines), i+2)]
                    ))
        
        return suggestions


class DuplicateCodePattern(ImprovementPattern):
    """Detect duplicate code blocks"""
    
    def __init__(self):
        super().__init__(
            "duplicate_code",
            ImprovementCategory.REFACTORING,
            ImprovementSeverity.MEDIUM
        )
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        suggestions = []
        lines = content.split('\n')
        
        # Simple duplicate detection: look for repeated patterns
        code_blocks = {}
        block_size = 5
        
        for i in range(len(lines) - block_size):
            block = '\n'.join(lines[i:i+block_size])
            normalized = re.sub(r'\s+', ' ', block).strip()
            
            if normalized and len(normalized) > 50:  # Meaningful blocks
                if normalized in code_blocks:
                    suggestions.append(ImprovementSuggestion(
                        file_path=file_path,
                        line_number=i + 1,
                        category=self.category,
                        severity=self.severity,
                        description=f"Duplicate code block detected (also at line {code_blocks[normalized]})",
                        rationale="Duplicate code increases maintenance burden. Extract to reusable function.",
                        suggested_fix="Create shared function for common logic",
                        automated_fix_available=False,
                        safe_to_auto_apply=False,
                        confidence_score=0.75
                    ))
                else:
                    code_blocks[normalized] = i + 1
        
        return suggestions


class LongFunctionPattern(ImprovementPattern):
    """Detect overly long functions"""
    
    def __init__(self):
        super().__init__(
            "long_function",
            ImprovementCategory.MAINTAINABILITY,
            ImprovementSeverity.LOW
        )
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        suggestions = []
        lines = content.split('\n')
        
        in_function = False
        function_start = 0
        function_name = ""
        
        for i, line in enumerate(lines, 1):
            # Simple Python function detection
            if line.strip().startswith('def '):
                if in_function and (i - function_start) > 50:
                    suggestions.append(ImprovementSuggestion(
                        file_path=file_path,
                        line_number=function_start,
                        category=self.category,
                        severity=self.severity,
                        description=f"Function '{function_name}' is too long ({i - function_start} lines)",
                        rationale="Long functions are harder to understand and test. Consider breaking into smaller functions.",
                        suggested_fix="Split function into logical sub-functions",
                        automated_fix_available=False,
                        safe_to_auto_apply=False,
                        confidence_score=0.9
                    ))
                
                in_function = True
                function_start = i
                match = re.search(r'def\s+(\w+)', line)
                function_name = match.group(1) if match else "unknown"
        
        return suggestions


class MagicNumberPattern(ImprovementPattern):
    """Detect magic numbers that should be named constants"""
    
    def __init__(self):
        super().__init__(
            "magic_numbers",
            ImprovementCategory.READABILITY,
            ImprovementSeverity.LOW
        )
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        suggestions = []
        lines = content.split('\n')
        
        # Exclude common/acceptable numbers
        acceptable_numbers = {0, 1, -1, 2, 10, 100, 1000}
        
        for i, line in enumerate(lines, 1):
            # Find numeric literals (simplified)
            numbers = re.findall(r'\b(\d{3,})\b', line)
            for num_str in numbers:
                num = int(num_str)
                if num not in acceptable_numbers:
                    suggestions.append(ImprovementSuggestion(
                        file_path=file_path,
                        line_number=i,
                        category=self.category,
                        severity=self.severity,
                        description=f"Magic number detected: {num}",
                        rationale="Magic numbers reduce code clarity. Use named constants.",
                        suggested_fix=f"Replace with named constant (e.g., MAX_ITEMS = {num})",
                        automated_fix_available=False,
                        safe_to_auto_apply=False,
                        confidence_score=0.7
                    ))
        
        return suggestions


class ErrorHandlingPattern(ImprovementPattern):
    """Detect missing error handling"""
    
    def __init__(self):
        super().__init__(
            "error_handling",
            ImprovementCategory.SECURITY,
            ImprovementSeverity.HIGH
        )
    
    def detect(self, file_path: str, content: str) -> List[ImprovementSuggestion]:
        suggestions = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Detect risky operations without try/except
            risky_ops = ['open(', '.read(', '.write(', 'json.loads(', 'int(', 'float(']
            
            if any(op in line for op in risky_ops):
                # Check if within try block (simplified)
                context_start = max(0, i - 5)
                context = lines[context_start:i]
                has_try = any('try:' in l for l in context)
                
                if not has_try:
                    suggestions.append(ImprovementSuggestion(
                        file_path=file_path,
                        line_number=i,
                        category=self.category,
                        severity=self.severity,
                        description="Potentially risky operation without error handling",
                        rationale="Unhandled exceptions can crash application. Add try/except.",
                        suggested_fix="Wrap in try/except block with appropriate error handling",
                        automated_fix_available=False,
                        safe_to_auto_apply=False,
                        confidence_score=0.6
                    ))
        
        return suggestions


class CodeImprovementEngine:
    """
    Main improvement engine coordinating pattern detection and suggestions
    
    Features:
    - Multiple improvement pattern detection
    - Confidence-based filtering
    - Category and severity prioritization
    - Integration with existing quality tools
    - Safe automation boundaries
    """
    
    def __init__(self):
        self._patterns: List[ImprovementPattern] = []
        self._register_default_patterns()
    
    def _register_default_patterns(self):
        """Register built-in improvement patterns"""
        self._patterns.extend([
            ComplexityPattern(),
            DuplicateCodePattern(),
            LongFunctionPattern(),
            MagicNumberPattern(),
            ErrorHandlingPattern()
        ])
    
    def register_pattern(self, pattern: ImprovementPattern):
        """Register custom improvement pattern"""
        self._patterns.append(pattern)
        logger.info("Registered improvement pattern: %s", pattern.name)
    
    def analyze_file(self, file_path: Path) -> List[ImprovementSuggestion]:
        """
        Analyze single file for improvement opportunities
        
        Args:
            file_path: Path to file to analyze
        
        Returns:
            List of improvement suggestions
        """
        try:
            content = file_path.read_text()
        except Exception as e:
            logger.error("Failed to read file %s: %s", file_path, e)
            return []
        
        suggestions = []
        for pattern in self._patterns:
            try:
                pattern_suggestions = pattern.detect(str(file_path), content)
                suggestions.extend(pattern_suggestions)
            except Exception as e:
                logger.error("Pattern %s failed on %s: %s", pattern.name, file_path, e)
        
        return suggestions
    
    def analyze_directory(
        self,
        directory: Path,
        file_patterns: Optional[List[str]] = None
    ) -> Dict[str, List[ImprovementSuggestion]]:
        """
        Analyze directory for improvements
        
        Args:
            directory: Directory to scan
            file_patterns: Glob patterns for files to analyze (default: ["*.py"])
        
        Returns:
            Dict mapping file paths to suggestions
        """
        if file_patterns is None:
            file_patterns = ["*.py"]
        
        results = {}
        
        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    suggestions = self.analyze_file(file_path)
                    if suggestions:
                        results[str(file_path)] = suggestions
        
        logger.info("Analyzed directory %s: found improvements in %d files", directory, len(results))
        return results
    
    def filter_suggestions(
        self,
        suggestions: List[ImprovementSuggestion],
        min_confidence: float = 0.5,
        categories: Optional[Set[ImprovementCategory]] = None,
        severities: Optional[Set[ImprovementSeverity]] = None
    ) -> List[ImprovementSuggestion]:
        """
        Filter suggestions by criteria
        
        Args:
            suggestions: List of suggestions to filter
            min_confidence: Minimum confidence score
            categories: Filter by categories (None = all)
            severities: Filter by severities (None = all)
        
        Returns:
            Filtered list of suggestions
        """
        filtered = suggestions
        
        # Filter by confidence
        filtered = [s for s in filtered if s.confidence_score >= min_confidence]
        
        # Filter by category
        if categories:
            filtered = [s for s in filtered if s.category in categories]
        
        # Filter by severity
        if severities:
            filtered = [s for s in filtered if s.severity in severities]
        
        return filtered
    
    def generate_report(
        self,
        analysis_results: Dict[str, List[ImprovementSuggestion]]
    ) -> Dict[str, Any]:
        """
        Generate improvement report
        
        Args:
            analysis_results: Results from analyze_directory()
        
        Returns:
            Report dictionary with statistics and suggestions
        """
        total_suggestions = sum(len(suggestions) for suggestions in analysis_results.values())
        
        # Group by category
        by_category = {}
        for suggestions in analysis_results.values():
            for suggestion in suggestions:
                category = suggestion.category.value
                by_category[category] = by_category.get(category, 0) + 1
        
        # Group by severity
        by_severity = {}
        for suggestions in analysis_results.values():
            for suggestion in suggestions:
                severity = suggestion.severity.value
                by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Count auto-fixable
        auto_fixable = sum(
            1 for suggestions in analysis_results.values()
            for s in suggestions if s.automated_fix_available
        )
        
        safe_auto_apply = sum(
            1 for suggestions in analysis_results.values()
            for s in suggestions if s.safe_to_auto_apply
        )
        
        return {
            "total_files_analyzed": len(analysis_results),
            "total_suggestions": total_suggestions,
            "by_category": by_category,
            "by_severity": by_severity,
            "automated_fix_available": auto_fixable,
            "safe_to_auto_apply": safe_auto_apply,
            "suggestions": {
                file_path: [s.to_dict() for s in suggestions]
                for file_path, suggestions in analysis_results.items()
            }
        }


# Global engine instance
_global_engine: Optional[CodeImprovementEngine] = None


def get_improvement_engine() -> CodeImprovementEngine:
    """Get or create global improvement engine"""
    global _global_engine
    if _global_engine is None:
        _global_engine = CodeImprovementEngine()
    return _global_engine


def reset_improvement_engine():
    """Reset global engine (useful for testing)"""
    global _global_engine
    _global_engine = None
