"""
Demonstration that PBKDF2HMAC import issue is fixed.

This script verifies that:
1. The correct PBKDF2HMAC class is imported (not PBKDF2 which doesn't exist)
2. CRYPTOGRAPHY_AVAILABLE is True when cryptography is installed
3. Ledger keys are encrypted, not stored in plaintext
"""

import sys
import tempfile
from pathlib import Path


def main():
    print("=" * 70)
    print("PBKDF2 Import Issue Fix Verification")
    print("=" * 70)

    # Test 1: Verify incorrect import fails
    print("\n1. Verifying incorrect PBKDF2 import fails...")
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
        print("   ❌ PBKDF2 should not exist (this is the bug)")
        return False
    except ImportError:
        print("   ✅ PBKDF2 correctly does not exist")

    # Test 2: Verify correct import works
    print("\n2. Verifying correct PBKDF2HMAC import works...")
    try:
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        print("   ✅ PBKDF2HMAC imported successfully")
    except ImportError as e:
        print(f"   ❌ PBKDF2HMAC import failed: {e}")
        return False

    # Test 3: Verify SecureStorage uses correct import
    print("\n3. Verifying SecureStorage uses PBKDF2HMAC...")
    try:
        # Load module directly without importing dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "secure_storage",
            "modules/insight_ledger/secure_storage.py"
        )
        secure_storage_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(secure_storage_module)

        SecureStorage = secure_storage_module.SecureStorage
        CRYPTOGRAPHY_AVAILABLE = secure_storage_module.CRYPTOGRAPHY_AVAILABLE

        if not CRYPTOGRAPHY_AVAILABLE:
            print("   ❌ CRYPTOGRAPHY_AVAILABLE is False (incorrect import)")
            return False
        print("   ✅ CRYPTOGRAPHY_AVAILABLE is True (correct import)")
    except ImportError as e:
        print(f"   ❌ SecureStorage import failed: {e}")
        return False

    # Test 4: Verify encryption actually works
    print("\n4. Verifying ledger keys are encrypted, not plaintext...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "ledger.key"
            test_key = "secret_key_" + "a" * 50

            # Store key
            secure_storage = SecureStorage(storage_path, password="test_pass")
            secure_storage.store_key(test_key)

            # Verify file is encrypted
            encrypted_content = storage_path.read_bytes()
            if test_key.encode('utf-8') in encrypted_content:
                print("   ❌ Key is stored in plaintext (encryption failed)")
                return False
            print("   ✅ Key is encrypted on disk")

            # Verify we can decrypt it
            loaded_key = secure_storage.load_key()
            if loaded_key != test_key:
                print("   ❌ Decrypted key doesn't match original")
                return False
            print("   ✅ Key can be decrypted correctly")
    except Exception as e:
        print(f"   ❌ Encryption test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5: Verify InsightLedger integration
    print("\n5. Verifying InsightLedger uses encrypted storage...")
    try:
        # Check that ledger_core imports SecureStorage
        with open('modules/insight_ledger/ledger_core.py', 'r') as f:
            ledger_code = f.read()

        if 'from .secure_storage import SecureStorage' not in ledger_code:
            print("   ❌ InsightLedger doesn't import SecureStorage")
            return False
        print("   ✅ InsightLedger imports SecureStorage")

        if '_store_key_securely' not in ledger_code:
            print("   ❌ InsightLedger doesn't have secure storage methods")
            return False
        print("   ✅ InsightLedger has secure key storage methods")

    except Exception as e:
        print(f"   ❌ Integration check failed: {e}")
        return False

    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\nSummary:")
    print("  • PBKDF2HMAC is correctly imported (not PBKDF2)")
    print("  • CRYPTOGRAPHY_AVAILABLE is True when library is installed")
    print("  • Ledger keys are encrypted at rest, not stored in plaintext")
    print("  • InsightLedger integrates with SecureStorage for key encryption")
    print("\nThe issue is FIXED! ✅")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
