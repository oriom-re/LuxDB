
"""
Modele SQLAlchemy dla LuxDB
"""

from ..config import Base, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, relationship, func

# Modele SQLAlchemy
class User(Base):
    """Model użytkownika"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relacje
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user")

class UserSession(Base):
    """Model sesji użytkownika"""
    __tablename__ = 'sessions'
    
    id = Column(String(255), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    data = Column(Text, nullable=True)  # JSON data
    
    # Relacje
    user = relationship("User", back_populates="sessions")

class Log(Base):
    """Model logów systemu"""
    __tablename__ = 'logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, index=True)
    
    # Relacje
    user = relationship("User", back_populates="logs")

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

__all__ = [
    'User',
    'UserSession',
    'Log',
    'DatabaseSchema',
    'Migration',
    'TableDefinition',
    'SYSTEM_MODELS',
    'Base'
]
