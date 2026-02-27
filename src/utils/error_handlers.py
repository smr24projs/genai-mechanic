"""
Error Handling & Retry Logic Module
Custom exception classes and retry decorators
"""

import time
from functools import wraps
from typing import Callable, Type, Tuple
import logging

logger = logging.getLogger(__name__)


# ==========================================
# CUSTOM EXCEPTIONS
# ==========================================
class DiagnosticError(Exception):
    """Base diagnostic system exception"""
    pass


class VisionExtractionError(DiagnosticError):
    """Vision processing/image extraction failed"""
    pass


class AgentExecutionError(DiagnosticError):
    """Agent workflow execution failed"""
    pass


class DataValidationError(DiagnosticError):
    """Data validation failed"""
    pass


class APIError(DiagnosticError):
    """External API call failed"""
    pass


class DatabaseError(DiagnosticError):
    """Database operation failed"""
    pass


# ==========================================
# RETRY DECORATOR
# ==========================================
def retry_with_backoff(
    max_attempts: int = 3,
    initial_wait: float = 2.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        backoff_factor: Multiplier for wait time after each retry
        exceptions: Tuple of exception types to catch
    
    Example:
        @retry_with_backoff(max_attempts=3, exceptions=(APIError, TimeoutError))
        def api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            wait_time = initial_wait
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    logger.info(f"Attempt {attempt}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    
                    if attempt < max_attempts:
                        time.sleep(wait_time)
                        wait_time *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            raise last_exception or DiagnosticError(f"Function {func.__name__} failed after {max_attempts} attempts")
        
        return wrapper
    return decorator


# ==========================================
# ERROR HANDLERS FOR STREAMLIT
# ==========================================
def handle_streamlit_error(error: Exception, context: str = "") -> str:
    """
    Convert exceptions to user-friendly streamlit error messages
    
    Args:
        error: The exception to handle
        context: Additional context about where error occurred
    
    Returns:
        User-friendly error message
    """
    error_messages = {
        VisionExtractionError: "Image processing failed. Please ensure the image is clear and readable.",
        AgentExecutionError: "Diagnostic analysis encountered an error. Please try again or provide more details.",
        DataValidationError: "Invalid data provided. Please check sensor values are within normal ranges.",
        APIError: "External service unavailable. Please try again in a moment.",
        DatabaseError: "Database operation failed. Please try again.",
    }
    
    error_type = type(error)
    message = error_messages.get(error_type, str(error))
    
    if context:
        message = f"{context}: {message}"
    
    logger.error(f"Handled {error_type.__name__}: {message}", exc_info=True)
    return f"❌ {message}"


# ==========================================
# TIMEOUT DECORATOR
# ==========================================
def timeout_handler(seconds: int = 30):
    """
    Decorator to add timeout to functions
    Note: Works best with async functions or on Unix systems
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds}s")
                raise APIError(f"Operation timed out after {seconds} seconds")
        return wrapper
    return decorator
