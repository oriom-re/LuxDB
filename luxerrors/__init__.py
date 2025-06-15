
"""
LuxErrors - Niezależny system obsługi błędów
Wyodrębniony z LuxDB dla uniwersalnego użytku
"""

from .error_codes import (
    LuxErrorCode,
    ErrorInfo,
    get_error_info,
    detect_error_from_exception,
    ERROR_DATABASE
)

from .error_handlers import (
    LuxError,
    ErrorCollector,
    handle_errors,
    safe_execute,
    create_error_response,
    safe_operation,
    analyze_exception
)

from .logging_integration import (
    ErrorLogger,
    get_error_logger,
    log_error_event
)

__version__ = "1.0.0"
__author__ = "LuxDB Team"
__description__ = "Universal error handling system extracted from LuxDB"

__all__ = [
    # Error codes
    'LuxErrorCode',
    'ErrorInfo', 
    'get_error_info',
    'detect_error_from_exception',
    'ERROR_DATABASE',
    
    # Error handlers
    'LuxError',
    'ErrorCollector',
    'handle_errors',
    'safe_execute',
    'create_error_response',
    'safe_operation',
    'analyze_exception',
    
    # Logging
    'ErrorLogger',
    'get_error_logger',
    'log_error_event'
]
