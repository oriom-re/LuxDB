
import sqlite3
import os
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
import threading

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Wyjątek dla błędów bazy danych"""
    pass

class MigrationError(Exception):
    """Wyjątek dla błędów migracji"""
    pass

class DatabaseManager:
    """
    Główny menedżer baz danych SQLite dla systemu Asty
    Obsługuje wiele instancji baz, wersjonowanie, migracje i replikację
    """
    
    def __init__(self, db_directory: str = "db"):
        self.db_directory = db_directory
        self.connections = {}
        self.schemas = {}
        self.migrations = {}
        self.lock = threading.RLock()
        
        # Zapewnij istnienie katalogu
        os.makedirs(db_directory, exist_ok=True)
        
        # Inicjalizuj główną bazę metadanych
        self._init_metadata_db()
    
    def _init_metadata_db(self):
        """Inicjalizuje bazę metadanych do zarządzania schematami i migracjami"""
        metadata_path = os.path.join(self.db_directory, "_metadata.db")
        
        with sqlite3.connect(metadata_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS database_schemas (
                    db_name TEXT PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    schema_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    db_name TEXT NOT NULL,
                    from_version INTEGER NOT NULL,
                    to_version INTEGER NOT NULL,
                    migration_sql TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (db_name) REFERENCES database_schemas (db_name)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS table_definitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    db_name TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    definition TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(db_name, table_name, version)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self, db_name: str):
        """Context manager dla bezpiecznego dostępu do połączenia z bazą"""
        with self.lock:
            db_path = os.path.join(self.db_directory, f"{db_name}.db")
            
            try:
                conn = sqlite3.connect(db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row  # Umożliwia dostęp do kolumn po nazwach
                conn.execute("PRAGMA foreign_keys = ON")  # Włącz klucze obce
                yield conn
            except Exception as e:
                logger.error(f"Błąd połączenia z bazą {db_name}: {e}")
                raise DatabaseError(f"Nie można połączyć się z bazą {db_name}: {e}")
            finally:
                if 'conn' in locals():
                    conn.close()
    
    def create_database(self, db_name: str) -> bool:
        """Tworzy nową bazę danych"""
        try:
            with self.get_connection(db_name) as conn:
                # Baza zostaje utworzona automatycznie przez połączenie
                pass
            
            # Zarejestruj w metadanych
            self._register_database(db_name)
            logger.info(f"Utworzono bazę danych: {db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia bazy {db_name}: {e}")
            return False
    
    def _register_database(self, db_name: str, version: int = 1):
        """Rejestruje bazę w systemie metadanych"""
        metadata_path = os.path.join(self.db_directory, "_metadata.db")
        
        with sqlite3.connect(metadata_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO database_schemas 
                (db_name, version, schema_hash, updated_at)
                VALUES (?, ?, ?, ?)
            """, (db_name, version, self._calculate_schema_hash(db_name), datetime.now()))
            conn.commit()
    
    def _calculate_schema_hash(self, db_name: str) -> str:
        """Oblicza hash schematu bazy danych"""
        try:
            with self.get_connection(db_name) as conn:
                cursor = conn.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                
                schema_sql = ''.join([row[0] or '' for row in cursor.fetchall()])
                return hashlib.md5(schema_sql.encode()).hexdigest()
        except:
            return ""
    
    def create_table(self, db_name: str, table_name: str, columns: Dict[str, str], 
                    constraints: List[str] = None) -> bool:
        """
        Tworzy tabelę w bazie danych
        
        Args:
            db_name: Nazwa bazy danych
            table_name: Nazwa tabeli
            columns: Słownik {nazwa_kolumny: definicja_typu}
            constraints: Lista dodatkowych ograniczeń
        """
        try:
            # Przygotuj SQL
            columns_sql = ", ".join([f"{name} {definition}" for name, definition in columns.items()])
            
            if constraints:
                constraints_sql = ", " + ", ".join(constraints)
            else:
                constraints_sql = ""
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql}{constraints_sql})"
            
            with self.get_connection(db_name) as conn:
                conn.execute(create_sql)
                conn.commit()
            
            # Zapisz definicję tabeli
            self._save_table_definition(db_name, table_name, create_sql)
            
            logger.info(f"Utworzono tabelę {table_name} w bazie {db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia tabeli {table_name} w bazie {db_name}: {e}")
            return False
    
    def _save_table_definition(self, db_name: str, table_name: str, definition: str):
        """Zapisuje definicję tabeli w metadanych"""
        version = self.get_database_version(db_name)
        metadata_path = os.path.join(self.db_directory, "_metadata.db")
        
        with sqlite3.connect(metadata_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO table_definitions 
                (db_name, table_name, version, definition)
                VALUES (?, ?, ?, ?)
            """, (db_name, table_name, version, definition))
            conn.commit()
    
    def drop_table(self, db_name: str, table_name: str, backup: bool = True) -> bool:
        """
        Usuwa tabelę z bazy danych
        
        Args:
            db_name: Nazwa bazy danych
            table_name: Nazwa tabeli
            backup: Czy utworzyć backup przed usunięciem
        """
        try:
            if backup:
                self._backup_table(db_name, table_name)
            
            with self.get_connection(db_name) as conn:
                conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                conn.commit()
            
            logger.info(f"Usunięto tabelę {table_name} z bazy {db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd usuwania tabeli {table_name} z bazy {db_name}: {e}")
            return False
    
    def _backup_table(self, db_name: str, table_name: str):
        """Tworzy backup tabeli przed usunięciem"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{table_name}_backup_{timestamp}"
        
        try:
            with self.get_connection(db_name) as conn:
                conn.execute(f"CREATE TABLE {backup_name} AS SELECT * FROM {table_name}")
                conn.commit()
            logger.info(f"Utworzono backup tabeli: {backup_name}")
        except Exception as e:
            logger.warning(f"Nie udało się utworzyć backupu tabeli {table_name}: {e}")
    
    def insert_data(self, db_name: str, table_name: str, data: Dict[str, Any]) -> bool:
        """Wstawia dane do tabeli"""
        try:
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = list(data.values())
            
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.get_connection(db_name) as conn:
                conn.execute(sql, values)
                conn.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Błąd wstawiania danych do {table_name} w bazie {db_name}: {e}")
            return False
    
    def insert_batch(self, db_name: str, table_name: str, data_list: List[Dict[str, Any]]) -> bool:
        """Wstawia wiele rekordów jednocześnie"""
        if not data_list:
            return True
            
        try:
            first_record = data_list[0]
            columns = ", ".join(first_record.keys())
            placeholders = ", ".join(["?" for _ in first_record])
            
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.get_connection(db_name) as conn:
                values_list = [list(record.values()) for record in data_list]
                conn.executemany(sql, values_list)
                conn.commit()
            
            logger.info(f"Wstawiono {len(data_list)} rekordów do {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd wstawiania batch do {table_name} w bazie {db_name}: {e}")
            return False
    
    def update_data(self, db_name: str, table_name: str, data: Dict[str, Any], 
                   where_clause: str, where_params: List[Any] = None) -> int:
        """
        Aktualizuje dane w tabeli
        
        Returns:
            Liczba zaktualizowanych rekordów
        """
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            
            if where_params:
                values.extend(where_params)
            
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            
            with self.get_connection(db_name) as conn:
                cursor = conn.execute(sql, values)
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Błąd aktualizacji danych w {table_name} w bazie {db_name}: {e}")
            return 0
    
    def delete_data(self, db_name: str, table_name: str, where_clause: str, 
                   where_params: List[Any] = None) -> int:
        """
        Usuwa dane z tabeli
        
        Returns:
            Liczba usuniętych rekordów
        """
        try:
            sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            params = where_params or []
            
            with self.get_connection(db_name) as conn:
                cursor = conn.execute(sql, params)
                conn.commit()
                return cursor.rowcount
                
        except Exception as e:
            logger.error(f"Błąd usuwania danych z {table_name} w bazie {db_name}: {e}")
            return 0
    
    def select_data(self, db_name: str, table_name: str, columns: str = "*", 
                   where_clause: str = None, where_params: List[Any] = None,
                   order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Pobiera dane z tabeli"""
        try:
            sql = f"SELECT {columns} FROM {table_name}"
            params = []
            
            if where_clause:
                sql += f" WHERE {where_clause}"
                if where_params:
                    params.extend(where_params)
            
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            if limit:
                sql += f" LIMIT {limit}"
            
            with self.get_connection(db_name) as conn:
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Błąd pobierania danych z {table_name} w bazie {db_name}: {e}")
            return []
    
    def execute_custom_query(self, db_name: str, sql: str, params: List[Any] = None) -> List[Dict[str, Any]]:
        """Wykonuje niestandardowe zapytanie SQL"""
        try:
            with self.get_connection(db_name) as conn:
                cursor = conn.execute(sql, params or [])
                if sql.strip().upper().startswith('SELECT'):
                    rows = cursor.fetchall()
                    return [dict(row) for row in rows]
                else:
                    conn.commit()
                    return [{"affected_rows": cursor.rowcount}]
                    
        except Exception as e:
            logger.error(f"Błąd wykonywania zapytania w bazie {db_name}: {e}")
            return []
    
    def get_database_version(self, db_name: str) -> int:
        """Pobiera aktualną wersję bazy danych"""
        metadata_path = os.path.join(self.db_directory, "_metadata.db")
        
        try:
            with sqlite3.connect(metadata_path) as conn:
                cursor = conn.execute(
                    "SELECT version FROM database_schemas WHERE db_name = ?", 
                    (db_name,)
                )
                result = cursor.fetchone()
                return result[0] if result else 1
        except:
            return 1
    
    def create_migration(self, db_name: str, migration_sql: str, 
                        description: str = "") -> bool:
        """Tworzy nową migrację bazy danych"""
        try:
            current_version = self.get_database_version(db_name)
            new_version = current_version + 1
            
            # Wykonaj migrację
            with self.get_connection(db_name) as conn:
                # Rozpocznij transakcję
                conn.execute("BEGIN")
                
                try:
                    # Wykonaj SQL migracji
                    for statement in migration_sql.split(';'):
                        if statement.strip():
                            conn.execute(statement)
                    
                    # Zapisz migrację w metadanych
                    metadata_path = os.path.join(self.db_directory, "_metadata.db")
                    with sqlite3.connect(metadata_path) as meta_conn:
                        meta_conn.execute("""
                            INSERT INTO migrations 
                            (db_name, from_version, to_version, migration_sql)
                            VALUES (?, ?, ?, ?)
                        """, (db_name, current_version, new_version, migration_sql))
                        
                        # Aktualizuj wersję bazy
                        meta_conn.execute("""
                            UPDATE database_schemas 
                            SET version = ?, schema_hash = ?, updated_at = ?
                            WHERE db_name = ?
                        """, (new_version, self._calculate_schema_hash(db_name), 
                             datetime.now(), db_name))
                        
                        meta_conn.commit()
                    
                    conn.commit()
                    logger.info(f"Migracja bazy {db_name} z wersji {current_version} do {new_version} zakończona")
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    raise e
                    
        except Exception as e:
            logger.error(f"Błąd migracji bazy {db_name}: {e}")
            return False
    
    def rollback_migration(self, db_name: str, target_version: int) -> bool:
        """Cofa migrację do określonej wersji"""
        current_version = self.get_database_version(db_name)
        
        if target_version >= current_version:
            logger.warning(f"Wersja docelowa {target_version} nie jest starsza od aktualnej {current_version}")
            return False
        
        try:
            # Utwórz backup przed rollback
            backup_name = f"{db_name}_backup_v{current_version}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._create_database_backup(db_name, backup_name)
            
            # Tutaj należy zaimplementować logikę rollback
            # Ze względu na ograniczenia SQLite, najlepszym sposobem jest
            # odtworzenie bazy z backupu lub reimport danych
            
            logger.info(f"Rollback bazy {db_name} do wersji {target_version}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd rollback bazy {db_name}: {e}")
            return False
    
    def _create_database_backup(self, db_name: str, backup_name: str):
        """Tworzy pełny backup bazy danych"""
        source_path = os.path.join(self.db_directory, f"{db_name}.db")
        backup_path = os.path.join(self.db_directory, f"{backup_name}.db")
        
        import shutil
        shutil.copy2(source_path, backup_path)
        logger.info(f"Utworzono backup bazy {db_name} jako {backup_name}")
    
    def sync_databases(self, source_db: str, target_db: str, tables: List[str] = None) -> bool:
        """Synchronizuje dane między bazami danych"""
        try:
            with self.get_connection(source_db) as source_conn:
                with self.get_connection(target_db) as target_conn:
                    
                    if not tables:
                        # Pobierz wszystkie tabele z bazy źródłowej
                        cursor = source_conn.execute("""
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name NOT LIKE 'sqlite_%'
                        """)
                        tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        # Pobierz strukturę tabeli
                        cursor = source_conn.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
                        create_sql = cursor.fetchone()
                        
                        if create_sql:
                            # Utwórz tabelę w bazie docelowej
                            target_conn.execute(create_sql[0])
                            
                            # Skopiuj dane
                            cursor = source_conn.execute(f"SELECT * FROM {table}")
                            rows = cursor.fetchall()
                            
                            if rows:
                                placeholders = ",".join(["?" for _ in rows[0]])
                                target_conn.executemany(
                                    f"INSERT OR REPLACE INTO {table} VALUES ({placeholders})", 
                                    rows
                                )
                    
                    target_conn.commit()
                    logger.info(f"Synchronizacja z {source_db} do {target_db} zakończona")
                    return True
                    
        except Exception as e:
            logger.error(f"Błąd synchronizacji baz {source_db} -> {target_db}: {e}")
            return False
    
    def get_database_info(self, db_name: str) -> Dict[str, Any]:
        """Pobiera informacje o bazie danych"""
        try:
            info = {
                "name": db_name,
                "version": self.get_database_version(db_name),
                "tables": [],
                "size": 0
            }
            
            db_path = os.path.join(self.db_directory, f"{db_name}.db")
            if os.path.exists(db_path):
                info["size"] = os.path.getsize(db_path)
            
            with self.get_connection(db_name) as conn:
                cursor = conn.execute("""
                    SELECT name, sql FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    ORDER BY name
                """)
                
                for row in cursor.fetchall():
                    table_name = row[0]
                    
                    # Pobierz liczbę rekordów
                    count_cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    record_count = count_cursor.fetchone()[0]
                    
                    info["tables"].append({
                        "name": table_name,
                        "records": record_count,
                        "sql": row[1]
                    })
            
            return info
            
        except Exception as e:
            logger.error(f"Błąd pobierania informacji o bazie {db_name}: {e}")
            return {}
    
    def list_databases(self) -> List[str]:
        """Zwraca listę wszystkich baz danych"""
        try:
            db_files = [f for f in os.listdir(self.db_directory) 
                       if f.endswith('.db') and not f.startswith('_')]
            return [f[:-3] for f in db_files]  # Usuń rozszerzenie .db
        except:
            return []
    
    def optimize_database(self, db_name: str) -> bool:
        """Optymalizuje bazę danych (VACUUM, ANALYZE)"""
        try:
            with self.get_connection(db_name) as conn:
                conn.execute("VACUUM")
                conn.execute("ANALYZE")
                conn.commit()
            
            logger.info(f"Optymalizacja bazy {db_name} zakończona")
            return True
            
        except Exception as e:
            logger.error(f"Błąd optymalizacji bazy {db_name}: {e}")
            return False
    
    def export_database(self, db_name: str, format: str = "sql") -> str:
        """Eksportuje bazę danych do pliku"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "sql":
                export_path = os.path.join(self.db_directory, f"{db_name}_export_{timestamp}.sql")
                
                with self.get_connection(db_name) as conn:
                    with open(export_path, 'w', encoding='utf-8') as f:
                        for line in conn.iterdump():
                            f.write(f"{line}\n")
                
                logger.info(f"Eksport bazy {db_name} do {export_path}")
                return export_path
                
            elif format.lower() == "json":
                export_path = os.path.join(self.db_directory, f"{db_name}_export_{timestamp}.json")
                
                export_data = {}
                with self.get_connection(db_name) as conn:
                    cursor = conn.execute("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name NOT LIKE 'sqlite_%'
                    """)
                    
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    for table in tables:
                        cursor = conn.execute(f"SELECT * FROM {table}")
                        columns = [description[0] for description in cursor.description]
                        rows = cursor.fetchall()
                        
                        export_data[table] = {
                            "columns": columns,
                            "data": [dict(zip(columns, row)) for row in rows]
                        }
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                logger.info(f"Eksport bazy {db_name} do {export_path}")
                return export_path
                
        except Exception as e:
            logger.error(f"Błąd eksportu bazy {db_name}: {e}")
            return ""
    
    def close_all_connections(self):
        """Zamyka wszystkie połączenia"""
        with self.lock:
            for conn in self.connections.values():
                try:
                    conn.close()
                except:
                    pass
            self.connections.clear()
            logger.info("Zamknięto wszystkie połączenia z bazami danych")

# Singleton instance dla globalnego dostępu
_db_manager_instance = None

def get_db_manager() -> DatabaseManager:
    """Zwraca singleton instance menedżera baz danych"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
