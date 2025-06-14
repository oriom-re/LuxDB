
"""
Modele SQLAlchemy dla systemu LuxDB
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config import Base

# Modele SQLAlchemy dla systemu LuxDB
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

# Predefiniowane modele dla systemu LuxDB
SYSTEM_MODELS = {
    "users": User,
    "sessions": UserSession,
    "logs": Log
}

__all__ = [
    "User", 
    "UserSession", 
    "Log", 
    "DatabaseSchema", 
    "Migration", 
    "TableDefinition",
    "SYSTEM_MODELS"
]
