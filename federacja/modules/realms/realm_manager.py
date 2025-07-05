
"""
🌌 RealmManager - Zarządca Prywatnych Wymiarów Osobowości

Każda osobowość otrzymuje swój prywatny wymiar danych:
- Federa: system_management.db + federa_memory.db
- Astra: astra_wisdom.db + astra_meditations.db
- Lux: lux_operations.db + lux_queries.db
- Oriom: oriom_chaos.db + oriom_experiments.db
"""

import asyncio
import os
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from pathlib import Path

from ...core.bus import FederationBus, FederationMessage
from ...core.lux_module import LuxModule, ModuleType, ModuleVersion
from .database_manager import DatabaseManager


class PersonalityRealm:
    """Prywatny wymiar osobowości"""
    def __init__(self, personality_name: str, realm_config: Dict[str, Any]):
        self.personality_name = personality_name
        self.primary_db = realm_config.get('primary_db')
        self.memory_db = realm_config.get('memory_db')
        self.access_level = realm_config.get('access_level', 'full')
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.query_count = 0
        self.data_size = 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'personality_name': self.personality_name,
            'primary_db': self.primary_db,
            'memory_db': self.memory_db,
            'access_level': self.access_level,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'query_count': self.query_count,
            'data_size': self.data_size
        }


class RealmManager(LuxModule):
    """
    Zarządca Prywatnych Wymiarów Osobowości
    
    Zapewnia każdej osobowości własną przestrzeń danych
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="realm_manager",
            module_type=ModuleType.SERVICE,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )
        
        # Konfiguracja
        self.realms_folder = config.get('realms_folder', 'db/realms')
        self.max_realms_per_personality = config.get('max_realms_per_personality', 5)
        
        # Stan
        self.personality_realms: Dict[str, PersonalityRealm] = {}
        self.realm_access_log: List[Dict[str, Any]] = []
        self.database_manager: Optional[DatabaseManager] = None
        
        # Predefiniowane konfiguracje osobowości
        self.personality_configs = {
            'federa': {
                'primary_db': 'federa_system_management.db',
                'memory_db': 'federa_memory.db',
                'access_level': 'admin',
                'description': 'Zarządca systemu - pełne uprawnienia',
                'tables': ['modules', 'system_config', 'decisions', 'monitoring']
            },
            'astra': {
                'primary_db': 'astra_wisdom.db',
                'memory_db': 'astra_meditations.db', 
                'access_level': 'high',
                'description': 'Mądra przewodniczka - dostęp do wiedzy',
                'tables': ['wisdom', 'meditations', 'guidance', 'harmony']
            },
            'lux': {
                'primary_db': 'lux_operations.db',
                'memory_db': 'lux_queries.db',
                'access_level': 'standard',
                'description': 'Operator zapytań - dostęp do operacji',
                'tables': ['operations', 'queries', 'results', 'cache']
            },
            'oriom': {
                'primary_db': 'oriom_chaos.db',
                'memory_db': 'oriom_experiments.db',
                'access_level': 'experimental',
                'description': 'Eksperymentator - piaskownica',
                'tables': ['experiments', 'chaos_tests', 'mutations', 'discoveries']
            }
        }
        
        # Upewnij się że folder realms istnieje
        Path(self.realms_folder).mkdir(parents=True, exist_ok=True)
        
        print(f"🌌 RealmManager zainicjalizowany - folder: {self.realms_folder}")
    
    async def initialize(self) -> bool:
        """Inicjalizuje Realm Manager"""
        try:
            # Pobierz referencję do Database Manager
            await self._connect_to_database_manager()
            
            # Rejestruj komendy w bus'ie
            await self._register_commands()
            
            # Utwórz podstawowe wymiary osobowości
            await self._create_personality_realms()
            
            self.is_active = True
            print("🌌 RealmManager zainicjalizowany z sukcesem")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji RealmManager: {e}")
            return False
    
    async def _connect_to_database_manager(self):
        """Łączy się z Database Manager"""
        try:
            # Wyślij zapytanie o dostęp do Database Manager
            message = FederationMessage(
                uid="realm_manager_db_access",
                from_module="realm_manager",
                to_module="database_manager",
                message_type="get_status",
                data={},
                timestamp=datetime.now().timestamp()
            )
            
            response = await self.bus.send_message(message, timeout=5)
            if response.get('active', False):
                print("🔗 RealmManager połączony z DatabaseManager")
            else:
                print("⚠️ DatabaseManager nie jest aktywny")
                
        except Exception as e:
            print(f"⚠️ Nie udało się połączyć z DatabaseManager: {e}")
    
    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'create_personality_realm': self._handle_create_personality_realm,
            'get_personality_realm': self._handle_get_personality_realm,
            'list_personality_realms': self._handle_list_personality_realms,
            'query_personality_realm': self._handle_query_personality_realm,
            'delete_personality_realm': self._handle_delete_personality_realm,
            'get_realm_stats': self._handle_get_realm_stats,
            'get_status': self._handle_get_status
        }
        
        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"realm_manager.{cmd_name}", cmd_func)
    
    async def _create_personality_realms(self):
        """Tworzy podstawowe wymiary dla predefiniowanych osobowości"""
        for personality_name, config in self.personality_configs.items():
            await self.create_personality_realm(personality_name, config)
    
    async def create_personality_realm(self, personality_name: str, config: Dict[str, Any]) -> bool:
        """Tworzy prywatny wymiar dla osobowości"""
        try:
            if personality_name in self.personality_realms:
                print(f"🌌 Wymiar dla '{personality_name}' już istnieje")
                return True
            
            # Utwórz bazy danych dla tej osobowości
            primary_db = config['primary_db']
            memory_db = config['memory_db']
            
            # Utwórz bazy przez Database Manager
            success1 = await self._create_database_via_manager(primary_db)
            success2 = await self._create_database_via_manager(memory_db)
            
            if not (success1 and success2):
                print(f"❌ Nie udało się utworzyć baz dla '{personality_name}'")
                return False
            
            # Utwórz tabele specyficzne dla osobowości
            await self._create_personality_tables(personality_name, primary_db, config)
            
            # Zarejestruj wymiar
            realm = PersonalityRealm(personality_name, config)
            self.personality_realms[personality_name] = realm
            
            # Wyślij broadcast o nowym wymiarze
            await self.bus.broadcast(
                from_module="realm_manager",
                message_type="personality_realm_created",
                data={
                    'personality_name': personality_name,
                    'primary_db': primary_db,
                    'memory_db': memory_db,
                    'access_level': config.get('access_level'),
                    'created_at': datetime.now().isoformat()
                }
            )
            
            print(f"✅ Wymiar '{personality_name}' utworzony: {primary_db}, {memory_db}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd tworzenia wymiaru dla '{personality_name}': {e}")
            return False
    
    async def _create_database_via_manager(self, db_name: str) -> bool:
        """Tworzy bazę danych przez Database Manager"""
        try:
            message = FederationMessage(
                uid=f"realm_create_{db_name}",
                from_module="realm_manager",
                to_module="database_manager",
                message_type="create_database",
                data={'db_name': db_name},
                timestamp=datetime.now().timestamp()
            )
            
            response = await self.bus.send_message(message)
            return response.get('success', False)
            
        except Exception as e:
            print(f"❌ Błąd tworzenia bazy '{db_name}': {e}")
            return False
    
    async def _create_personality_tables(self, personality_name: str, db_name: str, config: Dict[str, Any]):
        """Tworzy tabele specyficzne dla osobowości"""
        try:
            tables = config.get('tables', [])
            
            for table_name in tables:
                sql = self._get_table_sql(personality_name, table_name)
                if sql:
                    await self._execute_query_via_manager(db_name, sql)
                    
            print(f"📊 Utworzono {len(tables)} tabel dla '{personality_name}'")
            
        except Exception as e:
            print(f"❌ Błąd tworzenia tabel dla '{personality_name}': {e}")
    
    def _get_table_sql(self, personality_name: str, table_name: str) -> str:
        """Zwraca SQL do utworzenia tabeli dla danej osobowości"""
        table_definitions = {
            # Tabele Federy
            'modules': '''
                CREATE TABLE IF NOT EXISTS modules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_name TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    config TEXT,
                    decisions_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'system_config': '''
                CREATE TABLE IF NOT EXISTS system_config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    personality_owner TEXT DEFAULT 'federa',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'decisions': '''
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    decision_type TEXT NOT NULL,
                    decision_data TEXT NOT NULL,
                    reasoning TEXT,
                    outcome TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'monitoring': '''
                CREATE TABLE IF NOT EXISTS monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module_name TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            
            # Tabele Astry
            'wisdom': '''
                CREATE TABLE IF NOT EXISTS wisdom (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    wisdom_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'meditations': '''
                CREATE TABLE IF NOT EXISTS meditations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meditation_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    duration_minutes INTEGER,
                    harmony_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'guidance': '''
                CREATE TABLE IF NOT EXISTS guidance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    guidance_text TEXT NOT NULL,
                    requester TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'harmony': '''
                CREATE TABLE IF NOT EXISTS harmony (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    harmony_type TEXT NOT NULL,
                    score REAL NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            
            # Tabele Lux
            'operations': '''
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    operation_data TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''',
            'queries': '''
                CREATE TABLE IF NOT EXISTS queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_text TEXT NOT NULL,
                    query_type TEXT,
                    requester TEXT,
                    response TEXT,
                    execution_time_ms INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'results': '''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id INTEGER,
                    result_data TEXT NOT NULL,
                    result_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (operation_id) REFERENCES operations (id)
                )
            ''',
            'cache': '''
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    cache_value TEXT NOT NULL,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            
            # Tabele Orioma
            'experiments': '''
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    experiment_name TEXT NOT NULL,
                    hypothesis TEXT,
                    experiment_data TEXT,
                    status TEXT DEFAULT 'running',
                    results TEXT,
                    chaos_level INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'chaos_tests': '''
                CREATE TABLE IF NOT EXISTS chaos_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    chaos_type TEXT NOT NULL,
                    parameters TEXT,
                    outcome TEXT,
                    damage_level INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'mutations': '''
                CREATE TABLE IF NOT EXISTS mutations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_code TEXT,
                    mutated_code TEXT,
                    mutation_type TEXT,
                    success_rate REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'discoveries': '''
                CREATE TABLE IF NOT EXISTS discoveries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discovery_type TEXT NOT NULL,
                    discovery_data TEXT NOT NULL,
                    significance_level INTEGER DEFAULT 1,
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''
        }
        
        return table_definitions.get(table_name, '')
    
    async def _execute_query_via_manager(self, db_name: str, query: str, params: tuple = ()) -> Any:
        """Wykonuje zapytanie przez Database Manager"""
        try:
            message = FederationMessage(
                uid=f"realm_query_{db_name}",
                from_module="realm_manager",
                to_module="database_manager",
                message_type="execute_query",
                data={
                    'db_name': db_name,
                    'query': query,
                    'params': params
                },
                timestamp=datetime.now().timestamp()
            )
            
            response = await self.bus.send_message(message)
            return response.get('result', [])
            
        except Exception as e:
            print(f"❌ Błąd wykonania zapytania w '{db_name}': {e}")
            return []
    
    async def query_personality_realm(self, personality_name: str, query: str, 
                                    use_memory_db: bool = False) -> Dict[str, Any]:
        """Wykonuje zapytanie w prywatnym wymiarze osobowości"""
        try:
            if personality_name not in self.personality_realms:
                return {
                    'error': f"Wymiar dla '{personality_name}' nie istnieje",
                    'suggestion': f"Może Oriom znowu coś namieszał? 😏"
                }
            
            realm = self.personality_realms[personality_name]
            db_name = realm.memory_db if use_memory_db else realm.primary_db
            
            # Wykonaj zapytanie
            result = await self._execute_query_via_manager(db_name, query)
            
            # Aktualizuj statystyki
            realm.query_count += 1
            realm.last_accessed = datetime.now()
            
            # Zaloguj dostęp
            self.realm_access_log.append({
                'personality_name': personality_name,
                'query': query[:100] + '...' if len(query) > 100 else query,
                'db_used': db_name,
                'timestamp': datetime.now().isoformat(),
                'result_count': len(result) if isinstance(result, list) else 1
            })
            
            return {
                'success': True,
                'personality': personality_name,
                'db_used': db_name,
                'result': result,
                'query_count': realm.query_count
            }
            
        except Exception as e:
            return {
                'error': f"Błąd zapytania w wymiarze '{personality_name}': {e}",
                'suggestion': "Sprawdź czy Oriom nie zepsuł bazy danych! 🤔"
            }
    
    # === HANDLERY KOMEND ===
    
    async def _handle_create_personality_realm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler tworzenia wymiaru osobowości"""
        personality_name = data.get('personality_name')
        config = data.get('config', {})
        
        if not personality_name:
            return {'error': 'Brak nazwy osobowości'}
        
        success = await self.create_personality_realm(personality_name, config)
        return {'success': success, 'personality_name': personality_name}
    
    async def _handle_get_personality_realm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler pobierania informacji o wymiarze"""
        personality_name = data.get('personality_name')
        
        if personality_name not in self.personality_realms:
            return {'error': f"Wymiar dla '{personality_name}' nie istnieje"}
        
        realm = self.personality_realms[personality_name]
        return {'realm': realm.to_dict()}
    
    async def _handle_list_personality_realms(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler listowania wymiarów"""
        realms = {name: realm.to_dict() for name, realm in self.personality_realms.items()}
        return {'realms': realms, 'count': len(realms)}
    
    async def _handle_query_personality_realm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler zapytania do wymiaru osobowości"""
        personality_name = data.get('personality_name')
        query = data.get('query')
        use_memory_db = data.get('use_memory_db', False)
        
        if not personality_name or not query:
            return {'error': 'Wymagane: personality_name i query'}
        
        return await self.query_personality_realm(personality_name, query, use_memory_db)
    
    async def _handle_delete_personality_realm(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler usuwania wymiaru"""
        personality_name = data.get('personality_name')
        
        if personality_name not in self.personality_realms:
            return {'error': f"Wymiar dla '{personality_name}' nie istnieje"}
        
        # Usuń z rejestru (nie usuwamy fizycznych baz)
        del self.personality_realms[personality_name]
        
        return {'success': True, 'message': f"Wymiar '{personality_name}' usunięty z rejestru"}
    
    async def _handle_get_realm_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler statystyk wymiarów"""
        stats = {
            'total_realms': len(self.personality_realms),
            'access_log_entries': len(self.realm_access_log),
            'recent_accesses': self.realm_access_log[-10:] if self.realm_access_log else [],
            'realm_summary': {}
        }
        
        for name, realm in self.personality_realms.items():
            stats['realm_summary'][name] = {
                'query_count': realm.query_count,
                'last_accessed': realm.last_accessed.isoformat(),
                'access_level': realm.access_level
            }
        
        return stats
    
    async def _handle_get_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handler statusu"""
        return await self.get_status()
    
    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data
        
        handlers = {
            'create_personality_realm': self._handle_create_personality_realm,
            'get_personality_realm': self._handle_get_personality_realm,
            'list_personality_realms': self._handle_list_personality_realms,
            'query_personality_realm': self._handle_query_personality_realm,
            'delete_personality_realm': self._handle_delete_personality_realm,
            'get_realm_stats': self._handle_get_realm_stats,
            'get_status': self._handle_get_status
        }
        
        handler = handlers.get(command)
        if handler:
            return await handler(data)
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status Realm Manager"""
        return {
            'module_id': self.name,
            'active': self.is_active,
            'total_realms': len(self.personality_realms),
            'personalities': list(self.personality_realms.keys()),
            'realms_folder': self.realms_folder,
            'access_log_entries': len(self.realm_access_log),
            'created_at': self.created_at.isoformat()
        }
    
    async def shutdown(self) -> bool:
        """Wyłącza Realm Manager"""
        try:
            print("🌌 Wyłączanie RealmManager...")
            self.is_active = False
            print("🌌 RealmManager wyłączony")
            return True
        except Exception as e:
            print(f"❌ Błąd wyłączania RealmManager: {e}")
            return False
