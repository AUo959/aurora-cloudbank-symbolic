#!/usr/bin/env python3
"""
Aurora CloudBank - SSMT v2.2: Architectural Sonar Integration

Revolutionary enhancement to Smart Selective Merge Technology:
- Architectural drift detection for branch quality assessment
- Code entropy analysis for integration risk evaluation  
- Pattern adherence validation for compatibility checking
- Predictive refactoring guidance for merge strategies

Integrates the extracted Architectural Sonar with SSMT intelligence.

Author: GitHub Copilot Agent
Created: 2025-09-24  
Phase: SSMT v2.2 Evolution
"""

import ast
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import importlib

# Dynamic imports for graceful degradation
try:
    yaml = importlib.import_module("yaml")
except ImportError:
    yaml = None

try:
    _radon_complexity = importlib.import_module("radon.complexity")
    _radon_metrics = importlib.import_module("radon.metrics") 
    cc_rank = getattr(_radon_complexity, "cc_rank")
    mi_rank = getattr(_radon_metrics, "mi_rank")
except ImportError:
    def cc_rank(value): return "N/A"
    def mi_rank(value): return "N/A"

class SSMTArchitecturalSonar:
    """SSMT v2.2 with Integrated Architectural Intelligence"""
    
    def __init__(self):
        self.workspace_root = Path("/workspaces/aurora-cloudbank-symbolicf")
        self.results = {
            "ssmt_version": "2.2-ArchSonar",
            "start_time": datetime.now().isoformat(),
            "architectural_analysis": [],
            "enhanced_branch_assessments": [],
            "status": "initializing"
        }
        
        # Enhanced SSMT patterns with architectural awareness
        self.ssmt_patterns = {
            "architectural_safety_files": [
                "scripts/*.py", "docs/**/*.md", ".github/workflows/*.yml",
                "configs/*.json", "configs/*.yaml"
            ],
            "critical_architecture_files": [
                "src/core/native_vsa.py", "src/aurora/core/symbolic_engine.py",
                "modules/opal2/plugin_system.py", "aurora_api.py"
            ],
            "entropy_indicators": [
                "complexity_increase", "dependency_violations", 
                "pattern_drift", "maintainability_decline"
            ],
            "quality_thresholdsf": {
                "maintainability_index_min": 65,
                "cyclomatic_complexity_max": 10,
                "architectural_drift_max": 3
            }
        }
        
        # Target branches for enhanced architectural analysis
        self.analysis_targets = [
            "feature/digital-ghost-dlp-sonar",
            "codex/implement-opal2-core-and-regex-generation-engine", 
            "dependabot/npm_and_yarn/dotenv-17.0.1",
            "codex/enhance-arc-and-open-pr",
            "copilot/fix-0036cd47-826f-4065-81c3-8391d7236154"
        ]

    def run_command(self, command: str, check_return: bool = True) -> Optional[subprocess.CompletedProcess]:
        """Execute shell command with enhanced error handling - SECURITY FIX"""
        try:
            # SECURITY FIX: Replace shell=True with secure array-based execution
            import shlex
            if isinstance(command, str):
                command_args = shlex.split(command)
            else:
                command_args = command
                
            result = subprocess.run(
                command_args, shell=False, capture_output=True, text=True, 
                cwd=self.workspace_root, timeout=180
            )
            return result if not check_return or result.returncode == 0 else None
        except Exception:
            return None

    def analyze_branch_architecture(self, branch_name: str) -> Dict:
        """Comprehensive architectural analysis of a branch"""
        analysis = {
            "branch": branch_name,
            "start_time": datetime.now().isoformat(),
            "architectural_metrics": {},
            "entropy_assessment": {},
            "pattern_compliance": {},
            "integration_recommendations": []
        }
        
        try:
            print("")
# 🔍 ARCHITECTURAL SONAR: %s", branch_name)

            # Get branch files for analysis
            diff_result = self.run_command(f"git diff --name-only main..origin/{branch_name}", False)
            if not diff_result or diff_result.returncode != 0:
                analysis["error"] = "Branch unavailable for analysis"
                return analysis
                
            changed_files = [f.strip() for f in diff_result.stdout.split('\n') if f.strip().endswith('.py')]
            analysis["python_files_changed"] = len(changed_files)
            
            # Analyze each Python file for architectural metrics
            file_analyses = []
            for file_path in changed_files[:10]:  # Limit for performance
                if any(critical in file_path for critical in self.ssmt_patterns["critical_architecture_files"]):
                    file_analysis = self.analyze_file_architecture(branch_name, file_path)
                    file_analyses.append(file_analysis)
                    print(f"   📊 {file_path}: {file_analysis.get('quality_score', 'N/A')}")
            
            analysis["file_analyses"] = file_analyses
            analysis["architectural_metrics"] = self.compute_branch_architectural_metrics(file_analyses)
            analysis["entropy_assessment"] = self.assess_code_entropy(branch_name, changed_files)
            analysis["pattern_compliance"] = self.check_pattern_compliance(branch_name, changed_files)
            
            # Generate integration recommendations
            analysis["integration_recommendations"] = self.generate_integration_recommendations(analysis)
            
            print(f"   🎯 Quality Score: {analysis['architectural_metrics'].get('overall_quality_score', 'N/A')}")
            print(f"   🏗️ Architecture Risk: {analysis['entropy_assessment'].get('risk_level', 'unknown')}")
            
        except Exception as e:
            analysis["error"] = str(e)
            print(f"   ❌ Analysis error: {e}")
        
        analysis["end_time"] = datetime.now().isoformat()
        return analysis

    def analyze_file_architecture(self, branch_name: str, file_path: str) -> Dict:
        """Detailed architectural analysis of a single file"""
        file_analysis = {
            "file": file_path,
            "metrics": {},
            "violations": [],
            "quality_score": 0
        }
        
        try:
            # Get file content from branch
            show_result = self.run_command(f"git show origin/{branch_name}:{file_path}", False)
            if not show_result or not show_result.stdout:
                return file_analysis
            
            file_content = show_result.stdout
            
            # Parse AST for structural analysis
            try:
                tree = ast.parse(file_content, filename=file_path)
                file_analysis["ast_parsedf"] = True
                
                # Count complexity indicators
                complexity_indicators = {
                    "functions": 0, "classes": 0, "imports": 0, 
                    "nested_depth": 0, "long_functions": 0
                }
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity_indicators["functions"] += 1
                        # Estimate function length (simplified)
                        if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                            if node.end_lineno and node.lineno:
                                func_length = node.end_lineno - node.lineno
                                if func_length > 50:  # Long function threshold
                                    complexity_indicators["long_functions"] += 1
                    elif isinstance(node, ast.ClassDef):
                        complexity_indicators["classes"] += 1
                    elif isinstance(node, (ast.Import, ast.ImportFrom)):
                        complexity_indicators["imports"] += 1
                
                file_analysis["complexity_indicators"] = complexity_indicators
                
            except SyntaxError as e:
                file_analysis["violations"].append(f"Syntax error: {e}")
            
            # Check for SSMT pattern compliance  
            if "NativeDLPTracker" in file_content and "symbolic_operation" in file_content:
                file_analysis["ssmt_compliance"] = "good"
            elif "symbolic_operation" in file_content:
                file_analysis["ssmt_compliance"] = "needs_improvement"
                file_analysis["violations"].append("Symbolic operation without NativeDLPTracker")
            else:
                file_analysis["ssmt_compliance"] = "not_applicable"
            
            # Calculate quality score
            quality_score = 100
            quality_score -= len(file_analysis["violations"]) * 10
            quality_score -= complexity_indicators["long_functions"] * 5
            
            if complexity_indicators["functions"] > 20:
                quality_score -= 15
                
            file_analysis["quality_score"] = max(0, quality_score)
            
        except Exception as e:
            file_analysis["error"] = str(e)
        
        return file_analysis

    def compute_branch_architectural_metrics(self, file_analyses: List[Dict]) -> Dict:
        """Compute overall architectural metrics for the branch"""
        if not file_analyses:
            return {"overall_quality_score": 0, "analysis_count": 0}
        
        metrics = {
            "analysis_count": len(file_analyses),
            "average_quality_score": 0,
            "total_violations": 0,
            "ssmt_compliance_ratio": 0,
            "overall_quality_score": 0
        }
        
        try:
            quality_scores = [fa.get("quality_score", 0) for fa in file_analyses if "quality_score" in fa]
            if quality_scores:
                metrics["average_quality_score"] = sum(quality_scores) / len(quality_scores)
            
            metrics["total_violations"] = sum(len(fa.get("violations", [])) for fa in file_analyses)
            
            # SSMT compliance ratio
            compliant_files = sum(1 for fa in file_analyses 
            if fa.get("ssmt_compliance") in ["good", "not_applicable"])
            metrics["ssmt_compliance_ratio"] = compliant_files / len(file_analyses) if file_analyses else 0
            
            # Overall quality score calculation
            base_score = metrics["average_quality_score"]
            compliance_bonus = metrics["ssmt_compliance_ratio"] * 10
            violation_penalty = min(metrics["total_violations"] * 5, 30)
            
            metrics["overall_quality_score"] = max(0, base_score + compliance_bonus - violation_penalty)
            
        except Exception as e:
            metrics["error"] = str(e)
        
        return metrics

    def assess_code_entropy(self, branch_name: str, changed_files: List[str]) -> Dict:
        """Assess code entropy and architectural drift"""
        entropy_assessment = {
            "total_files": len(changed_files),
            "critical_files_affected": 0,
            "risk_factors": [],
            "risk_level": "low"
        }
        
        # Count critical files affected
        critical_affected = 0
        for file_path in changed_files:
            if any(critical in file_path for critical in self.ssmt_patterns["critical_architecture_files"]):
                critical_affected += 1
        
        entropy_assessment["critical_files_affected"] = critical_affected
        
        # Assess risk factors
        if critical_affected > 0:
            entropy_assessment["risk_factors"].append(f"Critical architecture files affected: {critical_affected}")
        
        if len(changed_files) > 100:
            entropy_assessment["risk_factors"].append(f"High file change count: {len(changed_files)}")
        
        # Determine risk level
        if critical_affected > 2 or len(changed_files) > 200:
            entropy_assessment["risk_level"] = "high"
        elif critical_affected > 0 or len(changed_files) > 50:
            entropy_assessment["risk_level"] = "medium"
        
        return entropy_assessment

    def check_pattern_compliance(self, branch_name: str, changed_files: List[str]) -> Dict:
        """Check compliance with Aurora CloudBank patterns"""
        compliance = {
            "compliant_files": 0,
            "non_compliant_files": 0,
            "compliance_ratio": 0,
            "pattern_violations": []
        }
        
        for file_path in changed_files[:5]:  # Sample check
            show_result = self.run_command(f"git show origin/{branch_name}:{file_path}", False)
            if show_result and show_result.stdout:
                content = show_result.stdout
                
                # Check for DLP patterns
                has_dlp_tracker = "NativeDLPTracker" in content
                has_symbolic_ops = "symbolic_operation" in content
                
                if has_symbolic_ops and not has_dlp_tracker:
                    compliance["non_compliant_files"] += 1
                    compliance["pattern_violations"].append(f"{file_path}: Missing DLP tracking")
                else:
                    compliance["compliant_files"] += 1
        
        total_checked = compliance["compliant_files"] + compliance["non_compliant_files"]
        if total_checked > 0:
            compliance["compliance_ratio"] = compliance["compliant_files"] / total_checked
        
        return compliance

    def generate_integration_recommendations(self, analysis: Dict) -> List[str]:
        """Generate intelligent integration recommendations"""
        recommendations = []
        
        metrics = analysis.get("architectural_metrics", {})
        entropy = analysis.get("entropy_assessment", {})
        patterns = analysis.get("pattern_compliance", {})
        
        overall_quality = metrics.get("overall_quality_score", 0)
        risk_level = entropy.get("risk_level", "unknown")
        compliance_ratio = patterns.get("compliance_ratio", 0)
        
        if overall_quality > 80 and risk_level == "low":
            recommendations.append("✅ High-quality branch - safe for SSMT selective merge")
        elif overall_quality > 60 and compliance_ratio > 0.8:
            recommendations.append("🟡 Moderate quality - consider filtered SSMT integration")
        elif risk_level == "high":
            recommendations.append("🔴 High risk - use SSMT value extraction only")
        else:
            recommendations.append("⚠️ Requires manual review before SSMT processing")
        
        # Specific recommendations based on analysis
        if entropy.get("critical_files_affected", 0) > 0:
            recommendations.append("🛡️ Critical files affected - create compatibility layer")
        
        if patterns.get("pattern_violations"):
            recommendations.append("🔧 Pattern violations detected - apply SSMT enhancement extraction")
        
        if metrics.get("total_violations", 0) > 5:
            recommendations.append("🧹 Multiple violations - recommend pre-integration cleanup")
        
        return recommendations

    def run_ssmt_architectural_analysis(self):
        """Execute SSMT v2.2 with Architectural Sonar Integration"""
        print("🚀 AURORA CLOUDBANK - SSMT v2.2: ARCHITECTURAL SONAR INTEGRATION")
        print("=" * 70)
        print("🧠 SSMT Architectural Sonar v%s", self.results['ssmt_version'])
        print("🎯 Analysis targets: %s branches", len(self.analysis_targets))
        
        self.results["status"] = "running"
        
        # Process each target branch with architectural intelligence
        for branch_name in self.analysis_targets:
            analysis_result = self.analyze_branch_architecture(branch_name)
            self.results["enhanced_branch_assessments"].append(analysis_result)
        
        # Generate overall assessment  
        self.results["overall_assessment"] = self.generate_overall_assessment()
        
        # Save comprehensive results
        self.results["status"] = "completed"
        self.results["end_time"] = datetime.now().isoformat()
        
        with open("SSMT_v2_2_ARCHITECTURAL_ANALYSIS.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Summary report
        total_branches = len(self.analysis_targets)
        high_quality = sum(1 for assessment in self.results["enhanced_branch_assessments"] 
        if assessment.get("architectural_metrics", {}).get("overall_quality_score", 0) > 70)
        
        print(f"\n🎯 SSMT v2.2 ARCHITECTURAL ANALYSIS COMPLETE:")
        print(f"   Branches analyzed: {total_branches}")
        print(f"   High-quality branches: {high_quality}")
        print(f"   Analysis success rate: {(len([a for a in self.results['enhanced_branch_assessments'] if 'error' not in a]) / total_branches * 100):.1f}%")
        
        print(f"\n📄 Detailed results saved to: SSMT_v2_2_ARCHITECTURAL_ANALYSIS.json")
        
        if high_quality > 0:
            print(f"\n🚀 SSMT v2.2 Architectural Analysis completed successfully!")
            print(f"💡 {high_quality} branches ready for enhanced SSMT integration!")
            return True
        else:
            print(f"\n⚠️ Analysis complete - all branches require specialized handling")
            return False

    def generate_overall_assessment(self) -> Dict:
        """Generate overall assessment of all analyzed branches"""
        assessment = {
            "total_branches": len(self.results["enhanced_branch_assessments"]),
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "risk_distributionf": {"low": 0, "medium": 0, "high": 0},
            "integration_strategy_recommendations": []
        }
        
        for branch_analysis in self.results["enhanced_branch_assessments"]:
            if "error" in branch_analysis:
                continue
                
            quality_score = branch_analysis.get("architectural_metrics", {}).get("overall_quality_score", 0)
            risk_level = branch_analysis.get("entropy_assessment", {}).get("risk_level", "unknown")
            
            # Quality distribution
            if quality_score > 70:
                assessment["quality_distribution"]["high"] += 1
            elif quality_score > 40:
                assessment["quality_distribution"]["medium"] += 1
            else:
                assessment["quality_distribution"]["low"] += 1
            
            # Risk distribution
            if risk_level in assessment["risk_distribution"]:
                assessment["risk_distribution"][risk_level] += 1
        
        # Generate strategic recommendations
        if assessment["quality_distribution"]["high"] > 0:
            assessment["integration_strategy_recommendations"].append(
                f"Consider full SSMT integration for {assessment['quality_distribution']['high']} high-quality branches"
            )
        
        if assessment["quality_distribution"]["medium"] > 0:
            assessment["integration_strategy_recommendations"].append(
                f"Apply filtered SSMT approach to {assessment['quality_distribution']['medium']} medium-quality branches"  
            )
        
        if assessment["risk_distribution"]["high"] > 0:
            assessment["integration_strategy_recommendations"].append(
                f"Use value extraction only for {assessment['risk_distribution']['high']} high-risk branches"
            )
        
        return assessment

def main():
    analyzer = SSMTArchitecturalSonar()
    success = analyzer.run_ssmt_architectural_analysis()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()