#!/usr/bin/env python3
"""
🔒 Aurora CloudBank Secure Storage Utilities

Provides secure mechanisms for storing and retrieving sensitive data,
preventing clear-text storage vulnerabilities.

T1 Anchor: T1-SEC-STORE-001
SRB Anchor: SRB-CRYPTO-STORAGE-v1.0
DLP Context: secure_storage_implementation
"""

import base64
import os
import stat
from pathlib import Path
from typing import Optional, Union

# Broken cryptography builds do not necessarily fail with ImportError
# (e.g. pyo3 Rust panic from a missing _cffi_backend), so catch BaseException
# here as modules/insight_ledger/secure_storage.py already does. Letting one of
# those escape would break importers of this module rather than degrading to
# CRYPTOGRAPHY_AVAILABLE = False.
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTOGRAPHY_AVAILABLE = True
except BaseException:  # noqa: BLE001
    CRYPTOGRAPHY_AVAILABLE = False


class SecureStorageError(Exception):
    """Exception raised for secure storage errors."""
    pass


# Length of the random per-payload salt prepended to every ciphertext.
SALT_BYTES = 16

# OWASP's current floor for PBKDF2-HMAC-SHA256. The module previously used
# 100_000, the 2018-era figure. Raising it cost nothing: the module has never
# successfully encrypted anything, so there was no stored ciphertext to re-key.
KDF_ITERATIONS = 600000


class SecureStorage:
    """
    Secure storage manager for sensitive data.
    
    Uses cryptography library for encryption when available.
    Implements defense-in-depth with file permissions and validation.
    
    Security Features:
    - AES-256 encryption via Fernet (cryptography library)
    - PBKDF2 key derivation with high iteration count
    - Restrictive file permissions (0o600)
    - Environment variable support for master keys
    - Validation of storage paths
    - Clear error messages without leaking sensitive data
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize secure storage.
        
        Args:
            master_key: Master encryption key (32 bytes).
                       If None, uses SECURE_STORAGE_KEY env var or generates new.
                       
        Raises:
            SecureStorageError: If cryptography library not available
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecureStorageError(
                "Cryptography library not available. "
                "Install with: pip install cryptography"
            )
        
        if master_key is None:
            # Try to load from environment
            env_key = os.environ.get('SECURE_STORAGE_KEY')
            if env_key:
                master_key = env_key.encode('utf-8')
            else:
                # Generate new key (should be persisted securely)
                master_key = Fernet.generate_key()
        
        if not isinstance(master_key, bytes):
            master_key = master_key.encode('utf-8')

        # Keep the master key; the cipher is derived per payload against that
        # payload's own random salt (see _cipher_for). Building a single cipher
        # in __init__ -- as this did before -- required a hardcoded salt, which
        # let one precomputation attack every Aurora installation at once.
        self._master_key = master_key

    def _cipher_for(self, salt: bytes) -> "Fernet":
        """Derive the Fernet cipher for a given salt.

        Deriving from the master key is what makes ciphertext portable across
        instances and processes. A previous version derived a key here and then
        discarded it in favour of Fernet.generate_key(), which silently made
        every instance's cipher random and unrecoverable.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=KDF_ITERATIONS,
        )
        # Fernet wants a url-safe base64-encoded 32-byte key.
        return Fernet(base64.urlsafe_b64encode(kdf.derive(self._master_key)))
    
    def encrypt_file(self, file_path: Union[str, Path], data: str) -> None:
        """
        Encrypt and write data to file securely.
        
        Args:
            file_path: Path where encrypted data will be stored
            data: Sensitive data to encrypt
            
        Raises:
            SecureStorageError: If encryption or write fails
        """
        try:
            path = Path(file_path)
            
            # Encrypt data (salt-prefixed, so any instance with the same
            # master key can read it back)
            encrypted_data = self.encrypt_string(data)
            
            # Write encrypted data
            path.write_bytes(encrypted_data)
            
            # Set restrictive permissions (owner read/write only)
            path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
            
        except Exception as e:
            raise SecureStorageError(f"Failed to encrypt file: {type(e).__name__}")
    
    def decrypt_file(self, file_path: Union[str, Path]) -> str:
        """
        Read and decrypt data from file.
        
        Args:
            file_path: Path to encrypted file
            
        Returns:
            Decrypted data as string
            
        Raises:
            SecureStorageError: If decryption or read fails
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                raise SecureStorageError(f"File not found: {path}")
            
            # Read encrypted data
            encrypted_data = path.read_bytes()
            
            # Decrypt (the salt travels in the first SALT_BYTES)
            return self.decrypt_string(encrypted_data)
            
        except SecureStorageError:
            raise
        except Exception as e:
            raise SecureStorageError(f"Failed to decrypt file: {type(e).__name__}")
    
    def encrypt_string(self, data: str) -> bytes:
        """
        Encrypt a string and return encrypted bytes.

        The returned payload is ``salt || fernet_token``. Carrying the salt
        alongside the ciphertext is what lets a fresh random salt be used per
        payload while keeping the result readable by any instance holding the
        same master key.

        Args:
            data: String to encrypt

        Returns:
            Encrypted bytes, prefixed with the salt used to derive the key
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        salt = os.urandom(SALT_BYTES)
        return salt + self._cipher_for(salt).encrypt(data)

    def decrypt_string(self, encrypted_data: bytes) -> str:
        """
        Decrypt bytes and return string.

        Args:
            encrypted_data: Encrypted bytes as produced by encrypt_string

        Returns:
            Decrypted string

        Raises:
            InvalidToken: If the payload is malformed or the key is wrong
        """
        salt, token = encrypted_data[:SALT_BYTES], encrypted_data[SALT_BYTES:]
        return self._cipher_for(salt).decrypt(token).decode('utf-8')
    
    @staticmethod
    def validate_storage_path(file_path: Union[str, Path]) -> Path:
        """
        Validate storage path for security.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            SecureStorageError: If path is invalid
        """
        path = Path(file_path)
        
        # Reject absolute paths from user input
        if path.is_absolute() and not str(path).startswith(str(Path.cwd())):
            raise SecureStorageError("Absolute paths outside working directory not allowed")
        
        # Check for parent directory references
        if '..' in path.parts:
            raise SecureStorageError("Parent directory references (..) not allowed")
        
        return path
    
    @staticmethod
    def secure_delete(file_path: Union[str, Path]) -> None:
        """
        Securely delete a file (overwrite then delete).
        
        Args:
            file_path: Path to file to delete
        """
        path = Path(file_path)
        
        if not path.exists():
            return
        
        try:
            # Overwrite with random data
            file_size = path.stat().st_size
            with path.open('wb') as f:
                f.write(os.urandom(file_size))
            
            # Delete file
            path.unlink()
            
        except Exception:
            # If secure delete fails, at least try regular delete
            path.unlink(missing_ok=True)


def get_env_key(key_name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely retrieve sensitive value from environment variable.
    
    Args:
        key_name: Name of environment variable
        default: Default value if not found
        
    Returns:
        Value from environment or default
    """
    return os.environ.get(key_name, default)


def validate_key_format(key: str, expected_length: Optional[int] = None) -> bool:
    """
    Validate cryptographic key format.
    
    Args:
        key: Key string to validate
        expected_length: Expected key length (None to skip check)
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(key, str):
        return False
    
    # Check for hex format
    try:
        bytes.fromhex(key)
    except ValueError:
        return False
    
    # Check length if specified
    if expected_length is not None:
        if len(key) != expected_length * 2:  # Hex is 2 chars per byte
            return False
    
    return True


# Convenience instance for common use cases
# In production, initialize with proper master key
_default_storage: Optional[SecureStorage] = None


def get_secure_storage() -> SecureStorage:
    """
    Get default secure storage instance.
    
    Returns:
        SecureStorage instance
        
    Raises:
        SecureStorageError: If initialization fails
    """
    global _default_storage
    
    if _default_storage is None:
        if not CRYPTOGRAPHY_AVAILABLE:
            raise SecureStorageError(
                "Cryptography library not available. "
                "Install with: pip install cryptography"
            )
        _default_storage = SecureStorage()
    
    return _default_storage
