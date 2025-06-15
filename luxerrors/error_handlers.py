
"""
Uniwersalny system obsługi błędów i wyjątków
"""

import functools
import traceback
from typing import Callable, Any, Optional, Dict, Tuple, Union
from datetime import datetime
from .error_codes import LuxErrorCode, ErrorInfo, get_error_info, detect_error_from_exception

class LuxError(Exception):
    """Bazowy wyjątek dla systemu LuxErrors"""
    
    def __init__(self, 
                 message: str, 
                 error_code: LuxErrorCode = None, 
                 context: Optional[Dict[str, Any]] = None,
                 original_exception: Exception = None):
        super().__init__(message)
        self.error_code = error_code or LuxErrorCode.GENERAL_ERROR
        self.context = context or {}
        self.original_exception = original_exception
        self.error_info = get_error_info(self.error_code)
        self.timestamp = datetime.utcnow()
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Zwraca szczegółowe informacje o błędzie"""
        info = self.error_info.to_dict()
        info.update({
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "traceback": traceback.format_exc() if self.original_exception else None,
            "original_exception": {
                "type": type(self.original_exception).__name__,
                "message": str(self.original_exception)
            } if self.original_exception else None
        })
        return info
    
    def __str__(self) -> str:
        return f"[{self.error_code.name}] {self.error_info.message}: {super().__str__()}"

class ValidationError(LuxError):
    """Błąd walidacji danych"""
    def __init__(self, message: str, field_errors: Dict[str, str] = None, 
                 context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context["field_errors"] = field_errors or {}
        super().__init__(message, LuxErrorCode.VALIDATION_ERROR, error_context)

class ConnectionError(LuxError):
    """Błąd połączenia"""
    def __init__(self, message: str, service_name: str = None,
                 context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context["service_name"] = service_name
        super().__init__(message, LuxErrorCode.CONNECTION_FAILED, error_context)

class DataNotFoundError(LuxError):
    """Błąd braku danych"""
    def __init__(self, message: str, resource_type: str = None, 
                 resource_id: str = None, context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })
        super().__init__(message, LuxErrorCode.DATA_NOT_FOUND, error_context)

class DuplicateDataError(LuxError):
    """Błąd duplikatu danych"""
    def __init__(self, message: str, duplicate_field: str = None,
                 duplicate_value: Any = None, context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context.update({
            "duplicate_field": duplicate_field,
            "duplicate_value": str(duplicate_value) if duplicate_value else None
        })
        super().__init__(message, LuxErrorCode.DUPLICATE_DATA, error_context)

class OperationError(LuxError):
    """Błąd operacji"""
    def __init__(self, message: str, operation_name: str = None,
                 context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context["operation_name"] = operation_name
        super().__init__(message, LuxErrorCode.OPERATION_FAILED, error_context)

class QueryExecutionError(LuxError):
    """Błąd wykonania zapytania SQL"""
    def __init__(self, message: str, query: str = None, parameters: Dict[str, Any] = None,
                 context: Optional[Dict[str, Any]] = None):
        error_context = context or {}
        error_context.update({
            "query": query,
            "parameters": parameters
        })
        super().__init__(message, LuxErrorCode.OPERATION_FAILED, error_context)

class UnifiedErrorHandler:
    """Ujednolicony handler błędów - routing na podstawie argumentów"""
    
    @staticmethod
    def create_error(message: str, error_type: str = None, **kwargs) -> LuxError:
        """
        Tworzy odpowiedni błąd na podstawie typu i argumentów
        
        Args:
            message: Wiadomość błędu
            error_type: Typ błędu ('validation', 'connection', 'data_not_found', 'duplicate', 'operation', 'query')
            **kwargs: Dodatkowe argumenty specyficzne dla typu błędu
        """
        context = kwargs.get('context', {})
        
        if error_type == 'validation':
            return ValidationError(
                message, 
                field_errors=kwargs.get('field_errors'),
                context=context
            )
        elif error_type == 'connection':
            return ConnectionError(
                message,
                service_name=kwargs.get('service_name'),
                context=context
            )
        elif error_type == 'data_not_found':
            return DataNotFoundError(
                message,
                resource_type=kwargs.get('resource_type'),
                resource_id=kwargs.get('resource_id'),
                context=context
            )
        elif error_type == 'duplicate':
            return DuplicateDataError(
                message,
                duplicate_field=kwargs.get('duplicate_field'),
                duplicate_value=kwargs.get('duplicate_value'),
                context=context
            )
        elif error_type == 'operation':
            return OperationError(
                message,
                operation_name=kwargs.get('operation_name'),
                context=context
            )
        elif error_type == 'query':
            return QueryExecutionError(
                message,
                query=kwargs.get('query'),
                parameters=kwargs.get('parameters'),
                context=context
            )
        else:
            # Domyślny błąd ogólny
            return LuxError(message, LuxErrorCode.GENERAL_ERROR, context)
    
    @staticmethod
    def validation_error(message: str, field_errors: Dict[str, str] = None, 
                        context: Optional[Dict[str, Any]] = None) -> ValidationError:
        """Skrót do tworzenia błędu walidacji"""
        return UnifiedErrorHandler.create_error(
            message, 'validation', 
            field_errors=field_errors, 
            context=context
        )
    
    @staticmethod
    def connection_error(message: str, service_name: str = None,
                        context: Optional[Dict[str, Any]] = None) -> ConnectionError:
        """Skrót do tworzenia błędu połączenia"""
        return UnifiedErrorHandler.create_error(
            message, 'connection',
            service_name=service_name,
            context=context
        )
    
    @staticmethod
    def data_not_found_error(message: str, resource_type: str = None, 
                           resource_id: str = None, 
                           context: Optional[Dict[str, Any]] = None) -> DataNotFoundError:
        """Skrót do tworzenia błędu braku danych"""
        return UnifiedErrorHandler.create_error(
            message, 'data_not_found',
            resource_type=resource_type,
            resource_id=resource_id,
            context=context
        )
    
    @staticmethod
    def duplicate_data_error(message: str, duplicate_field: str = None,
                           duplicate_value: Any = None, 
                           context: Optional[Dict[str, Any]] = None) -> DuplicateDataError:
        """Skrót do tworzenia błędu duplikatu"""
        return UnifiedErrorHandler.create_error(
            message, 'duplicate',
            duplicate_field=duplicate_field,
            duplicate_value=duplicate_value,
            context=context
        )
    
    @staticmethod
    def operation_error(message: str, operation_name: str = None,
                       context: Optional[Dict[str, Any]] = None) -> OperationError:
        """Skrót do tworzenia błędu operacji"""
        return UnifiedErrorHandler.create_error(
            message, 'operation',
            operation_name=operation_name,
            context=context
        )
    
    @staticmethod
    def query_error(message: str, query: str = None, parameters: Dict[str, Any] = None,
                   context: Optional[Dict[str, Any]] = None) -> QueryExecutionError:
        """Skrót do tworzenia błędu zapytania"""
        return UnifiedErrorHandler.create_error(
            message, 'query',
            query=query,
            parameters=parameters,
            context=context
        )

def analyze_exception(exception: Exception) -> Tuple[LuxErrorCode, str, Dict[str, Any]]:
    """Analizuje wyjątek i zwraca kod błędu, wiadomość i kontekst"""
    error_code = detect_error_from_exception(exception)
    error_info = get_error_info(error_code)
    
    context = {
        "original_exception_type": type(exception).__name__,
        "original_message": str(exception),
        "traceback": traceback.format_exc()
    }
    
    # Dodatkowa analiza dla specyficznych błędów
    if hasattr(exception, '__dict__'):
        # Dodaj atrybuty wyjątku do kontekstu
        for attr, value in exception.__dict__.items():
            if not attr.startswith('_') and not callable(value):
                context[f"exception_{attr}"] = str(value)
    
    return error_code, error_info.message, context

def handle_errors(operation_name: str = None, 
                 return_result: bool = False,
                 reraise: bool = True,
                 logger = None):
    """Dekorator do obsługi błędów
    
    Args:
        operation_name: Nazwa operacji (domyślnie nazwa funkcji)
        return_result: Jeśli True, zwraca tuple (success, result/error_info)
        reraise: Jeśli True, ponownie rzuca błąd po zalogowaniu
        logger: Logger do zapisywania błędów
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                if return_result:
                    return True, result
                return result
            except LuxError as e:
                if logger:
                    logger.error(f"LuxError in {op_name}: {e}")
                if return_result:
                    return False, e.get_detailed_info()
                if reraise:
                    raise
                return None
            except Exception as e:
                # Analizuj nieznany błąd
                error_code, message, context = analyze_exception(e)
                context.update({
                    'function': func.__name__,
                    'operation': op_name
                })
                
                lux_error = LuxError(message, error_code, context, e)
                
                if logger:
                    logger.error(f"Error in {op_name}: {lux_error}")
                
                if return_result:
                    return False, lux_error.get_detailed_info()
                if reraise:
                    raise lux_error
                return None
        return wrapper
    return decorator

def safe_execute(func: Callable, 
                default_return: Any = None, 
                log_errors: bool = True,
                logger = None) -> Any:
    """Bezpieczne wykonanie funkcji z obsługą błędów"""
    try:
        return func()
    except Exception as e:
        if log_errors and logger:
            logger.error(f"Error in safe_execute: {e}")
        return default_return

def create_error_response(success: bool, 
                         data: Any = None, 
                         error_info: Dict[str, Any] = None) -> Dict[str, Any]:
    """Tworzy standardową odpowiedź z obsługą błędów"""
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error_info or {}
    
    return response

def safe_operation(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Bezpieczne wykonanie operacji z pełną obsługą błędów"""
    try:
        result = func(*args, **kwargs)
        return create_error_response(True, result)
    except Exception as e:
        error_code, message, context = analyze_exception(e)
        error_info = get_error_info(error_code).to_dict()
        error_info.update(context)
        return create_error_response(False, error_info=error_info)

class ErrorCollector:
    """Kolektor błędów dla operacji batch"""
    
    def __init__(self, operation_name: str = "batch_operation"):
        self.operation_name = operation_name
        self.errors = []
        self.success_count = 0
        self.total_count = 0
        self.start_time = datetime.utcnow()
    
    def add_error(self, error: Exception, context: Dict[str, Any] = None):
        """Dodaj błąd do kolekcji"""
        if isinstance(error, LuxError):
            error_data = error.get_detailed_info()
        else:
            error_code, message, error_context = analyze_exception(error)
            error_context.update(context or {})
            error_data = get_error_info(error_code).to_dict()
            error_data.update(error_context)
        
        self.errors.append({
            'error_data': error_data,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'item_index': self.total_count
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
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        return {
            'operation_name': self.operation_name,
            'total_operations': self.total_count,
            'successful_operations': self.success_count,
            'failed_operations': len(self.errors),
            'errors': self.errors,
            'success_rate': (self.success_count / self.total_count * 100) if self.total_count > 0 else 0,
            'duration_seconds': duration,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat()
        }
    
    def get_error_codes_summary(self) -> Dict[str, int]:
        """Zwraca podsumowanie kodów błędów"""
        error_codes = {}
        for error in self.errors:
            code_name = error['error_data'].get('code_name', 'UNKNOWN')
            error_codes[code_name] = error_codes.get(code_name, 0) + 1
        return error_codes
    
    def get_most_common_errors(self, limit: int = 5) -> list:
        """Zwraca najczęstsze błędy"""
        error_counts = self.get_error_codes_summary()
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:limit]

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """Walidacja wymaganych pól"""
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")
    
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {missing_fields}",
            {"missing_fields": missing_fields}
        )

def validate_data_types(data: Dict[str, Any], type_definitions: Dict[str, type]) -> None:
    """Walidacja typów danych"""
    type_errors = {}
    
    for field, expected_type in type_definitions.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                type_errors[field] = f"Expected {expected_type.__name__}, got {type(data[field]).__name__}"
    
    if type_errors:
        raise ValidationError(
            "Data type validation failed",
            type_errors
        )
