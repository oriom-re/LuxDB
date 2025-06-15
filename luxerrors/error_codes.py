
"""
Uniwersalny system kodów błędów
Może być używany w dowolnym projekcie Python
"""

from enum import Enum
from typing import Dict, Any, Optional, Union

class LuxErrorCode(Enum):
    """Uniwersalne kody błędów"""
    
    # Błędy ogólne (1000-1999)
    GENERAL_ERROR = 1000
    UNKNOWN_ERROR = 1001
    VALIDATION_ERROR = 1002
    CONFIGURATION_ERROR = 1003
    AUTHENTICATION_ERROR = 1004
    AUTHORIZATION_ERROR = 1005
    
    # Błędy połączenia (2000-2999) 
    CONNECTION_FAILED = 2000
    SERVICE_UNAVAILABLE = 2001
    TIMEOUT_ERROR = 2002
    NETWORK_ERROR = 2003
    SSL_ERROR = 2004
    
    # Błędy danych (3000-3999)
    DATA_NOT_FOUND = 3000
    DUPLICATE_DATA = 3001
    INVALID_DATA_FORMAT = 3002
    DATA_CORRUPTION = 3003
    CONSTRAINT_VIOLATION = 3004
    DATA_TYPE_ERROR = 3005
    
    # Błędy operacji (4000-4999)
    OPERATION_FAILED = 4000
    OPERATION_TIMEOUT = 4001
    OPERATION_CANCELLED = 4002
    INVALID_OPERATION = 4003
    OPERATION_NOT_ALLOWED = 4004
    
    # Błędy systemu plików (5000-5999)
    FILE_NOT_FOUND = 5000
    FILE_ACCESS_DENIED = 5001
    FILE_ALREADY_EXISTS = 5002
    DISK_FULL = 5003
    FILE_CORRUPTION = 5004
    
    # Błędy API/HTTP (6000-6999)
    API_ERROR = 6000
    HTTP_BAD_REQUEST = 6400
    HTTP_UNAUTHORIZED = 6401
    HTTP_FORBIDDEN = 6403
    HTTP_NOT_FOUND = 6404
    HTTP_METHOD_NOT_ALLOWED = 6405
    HTTP_CONFLICT = 6409
    HTTP_UNPROCESSABLE_ENTITY = 6422
    HTTP_TOO_MANY_REQUESTS = 6429
    HTTP_INTERNAL_SERVER_ERROR = 6500
    HTTP_BAD_GATEWAY = 6502
    HTTP_SERVICE_UNAVAILABLE = 6503
    
    # Błędy external services (7000-7999)
    EXTERNAL_SERVICE_ERROR = 7000
    THIRD_PARTY_API_ERROR = 7001
    PAYMENT_PROCESSING_ERROR = 7002
    EMAIL_DELIVERY_ERROR = 7003

class ErrorSeverity(Enum):
    """Poziomy ważności błędów"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

class ErrorInfo:
    """Informacje o błędzie"""
    
    def __init__(self, 
                 code: LuxErrorCode, 
                 message: str, 
                 description: str,
                 recovery_hint: str = "", 
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 category: str = "general"):
        self.code = code
        self.message = message
        self.description = description
        self.recovery_hint = recovery_hint
        self.severity = severity
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
            "description": self.description,
            "recovery_hint": self.recovery_hint,
            "severity": self.severity.value,
            "category": self.category
        }

# Globalna baza informacji o błędach
ERROR_DATABASE: Dict[LuxErrorCode, ErrorInfo] = {
    # Błędy ogólne
    LuxErrorCode.GENERAL_ERROR: ErrorInfo(
        LuxErrorCode.GENERAL_ERROR,
        "Ogólny błąd systemu",
        "Wystąpił niespecyficzny błąd w systemie",
        "Sprawdź logi systemowe i kontekst operacji",
        ErrorSeverity.ERROR,
        "general"
    ),
    
    LuxErrorCode.UNKNOWN_ERROR: ErrorInfo(
        LuxErrorCode.UNKNOWN_ERROR,
        "Nieznany błąd",
        "Wystąpił błąd, który nie został rozpoznany przez system",
        "Zgłoś ten błąd do zespołu z pełnym kontekstem",
        ErrorSeverity.CRITICAL,
        "general"
    ),
    
    LuxErrorCode.VALIDATION_ERROR: ErrorInfo(
        LuxErrorCode.VALIDATION_ERROR,
        "Błąd walidacji danych",
        "Dane nie przeszły walidacji zgodnie z regułami",
        "Sprawdź format i typy danych według wymagań",
        ErrorSeverity.WARNING,
        "validation"
    ),
    
    LuxErrorCode.CONFIGURATION_ERROR: ErrorInfo(
        LuxErrorCode.CONFIGURATION_ERROR,
        "Błąd konfiguracji",
        "Problem z konfiguracją aplikacji lub systemu",
        "Sprawdź pliki konfiguracyjne i zmienne środowiskowe",
        ErrorSeverity.ERROR,
        "configuration"
    ),
    
    LuxErrorCode.AUTHENTICATION_ERROR: ErrorInfo(
        LuxErrorCode.AUTHENTICATION_ERROR,
        "Błąd uwierzytelniania",
        "Nieprawidłowe dane uwierzytelniające",
        "Sprawdź login, hasło lub token dostępu",
        ErrorSeverity.WARNING,
        "security"
    ),
    
    LuxErrorCode.AUTHORIZATION_ERROR: ErrorInfo(
        LuxErrorCode.AUTHORIZATION_ERROR,
        "Błąd autoryzacji",
        "Brak uprawnień do wykonania operacji",
        "Skontaktuj się z administratorem w celu uzyskania uprawnień",
        ErrorSeverity.WARNING,
        "security"
    ),
    
    # Błędy połączenia
    LuxErrorCode.CONNECTION_FAILED: ErrorInfo(
        LuxErrorCode.CONNECTION_FAILED,
        "Błąd połączenia",
        "Nie udało się nawiązać połączenia z usługą",
        "Sprawdź połączenie sieciowe i dostępność usługi",
        ErrorSeverity.ERROR,
        "connection"
    ),
    
    LuxErrorCode.SERVICE_UNAVAILABLE: ErrorInfo(
        LuxErrorCode.SERVICE_UNAVAILABLE,
        "Usługa niedostępna",
        "Usługa jest tymczasowo niedostępna",
        "Spróbuj ponownie za chwilę lub skontaktuj się z administratorem",
        ErrorSeverity.ERROR,
        "connection"
    ),
    
    LuxErrorCode.TIMEOUT_ERROR: ErrorInfo(
        LuxErrorCode.TIMEOUT_ERROR,
        "Przekroczono limit czasu",
        "Operacja trwała dłużej niż maksymalny dozwolony czas",
        "Sprawdź połączenie lub zwiększ timeout",
        ErrorSeverity.WARNING,
        "connection"
    ),
    
    LuxErrorCode.NETWORK_ERROR: ErrorInfo(
        LuxErrorCode.NETWORK_ERROR,
        "Błąd sieci",
        "Problem z połączeniem sieciowym",
        "Sprawdź połączenie internetowe i konfigurację sieci",
        ErrorSeverity.ERROR,
        "connection"
    ),
    
    # Błędy danych
    LuxErrorCode.DATA_NOT_FOUND: ErrorInfo(
        LuxErrorCode.DATA_NOT_FOUND,
        "Dane nie znalezione",
        "Żądane dane nie istnieją w systemie",
        "Sprawdź identyfikator lub kryteria wyszukiwania",
        ErrorSeverity.WARNING,
        "data"
    ),
    
    LuxErrorCode.DUPLICATE_DATA: ErrorInfo(
        LuxErrorCode.DUPLICATE_DATA,
        "Duplikat danych",
        "Dane o podanych parametrach już istnieją",
        "Użyj aktualizacji zamiast tworzenia nowych danych",
        ErrorSeverity.WARNING,
        "data"
    ),
    
    LuxErrorCode.INVALID_DATA_FORMAT: ErrorInfo(
        LuxErrorCode.INVALID_DATA_FORMAT,
        "Nieprawidłowy format danych",
        "Format danych nie odpowiada wymaganemu schematowi",
        "Sprawdź format danych według specyfikacji",
        ErrorSeverity.WARNING,
        "data"
    ),
    
    LuxErrorCode.DATA_CORRUPTION: ErrorInfo(
        LuxErrorCode.DATA_CORRUPTION,
        "Uszkodzenie danych",
        "Wykryto uszkodzenie integralności danych",
        "Przywróć dane z backup lub skontaktuj się z administratorem",
        ErrorSeverity.CRITICAL,
        "data"
    ),
    
    # Błędy operacji
    LuxErrorCode.OPERATION_FAILED: ErrorInfo(
        LuxErrorCode.OPERATION_FAILED,
        "Operacja nie powiodła się",
        "Wykonanie operacji zakończyło się błędem",
        "Sprawdź parametry operacji i spróbuj ponownie",
        ErrorSeverity.ERROR,
        "operation"
    ),
    
    LuxErrorCode.OPERATION_TIMEOUT: ErrorInfo(
        LuxErrorCode.OPERATION_TIMEOUT,
        "Przekroczono limit czasu operacji",
        "Operacja nie została ukończona w dozwolonym czasie",
        "Zwiększ timeout lub zoptymalizuj operację",
        ErrorSeverity.WARNING,
        "operation"
    ),
    
    LuxErrorCode.OPERATION_CANCELLED: ErrorInfo(
        LuxErrorCode.OPERATION_CANCELLED,
        "Operacja została anulowana",
        "Operacja została przerwana przez użytkownika lub system",
        "Spróbuj ponownie jeśli operacja jest nadal potrzebna",
        ErrorSeverity.INFO,
        "operation"
    ),
    
    # Błędy HTTP
    LuxErrorCode.HTTP_BAD_REQUEST: ErrorInfo(
        LuxErrorCode.HTTP_BAD_REQUEST,
        "Nieprawidłowe żądanie",
        "Żądanie HTTP zawiera błędy lub jest niekompletne",
        "Sprawdź składnię żądania i wymagane parametry",
        ErrorSeverity.WARNING,
        "http"
    ),
    
    LuxErrorCode.HTTP_UNAUTHORIZED: ErrorInfo(
        LuxErrorCode.HTTP_UNAUTHORIZED,
        "Brak autoryzacji",
        "Żądanie wymaga uwierzytelniania",
        "Podaj prawidłowe dane uwierzytelniające",
        ErrorSeverity.WARNING,
        "http"
    ),
    
    LuxErrorCode.HTTP_FORBIDDEN: ErrorInfo(
        LuxErrorCode.HTTP_FORBIDDEN,
        "Dostęp zabroniony",
        "Brak uprawnień do wykonania tej operacji",
        "Skontaktuj się z administratorem w celu uzyskania uprawnień",
        ErrorSeverity.WARNING,
        "http"
    ),
    
    LuxErrorCode.HTTP_NOT_FOUND: ErrorInfo(
        LuxErrorCode.HTTP_NOT_FOUND,
        "Zasób nie znaleziony",
        "Żądany zasób nie istnieje",
        "Sprawdź URL lub identyfikator zasobu",
        ErrorSeverity.WARNING,
        "http"
    ),
    
    LuxErrorCode.HTTP_INTERNAL_SERVER_ERROR: ErrorInfo(
        LuxErrorCode.HTTP_INTERNAL_SERVER_ERROR,
        "Wewnętrzny błąd serwera",
        "Wystąpił nieoczekiwany błąd po stronie serwera",
        "Spróbuj ponownie za chwilę lub skontaktuj się z administratorem",
        ErrorSeverity.CRITICAL,
        "http"
    ),
}

def get_error_info(code: LuxErrorCode) -> ErrorInfo:
    """Pobiera informacje o błędzie na podstawie kodu"""
    return ERROR_DATABASE.get(code, ERROR_DATABASE[LuxErrorCode.UNKNOWN_ERROR])

def detect_error_from_exception(exception: Exception) -> LuxErrorCode:
    """Wykrywa kod błędu na podstawie wyjątku"""
    error_message = str(exception).lower()
    exception_type = type(exception).__name__.lower()
    
    # Błędy połączenia
    if any(keyword in error_message for keyword in ['connection', 'timeout', 'network']):
        if 'timeout' in error_message:
            return LuxErrorCode.TIMEOUT_ERROR
        elif 'network' in error_message:
            return LuxErrorCode.NETWORK_ERROR
        else:
            return LuxErrorCode.CONNECTION_FAILED
    
    # Błędy danych
    if any(keyword in error_message for keyword in ['unique', 'duplicate', 'already exists']):
        return LuxErrorCode.DUPLICATE_DATA
    
    if any(keyword in error_message for keyword in ['not found', 'does not exist', 'missing']):
        return LuxErrorCode.DATA_NOT_FOUND
    
    if any(keyword in error_message for keyword in ['invalid', 'malformed', 'bad format']):
        return LuxErrorCode.INVALID_DATA_FORMAT
    
    # Błędy autoryzacji
    if any(keyword in error_message for keyword in ['unauthorized', 'authentication', 'login']):
        return LuxErrorCode.AUTHENTICATION_ERROR
    
    if any(keyword in error_message for keyword in ['forbidden', 'permission', 'access denied']):
        return LuxErrorCode.AUTHORIZATION_ERROR
    
    # Błędy walidacji
    if any(keyword in error_message for keyword in ['validation', 'constraint', 'required']):
        return LuxErrorCode.VALIDATION_ERROR
    
    # Błędy plików
    if 'filenotfounderror' in exception_type:
        return LuxErrorCode.FILE_NOT_FOUND
    
    if 'permissionerror' in exception_type:
        return LuxErrorCode.FILE_ACCESS_DENIED
    
    # HTTP błędy
    if hasattr(exception, 'status_code'):
        status_code = getattr(exception, 'status_code')
        http_errors = {
            400: LuxErrorCode.HTTP_BAD_REQUEST,
            401: LuxErrorCode.HTTP_UNAUTHORIZED,
            403: LuxErrorCode.HTTP_FORBIDDEN,
            404: LuxErrorCode.HTTP_NOT_FOUND,
            405: LuxErrorCode.HTTP_METHOD_NOT_ALLOWED,
            409: LuxErrorCode.HTTP_CONFLICT,
            422: LuxErrorCode.HTTP_UNPROCESSABLE_ENTITY,
            429: LuxErrorCode.HTTP_TOO_MANY_REQUESTS,
            500: LuxErrorCode.HTTP_INTERNAL_SERVER_ERROR,
            502: LuxErrorCode.HTTP_BAD_GATEWAY,
            503: LuxErrorCode.HTTP_SERVICE_UNAVAILABLE
        }
        return http_errors.get(status_code, LuxErrorCode.API_ERROR)
    
    # Domyślny błąd
    return LuxErrorCode.UNKNOWN_ERROR

def register_custom_error(code: LuxErrorCode, error_info: ErrorInfo):
    """Rejestruje niestandardowy błąd w bazie"""
    ERROR_DATABASE[code] = error_info

def get_errors_by_category(category: str) -> Dict[LuxErrorCode, ErrorInfo]:
    """Pobiera błędy według kategorii"""
    return {code: info for code, info in ERROR_DATABASE.items() 
            if info.category == category}

def get_errors_by_severity(severity: ErrorSeverity) -> Dict[LuxErrorCode, ErrorInfo]:
    """Pobiera błędy według poziomu ważności"""
    return {code: info for code, info in ERROR_DATABASE.items() 
            if info.severity == severity}
