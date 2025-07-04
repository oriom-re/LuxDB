"""
🗃️ ModuleMetadataManager - Manager metadanych modułów w bazie SQL

Przechowuje i zarządza metadanymi modułów, umożliwia wyszukiwanie
i pobieranie modułów na podstawie kryteriów.
"""

import asyncio
import json
import sqlite3
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..core.lux_module import LuxModule, ModuleType, ModuleFormType, ModuleStability
from ..core.bus import FederationBus, FederationMessage


class ModuleMetadataManager(LuxModule):
    """
    Manager metadanych modułów - przechowuje informacje o modułach w bazie SQL
    """

    def __init__(self, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="module_metadata_manager",
            module_type=ModuleType.CORE,
            version="1.0.0",
            config=config,
            bus=bus,
            creator_id="federation_system",
            form_type=ModuleFormType.FILE
        )

        self.db_path = config.get('db_path', 'db/module_metadata.db')
        self.connection: Optional[sqlite3.Connection] = None

        # Rejestracja w bus'ie
        self.bus.register_module("module_metadata_manager", self)

    async def initialize(self) -> bool:
        """Inicjalizuje manager metadanych"""
        try:
            # Połącz z bazą
            loop = asyncio.get_event_loop()
            self.connection = await loop.run_in_executor(
                None, 
                lambda: sqlite3.connect(self.db_path, check_same_thread=False)
            )
            self.connection.row_factory = sqlite3.Row

            # Utwórz tabele
            await self._create_tables()

            # Rejestruj komendy
            await self._register_commands()

            self.is_active = True
            print(f"🗃️ ModuleMetadataManager zainicjalizowany")
            return True

        except Exception as e:
            print(f"❌ Błąd inicjalizacji ModuleMetadataManager: {e}")
            return False

    async def shutdown(self) -> bool:
        """Wyłącza manager"""
        try:
            if self.connection:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.connection.close)
                self.connection = None

            self.is_active = False
            print("🗃️ ModuleMetadataManager wyłączony")
            return True

        except Exception as e:
            print(f"❌ Błąd wyłączania ModuleMetadataManager: {e}")
            return False

    async def _create_tables(self):
        """Tworzy tabele metadanych"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._execute_schema_creation)

    def _execute_schema_creation(self):
        """Wykonuje tworzenie schematu"""
        cursor = self.connection.cursor()

        # Tabela metadanych modułów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_metadata (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                module_type TEXT NOT NULL,
                form_type TEXT NOT NULL,
                version_major INTEGER,
                version_minor INTEGER,
                version_patch INTEGER,
                version_stability TEXT,
                version_build TEXT,
                description TEXT,
                author TEXT,
                license TEXT,
                dependencies TEXT,  -- JSON array
                capabilities TEXT,  -- JSON array
                config_schema TEXT, -- JSON
                binary_data TEXT,   -- base64 encoded dla BINARY modules
                created_at TEXT,
                updated_at TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                file_path TEXT,     -- ścieżka dla FILE modules
                class_name TEXT,
                module_path TEXT,
                genetic_record TEXT -- JSON
            )
        ''')

        # Indeksy dla wydajności
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_module_name ON module_metadata(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_module_type ON module_metadata(module_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_form_type ON module_metadata(form_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_version ON module_metadata(version_major, version_minor, version_patch)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_stability ON module_metadata(version_stability)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_count ON module_metadata(usage_count)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_last_used ON module_metadata(last_used)')

        # Tabela zależności modułów
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_dependencies (
                module_uuid TEXT,
                depends_on TEXT,
                dependency_type TEXT DEFAULT 'required',
                FOREIGN KEY (module_uuid) REFERENCES module_metadata(uuid)
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dependency_module ON module_dependencies(module_uuid)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dependency_depends ON module_dependencies(depends_on)')

        self.connection.commit()

    async def store_module_metadata(self, module: LuxModule, binary_data: Optional[str] = None, 
                                   file_path: Optional[str] = None) -> bool:
        """Przechowuje metadane modułu w bazie"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_store_metadata,
                module, binary_data, file_path
            )

            if success:
                print(f"🗃️ Zapisano metadane modułu: {module.name}")

            return success

        except Exception as e:
            print(f"❌ Błąd zapisywania metadanych modułu {module.name}: {e}")
            return False

    def _execute_store_metadata(self, module: LuxModule, binary_data: Optional[str], 
                               file_path: Optional[str]) -> bool:
        """Wykonuje zapis metadanych"""
        cursor = self.connection.cursor()

        # Przygotuj dane
        dependencies_json = json.dumps(module.manifest.dependencies)
        capabilities_json = json.dumps(module.manifest.capabilities)
        config_schema_json = json.dumps(module.manifest.config_schema) if module.manifest.config_schema else None
        genetic_record_json = json.dumps(module.genetic_record.to_dict())

        # Wstaw lub zaktualizuj
        cursor.execute('''
            INSERT OR REPLACE INTO module_metadata (
                uuid, name, module_type, form_type,
                version_major, version_minor, version_patch, version_stability, version_build,
                description, author, license,
                dependencies, capabilities, config_schema,
                binary_data, created_at, updated_at,
                usage_count, last_used,
                file_path, class_name, module_path,
                genetic_record
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            module.uuid,
            module.name,
            module.module_type.value,
            module.form_type.value,
            module.version.major,
            module.version.minor,
            module.version.patch,
            module.version.stability.value,
            module.version.build,
            module.manifest.description,
            module.manifest.author,
            module.manifest.license,
            dependencies_json,
            capabilities_json,
            config_schema_json,
            binary_data,
            module.created_at.isoformat(),
            datetime.now().isoformat(),
            module.usage_count,
            module.last_used.isoformat() if module.last_used else None,
            file_path,
            module.__class__.__name__,
            module.__class__.__module__,
            genetic_record_json
        ))

        # Zapisz zależności
        cursor.execute('DELETE FROM module_dependencies WHERE module_uuid = ?', (module.uuid,))
        for dependency in module.manifest.dependencies:
            cursor.execute('''
                INSERT INTO module_dependencies (module_uuid, depends_on, dependency_type)
                VALUES (?, ?, ?)
            ''', (module.uuid, dependency, 'required'))

        self.connection.commit()
        return True

    async def search_modules(self, **criteria) -> List[Dict[str, Any]]:
        """Wyszukuje moduły na podstawie kryteriów"""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._execute_search,
                criteria
            )

            return results

        except Exception as e:
            print(f"❌ Błąd wyszukiwania modułów: {e}")
            return []

    def _execute_search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Wykonuje wyszukiwanie"""
        cursor = self.connection.cursor()

        # Buduj zapytanie
        query = "SELECT * FROM module_metadata"
        params = []
        where_clauses = []

        # Filtruj według kryteriów
        if 'name' in criteria:
            where_clauses.append("name = ?")
            params.append(criteria['name'])

        if 'module_type' in criteria:
            where_clauses.append("module_type = ?")
            params.append(criteria['module_type'])

        if 'form_type' in criteria:
            where_clauses.append("form_type = ?")
            params.append(criteria['form_type'])

        if 'version_stability' in criteria:
            where_clauses.append("version_stability = ?")
            params.append(criteria['version_stability'])

        if 'capability' in criteria:
            where_clauses.append("capabilities LIKE ?")
            params.append(f'%"{criteria["capability"]}"%')

        if 'author' in criteria:
            where_clauses.append("author = ?")
            params.append(criteria['author'])

        if 'min_usage_count' in criteria:
            where_clauses.append("usage_count >= ?")
            params.append(criteria['min_usage_count'])

        # Dodaj WHERE
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        # Sortowanie
        if 'order_by' in criteria:
            query += f" ORDER BY {criteria['order_by']}"
        else:
            query += " ORDER BY usage_count DESC, updated_at DESC"

        # Limit
        if 'limit' in criteria:
            query += f" LIMIT {criteria['limit']}"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Konwertuj do słowników
        results = []
        for row in rows:
            module_data = dict(row)

            # Parsuj JSON pola
            if module_data['dependencies']:
                module_data['dependencies'] = json.loads(module_data['dependencies'])
            if module_data['capabilities']:
                module_data['capabilities'] = json.loads(module_data['capabilities'])
            if module_data['config_schema']:
                module_data['config_schema'] = json.loads(module_data['config_schema'])
            if module_data['genetic_record']:
                module_data['genetic_record'] = json.loads(module_data['genetic_record'])

            results.append(module_data)

        return results

    async def get_module_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Pobiera moduł po UUID"""
        results = await self.search_modules(uuid=uuid)
        return results[0] if results else None

    async def get_binary_module_data(self, uuid: str) -> Optional[str]:
        """Pobiera dane binarne modułu"""
        try:
            loop = asyncio.get_event_loop()
            binary_data = await loop.run_in_executor(
                None,
                self._execute_get_binary_data,
                uuid
            )

            return binary_data

        except Exception as e:
            print(f"❌ Błąd pobierania danych binarnych modułu {uuid}: {e}")
            return None

    def _execute_get_binary_data(self, uuid: str) -> Optional[str]:
        """Wykonuje pobieranie danych binarnych"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT binary_data FROM module_metadata WHERE uuid = ?", (uuid,))
        row = cursor.fetchone()

        return row['binary_data'] if row else None

    async def update_usage_stats(self, uuid: str) -> bool:
        """Aktualizuje statystyki użycia modułu"""
        try:
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._execute_update_usage,
                uuid
            )

            return success

        except Exception as e:
            print(f"❌ Błąd aktualizacji statystyk użycia {uuid}: {e}")
            return False

    def _execute_update_usage(self, uuid: str) -> bool:
        """Wykonuje aktualizację statystyk"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE module_metadata 
            SET usage_count = usage_count + 1, last_used = ?
            WHERE uuid = ?
        ''', (datetime.now().isoformat(), uuid))

        self.connection.commit()
        return cursor.rowcount > 0

    async def cleanup_old_modules(self, max_age_days: int = 30) -> int:
        """Usuwa stare, nieużywane moduły"""
        try:
            loop = asyncio.get_event_loop()
            removed_count = await loop.run_in_executor(
                None,
                self._execute_cleanup,
                max_age_days
            )

            if removed_count > 0:
                print(f"🧹 Usunięto {removed_count} starych modułów")

            return removed_count

        except Exception as e:
            print(f"❌ Błąd czyszczenia starych modułów: {e}")
            return 0

    def _execute_cleanup(self, max_age_days: int) -> int:
        """Wykonuje czyszczenie"""
        cursor = self.connection.cursor()

        # Usuń moduły binarne starsze niż max_age_days i nieużywane
        cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()

        cursor.execute('''
            DELETE FROM module_metadata 
            WHERE form_type = 'binary' 
            AND (last_used IS NULL OR last_used < ?)
            AND updated_at < ?
        ''', (cutoff_date, cutoff_date))

        removed_count = cursor.rowcount
        self.connection.commit()

        return removed_count

    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'store_module': self.store_module_metadata,
            'search_modules': self.search_modules,
            'get_module': self.get_module_by_uuid,
            'get_binary_data': self.get_binary_module_data,
            'update_usage': self.update_usage_stats,
            'cleanup_old': self.cleanup_old_modules,
            'get_status': self.get_status
        }

        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"module_metadata.{cmd_name}", cmd_func)

    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data

        if command == 'store_module':
            return await self.store_module_metadata(
                data.get('module'),
                data.get('binary_data'),
                data.get('file_path')
            )
        elif command == 'search_modules':
            return await self.search_modules(**data.get('criteria', {}))
        elif command == 'get_module':
            return await self.get_module_by_uuid(data.get('uuid'))
        elif command == 'get_binary_data':
            return await self.get_binary_module_data(data.get('uuid'))
        elif command == 'update_usage':
            return await self.update_usage_stats(data.get('uuid'))
        elif command == 'cleanup_old':
            return await self.cleanup_old_modules(data.get('max_age_days', 30))
        elif command == 'get_status':
            return await self.get_status()
        else:
            return {'error': f'Nieznana komenda: {command}'}

    async def start(self) -> bool:
        """Uruchamia Module Metadata Manager"""
        if not await super().start():
            return False

        print("📊 Module Metadata Manager started")
        return True

    async def heartbeat(self) -> bool:
        """Puls życia Module Metadata Manager"""
        if not await super().heartbeat():
            return False

        # Można tutaj wykonać maintenance metadanych
        return True

from datetime import timedelta