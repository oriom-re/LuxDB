
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
    
    def log_database_operation(self, operation: str, db_name: str, 
                             success: bool, details: Optional[str] = None,
                             execution_time: Optional[float] = None):
        """Loguje operacje bazodanowe w format human-friendly"""
        if success:
            message = f"✅ {operation} na bazie '{db_name}'"
            if execution_time:
                message += f" ({execution_time:.3f}s)"
            self.logger.info(message)
        else:
            import hashlib
            from datetime import datetime
            
            # Generuj ID dla niepowodzenia
            fail_id = hashlib.md5(f"{operation}_{db_name}_{datetime.now()}".encode()).hexdigest()[:8]
            
            message = f"❌ Niepowodzenie: {operation} na bazie '{db_name}' | ID: {fail_id}"
            self.logger.error(message)
            
            # Szczegóły w osobnym logu
            if details:
                detailed_message = f"[OPERATION_DETAILS:{fail_id}] {operation} na {db_name}"
                detailed_message += f"\n  Szczegóły: {details}"
                if execution_time:
                    detailed_message += f"\n  Czas wykonania: {execution_time:.3f}s"
                self.logger.debug(detailed_message)
    
    def log_query_execution(self, query_type: str, table_name: str, 
                          records_affected: int, execution_time: float):
        """Loguje wykonanie zapytań w format human-friendly"""
        # Wybierz odpowiednią ikonę
        icon = {
            'SELECT': '🔍',
            'INSERT': '➕',
            'UPDATE': '✏️',
            'DELETE': '🗑️'
        }.get(query_type.upper(), '📝')
        
        message = f"{icon} {query_type} na '{table_name}': {records_affected} rekordów"
        
        # Dodaj ostrzeżenie jeśli zapytanie było wolne
        if execution_time > 1.0:
            message += f" ⚠️ ({execution_time:.3f}s - wolne zapytanie)"
        elif execution_time > 0.1:
            message += f" ({execution_time:.3f}s)"
        
        self.logger.info(message)
    
    def log_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Loguje błędy z kontekstem w format human-friendly"""
        import traceback
        import hashlib
        from datetime import datetime
        
        # Generuj unikalny ID błędu
        error_id = hashlib.md5(f"{operation}_{str(error)}_{datetime.now()}".encode()).hexdigest()[:8]
        
        # Podstawowy komunikat dla człowieka
        human_message = f"❌ Błąd w operacji '{operation}': {type(error).__name__}"
        
        # Dodaj kontekst jeśli istnieje
        if context:
            important_context = {k: v for k, v in context.items() 
                               if k in ['table_name', 'db_name', 'model_name', 'operation_name']}
            if important_context:
                context_str = ", ".join([f"{k}={v}" for k, v in important_context.items()])
                human_message += f" ({context_str})"
        
        # Link do szczegółów
        human_message += f" | Szczegóły: error_id={error_id}"
        
        # Loguj podstawowy komunikat
        self.logger.error(human_message)
        
        # Loguj szczegółowe informacje z unikalnym ID
        detailed_message = f"[ERROR_DETAILS:{error_id}] {operation}"
        detailed_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "traceback": traceback.format_exc(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Formatuj szczegóły w czytelny sposób
        details_str = f"\n  Typ błędu: {detailed_info['error_type']}"
        details_str += f"\n  Komunikat: {detailed_info['error_message']}"
        if detailed_info['context']:
            details_str += f"\n  Kontekst: {detailed_info['context']}"
        details_str += f"\n  Czas: {detailed_info['timestamp']}"
        details_str += f"\n  Stack trace:\n{detailed_info['traceback']}"
        
        self.logger.debug(detailed_message + details_str)
    
    def log_migration(self, db_name: str, from_version: int, to_version: int, 
                     success: bool, execution_time: Optional[float] = None):
        """Loguje migracje w format human-friendly"""
        if success:
            message = f"🔄 Migracja '{db_name}': v{from_version} → v{to_version}"
            if execution_time:
                message += f" ({execution_time:.3f}s)"
            self.logger.info(message)
        else:
            import hashlib
            from datetime import datetime
            
            migration_id = hashlib.md5(f"migration_{db_name}_{from_version}_{to_version}_{datetime.now()}".encode()).hexdigest()[:8]
            message = f"❌ Błąd migracji '{db_name}': v{from_version} → v{to_version} | ID: {migration_id}"
            self.logger.error(message)
            
            # Szczegóły w debug
            if execution_time:
                detailed_message = f"[MIGRATION_DETAILS:{migration_id}] Czas wykonania: {execution_time:.3f}s"
                self.logger.debug(detailed_message)
    
    def log_sync(self, source_db: str, target_db: str, models: list, 
                success: bool, records_synced: int = 0):
        """Loguje synchronizację w format human-friendly"""
        model_names = [m.__name__ for m in models] if models else []
        
        if success:
            message = f"🔄 Synchronizacja: {source_db} → {target_db} | {len(model_names)} modeli, {records_synced} rekordów"
            self.logger.info(message)
        else:
            import hashlib
            from datetime import datetime
            
            sync_id = hashlib.md5(f"sync_{source_db}_{target_db}_{datetime.now()}".encode()).hexdigest()[:8]
            message = f"❌ Błąd synchronizacji: {source_db} → {target_db} | ID: {sync_id}"
            self.logger.error(message)
            
            # Szczegóły w debug
            detailed_message = f"[SYNC_DETAILS:{sync_id}] Modele: {model_names}, Rekordy: {records_synced}"
            self.logger.debug(detailed_message)

# Singleton instance
_db_logger = None

def get_db_logger() -> DatabaseLogger:
    """Zwraca singleton instance loggera"""
    global _db_logger
    if _db_logger is None:
        _db_logger = DatabaseLogger()
    return _db_logger
