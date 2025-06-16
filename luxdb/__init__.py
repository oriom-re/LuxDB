
"""
LuxDB - Zaawansowany manager baz danych SQLAlchemy z generatorem modeli
"""

__version__ = "1.0.0"
__author__ = "LuxDB Team"
__email__ = "team@luxdb.dev"

from .manager import DatabaseManager, get_db_manager
from .config import DatabaseConfig, DatabaseType, ConnectionPool
from .models import User, UserSession, Log, DatabaseSchema, Migration, TableDefinition
from .session_manager import SessionManager, get_session_manager

__all__ = [
    'DatabaseManager',
    'get_db_manager',
    'SessionManager',
    'get_session_manager',
    'DatabaseConfig', 
    'DatabaseType',
    'ConnectionPool',
    'User',
    'UserSession', 
    'Log',
    'DatabaseSchema',
    'Migration',
    'TableDefinition'
]
