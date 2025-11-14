"""
Secure Storage for Ledger Keys

Provides encrypted storage for sensitive cryptographic keys using PBKDF2HMAC
key derivation and Fernet symmetric encryption.

Anchor: T1-TIL-SEC-001
"""

import base64
import os
from pathlib import Path
from typing import Optional

# Try to import cryptography for secure key storage
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    PBKDF2HMAC = None  # type: ignore
    Fernet = None  # type: ignore


class SecureStorage:
    """
    Secure storage for cryptographic keys with encryption at rest.

    Uses PBKDF2HMAC for key derivation from a password and Fernet for
    symmetric encryption of the stored keys.

    If cryptography library is not available, falls back to plaintext storage
    with appropriate warnings.
    """

    def __init__(self, storage_path: Path, password: Optional[str] = None):
        """
        Initialize secure storage.

        Args:
            storage_path: Path to store encrypted keys
            password: Password for key derivation (if None, uses environment or generates)

        Raises:
            RuntimeError: If cryptography library is not available for encrypted storage
        """
        self.storage_path = storage_path
        self.encrypted = CRYPTOGRAPHY_AVAILABLE

        if not self.encrypted:
            raise RuntimeError(
                "Cryptography library not available. Install with: pip install cryptography"
            )

        # Get or generate password for encryption
        if password is None:
            password = os.environ.get('LEDGER_KEY_PASSWORD')
            if password is None:
                # Generate a random password and store it securely
                # In production, this should be provided by the user or a key management system
                password = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')

        self._password = password.encode('utf-8')
        self._derive_key()

    def _derive_key(self) -> None:
        """Derive encryption key from password using PBKDF2HMAC."""
        # Use a salt from file or generate new one
        salt_file = self.storage_path.parent / f"{self.storage_path.name}.salt"

        if salt_file.exists():
            salt = salt_file.read_bytes()
        else:
            salt = os.urandom(16)
            salt_file.write_bytes(salt)
            salt_file.chmod(0o600)

        # Derive key using PBKDF2HMAC
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommendation as of 2023
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(self._password))
        self._fernet = Fernet(key)

    def store_key(self, key_data: str) -> None:
        """
        Store key data with encryption.

        Args:
            key_data: Key data to store (hex string)
        """
        if not self.encrypted:
            raise RuntimeError("Cryptography library not available")

        # Encrypt the key data
        encrypted_data = self._fernet.encrypt(key_data.encode('utf-8'))

        # Write to file
        self.storage_path.write_bytes(encrypted_data)
        self.storage_path.chmod(0o600)

    def load_key(self) -> str:
        """
        Load and decrypt key data.

        Returns:
            Decrypted key data (hex string)

        Raises:
            FileNotFoundError: If key file doesn't exist
            ValueError: If decryption fails
        """
        if not self.encrypted:
            raise RuntimeError("Cryptography library not available")

        if not self.storage_path.exists():
            raise FileNotFoundError(f"Key file not found: {self.storage_path}")

        # Read encrypted data
        encrypted_data = self.storage_path.read_bytes()

        # Decrypt
        try:
            decrypted_data = self._fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Failed to decrypt key data: {e}")

    def key_exists(self) -> bool:
        """Check if encrypted key file exists."""
        return self.storage_path.exists()


def migrate_plaintext_to_encrypted(plaintext_path: Path, password: Optional[str] = None) -> None:
    """
    Migrate a plaintext key file to encrypted storage.

    Args:
        plaintext_path: Path to plaintext key file
        password: Password for encryption (optional)

    Raises:
        FileNotFoundError: If plaintext file doesn't exist
    """
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("Cryptography library not available for migration")

    if not plaintext_path.exists():
        raise FileNotFoundError(f"Plaintext key file not found: {plaintext_path}")

    # Read plaintext key
    plaintext_key = plaintext_path.read_text().strip()

    # Create encrypted storage
    encrypted_path = plaintext_path.parent / f"{plaintext_path.name}.encrypted"
    secure_storage = SecureStorage(encrypted_path, password=password)

    # Store encrypted key
    secure_storage.store_key(plaintext_key)

    # Securely delete plaintext file
    # Overwrite with random data before deletion
    plaintext_path.write_bytes(os.urandom(len(plaintext_key.encode('utf-8'))))
    plaintext_path.unlink()

    # Rename encrypted file to original name
    encrypted_path.rename(plaintext_path)
