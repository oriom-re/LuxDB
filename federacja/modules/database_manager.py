
"""
🗃️ DatabaseManager - Główny Moduł Zarządzania Bazą w Federacji

Koordynuje wszystkie realms i zarządza danymi na wysokim poziomie
"""

import asyncio
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from ..core.bus import FederationBus, FederationMessage
from ..core.lux_module import LuxModule, ModuleType, ModuleVersion
from .realm_base import BaseRealmModule
from .realm_sqlite import SQLiteRealmModule
from .realm_memory import MemoryRealmModule


class DatabaseManager(LuxModule):
    """
    Główny menedżer bazy danych - koordynuje wszystkie realms
    """
    
    # Mapa typów realms do klas
    REALM_TYPES: Dict[str, Type[BaseRealmModule]] = {
        'sqlite': SQLiteRealmModule,
        'memory': MemoryRealmModule,
        # Tutaj będziemy dodawać kolejne typy realms
    }
    
    def __init__(self, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name="database_manager",
            module_type=ModuleType.CORE,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )
        
        self.module_id = "database_manager"
        
        # Słownik aktywnych realms
        self.realms: Dict[str, BaseRealmModule] = {}
        
        # Statystyki
        self.total_beings = 0
        self.total_operations = 0
        
        # Rejestracja w bus'ie
        self.bus.register_module(self.module_id, self)
    
    async def initialize(self) -> bool:
        """Inicjalizuje menedżer bazy danych"""
        try:
            print("🗃️ Inicjalizacja Database Manager...")
            
            # Załaduj realms z konfiguracji
            realms_config = self.config.get('realms', {})
            
            for realm_name, realm_config in realms_config.items():
                success = await self._load_realm(realm_name, realm_config)
                if not success:
                    print(f"⚠️ Nie udało się załadować realm '{realm_name}'")
            
            # Rejestruj komendy w bus'ie
            await self._register_commands()
            
            self.is_active = True
            print(f"🗃️ Database Manager zainicjalizowany - realms: {list(self.realms.keys())}")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji Database Manager: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Wyłącza menedżer bazy danych"""
        try:
            print("🗃️ Wyłączanie Database Manager...")
            
            # Wyłącz wszystkie realms
            for realm_name, realm in self.realms.items():
                await realm.shutdown()
            
            self.realms.clear()
            self.is_active = False
            
            print("🗃️ Database Manager wyłączony")
            return True
            
        except Exception as e:
            print(f"❌ Błąd wyłączania Database Manager: {e}")
            return False
    
    async def _load_realm(self, realm_name: str, realm_config: Dict[str, Any]) -> bool:
        """Ładuje pojedynczy realm"""
        try:
            realm_type = realm_config.get('type', 'memory')
            
            if realm_type not in self.REALM_TYPES:
                print(f"❌ Nieznany typ realm: {realm_type}")
                return False
            
            # Utwórz instancję realm
            realm_class = self.REALM_TYPES[realm_type]
            realm = realm_class(realm_name, realm_config, self.bus)
            
            # Inicjalizuj realm
            success = await realm.initialize()
            if success:
                self.realms[realm_name] = realm
                print(f"✅ Realm '{realm_name}' ({realm_type}) załadowany")
            
            return success
            
        except Exception as e:
            print(f"❌ Błąd ładowania realm '{realm_name}': {e}")
            return False
    
    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'get_status': self.get_status,
            'list_realms': self.list_realms,
            'get_realm_status': self.get_realm_status,
            'total_beings': self.get_total_beings,
            'health_check': self.health_check,
            'create_realm': self.create_realm,
            'drop_realm': self.drop_realm,
            # Operacje przekazywane do realms
            'manifest': self.manifest_being,
            'contemplate': self.contemplate_beings,
            'transcend': self.transcend_being,
            'evolve': self.evolve_being
        }
        
        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"{self.module_id}.{cmd_name}", cmd_func)
    
    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data
        
        if command == 'get_status':
            return await self.get_status()
        elif command == 'list_realms':
            return await self.list_realms()
        elif command == 'get_realm_status':
            return await self.get_realm_status(data.get('realm_name'))
        elif command == 'total_beings':
            return await self.get_total_beings()
        elif command == 'health_check':
            return await self.health_check()
        elif command == 'create_realm':
            return await self.create_realm(data.get('realm_name'), data.get('config', {}))
        elif command == 'drop_realm':
            return await self.drop_realm(data.get('realm_name'))
        elif command == 'manifest':
            return await self.manifest_being(data.get('realm_name'), data.get('being_data', {}))
        elif command == 'contemplate':
            return await self.contemplate_beings(data.get('realm_name'), data.get('intention', ''), **data.get('conditions', {}))
        elif command == 'transcend':
            return await self.transcend_being(data.get('realm_name'), data.get('being_id'))
        elif command == 'evolve':
            return await self.evolve_being(data.get('realm_name'), data.get('being_id'), data.get('new_data', {}))
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status menedżera bazy danych"""
        realm_statuses = {}
        total_beings = 0
        
        for realm_name, realm in self.realms.items():
            status = await realm.get_status()
            realm_statuses[realm_name] = status
            total_beings += status.get('being_count', 0)
        
        return {
            'module_id': self.module_id,
            'active': self.is_active,
            'realms_count': len(self.realms),
            'total_beings': total_beings,
            'total_operations': self.total_operations,
            'created_at': self.created_at.isoformat(),
            'realms': realm_statuses
        }
    
    async def list_realms(self) -> List[str]:
        """Zwraca listę nazw realms"""
        return list(self.realms.keys())
    
    async def get_realm_status(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """Zwraca status konkretnego realm"""
        if realm_name not in self.realms:
            return None
        
        return await self.realms[realm_name].get_status()
    
    async def get_total_beings(self) -> int:
        """Zwraca łączną liczbę bytów we wszystkich realms"""
        total = 0
        for realm in self.realms.values():
            total += await realm.count_beings()
        return total
    
    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie całego systemu bazy danych"""
        realm_health = {}
        all_healthy = True
        
        for realm_name, realm in self.realms.items():
            health = await realm.health_check()
            realm_health[realm_name] = health
            if not health.get('healthy', False):
                all_healthy = False
        
        return {
            'database_healthy': all_healthy and self.is_active,
            'realms_healthy': all_healthy,
            'active_realms': len(self.realms),
            'realm_health': realm_health,
            'last_check': datetime.now().isoformat()
        }
    
    async def create_realm(self, realm_name: str, config: Dict[str, Any]) -> bool:
        """Tworzy nowy realm dynamicznie"""
        if realm_name in self.realms:
            return False  # Realm już istnieje
        
        return await self._load_realm(realm_name, config)
    
    async def drop_realm(self, realm_name: str) -> bool:
        """Usuwa realm"""
        if realm_name not in self.realms:
            return False
        
        realm = self.realms[realm_name]
        await realm.shutdown()
        del self.realms[realm_name]
        
        print(f"🗑️ Realm '{realm_name}' usunięty")
        return True
    
    # Operacje przekazywane do realms
    async def manifest_being(self, realm_name: str, being_data: Dict[str, Any]) -> Any:
        """Manifestuje byt w określonym realm"""
        if realm_name not in self.realms:
            return {'error': f'Realm {realm_name} nie istnieje'}
        
        self.total_operations += 1
        return await self.realms[realm_name].manifest(being_data)
    
    async def contemplate_beings(self, realm_name: str, intention: str, **conditions) -> List[Any]:
        """Kontempluje byty w określonym realm"""
        if realm_name not in self.realms:
            return []
        
        self.total_operations += 1
        return await self.realms[realm_name].contemplate(intention, **conditions)
    
    async def transcend_being(self, realm_name: str, being_id: Any) -> bool:
        """Transcenduje byt z określonego realm"""
        if realm_name not in self.realms:
            return False
        
        self.total_operations += 1
        return await self.realms[realm_name].transcend(being_id)
    
    async def evolve_being(self, realm_name: str, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """Ewoluuje byt w określonym realm"""
        if realm_name not in self.realms:
            return None
        
        self.total_operations += 1
        return await self.realms[realm_name].evolve(being_id, new_data)
    
    def get_realm(self, realm_name: str) -> Optional[BaseRealmModule]:
        """Zwraca instancję realm po nazwie"""
        return self.realms.get(realm_name)
