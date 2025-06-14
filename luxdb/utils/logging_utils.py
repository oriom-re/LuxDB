
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
    
    def log_error(self, operation: str, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Loguje błędy z kontekstem"""
        message = f"Error in {operation}: {str(error)}"
        
        if context:
            context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
            message += f" | Context: {context_str}"
        
        self.logger.error(message, exc_info=True)
    
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
