#!/bin/bash
# Aurora CloudBank Selective Test Runner

echo "🧪 Aurora CloudBank Selective Test Runner"
echo "========================================"

# Performance-optimized test commands
echo ""
echo "🚀 Quick Test Commands:"
echo "----------------------"

echo "# Smoke tests (critical functionality, ~30 seconds)"
echo "pytest -m smoke -v"

echo ""
echo "# Unit tests only (fast, ~2 minutes)"
echo "pytest -m unit -v"

echo ""
echo "# Opal2 system tests only"
echo "pytest -m opal2 -v"

echo ""
echo "# Security tests only"
echo "pytest -m security -v"

echo ""
echo "# Integration tests (slower, ~5-10 minutes)"
echo "pytest -m integration -v"

echo ""
echo "🎯 Targeted Test Commands:"
echo "-------------------------"

echo "# Test specific components"
echo "pytest -m 'aurora and unit' -v          # Aurora unit tests only"
echo "pytest -m 'opal2 and not slow' -v       # Fast Opal2 tests"
echo "pytest -m 'api or cli' -v               # Interface tests"
echo "pytest -m 'not (slow or network)' -v    # Skip slow/network tests"

echo ""
echo "⚡ Performance Commands:"
echo "----------------------"

echo "# Fastest tests (under 1 second each)"
echo "pytest -m 'unit and not slow' --maxfail=5 -q"

echo "# Memory-focused tests"
echo "pytest -m memory --tb=short -v"

echo "# Performance benchmarking"
echo "pytest -m performance --benchmark-only -v"

echo ""
echo "🔧 Development Workflow Commands:"
echo "--------------------------------"

echo "# Pre-commit validation (essential tests)"
echo "pytest -m 'smoke or critical' --maxfail=3 -q"

echo "# File-specific testing"
echo "pytest tests/test_opal2_system.py -v"
echo "pytest tests/test_security.py -m 'not slow' -v"

echo ""
echo "📊 Coverage and Reporting:"
echo "------------------------"

echo "# Full coverage report"
echo "pytest --cov=. --cov-report=html -m 'not slow'"

echo "# Coverage for specific modules"
echo "pytest --cov=modules/opal2 --cov-report=term-missing -m opal2"

echo ""
echo "🎮 Interactive Test Selection:"
echo "-----------------------------"

PS3="Select test suite: "
options=("Smoke Tests (30s)" "Unit Tests (2m)" "Opal2 Tests" "Security Tests" "All Fast Tests" "Custom Selection" "Exit")

select opt in "${options[@]}"
do
    case $opt in
        "Smoke Tests (30s)")
            echo "Running smoke tests..."
            pytest -m smoke -v --tb=short
            break
            ;;
        "Unit Tests (2m)")
            echo "Running unit tests..."
            pytest -m unit -v --maxfail=5
            break
            ;;
        "Opal2 Tests")
            echo "Running Opal2 tests..."
            pytest -m opal2 -v
            break
            ;;
        "Security Tests")
            echo "Running security tests..."
            pytest -m security -v --tb=short
            break
            ;;
        "All Fast Tests")
            echo "Running all fast tests..."
            pytest -m 'not slow' -v --maxfail=10
            break
            ;;
        "Custom Selection")
            echo "Enter pytest command (e.g., 'pytest -m \"unit and opal2\" -v'):"
            read -r custom_cmd
            eval "$custom_cmd"
            break
            ;;
        "Exit")
            echo "Exiting test runner"
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac
done
