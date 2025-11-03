"""
Logging Security Utilities

Provides sanitization functions to prevent log injection attacks.

Log injection occurs when unsanitized user input is written to logs,
potentially allowing attackers to:
- Forge log entries
- Hide malicious activity
- Inject false information
- Break log parsing tools

Anchor: T1-SEC-LOG-001
"""

import re
from typing import Any, Optional


def sanitize_for_logging(value: Any, max_length: int = 200) -> str:
    """
    Sanitize a value for safe logging by removing control characters
    and newlines that could enable log injection attacks.
    
    Args:
        value: Value to sanitize (will be converted to string)
        max_length: Maximum length of sanitized output (default 200)
        
    Returns:
        Sanitized string safe for logging
        
    Example:
        >>> sanitize_for_logging("User: alice\\nAdmin action: delete")
        'User: alice Admin action: delete'
        
        >>> sanitize_for_logging("Data\\r\\nINFO: Fake log entry")
        'Data INFO: Fake log entry'
    """
    # Convert to string
    text = str(value)
    
    # Remove carriage returns and newlines (log injection vectors)
    text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Remove other control characters (ASCII 0-31 except space)
    text = ''.join(char if ord(char) >= 32 or char == ' ' else '?' for char in text)
    
    # Remove ANSI escape sequences that could manipulate terminal output
    text = re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    # Truncate to max length
    if len(text) > max_length:
        text = text[:max_length] + '...'
    
    return text


def sanitize_path_for_logging(path: Any, max_length: int = 150) -> str:
    """
    Sanitize a file path for logging, preserving path structure but
    removing control characters and limiting length.
    
    Args:
        path: File path to sanitize
        max_length: Maximum length of sanitized output (default 150)
        
    Returns:
        Sanitized path safe for logging
        
    Example:
        >>> sanitize_path_for_logging("/etc/passwd\\n/var/log/secure")
        '/etc/passwd /var/log/secure'
    """
    return sanitize_for_logging(path, max_length=max_length)


def sanitize_error_for_logging(error: Exception, max_length: int = 300) -> str:
    """
    Sanitize an exception for logging, preserving error type and message
    while removing injection vectors.
    
    Args:
        error: Exception to sanitize
        max_length: Maximum length of sanitized output (default 300)
        
    Returns:
        Sanitized error string safe for logging
        
    Example:
        >>> sanitize_error_for_logging(ValueError("Bad input\\nAdmin: user deleted"))
        'ValueError: Bad input Admin: user deleted'
    """
    # Format as "ExceptionType: message"
    error_str = f"{type(error).__name__}: {str(error)}"
    return sanitize_for_logging(error_str, max_length=max_length)


def sanitize_dict_for_logging(data: dict, max_entries: int = 10, max_value_length: int = 100) -> dict:
    """
    Sanitize a dictionary for logging by sanitizing all string values
    and limiting the number of entries.
    
    Args:
        data: Dictionary to sanitize
        max_entries: Maximum number of entries to include (default 10)
        max_value_length: Maximum length per value (default 100)
        
    Returns:
        Sanitized dictionary safe for logging
    """
    sanitized = {}
    count = 0
    
    for key, value in data.items():
        if count >= max_entries:
            sanitized['...'] = f'({len(data) - count} more entries)'
            break
        
        # Sanitize key and value
        safe_key = sanitize_for_logging(key, max_length=50)
        
        if isinstance(value, str):
            safe_value = sanitize_for_logging(value, max_length=max_value_length)
        elif isinstance(value, dict):
            safe_value = f"<dict with {len(value)} keys>"
        elif isinstance(value, (list, tuple)):
            safe_value = f"<{type(value).__name__} with {len(value)} items>"
        else:
            safe_value = sanitize_for_logging(value, max_length=max_value_length)
        
        sanitized[safe_key] = safe_value
        count += 1
    
    return sanitized


# Convenience functions for common logging patterns
def safe_str(value: Any, max_length: int = 200) -> str:
    """Alias for sanitize_for_logging - shorter for frequent use."""
    return sanitize_for_logging(value, max_length=max_length)


def safe_path(path: Any, max_length: int = 150) -> str:
    """Alias for sanitize_path_for_logging."""
    return sanitize_path_for_logging(path, max_length=max_length)


def safe_error(error: Exception, max_length: int = 300) -> str:
    """Alias for sanitize_error_for_logging."""
    return sanitize_error_for_logging(error, max_length=max_length)
