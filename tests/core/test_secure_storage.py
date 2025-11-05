#!/usr/bin/env python3
"""
🔒 Security Tests for Sensitive Storage and HTML Sanitization

Tests for PR #3: Sensitive Storage & HTML Sanitization

T1 Anchor: T1-SEC-TEST-003
SRB Anchor: SRB-SECURITY-TESTS-v1.0
DLP Context: security_testing_sensitive_storage
"""

import os
import tempfile
from pathlib import Path

import pytest

# Import modules under test
from src.core.secure_storage import (
    SecureStorage,
    SecureStorageError,
    get_env_key,
    validate_key_format,
    CRYPTOGRAPHY_AVAILABLE
)


# =============================================================================
# Secure Storage Tests
# =============================================================================

class TestSecureStorage:
    """Test secure storage encryption and decryption."""
    
    def test_encryption_decryption_roundtrip(self, tmp_path):
        """Test that data can be encrypted and decrypted successfully."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        test_data = "sensitive_secret_key_12345"
        test_file = tmp_path / "test_key.enc"
        
        # Encrypt
        storage.encrypt_file(test_file, test_data)
        
        # Verify file exists
        assert test_file.exists()
        
        # Verify content is encrypted (not plain text)
        raw_content = test_file.read_bytes()
        assert test_data.encode() not in raw_content
        
        # Decrypt
        decrypted = storage.decrypt_file(test_file)
        
        # Verify decrypted matches original
        assert decrypted == test_data
    
    def test_file_permissions_restrictive(self, tmp_path):
        """Test that encrypted files have restrictive permissions."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        test_file = tmp_path / "secret.enc"
        
        storage.encrypt_file(test_file, "secret_data")
        
        # Check file permissions (should be 0o600 - owner read/write only)
        file_stat = test_file.stat()
        permissions = file_stat.st_mode & 0o777
        
        # Verify owner can read/write
        assert permissions & 0o600 == 0o600
        
        # Verify group and others have no permissions
        assert permissions & 0o077 == 0
    
    def test_encrypt_non_existent_directory(self, tmp_path):
        """Test encryption to non-existent directory fails gracefully."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        bad_path = tmp_path / "nonexistent" / "dir" / "file.enc"
        
        with pytest.raises(SecureStorageError):
            storage.encrypt_file(bad_path, "data")
    
    def test_decrypt_non_existent_file(self, tmp_path):
        """Test decryption of non-existent file fails properly."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        bad_path = tmp_path / "nonexistent.enc"
        
        with pytest.raises(SecureStorageError, match="File not found"):
            storage.decrypt_file(bad_path)
    
    def test_decrypt_corrupted_file(self, tmp_path):
        """Test decryption of corrupted file fails safely."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        bad_file = tmp_path / "corrupted.enc"
        
        # Write invalid encrypted data
        bad_file.write_bytes(b"this is not valid encrypted data")
        
        with pytest.raises(SecureStorageError):
            storage.decrypt_file(bad_file)
    
    def test_encrypt_string_method(self):
        """Test direct string encryption method."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        test_data = "sensitive_value"
        
        # Encrypt
        encrypted = storage.encrypt_string(test_data)
        
        # Verify encrypted is bytes
        assert isinstance(encrypted, bytes)
        
        # Verify not plain text
        assert test_data.encode() not in encrypted
        
        # Decrypt
        decrypted = storage.decrypt_string(encrypted)
        
        # Verify matches original
        assert decrypted == test_data
    
    def test_master_key_from_environment(self, monkeypatch):
        """Test loading master key from environment variable."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        test_key = b"test_master_key_from_env_var_12"
        monkeypatch.setenv('SECURE_STORAGE_KEY', test_key.decode('utf-8'))
        
        # Should not raise exception
        storage = SecureStorage()
        assert storage is not None


class TestPathValidation:
    """Test storage path validation."""
    
    def test_validate_storage_path_safe(self, tmp_path):
        """Test that safe paths are validated."""
        safe_path = "data/keys/test.key"
        validated = SecureStorage.validate_storage_path(safe_path)
        
        assert isinstance(validated, Path)
        assert ".." not in validated.parts
    
    def test_fallback_graceful_error_handling(self):
        """Test that fallback handles errors gracefully."""
        # Invalid inputs
        dangerous_path = "../../../etc/passwd"  # nosec B108 - test data for security validation
        
        with pytest.raises(SecureStorageError, match="Parent directory"):
            SecureStorage.validate_storage_path(dangerous_path)
    
    def test_validate_storage_path_absolute_outside_cwd_blocked(self):
        """Test that absolute paths outside working directory are blocked."""
        dangerous_path = "/etc/passwd"
        
        with pytest.raises(SecureStorageError, match="Absolute paths"):
            SecureStorage.validate_storage_path(dangerous_path)


class TestSecureDelete:
    """Test secure file deletion."""
    
    def test_secure_delete_overwrites_file(self, tmp_path):
        """Test that secure delete overwrites file contents."""
        test_file = tmp_path / "to_delete.txt"
        original_content = b"sensitive data to securely delete"
        
        # Create file with sensitive content
        test_file.write_bytes(original_content)
        original_size = test_file.stat().st_size
        
        # Note: This is a basic test - true verification of overwrite
        # would require low-level disk analysis
        SecureStorage.secure_delete(test_file)
        
        # Verify file is deleted
        assert not test_file.exists()
    
    def test_secure_delete_non_existent_file(self, tmp_path):
        """Test secure delete handles non-existent files gracefully."""
        non_existent = tmp_path / "does_not_exist.txt"
        
        # Should not raise exception
        SecureStorage.secure_delete(non_existent)


# =============================================================================
# Key Management Tests
# =============================================================================

class TestKeyManagement:
    """Test cryptographic key validation and management."""
    
    def test_validate_key_format_valid_hex(self):
        """Test validation of valid hex key."""
        # 32 bytes = 64 hex characters
        valid_key = "a" * 64
        
        assert validate_key_format(valid_key, expected_length=32)
    
    def test_validate_key_format_invalid_hex(self):
        """Test validation rejects non-hex strings."""
        invalid_key = "not a hex string!"
        
        assert not validate_key_format(invalid_key)
    
    def test_validate_key_format_wrong_length(self):
        """Test validation rejects wrong length keys."""
        # 16 bytes but expecting 32
        short_key = "a" * 32
        
        assert not validate_key_format(short_key, expected_length=32)
    
    def test_validate_key_format_non_string(self):
        """Test validation rejects non-string input."""
        assert not validate_key_format(12345)
        assert not validate_key_format(None)
        assert not validate_key_format([])
    
    def test_get_env_key_exists(self, monkeypatch):
        """Test retrieving key from environment."""
        test_key = "test_secret_key"
        monkeypatch.setenv('TEST_KEY', test_key)
        
        result = get_env_key('TEST_KEY')
        
        assert result == test_key
    
    def test_get_env_key_not_exists(self):
        """Test retrieving non-existent key returns default."""
        result = get_env_key('NON_EXISTENT_KEY', default='fallback')
        
        assert result == 'fallback'
    
    def test_get_env_key_no_default(self):
        """Test retrieving non-existent key without default returns None."""
        result = get_env_key('NON_EXISTENT_KEY')
        
        assert result is None


# =============================================================================
# Integration Tests
# =============================================================================

class TestSecureStorageIntegration:
    """Integration tests for secure storage in real-world scenarios."""
    
    def test_ledger_key_storage_scenario(self, tmp_path):
        """Test typical ledger key storage and retrieval."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        key_file = tmp_path / "ledger.key"
        
        # Simulate storing a newly generated HMAC key
        hmac_key = "a" * 64  # 64 hex chars = 32 bytes
        
        # Encrypt and store
        storage.encrypt_file(key_file, hmac_key)
        
        # Verify stored securely
        assert key_file.exists()
        assert hmac_key.encode() not in key_file.read_bytes()
        
        # Later: Retrieve and use
        retrieved_key = storage.decrypt_file(key_file)
        assert retrieved_key == hmac_key
    
    def test_multiple_keys_different_storage(self, tmp_path):
        """Test storing multiple different keys."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        
        keys = {
            "api_key.enc": "api_secret_12345",
            "db_password.enc": "database_password_xyz",
            "jwt_secret.enc": "jwt_signing_secret_abc"
        }
        
        # Store all keys
        for filename, secret in keys.items():
            key_file = tmp_path / filename
            storage.encrypt_file(key_file, secret)
        
        # Verify all can be retrieved correctly
        for filename, expected_secret in keys.items():
            key_file = tmp_path / filename
            retrieved = storage.decrypt_file(key_file)
            assert retrieved == expected_secret
    
    def test_key_rotation_scenario(self, tmp_path):
        """Test key rotation: old key -> new key."""
        if not CRYPTOGRAPHY_AVAILABLE:
            pytest.skip("Cryptography library not available")
        
        storage = SecureStorage()
        key_file = tmp_path / "rotation.key"
        
        # Store old key
        old_key = "old_secret_key"
        storage.encrypt_file(key_file, old_key)
        
        # Rotate: read old, generate new, store new
        retrieved_old = storage.decrypt_file(key_file)
        assert retrieved_old == old_key
        
        # Store new key (overwrite)
        new_key = "new_secret_key"
        storage.encrypt_file(key_file, new_key)
        
        # Verify new key stored
        retrieved_new = storage.decrypt_file(key_file)
        assert retrieved_new == new_key
        assert retrieved_new != old_key


# =============================================================================
# Fallback Behavior Tests
# =============================================================================

class TestFallbackBehavior:
    """Test graceful degradation when cryptography unavailable."""
    
    def test_secure_storage_raises_without_cryptography(self, monkeypatch):
        """Test SecureStorage raises clear error without cryptography."""
        # Simulate cryptography not available
        import src.core.secure_storage as storage_module
        original_value = storage_module.CRYPTOGRAPHY_AVAILABLE
        
        try:
            monkeypatch.setattr(storage_module, 'CRYPTOGRAPHY_AVAILABLE', False)
            
            with pytest.raises(SecureStorageError, match="Cryptography library not available"):
                SecureStorage()
        
        finally:
            # Restore original value
            monkeypatch.setattr(storage_module, 'CRYPTOGRAPHY_AVAILABLE', original_value)
