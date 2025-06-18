
"""
Konfiguracja i klasy pomocnicze dla systemu zarządzania bazami danych z SQLAlchemy
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, create_engine, MetaData, JSON
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship, Session, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import threading

Base = declarative_base()



class DatabaseType(Enum):
    """Typy baz danych obsługiwane przez system"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"

class MigrationType(Enum):
    """Typy migracji"""
    SCHEMA_CHANGE = "schema_change"
    DATA_MIGRATION = "data_migration" 
    INDEX_CREATION = "index_creation"
    CONSTRAINT_CHANGE = "constraint_change"

@dataclass
class DatabaseConfig:
    """Konfiguracja bazy danych"""
    name: str
    type: DatabaseType
    version: int = 1
    max_connections: int = 10
    backup_enabled: bool = True
    auto_optimize: bool = True
    replication_enabled: bool = False
    replica_targets: List[str] = None
    connection_string: str = ""
    
    def __post_init__(self):
        if self.replica_targets is None:
            self.replica_targets = []
        if not self.connection_string:
            self.connection_string = f"sqlite:///db/{self.name}.db"

class ConnectionPool:
    """Pool połączeń SQLAlchemy"""
    
    def __init__(self, connection_string: str, max_connections: int = 10, echo: bool = False):
        self.connection_string = connection_string
        self.max_connections = max_connections
        self.engine = create_engine(
            connection_string,
            pool_size=max_connections,
            max_overflow=0,
            echo=echo
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.lock = threading.RLock()
    
    def get_session(self) -> Session:
        """Pobiera sesję z poola"""
        return self.SessionLocal()
    
    def create_tables(self, base=Base):
        """Tworzy wszystkie tabele"""
        base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self, base=Base):
        """Usuwa wszystkie tabele"""
        base.metadata.drop_all(bind=self.engine)
    
    def close(self):
        """Zamyka pool połączeń"""
        self.engine.dispose()

# Konfiguracje domyślne dla różnych typów baz
DEFAULT_CONFIGS = {
    "main": DatabaseConfig(
        name="main",
        type=DatabaseType.SQLITE,
        max_connections=20,
        backup_enabled=True,
        auto_optimize=True,
        connection_string="sqlite:///db/main.db"
    ),
    
    "analytics": DatabaseConfig(
        name="analytics", 
        type=DatabaseType.SQLITE,
        max_connections=10,
        backup_enabled=True,
        auto_optimize=True,
        connection_string="sqlite:///db/analytics.db"
    ),
    
    "cache": DatabaseConfig(
        name="cache",
        type=DatabaseType.SQLITE,
        max_connections=5,
        backup_enabled=False,
        auto_optimize=False,
        connection_string="sqlite:///db/cache.db"
    )
}
