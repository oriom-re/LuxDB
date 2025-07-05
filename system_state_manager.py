
#!/usr/bin/env python3
"""
🗃️ System State Manager - Zarządca stanu systemu

Zastępuje statyczne pliki konfiguracyjne dynamicznym zarządzaniem stanem
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class SystemModule:
    """Definicja modułu systemowego"""
    name: str
    type: str  # 'core', 'realm', 'service', 'ai'
    status: str  # 'active', 'inactive', 'error', 'pending'
    config: Dict[str, Any]
    dependencies: List[str]
    created_at: str
    last_update: str

@dataclass
class DatabaseDefinition:
    """Definicja bazy danych"""
    name: str
    type: str  # 'sqlite', 'memory', 'postgresql'
    description: str
    config: Dict[str, Any]
    status: str  # 'active', 'inactive', 'error'
    created_at: str
    last_access: str

class SystemStateManager:
    """
    Zarządca stanu systemu - zastępuje statyczne pliki konfiguracyjne
    """
    
    def __init__(self, db_path: str = "db/system_state.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Słowniki cache
        self.modules_cache: Dict[str, SystemModule] = {}
        self.databases_cache: Dict[str, DatabaseDefinition] = {}
        
        # Stan systemu
        self.system_info = {
            'version': '1.0.0',
            'initialized_at': None,
            'last_update': None,
            'total_modules': 0,
            'active_modules': 0,
            'total_databases': 0,
            'active_databases': 0
        }
    
    async def initialize(self) -> bool:
        """Inicjalizuje zarządcę stanu systemu"""
        try:
            # Utwórz bazę danych stanu
            await self._create_system_database()
            
            # Załaduj istniejący stan
            await self._load_system_state()
            
            # Jeśli to pierwsza inicjalizacja, utwórz domyślną konfigurację
            if not self.system_info['initialized_at']:
                await self._create_default_configuration()
            
            self.system_info['last_update'] = datetime.now().isoformat()
            
            print("🗃️ System State Manager zainicjalizowany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji System State Manager: {e}")
            return False
    
    async def _create_system_database(self):
        """Tworzy bazę danych stanu systemu"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela informacji o systemie
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_info (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        
        # Tabela modułów systemu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_modules (
                name TEXT PRIMARY KEY,
                type TEXT,
                status TEXT,
                config TEXT,
                dependencies TEXT,
                created_at TEXT,
                last_update TEXT
            )
        ''')
        
        # Tabela definicji baz danych
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS database_definitions (
                name TEXT PRIMARY KEY,
                type TEXT,
                description TEXT,
                config TEXT,
                status TEXT,
                created_at TEXT,
                last_access TEXT
            )
        ''')
        
        # Tabela logów zmian
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type TEXT,
                target_name TEXT,
                old_value TEXT,
                new_value TEXT,
                timestamp TEXT,
                user_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("🏗️ Baza danych stanu systemu utworzona")
    
    async def _load_system_state(self):
        """Ładuje stan systemu z bazy"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Załaduj informacje o systemie
            cursor.execute("SELECT key, value FROM system_info")
            for key, value in cursor.fetchall():
                try:
                    self.system_info[key] = json.loads(value)
                except:
                    self.system_info[key] = value
            
            # Załaduj moduły
            cursor.execute("SELECT * FROM system_modules")
            for row in cursor.fetchall():
                module = SystemModule(
                    name=row[0],
                    type=row[1],
                    status=row[2],
                    config=json.loads(row[3]),
                    dependencies=json.loads(row[4]),
                    created_at=row[5],
                    last_update=row[6]
                )
                self.modules_cache[row[0]] = module
            
            # Załaduj definicje baz danych
            cursor.execute("SELECT * FROM database_definitions")
            for row in cursor.fetchall():
                database = DatabaseDefinition(
                    name=row[0],
                    type=row[1],
                    description=row[2],
                    config=json.loads(row[3]),
                    status=row[4],
                    created_at=row[5],
                    last_access=row[6]
                )
                self.databases_cache[row[0]] = database
            
            conn.close()
            
            # Aktualizuj statystyki
            self.system_info['total_modules'] = len(self.modules_cache)
            self.system_info['active_modules'] = len([m for m in self.modules_cache.values() if m.status == 'active'])
            self.system_info['total_databases'] = len(self.databases_cache)
            self.system_info['active_databases'] = len([d for d in self.databases_cache.values() if d.status == 'active'])
            
            print(f"📊 Stan systemu załadowany - moduły: {self.system_info['total_modules']}, bazy: {self.system_info['total_databases']}")
            
        except Exception as e:
            print(f"❌ Błąd ładowania stanu systemu: {e}")
    
    async def _create_default_configuration(self):
        """Tworzy domyślną konfigurację systemu"""
        try:
            current_time = datetime.now().isoformat()
            
            # Domyślne moduły systemu
            default_modules = [
                {
                    'name': 'database_manager',
                    'type': 'core',
                    'status': 'active',
                    'config': {
                        'static_startup': True,
                        'priority': 1,
                        'auto_start': True
                    },
                    'dependencies': []
                },
                {
                    'name': 'realm_memory',
                    'type': 'realm',
                    'status': 'active',
                    'config': {
                        'static_startup': True,
                        'max_size': 10000,
                        'auto_cleanup': True
                    },
                    'dependencies': ['database_manager']
                },
                {
                    'name': 'realm_sqlite',
                    'type': 'realm',
                    'status': 'active',
                    'config': {
                        'static_startup': True,
                        'default_path': 'db/',
                        'auto_create': True
                    },
                    'dependencies': ['database_manager']
                },
                {
                    'name': 'federa',
                    'type': 'ai',
                    'status': 'managed',
                    'config': {
                        'static_startup': False,
                        'managed_by': 'database_manager',
                        'auto_start': True
                    },
                    'dependencies': ['database_manager', 'realm_memory']
                }
            ]
            
            # Domyślne bazy danych
            default_databases = [
                {
                    'name': 'system_state',
                    'type': 'sqlite',
                    'description': 'Baza stanu systemu Federacji',
                    'config': {
                        'path': 'db/system_state.db',
                        'auto_create': True,
                        'backup_enabled': True
                    },
                    'status': 'active'
                },
                {
                    'name': 'federation_memory',
                    'type': 'memory',
                    'description': 'Pamięć operacyjna Federacji',
                    'config': {
                        'max_size': 10000,
                        'auto_cleanup': True,
                        'cleanup_interval': 3600
                    },
                    'status': 'active'
                },
                {
                    'name': 'realm_main',
                    'type': 'sqlite',
                    'description': 'Główny realm danych użytkownika',
                    'config': {
                        'path': 'db/realm_main.db',
                        'auto_create': True,
                        'backup_enabled': True
                    },
                    'status': 'active'
                }
            ]
            
            # Zapisz moduły
            for module_data in default_modules:
                module = SystemModule(
                    name=module_data['name'],
                    type=module_data['type'],
                    status=module_data['status'],
                    config=module_data['config'],
                    dependencies=module_data['dependencies'],
                    created_at=current_time,
                    last_update=current_time
                )
                await self.register_module(module)
            
            # Zapisz bazy danych
            for db_data in default_databases:
                database = DatabaseDefinition(
                    name=db_data['name'],
                    type=db_data['type'],
                    description=db_data['description'],
                    config=db_data['config'],
                    status=db_data['status'],
                    created_at=current_time,
                    last_access=current_time
                )
                await self.register_database(database)
            
            # Oznacz system jako zainicjalizowany
            self.system_info['initialized_at'] = current_time
            await self._save_system_info()
            
            print("🎯 Domyślna konfiguracja systemu utworzona")
            
        except Exception as e:
            print(f"❌ Błąd tworzenia domyślnej konfiguracji: {e}")
    
    async def register_module(self, module: SystemModule) -> bool:
        """Rejestruje moduł w systemie"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO system_modules 
                (name, type, status, config, dependencies, created_at, last_update)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                module.name,
                module.type,
                module.status,
                json.dumps(module.config),
                json.dumps(module.dependencies),
                module.created_at,
                module.last_update
            ))
            
            conn.commit()
            conn.close()
            
            # Aktualizuj cache
            self.modules_cache[module.name] = module
            
            # Zapisz zmianę
            await self._log_change('module_registered', module.name, None, asdict(module))
            
            print(f"📦 Moduł '{module.name}' zarejestrowany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd rejestracji modułu '{module.name}': {e}")
            return False
    
    async def register_database(self, database: DatabaseDefinition) -> bool:
        """Rejestruje bazę danych w systemie"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO database_definitions 
                (name, type, description, config, status, created_at, last_access)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                database.name,
                database.type,
                database.description,
                json.dumps(database.config),
                database.status,
                database.created_at,
                database.last_access
            ))
            
            conn.commit()
            conn.close()
            
            # Aktualizuj cache
            self.databases_cache[database.name] = database
            
            # Zapisz zmianę
            await self._log_change('database_registered', database.name, None, asdict(database))
            
            print(f"🗄️ Baza '{database.name}' zarejestrowana")
            return True
            
        except Exception as e:
            print(f"❌ Błąd rejestracji bazy '{database.name}': {e}")
            return False
    
    async def get_startup_modules(self) -> List[SystemModule]:
        """Zwraca moduły do uruchomienia przy starcie"""
        startup_modules = []
        
        # Sortuj moduły według priorytetu i zależności
        for module in self.modules_cache.values():
            if module.config.get('auto_start', False):
                startup_modules.append(module)
        
        # Sortuj według priorytetu
        startup_modules.sort(key=lambda m: m.config.get('priority', 999))
        
        return startup_modules
    
    async def get_required_databases(self) -> List[DatabaseDefinition]:
        """Zwraca bazy danych wymagane do uruchomienia"""
        required_databases = []
        
        for database in self.databases_cache.values():
            if database.status == 'active':
                required_databases.append(database)
        
        return required_databases
    
    async def update_module_status(self, module_name: str, status: str) -> bool:
        """Aktualizuje status modułu"""
        try:
            if module_name not in self.modules_cache:
                return False
            
            old_status = self.modules_cache[module_name].status
            self.modules_cache[module_name].status = status
            self.modules_cache[module_name].last_update = datetime.now().isoformat()
            
            # Zapisz do bazy
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE system_modules 
                SET status = ?, last_update = ?
                WHERE name = ?
            ''', (status, self.modules_cache[module_name].last_update, module_name))
            
            conn.commit()
            conn.close()
            
            # Zapisz zmianę
            await self._log_change('module_status_updated', module_name, old_status, status)
            
            print(f"📊 Status modułu '{module_name}': {old_status} → {status}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd aktualizacji statusu modułu '{module_name}': {e}")
            return False
    
    async def _save_system_info(self):
        """Zapisuje informacje o systemie"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for key, value in self.system_info.items():
                cursor.execute('''
                    INSERT OR REPLACE INTO system_info (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', (key, json.dumps(value), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Błąd zapisywania informacji o systemie: {e}")
    
    async def _log_change(self, change_type: str, target_name: str, old_value: Any, new_value: Any, user_id: str = "system"):
        """Zapisuje log zmian"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_changes 
                (change_type, target_name, old_value, new_value, timestamp, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                change_type,
                target_name,
                json.dumps(old_value) if old_value is not None else None,
                json.dumps(new_value) if new_value is not None else None,
                datetime.now().isoformat(),
                user_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Błąd zapisu logu zmian: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Zwraca pełny status systemu"""
        await self._save_system_info()
        
        return {
            'system_info': self.system_info,
            'modules': {name: asdict(module) for name, module in self.modules_cache.items()},
            'databases': {name: asdict(db) for name, db in self.databases_cache.items()},
            'statistics': {
                'total_modules': len(self.modules_cache),
                'active_modules': len([m for m in self.modules_cache.values() if m.status == 'active']),
                'total_databases': len(self.databases_cache),
                'active_databases': len([d for d in self.databases_cache.values() if d.status == 'active'])
            }
        }

# Testowanie
async def test_system_state_manager():
    """Test System State Manager"""
    print("🧪 Testowanie System State Manager...")
    
    manager = SystemStateManager()
    
    # Inicjalizuj
    success = await manager.initialize()
    if not success:
        print("❌ Inicjalizacja nie powiodła się")
        return
    
    # Pobierz moduły startowe
    startup_modules = await manager.get_startup_modules()
    print(f"🚀 Moduły do uruchomienia: {[m.name for m in startup_modules]}")
    
    # Pobierz wymagane bazy
    required_databases = await manager.get_required_databases()
    print(f"🗄️ Wymagane bazy: {[d.name for d in required_databases]}")
    
    # Aktualizuj status modułu
    await manager.update_module_status('database_manager', 'active')
    
    # Pobierz status systemu
    status = await manager.get_system_status()
    print(f"📊 Status systemu: {status['statistics']}")
    
    print("✅ Test zakończony pomyślnie")

if __name__ == "__main__":
    asyncio.run(test_system_state_manager())
