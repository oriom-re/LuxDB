
"""
Konfiguracja i klasy pomocnicze dla systemu zarządzania bazami danych z SQLAlchemy
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
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
    
# Modele SQLAlchemy dla systemu Asty
class User(Base):
    """Model użytkownika"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), default=None)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    # Relacje
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user")

class UserSession(Base):
    """Model sesji użytkownika"""
    __tablename__ = 'sessions'
    
    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    expires_at = Column(DateTime, nullable=False)
    data = Column(Text)
    
    # Relacje
    user = relationship("User", back_populates="sessions")

class Log(Base):
    """Model logów systemu"""
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'))
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=func.current_timestamp())
    
    # Relacje
    user = relationship("User", back_populates="logs")

# Modele metadanych
class DatabaseSchema(Base):
    """Model schematu bazy danych"""
    __tablename__ = 'database_schemas'
    
    db_name = Column(String(255), primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    schema_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

class Migration(Base):
    """Model migracji"""
    __tablename__ = 'migrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    db_name = Column(String(255), ForeignKey('database_schemas.db_name'), nullable=False)
    from_version = Column(Integer, nullable=False)
    to_version = Column(Integer, nullable=False)
    migration_sql = Column(Text, nullable=False)
    applied_at = Column(DateTime, default=func.current_timestamp())

class TableDefinition(Base):
    """Model definicji tabel"""
    __tablename__ = 'table_definitions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    db_name = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False)
    definition = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.current_timestamp())

class QueryBuilder:
    """Builder do tworzenia zapytań SQLAlchemy"""
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.session = None
        self.reset()
    
    def reset(self):
        """Resetuje builder"""
        self._query = None
        self._filters = []
        self._joins = []
        self._order_by_clauses = []
        self._group_by_clauses = []
        self._having_clauses = []
        self._limit_value = None
        self._offset_value = None
        return self
    
    def set_session(self, session: Session):
        """Ustawia sesję SQLAlchemy"""
        self.session = session
        return self
    
    def select(self, *columns):
        """Dodaje kolumny do SELECT"""
        if not self.session:
            raise ValueError("Sesja nie została ustawiona")
        
        if columns:
            self._query = self.session.query(*[getattr(self.model_class, col) for col in columns])
        else:
            self._query = self.session.query(self.model_class)
        return self
    
    def filter(self, *conditions):
        """Dodaje warunki WHERE"""
        if not self._query:
            self.select()
        
        for condition in conditions:
            self._query = self._query.filter(condition)
        return self
    
    def join(self, *args, **kwargs):
        """Dodaje JOIN"""
        if not self._query:
            self.select()
        
        self._query = self._query.join(*args, **kwargs)
        return self
    
    def order_by(self, *columns):
        """Dodaje ORDER BY"""
        if not self._query:
            self.select()
        
        self._query = self._query.order_by(*columns)
        return self
    
    def group_by(self, *columns):
        """Dodaje GROUP BY"""
        if not self._query:
            self.select()
        
        self._query = self._query.group_by(*columns)
        return self
    
    def having(self, condition):
        """Dodaje HAVING"""
        if not self._query:
            self.select()
        
        self._query = self._query.having(condition)
        return self
    
    def limit(self, count: int):
        """Dodaje LIMIT"""
        if not self._query:
            self.select()
        
        self._query = self._query.limit(count)
        return self
    
    def offset(self, count: int):
        """Dodaje OFFSET"""
        if not self._query:
            self.select()
        
        self._query = self._query.offset(count)
        return self
    
    def all(self):
        """Zwraca wszystkie wyniki"""
        if not self._query:
            self.select()
        return self._query.all()
    
    def first(self):
        """Zwraca pierwszy wynik"""
        if not self._query:
            self.select()
        return self._query.first()
    
    def count(self):
        """Zwraca liczbę wyników"""
        if not self._query:
            self.select()
        return self._query.count()

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

# Predefiniowane modele dla systemu Asty
SYSTEM_MODELS = {
    "users": User,
    "sessions": Session,
    "logs": Log
}

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
