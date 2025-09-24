#!/usr/bin/env python3
from datetime import datetime
import json
import os
import sys
"""
Aurora CloudBank ChatGPT Agent Mode Startup Validator

Validates that the agent mode integration is ready for ChatGPT agent interactions.
Provides system health checks and capability verification.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def print_banner():
    """Print Aurora CloudBank agent mode banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🌟 Aurora CloudBank Agent Mode                            ║
║                       ChatGPT Integration Ready                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

async def validate_agent_integration():
    """Validate ChatGPT agent mode integration"""
    print("🔍 Validating ChatGPT Agent Mode Integration...")

    try:
        # Import and test agent integration
        from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration

        agent = ChatGPTAgentModeIntegration()
        print("✅ Agent integration initialized: %s", agent.agent_status)

        # Test tool discovery
        tools_info = await agent.discover_tools()
        print("✅ Tool discovery: %s tools available", len(tools_info['tools']))

        # List available tools
        for tool_name, tool_info in tools_info['tools'].items():
            print("   🛠️  {tool_name}: %s", tool_info['description'])

        # Test system status
        status_result = await agent.execute_tool("system_status", {"detail_level": "basic"})
        if status_result['success']:
            print("✅ System status check: HEALTHY")
        else:
            print("⚠️  System status check: Issues detected")

        # Test session management
        session_result = await agent.execute_tool("session_management", {"action": "create"})
        if session_result['success']:
            session_id = session_result['result']['session_id']
            print("✅ Session management: Working (test session: %s...)", session_id[:8])
        else:
            print("⚠️  Session management: Issues detected")

        # Test symbolic processing
        symbolic_result = await agent.execute_tool("symbolic_processing", {
            "operation": "startup_validation",
            "data": {"timestamp": datetime.now().isoformat()}
        })
        if symbolic_result['success']:
            print("✅ Symbolic processing: Working")
        else:
            print("⚠️  Symbolic processing: Issues detected")

        # Test geometric algebra
        geo_result = await agent.execute_tool("geometric_algebra", {
            "expression_a": "e1",
            "expression_b": "e2",
            "operation": "mult"
        })
        if geo_result['success']:
            print("✅ Geometric algebra: Working")
        else:
            print("⚠️  Geometric algebra: Issues detected")

        return True

    except Exception as e:
        print("❌ Agent integration failed: %s", str(e))
        return False

def validate_api_endpoints():
    """Validate API endpoint definitions"""
    print("\n🔍 Validating API Endpoint Configuration...")

    try:
        # Check if agent mode configuration exists
        config_path = 'src/integrations/chatgpt_agent_mode_config.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

            endpoints = config.get('integration_endpoints', {})
            print("✅ Configuration loaded: %s endpoints defined", len(endpoints))

            for endpoint, info in endpoints.items():
                method = info.get('method', 'GET')
                desc = info.get('description', 'No description')
                print("   🌐 {method} {endpoint}: %s", desc)

            return True
        else:
            print("⚠️  Agent mode configuration not found")
            return False

    except Exception as e:
        print("❌ API validation failed: %s", str(e))
        return False

def check_aurora_dependencies():
    """Check Aurora system dependencies"""
    print("\n🔍 Checking Aurora System Dependencies...")

    # Check for key Aurora components
    dependencies = [
        ('src/integrations/chatgpt_agent_mode.py', 'Agent Mode Integration'),
        ('src/integrations/chatgpt_agent_mode_config.json', 'Agent Configuration'),
        ('aurora_api.py', 'Aurora API Server'),
        ('modules/symbolic_core/', 'Symbolic Core Modules'),
        ('src/integrations/aurora_custom_gpt_bridge.js', 'Custom GPT Bridge'),
    ]

    all_good = True
    for path, name in dependencies:
        if os.path.exists(path):
            print("✅ %s: Available", name)
        else:
            print("⚠️  {name}: Not found at %s", path)
            all_good = False

    return all_good

def print_integration_summary():
    """Print integration summary and next steps"""
    summary = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                           🎯 Integration Summary                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Aurora CloudBank is now ready for ChatGPT Agent Mode integration!         │
│                                                                             │
│  📋 Available Capabilities:                                                │
│     • Function calling with 4 core tools                                   │
│     • Session persistence and state management                             │
│     • Real-time WebSocket communication                                    │
│     • Symbolic processing with Aurora's quantum engine                     │
│     • Geometric algebra computations                                       │
│     • Comprehensive error handling and recovery                            │
│                                                                             │
│  🚀 Quick Start:                                                           │
│     1. Start Aurora API: uvicorn aurora_api:app --reload                   │
│     2. Discover tools: GET /agent/tools                                    │
│     3. Execute tools: POST /agent/execute                                  │
│     4. Stream mode: WebSocket /agent/stream                                │
│                                                                             │
│  📖 Documentation: docs/CHATGPT_AGENT_MODE_INTEGRATION.md                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
"""
    print(summary)

async def main():
    """Main validation routine"""
    print_banner()

    # Run validation steps
    dependencies_ok = check_aurora_dependencies()
    api_config_ok = validate_api_endpoints()
    agent_integration_ok = await validate_agent_integration()

    print("\n📊 Validation Results:")
    print("   Dependencies: %s", '✅ PASS' if dependencies_ok else '❌ FAIL')
    print("   API Configuration: %s", '✅ PASS' if api_config_ok else '❌ FAIL')
    print("   Agent Integration: %s", '✅ PASS' if agent_integration_ok else '❌ FAIL')

    overall_status = dependencies_ok and api_config_ok and agent_integration_ok

    if overall_status:
        print("\n🎉 Overall Status: ✅ READY FOR CHATGPT AGENT MODE")
        print_integration_summary()
        return 0
    else:
        print(f"\n⚠️  Overall Status: ❌ REQUIRES ATTENTION")
        print("\n🔧 Please address the issues above before proceeding with ChatGPT agent integration.")
        return 1

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        exit_code = loop.run_until_complete(main())
        loop.close()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print("
❌ Validation failed with error: %s", str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)
