"""
Exception Handler Decorator for Aurora CloudBank
Systematic exception handling with proper logging and user-safe error messages

Created: 2025-11-10
Part of: Phase 1 Code Quality Sprint (Issue #320)
"""

import logging
import functools
from typing import Any, Callable, Dict
from enum import Enum
from fastapi import HTTPException


class ErrorCategory(Enum):
    """Categorized error types for consistent error handling"""
    VALIDATION = "validation"
    PROCESSING = "processing"
    INTEGRATION = "integration"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    INTERNAL = "internal"


class ErrorMessage(Enum):
    """Generic user-safe error messages"""
    INVALID_INPUT = "Invalid input provided"
    PROCESSING_ERROR = "Processing failed"
    INTEGRATION_ERROR = "External service unavailable"
    AUTH_REQUIRED = "Authentication required"
    FORBIDDEN = "Access denied"
    NOT_FOUND = "Resource not found"
    INTERNAL_ERROR = "An internal error occurred"


# Map error categories to HTTP status codes
ERROR_STATUS_CODES: Dict[ErrorCategory, int] = {
    ErrorCategory.VALIDATION: 400,
    ErrorCategory.PROCESSING: 400,
    ErrorCategory.INTEGRATION: 503,
    ErrorCategory.AUTHENTICATION: 401,
    ErrorCategory.AUTHORIZATION: 403,
    ErrorCategory.NOT_FOUND: 404,
    ErrorCategory.INTERNAL: 500,
}

# Map error categories to error messages
ERROR_MESSAGES: Dict[ErrorCategory, str] = {
    ErrorCategory.VALIDATION: ErrorMessage.INVALID_INPUT.value,
    ErrorCategory.PROCESSING: ErrorMessage.PROCESSING_ERROR.value,
    ErrorCategory.INTEGRATION: ErrorMessage.INTEGRATION_ERROR.value,
    ErrorCategory.AUTHENTICATION: ErrorMessage.AUTH_REQUIRED.value,
    ErrorCategory.AUTHORIZATION: ErrorMessage.FORBIDDEN.value,
    ErrorCategory.NOT_FOUND: ErrorMessage.NOT_FOUND.value,
    ErrorCategory.INTERNAL: ErrorMessage.INTERNAL_ERROR.value,
}


def handle_exceptions(
    error_category: ErrorCategory = ErrorCategory.INTERNAL,
    log_level: int = logging.ERROR,
    include_context: bool = True
) -> Callable:
    """
    Decorator for systematic exception handling with proper logging.
    
    Replaces generic 'except Exception as e' patterns with:
    - Specific exception type catching
    - Proper structured logging
    - User-safe error messages
    - Context preservation for debugging
    
    Args:
        error_category: Category of error for this endpoint
        log_level: Logging level for exceptions
        include_context: Whether to include request context in logs
    
    Returns:
        Decorated function with exception handling
    
    Example:
        @handle_exceptions(error_category=ErrorCategory.VALIDATION)
        async def process_data(data: dict):
            # Your code here
            return result
    """
    def decorator(func: Callable) -> Callable:
        logger = logging.getLogger(func.__module__)
        
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            
            except HTTPException:
                # Re-raise HTTP exceptions (already handled)
                raise
            
            except ValueError as e:
                # Validation errors
                logger.warning(
                    f"Validation error in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "ValueError",
                        "error_category": ErrorCategory.VALIDATION.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.VALIDATION],
                    detail=ERROR_MESSAGES[ErrorCategory.VALIDATION]
                )
            
            except KeyError as e:
                # Missing required data
                logger.warning(
                    f"Missing data in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "KeyError",
                        "missing_key": str(e)
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.VALIDATION],
                    detail=ERROR_MESSAGES[ErrorCategory.VALIDATION]
                )
            
            except ConnectionError as e:
                # External service errors
                logger.error(
                    f"Integration error in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "ConnectionError",
                        "error_category": ErrorCategory.INTEGRATION.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.INTEGRATION],
                    detail=ERROR_MESSAGES[ErrorCategory.INTEGRATION]
                )
            
            except Exception as e:
                # Catch-all for unexpected errors
                logger.log(
                    log_level,
                    f"Unexpected error in {func.__name__}: {type(e).__name__}",
                    exc_info=True,  # Always include full trace for unexpected errors
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_category": error_category.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[error_category],
                    detail=ERROR_MESSAGES[error_category]
                )
        
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            
            except HTTPException:
                # Re-raise HTTP exceptions (already handled)
                raise
            
            except ValueError as e:
                # Validation errors
                logger.warning(
                    f"Validation error in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "ValueError",
                        "error_category": ErrorCategory.VALIDATION.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.VALIDATION],
                    detail=ERROR_MESSAGES[ErrorCategory.VALIDATION]
                )
            
            except KeyError as e:
                # Missing required data
                logger.warning(
                    f"Missing data in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "KeyError",
                        "missing_key": str(e)
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.VALIDATION],
                    detail=ERROR_MESSAGES[ErrorCategory.VALIDATION]
                )
            
            except ConnectionError as e:
                # External service errors
                logger.error(
                    f"Integration error in {func.__name__}: {e}",
                    exc_info=include_context,
                    extra={
                        "function": func.__name__,
                        "error_type": "ConnectionError",
                        "error_category": ErrorCategory.INTEGRATION.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[ErrorCategory.INTEGRATION],
                    detail=ERROR_MESSAGES[ErrorCategory.INTEGRATION]
                )
            
            except Exception as e:
                # Catch-all for unexpected errors
                logger.log(
                    log_level,
                    f"Unexpected error in {func.__name__}: {type(e).__name__}",
                    exc_info=True,  # Always include full trace for unexpected errors
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_category": error_category.value
                    }
                )
                raise HTTPException(
                    status_code=ERROR_STATUS_CODES[error_category],
                    detail=ERROR_MESSAGES[error_category]
                )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Convenience decorators for common error categories
validation_handler = functools.partial(handle_exceptions, error_category=ErrorCategory.VALIDATION)
processing_handler = functools.partial(handle_exceptions, error_category=ErrorCategory.PROCESSING)
integration_handler = functools.partial(handle_exceptions, error_category=ErrorCategory.INTEGRATION)
auth_handler = functools.partial(handle_exceptions, error_category=ErrorCategory.AUTHENTICATION)
