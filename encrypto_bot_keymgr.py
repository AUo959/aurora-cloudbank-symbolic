"""Utility stubs for encryption key management used in testing."""

def generate_key() -> bytes:
    """Return a predictable dummy key for tests."""
    return b"0" * 32

def store_key(key: bytes) -> None:
    """Placeholder for secure key storage logic."""
    # In production this would write to a secure location or KMS.
    _ = key
