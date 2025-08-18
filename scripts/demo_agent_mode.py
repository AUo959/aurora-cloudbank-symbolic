#!/usr/bin/env python3
from datetime import datetime
import os
import sys
"""
Aurora CloudBank ChatGPT Agent Mode Demo

Demonstrates the agent mode capabilities with interactive examples.
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from src.integrations.chatgpt_agent_mode import ChatGPTAgentModeIntegration

def print_demo_header():
    """Print demo header"""
    print("🎮 Aurora CloudBank ChatGPT Agent Mode Demo")
    print("=" * 50)
    print()

async def demo_tool_discovery(agent):
    """Demonstrate tool discovery"""
    print("🔍 Demo 1: Tool Discovery")
    print("-" * 30)

    tools_info = await agent.discover_tools()
    print(f"Available tools: {len(tools_info['tools'])}")

    for tool_name, tool_def in tools_info['tools'].items():
        print(f"\n🛠️  {tool_name}")
        print(f"   Description: {tool_def['description']}")
        print(f"   Parameters: {list(tool_def['parameters']['properties'].keys())}")

    print(f"\nSymbolic Anchors: {tools_info['symbolic_anchors']['anchor_seed']}")
    print(f"Ethics Protocol: {tools_info['symbolic_anchors']['ethics_protocol']}")
    print()

async def demo_geometric_algebra(agent):
    """Demonstrate geometric algebra capabilities"""
    print("🧮 Demo 2: Geometric Algebra Computation")
    print("-" * 40)

    test_cases = [
        {"expression_a": "e1", "expression_b": "e2", "operation": "mult"},
        {"expression_a": "e1 + e2", "expression_b": "e3", "operation": "add"},
        {"expression_a": "2*e1", "expression_b": "e1*e2", "operation": "mult"}
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {case['expression_a']} {case['operation']} {case['expression_b']}")

        _ = await agent.execute_tool("geometric_algebra", case)
        if result['success']:
            geo_result = result['result']['geometric_result']
            print(f"Result: {geo_result}")
        else:
            print(f"Error: {result['error']}")
    print()

async def demo_session_management(agent):
    """Demonstrate session management"""
    print("💾 Demo 3: Session Management")
    print("-" * 30)

    # Create session
    print("Creating new session...")
    create_result = await agent.execute_tool("session_management", {
        "action": "create",
        "state_data": {"demo": "session", "timestamp": datetime.now().isoformat()}
    })

    if create_result['success']:
        session_id = create_result['result']['session_id']
        print(f"✅ Session created: {session_id[:8]}...")

        # Update session
        print("Updating session state...")
        update_result = await agent.execute_tool("session_management", {
            "action": "update",
            "session_id": session_id,
            "state_data": {"demo": "updated", "counter": 42}
        })

        if update_result['success']:
            print("✅ Session updated")

            # Get session
            print("Retrieving session state...")
            get_result = await agent.execute_tool("session_management", {
                "action": "get",
                "session_id": session_id
            })

            if get_result['success']:
                state = get_result['result']['state']['state']
                print(f"✅ Session state: {state}")

                # Clean up - delete session
                delete_result = await agent.execute_tool("session_management", {
                    "action": "delete",
                    "session_id": session_id
                })

                if delete_result['success']:
                    print("✅ Session deleted")
    print()

async def demo_symbolic_processing(agent):
    """Demonstrate symbolic processing"""
    print("🔮 Demo 4: Symbolic Processing")
    print("-" * 30)

    operations = [
        {"operation": "quantum_state_preparation", "data": {"qubits": 3, "state": "superposition"}},
        {"operation": "symbolic_differentiation", "data": {"expression": "x^2 + 2*x + 1", "variable": "x"}},
        {"operation": "vector_encoding", "data": {"symbols": ["alpha", "beta", "gamma"], "dimension": 1024}}
    ]

    for i, op in enumerate(operations, 1):
        print(f"\nOperation {i}: {op['operation']}")
        print(f"Input: {op['data']}")

        _ = await agent.execute_tool("symbolic_processing", op)
        if result['success']:
            processed = result['result']
            print(f"Status: ✅ {processed['symbolic_validation']}")
            print(f"Context: {processed['anchor_context']}")
        else:
            print(f"Error: {result['error']}")
    print()

async def demo_system_status(agent):
    """Demonstrate system status reporting"""
    print("📊 Demo 5: System Status")
    print("-" * 25)

    status_levels = ["basic", "detailed", "full"]

    for level in status_levels:
        print(f"\nStatus level: {level}")

        _ = await agent.execute_tool("system_status", {"detail_level": level})
        if result['success']:
            status = result['result']
            print(f"Agent Status: {status['agent_status']}")
            print(f"Active Sessions: {status['active_sessions']}")
            print(f"Available Tools: {len(status['available_tools'])}")

            if level == "detailed":
                print(f"Capabilities: {len(status.get('capabilities', []))}")
                print(f"Sonnet4 Status: {status.get('sonnet4_status', 'unknown')}")

            if level == "full":
                print(f"Tool Registry: {len(status.get('tool_registry', {}))}")
    print()

async def demo_error_handling(agent):
    """Demonstrate error handling and recovery"""
    print("⚠️  Demo 6: Error Handling")
    print("-" * 30)

    # Test invalid tool
    print("Testing invalid tool name...")
    try:
        _ = await agent.execute_tool("non_existent_tool", {})
        print(f"Result: {result['success']} (unexpected)")
    except Exception as e:
        print(f"Error handled: {str(e)[:50]}... ✅")

    # Test invalid parameters
    print("\nTesting invalid parameters...")
    _ = await agent.execute_tool("geometric_algebra", {"invalid": "params"})
    if not result['success']:
        print("Error handled gracefully ✅")
        suggestions = result.get('recovery_suggestions', [])
        print(f"Recovery suggestions: {len(suggestions)}")
        for suggestion in suggestions[:2]:  # Show first 2 suggestions
            print(f"  • {suggestion}")
    else:
        print("Unexpected success")
    print()

async def main():
    """Main demo routine"""
    print_demo_header()

    try:
        # Initialize agent
        agent = ChatGPTAgentModeIntegration()
        print(f"🚀 Agent initialized with status: {agent.agent_status}")
        print()

        # Run demos
        await demo_tool_discovery(agent)
        await demo_geometric_algebra(agent)
        await demo_session_management(agent)
        await demo_symbolic_processing(agent)
        await demo_system_status(agent)
        await demo_error_handling(agent)

        # Final status
        final_status = await agent.get_agent_status()
        print("🎯 Final Integration Status")
        print("-" * 30)
        print(f"Mode: {final_status['agent_mode']}")
        print(f"Version: {final_status['version']}")
        print(f"Tools Available: {final_status['tools_available']}")
        print(f"DLP Compliance: {final_status['dlp_compliance']}")
        print(f"Integration: {final_status['integration_status']}")

        print("\n🎉 Demo completed successfully!")
        print("Aurora CloudBank is ready for ChatGPT Agent Mode integration.")

    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        exit_code = loop.run_until_complete(main())
        loop.close()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(1)
