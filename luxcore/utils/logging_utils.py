
"""
Narzędzia do standaryzowanego rejestrowania w LuxDB
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class LogLevel(Enum):
    """Poziomy logowania"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DatabaseLogger:
    """Standaryzowany logger dla operacji bazodanowych"""
    
    def __init__(self, name: str = "luxdb", level: LogLevel = LogLevel.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.value))
        
        # Usuń istniejące handlery
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Dodaj nowy handler
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def info(self, message: str):
        """Standard info logging method"""
        self.logger.info(message)
    
    def error(self, message: str):
        """Standard error logging method"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """Standard warning logging method"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """Standard debug logging method"""
        self.logger.debug(message)
    
    def log_database_operation(self, operation: str, db_name: str, 
                             success: bool, details: Optional[str] = None,
                             execution_time: Optional[float] = None):
        """Loguje operacje bazodanowe"""
        status = "SUCCESS" if success else "FAILED"
        message = f"DB Operation: {operation} on '{db_name}' - {status}"
        
        if details:
            message += f" | Details: {details}"
        
        if execution_time:
            message += f" | Time: {execution_time:.3f}s"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_query_execution(self, query_type: str, table_name: str, 
                          records_affected: int, execution_time: float):
        """Loguje wykonanie zapytań"""
        message = f"Query: {query_type} on '{table_name}' | Records: {records_affected} | Time: {execution_time:.3f}s"
        self.logger.info(message)
    
    def log_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None,
                 include_traceback: bool = True, severity_level: str = "ERROR", 
                 error_code: Optional[str] = None, user_id: Optional[str] = None,
                 session_id: Optional[str] = None, request_id: Optional[str] = None,
                 additional_tags: Optional[Dict[str, Any]] = None,
                 sanitize_sensitive_data: bool = True, max_context_length: int = 1000):
        """
        Loguje błędy z rozszerzonym kontekstem i konfiguracją
        
        Args:
            operation: Nazwa operacji podczas której wystąpił błąd
            error: Wyjątek do zalogowania
            context: Dodatkowy kontekst błędu
            include_traceback: Czy dołączyć pełny stack trace
            severity_level: Poziom ważności (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            error_code: Unikalny kod błędu dla kategoryzacji
            user_id: ID użytkownika związanego z błędem
            session_id: ID sesji podczas której wystąpił błąd
            request_id: ID żądania związanego z błędem
            additional_tags: Dodatkowe tagi dla filtrowania i kategoryzacji
            sanitize_sensitive_data: Czy usunąć potencjalnie wrażliwe dane
            max_context_length: Maksymalna długość kontekstu do logowania
        """
        # Podstawowa struktura wiadomości
        message_parts = [f"Error in {operation}: {str(error)}"]
        
        # Dodaj kod błędu jeśli podany
        if error_code:
            message_parts.append(f"Code: {error_code}")
        
        # Przetwarzanie kontekstu
        if context:
            # Sanityzacja wrażliwych danych
            processed_context = self._sanitize_context(context) if sanitize_sensitive_data else context
            
            # Skracanie zbyt długiego kontekstu
            context_str = ", ".join([f"{k}={v}" for k, v in processed_context.items()])
            if len(context_str) > max_context_length:
                context_str = context_str[:max_context_length] + "... (truncated)"
            
            message_parts.append(f"Context: {context_str}")
        
        # Dodaj identyfikatory jeśli podane
        identifiers = []
        if user_id:
            identifiers.append(f"user_id={user_id}")
        if session_id:
            identifiers.append(f"session_id={session_id}")
        if request_id:
            identifiers.append(f"request_id={request_id}")
        
        if identifiers:
            message_parts.append(f"IDs: {', '.join(identifiers)}")
        
        # Dodaj dodatkowe tagi
        if additional_tags:
            tags_str = ", ".join([f"{k}={v}" for k, v in additional_tags.items()])
            message_parts.append(f"Tags: {tags_str}")
        
        # Złóż finalną wiadomość
        final_message = " | ".join(message_parts)
        
        # Loguj zgodnie z poziomem ważności
        log_method = getattr(self.logger, severity_level.lower(), self.logger.error)
        log_method(final_message, exc_info=include_traceback)
    
    def _sanitize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Usuwa potencjalnie wrażliwe dane z kontekstu"""
        sensitive_keys = {'password', 'token', 'secret', 'key', 'auth', 'credential', 'api_key'}
        sanitized = {}
        
        for key, value in context.items():
            key_lower = str(key).lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, str) and len(value) > 100:
                # Skróć bardzo długie stringi
                sanitized[key] = value[:97] + "..."
            else:
                sanitized[key] = value
        
        return sanitized
        
    #log_info
    def log_info(self, message: str):
        """Loguje informacje"""
        self.logger.info(message)
    
    def log_migration(self, db_name: str, from_version: int, to_version: int, 
                     success: bool, execution_time: Optional[float] = None):
        """Loguje migracje"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Migration: {db_name} v{from_version} -> v{to_version} - {status}"
        
        if execution_time:
            message += f" | Time: {execution_time:.3f}s"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)
    
    def log_critical_error(self, operation: str, error: Exception, **kwargs):
        """Loguje krytyczne błędy"""
        kwargs['severity_level'] = 'CRITICAL'
        self.log_error(operation, error, **kwargs)
    
    def log_warning_error(self, operation: str, error: Exception, **kwargs):
        """Loguje błędy na poziomie ostrzeżenia"""
        kwargs['severity_level'] = 'WARNING'
        kwargs['include_traceback'] = kwargs.get('include_traceback', False)
        self.log_error(operation, error, **kwargs)
    
    def log_user_error(self, operation: str, error: Exception, user_id: str, **kwargs):
        """Loguje błędy związane z konkretnym użytkownikiem"""
        kwargs['user_id'] = user_id
        kwargs['error_code'] = kwargs.get('error_code', 'USER_ERROR')
        self.log_error(operation, error, **kwargs)
    
    def log_database_error(self, operation: str, error: Exception, db_name: str, **kwargs):
        """Loguje błędy bazodanowe z kontekstem bazy"""
        kwargs['additional_tags'] = kwargs.get('additional_tags', {})
        kwargs['additional_tags']['database'] = db_name
        kwargs['error_code'] = kwargs.get('error_code', 'DB_ERROR')
        self.log_error(operation, error, **kwargs)
    
    def log_sync(self, source_db: str, target_db: str, models: list, 
                success: bool, records_synced: int = 0):
        """Loguje synchronizację"""
        status = "SUCCESS" if success else "FAILED"
        model_names = [m.__name__ for m in models]
        message = f"Sync: {source_db} -> {target_db} | Models: {model_names} | Records: {records_synced} - {status}"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)

# Singleton instance
_db_logger = None

def get_db_logger() -> DatabaseLogger:
    """Zwraca singleton instance loggera"""
    global _db_logger
    if _db_logger is None:
        _db_logger = DatabaseLogger()
    return _db_logger
