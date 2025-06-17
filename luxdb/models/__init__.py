"""
Modele LuxDB - Astralny archetyp bytów
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..config import Base

class User(Base):
    """Model użytkownika Astralnej Biblioteki"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relacje
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class UserSession(Base):
    """Model sesji użytkownika"""
    __tablename__ = 'user_sessions'

    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    destroyed_at = Column(DateTime, nullable=True)
    data = Column(Text, nullable=True, default='{}')
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # Relacje
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return f"<UserSession(id='{self.id}', user_id={self.user_id}, expires_at='{self.expires_at}')>"

class Log(Base):
    """Model logów systemowych"""
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # Relacje
    user = relationship("User", back_populates="logs")

    def __repr__(self):
        return f"<Log(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"

class DatabaseSchema(Base):
    """Model schematu bazy danych"""
    __tablename__ = 'database_schemas'
    
    db_name = Column(String(255), primary_key=True)
    version = Column(Integer, nullable=False, default=1)
    schema_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)

class Migration(Base):
    """Model migracji bazy danych"""
    __tablename__ = 'migrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    db_name = Column(String(255), nullable=False, index=True)
    from_version = Column(Integer, nullable=False)
    to_version = Column(Integer, nullable=False)
    migration_sql = Column(Text, nullable=False)
    applied_at = Column(DateTime, default=func.current_timestamp(), nullable=False)

class TableDefinition(Base):
    """Model definicji tabeli"""
    __tablename__ = 'table_definitions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    db_name = Column(String(255), nullable=False, index=True)
    table_name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    definition = Column(Text, nullable=False)  # JSON definition
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)

# Lista wszystkich modeli systemu
SYSTEM_MODELS = {
    'User': User,
    'UserSession': UserSession,
    'Log': Log,
    'DatabaseSchema': DatabaseSchema,
    'Migration': Migration,
    'TableDefinition': TableDefinition
}

__all__ = ['User', 'UserSession', 'Log', 'DatabaseSchema', 'Migration', 'TableDefinition', 'SYSTEM_MODELS']