
"""
Obsługa błędów i wyjątków w LuxDB
"""

import functools
import traceback
from typing import Callable, Any, Optional, Dict
from .logging_utils import get_db_logger

class LuxDBError(Exception):
    """Bazowy wyjątek dla LuxDB"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}

class DatabaseConnectionError(LuxDBError):
    """Błąd połączenia z bazą danych"""
    pass

class ModelValidationError(LuxDBError):
    """Błąd walidacji modelu"""
    pass

class MigrationError(LuxDBError):
    """Błąd migracji bazy danych"""
    pass

class QueryExecutionError(LuxDBError):
    """Błąd wykonania zapytania"""
    pass

class SynchronizationError(LuxDBError):
    """Błąd synchronizacji baz danych"""
    pass

def handle_database_errors(operation_name: str = None):
    """Dekorator do obsługi błędów bazodanowych"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_db_logger()
            op_name = operation_name or func.__name__
            
            try:
                return func(*args, **kwargs)
            except LuxDBError as e:
                logger.log_error(op_name, e, e.context)
                raise
            except Exception as e:
                # Konwertuj inne błędy na LuxDBError
                context = {
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                }
                luxdb_error = LuxDBError(f"Unexpected error in {op_name}: {str(e)}", context)
                logger.log_error(op_name, luxdb_error, context)
                raise luxdb_error
        return wrapper
    return decorator

def safe_execute(func: Callable, default_return: Any = None, 
                log_errors: bool = True) -> Any:
    """Bezpieczne wykonanie funkcji z obsługą błędów"""
    logger = get_db_logger()
    
    try:
        return func()
    except Exception as e:
        if log_errors:
            logger.log_error(func.__name__, e)
        return default_return

def validate_db_name(db_name: str) -> None:
    """Walidacja nazwy bazy danych"""
    if not db_name or not isinstance(db_name, str):
        raise DatabaseConnectionError("Database name must be a non-empty string")
    
    if not db_name.replace('_', '').replace('-', '').isalnum():
        raise DatabaseConnectionError("Database name can only contain letters, numbers, underscores and hyphens")

def validate_model_data(data: Dict[str, Any], required_fields: list = None) -> None:
    """Walidacja danych modelu"""
    if not isinstance(data, dict):
        raise ModelValidationError("Model data must be a dictionary")
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ModelValidationError(f"Missing required fields: {missing_fields}")

class ErrorCollector:
    """Kolektor błędów dla operacji batch"""
    
    def __init__(self):
        self.errors = []
        self.success_count = 0
        self.total_count = 0
    
    def add_error(self, error: Exception, context: Dict[str, Any] = None):
        """Dodaj błąd do kolekcji"""
        self.errors.append({
            'error': error,
            'context': context or {},
            'timestamp': traceback.format_exc()
        })
    
    def add_success(self):
        """Zwiększ licznik sukcesów"""
        self.success_count += 1
    
    def increment_total(self):
        """Zwiększ licznik całkowity"""
        self.total_count += 1
    
    def has_errors(self) -> bool:
        """Sprawdź czy wystąpiły błędy"""
        return len(self.errors) > 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Pobierz podsumowanie błędów"""
        return {
            'total_operations': self.total_count,
            'successful_operations': self.success_count,
            'failed_operations': len(self.errors),
            'errors': self.errors,
            'success_rate': (self.success_count / self.total_count * 100) if self.total_count > 0 else 0
        }
