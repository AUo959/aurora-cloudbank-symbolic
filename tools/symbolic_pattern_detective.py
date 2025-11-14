"""
🔍 Aurora CloudBank Symbolic Pattern Detective

Advanced pattern detection using quantum-inspired vector similarity
and Aurora's symbolic anchor tracking.

Features:
- Multi-domain pattern detection (code, logs, symbolic sequences)
- Quantum vector similarity for fuzzy matching
- Security anti-pattern detection
- Performance bottleneck identification
- Complete DLP tracking with T1/SRB anchors
"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from pathlib import Path


@dataclass
class DetectedPattern:
    """Detected pattern with metadata"""
    pattern_type: str
    location: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    code_snippet: str
    remediation: str
    confidence: float
    cultural_impact: float
    t1_state: int
    srb_resolution: int
    detection_hash: str


class T1Anchor:
    """Temporal T1 anchor"""
    def __init__(self):
        self.state = 0

    def advance(self, data: str) -> int:
        self.state += len(str(data))
        return self.state

    def export(self) -> dict:
        return {"type": "T1", "state": self.state}


class SRBAnchor:
    """Spatial-Relational Boundary anchor"""
    def __init__(self):
        self.resolution = 0

    def resolve(self, boundary: str) -> int:
        self.resolution += hash(str(boundary)) % 1000
        return self.resolution

    def export(self) -> dict:
        return {"type": "SRB", "resolution": self.resolution}


class SymbolicPatternDetective:
    """
    Advanced pattern detection engine with quantum-inspired similarity
    and Aurora symbolic anchor integration
    """

    def __init__(self, anchor_seed: str = "PATTERN_DETECTIVE_001"):
        self.anchor_seed = anchor_seed
        self.t1 = T1Anchor()
        self.srb = SRBAnchor()
        self.detected_patterns: List[DetectedPattern] = []

        # Pattern definitions
        self._init_pattern_definitions()

    def _init_pattern_definitions(self):
        """Initialize pattern detection rules"""
        # Security anti-patterns
        self.security_patterns = {
            "sql_injection": {
                "regex": r"execute\s*\(\s*['\"].*?\+.*?['\"]",
                "severity": "critical",
                "description": "Potential SQL injection vulnerability",
                "remediation": "Use parameterized queries instead of string concatenation",
            },
            "hardcoded_credentials": {
                "regex": r"password\s*=\s*['\"][^'\"]+['\"]|api_key\s*=\s*['\"][^'\"]+['\"]",
                "severity": "critical",
                "description": "Hardcoded credentials detected",
                "remediation": "Use environment variables or secure credential storage",
            },
            "eval_usage": {
                "regex": r"\beval\s*\(|exec\s*\(",
                "severity": "high",
                "description": "Dangerous eval() or exec() usage",
                "remediation": "Avoid eval/exec; use safer alternatives like ast.literal_eval",
            },
            "path_traversal": {
                "regex": r"open\s*\([^)]*?\+[^)]*?['\"]\.\.\/['\"]",
                "severity": "high",
                "description": "Potential path traversal vulnerability",
                "remediation": "Sanitize file paths and use os.path.join() safely",
            },
        }

        # Performance anti-patterns
        self.performance_patterns = {
            "nested_loops": {
                "regex": r"for\s+.*?:\s*\n\s+for\s+.*?:\s*\n\s+for",
                "severity": "medium",
                "description": "Triple nested loop detected - O(n³) complexity",
                "remediation": "Consider algorithmic optimization or data structure changes",
            },
            "redundant_computation": {
                "regex": r"(\w+\([^)]+\))\s*==\s*\1",
                "severity": "low",
                "description": "Redundant function calls in comparison",
                "remediation": "Cache the function result in a variable",
            },
            "global_var_in_loop": {
                "regex": r"for\s+.*?:\s*\n\s+global\s+\w+",
                "severity": "medium",
                "description": "Global variable modification in loop",
                "remediation": "Use local variables and return values instead",
            },
        }

        # Symbolic chain patterns
        self.symbolic_patterns = {
            "broken_chain": {
                "regex": r"\d{3}\/\/(?!\d{3}\/\/)",
                "severity": "medium",
                "description": "Incomplete symbolic chain notation",
                "remediation": "Ensure chain notation follows 001//999// format",
            },
            "anchor_drift": {
                "regex": r"T1_\w+.*?SRB_\w+.*?T1_\w+",
                "severity": "low",
                "description": "Potential anchor coordination issue",
                "remediation": "Ensure T1 and SRB anchors are properly synchronized",
            },
        }

    def _compute_vector_similarity(self, text1: str, text2: str) -> float:
        """
        Quantum-inspired vector similarity (simplified)
        Real implementation would use actual quantum vectors
        """
        # Simple character-based similarity
        if not text1 or not text2:
            return 0.0

        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        if union == 0:
            return 0.0
        
        return intersection / union

    def _compute_cultural_impact(self, pattern_type: str, code: str) -> float:
        """
        Assess cultural impact of detected pattern (mock CASK integration)
        """
        # Base impact
        impact = 0.5
        
        # Security issues have higher cultural impact (trust)
        if pattern_type in self.security_patterns:
            impact += 0.3
        
        # Performance issues affect user experience
        if pattern_type in self.performance_patterns:
            impact += 0.2
        
        # Code with comments has lower cultural friction
        if "//" in code or "#" in code:
            impact -= 0.1
        
        return min(1.0, max(0.0, impact))

    def _compute_detection_hash(self, pattern: str, location: str) -> str:
        """Compute unique hash for detection"""
        data = f"{pattern}:{location}:{self.anchor_seed}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def detect_in_text(
        self,
        text: str,
        location: str,
        pattern_types: List[str],
        sensitivity: float = 0.8
    ) -> List[DetectedPattern]:
        """
        Detect patterns in text with quantum-inspired fuzzy matching
        
        Args:
            text: Text to scan
            location: Location identifier (file path, etc.)
            pattern_types: Types to detect ('security', 'performance', 'symbolic')
            sensitivity: Detection sensitivity (0.0-1.0)
            
        Returns:
            List of detected patterns
        """
        detections = []
        
        # Combine pattern dictionaries based on requested types
        patterns_to_check = {}
        if "security" in pattern_types or "security_antipattern" in pattern_types:
            patterns_to_check.update(self.security_patterns)
        if "performance" in pattern_types or "performance_bottleneck" in pattern_types:
            patterns_to_check.update(self.performance_patterns)
        if "symbolic" in pattern_types:
            patterns_to_check.update(self.symbolic_patterns)
        
        # Scan for each pattern
        for pattern_name, pattern_def in patterns_to_check.items():
            regex = pattern_def["regex"]
            matches = re.finditer(regex, text, re.MULTILINE | re.IGNORECASE)
            
            for match in matches:
                # Extract code snippet with context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                snippet = text[start:end].strip()
                
                # Compute confidence based on match quality
                confidence = 0.9  # High confidence for regex matches
                
                # Adjust confidence based on sensitivity
                if confidence >= sensitivity:
                    detection = DetectedPattern(
                        pattern_type=pattern_name,
                        location=location,
                        severity=pattern_def["severity"],
                        description=pattern_def["description"],
                        code_snippet=snippet,
                        remediation=pattern_def["remediation"],
                        confidence=confidence,
                        cultural_impact=self._compute_cultural_impact(pattern_name, snippet),
                        t1_state=self.t1.advance(snippet),
                        srb_resolution=self.srb.resolve(f"{location}:{pattern_name}"),
                        detection_hash=self._compute_detection_hash(pattern_name, location)
                    )
                    detections.append(detection)
                    self.detected_patterns.append(detection)
        
        return detections

    def scan_directory(
        self,
        directory: str,
        pattern_types: List[str],
        file_extensions: List[str] = [".py", ".js", ".java"],
        sensitivity: float = 0.8
    ) -> Dict[str, Any]:
        """
        Scan directory for patterns
        
        Args:
            directory: Directory path to scan
            pattern_types: Pattern types to detect
            file_extensions: File extensions to scan
            sensitivity: Detection sensitivity
            
        Returns:
            Scan results with DLP tracking
        """
        all_detections = []
        scanned_files = []
        
        # For demo purposes, create mock files
        mock_files = self._create_mock_files()
        
        for file_path, content in mock_files.items():
            if any(file_path.endswith(ext) for ext in file_extensions):
                scanned_files.append(file_path)
                detections = self.detect_in_text(
                    text=content,
                    location=file_path,
                    pattern_types=pattern_types,
                    sensitivity=sensitivity
                )
                all_detections.extend(detections)
        
        return self._create_scan_results(
            scanned_files=scanned_files,
            detections=all_detections,
            pattern_types=pattern_types
        )

    def _create_mock_files(self) -> Dict[str, str]:
        """Create mock files for demonstration"""
        return {
            "./src/database.py": '''
def get_user(user_id):
    # BAD: SQL injection vulnerability
    query = "SELECT * FROM users WHERE id = '" + user_id + "'"
    return execute(query)

# BAD: Hardcoded credentials
api_key = "sk_test_1234567890abcdef"
password = "admin123"
''',
            "./src/processing.py": '''
def process_data(data):
    # BAD: Triple nested loop - O(n³)
    for i in range(len(data)):
        for j in range(len(data)):
            for k in range(len(data)):
                result = compute(data[i], data[j], data[k])
    
    # BAD: Redundant computation
    if expensive_function(x) == expensive_function(x):
        pass
''',
            "./src/symbolic_chain.py": '''
# Example of Aurora symbolic chains
def process_chain():
    # GOOD: Proper chain notation
    chain1 = "001//999//"
    
    # BAD: Incomplete chain
    chain2 = "001//"
    
    # Anchor coordination
    T1_anchor = create_anchor()
    SRB_anchor = create_boundary()
    T1_next = advance()
''',
            "./src/file_handler.py": '''
import os

def read_user_file(filename):
    # BAD: Path traversal vulnerability
    path = "/data/" + filename + "../../../etc/passwd"
    with open(path) as f:
        return f.read()
    
    # BAD: eval usage
    eval(user_input)
''',
        }

    def _create_scan_results(
        self,
        scanned_files: List[str],
        detections: List[DetectedPattern],
        pattern_types: List[str]
    ) -> Dict[str, Any]:
        """Create comprehensive scan results with DLP tracking"""
        # Group by severity
        by_severity = {
            "critical": [d for d in detections if d.severity == "critical"],
            "high": [d for d in detections if d.severity == "high"],
            "medium": [d for d in detections if d.severity == "medium"],
            "low": [d for d in detections if d.severity == "low"],
        }
        
        return {
            "success": True,
            "summary": {
                "files_scanned": len(scanned_files),
                "patterns_detected": len(detections),
                "critical_issues": len(by_severity["critical"]),
                "high_issues": len(by_severity["high"]),
                "medium_issues": len(by_severity["medium"]),
                "low_issues": len(by_severity["low"]),
                "avg_confidence": sum(d.confidence for d in detections) / max(1, len(detections)),
                "avg_cultural_impact": sum(d.cultural_impact for d in detections) / max(1, len(detections)),
            },
            "detections_by_severity": {
                severity: [
                    {
                        "type": d.pattern_type,
                        "location": d.location,
                        "description": d.description,
                        "snippet": d.code_snippet[:100] + "..." if len(d.code_snippet) > 100 else d.code_snippet,
                        "remediation": d.remediation,
                        "confidence": d.confidence,
                        "cultural_impact": d.cultural_impact,
                    }
                    for d in patterns
                ]
                for severity, patterns in by_severity.items()
                if patterns
            },
            "metadata": {
                "anchor_seed": self.anchor_seed,
                "t1_anchor": self.t1.export(),
                "srb_anchor": self.srb.export(),
                "pattern_types": pattern_types,
                "context_tag": "symbolic_pattern_detective",
                "timestamp": datetime.now().isoformat(),
                "dlp_hash": self._compute_dlp_hash(),
            }
        }

    def _compute_dlp_hash(self) -> str:
        """Compute DLP tracking hash"""
        data = f"{self.anchor_seed}:{self.t1.state}:{self.srb.resolution}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def export_detections(self) -> List[Dict[str, Any]]:
        """Export all detections with full metadata"""
        return [
            {
                "pattern_type": d.pattern_type,
                "location": d.location,
                "severity": d.severity,
                "description": d.description,
                "remediation": d.remediation,
                "confidence": d.confidence,
                "cultural_impact": d.cultural_impact,
                "t1_state": d.t1_state,
                "srb_resolution": d.srb_resolution,
                "detection_hash": d.detection_hash,
            }
            for d in self.detected_patterns
        ]


def demo_pattern_detective():
    """Demonstration of Symbolic Pattern Detective"""
    print("🔍 Aurora CloudBank Symbolic Pattern Detective Demo")
    print("=" * 70)
    print()
    
    # Initialize detective
    detective = SymbolicPatternDetective(anchor_seed="DEMO_DETECTIVE_001")
    
    # Scan for different pattern types
    scan_configs = [
        (["security_antipattern"], "Security Anti-patterns"),
        (["performance_bottleneck"], "Performance Bottlenecks"),
        (["symbolic"], "Symbolic Chain Issues"),
    ]
    
    for pattern_types, scan_name in scan_configs:
        print(f"🔬 Scanning for: {scan_name}")
        print("-" * 70)
        
        results = detective.scan_directory(
            directory="./src",
            pattern_types=pattern_types,
            sensitivity=0.8
        )
        
        print(f"📊 Scan Summary:")
        print(f"  Files Scanned: {results['summary']['files_scanned']}")
        print(f"  Patterns Detected: {results['summary']['patterns_detected']}")
        print(f"  Critical: {results['summary']['critical_issues']}")
        print(f"  High: {results['summary']['high_issues']}")
        print(f"  Medium: {results['summary']['medium_issues']}")
        print(f"  Low: {results['summary']['low_issues']}")
        print(f"  Avg Confidence: {results['summary']['avg_confidence']:.2f}")
        print(f"  Avg Cultural Impact: {results['summary']['avg_cultural_impact']:.2f}")
        print()
        
        # Show detections
        for severity in ["critical", "high", "medium", "low"]:
            if severity in results['detections_by_severity']:
                detections = results['detections_by_severity'][severity]
                if detections:
                    print(f"🚨 {severity.upper()} Issues:")
                    for i, det in enumerate(detections, 1):
                        print(f"  {i}. {det['type']} in {det['location']}")
                        print(f"     Description: {det['description']}")
                        print(f"     Remediation: {det['remediation']}")
                        print(f"     Confidence: {det['confidence']:.2f}")
                        print()
        
        print(f"🔐 DLP Metadata:")
        print(f"  T1 State: {results['metadata']['t1_anchor']['state']}")
        print(f"  SRB Resolution: {results['metadata']['srb_anchor']['resolution']}")
        print(f"  DLP Hash: {results['metadata']['dlp_hash']}")
        print()
        print("=" * 70)
        print()
    
    # Export all detections
    print("📋 Complete Detection Report:")
    print("-" * 70)
    all_detections = detective.export_detections()
    print(f"Total Unique Detections: {len(all_detections)}")
    print()
    
    # Group by file
    by_file = {}
    for det in all_detections:
        file = det['location']
        if file not in by_file:
            by_file[file] = []
        by_file[file].append(det)
    
    for file, dets in by_file.items():
        print(f"📄 {file}: {len(dets)} issues")
    print()


if __name__ == "__main__":
    demo_pattern_detective()
