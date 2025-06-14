
"""
LuxDB - Zaawansowany menedżer baz danych SQLAlchemy
"""

from .manager import DatabaseManager, get_db_manager
from .config import DatabaseConfig, DatabaseType, ConnectionPool
from .models import User, UserSession, Log, DatabaseSchema, Migration, TableDefinition
from .utils import ModelGenerator, QueryBuilder

__version__ = "1.0.0"
__author__ = "LuxDB Team"

__all__ = [
    "DatabaseManager",
    "get_db_manager", 
    "DatabaseConfig",
    "DatabaseType",
    "ConnectionPool",
    "User",
    "UserSession", 
    "Log",
    "DatabaseSchema",
    "Migration",
    "TableDefinition",
    "ModelGenerator",
    "QueryBuilder"
]
