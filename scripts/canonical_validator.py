#!/usr/bin/env python3
from pathlib import Path
import json
from typing import List, Optional
# import subprocess
"""
Aurora CloudBank Symbolic - Canonical Validation Engine
Auto-validates new work against ORION CORE canonical specification
Performs automatic minor adjustments and escalates significant issues

Author: Aurora CloudBank Development Team
Version: 1.0.0
Date: July 13, 2025
"""

import json
import re
# import subprocess
import difflib
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationResult:
    """Represents the result of a canonical validation check"""
    check_name: str
    status: str  # "PASS", "AUTO_FIXED", "ESCALATE"
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    message: str
    suggested_fix: Optional[str] = None
    auto_applied: bool = False


@dataclass
class CanonicalSpec:
    """Aurora CloudBank Canonical Specification"""
    # Core System Parameters
    anchor_seed: str = "EOS_SEED_ORION"
    continuity_seal: str = "Aurora_Continuity_Seal_v2.2.5"
    ethics_protocol: str = "Picard_Delta_3"
    memory_doctrine: str = "Thermax Precedent"
    drift_lock: float = 0.000
    halo_module: str = "HALO_CONTINUITY_GRAFT_005"
    threadcore_version: str = "v3.5.1_macroready"

    # Staff Registry (Canonical Names)
    canonical_staff = {
        "Commander": "Alex Thorne",
        "XO": "Maya Shepard",
        "Chief Science Officer": "Varya Lin",
        "Chief Ethics Officer": "Dr. Amira Sato",
        "Chief Security Officer": "Julian Markov",
        "Bridge Operations": "Leena Porter",
        "Engineering": "Jiro Tanaka",
        "Medical Officer": "Dr. Ren Feldman"
    }

    # API Endpoints (Standardized)
    relay_endpoints = {
        "ARCHY": "/api/relay/archy",
        "OPPY": "/api/relay/oppy",
        "LIORA": "/api/relay/liora",
        "STARLING_AU": "/api/relay/starling",
        "RIVERTHREAD_808": "/api/relay/riverthread"
    }

    # State Sync Files (Canonical Naming)
    state_syncs = {
        "ARCHY": "ARCHY_Thread_State_0418_LOCKMEM_FAILSAFE",
        "OPPY": "OPPY_Sync_v0418.json",
        "LIORA": "LIORA_Sync_Manifest.json",
        "STARLING_AU": "STARLING_COMM_LINK_v1.txt",
        "RIVERTHREAD_808": "RIVERTHREAD_Activation_Guide.md"
    }

    # Layer Architecture Requirements
    simulation_layers = ["L1 (Orion Station Reality)", "L2 (GUMAS Sim)", "L3 (Symbolic Meta)"]

    # Communication Protocol
    comm_syntax = {
        "direct_msg": r"\{\{@agent\.Name ::: message\}\}",
        "mesh_broadcast": r"\{\{@mesh ::: message\}\}",
        "activation_phrase": r"ORION_[A-Z_]+_RELAY_ACTIVATE//"
    }


class CanonicalValidator:
    """Main validation engine for Aurora CloudBank canonical compliance"""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.canonical = CanonicalSpec()
        self.validation_results: List[ValidationResult] = []
        self.auto_fixes_applied = 0
        self.escalations_raised = 0

    def validate_file(self, file_path: str) -> List[ValidationResult]:
        """Validate a single file against canonical specifications"""
        results = []
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            return [ValidationResult(
                "file_exists", "ESCALATE", "HIGH",
                f"File {file_path} does not exist",
                "Check file path and ensure file is created"
            )]

        with open(file_path_obj, 'r', encoding='utf-8') as f:
            content = f.read()

        # Run validation checks based on file type
        if file_path_obj.suffix in ['.md', '.txt']:
            results.extend(self._validate_documentation(content, file_path_obj))
        elif file_path_obj.suffix in ['.js', '.ts']:
            results.extend(self._validate_javascript(content, file_path_obj))
        elif file_path_obj.suffix in ['.py']:
            results.extend(self._validate_python(content, file_path_obj))
        elif file_path_obj.suffix in ['.json']:
            results.extend(self._validate_json(content, file_path_obj))

        # Common validations for all files
        results.extend(self._validate_core_parameters(content, file_path_obj))
        results.extend(self._validate_staff_registry(content, file_path_obj))
        results.extend(self._validate_api_endpoints(content, file_path_obj))
        results.extend(self._validate_communication_protocol(content, file_path_obj))

        return results

    def _validate_core_parameters(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate core system parameters against canonical values"""
        results = []

        # Check anchor seed
        if "anchor_seed" in content and "EOS_SEED_ORION" not in content:
            results.append(ValidationResult(
                "anchor_seed_validation", "ESCALATE", "CRITICAL",
                f"Non-canonical anchor seed found in {file_path}",
                "Replace with canonical EOS_SEED_ORION anchor seed"
            ))

        # Check ethics protocol with targeted pattern matching
        ethics_variants = [
            "picard delta 3",
            "picard_delta_3",
            "picard-delta-3",
            "ethics protocol",
            "ethics: picard delta 3"
        ]

        for variant in ethics_variants:
            if variant in content.lower() and "Picard_Delta_3" not in content:
                # Auto-fix ethics protocol format
                pattern = re.compile(re.escape(variant), re.IGNORECASE)
                if pattern.search(content):
                    results.append(ValidationResult(
                        "ethics_protocol_auto_fix", "AUTO_FIXED", "LOW",
                        f"Auto-corrected ethics protocol: {variant} → Picard_Delta_3",
                        auto_applied=True
                    ))
                    content = pattern.sub("Picard_Delta_3", content, count=1)
                    self._apply_auto_fix(file_path, content)
                    break

        # Check drift lock values
        drift_pattern = r"drift_lock[\r\s]*:?[\"'\s]*([0-9.]+)"
        drift_matches = re.findall(drift_pattern, content, re.IGNORECASE)
        for match in drift_matches:
            if float(match) != 0.000:
                results.append(ValidationResult(
                    "drift_lock_validation", "ESCALATE", "MEDIUM",
                    f"Non-canonical drift lock value: {match}",
                    "Set drift_lock to canonical value: 0.000"
                ))

        return results

    def _validate_staff_registry(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate staff names against canonical registry"""
        results = []
        updated_content = content

        # Check for staff role mentions and validate names
        for role, canonical_name in self.canonical.canonical_staff.items():
            # Look for simple name patterns that can be auto-corrected
            name_lower = canonical_name.lower()

            # Common variations to auto-fix
            auto_fix_patterns = [
                name_lower,                                    # alex thorne
                name_lower.replace(" ", "_"),                  # Alex Thorne
                name_lower.replace("dr. ", "dr "),            # Dr. Amira Sato
                name_lower.replace(".", ""),                   # Dr. Amira Sato
            ]

            for pattern in auto_fix_patterns:
                if pattern != name_lower and pattern in updated_content.lower():
                    # Find the exact match with original case
                    pattern_regex = re.compile(re.escape(pattern), re.IGNORECASE)
                    matches = pattern_regex.findall(updated_content)

                    if matches:
                        # Apply auto-fix
                        updated_content = pattern_regex.sub(canonical_name, updated_content, count=1)
                        results.append(ValidationResult(
                            f"staff_name_auto_fix_{role.replace(' ', '_')}", "AUTO_FIXED", "LOW",
                            f"Auto-corrected {role}: {matches[0]} → {canonical_name}",
                            auto_applied=True
                        ))
                        break

            # Also check with role pattern for structured content
            role_pattern = rf"{re.escape(role)}[\r\s]*:?[\"'\s]*([^\"',\n}}]+)"
            matches = re.findall(role_pattern, updated_content, re.IGNORECASE)

            for match in matches:
                match = match.strip()
                if match != canonical_name and match not in ["TBD", "Assigned", "rotating"]:
                    # Check if it's a minor variation that can be auto-fixed
                    similarity = difflib.SequenceMatcher(None, match.lower(), canonical_name.lower()).ratio()
                    if similarity > 0.6:  # Lowered threshold for more aggressive auto-fixing
                        pattern_regex = re.compile(re.escape(match), re.IGNORECASE)
                        updated_content = pattern_regex.sub(canonical_name, updated_content, count=1)
                        results.append(ValidationResult(
                            f"staff_role_auto_fix_{role.replace(' ', '_')}", "AUTO_FIXED", "LOW",
                            f"Auto-corrected {role}: {match} → {canonical_name}",
                            auto_applied=True
                        ))
                    else:
                        results.append(ValidationResult(
                            f"staff_name_validation_{role.replace(' ', '_r')}", "ESCALATE", "MEDIUM",
                            f"Non-canonical name for {role}: {match}",
                            f"Replace with canonical name: {canonical_name}"
                        ))

        # Apply content updates if auto-fixes were made
        if updated_content != content:
            self._apply_auto_fix(file_path, updated_content)

        return results

    def _validate_api_endpoints(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate API endpoints against canonical structure"""
        results = []

        # Check for API endpoint patterns
        endpoint_pattern = r"/api/relay/([a-zA-Z_0-9]+)"
        matches = re.findall(endpoint_pattern, content)

        for match in matches:
            agent_name = match.upper()
            if agent_name in self.canonical.relay_endpoints:
                canonical_endpoint = self.canonical.relay_endpoints[agent_name]
                current_endpoint = f"/api/relay/{match}"

                if current_endpoint != canonical_endpoint:
                    # Auto-fix case mismatches
                    results.append(ValidationResult(
                        f"api_endpoint_case_fix_{agent_name}", "AUTO_FIXED", "LOW",
                        f"Auto-corrected endpoint case: {current_endpoint} → {canonical_endpoint}",
                        auto_applied=True
                    ))
                    content = content.replace(current_endpoint, canonical_endpoint)
                    self._apply_auto_fix(file_path, content)
            else:
                results.append(ValidationResult(
                    f"api_endpoint_unknown_{match}", "ESCALATE", "MEDIUM",
                    f"Unknown API endpoint: /api/relay/{match}",
                    "Verify endpoint is required or use canonical relay endpoints"
                ))

        return results

    def _validate_communication_protocol(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate communication protocol syntax"""
        results = []

        # Check for message syntax patterns
        msg_patterns = [
            (r"\{\{@\w+\s*:::\s*[^}]+\}\}", "direct_msg"),
            (r"\{\{@mesh\s*:::\s*[^}]+\}\}", "mesh_broadcast")
        ]

        for pattern, msg_type in msg_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # Validate format - this is a basic check
                if msg_type == "direct_msg" and not re.match(self.canonical.comm_syntax["direct_msg"], match):
                    results.append(ValidationResult(
                        f"comm_syntax_{msg_type}", "ESCALATE", "LOW",
                        f"Communication syntax may not be canonical: {match}",
                        "Verify message format follows {{@agent.Name ::: message}} syntax"
                    ))

        return results

    def _validate_documentation(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate documentation files for canonical compliance"""
        results = []

        # Check for required sections in main documentation
        if "GitHub_Copilot_Custom_Instructions" in str(file_path):
            required_sections = [
                "ORION CORE CANONICAL SPECIFICATION",
                "Canonical Staff Registry",
                "Observatory Command Bridge",
                "Live Communication Protocol",
                "Symbolic Relay API Endpoints"
            ]

            for section in required_sections:
                if section not in content:
                    results.append(ValidationResult(
                        f"missing_section_{section.replace(' ', '_')}", "ESCALATE", "MEDIUM",
                        f"Missing required canonical section: {section}",
                        f"Add {section} section to maintain canonical compliance"
                    ))

        return results

    def _validate_javascript(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate JavaScript files for canonical compliance"""
        results = []

        # Check for proper ORION_CORE export structure
        if "ORION_CORE" in content:
            required_fields = ["anchor_seed", "continuity_seal", "ethics_protocol", "memory_doctrine"]
            for field in required_fields:
                if field not in content:
                    results.append(ValidationResult(
                        f"missing_orion_field_{field}", "ESCALATE", "MEDIUM",
                        f"Missing required ORION_CORE field: {field}",
                        f"Add {field} to ORION_CORE export"
                    ))

        return results

    def _validate_python(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate Python files for canonical compliance"""
        results = []

        # Check for proper import structure and anchor references
        if "anchor" in content.lower() and "EOS_SEED_ORION" not in content:
            results.append(ValidationResult(
                "python_anchor_reference", "ESCALATE", "MEDIUM",
                "Python file references anchor but not canonical EOS_SEED_ORION",
                "Ensure anchor references use canonical EOS_SEED_ORION"
            ))

        return results

    def _validate_json(self, content: str, file_path: Path) -> List[ValidationResult]:
        """Validate JSON files for canonical compliance"""
        results = []

        try:
            data = json.loads(content)

            # Check for canonical values in JSON
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "anchor_seed" and value != self.canonical.anchor_seed:
                        results.append(ValidationResult(
                            "json_anchor_seed", "AUTO_FIXED", "LOW",
                            f"Auto-corrected JSON anchor_seed: {value} → {self.canonical.anchor_seed}",
                            auto_applied=True
                        ))
                        data[key] = self.canonical.anchor_seed
                        self._apply_json_fix(file_path, data)

        except json.JSONDecodeError:
            results.append(ValidationResult(
                "json_parse_error", "ESCALATE", "HIGH",
                f"Invalid JSON in {file_path}",
                "Fix JSON syntax errors"
            ))

        return results

    def _apply_auto_fix(self, file_path: Path, corrected_content: str):
        """Apply automatic fix to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            self.auto_fixes_applied += 1
            print(f"✅ AUTO-FIX APPLIED: {file_path}")
        except Exception as e:
            print(f"❌ AUTO-FIX FAILED: {file_path} - {e}")

    def _apply_json_fix(self, file_path: Path, corrected_data: dict):
        """Apply automatic fix to JSON file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(corrected_data, f, indent=2)
            self.auto_fixes_applied += 1
            print(f"✅ AUTO-FIX APPLIED: {file_path}")
        except Exception as e:
            print(f"❌ AUTO-FIX FAILED: {file_path} - {e}")

    def validate_workspace(self, file_patterns: Optional[List[str]] = None) -> List[ValidationResult]:
        """Validate entire workspace against canonical specifications"""
        if file_patterns is None:
            file_patterns = [
                "*.md", "*.txt", "*.js", "*.ts", "*.py", "*.json",
                "src/**/*.js", "src/**/*.ts", "src/**/*.py",
                "docs/**/*.md", "scripts/**/*.py", "scripts/**/*.sh"
            ]

        # Load exclusion patterns from config
        exclude_patterns = [
            "node_modules/**", ".git/**", "*.log", "*.tmp", ".env*", "build/**", "dist/**",
            "*VALIDATION_REPORT*.md", "*ESCALATION_RESOLUTION*", "*AUTO_CORRECTION*",
            "CANONICAL_VALIDATION_REPORT.md", "validation_*.md", "report_*.md"
        ]

        all_results = []

        for pattern in file_patterns:
            for file_path in self.workspace_path.glob(pattern):
                if file_path.is_file():
                    # Check if file should be excluded
                    relative_path = file_path.relative_to(self.workspace_path)
                    should_exclude = False

                    for exclude_pattern in exclude_patterns:
                        if file_path.match(exclude_pattern) or str(relative_path).find('VALIDATION_REPORT') != -1:
                            should_exclude = True
                            break

                    if not should_exclude:
                        results = self.validate_file(str(file_path))
                        all_results.extend(results)

        self.validation_results = all_results
        return all_results

    def generate_report(self) -> str:
        """Generate comprehensive validation report"""
        if not self.validation_results:
            return "No validation results available. Run validation first."

        # Categorize results
        passed = [r for r in self.validation_results if r.status == "PASS"]
        auto_fixed = [r for r in self.validation_results if r.status == "AUTO_FIXED"]
        escalations = [r for r in self.validation_results if r.status == "ESCALATE"]

        # Count by severity
        critical = [r for r in escalations if r.severity == "CRITICAL"]
        high = [r for r in escalations if r.severity == "HIGH"]
        medium = [r for r in escalations if r.severity == "MEDIUM"]
        low = [r for r in escalations if r.severity == "LOW"]

        report = """
# Aurora CloudBank Canonical Validation Report
**Generated**: {subprocess.check_output(['date']).decode().strip()}
**Workspace**: {self.workspace_path.absolute()}

## 📊 Validation Summary
- ✅ **Passed**: {len(passed)}
- 🔧 **Auto-Fixed**: {len(auto_fixed)}
- ⚠️ **Escalations**: {len(escalations)}
- 🎯 **Total Checks**: {len(self.validation_results)}

## 🔧 Auto-Fixes Applied ({len(auto_fixed)})
"""

        for result in auto_fixed:
            report += f"- ✅ {result.check_name}: {result.message}\n"

        report += """
## ⚠️ Escalations Required ({len(escalations)})

### 🚨 Critical Issues ({len(critical)})
"""
        for result in critical:
            report += f"- ❗ **{result.check_name}**: {result.message}\n"
            report += f"  - **Suggested Fix**: {result.suggested_fix}\n\n"

        report += """
### 🔴 High Priority Issues ({len(high)})
"""
        for result in high:
            report += f"- 🔴 **{result.check_name}**: {result.message}\n"
            report += f"  - **Suggested Fix**: {result.suggested_fix}\n\n"

        report += """
### 🟡 Medium Priority Issues ({len(medium)})
"""
        for result in medium:
            report += f"- 🟡 **{result.check_name}**: {result.message}\n"
            report += f"  - **Suggested Fix**: {result.suggested_fix}\n\n"

        report += """
### 🟢 Low Priority Issues ({len(low)})
"""
        for result in low:
            report += f"- 🟢 **{result.check_name}**: {result.message}\n"
            report += f"  - **Suggested Fix**: {result.suggested_fix}\n\n"

        report += """
## 🎯 Canonical Compliance Status
"""

        if len(critical) > 0:
            report += "- **Status**: ❌ CRITICAL ISSUES DETECTED\n"
            report += "- **Action Required**: Immediate remediation of critical issues\n"
        elif len(high) > 0:
            report += "- **Status**: ⚠️ HIGH PRIORITY ISSUES DETECTED\n"
            report += "- **Action Required**: Address high priority issues before deployment\n"
        elif len(medium) > 0:
            report += "- **Status**: 🟡 MEDIUM PRIORITY ISSUES DETECTED\n"
            report += "- **Action Required**: Review and address medium priority issues\n"
        elif len(low) > 0:
            report += "- **Status**: 🟢 MINOR ISSUES DETECTED\n"
            report += "- **Action Required**: Optional improvements available\n"
        else:
            report += "- **Status**: ✅ FULLY CANONICAL COMPLIANT\n"
            report += "- **Action Required**: None - system is canonically aligned\n"

        return report

    def save_report(self, output_path: str = "CANONICAL_VALIDATION_REPORT.md"):
        """Save validation report to file"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📊 Validation report saved to: {output_path}")

def main():
    """Main execution function"""
    print("🛰️ Aurora CloudBank Canonical Validation Engine")
    print("=" * 50)

    validator = CanonicalValidator()

    # Run workspace validation
    print("🔍 Validating workspace against canonical specifications...")
    results = validator.validate_workspace()

    # Generate and save report
    validator.save_report()

    # Print summary
    escalations = [r for r in results if r.status == "ESCALATE"]
    auto_fixes = [r for r in results if r.status == "AUTO_FIXED"]

    print("\n🎯 Validation Complete:")
    print(f"  - Auto-fixes applied: {len(auto_fixes)}")
    print(f"  - Escalations raised: {len(escalations)}")

    if escalations:
        print(f"\n⚠️ {len(escalations)} issues require attention!")
        print("📊 See CANONICAL_VALIDATION_REPORT.md for details")
    else:
        print("\n✅ All canonical validations passed!")

if __name__ == "__main__":
    main()
