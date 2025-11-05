#!/bin/bash
# Aurora CloudBank Environment Activation Helper

if [[ -f ".venv/bin/activate" ]]; then
    source .venv/bin/activate
    echo "✅ Aurora CloudBank environment activated"
    echo "🌐 API docs: http://localhost:8000/docs (when running)"
    echo "🧪 Run tests: python -m pytest tests/"
    echo "🔧 Validate deps: python scripts/validate_dependencies.py"
    echo "📊 Status check: make status"
else
    echo "❌ Virtual environment not found"
    echo "Run: bash scripts/setup_environment.sh"
fi
