#!/usr/bin/env python3
"""
Secure Logging Helper - SECURITY FIX for log injection vulnerabilities

Provides secure logging functions that prevent log injection attacks
"""

import logging
import re
from typing import Any


class SecureLogger:
    """Secure logging wrapper to prevent log injection attacks"""
    
    def __init__(self, logger_name: str):
        """Initialize secure logger with given name"""
        self.logger = logging.getLogger(logger_name)
    
    @staticmethod
    def sanitize_log_input(input_value: Any, max_length: int = 200) -> str:
        """
        Sanitize input for secure logging - prevents log injection
        
        Args:
            input_value: Value to sanitize for logging
            max_length: Maximum length of logged value
            
        Returns:
            Sanitized string safe for logging
        """
        if input_value is None:
            return "None"
            
        # Convert to string
        log_str = str(input_value)
        
        # Remove control characters that could break log format
        log_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', log_str)
        
        # Remove newlines and carriage returns to prevent log injection
        log_str = log_str.replace('\n', ' ').replace('\r', ' ')
        
        # Replace multiple spaces with single space
        log_str = re.sub(r'\s+', ' ', log_str)
        
        # Truncate to prevent log flooding
        if len(log_str) > max_length:
            log_str = log_str[:max_length] + "..."
            
        return log_str.strip()
    
    def safe_info(self, message: str, *args) -> None:
        """Safely log info message with sanitized arguments"""
        if args:
            sanitized_args = [self.sanitize_log_input(arg) for arg in args]
            self.logger.info(message, *sanitized_args)
        else:
            self.logger.info(self.sanitize_log_input(message))
    
    def safe_warning(self, message: str, *args) -> None:
        """Safely log warning message with sanitized arguments"""
        if args:
            sanitized_args = [self.sanitize_log_input(arg) for arg in args]
            self.logger.warning(message, *sanitized_args)
        else:
            self.logger.warning(self.sanitize_log_input(message))
    
    def safe_error(self, message: str, *args) -> None:
        """Safely log error message with sanitized arguments"""
        if args:
            sanitized_args = [self.sanitize_log_input(arg) for arg in args]
            self.logger.error(message, *sanitized_args)
        else:
            self.logger.error(self.sanitize_log_input(message))
    
    def safe_debug(self, message: str, *args) -> None:
        """Safely log debug message with sanitized arguments"""
        if args:
            sanitized_args = [self.sanitize_log_input(arg) for arg in args]
            self.logger.debug(message, *sanitized_args)
        else:
            self.logger.debug(self.sanitize_log_input(message))
    
    def safe_critical(self, message: str, *args) -> None:
        """Safely log critical message with sanitized arguments"""
        if args:
            sanitized_args = [self.sanitize_log_input(arg) for arg in args]
            self.logger.critical(message, *sanitized_args)
        else:
            self.logger.critical(self.sanitize_log_input(message))


def get_secure_logger(name: str) -> SecureLogger:
    """Get a secure logger instance"""
    return SecureLogger(name)


# Convenience function for backward compatibility
def sanitize_for_logging(value: Any) -> str:
    """Sanitize a value for safe logging"""
    return SecureLogger.sanitize_log_input(value)