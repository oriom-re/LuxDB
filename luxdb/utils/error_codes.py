
"""
System kodów błędów LuxDB z globalną bazą informacyjną
"""

from enum import Enum
from typing import Dict, Any, Optional

class LuxDBErrorCode(Enum):
    """Kody błędów LuxDB"""
    
    # Błędy ogólne (1000-1999)
    GENERAL_ERROR = 1000
    UNKNOWN_ERROR = 1001
    VALIDATION_ERROR = 1002
    
    # Błędy połączenia (2000-2999) 
    CONNECTION_FAILED = 2000
    DATABASE_NOT_FOUND = 2001
    POOL_EXHAUSTED = 2002
    TIMEOUT_ERROR = 2003
    
    # Błędy danych (3000-3999)
    DUPLICATE_KEY = 3000
    UNIQUE_CONSTRAINT_VIOLATION = 3001
    FOREIGN_KEY_VIOLATION = 3002
    NULL_CONSTRAINT_VIOLATION = 3003
    CHECK_CONSTRAINT_VIOLATION = 3004
    DATA_TYPE_ERROR = 3005
    
    # Błędy zapytań (4000-4999)
    QUERY_SYNTAX_ERROR = 4000
    QUERY_EXECUTION_ERROR = 4001
    QUERY_TIMEOUT = 4002
    INVALID_QUERY_PARAMS = 4003
    
    # Błędy migracji (5000-5999)
    MIGRATION_FAILED = 5000
    MIGRATION_ROLLBACK_FAILED = 5001
    SCHEMA_CONFLICT = 5002
    VERSION_CONFLICT = 5003
    
    # Błędy synchronizacji (6000-6999)
    SYNC_FAILED = 6000
    SOURCE_DB_ERROR = 6001
    TARGET_DB_ERROR = 6002
    DATA_INCONSISTENCY = 6003

class ErrorInfo:
    """Informacje o błędzie"""
    
    def __init__(self, code: LuxDBErrorCode, message: str, description: str, 
                 recovery_hint: str = "", severity: str = "ERROR"):
        self.code = code
        self.message = message
        self.description = description
        self.recovery_hint = recovery_hint
        self.severity = severity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "code_name": self.code.name,
            "message": self.message,
            "description": self.description,
            "recovery_hint": self.recovery_hint,
            "severity": self.severity
        }

# Globalna baza informacji o błędach
ERROR_DATABASE: Dict[LuxDBErrorCode, ErrorInfo] = {
    # Błędy ogólne
    LuxDBErrorCode.GENERAL_ERROR: ErrorInfo(
        LuxDBErrorCode.GENERAL_ERROR,
        "Ogólny błąd systemu",
        "Wystąpił niespecyficzny błąd w systemie LuxDB",
        "Sprawdź logi systemowe i kontekst operacji"
    ),
    
    LuxDBErrorCode.UNKNOWN_ERROR: ErrorInfo(
        LuxDBErrorCode.UNKNOWN_ERROR,
        "Nieznany błąd",
        "Wystąpił błąd, który nie został rozpoznany przez system",
        "Zgłoś ten błąd do zespołu LuxDB z pełnym kontekstem"
    ),
    
    LuxDBErrorCode.VALIDATION_ERROR: ErrorInfo(
        LuxDBErrorCode.VALIDATION_ERROR,
        "Błąd walidacji danych",
        "Dane nie przeszły walidacji zgodnie z regułami modelu",
        "Sprawdź format i typy danych według definicji modelu"
    ),
    
    # Błędy połączenia
    LuxDBErrorCode.CONNECTION_FAILED: ErrorInfo(
        LuxDBErrorCode.CONNECTION_FAILED,
        "Błąd połączenia z bazą danych",
        "Nie udało się nawiązać połączenia z bazą danych",
        "Sprawdź string połączenia i dostępność bazy danych"
    ),
    
    LuxDBErrorCode.DATABASE_NOT_FOUND: ErrorInfo(
        LuxDBErrorCode.DATABASE_NOT_FOUND,
        "Baza danych nie istnieje",
        "Próba dostępu do nieistniejącej bazy danych",
        "Utwórz bazę danych lub sprawdź nazwę"
    ),
    
    LuxDBErrorCode.POOL_EXHAUSTED: ErrorInfo(
        LuxDBErrorCode.POOL_EXHAUSTED,
        "Wyczerpano pulę połączeń",
        "Wszystkie dostępne połączenia są w użyciu",
        "Zwiększ max_connections lub zamknij nieużywane połączenia"
    ),
    
    LuxDBErrorCode.TIMEOUT_ERROR: ErrorInfo(
        LuxDBErrorCode.TIMEOUT_ERROR,
        "Przekroczono limit czasu operacji",
        "Operacja trwała dłużej niż maksymalny dozwolony czas",
        "Zoptymalizuj zapytanie lub zwiększ timeout"
    ),
    
    # Błędy danych
    LuxDBErrorCode.DUPLICATE_KEY: ErrorInfo(
        LuxDBErrorCode.DUPLICATE_KEY,
        "Duplikat klucza głównego",
        "Próba wstawienia rekordu z już istniejącym kluczem głównym",
        "Użyj update zamiast insert lub sprawdź istniejące rekordy",
        "WARNING"
    ),
    
    LuxDBErrorCode.UNIQUE_CONSTRAINT_VIOLATION: ErrorInfo(
        LuxDBErrorCode.UNIQUE_CONSTRAINT_VIOLATION,
        "Naruszenie ograniczenia unikalności",
        "Próba wstawienia wartości, która narusza ograniczenie UNIQUE",
        "Sprawdź istniejące wartości w kolumnie z ograniczeniem UNIQUE",
        "WARNING"
    ),
    
    LuxDBErrorCode.FOREIGN_KEY_VIOLATION: ErrorInfo(
        LuxDBErrorCode.FOREIGN_KEY_VIOLATION,
        "Naruszenie klucza obcego",
        "Referencja do nieistniejącego rekordu w tabeli nadrzędnej",
        "Sprawdź czy rekord referencyjny istnieje w tabeli nadrzędnej"
    ),
    
    LuxDBErrorCode.NULL_CONSTRAINT_VIOLATION: ErrorInfo(
        LuxDBErrorCode.NULL_CONSTRAINT_VIOLATION,
        "Naruszenie ograniczenia NOT NULL",
        "Próba wstawienia wartości NULL do kolumny z ograniczeniem NOT NULL",
        "Podaj wartość dla wymaganego pola"
    ),
    
    LuxDBErrorCode.CHECK_CONSTRAINT_VIOLATION: ErrorInfo(
        LuxDBErrorCode.CHECK_CONSTRAINT_VIOLATION,
        "Naruszenie ograniczenia CHECK",
        "Wartość nie spełnia warunków zdefiniowanych w ograniczeniu CHECK",
        "Sprawdź reguły walidacji dla tego pola"
    ),
    
    LuxDBErrorCode.DATA_TYPE_ERROR: ErrorInfo(
        LuxDBErrorCode.DATA_TYPE_ERROR,
        "Błąd typu danych",
        "Nieprawidłowy typ danych dla kolumny",
        "Sprawdź czy typ wartości odpowiada definicji kolumny"
    ),
    
    # Błędy zapytań
    LuxDBErrorCode.QUERY_SYNTAX_ERROR: ErrorInfo(
        LuxDBErrorCode.QUERY_SYNTAX_ERROR,
        "Błąd składni zapytania SQL",
        "Zapytanie SQL zawiera błędy składniowe",
        "Sprawdź składnię SQL zapytania"
    ),
    
    LuxDBErrorCode.QUERY_EXECUTION_ERROR: ErrorInfo(
        LuxDBErrorCode.QUERY_EXECUTION_ERROR,
        "Błąd wykonania zapytania",
        "Wystąpił błąd podczas wykonywania zapytania SQL",
        "Sprawdź poprawność zapytania i parametrów"
    ),
    
    LuxDBErrorCode.QUERY_TIMEOUT: ErrorInfo(
        LuxDBErrorCode.QUERY_TIMEOUT,
        "Przekroczono limit czasu zapytania",
        "Zapytanie nie zostało wykonane w dozwolonym czasie",
        "Zoptymalizuj zapytanie lub dodaj indeksy"
    ),
    
    LuxDBErrorCode.INVALID_QUERY_PARAMS: ErrorInfo(
        LuxDBErrorCode.INVALID_QUERY_PARAMS,
        "Nieprawidłowe parametry zapytania",
        "Parametry zapytania są nieprawidłowe lub niekompletne",
        "Sprawdź format i kompletność parametrów zapytania"
    ),
    
    # Błędy migracji
    LuxDBErrorCode.MIGRATION_FAILED: ErrorInfo(
        LuxDBErrorCode.MIGRATION_FAILED,
        "Migracja nie powiodła się",
        "Wykonanie migracji bazy danych zakończyło się błędem",
        "Sprawdź SQL migracji i stan bazy danych"
    ),
    
    LuxDBErrorCode.MIGRATION_ROLLBACK_FAILED: ErrorInfo(
        LuxDBErrorCode.MIGRATION_ROLLBACK_FAILED,
        "Rollback migracji nie powiódł się",
        "Nie udało się cofnąć migracji po błędzie",
        "Przywróć bazę z backup i sprawdź integralność danych"
    ),
    
    LuxDBErrorCode.SCHEMA_CONFLICT: ErrorInfo(
        LuxDBErrorCode.SCHEMA_CONFLICT,
        "Konflikt schematu bazy danych",
        "Schemat bazy nie jest zgodny z oczekiwanym",
        "Uruchom migracje lub sprawdź wersję schematu"
    ),
    
    LuxDBErrorCode.VERSION_CONFLICT: ErrorInfo(
        LuxDBErrorCode.VERSION_CONFLICT,
        "Konflikt wersji bazy danych",
        "Wersja bazy danych nie jest zgodna z aplikacją",
        "Zaktualizuj bazę do odpowiedniej wersji"
    ),
    
    # Błędy synchronizacji
    LuxDBErrorCode.SYNC_FAILED: ErrorInfo(
        LuxDBErrorCode.SYNC_FAILED,
        "Synchronizacja baz danych nie powiodła się",
        "Błąd podczas synchronizacji danych między bazami",
        "Sprawdź połączenia i integralność danych w obu bazach"
    ),
    
    LuxDBErrorCode.SOURCE_DB_ERROR: ErrorInfo(
        LuxDBErrorCode.SOURCE_DB_ERROR,
        "Błąd bazy źródłowej podczas synchronizacji",
        "Problem z dostępem do bazy źródłowej",
        "Sprawdź połączenie i stan bazy źródłowej"
    ),
    
    LuxDBErrorCode.TARGET_DB_ERROR: ErrorInfo(
        LuxDBErrorCode.TARGET_DB_ERROR,
        "Błąd bazy docelowej podczas synchronizacji",
        "Problem z dostępem do bazy docelowej",
        "Sprawdź połączenie i stan bazy docelowej"
    ),
    
    LuxDBErrorCode.DATA_INCONSISTENCY: ErrorInfo(
        LuxDBErrorCode.DATA_INCONSISTENCY,
        "Niespójność danych podczas synchronizacji",
        "Wykryto różnice w danych między bazami",
        "Sprawdź integralność danych i rozwiąż konflikty ręcznie"
    ),
}

def get_error_info(code: LuxDBErrorCode) -> ErrorInfo:
    """Pobiera informacje o błędzie na podstawie kodu"""
    return ERROR_DATABASE.get(code, ERROR_DATABASE[LuxDBErrorCode.UNKNOWN_ERROR])

def detect_error_from_exception(exception: Exception) -> LuxDBErrorCode:
    """Wykrywa kod błędu na podstawie wyjątku SQLAlchemy"""
    error_message = str(exception).lower()
    
    # Błędy unikalności
    if "unique constraint" in error_message or "duplicate" in error_message:
        if "primary key" in error_message:
            return LuxDBErrorCode.DUPLICATE_KEY
        else:
            return LuxDBErrorCode.UNIQUE_CONSTRAINT_VIOLATION
    
    # Błędy kluczy obcych
    if "foreign key" in error_message:
        return LuxDBErrorCode.FOREIGN_KEY_VIOLATION
    
    # Błędy NOT NULL
    if "not null" in error_message or "null constraint" in error_message:
        return LuxDBErrorCode.NULL_CONSTRAINT_VIOLATION
    
    # Błędy CHECK
    if "check constraint" in error_message:
        return LuxDBErrorCode.CHECK_CONSTRAINT_VIOLATION
    
    # Błędy połączenia
    if "connection" in error_message or "timeout" in error_message:
        if "timeout" in error_message:
            return LuxDBErrorCode.TIMEOUT_ERROR
        else:
            return LuxDBErrorCode.CONNECTION_FAILED
    
    # Błędy zapytań
    if "syntax error" in error_message:
        return LuxDBErrorCode.QUERY_SYNTAX_ERROR
    
    # Domyślny błąd
    return LuxDBErrorCode.UNKNOWN_ERROR
