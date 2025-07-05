
"""
🌌 DynamicRealmLoader - Dynamiczne ładowanie nowych wymiarów w locie

Pozwala Federze dodawać nowe typy wymiarów bez restartowania systemu
"""

import asyncio
import importlib
import sys
from typing import Dict, Any, Type, Optional
from pathlib import Path

from ..core.lux_module import LuxModule, ModuleType, ModuleVersion
from ..core.bus import FederationBus, FederationMessage
from .realm_base import BaseRealmModule


class DynamicRealmLoader(LuxModule):
    """
    Moduł dynamicznego ładowania wymiarów - pozwala dodawać nowe realmy w locie
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
        
        self.loaded_realm_types: Dict[str, Type[BaseRealmModule]] = {}
        self.active_realms: Dict[str, BaseRealmModule] = {}
        self.realm_modules_path = Path("federacja/modules/realms")  # Folder dla nowych wymiarów
        
        # Rejestracja w bus'ie
        self.bus.register_module(self.name, self)
        
        # Cykl życia
        self.running = False
        self.lifecycle_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """Inicjalizuje loader"""
        try:
            # Utwórz folder dla modułów realm jeśli nie istnieje
            self.realm_modules_path.mkdir(parents=True, exist_ok=True)
            
            # Załaduj istniejące typy wymiarów
            await self._discover_realm_types()
            
            # Uruchom lifecycle
            self.running = True
            self.lifecycle_task = asyncio.create_task(self._lifecycle_loop())
            
            self.is_active = True
            print(f"🌌 DynamicRealmLoader zainicjalizowany")
            return True
            
        except Exception as e:
            print(f"❌ Błąd inicjalizacji DynamicRealmLoader: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Wyłącza loader"""
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
    
    async def _lifecycle_loop(self):
        """Główna pętla cyklu życia - monitoruje i zarządza wymiarami"""
        print("🔄 DynamicRealmLoader lifecycle started")
        
        while self.running:
            try:
                # Sprawdź nowe pliki modułów
                await self._check_for_new_realm_modules()
                
                # Sprawdź zdrowie aktywnych wymiarów
                await self._health_check_realms()
                
                # Sprawdź czy dodano nowe typy
                await self._discover_realm_types()
                
                await asyncio.sleep(5)  # Sprawdzaj co 5 sekund
                
            except Exception as e:
                print(f"❌ Błąd w lifecycle loop: {e}")
                await asyncio.sleep(10)
        
        print("🔄 DynamicRealmLoader lifecycle stopped")
    
    async def _discover_realm_types(self):
        """Odkrywa dostępne typy wymiarów"""
        try:
            # Standardowe typy
            from .realm_memory import MemoryRealmModule
            from .realm_sqlite import SQLiteRealmModule
            
            self.loaded_realm_types.update({
                'memory': MemoryRealmModule,
                'sqlite': SQLiteRealmModule
            })
            
            # Szukaj nowych typów w folderze realms
            if self.realm_modules_path.exists():
                for module_file in self.realm_modules_path.glob("realm_*.py"):
                    realm_type = module_file.stem[6:]  # usuń "realm_"
                    
                    if realm_type not in self.loaded_realm_types:
                        await self._load_realm_type_from_file(module_file, realm_type)
            
        except Exception as e:
            print(f"❌ Błąd odkrywania typów wymiarów: {e}")
    
    async def _load_realm_type_from_file(self, module_file: Path, realm_type: str):
        """Ładuje typ wymiaru z pliku"""
        try:
            # Dynamiczny import
            spec = importlib.util.spec_from_file_location(f"realm_{realm_type}", module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Znajdź klasę realm
            class_name = f"{realm_type.title()}RealmModule"
            if hasattr(module, class_name):
                realm_class = getattr(module, class_name)
                self.loaded_realm_types[realm_type] = realm_class
                print(f"🌌 Załadowano nowy typ wymiaru: {realm_type}")
            
        except Exception as e:
            print(f"❌ Błąd ładowania typu wymiaru {realm_type}: {e}")
    
    async def _check_for_new_realm_modules(self):
        """Sprawdza czy pojawiły się nowe moduły"""
        # Tu można dodać logikę hot-reload
        pass
    
    async def _health_check_realms(self):
        """Sprawdza zdrowie aktywnych wymiarów"""
        for realm_name, realm in list(self.active_realms.items()):
            try:
                health = await realm.health_check()
                if not health.get('healthy', False):
                    print(f"⚠️ Wymiar {realm_name} niezdrowy: {health}")
                    # Tu można dodać auto-healing
                    
            except Exception as e:
                print(f"❌ Błąd sprawdzania zdrowia wymiaru {realm_name}: {e}")
    
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
            return list(self.active_realms.keys())
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    async def create_realm(self, realm_name: str, realm_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Tworzy nowy wymiar w locie"""
        try:
            if realm_name in self.active_realms:
                return {'success': False, 'error': f'Wymiar {realm_name} już istnieje'}
            
            if realm_type not in self.loaded_realm_types:
                return {'success': False, 'error': f'Nieznany typ wymiaru: {realm_type}'}
            
            # Utwórz instancję
            realm_class = self.loaded_realm_types[realm_type]
            realm = realm_class(realm_name, config, self.bus)
            
            # Inicjalizuj
            success = await realm.initialize()
            if success:
                self.active_realms[realm_name] = realm
                print(f"✨ Utworzono wymiar {realm_name} ({realm_type}) w locie")
                return {'success': True, 'realm_name': realm_name, 'type': realm_type}
            else:
                return {'success': False, 'error': 'Inicjalizacja nie powiodła się'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_available_realm_types(self) -> Dict[str, Any]:
        """Zwraca dostępne typy wymiarów"""
        return {
            'available_types': list(self.loaded_realm_types.keys()),
            'active_realms': list(self.active_realms.keys()),
            'total_types': len(self.loaded_realm_types)
        }
    
    async def heartbeat(self) -> bool:
        """Puls życia"""
        return self.running and self.is_active
    
    async def health_check(self) -> bool:
        """Sprawdza zdrowie modułu"""
        return self.running and self.is_active and (self.lifecycle_task is not None)
