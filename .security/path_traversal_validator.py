#!/usr/bin/env python3
"""
🛤️ Aurora CloudBank Path Traversal Validator
Security validator for path traversal vulnerabilities
"""
import sys
import re

def validate_path_traversal(file_path):
    """Validate for path traversal vulnerabilities"""
    violations = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Path traversal patterns
        patterns = [
            (r'open\s*\(\s*[^,)]*\+.*["\']\.\./', 'File open with concatenated path traversal'),
            (r'open\s*\(\s*f["\'].*\{.*\}.*\.\./', 'File open with f-string path traversal'),
            (r'Path\s*\(\s*[^,)]*\+.*["\']\.\./', 'Path() with concatenated traversal'),
            (r'os\.path\.join.*\+.*["\']\.\./', 'os.path.join with concatenated traversal'),
            (r'read_file\s*\(\s*[^,)]*\+.*["\']\.\./', 'read_file with concatenated traversal'),
            (r'file_path.*=.*input\(\)', 'Direct user input for file path'),
            (r'filename.*=.*request\.(get|args|form)', 'HTTP request filename without validation'),
            (r'\.\.\/.*\.\.\/.*\.\./', 'Multiple directory traversal sequences'),
            (r'%2e%2e%2f', 'URL-encoded directory traversal'),
            (r'\\\.\\\.\\', 'Windows directory traversal'),
        ]
        
        for i, line in enumerate(lines, 1):
            # Skip comments and safe contexts
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue
                
            for pattern, desc in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check for validation patterns
                    if not any(safe_pattern in line.lower() for safe_pattern in [
                        'validate_path', 'secure_path', 'sanitize_path', 'resolve()', 'is_safe'
                    ]):
                        violations.append(f"Line {i}: {desc} - {line.strip()}")
        
        return violations
    
    except Exception as e:
        return [f"Error reading {file_path}: {e}"]

def main():
    """Main validator function"""
    violations = []
    
    for file_path in sys.argv[1:]:
        if file_path.endswith(('.py', '.js', '.ts')):
            file_violations = validate_path_traversal(file_path)
            if file_violations:
                violations.extend([f"{file_path}: {v}" for v in file_violations])
    
    if violations:
        print("🚨 PATH TRAVERSAL VULNERABILITIES DETECTED:")
        for violation in violations:
            print(f"  ❌ {violation}")
        print("\n💡 Fix: Validate and sanitize file paths, use Path.resolve() and check against allowed directories")
        sys.exit(1)
    
    print("✅ Path traversal validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()