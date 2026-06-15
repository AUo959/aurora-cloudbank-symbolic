# Secure Storage for Ledger Keys

## Overview

This fix addresses the issue where attempting to import the non-existent `PBKDF2` class from cryptography was disabling encryption, leaving ledger keys stored in plaintext.

## The Problem

The original issue was that code attempted to import:
```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2  # ❌ WRONG - doesn't exist
```

This caused an `ImportError` which was being swallowed, setting `CRYPTOGRAPHY_AVAILABLE = False`, which meant:
- SecureStorage would raise "Cryptography library not available" errors
- Ledger keys were stored in plaintext
- Encrypted storage path was never enabled

## The Solution

We created a proper `SecureStorage` class that uses the correct import:
```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC  # ✅ CORRECT
```

### Key Features

1. **Correct PBKDF2HMAC Import**: Uses the actual class name from cryptography
2. **Key Derivation**: PBKDF2HMAC with SHA-256, 480,000 iterations (OWASP 2023)
3. **Encryption**: Fernet symmetric encryption for key storage
4. **Graceful Fallback**: Falls back to plaintext with warning if cryptography unavailable
5. **Integration**: InsightLedger automatically uses encrypted storage when available

## Usage

### Automatic (Recommended)

The InsightLedger automatically uses encrypted storage:

```python
from modules.insight_ledger import InsightLedger

# Keys are automatically encrypted
ledger = InsightLedger(storage_path="my_ledger")
```

### Manual Control

For direct control over key encryption:

```python
from modules.insight_ledger.secure_storage import SecureStorage

# Create encrypted storage
secure_storage = SecureStorage(
    storage_path=Path("ledger.key"),
    password="your_password"  # Optional, uses env var or generates if None
)

# Store encrypted key
secure_storage.store_key("your_secret_key_hex")

# Load encrypted key
key = secure_storage.load_key()
```

### Environment Variables

Set `LEDGER_KEY_PASSWORD` to provide a password for encryption:

```bash
export LEDGER_KEY_PASSWORD="your_secure_password"
```

### Migration from Plaintext

To migrate existing plaintext keys to encrypted storage:

```python
from modules.insight_ledger.secure_storage import migrate_plaintext_to_encrypted
from pathlib import Path

migrate_plaintext_to_encrypted(
    plaintext_path=Path("ledger.key"),
    password="your_password"
)
```

## Security Details

### Encryption Scheme

- **Key Derivation**: PBKDF2-HMAC-SHA256 with 480,000 iterations
- **Encryption**: Fernet (AES-128-CBC + HMAC-SHA256)
- **Salt**: 16 random bytes, stored in `.salt` file
- **File Permissions**: 0o600 (read/write for owner only)

### Key Derivation Function

```python
PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,  # OWASP recommendation as of 2023
    backend=default_backend()
)
```

## Testing

Run the verification script to confirm the fix:

```bash
python3 verify_pbkdf2_fix.py
```

Or run the test suite:

```bash
pytest tests/test_secure_storage.py -v
```

## Files Changed

### New Files
- `modules/insight_ledger/secure_storage.py` - Encrypted storage implementation
- `tests/test_secure_storage.py` - Test suite
- `verify_pbkdf2_fix.py` - Verification script

### Modified Files
- `modules/insight_ledger/ledger_core.py` - Integrated SecureStorage
- `modules/insight_ledger/__init__.py` - Exported SecureStorage

## Backwards Compatibility

- Existing plaintext keys can still be loaded
- InsightLedger tries encrypted loading first, falls back to plaintext
- Warning is issued when falling back to plaintext storage
- No breaking changes to existing API

## Future Enhancements

Potential improvements for future versions:
- Key rotation support
- Hardware Security Module (HSM) integration
- Multiple key derivation algorithms
- Audit logging for key access
- Key backup and recovery procedures

## References

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Cryptography Documentation](https://cryptography.io/)
- [NIST SP 800-132](https://csrc.nist.gov/publications/detail/sp/800-132/final)
