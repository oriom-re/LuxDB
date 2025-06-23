
"""
Główny menedżer baz danych SQLAlchemy dla systemu LuxDB
"""

import os
import json
import hashlib
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Type, Union
from contextlib import contextmanager
import threading

from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .config import (
    Base, DatabaseConfig, DatabaseType, ConnectionPool,
    DEFAULT_CONFIGS
)
from .models import (
    User, UserSession, Log, DatabaseSchema, Migration, TableDefinition, LuxBase,
    SYSTEM_MODELS
)
# QueryBuilder usunięty - używamy czystego SQLAlchemy

# Konfiguracja logowania
from .utils.logging_utils import get_db_logger
logging.basicConfig(level=logging.INFO)
logger = get_db_logger()

class DatabaseError(Exception):
    """Wyjątek dla błędów bazy danych"""
    pass

class MigrationError(Exception):
    """Wyjątek dla błędów migracji"""
    pass

class DatabaseManager:
    """
    Główny menedżer baz danych SQLAlchemy dla systemu LuxDB
    Obsługuje wiele instancji baz, wersjonowanie, migracje i replikację
    """
    
    def __init__(self, db_directory: str = "db"):
        self.db_directory = db_directory
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.configs: Dict[str, DatabaseConfig] = {}
        self.lock = threading.RLock()
        
        # Zapewnij istnienie katalogu
        os.makedirs(db_directory, exist_ok=True)
        
        # Inicjalizuj główną bazę metadanych
        self._init_metadata_db()
    
    def _init_metadata_db(self):
        """Inicjalizuje bazę metadanych do zarządzania schematami i migracjami"""
        metadata_path = os.path.join(self.db_directory, "_metadata.db")
        connection_string = f"sqlite:///{metadata_path}"
        
        self.metadata_pool = ConnectionPool(connection_string, max_connections=5)
        
        # Tworzy tabele metadanych
        metadata_base = type('MetadataBase', (object,), {
            'metadata': MetaData()
        })
        
        # Dodaj tabele metadanych do oddzielnej bazy
        for table in [DatabaseSchema.__table__, Migration.__table__, TableDefinition.__table__]:
            table.tometadata(metadata_base.metadata)
        
        metadata_base.metadata.create_all(bind=self.metadata_pool.engine)
        
        logger.info("Zainicjalizowano bazę metadanych SQLAlchemy")
    
    @contextmanager
    def get_session(self, db_name: str):
        """Context manager dla bezpiecznego dostępu do sesji SQLAlchemy"""
        if db_name not in self.connection_pools:
            raise DatabaseError(f"Baza danych {db_name} nie istnieje")
        
        session = self.connection_pools[db_name].get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Błąd sesji z bazą {db_name}: {e}")
            raise DatabaseError(f"Błąd sesji z bazą {db_name}: {e}")
        finally:
            session.close()
    
    @contextmanager
    def get_metadata_session(self):
        """Context manager dla sesji metadanych"""
        session = self.metadata_pool.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Błąd sesji metadanych: {e}")
            raise DatabaseError(f"Błąd sesji metadanych: {e}")
        finally:
            session.close()
    
    def create_database(self, db_name: str, config: DatabaseConfig = None) -> bool:
        """Tworzy nową bazę danych"""
        try:
            if not config:
                config = DatabaseConfig(
                    name=db_name,
                    type=DatabaseType.SQLITE,
                    connection_string=f"sqlite:///{os.path.join(self.db_directory, db_name)}.db"
                )
            
            # Utwórz pool połączeń
            pool = ConnectionPool(config.connection_string, config.max_connections)
            
            # Utwórz tabele systemu
            pool.create_tables(Base)
            
            # Zapisz konfigurację
            self.connection_pools[db_name] = pool
            self.configs[db_name] = config
            
            # Zarejestruj w metadanych
            self._register_database(db_name, config.version)
            
            logger.info(f"Utworzono bazę danych SQLAlchemy: {db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia bazy {db_name}: {e}")
            return False
            
    def add_database(self, config: DatabaseConfig) -> bool:
        """Dodaje nową bazę danych na podstawie konfiguracji"""
        return self.create_database(config.name, config)

    def create_tables(self, db_name: str, models: List[Type[LuxBase]] = None) -> bool:
        """Tworzy tabele w bazie danych na podstawie modeli"""
        try:
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            pool = self.connection_pools[db_name]
            
            if not models:
                models = [User, UserSession, Log]
            
            for model in models:
                model.__table__.create(bind=pool.engine, checkfirst=True)
                
                # Zapisz definicję tabeli
                self._save_table_definition(db_name, model.__tablename__, str(model.__table__))
            
            logger.info(f"Utworzono tabele w bazie {db_name}")
            return True
        except Exception as e:
            logger.error(f"Błąd tworzenia tabel w bazie {db_name}: {e}")

    def create_all_tables(self) -> bool:
        """Tworzy wszystkie tabele w wszystkich bazach danych"""
        try:
            for db_name in self.connection_pools.keys():
                self.create_tables(db_name)
            
            logger.info("Utworzono wszystkie tabele w bazach danych")
            return True
        except Exception as e:
            logger.error(f"Błąd tworzenia wszystkich tabel: {e}")
    
    def _register_database(self, db_name: str, version: int = 1):
        """Rejestruje bazę w systemie metadanych"""
        try:
            with self.get_metadata_session() as session:
                schema_hash = self._calculate_schema_hash(db_name)
                
                db_schema = session.query(DatabaseSchema).filter_by(db_name=db_name).first()
                if db_schema:
                    db_schema.version = version
                    db_schema.schema_hash = schema_hash
                    db_schema.updated_at = datetime.now()
                else:
                    db_schema = DatabaseSchema(
                        db_name=db_name,
                        version=version,
                        schema_hash=schema_hash
                    )
                    session.add(db_schema)
                
                logger.info(f"Zarejestrowano bazę {db_name} w metadanych")
        except Exception as e:
            logger.error(f"Błąd rejestracji bazy {db_name}: {e}")
    
    def _calculate_schema_hash(self, db_name: str) -> str:
        """Oblicza hash schematu bazy danych"""
        try:
            if db_name not in self.connection_pools:
                return ""
            
            pool = self.connection_pools[db_name]
            inspector = inspect(pool.engine)
            tables = inspector.get_table_names()
            
            schema_info = []
            for table in sorted(tables):
                columns = inspector.get_columns(table)
                schema_info.append(f"{table}:{sorted([col['name'] + col['type'].__class__.__name__ for col in columns])}")
            
            schema_str = '|'.join(schema_info)
            return hashlib.md5(schema_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Błąd obliczania hash schematu dla {db_name}: {e}")
            return ""
    
    def create_table_from_model(self, db_name: str, model_class: Type[Base]) -> bool:
        """Tworzy tabelę na podstawie modelu SQLAlchemy"""
        try:
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            pool = self.connection_pools[db_name]
            model_class.__table__.create(bind=pool.engine, checkfirst=True)
            
            # Zapisz definicję tabeli
            self._save_table_definition(db_name, model_class.__tablename__, str(model_class.__table__))
            
            logger.info(f"Utworzono tabelę {model_class.__tablename__} w bazie {db_name}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd tworzenia tabeli {model_class.__tablename__} w bazie {db_name}: {e}")
            return False
    
    def _save_table_definition(self, db_name: str, table_name: str, definition: str):
        """Zapisuje definicję tabeli w metadanych"""
        try:
            version = self.get_database_version(db_name)
            
            with self.get_metadata_session() as session:
                table_def = TableDefinition(
                    db_name=db_name,
                    table_name=table_name,
                    version=version,
                    definition=definition
                )
                session.merge(table_def)
        except Exception as e:
            logger.error(f"Błąd zapisywania definicji tabeli {table_name}: {e}")
    
    def insert_data(self, 
                    session,
                    db_name: str, 
                    model_class: Type[Base], 
                    data: Dict[str, Any]) -> bool:
        """Wstawia dane do tabeli"""
        try:
            instance = model_class(**data)
            session.add(instance)
            session.commit()
            logger.info(f"Wstawiono dane do {model_class.__tablename__}")
            return instance
            
        except Exception as e:
            logger.error(f"Błąd wstawiania danych do {model_class.__tablename__} w bazie {db_name}: {e}")
            return False
    
    def insert_batch(self, 
                     session,
                     db_name: str, 
                     model_class: Type[Base], 
                     data_list: List[Dict[str, Any]]) -> bool:
        """Wstawia wiele rekordów jednocześnie"""
        if not data_list:
            logger.warning(f"Pusta lista danych do wstawienia do {model_class.__tablename__}")
            return True
            
        try:
            instances = [model_class(**data) for data in data_list]
            session.add_all(instances)
            session.commit()
            logger.info(f"Wstawiono {len(data_list)} rekordów do {model_class.__tablename__}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd wstawiania batch do {model_class.__tablename__} w bazie {db_name}: {e}")
            return False
    
    def select_data(self, session, db_name: str, model_class: Type[Base], filters: Dict[str, Any] = None,
                   order_by: str = None, limit: int = None) -> List[Any]:
        """Pobiera dane z tabeli"""
        try:
            query = session.query(model_class)
            
            if filters:
                for key, value in filters.items():
                    query = query.filter(getattr(model_class, key) == value)
            
            if order_by:
                query = query.order_by(getattr(model_class, order_by))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
                
        except Exception as e:
            logger.error(f"Błąd pobierania danych z {model_class.__tablename__} w bazie {db_name}: {e}")
            return []
    
    # QueryBuilder usunięty - używamy bezpośrednio session.query() jak w duchowych praktykach
    
    def execute_raw_sql(self, db_name: str, sql: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Wykonuje surowe zapytanie SQL"""
        try:
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            pool = self.connection_pools[db_name]
            with pool.engine.connect() as conn:
                result = conn.execute(text(sql), params or {})
                
                if sql.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    return [dict(row._mapping) for row in rows]
                else:
                    conn.commit()
                    return [{"affected_rows": result.rowcount}]
                    
        except Exception as e:
            logger.error(f"Błąd wykonywania SQL w bazie {db_name}: {e}")
            return []
    
    def get_database_version(self, db_name: str) -> int:
        """Pobiera aktualną wersję bazy danych"""
        try:
            with self.get_metadata_session() as session:
                db_schema = session.query(DatabaseSchema).filter_by(db_name=db_name).first()
                return db_schema.version if db_schema else 1
        except Exception as e:
            logger.error(f"Błąd pobierania wersji bazy {db_name}: {e}")
            return 1
    
    def create_migration(self, db_name: str, migration_sql: str, description: str = "") -> bool:
        """Tworzy nową migrację bazy danych"""
        try:
            current_version = self.get_database_version(db_name)
            new_version = current_version + 1
            
            # Wykonaj migrację
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            pool = self.connection_pools[db_name]
            
            with pool.engine.begin() as conn:
                # Wykonaj SQL migracji
                for statement in migration_sql.split(';'):
                    if statement.strip():
                        conn.execute(text(statement))
                
                # Zapisz migrację w metadanych
                with self.get_metadata_session() as meta_session:
                    migration = Migration(
                        db_name=db_name,
                        from_version=current_version,
                        to_version=new_version,
                        migration_sql=migration_sql
                    )
                    meta_session.add(migration)
                    
                    # Aktualizuj wersję bazy
                    db_schema = meta_session.query(DatabaseSchema).filter_by(db_name=db_name).first()
                    if db_schema:
                        db_schema.version = new_version
                        db_schema.schema_hash = self._calculate_schema_hash(db_name)
                        db_schema.updated_at = datetime.now()
                
                logger.info(f"Migracja bazy {db_name} z wersji {current_version} do {new_version} zakończona")
                return True
                
        except Exception as e:
            logger.error(f"Błąd migracji bazy {db_name}: {e}")
            return False
    
    def sync_databases(self, source_db: str, target_db: str, models: List[Type[Base]] = None) -> bool:
        """Synchronizuje dane między bazami danych"""
        try:
            if source_db not in self.connection_pools or target_db not in self.connection_pools:
                raise DatabaseError("Jedna lub obie bazy danych nie istnieją")
            
            if not models:
                models = [User, UserSession, Log]
            
            for model in models:
                # Pobierz dane z bazy źródłowej
                with self.get_session(source_db) as source_session:
                    source_data = self.select_data(source_session, source_db, model)
                    
                    # Usuń istniejące dane z bazy docelowej i wstaw nowe
                    with self.get_session(target_db) as target_session:
                        target_session.query(model).delete()
                        
                        # Wstaw dane do bazy docelowej
                        if source_data:
                            data_dicts = []
                            for item in source_data:
                                data_dict = {}
                                for column in model.__table__.columns:
                                    data_dict[column.name] = getattr(item, column.name)
                                data_dicts.append(data_dict)
                            
                            self.insert_batch(target_session, target_db, model, data_dicts)
            
            logger.info(f"Synchronizacja z {source_db} do {target_db} zakończona")
            return True
            
        except Exception as e:
            logger.error(f"Błąd synchronizacji baz {source_db} -> {target_db}: {e}")
            return False
    
    def get_database_info(self, db_name: str) -> Dict[str, Any]:
        """Pobiera informacje o bazie danych"""
        try:
            if db_name not in self.connection_pools:
                raise ConnectionError(f"Baza danych {db_name} nie istnieje", 
                                     service_name="database",
                                     context={"db_name": db_name})

            pool = self.connection_pools[db_name]
            inspector = inspect(pool.engine)

            info = {
                "name": db_name,
                "version": self.get_database_version(db_name),
                "tables": [],
                "size": 0
            }

            # Rozmiar pliku bazy (tylko dla SQLite)
            if self.configs[db_name].type == DatabaseType.SQLITE:
                db_path = self.configs[db_name].connection_string.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    info["size"] = os.path.getsize(db_path)

            # Informacje o tabelach
            tables = inspector.get_table_names()
            for table_name in tables:
                with self.get_session(db_name) as session:
                    result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    record_count = result.scalar()

                info["tables"].append({
                    "name": table_name,
                    "records": record_count,
                    "columns": [col['name'] for col in inspector.get_columns(table_name)]
                })
    
            return info

        except Exception as e:
            logger.error(f"Błąd pobierania informacji o bazie {db_name}: {e}")
            return {}
    
    def list_databases(self) -> List[str]:
        """Zwraca listę wszystkich baz danych"""
        return list(self.connection_pools.keys())
    
    def optimize_database(self, db_name: str) -> bool:
        """Optymalizuje bazę danych"""
        try:
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            pool = self.connection_pools[db_name]
            
            # Optymalizacja dla SQLite
            if self.configs[db_name].type == DatabaseType.SQLITE:
                with pool.engine.connect() as conn:
                    conn.execute(text("VACUUM"))
                    conn.execute(text("ANALYZE"))
                    conn.commit()
            
            logger.info(f"Optymalizacja bazy {db_name} zakończona")
            return True
            
        except Exception as e:
            logger.error(f"Błąd optymalizacji bazy {db_name}: {e}")
            return False
    
    def export_database(self, db_name: str, format: str = "json") -> str:
        """Eksportuje bazę danych do pliku"""
        try:
            if db_name not in self.connection_pools:
                raise DatabaseError(f"Baza danych {db_name} nie istnieje")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join(self.db_directory, f"{db_name}_export_{timestamp}.{format}")
            
            if format.lower() == "json":
                export_data = {}
                
                for model_name, model_class in SYSTEM_MODELS.items():
                    try:
                        with self.get_session(db_name) as session:
                            data = self.select_data(session, db_name, model_class)
                            export_data[model_name] = []
                        
                        for item in data:
                            item_dict = {}
                            for column in model_class.__table__.columns:
                                value = getattr(item, column.name)
                                if isinstance(value, datetime):
                                    value = value.isoformat()
                                item_dict[column.name] = value
                            export_data[model_name].append(item_dict)
                    except:
                        continue
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                logger.info(f"Eksport bazy {db_name} do {export_path}")
                return export_path
                
        except Exception as e:
            logger.error(f"Błąd eksportu bazy {db_name}: {e}")
            return ""
    
    def close_all(self):
        """Zamyka wszystkie połączenia"""
        with self.lock:
            for pool in self.connection_pools.values():
                try:
                    pool.close()
                except:
                    pass
            
            try:
                self.metadata_pool.close()
            except:
                pass
            
            self.connection_pools.clear()
            logger.info("Zamknięto wszystkie połączenia SQLAlchemy")

# Singleton instance dla globalnego dostępu
_db_manager_instance = None

def get_db_manager() -> DatabaseManager:
    """Zwraca singleton instance menedżera baz danych"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
