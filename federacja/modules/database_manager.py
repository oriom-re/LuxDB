
"""
🗃️ DatabaseManager - Koordynator Systemów Bazodanowych

Uproszczony koordynator który deleguje wszystko do DynamicRealmLoader
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..core.bus import FederationBus, FederationMessage
from ..core.lux_module import LuxModule, ModuleType, ModuleVersion


class DatabaseManagerModule(LuxModule):
    """
    Koordynator systemów bazodanowych - deleguje do DynamicRealmLoader
    """
    
    def __init__(self, config: Dict[str, Any], bus: FederationBus, name: str = "database_manager"):
        super().__init__(
            name=name,
            module_type=ModuleType.CORE,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )
        
        self.module_id = "database_manager"
        
        # Statystyki
        self.total_operations = 0
        
        # Rejestracja w bus'ie
        self.bus.register_module(self.module_id, self)
    
    async def initialize(self) -> bool:
        """Inicjalizuje menedżer bazy danych"""
        try:
            print("🗃️ Inicjalizacja Database Manager...")
            
            # Rejestruj komendy w bus'ie
            await self._register_commands()
            
            self.is_active = True
            print(f"🗃️ Database Manager zainicjalizowany - deleguje do DynamicRealmLoader")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji Database Manager: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Wyłącza menedżer bazy danych"""
        try:
            print("🗃️ Wyłączanie Database Manager...")
            self.is_active = False
            print("🗃️ Database Manager wyłączony")
            return True
            
        except Exception as e:
            print(f"❌ Błąd wyłączania Database Manager: {e}")
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
            # Operacje przekazywane do realms przez loader
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
    
    async def _get_loader(self):
        """Pobiera instancję DynamicRealmLoader"""
        loader_msg = FederationMessage(
            message_id="get_loader_instance",
            from_module=self.module_id,
            to_module="dynamic_realm_loader",
            message_type="get_status",
            data={}
        )
        return await self.bus.send_message(loader_msg)
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status menedżera bazy danych - deleguje do loader"""
        try:
            loader_status = await self._get_loader()
            
            return {
                'module_id': self.module_id,
                'active': self.is_active,
                'total_operations': self.total_operations,
                'created_at': self.created_at.isoformat(),
                'loader_status': loader_status,
                'note': 'Deleguje do DynamicRealmLoader'
            }
        except Exception as e:
            return {
                'module_id': self.module_id,
                'active': self.is_active,
                'error': str(e)
            }
    
    async def list_realms(self) -> List[str]:
        """Zwraca listę nazw realms - deleguje do loader"""
        try:
            loader_msg = FederationMessage(
                message_id="list_realms",
                from_module=self.module_id,
                to_module="dynamic_realm_loader",
                message_type="get_active_realms",
                data={}
            )
            result = await self.bus.send_message(loader_msg)
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"❌ Błąd pobierania listy realms: {e}")
            return []
    
    async def get_realm_status(self, realm_name: str) -> Optional[Dict[str, Any]]:
        """Zwraca status konkretnego realm - deleguje do loader"""
        try:
            # Tu trzeba by dodać metodę do pobierania statusu konkretnego realm
            return None
        except Exception as e:
            print(f"❌ Błąd pobierania statusu realm {realm_name}: {e}")
            return None
    
    async def get_total_beings(self) -> int:
        """Zwraca łączną liczbę bytów - deleguje do loader"""
        try:
            loader_status = await self._get_loader()
            return loader_status.get('total_beings', 0)
        except Exception as e:
            print(f"❌ Błąd pobierania liczby bytów: {e}")
            return 0
    
    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie systemu - deleguje do loader"""
        try:
            loader_msg = FederationMessage(
                message_id="health_check",
                from_module=self.module_id,
                to_module="dynamic_realm_loader",
                message_type="health_check",
                data={}
            )
            loader_health = await self.bus.send_message(loader_msg)
            
            return {
                'database_healthy': self.is_active and loader_health.get('healthy', False),
                'manager_active': self.is_active,
                'loader_health': loader_health,
                'last_check': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'database_healthy': False,
                'manager_active': self.is_active,
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def create_realm(self, realm_name: str, config: Dict[str, Any]) -> bool:
        """Tworzy nowy realm - deleguje do loader"""
        try:
            loader_msg = FederationMessage(
                message_id="create_realm",
                from_module=self.module_id,
                to_module="dynamic_realm_loader",
                message_type="create_realm",
                data={
                    'realm_name': realm_name,
                    'realm_type': config.get('type', 'memory'),
                    'config': config
                }
            )
            result = await self.bus.send_message(loader_msg)
            return result.get('success', False)
        except Exception as e:
            print(f"❌ Błąd tworzenia realm {realm_name}: {e}")
            return False
    
    async def drop_realm(self, realm_name: str) -> bool:
        """Usuwa realm - deleguje do loader"""
        try:
            loader_msg = FederationMessage(
                message_id="shutdown_realm",
                from_module=self.module_id,
                to_module="dynamic_realm_loader", 
                message_type="shutdown_realm",
                data={'realm_name': realm_name}
            )
            result = await self.bus.send_message(loader_msg)
            return result.get('success', False)
        except Exception as e:
            print(f"❌ Błąd usuwania realm {realm_name}: {e}")
            return False
    
    # Operacje delegowane bezpośrednio do realms
    async def manifest_being(self, realm_name: str, being_data: Dict[str, Any]) -> Any:
        """Manifestuje byt - deleguje do konkretnego realm"""
        self.total_operations += 1
        try:
            realm_msg = FederationMessage(
                message_id="manifest",
                from_module=self.module_id,
                to_module=f"realm_{realm_name}",
                message_type="manifest",
                data=being_data
            )
            return await self.bus.send_message(realm_msg)
        except Exception as e:
            return {'error': f'Błąd manifestacji w realm {realm_name}: {e}'}
    
    async def contemplate_beings(self, realm_name: str, intention: str, **conditions) -> List[Any]:
        """Kontempluje byty - deleguje do konkretnego realm"""
        self.total_operations += 1
        try:
            realm_msg = FederationMessage(
                message_id="contemplate",
                from_module=self.module_id,
                to_module=f"realm_{realm_name}",
                message_type="contemplate",
                data={
                    'intention': intention,
                    'conditions': conditions
                }
            )
            result = await self.bus.send_message(realm_msg)
            return result if isinstance(result, list) else []
        except Exception as e:
            print(f"❌ Błąd kontemplacji w realm {realm_name}: {e}")
            return []
    
    async def transcend_being(self, realm_name: str, being_id: Any) -> bool:
        """Transcenduje byt - deleguje do konkretnego realm"""
        self.total_operations += 1
        try:
            realm_msg = FederationMessage(
                message_id="transcend",
                from_module=self.module_id,
                to_module=f"realm_{realm_name}",
                message_type="transcend",
                data={'being_id': being_id}
            )
            return await self.bus.send_message(realm_msg)
        except Exception as e:
            print(f"❌ Błąd transcendencji w realm {realm_name}: {e}")
            return False
    
    async def evolve_being(self, realm_name: str, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """Ewoluuje byt - deleguje do konkretnego realm"""
        self.total_operations += 1
        try:
            realm_msg = FederationMessage(
                message_id="evolve",
                from_module=self.module_id,
                to_module=f"realm_{realm_name}",
                message_type="evolve",
                data={
                    'being_id': being_id,
                    'new_data': new_data
                }
            )
            return await self.bus.send_message(realm_msg)
        except Exception as e:
            print(f"❌ Błąd ewolucji w realm {realm_name}: {e}")
            return None
