
"""
Obsługa błędów i wyjątków w LuxDB
"""

import functools
import traceback
from typing import Callable, Any, Optional, Dict, Tuple
from .logging_utils import get_db_logger
from .error_codes import LuxDBErrorCode, get_error_info, detect_error_from_exception

class LuxDBError(Exception):
    """Bazowy wyjątek dla LuxDB"""
    def __init__(self, message: str, error_code: LuxDBErrorCode = None, 
                 context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.error_code = error_code or LuxDBErrorCode.GENERAL_ERROR
        self.context = context or {}
        self.error_info = get_error_info(self.error_code)
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Zwraca szczegółowe informacje o błędzie"""
        return {
            **self.error_info.to_dict(),
            "context": self.context,
            "traceback": traceback.format_exc()
        }

class DatabaseConnectionError(LuxDBError):
    """Błąd połączenia z bazą danych"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, LuxDBErrorCode.CONNECTION_FAILED, context)

class ModelValidationError(LuxDBError):
    """Błąd walidacji modelu"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, LuxDBErrorCode.VALIDATION_ERROR, context)

class MigrationError(LuxDBError):
    """Błąd migracji bazy danych"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, LuxDBErrorCode.MIGRATION_FAILED, context)

class QueryExecutionError(LuxDBError):
    """Błąd wykonania zapytania"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, LuxDBErrorCode.QUERY_EXECUTION_ERROR, context)

class SynchronizationError(LuxDBError):
    """Błąd synchronizacji baz danych"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, LuxDBErrorCode.SYNC_FAILED, context)

class UniqueConstraintError(LuxDBError):
    """Błąd naruszenia ograniczenia unikalności"""
    def __init__(self, message: str, constraint_name: str = None, 
                 table_name: str = None, context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context.update({
            "constraint_name": constraint_name,
            "table_name": table_name
        })
        super().__init__(message, LuxDBErrorCode.UNIQUE_CONSTRAINT_VIOLATION, error_context)

class DuplicateKeyError(LuxDBError):
    """Błąd duplikatu klucza głównego"""
    def __init__(self, message: str, key_value: Any = None, 
                 table_name: str = None, context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context.update({
            "key_value": str(key_value) if key_value else None,
            "table_name": table_name
        })
        super().__init__(message, LuxDBErrorCode.DUPLICATE_KEY, error_context)

def analyze_sqlalchemy_error(exception: Exception) -> Tuple[LuxDBErrorCode, str, Dict[str, Any]]:
    """Analizuje błąd SQLAlchemy i zwraca kod błędu, wiadomość i kontekst"""
    error_code = detect_error_from_exception(exception)
    error_info = get_error_info(error_code)
    
    context = {
        "original_exception": type(exception).__name__,
        "original_message": str(exception)
    }
    
    # Dodatkowa analiza dla specyficznych błędów
    error_message = str(exception).lower()
    
    if "unique constraint failed" in error_message:
        # Wyciągnij nazwę tabeli i kolumny
        parts = str(exception).split(":")
        if len(parts) > 1:
            constraint_info = parts[1].strip()
            context["constraint_details"] = constraint_info
            
            if "." in constraint_info:
                table_col = constraint_info.split(".")
                context["table_name"] = table_col[0]
                context["column_name"] = table_col[1] if len(table_col) > 1 else None
    
    return error_code, error_info.message, context

def handle_database_errors(operation_name: str = None, return_result: bool = False):
    """Dekorator do obsługi błędów bazodanowych
    
    Args:
        operation_name: Nazwa operacji (domyślnie nazwa funkcji)
        return_result: Jeśli True, zwraca tuple (success, result/error_info)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_db_logger()
            op_name = operation_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                if return_result:
                    return True, result
                return result
            except LuxDBError as e:
                logger.log_error(op_name, e, e.context)
                if return_result:
                    return False, e.get_detailed_info()
                raise
            except Exception as e:
                # Analizuj błąd SQLAlchemy
                error_code, message, context = analyze_sqlalchemy_error(e)
                context.update({
                    'function': func.__name__,
                    'operation': op_name
                })
                
                luxdb_error = LuxDBError(message, error_code, context)
                logger.log_error(op_name, luxdb_error, context)
                
                if return_result:
                    return False, luxdb_error.get_detailed_info()
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

def create_error_response(success: bool, data: Any = None, error_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Tworzy standardową odpowiedź z obsługą błędów"""
    response = {
        "success": success,
        "timestamp": traceback.format_exc() if not success else None
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error_info or {}
    
    return response

def safe_database_operation(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Bezpieczne wykonanie operacji bazodanowej z pełną obsługą błędów"""
    try:
        result = func(*args, **kwargs)
        return create_error_response(True, result)
    except Exception as e:
        error_code, message, context = analyze_sqlalchemy_error(e)
        error_info = get_error_info(error_code).to_dict()
        error_info.update(context)
        return create_error_response(False, error_info=error_info)

class ErrorCollector:
    """Kolektor błędów dla operacji batch"""
    
    def __init__(self):
        self.errors = []
        self.success_count = 0
        self.total_count = 0
    
    def add_error(self, error: Exception, context: Dict[str, Any] = None):
        """Dodaj błąd do kolekcji"""
        if isinstance(error, LuxDBError):
            error_data = error.get_detailed_info()
        else:
            error_code, message, error_context = analyze_sqlalchemy_error(error)
            error_context.update(context or {})
            error_data = get_error_info(error_code).to_dict()
            error_data.update(error_context)
        
        self.errors.append({
            'error_data': error_data,
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
    
    def get_error_codes_summary(self) -> Dict[str, int]:
        """Zwraca podsumowanie kodów błędów"""
        error_codes = {}
        for error in self.errors:
            code_name = error['error_data'].get('code_name', 'UNKNOWN')
            error_codes[code_name] = error_codes.get(code_name, 0) + 1
        return error_codes
