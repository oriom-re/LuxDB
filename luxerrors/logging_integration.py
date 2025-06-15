"""
Integracja z systemem logowania dla LuxErrors
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from .error_codes import LuxErrorCode, ErrorInfo, get_error_info

class ErrorLogger:
    """Logger specjalizujący się w błędach LuxErrors"""

    def __init__(self, logger_name: str = "luxerrors", level: int = logging.INFO):
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(level)

        # Dodaj handler jeśli nie ma żadnego
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_error(self, error_code: LuxErrorCode, message: str, 
                  context: Optional[Dict[str, Any]] = None):
        """Loguje błąd z kodem"""
        error_info = get_error_info(error_code)

        log_data = {
            'error_code': error_code.value,
            'error_name': error_code.name,
            'message': message,
            'severity': error_info.severity.value,
            'category': error_info.category,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat()
        }

        log_message = f"[{error_code.name}] {message}"
        if context:
            log_message += f" | Context: {json.dumps(context)}"

        # Wybierz poziom logowania na podstawie severity
        if error_info.severity.value == "CRITICAL":
            self.logger.critical(log_message, extra=log_data)
        elif error_info.severity.value == "ERROR":
            self.logger.error(log_message, extra=log_data)
        elif error_info.severity.value == "WARNING":
            self.logger.warning(log_message, extra=log_data)
        elif error_info.severity.value == "INFO":
            self.logger.info(log_message, extra=log_data)
        else:
            self.logger.debug(log_message, extra=log_data)

    def log_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Loguje wyjątek z automatyczną detekcją kodu błędu"""
        from .error_handlers import analyze_exception

        error_code, message, error_context = analyze_exception(exception)
        if context:
            error_context.update(context)

        self.log_error(error_code, message, error_context)

# Globalna instancja logger
_global_logger = None

def get_error_logger(logger_name: str = "luxerrors") -> ErrorLogger:
    """Pobiera globalną instancję error logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ErrorLogger(logger_name)
    return _global_logger

def log_error_event(error_code: LuxErrorCode, message: str, 
                   context: Optional[Dict[str, Any]] = None):
    """Szybki sposób na zalogowanie błędu"""
    logger = get_error_logger()
    logger.log_error(error_code, message, context)