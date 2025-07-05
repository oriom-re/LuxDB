"""
🗄️ DatabaseManager - Zarządca Baz Danych w Pakiecie Realms

Centralny moduł zarządzający wszystkimi bazami danych w systemie Federacji
"""

import asyncio
import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from ...core.bus import FederationBus, FederationMessage
from ...core.lux_module import LuxModule, ModuleType, ModuleVersion


class DatabaseManager(LuxModule):
    """
    Zarządca baz danych - tworzy, zarządza i monitoruje bazy danych
    """

    def __init__(self, name: str, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="database_manager",
            module_type=ModuleType.SERVICE,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )

        # Konfiguracja
        self.db_folder = config.get('db_folder', 'db')
        self.max_connections = config.get('max_connections', 100)
        self.pool_size = config.get('pool_size', 10)

        # Stan
        self.databases: Dict[str, sqlite3.Connection] = {}
        self.connection_pool: Dict[str, List[sqlite3.Connection]] = {}

        # Upewnij się że folder db istnieje
        Path(self.db_folder).mkdir(exist_ok=True)

        print(f"🗄️ DatabaseManager zainicjalizowany - folder: {self.db_folder}")

    async def initialize(self) -> bool:
        """Inicjalizuje Database Manager"""
        try:
            # Rejestruj komendy w bus'ie
            await self._register_commands()

            # Utwórz podstawowe bazy danych
            await self._create_system_databases()

            self.is_active = True
            print("🗄️ DatabaseManager zainicjalizowany z sukcesem")
            return True

        except Exception as e:
            print(f"❌ Błąd inicjalizacji DatabaseManager: {e}")
            return False

    async def shutdown(self) -> bool:
        """Wyłącza Database Manager"""
        try:
            # Zamknij wszystkie połączenia
            for db_name, conn in self.databases.items():
                conn.close()
                print(f"🗄️ Zamknięto bazę: {db_name}")

            # Wyczyść pool połączeń
            for db_name, pool in self.connection_pool.items():
                for conn in pool:
                    conn.close()

            self.databases.clear()
            self.connection_pool.clear()
            self.is_active = False

            print("🗄️ DatabaseManager wyłączony")
            return True

        except Exception as e:
            print(f"❌ Błąd wyłączania DatabaseManager: {e}")
            return False

    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'create_database': self._handle_create_database,
            'get_database': self._handle_get_database,
            'list_databases': self._handle_list_databases,
            'execute_query': self._handle_execute_query,
            'get_connection': self._handle_get_connection,
            'get_status': self._handle_get_status,
            'subscribe_to_database': self._handle_subscribe_to_database,
            'get_available_databases': self._handle_get_available_databases
        }

        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"database_manager.{cmd_name}", cmd_func)

    async def _create_system_databases(self):
        """Tworzy podstawowe bazy systemowe"""
        system_dbs = [
            'system_state.db',
            'federation_memory.db',
            'realm_main.db'
        ]

        for db_name in system_dbs:
            await self.create_database(db_name)

    async def create_database(self, db_name: str) -> bool:
        """Tworzy nową bazę danych"""
        try:
            db_path = os.path.join(self.db_folder, db_name)

            # Sprawdź czy baza już istnieje
            if db_name in self.databases:
                print(f"🗄️ Baza '{db_name}' już istnieje")
                return True

            # Utwórz połączenie
            connection = sqlite3.connect(
                db_path,
                check_same_thread=False,
                timeout=30.0
            )
            connection.row_factory = sqlite3.Row

            # Dodaj do rejestru
            self.databases[db_name] = connection

            # Utwórz podstawowe tabele systemowe
            await self._create_system_tables(connection, db_name)

            # 🚀 PUBLIKUJ BAZĘ W BUS'IE
            await self._publish_database_to_bus(db_name, db_path)

            print(f"✅ Baza '{db_name}' utworzona i opublikowana: {db_path}")
            return True

        except Exception as e:
            print(f"❌ Błąd tworzenia bazy '{db_name}': {e}")
            return False

    async def _create_system_tables(self, connection: sqlite3.Connection, db_name: str):
        """Tworzy podstawowe tabele systemowe"""
        cursor = connection.cursor()

        if 'system_state' in db_name:
            # Tabela modułów systemowych
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabela konfiguracji systemu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        elif 'federation_memory' in db_name:
            # Tabela pamięci federacji
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS federation_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        elif 'realm_main' in db_name:
            # Tabela głównych danych realm
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS beings (
                    soul_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

        connection.commit()

    async def _publish_database_to_bus(self, db_name: str, db_path: str):
        """Publikuje bazę danych w bus'ie dla innych modułów"""
        try:
            # Wyślij broadcast że baza jest dostępna
            await self.bus.broadcast(
                from_module="database_manager",
                message_type="database_available",
                data={
                    'db_name': db_name,
                    'db_path': db_path,
                    'manager': 'database_manager',
                    'operations': ['query', 'insert', 'update', 'delete'],
                    'tables': await self._get_database_tables(db_name),
                    'published_at': datetime.now().isoformat()
                }
            )

            print(f"📡 Baza '{db_name}' opublikowana w bus'ie")

        except Exception as e:
            print(f"⚠️ Nie udało się opublikować bazy '{db_name}': {e}")

    async def _get_database_tables(self, db_name: str) -> List[str]:
        """Pobiera listę tabel z bazy danych"""
        try:
            query = "SELECT name FROM sqlite_master WHERE type='table'"
            result = await self.execute_query(db_name, query)
            return [row['name'] for row in result]
        except Exception:
            return []

    async def get_database(self, db_name: str) -> Optional[sqlite3.Connection]:
        """Zwraca połączenie z bazą danych"""
        return self.databases.get(db_name)

    async def execute_query(self, db_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Wykonuje zapytanie SQL"""
        try:
            connection = await self.get_database(db_name)
            if not connection:
                raise ValueError(f"Baza '{db_name}' nie istnieje")

            cursor = connection.cursor()
            cursor.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            else:
                connection.commit()
                return [{'affected_rows': cursor.rowcount}]

        except Exception as e:
            print(f"❌ Błąd wykonania zapytania: {e}")
            raise

    # === HANDLERY KOMEND ===

    async def _handle_create_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler tworzenia bazy"""
        db_name = data.get('db_name')
        if not db_name:
            return {'error': 'Brak nazwy bazy danych'}

        success = await self.create_database(db_name)
        return {'success': success, 'db_name': db_name}

    async def _handle_get_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pobierania bazy"""
        db_name = data.get('db_name')
        connection = await self.get_database(db_name)
        return {'exists': connection is not None, 'db_name': db_name}

    async def _handle_list_databases(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler listowania baz"""
        return {'databases': list(self.databases.keys())}

    async def _handle_execute_query(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler wykonania zapytania"""
        try:
            db_name = data.get('db_name')
            query = data.get('query')
            params = data.get('params', ())

            result = await self.execute_query(db_name, query, params)
            return {'success': True, 'result': result}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def _handle_get_connection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pobierania połączenia"""
        db_name = data.get('db_name')
        connection = await self.get_database(db_name)
        return {'available': connection is not None}

    async def _handle_get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler statusu"""
        return await self.get_status()

    async def _handle_subscribe_to_database(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler subskrypcji bazy danych"""
        module_name = data.get('module_name')
        db_name = data.get('db_name')

        if not module_name or not db_name:
            return {'error': 'Wymagane: module_name i db_name'}

        if db_name not in self.databases:
            return {'error': f'Baza {db_name} nie istnieje'}

        # Wyślij informacje o bazie do subskrybenta
        await self.bus.send_simple(
            from_module="database_manager",
            to_module=module_name,
            message_type="database_access_granted",
            data={
                'db_name': db_name,
                'tables': await self._get_database_tables(db_name),
                'access_level': 'full',
                'operations': ['query', 'insert', 'update', 'delete']
            }
        )

        return {'success': True, 'message': f'Dostęp do bazy {db_name} udzielony'}

    async def _handle_get_available_databases(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler listowania dostępnych baz"""
        available_dbs = []

        for db_name in self.databases.keys():
            tables = await self._get_database_tables(db_name)
            available_dbs.append({
                'name': db_name,
                'tables': tables,
                'table_count': len(tables),
                'path': os.path.join(self.db_folder, db_name)
            })

        return {
            'available_databases': available_dbs,
            'total_count': len(available_dbs)
        }

    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data

        if command == 'create_database':
            return await self._handle_create_database(data)
        elif command == 'get_database':
            return await self._handle_get_database(data)
        elif command == 'list_databases':
            return await self._handle_list_databases(data)
        elif command == 'execute_query':
            return await self._handle_execute_query(data)
        elif command == 'get_status':
            return await self._handle_get_status(data)
        else:
            return {'error': f'Nieznana komenda: {command}'}

    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status Database Manager"""
        return {
            'module_id': self.name,
            'active': self.is_active,
            'databases_count': len(self.databases),
            'databases': list(self.databases.keys()),
            'db_folder': self.db_folder,
            'max_connections': self.max_connections,
            'created_at': self.created_at.isoformat()
        }

    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie Database Manager"""
        return {
            'healthy': self.is_active and len(self.databases) > 0,
            'databases_accessible': len(self.databases),
            'last_check': datetime.now().isoformat()
        }