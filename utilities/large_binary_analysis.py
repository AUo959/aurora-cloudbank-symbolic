#!/usr/bin/env python3
"""
Aurora CloudBank - Large Binary File Cleanup Analysis
Comprehensive analysis and safe removal recommendations
"""

import os
import subprocess
import json
from datetime import datetime

class LargeBinaryAnalyzer:
    def __init__(self):
        self.large_files = []
        self.safe_to_remove = []
        self.keep_files = []
        self.total_space_savings = 0
        
    def analyze_large_files(self):
        """Analyze large files and categorize them for potential removal"""
        
        print("🔍 Aurora CloudBank - Large Binary File Analysis")
        print("=" * 55)
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Files that are definitely safe to remove
        safe_removal_candidates = [
            # Virtual environments (can be recreated)
            "./venv_opal2/",
            
            # Large ZIP archives (likely temporary or backup files)
            "./SRB_SHADOWFAX_Stillness_v1.0.zip",  # 7.3MB
            "./CASK_Assets.zip",  # 482KB
            
            # Large JSON reports (can be regenerated)
            "./REPOSITORY_AUDIT_REPORT.json",  # 3.9MB
            
            # Large PDF documentation (keep essential ones only)
            "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf",  # 4.3MB
        ]
        
        # Files to keep (essential for project)
        keep_files = [
            # Essential project archives
            "./Aurora_CloudBank_Repo_Seed_v1.zip",
            "./aurora_symbolic_system_scaffold.zip",
            
            # Core documentation
            "./docs/operational/guides/CASK_ Culturally Aware Simulation Knowledge Core.pdf",
            "./docs/operational/guides/Aurora G.S.O.P._ A Comprehensive Framework for Rec.pdf",
        ]
        
        print("📊 Analysis Results:")
        print()
        
        print("🗑️  SAFE TO REMOVE (High Confidence):")
        estimated_savings = 0
        
        # Check venv_opal2
        if os.path.exists("./venv_opal2"):
            venv_size = self._get_directory_size("./venv_opal2")
            print(f"   📁 ./venv_opal2/ - {venv_size:.1f}MB (Virtual environment - can be recreated)")
            estimated_savings += venv_size
            self.safe_to_remove.append("./venv_opal2/")
        
        # Check large ZIP file
        if os.path.exists("./SRB_SHADOWFAX_Stillness_v1.0.zip"):
            zip_size = self._get_file_size("./SRB_SHADOWFAX_Stillness_v1.0.zip")  
            print(f"   📦 ./SRB_SHADOWFAX_Stillness_v1.0.zip - {zip_size:.1f}MB (Large archive)")
            estimated_savings += zip_size
            self.safe_to_remove.append("./SRB_SHADOWFAX_Stillness_v1.0.zip")
        
        # Check large audit report
        if os.path.exists("./REPOSITORY_AUDIT_REPORT.json"):
            json_size = self._get_file_size("./REPOSITORY_AUDIT_REPORT.json")
            print(f"   📋 ./REPOSITORY_AUDIT_REPORT.json - {json_size:.1f}MB (Can be regenerated)")
            estimated_savings += json_size
            self.safe_to_remove.append("./REPOSITORY_AUDIT_REPORT.json")
        
        # Check large PDF
        pdf_path = "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf"
        if os.path.exists(pdf_path):
            pdf_size = self._get_file_size(pdf_path)
            print(f"   📄 Large PDF guide - {pdf_size:.1f}MB (External documentation)")
            estimated_savings += pdf_size
            self.safe_to_remove.append(pdf_path)
        
        print()
        print("✅ KEEP (Essential Files):")
        for file in keep_files:
            if os.path.exists(file):
                size = self._get_file_size(file)
                print(f"   📦 {file} - {size:.1f}MB (Essential)")
        
        print()
        print(f"💾 ESTIMATED SPACE SAVINGS: {estimated_savings:.1f}MB")
        self.total_space_savings = estimated_savings
        
        print()
        print("🎯 RECOMMENDATIONS:")
        print("1. Remove virtual environment (venv_opal2) - easily recreated")
        print("2. Remove large ZIP archives that aren't essential")
        print("3. Remove large audit reports that can be regenerated")
        print("4. Keep essential project files and core documentation")
        print("5. Add removed file patterns to .gitignore")
        
        return estimated_savings > 50  # Recommend cleanup if >50MB savings
    
    def _get_file_size(self, filepath):
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            return size_bytes / (1024 * 1024)
        except:
            return 0
    
    def _get_directory_size(self, dirpath):
        """Get directory size in MB"""
        try:
            result = subprocess.run(['du', '-sm', dirpath], capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.split()[0])
            return 0
        except:
            return 0
    
    def generate_cleanup_script(self):
        """Generate a safe cleanup script"""
        
        cleanup_script = """#!/bin/bash
# Aurora CloudBank - Safe Binary File Cleanup Script
# Generated automatically - review before execution

echo "🧹 Aurora CloudBank - Safe Binary File Cleanup"
echo "============================================="
echo "📅 Cleanup Date: $(date)"
echo ""

# Create backup directory
mkdir -p .cleanup_backup

echo "🗑️  Removing large files safely..."

# Remove virtual environment (can be recreated)
if [ -d "./venv_opal2" ]; then
    echo "   Removing venv_opal2/ (81MB)"
    rm -rf ./venv_opal2
    echo "   ✅ venv_opal2 removed"
fi

# Remove large ZIP archive
if [ -f "./SRB_SHADOWFAX_Stillness_v1.0.zip" ]; then
    echo "   Moving large ZIP to backup..."
    mv "./SRB_SHADOWFAX_Stillness_v1.0.zip" .cleanup_backup/
    echo "   ✅ Large ZIP moved to backup"
fi

# Remove large audit report (can be regenerated)
if [ -f "./REPOSITORY_AUDIT_REPORT.json" ]; then
    echo "   Removing audit report (can be regenerated)"
    rm "./REPOSITORY_AUDIT_REPORT.json"
    echo "   ✅ Audit report removed"
fi

# Remove large PDF documentation
if [ -f "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf" ]; then
    echo "   Moving large PDF to backup..."
    mv "./docs/operational/guides/Comprehensive Guide to Integrating ChatGPT Workflo.pdf" .cleanup_backup/
    echo "   ✅ Large PDF moved to backup"
fi

echo ""
echo "🎉 Cleanup completed successfully!"
echo "💾 Estimated space saved: ~95MB"
echo "📁 Backups available in .cleanup_backup/"
echo ""
echo "📋 Next steps:"
echo "1. Test that everything still works"
echo "2. Recreate venv_opal2 if needed: python3 -m venv venv_opal2"
echo "3. Commit the cleanup changes"
"""
        
        with open('safe_binary_cleanup.sh', 'w') as f:
            f.write(cleanup_script)
        
        print()
        print("📜 Generated cleanup script: safe_binary_cleanup.sh")
        print("🔍 Review the script before running it!")

if __name__ == "__main__":
    analyzer = LargeBinaryAnalyzer()
    should_cleanup = analyzer.analyze_large_files()
    
    if should_cleanup:
        analyzer.generate_cleanup_script()
        print()
        print("🚀 RECOMMENDATION: Proceed with cleanup - significant space savings available!")
    else:
        print()
        print("ℹ️  No significant cleanup needed at this time.")