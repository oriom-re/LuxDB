"""
🌌 DynamicRealmLoader - Główny Loader i Manager Cyklu Życia Wymiarów

Centralny punkt zarządzania wszystkimi modułami realm w systemie
"""

import asyncio
from typing import Dict, Any, List, Optional, Type
from datetime import datetime

from .base_realm import BaseRealmModule
from .memory_realm import MemoryRealmModule
from .sqlite_realm import SQLiteRealmModule
from . import get_realm_types
from ...core.lux_module import LuxModule, ModuleType, ModuleVersion
from ...core.bus import FederationBus, FederationMessage


class DynamicRealmLoader(LuxModule):
    """
    Główny loader i manager cyklu życia wymiarów

    Zarządza:
    - Ładowaniem typów realms
    - Tworzeniem instancji realms 
    - Cyklem życia realms
    - Monitorowaniem zdrowia
    """

    def __init__(self, config: Dict[str, Any], bus: FederationBus, name: str = "dynamic_realm_loader"):
        super().__init__(
            name=name,
            module_type=ModuleType.CORE,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )

        # Registry dostępnych typów
        self.loaded_realm_types: Dict[str, Type[BaseRealmModule]] = get_realm_types().copy()

        # Aktywne instancje realms
        self.active_realms: Dict[str, BaseRealmModule] = {}

        # Statystyki
        self.total_realms_created = 0
        self.total_operations = 0

        # Rejestracja w bus'ie
        self.bus.register_module(self.name, self)

        # Cykl życia
        self.running = False
        self.lifecycle_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """Inicjalizuje loader i manager"""
        try:
            # Załaduj realmy z konfiguracji
            await self._load_configured_realms()

            # Uruchom lifecycle
            self.running = True
            self.lifecycle_task = asyncio.create_task(self._lifecycle_loop())

            # Rejestruj komendy
            await self._register_commands()

            self.is_active = True
            print(f"🌌 DynamicRealmLoader zainicjalizowany z {len(self.active_realms)} realms")
            return True

        except Exception as e:
            print(f"❌ Błąd inicjalizacji DynamicRealmLoader: {e}")
            return False

    async def shutdown(self) -> bool:
        """Wyłącza loader i wszystkie realmy"""
        try:
            self.running = False

            # Zatrzymaj lifecycle
            if self.lifecycle_task:
                self.lifecycle_task.cancel()
                try:
                    await self.lifecycle_task
                except asyncio.CancelledError:
                    pass

            # Wyłącz wszystkie aktywne realmy
            for realm_name, realm in self.active_realms.items():
                await realm.shutdown()

            self.active_realms.clear()
            self.is_active = False

            print("🌌 DynamicRealmLoader wyłączony")
            return True

        except Exception as e:
            print(f"❌ Błąd wyłączania DynamicRealmLoader: {e}")
            return False

    async def _load_configured_realms(self):
        """Ładuje realmy z konfiguracji"""
        realms_config = self.config.get('realms', {})

        for realm_name, realm_config in realms_config.items():
            if realm_config.get('enabled', True):
                success = await self._create_realm_instance(realm_name, realm_config)
                if not success:
                    print(f"⚠️ Nie udało się załadować realm '{realm_name}'")

    async def _create_realm_instance(self, realm_name: str, realm_config: Dict[str, Any]) -> bool:
        """Tworzy instancję realm"""
        try:
            realm_type = realm_config.get('type', 'memory')

            if realm_type not in self.loaded_realm_types:
                print(f"❌ Nieznany typ realm: {realm_type}")
                return False

            # Utwórz instancję
            realm_class = self.loaded_realm_types[realm_type]
            realm = realm_class(realm_name, realm_config, self.bus)

            # Inicjalizuj
            success = await realm.initialize()
            if success:
                self.active_realms[realm_name] = realm
                self.total_realms_created += 1
                print(f"✅ Realm '{realm_name}' ({realm_type}) załadowany przez loader")

            return success

        except Exception as e:
            print(f"❌ Błąd tworzenia realm '{realm_name}': {e}")
            return False

    async def _lifecycle_loop(self):
        """Główna pętla cyklu życia - monitoruje i zarządza wymiarami"""
        print("🔄 DynamicRealmLoader lifecycle started")

        while self.running:
            try:
                # Sprawdź zdrowie aktywnych wymiarów
                await self._health_check_realms()

                # Sprawdź czy dodano nowe typy
                await self._discover_new_realm_types()

                await asyncio.sleep(10)  # Sprawdzaj co 10 sekund

            except Exception as e:
                print(f"❌ Błąd w lifecycle loop: {e}")
                await asyncio.sleep(30)

        print("🔄 DynamicRealmLoader lifecycle stopped")

    async def _health_check_realms(self):
        """Sprawdza zdrowie aktywnych wymiarów"""
        unhealthy_realms = []

        for realm_name, realm in list(self.active_realms.items()):
            try:
                health = await realm.health_check()
                if not health.get('healthy', False):
                    print(f"⚠️ Wymiar {realm_name} niezdrowy: {health}")
                    unhealthy_realms.append(realm_name)

            except Exception as e:
                print(f"❌ Błąd sprawdzania zdrowia wymiaru {realm_name}: {e}")
                unhealthy_realms.append(realm_name)

        # Auto-healing dla niezdrowych realms
        for realm_name in unhealthy_realms:
            if self.config.get('auto_healing', False):
                await self._try_heal_realm(realm_name)

    async def _try_heal_realm(self, realm_name: str):
        """Próbuje naprawić niezdrowy realm"""
        try:
            realm = self.active_realms.get(realm_name)
            if realm:
                print(f"🔧 Próba naprawy realm {realm_name}...")
                await realm.shutdown()
                success = await realm.initialize()
                if success:
                    print(f"✅ Realm {realm_name} naprawiony")
                else:
                    print(f"❌ Nie udało się naprawić realm {realm_name}")

        except Exception as e:
            print(f"❌ Błąd naprawy realm {realm_name}: {e}")

    async def _discover_new_realm_types(self):
        """Odkrywa nowe typy wymiarów"""
        # Tu można dodać logikę dynamicznego ładowania nowych typów
        pass

    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'create_realm': self.create_realm,
            'list_realm_types': self.list_available_realm_types,
            'get_active_realms': self.get_active_realms,
            'get_status': self.get_status,
            'health_check': self.health_check,
            'shutdown_realm': self.shutdown_realm
        }

        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"{self.name}.{cmd_name}", cmd_func)

    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data

        if command == 'create_realm':
            return await self.create_realm(
                data.get('realm_name'),
                data.get('realm_type'),
                data.get('config', {})
            )
        elif command == 'list_realm_types':
            return self.list_available_realm_types()
        elif command == 'get_active_realms':
            return self.get_active_realms()
        elif command == 'get_status':
            return await self.get_status()
        elif command == 'health_check':
            return await self.health_check()
        elif command == 'shutdown_realm':
            return await self.shutdown_realm(data.get('realm_name'))
        else:
            return {'error': f'Nieznana komenda: {command}'}

    async def create_realm(self, realm_name: str, realm_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy nowy wymiar w locie"""
        try:
            if realm_name in self.active_realms:
                return {'success': False, 'error': f'Wymiar {realm_name} już istnieje'}

            if realm_type not in self.loaded_realm_types:
                return {'success': False, 'error': f'Nieznany typ wymiaru: {realm_type}'}

            # Dodaj typ do konfiguracji
            config['type'] = realm_type

            # Utwórz instancję
            success = await self._create_realm_instance(realm_name, config)
            if success:
                return {'success': True, 'realm_name': realm_name, 'type': realm_type}
            else:
                return {'success': False, 'error': 'Inicjalizacja nie powiodła się'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def shutdown_realm(self, realm_name: str) -> Dict[str, Any]:
        """Wyłącza konkretny realm"""
        try:
            if realm_name not in self.active_realms:
                return {'success': False, 'error': f'Wymiar {realm_name} nie istnieje'}

            realm = self.active_realms[realm_name]
            success = await realm.shutdown()

            if success:
                del self.active_realms[realm_name]
                return {'success': True, 'realm_name': realm_name}
            else:
                return {'success': False, 'error': 'Nie udało się wyłączyć realm'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_available_realm_types(self) -> Dict[str, Any]:
        """Zwraca dostępne typy wymiarów"""
        return {
            'available_types': list(self.loaded_realm_types.keys()),
            'active_realms': list(self.active_realms.keys()),
            'total_types': len(self.loaded_realm_types),
            'total_active': len(self.active_realms)
        }

    def get_active_realms(self) -> List[str]:
        """Zwraca listę aktywnych realms"""
        return list(self.active_realms.keys())

    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status loadera"""
        realm_statuses = {}
        total_beings = 0

        for realm_name, realm in self.active_realms.items():
            try:
                status = await realm.get_status()
                realm_statuses[realm_name] = status
                total_beings += status.get('being_count', 0)
            except Exception as e:
                realm_statuses[realm_name] = {'error': str(e)}

        return {
            'module_id': self.name,
            'active': self.is_active,
            'running': self.running,
            'total_realm_types': len(self.loaded_realm_types),
            'active_realms_count': len(self.active_realms),
            'total_realms_created': self.total_realms_created,
            'total_beings': total_beings,
            'created_at': self.created_at.isoformat(),
            'realms': realm_statuses
        }

    async def heartbeat(self) -> bool:
        """Puls życia"""
        return self.running and self.is_active

    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie modułu"""
        healthy_realms = 0
        total_realms = len(self.active_realms)

        for realm in self.active_realms.values():
            try:
                health = await realm.health_check()
                if health.get('healthy', False):
                    healthy_realms += 1
            except:
                pass

        return {
            'healthy': self.running and self.is_active and (self.lifecycle_task is not None),
            'loader_running': self.running,
            'lifecycle_active': self.lifecycle_task is not None,
            'total_realms': total_realms,
            'healthy_realms': healthy_realms,
            'health_ratio': healthy_realms / total_realms if total_realms > 0 else 1.0,
            'last_check': datetime.now().isoformat()
        }

    def get_realm(self, realm_name: str) -> Optional[BaseRealmModule]:
        """Zwraca instancję realm po nazwie"""
        return self.active_realms.get(realm_name)