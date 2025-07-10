#!/usr/bin/env python3
"""
Quick fix for duplicate encoding parameters
"""
import re
from pathlib import Path

def fix_duplicate_encoding():
    """Fix duplicate encoding parameters in all files"""
    files_to_fix = [
        "security_remediation.py",
        "aurora_enhanced_security.py", 
        "aurora_security_validation.py"
    ]
    
    for filename in files_to_fix:
        file_path = Path(filename)
        if not file_path.exists():
            continue
            
        print(f"🔧 Fixing encoding in {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix multiple encoding parameters
        content = re.sub(r', encoding="utf-8", encoding="utf-8"', '', content)
        content = re.sub(r', encoding="utf-8", encoding=\'utf-8\'', '', content)
        content = re.sub(r'encoding="utf-8", encoding="utf-8", encoding=\'utf-8\'', 'encoding="utf-8"', content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed {filename}")

if __name__ == "__main__":
    fix_duplicate_encoding()
    print("🎉 All encoding issues fixed!")
