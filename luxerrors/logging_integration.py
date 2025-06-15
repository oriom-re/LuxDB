
"""
Integracja systemu błędów z logowaniem
"""

import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
from .error_codes import LuxErrorCode, ErrorSeverity
from .error_handlers import LuxError

class ErrorLogger:
    """Logger specjalizowany w obsłudze błędów"""
    
    def __init__(self, name: str = "luxerrors", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Konfiguracja formattera
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_error(self, error: LuxError, context: Dict[str, Any] = None):
        """Loguje błąd LuxError"""
        error_info = error.get_detailed_info()
        if context:
            error_info.update(context)
        
        # Wybierz poziom logowania na podstawie severity
        log_level = self._get_log_level(error.error_info.severity)
        
        message = f"[{error.error_code.name}] {error.error_info.message}"
        extra = {
            "error_code": error.error_code.value,
            "error_details": error_info,
            "context": context or {}
        }
        
        self.logger.log(log_level, message, extra=extra)
    
    def log_exception(self, exception: Exception, operation: str = None, 
                     context: Dict[str, Any] = None):
        """Loguje dowolny wyjątek"""
        from .error_handlers import analyze_exception
        
        error_code, message, error_context = analyze_exception(exception)
        error_context.update(context or {})
        
        if operation:
            error_context["operation"] = operation
        
        lux_error = LuxError(message, error_code, error_context, exception)
        self.log_error(lux_error, context)
    
    def log_operation_success(self, operation: str, duration: float = None,
                            context: Dict[str, Any] = None):
        """Loguje sukces operacji"""
        message = f"Operation '{operation}' completed successfully"
        if duration:
            message += f" in {duration:.3f}s"
        
        extra = {
            "operation": operation,
            "status": "success",
            "duration": duration,
            "context": context or {}
        }
        
        self.logger.info(message, extra=extra)
    
    def log_operation_start(self, operation: str, context: Dict[str, Any] = None):
        """Loguje rozpoczęcie operacji"""
        message = f"Starting operation: {operation}"
        extra = {
            "operation": operation,
            "status": "started",
            "context": context or {}
        }
        
        self.logger.info(message, extra=extra)
    
    def log_validation_error(self, field_errors: Dict[str, str], 
                           context: Dict[str, Any] = None):
        """Loguje błędy walidacji"""
        message = f"Validation failed for fields: {list(field_errors.keys())}"
        extra = {
            "error_type": "validation",
            "field_errors": field_errors,
            "context": context or {}
        }
        
        self.logger.warning(message, extra=extra)
    
    def log_performance_warning(self, operation: str, duration: float,
                              threshold: float, context: Dict[str, Any] = None):
        """Loguje ostrzeżenie o wydajności"""
        message = f"Performance warning: {operation} took {duration:.3f}s (threshold: {threshold:.3f}s)"
        extra = {
            "operation": operation,
            "duration": duration,
            "threshold": threshold,
            "performance_ratio": duration / threshold,
            "context": context or {}
        }
        
        self.logger.warning(message, extra=extra)
    
    def _get_log_level(self, severity: ErrorSeverity) -> int:
        """Mapuje severity na poziom logowania"""
        mapping = {
            ErrorSeverity.CRITICAL: logging.CRITICAL,
            ErrorSeverity.ERROR: logging.ERROR,
            ErrorSeverity.WARNING: logging.WARNING,
            ErrorSeverity.INFO: logging.INFO,
            ErrorSeverity.DEBUG: logging.DEBUG
        }
        return mapping.get(severity, logging.ERROR)

class StructuredErrorLogger(ErrorLogger):
    """Logger z strukturalnym formatowaniem JSON"""
    
    def __init__(self, name: str = "luxerrors_structured", level: int = logging.INFO):
        super().__init__(name, level)
        
        # Zastąp formatter na JSON
        if self.logger.handlers:
            for handler in self.logger.handlers:
                handler.setFormatter(self._create_json_formatter())
    
    def _create_json_formatter(self):
        """Tworzy JSON formatter"""
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno
                }
                
                # Dodaj dodatkowe dane jeśli są dostępne
                if hasattr(record, 'error_code'):
                    log_data["error_code"] = record.error_code
                
                if hasattr(record, 'error_details'):
                    log_data["error_details"] = record.error_details
                
                if hasattr(record, 'context'):
                    log_data["context"] = record.context
                
                if hasattr(record, 'operation'):
                    log_data["operation"] = record.operation
                
                if hasattr(record, 'duration'):
                    log_data["duration"] = record.duration
                
                return json.dumps(log_data, ensure_ascii=False)
        
        return JsonFormatter()

# Globalne instancje loggerów
_error_logger = None
_structured_logger = None

def get_error_logger() -> ErrorLogger:
    """Pobiera globalną instancję error loggera"""
    global _error_logger
    if _error_logger is None:
        _error_logger = ErrorLogger()
    return _error_logger

def get_structured_logger() -> StructuredErrorLogger:
    """Pobiera globalną instancję structured loggera"""
    global _structured_logger
    if _structured_logger is None:
        _structured_logger = StructuredErrorLogger()
    return _structured_logger

def log_error_event(error: Exception, operation: str = None, 
                   context: Dict[str, Any] = None, structured: bool = False):
    """Funkcja convenience do logowania błędów"""
    logger = get_structured_logger() if structured else get_error_logger()
    
    if isinstance(error, LuxError):
        logger.log_error(error, context)
    else:
        logger.log_exception(error, operation, context)

def setup_error_logging(level: int = logging.INFO, 
                       structured: bool = False,
                       log_file: str = None):
    """Konfiguruje system logowania błędów"""
    logger_class = StructuredErrorLogger if structured else ErrorLogger
    logger = logger_class(level=level)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        formatter = logger._create_json_formatter() if structured else logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.logger.addHandler(file_handler)
    
    return logger
