#!/usr/bin/env python3
from pathlib import Path
import sys
"""
Direct Sonnet 4 Enablement Script
Enables Claude Sonnet 4 for all clients without requiring API to be running
"""

import asyncio
import logging
import sys
from pathlib import Path

from modules.symbolic_core.sonnet4_integration_hub import enable_sonnet4_globally, sonnet4_hub

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main enablement function"""
    print("🚀 Aurora CloudBank Symbolic - Enabling Claude Sonnet 4")
    print("=" * 60)

    try:
        # Check current status
        print("📊 Current Sonnet 4 Status:")
        status = sonnet4_hub.get_global_status()
        for key, value in status.items():
            print(f"   • {key}: {value}")
        print()

        # Enable Sonnet 4 for all clients
        print("🧠 Enabling Claude Sonnet 4 for all clients...")
        results = await enable_sonnet4_globally()

        if "error" not in results:
            print("✅ Claude Sonnet 4 successfully enabled for all clients!")
            print(f"📈 Results: {results}")
        else:
            print(f"❌ Error: {results}")
            return False

        # Show updated status
        print("\n📊 Updated Sonnet 4 Status:")
        updated_status = sonnet4_hub.get_global_status()
        for key, value in updated_status.items():
            print(f"   • {key}: {value}")

        print("\n🎯 Claude Sonnet 4 Features Enabled:")
        print("   • Quantum Bridge Integration")
        print("   • Symbolic Validation")
        print("   • Ethics & Security")
        print("   • Reflective Autonomy")
        print("   • Enhanced Reasoning")
        print("   • GPT-4o Compatibility Preserved")

        print("\n✨ Aurora CloudBank Symbolic with Claude Sonnet 4 is ready!")
        return True

    except Exception as e:
        logger.error("Failed to enable Sonnet 4: %s", e)
        print(f"❌ Failed to enable Claude Sonnet 4: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
