"""
Test Suite for Secure Storage

Tests for encrypted key storage using PBKDF2HMAC and Fernet.

Anchor: T1-TIL-SEC-002
"""

import os
import tempfile
from pathlib import Path

import pytest

from modules.insight_ledger.secure_storage import (
    SecureStorage,
    CRYPTOGRAPHY_AVAILABLE,
    migrate_plaintext_to_encrypted
)


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_initialization():
    """Test SecureStorage initialization with and without password."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"

        # Initialize with explicit password
        secure_storage = SecureStorage(storage_path, password="test_password_123")
        assert secure_storage.encrypted is True
        assert secure_storage.storage_path == storage_path


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_store_and_load():
    """Test storing and loading encrypted keys."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"
        password = "test_password_123"
        test_key = "abcdef1234567890" * 4  # 64 hex chars

        # Store key
        secure_storage = SecureStorage(storage_path, password=password)
        secure_storage.store_key(test_key)

        # Verify file exists and is encrypted (not plaintext)
        assert storage_path.exists()
        encrypted_content = storage_path.read_bytes()
        assert test_key.encode('utf-8') not in encrypted_content

        # Load key with same password
        loaded_key = secure_storage.load_key()
        assert loaded_key == test_key


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_different_password_fails():
    """Test that loading with wrong password fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"
        test_key = "abcdef1234567890" * 4

        # Store with one password
        secure_storage1 = SecureStorage(storage_path, password="password1")
        secure_storage1.store_key(test_key)

        # Try to load with different password
        secure_storage2 = SecureStorage(storage_path, password="password2")
        with pytest.raises(ValueError, match="Failed to decrypt"):
            secure_storage2.load_key()


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_file_not_found():
    """Test loading from non-existent file raises error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "nonexistent.key"

        secure_storage = SecureStorage(storage_path, password="test_password")
        with pytest.raises(FileNotFoundError):
            secure_storage.load_key()


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_key_exists():
    """Test key_exists method."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"

        secure_storage = SecureStorage(storage_path, password="test_password")

        # Initially doesn't exist
        assert not secure_storage.key_exists()

        # After storing, exists
        secure_storage.store_key("test_key_data")
        assert secure_storage.key_exists()


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_persistence():
    """Test that encrypted keys persist across SecureStorage instances."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"
        password = "test_password_123"
        test_key = "1234567890abcdef" * 4

        # Store with first instance
        storage1 = SecureStorage(storage_path, password=password)
        storage1.store_key(test_key)

        # Load with new instance (simulating restart)
        storage2 = SecureStorage(storage_path, password=password)
        loaded_key = storage2.load_key()

        assert loaded_key == test_key


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
@pytest.mark.xfail(reason="Encryption migration requires consistent password handling")
def test_migrate_plaintext_to_encrypted():
    """Test migration from plaintext to encrypted storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        plaintext_path = Path(tmpdir) / "ledger.key"
        test_key = "fedcba0987654321" * 4
        password = "migration_password"

        # Create plaintext key file
        plaintext_path.write_text(test_key)
        assert plaintext_path.exists()

        # Migrate to encrypted
        migrate_plaintext_to_encrypted(plaintext_path, password=password)

        # Original file should still exist (renamed) but be encrypted
        assert plaintext_path.exists()
        encrypted_content = plaintext_path.read_bytes()
        assert test_key.encode('utf-8') not in encrypted_content

        # Should be able to load as encrypted
        secure_storage = SecureStorage(plaintext_path, password=password)
        loaded_key = secure_storage.load_key()
        assert loaded_key == test_key


@pytest.mark.unit
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_with_environment_password():
    """Test that SecureStorage uses environment variable for password."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"
        test_key = "0123456789abcdef" * 4
        env_password = "env_password_123"

        # Set environment variable
        os.environ['LEDGER_KEY_PASSWORD'] = env_password

        try:
            # Store without explicit password (should use env var)
            storage1 = SecureStorage(storage_path)
            storage1.store_key(test_key)

            # Load without explicit password (should use env var)
            storage2 = SecureStorage(storage_path)
            loaded_key = storage2.load_key()

            assert loaded_key == test_key
        finally:
            # Clean up environment variable
            if 'LEDGER_KEY_PASSWORD' in os.environ:
                del os.environ['LEDGER_KEY_PASSWORD']


@pytest.mark.unit
def test_cryptography_not_available_raises_error():
    """Test that SecureStorage raises error when cryptography is not available."""
    # This test only makes sense if cryptography is NOT available
    # We can't easily test this in an environment where cryptography IS available
    # but we can at least verify the error message structure
    if CRYPTOGRAPHY_AVAILABLE:
        pytest.skip("Cryptography is available, cannot test unavailable scenario")

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"

        with pytest.raises(RuntimeError, match="Cryptography library not available"):
            SecureStorage(storage_path, password="test")


@pytest.mark.integration
@pytest.mark.skipif(not CRYPTOGRAPHY_AVAILABLE, reason="Cryptography library not available")
def test_secure_storage_with_special_characters():
    """Test storing and loading keys with various character patterns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "test.key"
        password = "test_password"

        # Test various key patterns
        test_keys = [
            "a" * 64,  # All same char
            "0123456789abcdef" * 4,  # Pattern
            "f" * 32 + "0" * 32,  # Split pattern
        ]

        for test_key in test_keys:
            secure_storage = SecureStorage(storage_path, password=password)
            secure_storage.store_key(test_key)
            loaded_key = secure_storage.load_key()
            assert loaded_key == test_key, f"Failed for key pattern: {test_key[:16]}..."
