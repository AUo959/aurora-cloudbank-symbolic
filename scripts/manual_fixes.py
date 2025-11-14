#!/usr/bin/env python3
"""
Manual fix for the 11 most problematic files
These need contextual understanding beyond automation
"""
import logging

logger = logging.getLogger(__name__)

import sys
from pathlib import Path


# File 1: test_runner.py - Rewrite main() function
def fix_test_runner():
    file_path = Path("test_runner.py")
    content = file_path.read_text()
    
    # Find and replace the broken main() function
    broken_main = """def main():
    \"\"\"Main test runner entry point\"\"\"
    runner = AuroraTestRunner()

    
        if len(sys.argv) > 1:
            pass  # Placeholder
        test_type = sys.argv[1].lower()

        
        if test_type == "native":
            _ = runner.run_native_tests()
        
        elif test_type == "unit":
            _ = runner.run_unit_tests()
        
        elif test_type == "smoke":
            _ = runner.run_smoke_tests()
        
        elif test_type == "api":
            _ = runner.run_api_tests()
        
        elif test_type == "benchmark":            result = runner.run_api_tests()        
        elif test_type == "all":
            success = runner.run_all_tests()
            
        sys.exit(0 if success else 1)
        result = runner.run_performance_benchmark()            
        print(f"Unknown test type: {test_type}")
            
        sys.exit(1)
    
    else:
        # Default: run all tests
        _ = runner.run_native_tests()"""
    
    fixed_main = """def main():
    \"\"\"Main test runner entry point\"\"\"
    runner = AuroraTestRunner()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "native":
            success = runner.run_native_tests()
        elif test_type == "unit":
            success = runner.run_unit_tests()
        elif test_type == "smoke":
            success = runner.run_smoke_tests()
        elif test_type == "api":
            success = runner.run_api_tests()
        elif test_type == "benchmark":
            success = runner.run_performance_benchmark()
        elif test_type == "all":
            success = runner.run_all_tests()
        else:
            print(f"Unknown test type: {test_type}")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
    else:
        # Default: run all tests
        success = runner.run_native_tests()"""
    
    if broken_main in content:
        content = content.replace(broken_main, fixed_main)
        file_path.write_text(content)
        logger.info("Fixed test_runner.py")
        return True
    else:
        print("⏭️  test_runner.py - pattern not found")
        return False


# File 2: validate_aurora_system.py - Fix indentation in test_core_documentation
def fix_validate_aurora():
    file_path = Path("validate_aurora_system.py")
    content = file_path.read_text()
    
    broken_func = """def test_core_documentation():
    \"\"\"Test that core documentation exists\"\"\"
    print("📚 Testing Core Documentation...")
        docs = [
        "AURORA_ERROR_RESOLUTION_SUCCESS.md",
        "AURORA_CLOUDBANK_FINAL_STATUS.md",
        "CANONICAL_INTEGRATION_COMPLETE.md",
    ]
        all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            logger.info("{doc} exists")
        
        else:
            logger.error("{doc} missing")
        all_exist = False

    return all_exist"""
    
    fixed_func = """def test_core_documentation():
    \"\"\"Test that core documentation exists\"\"\"
    print("📚 Testing Core Documentation...")
    docs = [
        "AURORA_ERROR_RESOLUTION_SUCCESS.md",
        "AURORA_CLOUDBANK_FINAL_STATUS.md",
        "CANONICAL_INTEGRATION_COMPLETE.md",
    ]
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            logger.info("{doc} exists")
        else:
            logger.error("{doc} missing")
            all_exist = False
    
    return all_exist"""
    
    if broken_func in content:
        content = content.replace(broken_func, fixed_func)
        file_path.write_text(content)
        logger.info("Fixed validate_aurora_system.py")
        return True
    
    # Try alternative fix - just clean up the indentation globally
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Fix the specific error at line 71
        if i == 70 and line.strip().startswith('docs ='):
            # Dedent this and following lines
            fixed_lines.append('    ' + line.lstrip())
        elif 70 < i < 90 and line.startswith(' ' * 8):
            # Dedent over-indented lines in this section
            fixed_lines.append('    ' + line.lstrip())
        else:
            fixed_lines.append(line)
        i += 1
    
    file_path.write_text('\n'.join(fixed_lines))
    logger.info("Fixed validate_aurora_system.py (alternative method)")
    return True


# File 3: Fix aurora_workflow_config.py - Logger statement indentation
def fix_aurora_workflow_config():
    file_path = Path("aurora_workflow_config.py")
    content = file_path.read_text()
    lines = content.split('\n')
    
    # Find line 173 and check if logger is misindented
    if len(lines) > 173 and 'logger.info("Configuration saved' in lines[172]:
        # Fix: It should be inside the with block
        if not lines[172].startswith('            '):
            lines[172] = '            ' + lines[172].lstrip()
            file_path.write_text('\n'.join(lines))
            logger.info("Fixed aurora_workflow_config.py")
            return True
    
    print("⏭️  aurora_workflow_config.py - already correct or pattern changed")
    return False


def main():
    print("🔧 Applying manual fixes to problematic files...\n")
    
    fixes_applied = 0
    
    if fix_test_runner():
        fixes_applied += 1
    
    if fix_validate_aurora():
        fixes_applied += 1
    
    if fix_aurora_workflow_config():
        fixes_applied += 1
    
    print(f"\n✅ Applied {fixes_applied} manual fixes")
    
    # Re-check errors
    import subprocess
    result = subprocess.run(
        ["python3", "-m", "flake8", ".", "--select=E999", "--count"],
        capture_output=True,
        text=True
    )
    print(f"📊 Remaining E999 errors: {result.stdout.strip()}")


if __name__ == "__main__":
    main()
