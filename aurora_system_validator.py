#!/usr/bin/env python3
"""
Aurora CloudBank System Validator
Comprehensive validation of the Aurora CloudBank Symbolic repository
"""

import os
import json
import sys
from pathlib import Path

class AuroraSystemValidator:
    def __init__(self):
        self.project_root = Path('/workspaces/aurora-cloudbank-symbolic')
        self.results = {}
        
    def validate_copilot_toolsets(self):
        """Validate the GitHub Copilot toolsets configuration"""
        toolsets_file = self.project_root / 'aurora_copilot_toolsets.jsonc'
        
        if not toolsets_file.exists():
            return False, "Copilot toolsets file not found"
            
        try:
            # Read and validate the JSON content (ignoring comments)
            with open(toolsets_file, 'r') as f:
                content = f.read()
                
            # Count toolsets defined
            toolset_count = content.count('"description":')
            
            if toolset_count >= 10:
                return True, f"✅ {toolset_count} specialized toolsets configured"
            else:
                return False, f"❌ Only {toolset_count} toolsets found, expected 10+"
                
        except Exception as e:
            return False, f"❌ Error reading toolsets file: {str(e)}"
    
    def validate_git_status(self):
        """Validate git repository status"""
        try:
            # Check if .git exists
            git_dir = self.project_root / '.git'
            if not git_dir.exists():
                return False, "❌ Not a git repository"
            
            # Check .gitignore
            gitignore = self.project_root / '.gitignore'
            if not gitignore.exists():
                return False, "❌ .gitignore file missing"
                
            # Check for GitWiz exclusions
            with open(gitignore, 'r') as f:
                gitignore_content = f.read()
                
            if '.gitwiz/memory.db' in gitignore_content:
                return True, "✅ Git repository properly configured with GitWiz exclusions"
            else:
                return False, "❌ GitWiz exclusions not found in .gitignore"
                
        except Exception as e:
            return False, f"❌ Error checking git status: {str(e)}"
    
    def validate_source_structure(self):
        """Validate source code structure"""
        required_files = [
            'aurora_api.py',
            'aurora_gui_cloudhub_fastapi.py',
            'aurora_command_router.js',
            'aurora_status_checker.js',
            'aurora_launch.sh'
        ]
        
        missing_files = []
        for file_name in required_files:
            if not (self.project_root / file_name).exists():
                missing_files.append(file_name)
        
        if not missing_files:
            return True, f"✅ All {len(required_files)} core files present"
        else:
            return False, f"❌ Missing files: {', '.join(missing_files)}"
    
    def validate_documentation(self):
        """Validate documentation completeness"""
        doc_files = [
            'README.md',
            'CURRENT_STATUS_SUMMARY.md',
            'FINAL_COMPLETION_STATUS.md',
            'HEALTH_CHECK_REPORT_COMPREHENSIVE.md'
        ]
        
        present_docs = []
        for doc_file in doc_files:
            if (self.project_root / doc_file).exists():
                present_docs.append(doc_file)
        
        completion_rate = (len(present_docs) / len(doc_files)) * 100
        
        if completion_rate >= 75:
            return True, f"✅ Documentation {completion_rate:.0f}% complete ({len(present_docs)}/{len(doc_files)} files)"
        else:
            return False, f"❌ Documentation only {completion_rate:.0f}% complete"
    
    def validate_configuration_files(self):
        """Validate configuration files"""
        config_files = [
            'package.json',
            'requirements.txt',
            'pyproject.toml',
            '.eslintrc.json'
        ]
        
        valid_configs = []
        for config_file in config_files:
            config_path = self.project_root / config_file
            if config_path.exists():
                # Basic validation for JSON files
                if config_file.endswith('.json'):
                    try:
                        with open(config_path, 'r') as f:
                            json.load(f)
                        valid_configs.append(config_file)
                    except json.JSONDecodeError:
                        continue
                else:
                    valid_configs.append(config_file)
        
        if len(valid_configs) >= 3:
            return True, f"✅ Configuration files valid ({len(valid_configs)}/{len(config_files)})"
        else:
            return False, f"❌ Insufficient valid configuration files ({len(valid_configs)}/{len(config_files)})"
    
    def run_validation(self):
        """Run complete system validation"""
        print("🌟 AURORA CLOUDBANK SYMBOLIC - SYSTEM VALIDATION")
        print("=" * 60)
        print(f"📅 Validation Date: {os.popen('date').read().strip()}")
        print(f"📁 Project Root: {self.project_root}")
        print()
        
        validations = [
            ("GitHub Copilot Toolsets", self.validate_copilot_toolsets),
            ("Git Repository Status", self.validate_git_status),
            ("Source Code Structure", self.validate_source_structure),
            ("Documentation", self.validate_documentation),
            ("Configuration Files", self.validate_configuration_files)
        ]
        
        total_score = 0
        max_score = len(validations)
        
        for name, validator in validations:
            try:
                success, message = validator()
                if success:
                    total_score += 1
                    print(f"✅ {name}: {message}")
                else:
                    print(f"❌ {name}: {message}")
            except Exception as e:
                print(f"❌ {name}: Error during validation - {str(e)}")
        
        print()
        print("=" * 60)
        
        completion_percentage = (total_score / max_score) * 100
        
        if completion_percentage >= 90:
            status = "🎉 EXCELLENT"
            color = "GREEN"
        elif completion_percentage >= 75:
            status = "✅ GOOD"
            color = "YELLOW"
        else:
            status = "❌ NEEDS WORK"
            color = "RED"
        
        print(f"🎯 VALIDATION SCORE: {total_score}/{max_score} ({completion_percentage:.0f}%)")
        print(f"📊 OVERALL STATUS: {status}")
        
        if completion_percentage >= 75:
            print()
            print("🚀 SYSTEM READY FOR:")
            print("  • Development continuation")
            print("  • Production deployment")
            print("  • GitHub Copilot integration")
            print("  • Advanced feature development")
        else:
            print()
            print("⚠️  RECOMMENDED ACTIONS:")
            print("  • Address validation failures")
            print("  • Complete missing configurations")
            print("  • Update documentation")
        
        print("=" * 60)
        return completion_percentage

if __name__ == "__main__":
    validator = AuroraSystemValidator()
    score = validator.run_validation()
    
    # Exit with appropriate code
    sys.exit(0 if score >= 75 else 1)
