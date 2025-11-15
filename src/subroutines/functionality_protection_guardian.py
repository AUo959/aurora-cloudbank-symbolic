#!/usr/bin/env python3
"""
Functionality Protection Guardian Subroutine
===========================================
Anchor: FPG-GUARDIAN-001
Team: AUo959-team  
Ethics: Picard_Delta_3
DLP: CONFIDENTIAL_PROTECTION_SYSTEM

Advanced protection subroutine that prevents superior functionality from being 
overwritten without explicit authorization. Tracks feature metrics, version 
superiority, and implements approval workflows for edge cases.

This subroutine was created in response to the PR #338 incident where Quantum 
Forge v2.0 (961 lines, 100% tests, advanced features) was inadvertently 
overwritten by v3.0 (14 failing tests, reduced functionality).

Key Capabilities:
- Pre-commit feature superiority analysis
- Version regression detection  
- Emergency approval workflow for critical overwrites
- Comprehensive audit trail with DLP tracking
- Integration with git hooks and CI/CD pipelines
"""

import os
import sys
import json
import hashlib
import logging
from datetime import datetime, UTC
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import subprocess
import ast
import re

# Aurora imports
from src.core.native_dlp_export import NativeDLPTracker
from src.subroutines.registry import SubroutineRegistry, Subroutine, SubroutineCategory

logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """Protection severity levels"""
    MONITOR = "monitor"         # Log only, allow changes
    WARN = "warn"              # Warn but allow with confirmation
    BLOCK = "block"            # Block and require approval
    CRITICAL = "critical"      # Block with emergency approval only


class FeatureMetric(Enum):
    """Types of feature metrics to compare"""
    LINES_OF_CODE = "lines_of_code"
    TEST_COVERAGE = "test_coverage" 
    TEST_PASS_RATE = "test_pass_rate"
    FUNCTION_COUNT = "function_count"
    CLASS_COUNT = "class_count"
    COMPLEXITY_SCORE = "complexity_score"
    FEATURE_FLAGS = "feature_flags"
    API_ENDPOINTS = "api_endpoints"
    DOCUMENTATION_COVERAGE = "documentation_coverage"


@dataclass
class FeatureProfile:
    """Complete feature profile for a module/file"""
    file_path: str
    version: str
    timestamp: datetime
    metrics: Dict[FeatureMetric, Any] = field(default_factory=dict)
    feature_list: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)
    hash_signature: str = ""
    
    def __post_init__(self):
        """Calculate hash signature"""
        profile_data = {
            "file_path": self.file_path,
            "metrics": {k.value: v for k, v in self.metrics.items()},
            "feature_list": sorted(self.feature_list)
        }
        self.hash_signature = hashlib.sha256(
            json.dumps(profile_data, sort_keys=True).encode()
        ).hexdigest()[:16]


@dataclass
class SuperiorityAnalysis:
    """Analysis of whether current version is superior to proposed changes"""
    is_superior: bool
    superiority_score: float  # 0.0 = much worse, 1.0 = much better
    critical_metrics: Dict[FeatureMetric, Dict[str, Any]]
    recommendation: ProtectionLevel
    justification: str
    approval_required: bool = False
    emergency_override_code: Optional[str] = None


@dataclass
class ApprovalRequest:
    """Request for approval to overwrite superior functionality"""
    request_id: str
    file_path: str
    current_profile: FeatureProfile
    proposed_profile: FeatureProfile
    superiority_analysis: SuperiorityAnalysis
    requester: str
    timestamp: datetime
    justification: str
    approval_status: str = "pending"
    approver: Optional[str] = None
    approval_timestamp: Optional[datetime] = None


class FunctionalityProtectionGuardian:
    """
    Advanced protection system for preserving superior functionality
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 profiles_path: Optional[str] = None):
        self.config_path = config_path or ".aurora/protection_config.json"
        self.profiles_path = profiles_path or ".aurora/feature_profiles.json" 
        self.approvals_path = ".aurora/approval_requests.json"
        self.audit_path = ".aurora/protection_audit.log"
        
        self.config = self._load_config()
        self.profiles = self._load_profiles()
        self.dlp_tracker = NativeDLPTracker()
        
        # Ensure directories exist
        Path(".aurora").mkdir(exist_ok=True)
        
    def _load_config(self) -> Dict[str, Any]:
        """Load protection configuration"""
        default_config = {
            "protection_enabled": True,
            "default_protection_level": ProtectionLevel.WARN.value,
            "critical_files": [
                "modules/quantum_forge/**/*.py",
                "modules/vector_gen/**/*.py", 
                "src/aurora/core/**/*.py",
                "api/aurora_api.py"
            ],
            "protected_metrics": {
                FeatureMetric.TEST_PASS_RATE.value: {"min_threshold": 0.9},
                FeatureMetric.LINES_OF_CODE.value: {"regression_threshold": 0.8},
                FeatureMetric.FEATURE_FLAGS.value: {"allow_removal": False}
            },
            "approval_contacts": [
                "AUo959@github.com",
                "aurora-team@cloudbank.local"
            ],
            "emergency_override_enabled": True,
            "audit_retention_days": 90
        }
        
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            
        return default_config
        
    def _load_profiles(self) -> Dict[str, FeatureProfile]:
        """Load existing feature profiles"""
        profiles = {}
        try:
            if Path(self.profiles_path).exists():
                with open(self.profiles_path, 'r') as f:
                    data = json.load(f)
                    for file_path, profile_data in data.items():
                        # Convert back to FeatureProfile
                        profile_data['timestamp'] = datetime.fromisoformat(
                            profile_data['timestamp']
                        )
                        # Convert metric keys back to enums
                        metrics = {}
                        for k, v in profile_data['metrics'].items():
                            try:
                                metrics[FeatureMetric(k)] = v
                            except ValueError:
                                logger.warning(f"Unknown metric: {k}")
                        profile_data['metrics'] = metrics
                        
                        profiles[file_path] = FeatureProfile(**profile_data)
        except Exception as e:
            logger.warning(f"Failed to load profiles: {e}")
            
        return profiles
        
    def _save_profiles(self):
        """Persist feature profiles to disk"""
        try:
            # Convert profiles to JSON-serializable format
            data = {}
            for file_path, profile in self.profiles.items():
                profile_dict = {
                    "file_path": profile.file_path,
                    "version": profile.version,
                    "timestamp": profile.timestamp.isoformat(),
                    "metrics": {k.value: v for k, v in profile.metrics.items()},
                    "feature_list": profile.feature_list,
                    "test_results": profile.test_results,
                    "hash_signature": profile.hash_signature
                }
                data[file_path] = profile_dict
                
            with open(self.profiles_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
            
    def analyze_file_features(self, file_path: str) -> FeatureProfile:
        """
        Comprehensive analysis of file features and capabilities
        """
        try:
            if not Path(file_path).exists():
                return FeatureProfile(
                    file_path=file_path,
                    version="deleted",
                    timestamp=datetime.now(UTC)
                )
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Initialize metrics
            metrics = {}
            feature_list = []
            
            # Lines of code
            lines = content.split('\n')
            code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
            metrics[FeatureMetric.LINES_OF_CODE] = len(code_lines)
            
            # AST analysis for Python files
            if file_path.endswith('.py'):
                try:
                    tree = ast.parse(content)
                    
                    # Count functions and classes
                    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    metrics[FeatureMetric.FUNCTION_COUNT] = len(functions)
                    metrics[FeatureMetric.CLASS_COUNT] = len(classes)
                    
                    # Extract feature names
                    for node in functions:
                        feature_list.append(f"function:{node.name}")
                    for node in classes:
                        feature_list.append(f"class:{node.name}")
                        
                    # Look for advanced patterns
                    if "async def" in content:
                        feature_list.append("async_support")
                    if "@dataclass" in content:
                        feature_list.append("dataclass_usage")
                    if "QuantumState" in content:
                        feature_list.append("quantum_state_tracking")
                    if "SymbolicLayer" in content:
                        feature_list.append("symbolic_layer_processing")
                    if "export_agent" in content:
                        feature_list.append("agent_persistence")
                    if "import_agent" in content:
                        feature_list.append("agent_restoration")
                        
                except SyntaxError as e:
                    logger.warning(f"Syntax error in {file_path}: {e}")
                    
            # Test analysis
            test_results = self._analyze_test_results(file_path)
            metrics[FeatureMetric.TEST_PASS_RATE] = test_results.get("pass_rate", 0.0)
            
            # Documentation analysis
            doc_coverage = self._analyze_documentation_coverage(content)
            metrics[FeatureMetric.DOCUMENTATION_COVERAGE] = doc_coverage
            
            # API endpoint analysis for API files
            if "api" in file_path.lower() and "app.route" in content:
                endpoints = len(re.findall(r'@app\.route|@router\.|@.*\.route', content))
                metrics[FeatureMetric.API_ENDPOINTS] = endpoints
                
            return FeatureProfile(
                file_path=file_path,
                version=self._extract_version(content),
                timestamp=datetime.now(UTC),
                metrics=metrics,
                feature_list=feature_list,
                test_results=test_results
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            return FeatureProfile(
                file_path=file_path,
                version="error",
                timestamp=datetime.now(UTC)
            )
            
    def _analyze_test_results(self, file_path: str) -> Dict[str, Any]:
        """Analyze test results for the given file"""
        test_results = {"pass_rate": 0.0, "total_tests": 0, "passing_tests": 0}
        
        # Look for corresponding test file
        test_patterns = [
            f"tests/test_{Path(file_path).stem}.py",
            f"test_{Path(file_path).stem}.py", 
            f"{Path(file_path).parent}/tests/test_{Path(file_path).stem}.py"
        ]
        
        for test_file in test_patterns:
            if Path(test_file).exists():
                # Try to extract test count from file
                try:
                    with open(test_file, 'r') as f:
                        test_content = f.read()
                        
                    # Count test functions
                    test_functions = len(re.findall(r'def test_\w+', test_content))
                    test_results["total_tests"] = test_functions
                    
                    # If recent pytest results available, use them
                    # This is a placeholder - in practice, integrate with CI/CD
                    test_results["passing_tests"] = test_functions  # Assume all pass for now
                    test_results["pass_rate"] = 1.0 if test_functions > 0 else 0.0
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze test file {test_file}: {e}")
                break
                
        return test_results
        
    def _analyze_documentation_coverage(self, content: str) -> float:
        """Calculate documentation coverage score"""
        try:
            # Count docstrings vs functions/classes
            docstring_count = len(re.findall(r'""".*?"""', content, re.DOTALL))
            function_count = len(re.findall(r'def \w+', content))
            class_count = len(re.findall(r'class \w+', content))
            
            total_items = function_count + class_count
            if total_items == 0:
                return 1.0  # No items to document
                
            # Rough documentation coverage
            return min(1.0, docstring_count / total_items)
            
        except Exception:
            return 0.0
            
    def _extract_version(self, content: str) -> str:
        """Extract version information from file content"""
        # Look for version patterns
        version_patterns = [
            r'__version__\s*=\s*["\']([^"\']+)["\']',
            r'VERSION\s*=\s*["\']([^"\']+)["\']',
            r'version\s*:\s*["\']([^"\']+)["\']',
            r'v(\d+\.\d+\.\d+)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)
                
        return "unknown"
        
    def compare_superiority(self, 
                          current: FeatureProfile, 
                          proposed: FeatureProfile) -> SuperiorityAnalysis:
        """
        Comprehensive comparison to determine which version is superior
        """
        critical_metrics = {}
        score_components = []
        
        # Compare each metric
        for metric in FeatureMetric:
            current_val = current.metrics.get(metric, 0)
            proposed_val = proposed.metrics.get(metric, 0)
            
            if isinstance(current_val, (int, float)) and isinstance(proposed_val, (int, float)):
                if current_val > 0:  # Avoid division by zero
                    ratio = proposed_val / current_val
                    
                    # Different metrics have different "better" directions
                    if metric in [FeatureMetric.TEST_PASS_RATE, FeatureMetric.DOCUMENTATION_COVERAGE]:
                        # Higher is better
                        component_score = min(2.0, ratio)  # Cap at 2x better
                    elif metric in [FeatureMetric.LINES_OF_CODE, FeatureMetric.FUNCTION_COUNT]:
                        # More is generally better, but with diminishing returns
                        component_score = min(1.5, ratio) if ratio >= 1.0 else ratio * 0.8
                    else:
                        component_score = ratio
                        
                    score_components.append(component_score)
                    
                    critical_metrics[metric] = {
                        "current": current_val,
                        "proposed": proposed_val,
                        "ratio": ratio,
                        "component_score": component_score
                    }
                    
        # Feature list comparison
        current_features = set(current.feature_list)
        proposed_features = set(proposed.feature_list)
        
        added_features = proposed_features - current_features
        removed_features = current_features - proposed_features
        
        # Penalty for removing advanced features
        feature_score = 1.0
        if removed_features:
            advanced_removed = [f for f in removed_features 
                              if any(keyword in f for keyword in 
                                   ["quantum", "symbolic", "persistence", "async", "agent"])]
            if advanced_removed:
                feature_score -= 0.3 * len(advanced_removed)  # Significant penalty
                
        if added_features:
            advanced_added = [f for f in added_features
                            if any(keyword in f for keyword in 
                                 ["quantum", "symbolic", "persistence", "async", "agent"])]
            if advanced_added:
                feature_score += 0.2 * len(advanced_added)  # Bonus for advanced features
                
        score_components.append(feature_score)
        
        # Overall superiority score
        if score_components:
            superiority_score = sum(score_components) / len(score_components)
        else:
            superiority_score = 1.0  # Neutral if no metrics to compare
            
        # Determine protection level and recommendation
        if superiority_score < 0.7:  # Significant regression
            if removed_features:
                protection_level = ProtectionLevel.CRITICAL
                justification = f"CRITICAL: Significant regression detected (score: {superiority_score:.2f}). Advanced features removed: {removed_features}"
            else:
                protection_level = ProtectionLevel.BLOCK
                justification = f"BLOCK: Quality regression detected (score: {superiority_score:.2f})"
        elif superiority_score < 0.9:  # Minor regression
            protection_level = ProtectionLevel.WARN
            justification = f"WARNING: Minor regression detected (score: {superiority_score:.2f})"
        else:
            protection_level = ProtectionLevel.MONITOR
            justification = f"OK: No significant regression (score: {superiority_score:.2f})"
            
        # Emergency override code for critical cases
        emergency_code = None
        if protection_level == ProtectionLevel.CRITICAL:
            emergency_code = hashlib.sha256(
                f"{current.file_path}:{current.hash_signature}:{datetime.now(UTC).date()}".encode()
            ).hexdigest()[:12].upper()
            
        return SuperiorityAnalysis(
            is_superior=superiority_score >= 1.0,
            superiority_score=superiority_score,
            critical_metrics=critical_metrics,
            recommendation=protection_level,
            justification=justification,
            approval_required=protection_level in [ProtectionLevel.BLOCK, ProtectionLevel.CRITICAL],
            emergency_override_code=emergency_code
        )
        
    def register_baseline(self, file_path: str) -> bool:
        """Register current version of file as baseline"""
        try:
            profile = self.analyze_file_features(file_path)
            self.profiles[file_path] = profile
            self._save_profiles()
            
            # Log registration
            self._audit_log(f"Registered baseline for {file_path}: {profile.hash_signature}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to register baseline for {file_path}: {e}")
            return False
            
    def check_protection_pre_commit(self, changed_files: List[str]) -> Dict[str, Any]:
        """
        Pre-commit hook integration - check all changed files for regressions
        """
        protection_results = {
            "allowed": True,
            "blocked_files": [],
            "warnings": [],
            "approval_required": [],
            "emergency_codes": {}
        }
        
        for file_path in changed_files:
            if not self._is_protected_file(file_path):
                continue
                
            if file_path not in self.profiles:
                # First time seeing this file - register as baseline
                self.register_baseline(file_path)
                continue
                
            current_profile = self.profiles[file_path]
            proposed_profile = self.analyze_file_features(file_path)
            
            analysis = self.compare_superiority(current_profile, proposed_profile)
            
            if analysis.recommendation == ProtectionLevel.CRITICAL:
                protection_results["allowed"] = False
                protection_results["blocked_files"].append(file_path)
                protection_results["emergency_codes"][file_path] = analysis.emergency_override_code
                
            elif analysis.recommendation == ProtectionLevel.BLOCK:
                if not self._check_approval(file_path):
                    protection_results["allowed"] = False
                    protection_results["blocked_files"].append(file_path)
                    protection_results["approval_required"].append(file_path)
                    
            elif analysis.recommendation == ProtectionLevel.WARN:
                protection_results["warnings"].append({
                    "file": file_path,
                    "message": analysis.justification
                })
                
            # Log analysis
            self._audit_log(f"Protection check for {file_path}: {analysis.justification}")
            
        return protection_results
        
    def _is_protected_file(self, file_path: str) -> bool:
        """Check if file matches protected patterns"""
        import fnmatch
        
        for pattern in self.config["critical_files"]:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False
        
    def _check_approval(self, file_path: str) -> bool:
        """Check if approval exists for file modification"""
        try:
            if Path(self.approvals_path).exists():
                with open(self.approvals_path, 'r') as f:
                    approvals = json.load(f)
                    
                for approval in approvals:
                    if (approval["file_path"] == file_path and 
                        approval["approval_status"] == "approved"):
                        return True
        except Exception as e:
            logger.warning(f"Failed to check approvals: {e}")
            
        return False
        
    def request_approval(self, 
                        file_path: str, 
                        justification: str,
                        requester: str = "unknown") -> str:
        """Submit approval request for overwriting superior functionality"""
        
        current_profile = self.profiles.get(file_path)
        if not current_profile:
            raise ValueError(f"No baseline profile found for {file_path}")
            
        proposed_profile = self.analyze_file_features(file_path)
        analysis = self.compare_superiority(current_profile, proposed_profile)
        
        request = ApprovalRequest(
            request_id=hashlib.sha256(
                f"{file_path}:{datetime.now(UTC).isoformat()}".encode()
            ).hexdigest()[:16],
            file_path=file_path,
            current_profile=current_profile,
            proposed_profile=proposed_profile,
            superiority_analysis=analysis,
            requester=requester,
            timestamp=datetime.now(UTC),
            justification=justification
        )
        
        # Save approval request
        self._save_approval_request(request)
        
        # Send notification (placeholder - implement actual notification)
        self._notify_approval_contacts(request)
        
        return request.request_id
        
    def _save_approval_request(self, request: ApprovalRequest):
        """Persist approval request"""
        try:
            approvals = []
            if Path(self.approvals_path).exists():
                with open(self.approvals_path, 'r') as f:
                    approvals = json.load(f)
                    
            # Convert request to JSON-serializable format
            request_dict = {
                "request_id": request.request_id,
                "file_path": request.file_path,
                "requester": request.requester,
                "timestamp": request.timestamp.isoformat(),
                "justification": request.justification,
                "approval_status": request.approval_status,
                "superiority_score": request.superiority_analysis.superiority_score,
                "justification_analysis": request.superiority_analysis.justification
            }
            
            approvals.append(request_dict)
            
            with open(self.approvals_path, 'w') as f:
                json.dump(approvals, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save approval request: {e}")
            
    def _notify_approval_contacts(self, request: ApprovalRequest):
        """Send notification to approval contacts"""
        # Placeholder - implement actual notification system
        message = f"""
Functionality Protection Alert
=============================

File: {request.file_path}
Requester: {request.requester}
Request ID: {request.request_id}

Analysis: {request.superiority_analysis.justification}
Superiority Score: {request.superiority_analysis.superiority_score:.3f}

Justification: {request.justification}

Please review and approve/reject this modification request.
        """
        
        logger.info(f"Approval notification: {message}")
        
    def _audit_log(self, message: str):
        """Add entry to protection audit log"""
        try:
            timestamp = datetime.now(UTC).isoformat()
            log_entry = f"[{timestamp}] {message}\n"
            
            with open(self.audit_path, 'a') as f:
                f.write(log_entry)
                
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            
    def emergency_override(self, file_path: str, override_code: str) -> bool:
        """Emergency override for critical protection blocks"""
        if not self.config.get("emergency_override_enabled", False):
            return False
            
        # Verify override code
        current_profile = self.profiles.get(file_path)
        if not current_profile:
            return False
            
        expected_code = hashlib.sha256(
            f"{file_path}:{current_profile.hash_signature}:{datetime.now(UTC).date()}".encode()
        ).hexdigest()[:12].upper()
        
        if override_code != expected_code:
            self._audit_log(f"INVALID emergency override attempt for {file_path}: {override_code}")
            return False
            
        # Log emergency override
        self._audit_log(f"EMERGENCY OVERRIDE used for {file_path}: {override_code}")
        
        # Create DLP export for emergency override
        export_data = {
            "operation": "emergency_override",
            "file_path": file_path,
            "override_code": override_code,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        self.dlp_tracker.create_export(
            data=export_data,
            context_tag=f"emergency_override_{file_path.replace('/', '_')}",
            symbolic_validation=True
        )
        
        return True
        
    def generate_protection_report(self) -> Dict[str, Any]:
        """Generate comprehensive protection status report"""
        report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "protection_enabled": self.config["protection_enabled"],
            "protected_files_count": len([f for f in self.profiles.keys() 
                                        if self._is_protected_file(f)]),
            "total_profiles": len(self.profiles),
            "recent_blocks": [],
            "pending_approvals": [],
            "emergency_overrides_today": 0
        }
        
        # Analyze recent audit log
        if Path(self.audit_path).exists():
            with open(self.audit_path, 'r') as f:
                recent_logs = f.readlines()[-100:]  # Last 100 entries
                
            today = datetime.now(UTC).date().isoformat()
            for log_line in recent_logs:
                if "BLOCK:" in log_line and today in log_line:
                    report["recent_blocks"].append(log_line.strip())
                elif "EMERGENCY OVERRIDE" in log_line and today in log_line:
                    report["emergency_overrides_today"] += 1
                    
        # Check pending approvals
        if Path(self.approvals_path).exists():
            with open(self.approvals_path, 'r') as f:
                approvals = json.load(f)
                
            for approval in approvals:
                if approval["approval_status"] == "pending":
                    report["pending_approvals"].append({
                        "request_id": approval["request_id"],
                        "file_path": approval["file_path"],
                        "requester": approval["requester"],
                        "timestamp": approval["timestamp"]
                    })
                    
        return report
        
    def update_baseline_post_approval(self, file_path: str):
        """Update baseline after approved modification"""
        if self._check_approval(file_path):
            self.register_baseline(file_path)
            self._audit_log(f"Baseline updated after approval: {file_path}")
            return True
        return False
        

# Git hook integration functions
def pre_commit_hook() -> int:
    """Git pre-commit hook integration"""
    try:
        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            return 0  # Allow commit if can't determine changes
            
        changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
        
        if not changed_files:
            return 0  # No files changed
            
        # Check protection
        guardian = FunctionalityProtectionGuardian()
        protection_results = guardian.check_protection_pre_commit(changed_files)
        
        # Handle results
        if not protection_results["allowed"]:
            print("\n🚫 COMMIT BLOCKED - Superior functionality protection active!")
            
            for file_path in protection_results["blocked_files"]:
                print(f"\n❌ BLOCKED: {file_path}")
                
            if protection_results["emergency_codes"]:
                print("\n🆘 EMERGENCY OVERRIDE CODES:")
                for file_path, code in protection_results["emergency_codes"].items():
                    print(f"   {file_path}: {code}")
                    
            if protection_results["approval_required"]:
                print("\n📝 APPROVAL REQUIRED for files:")
                for file_path in protection_results["approval_required"]:
                    print(f"   {file_path}")
                    
            print("\n💡 Use 'python -m src.subroutines.functionality_protection_guardian --request-approval <file>' to request approval")
            print("💡 Use 'python -m src.subroutines.functionality_protection_guardian --emergency-override <file> <code>' for emergency")
            
            return 1  # Block commit
            
        # Show warnings
        for warning in protection_results["warnings"]:
            print(f"\n⚠️  WARNING: {warning['file']}")
            print(f"    {warning['message']}")
            
        return 0  # Allow commit
        
    except Exception as e:
        logger.error(f"Protection hook error: {e}")
        return 0  # Allow commit on error to avoid blocking development


# CLI interface
def main():
    """Command line interface for functionality protection guardian"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Functionality Protection Guardian")
    parser.add_argument("--register-baseline", help="Register file as baseline")
    parser.add_argument("--check-file", help="Check single file for regressions")
    parser.add_argument("--request-approval", help="Request approval for file modification")
    parser.add_argument("--emergency-override", nargs=2, 
                       help="Emergency override: file_path override_code")
    parser.add_argument("--report", action="store_true", help="Generate protection report")
    parser.add_argument("--install-hooks", action="store_true", 
                       help="Install git hooks")
    
    args = parser.parse_args()
    guardian = FunctionalityProtectionGuardian()
    
    if args.register_baseline:
        success = guardian.register_baseline(args.register_baseline)
        print(f"Baseline registration: {'✅ Success' if success else '❌ Failed'}")
        
    elif args.check_file:
        if args.check_file in guardian.profiles:
            current = guardian.profiles[args.check_file]
            proposed = guardian.analyze_file_features(args.check_file)
            analysis = guardian.compare_superiority(current, proposed)
            
            print(f"File: {args.check_file}")
            print(f"Superiority Score: {analysis.superiority_score:.3f}")
            print(f"Recommendation: {analysis.recommendation.value}")
            print(f"Analysis: {analysis.justification}")
            
            if analysis.emergency_override_code:
                print(f"Emergency Code: {analysis.emergency_override_code}")
        else:
            print("No baseline found - registering current version")
            guardian.register_baseline(args.check_file)
            
    elif args.request_approval:
        justification = input("Justification for modification: ")
        request_id = guardian.request_approval(
            args.request_approval, 
            justification,
            os.getenv("USER", "unknown")
        )
        print(f"Approval request submitted: {request_id}")
        
    elif args.emergency_override:
        file_path, override_code = args.emergency_override
        success = guardian.emergency_override(file_path, override_code)
        print(f"Emergency override: {'✅ Success' if success else '❌ Failed'}")
        
    elif args.report:
        report = guardian.generate_protection_report()
        print(json.dumps(report, indent=2))
        
    elif args.install_hooks:
        # Install git hooks
        hook_content = f"""#!/bin/bash
# Functionality Protection Guardian Pre-commit Hook
python3 -c "
import sys
sys.path.append('.')
from src.subroutines.functionality_protection_guardian import pre_commit_hook
exit(pre_commit_hook())
"
"""
        
        hook_path = Path(".git/hooks/pre-commit")
        hook_path.parent.mkdir(exist_ok=True)
        
        with open(hook_path, 'w') as f:
            f.write(hook_content)
            
        hook_path.chmod(0o755)
        print("✅ Functionality protection hook installed")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


# Register subroutine
def register_subroutine():
    """Register this subroutine with the Aurora registry"""
    registry = SubroutineRegistry()
    
    subroutine = Subroutine(
        id="functionality_protection_guardian",
        name="Functionality Protection Guardian",
        version="1.0.0",
        description="Prevents superior functionality from being overwritten without explicit permission",
        category=SubroutineCategory.EXECUTIVE,
        module_path="src.subroutines.functionality_protection_guardian",
        class_name="FunctionalityProtectionGuardian",
        entry_point="check_protection_pre_commit",
        integrations=["git_hooks", "dlp_tracker", "audit_log"],
        tags=["protection", "version_control", "quality_assurance", "regression_prevention"],
        documentation_url="docs/subroutines/functionality_protection_guardian.md"
    )
    
    registry.register(subroutine)
    return subroutine


# Auto-register when imported
if __name__ != "__main__":
    try:
        register_subroutine()
    except Exception as e:
        logger.warning(f"Failed to auto-register subroutine: {e}")