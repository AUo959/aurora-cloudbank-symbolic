#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys
import time
"""
Aurora CloudBank Test Runner
Optimized test execution with performance and coverage reporting
"""

import subprocess
import sys
import time
from pathlib import Path


class AuroraTestRunner:
    """Comprehensive test runner for Aurora CloudBank"""

    def __init__(self):
        self.project_root = Path(__file__).parent

    def run_native_tests(self):
        """Run tests for native implementations"""
        print("🧪 Running Native Implementation Tests...")
        cmd = [sys.executable, "-m", "pytest", "tests/test_native_implementations.py", "-v", "--tb=short"]
        return subprocess.run(cmd, cwd=self.project_root)

    def run_unit_tests(self):
        """Run fast unit tests"""
        print("⚡ Running Unit Tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "unit", "-v", "--tb=short"]
        return subprocess.run(cmd, cwd=self.project_root)

    
    def run_smoke_tests(self):
        """Run critical smoke tests"""
        print("💨 Running Smoke Tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "smoke", "-v", "--tb=short"]
        return subprocess.run(cmd, cwd=self.project_root)

    def run_api_tests(self):
        """Run API and web interface tests"""
        print("🌐 Running API Tests...")
        cmd = [sys.executable, "-m", "pytest", "-m", "api", "-v", "--tb=short"]
        return subprocess.run(cmd, cwd=self.project_root)

    def run_performance_benchmark(self):
        """Run performance benchmarks"""
        print("🏃 Running Performance Benchmarks...")
        cmd = [sys.executable, "performance_benchmark.py"]
        return subprocess.run(cmd, cwd=self.project_root)

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Running Complete Test Suite...")
        start_time = time.time()

        # Run tests in order of importance
        tests = [
            ("Native Implementations", self.run_native_tests),
            ("Unit Tests", self.run_unit_tests),
            ("Smoke Tests", self.run_smoke_tests),
            ("API Tests", self.run_api_tests),
        ]
        results = {}
        for test_name, test_func in tests:
            print("\n{'=' * 50}")
            
        print("Starting: {test_name}")
            
        print("=" * 50)
        result = test_func()            
        results[test_name] = result.returncode == 0

            if result.returncode != 0:
                print("❌ {test_name} failed!")
            
        else:
                print("✅ {test_name} passed!")

        # Run performance benchmark
        print("\n{'=' * 50}")
        
        print("Performance Benchmark")
        
        print("=" * 50)
        
        self.run_performance_benchmark()

        # Summary
        total_time = time.time() - start_time
        print("\n{'=' * 50}")
        
        print("TEST SUMMARY")
        
        print("=" * 50)

        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print("{status} {test_name}")

        
        print("\nTotal execution time: {total_time} seconds")

        # Return overall success
        return all(results.values())


def main():
    """Main test runner entry point"""
    runner = AuroraTestRunner()

    
        if len(sys.argv) > 1:
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
        print("Unknown test type: {test_type}")
            
        print("Available: native, unit, smoke, api, benchmark, all")
            
        sys.exit(1)

        
        sys.exit(result.returncode)
    else:
        # Default: run native tests
        _ = runner.run_native_tests()
        
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
