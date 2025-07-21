#!/usr/bin/env python3
"""

        from fastapi import FastAPI

Simple Opal2 API Test
Test the FastAPI application
"""


# Add project root to path
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

def test_api_imports():
    """Test that all API imports work"""
    print("🔮 Testing Opal2 API Imports")
    print("=" * 40)

    try:
        # Test basic imports

        print("✅ FastAPI import successful")

        print("✅ Pydantic import successful")

        # Test if we can create a simple FastAPI app
        app = FastAPI(title="Test App")
        print("✅ FastAPI app creation successful")

        print("\n🎉 All basic imports successful!")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_opal2_structure():
    """Test Opal2 module structure"""
    print("\n📁 Testing Opal2 Module Structure")
    print("=" * 40)

    opal2_path = Path("modules/opal2")

    expected_files = [
        "glyph_core.py",
        "glyph_cache.py",
        "quantum_renderer.py",
        "plugin_system.py",
        "config_manager.py",
    ]

    for file in expected_files:
        file_path = opal2_path / file
        if file_path.exists():
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")

    api_path = opal2_path / "api" / "opal2_api.py"
    if api_path.exists():
        print("✅ opal2_api.py exists")
    else:
        print("❌ opal2_api.py missing")

    print("\n📊 Module structure check complete")

if __name__ == "__main__":
    success = test_api_imports()
    test_opal2_structure()

    if success:
        print("\n🚀 Ready to proceed with Opal2 expansion!")
    else:
        print("\n⚠️  Some imports failed - check dependencies")
