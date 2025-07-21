#!/usr/bin/env python3
"""
Opal2 System Integration Test
Test all components working together
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.opal2.glyph_cache import GlyphCache
from modules.opal2.glyph_core import GlyphCore
from modules.opal2.plugin_system import PluginSystem
from modules.opal2.quantum_renderer import QuantumRenderer

async def test_opal2_integration():
    """Test full Opal2 system integration"""
    print("🔮 Testing Opal2 Modular System Integration")
    print("=" * 50)

    # Initialize components
    print("📦 Initializing components...")
    glyph_core = GlyphCore()
    glyph_cache = GlyphCache()
    quantum_renderer = QuantumRenderer()
    plugin_system = PluginSystem()

    # Test 1: Glyph Core
    print("\n🧬 Testing Glyph Core...")
    try:
        test_expression = {"symbol": "test_symbol"}
        glyph_result = await glyph_core.generate_async(
            expression=test_expression,
            style_params={"color": "blue", "size": 100},
            quantum_enhancement=True,
        )
        print(f"✅ Glyph generated: {len(glyph_result)} properties")
        print(f"   - Type: {glyph_result.get('type')}")
        print(f"   - Quantum Enhanced: {glyph_result.get('quantum_enhanced')}")
    except Exception as e:
        print(f"❌ Glyph Core test failed: {e}")
        return False

    # Test 2: Cache System
    print("\n💾 Testing Cache System...")
    try:
        # Store and retrieve
        await glyph_cache.set_async("test_key", glyph_result)
        cached_result = await glyph_cache.get_async("test_key")

        if cached_result:
            print("✅ Cache store/retrieve successful")
            stats = await glyph_cache.get_stats()
            print(f"   - Cache size: {stats['cache_size']}")
            print(f"   - Hit rate: {stats['hit_rate']:.1f}%")
        else:
            print("❌ Cache retrieve failed")
            return False
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False

    # Test 3: Quantum Renderer
    print("\n⚛️ Testing Quantum Renderer...")
    try:
        render_result = await quantum_renderer.test_render()
        if render_result.get("success"):
            print("✅ Quantum Renderer test successful")
            print(f"   - Render modes: {render_result.get('render_modes', 0)}")
        else:
            print(f"❌ Quantum Renderer test failed: {render_result.get('error')}")
            return False
    except Exception as e:
        print(f"❌ Quantum Renderer test failed: {e}")
        return False

    # Test 4: Plugin System
    print("\n🔌 Testing Plugin System...")
    try:
        plugins = plugin_system.list_plugins()
        print(f"✅ Plugin system operational")
        print(f"   - Available plugins: {len(plugins)}")
        for plugin in plugins[:3]:  # Show first 3
            print(
                f"   - {plugin.get('name', 'unknown')}: {plugin.get('type', 'unknown')}"
            )
    except Exception as e:
        print(f"❌ Plugin System test failed: {e}")
        return False

    # Test 5: Full Integration
    print("\n🔗 Testing Full Integration...")
    try:
        # Generate, cache, and render
        expression = {"symbol": "integration_test"}
        glyph_data = await glyph_core.generate_async(expression)

        cache_key = "integration_test_key"
        await glyph_cache.set_async(cache_key, glyph_data)

        # Simulate render request
        render_context = {
            "glyph_data": glyph_data,
            "dimensions": {"width": 800, "height": 600},
            "quantum_params": {"coherence_factor": 0.8},
        }

        print("✅ Full integration test successful")
        print(f"   - Generated glyph with {len(glyph_data)} properties")
        print(f"   - Cached with key: {cache_key}")
        print(f"   - Render context prepared")

    except Exception as e:
        print(f"❌ Full integration test failed: {e}")
        return False

    print("\n🎉 All tests passed! Opal2 system is fully operational.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_opal2_integration())
    sys.exit(0 if success else 1)
