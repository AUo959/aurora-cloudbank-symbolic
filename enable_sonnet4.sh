#!/bin/bash

# Aurora CloudBank Symbolic - Sonnet 4 Enablement Script
# Automatically enables Claude Sonnet 4 for all clients

echo "🚀 Aurora CloudBank Symbolic - Enabling Claude Sonnet 4"
echo "================================================"

# Check if the API is running
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "⚠️  Starting Aurora API first..."
    python -m uvicorn aurora_api:app --host 0.0.0.0 --port 8000 &
    API_PID=$!
    sleep 5
fi

# Enable Sonnet 4 for all clients
echo "🧠 Enabling Claude Sonnet 4 for all clients..."
response=$(curl -s -X POST "http://localhost:8000/sonnet4/enable" \
    -H "Content-Type: application/json" \
    -d '{"enable_all": true}')

if echo "$response" | grep -q '"status": "success"'; then
    echo "✅ Claude Sonnet 4 successfully enabled for all clients!"
    echo "📊 Status:"
    curl -s "http://localhost:8000/sonnet4/status" | python -m json.tool
else
    echo "❌ Failed to enable Claude Sonnet 4"
    echo "Response: $response"
    exit 1
fi

echo ""
echo "🎯 Claude Sonnet 4 is now active with the following features:"
echo "   • Quantum Bridge Integration"
echo "   • Symbolic Validation"
echo "   • Ethics & Security"
echo "   • Reflective Autonomy"
echo "   • Enhanced Reasoning"
echo "   • GPT-4o Compatibility Preserved"
echo ""
echo "🔗 Access endpoints:"
echo "   • Status: http://localhost:8000/sonnet4/status"
echo "   • Enable: http://localhost:8000/sonnet4/enable"
echo "   • Client Status: http://localhost:8000/sonnet4/clients/{client_id}"
echo ""
echo "✨ Aurora CloudBank Symbolic with Claude Sonnet 4 is ready!"
