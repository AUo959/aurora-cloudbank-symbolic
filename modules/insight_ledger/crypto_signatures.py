"""
Cryptographic Signature Manager

SHA-256 hashing and HMAC signatures for ledger integrity verification.
Uses Python stdlib only (hashlib, hmac, secrets).

Anchor: T1-TIL-001
"""

import hashlib
import hmac
import json
import secrets
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class HashAlgorithm(str, Enum):
    """Supported hash algorithms."""

    SHA256 = "sha256"
    SHA512 = "sha512"


class SignatureManager:
    """
    Manages cryptographic signatures for ledger entries.

    Uses HMAC-SHA256 for entry signatures and SHA-256 for hash chains.
    Secret key should be persisted securely and loaded at initialization.
    """

    def __init__(
        self, secret_key: Optional[str] = None, hash_algorithm: HashAlgorithm = HashAlgorithm.SHA256
    ):
        """
        Initialize signature manager.

        Args:
            secret_key: HMAC secret key (hex string). If None, generates new key.
            hash_algorithm: Hash algorithm to use (default: SHA256)
        """
        self.hash_algorithm = hash_algorithm

        if secret_key is None:
            # Generate 32-byte (256-bit) random key
            self._secret_key = secrets.token_bytes(32)
        else:
            # Load existing key from hex string
            self._secret_key = bytes.fromhex(secret_key)

    @property
    def secret_key_hex(self) -> str:
        """Get secret key as hex string (for persistence)."""
        return self._secret_key.hex()

    def hash_data(self, data: Dict[str, Any]) -> str:
        """
        Create SHA-256 hash of data dictionary.

        Args:
            data: Dictionary to hash

        Returns:
            Hex-encoded hash string
        """
        # Serialize to canonical JSON (sorted keys, no whitespace)
        json_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

        if self.hash_algorithm == HashAlgorithm.SHA512:
            return hashlib.sha512(json_bytes).hexdigest()
        return hashlib.sha256(json_bytes).hexdigest()

    def sign_entry(self, entry_data: Dict[str, Any]) -> str:
        """
        Create HMAC signature for ledger entry.

        Args:
            entry_data: Entry data to sign

        Returns:
            Hex-encoded HMAC signature
        """
        # Serialize to canonical JSON
        json_bytes = json.dumps(entry_data, sort_keys=True, separators=(",", ":")).encode("utf-8")

        # Create HMAC signature
        if self.hash_algorithm == HashAlgorithm.SHA512:
            signature = hmac.new(self._secret_key, json_bytes, hashlib.sha512)
        else:
            signature = hmac.new(self._secret_key, json_bytes, hashlib.sha256)

        return signature.hexdigest()

    def verify_signature(self, entry_data: Dict[str, Any], signature: str) -> bool:
        """
        Verify HMAC signature for entry data.

        Args:
            entry_data: Entry data to verify
            signature: Expected signature (hex string)

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = self.sign_entry(entry_data)
            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False

    def hash_entry(
        self,
        entry_id: str,
        timestamp: datetime,
        content: str,
        previous_hash: Optional[str],
        signature: str,
    ) -> str:
        """
        Create hash of entry for chain linking.

        Args:
            entry_id: Entry identifier
            timestamp: Entry timestamp
            content: Entry content
            previous_hash: Hash of previous entry (None for genesis)
            signature: Entry signature

        Returns:
            Hex-encoded hash
        """
        chain_data = {
            "entry_id": entry_id,
            "timestamp": timestamp.isoformat(),
            "content": content,
            "previous_hash": previous_hash,
            "signature": signature,
        }
        return self.hash_data(chain_data)

    def verify_chain_link(
        self,
        entry_id: str,
        timestamp: datetime,
        content: str,
        previous_hash: Optional[str],
        signature: str,
        entry_hash: str,
    ) -> bool:
        """
        Verify that entry hash matches computed hash (chain integrity).

        Args:
            entry_id: Entry identifier
            timestamp: Entry timestamp
            content: Entry content
            previous_hash: Previous entry hash
            signature: Entry signature
            entry_hash: Claimed hash to verify

        Returns:
            True if hash is correct, False otherwise
        """
        computed_hash = self.hash_entry(entry_id, timestamp, content, previous_hash, signature)
        return hmac.compare_digest(computed_hash, entry_hash)


class VerificationResult:
    """Result of signature or chain verification."""

    def __init__(self, valid: bool, error_message: Optional[str] = None):
        """
        Initialize verification result.

        Args:
            valid: Whether verification passed
            error_message: Error description if verification failed
        """
        self.valid = valid
        self.error_message = error_message

    def __bool__(self) -> bool:
        """Allow using result in boolean context."""
        return self.valid

    def __repr__(self) -> str:
        """String representation."""
        if self.valid:
            return "VerificationResult(valid=True)"
        return f"VerificationResult(valid=False, error='{self.error_message}')"


def generate_secret_key() -> str:
    """
    Generate a new random secret key for HMAC signatures.

    Returns:
        Hex-encoded 256-bit secret key
    """
    return secrets.token_hex(32)


def validate_secret_key(secret_key: str) -> bool:
    """
    Validate that secret key is properly formatted.

    Args:
        secret_key: Hex-encoded secret key

    Returns:
        True if valid, False otherwise
    """
    try:
        key_bytes = bytes.fromhex(secret_key)
        return len(key_bytes) >= 16  # At least 128 bits
    except ValueError:
        return False
