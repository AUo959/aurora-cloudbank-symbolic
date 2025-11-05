#!/bin/bash
# Aurora CloudBank Test Suite
# Quick test execution scripts for common scenarios

echo "🚀 Aurora CloudBank Test Suite"
echo "==============================="

# Function to display usage
usage() {
    echo "Usage: $0 [test-type]"
    echo ""
    echo "Available test types:"
    echo "  native     - Test native implementations (fast)"
    echo "  unit       - Run unit tests"
    echo "  smoke      - Run smoke tests"
    echo "  api        - Test API functionality"
    echo "  benchmark  - Run performance benchmarks"
    echo "  all        - Run complete test suite"
    echo "  quick      - Quick validation (native + smoke)"
    echo ""
    echo "Examples:"
    echo "  $0 native     # Test native implementations"
    echo "  $0 quick      # Quick validation"
    echo "  $0 all        # Full test suite"
}

# Check if python test runner exists
if [ ! -f "test_runner.py" ]; then
    echo "❌ test_runner.py not found!"
    exit 1
fi

# Get test type from argument
TEST_TYPE=${1:-"native"}

case $TEST_TYPE in
    "native")
        echo "🧪 Running Native Implementation Tests..."
        python3 test_runner.py native
        ;;
    "unit")
        echo "⚡ Running Unit Tests..."
        python3 test_runner.py unit
        ;;
    "smoke")
        echo "💨 Running Smoke Tests..."
        python3 test_runner.py smoke
        ;;
    "api")
        echo "🌐 Running API Tests..."
        python3 test_runner.py api
        ;;
    "benchmark")
        echo "🏃 Running Performance Benchmarks..."
        python3 test_runner.py benchmark
        ;;
    "all")
        echo "🚀 Running Complete Test Suite..."
        python3 test_runner.py all
        ;;
    "quick")
        echo "⚡ Quick Validation Tests..."
        echo ""
        echo "Step 1: Native Implementation Tests"
        python3 test_runner.py native
        if [ $? -ne 0 ]; then
            echo "❌ Native tests failed!"
            exit 1
        fi
        
        echo ""
        echo "Step 2: Smoke Tests"
        python3 test_runner.py smoke
        if [ $? -ne 0 ]; then
            echo "❌ Smoke tests failed!"
            exit 1
        fi
        
        echo ""
        echo "✅ Quick validation completed successfully!"
        ;;
    "help"|"-h"|"--help")
        usage
        exit 0
        ;;
    *)
        echo "❌ Unknown test type: $TEST_TYPE"
        echo ""
        usage
        exit 1
        ;;
esac

exit $?
