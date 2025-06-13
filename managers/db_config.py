
"""
Konfiguracja i klasy pomocnicze dla systemu zarządzania bazami danych
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

class DatabaseType(Enum):
    """Typy baz danych obsługiwane przez system"""
    SQLITE = "sqlite"
    DISTRIBUTED = "distributed"
    REPLICA = "replica"

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
    
    def __post_init__(self):
        if self.replica_targets is None:
            self.replica_targets = []

@dataclass 
class TableSchema:
    """Schemat tabeli"""
    name: str
    columns: Dict[str, str]
    constraints: List[str] = None
    indexes: List[str] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.indexes is None:
            self.indexes = []

@dataclass
class Migration:
    """Definicja migracji"""
    id: str
    db_name: str
    from_version: int
    to_version: int
    type: MigrationType
    sql: str
    rollback_sql: str = ""
    description: str = ""
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class QueryBuilder:
    """Builder do tworzenia zapytań SQL"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.reset()
    
    def reset(self):
        """Resetuje builder"""
        self._select_fields = []
        self._where_conditions = []
        self._where_params = []
        self._join_clauses = []
        self._order_by = []
        self._group_by = []
        self._having = []
        self._limit_value = None
        self._offset_value = None
        return self
    
    def select(self, *fields):
        """Dodaje pola do SELECT"""
        self._select_fields.extend(fields)
        return self
    
    def where(self, condition: str, *params):
        """Dodaje warunek WHERE"""
        self._where_conditions.append(condition)
        self._where_params.extend(params)
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER"):
        """Dodaje JOIN"""
        self._join_clauses.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self
    
    def order_by(self, field: str, direction: str = "ASC"):
        """Dodaje ORDER BY"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields):
        """Dodaje GROUP BY"""
        self._group_by.extend(fields)
        return self
    
    def having(self, condition: str):
        """Dodaje HAVING"""
        self._having.append(condition)
        return self
    
    def limit(self, count: int):
        """Dodaje LIMIT"""
        self._limit_value = count
        return self
    
    def offset(self, count: int):
        """Dodaje OFFSET"""
        self._offset_value = count
        return self
    
    def build_select(self) -> tuple:
        """Buduje zapytanie SELECT"""
        fields = ", ".join(self._select_fields) if self._select_fields else "*"
        sql = f"SELECT {fields} FROM {self.table_name}"
        
        if self._join_clauses:
            sql += " " + " ".join(self._join_clauses)
        
        if self._where_conditions:
            sql += " WHERE " + " AND ".join(self._where_conditions)
        
        if self._group_by:
            sql += " GROUP BY " + ", ".join(self._group_by)
        
        if self._having:
            sql += " HAVING " + " AND ".join(self._having)
        
        if self._order_by:
            sql += " ORDER BY " + ", ".join(self._order_by)
        
        if self._limit_value:
            sql += f" LIMIT {self._limit_value}"
        
        if self._offset_value:
            sql += f" OFFSET {self._offset_value}"
        
        return sql, self._where_params
    
    def build_update(self, data: Dict[str, Any]) -> tuple:
        """Buduje zapytanie UPDATE"""
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        sql = f"UPDATE {self.table_name} SET {set_clause}"
        params = list(data.values())
        
        if self._where_conditions:
            sql += " WHERE " + " AND ".join(self._where_conditions)
            params.extend(self._where_params)
        
        return sql, params
    
    def build_delete(self) -> tuple:
        """Buduje zapytanie DELETE"""
        sql = f"DELETE FROM {self.table_name}"
        
        if self._where_conditions:
            sql += " WHERE " + " AND ".join(self._where_conditions)
        
        return sql, self._where_params

class ConnectionPool:
    """Pool połączeń do bazy danych"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self.available_connections = []
        self.used_connections = set()
        self.lock = threading.RLock()
    
    def get_connection(self):
        """Pobiera połączenie z poola"""
        with self.lock:
            if self.available_connections:
                conn = self.available_connections.pop()
                self.used_connections.add(conn)
                return conn
            elif len(self.used_connections) < self.max_connections:
                import sqlite3
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.used_connections.add(conn)
                return conn
            else:
                raise Exception("Brak dostępnych połączeń w poolu")
    
    def return_connection(self, conn):
        """Zwraca połączenie do poola"""
        with self.lock:
            if conn in self.used_connections:
                self.used_connections.remove(conn)
                self.available_connections.append(conn)
    
    def close_all(self):
        """Zamyka wszystkie połączenia"""
        with self.lock:
            for conn in self.available_connections + list(self.used_connections):
                try:
                    conn.close()
                except:
                    pass
            self.available_connections.clear()
            self.used_connections.clear()

# Predefiniowane schematy tabel dla systemu Asty
SYSTEM_TABLES = {
    "users": TableSchema(
        name="users",
        columns={
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "username": "TEXT UNIQUE NOT NULL",
            "email": "TEXT UNIQUE NOT NULL", 
            "password_hash": "TEXT NOT NULL",
            "phone": "TEXT DEFAULT frtg",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "updated_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "is_active": "BOOLEAN DEFAULT 1"
        },
        indexes=["CREATE INDEX idx_users_email ON users(email)",
                "CREATE INDEX idx_users_username ON users(username)"]
    ),
    
    "sessions": TableSchema(
        name="sessions",
        columns={
            "id": "TEXT PRIMARY KEY",
            "user_id": "INTEGER NOT NULL",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "expires_at": "TIMESTAMP NOT NULL",
            "data": "TEXT"
        },
        constraints=["FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"],
        indexes=["CREATE INDEX idx_sessions_user_id ON sessions(user_id)",
                "CREATE INDEX idx_sessions_expires ON sessions(expires_at)"]
    ),
    
    "logs": TableSchema(
        name="logs",
        columns={
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "level": "TEXT NOT NULL",
            "message": "TEXT NOT NULL",
            "module": "TEXT",
            "user_id": "INTEGER",
            "ip_address": "TEXT",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },
        indexes=["CREATE INDEX idx_logs_level ON logs(level)",
                "CREATE INDEX idx_logs_created_at ON logs(created_at)",
                "CREATE INDEX idx_logs_user_id ON logs(user_id)"]
    )
}

# Konfiguracje domyślne dla różnych typów baz
DEFAULT_CONFIGS = {
    "main": DatabaseConfig(
        name="main",
        type=DatabaseType.SQLITE,
        max_connections=20,
        backup_enabled=True,
        auto_optimize=True
    ),
    
    "analytics": DatabaseConfig(
        name="analytics", 
        type=DatabaseType.SQLITE,
        max_connections=10,
        backup_enabled=True,
        auto_optimize=True
    ),
    
    "cache": DatabaseConfig(
        name="cache",
        type=DatabaseType.SQLITE,
        max_connections=5,
        backup_enabled=False,
        auto_optimize=False
    )
}
