
"""
🌍 BaseRealmModule - Bazowy Moduł Wymiaru w Federacji

Abstrakcyjna klasa bazowa dla wszystkich modułów realms
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..core.bus import FederationBus, FederationMessage


class BaseRealmModule(ABC):
    """
    Bazowy moduł wymiaru - każdy realm będzie dziedziczyć po tej klasie
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus: FederationBus):
        self.name = name
        self.config = config
        self.bus = bus
        self.module_id = f"realm_{name}"
        self.is_active = False
        self.is_connected = False
        self.created_at = datetime.now()
        self._being_count = 0
        
        # Rejestracja w bus'ie
        self.bus.register_module(self.module_id, self)
    
    async def initialize(self) -> bool:
        """Inicjalizuje moduł realm"""
        try:
            success = await self.connect()
            if success:
                self.is_active = True
                await self._register_commands()
                print(f"🌍 Realm '{self.name}' zainicjalizowany")
            return success
        except Exception as e:
            print(f"❌ Błąd inicjalizacji realm '{self.name}': {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Wyłącza moduł realm"""
        try:
            await self.disconnect()
            self.is_active = False
            print(f"🕊️ Realm '{self.name}' wyłączony")
            return True
        except Exception as e:
            print(f"❌ Błąd wyłączania realm '{self.name}': {e}")
            return False
    
    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'manifest': self.manifest,
            'contemplate': self.contemplate,
            'transcend': self.transcend,
            'evolve': self.evolve,
            'get_status': self.get_status,
            'count_beings': self.count_beings,
            'health_check': self.health_check
        }
        
        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"{self.module_id}.{cmd_name}", cmd_func)
    
    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a"""
        command = message.message_type
        data = message.data
        
        if command == 'manifest':
            return await self.manifest(data)
        elif command == 'contemplate':
            return await self.contemplate(data.get('intention', ''), **data.get('conditions', {}))
        elif command == 'transcend':
            return await self.transcend(data.get('being_id'))
        elif command == 'evolve':
            return await self.evolve(data.get('being_id'), data.get('new_data', {}))
        elif command == 'get_status':
            return await self.get_status()
        elif command == 'count_beings':
            return await self.count_beings()
        elif command == 'health_check':
            return await self.health_check()
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    @abstractmethod
    async def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Rozłącza z wymiarem"""
        pass
    
    @abstractmethod
    async def manifest(self, being_data: Dict[str, Any]) -> Any:
        """Manifestuje nowy byt w wymiarze"""
        pass
    
    @abstractmethod
    async def contemplate(self, intention: str, **conditions) -> List[Any]:
        """Kontempluje (wyszukuje) byty w wymiarze"""
        pass
    
    @abstractmethod
    async def transcend(self, being_id: Any) -> bool:
        """Transcenduje (usuwa) byt z wymiaru"""
        pass
    
    @abstractmethod
    async def evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """Ewoluuje (aktualizuje) byt"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status wymiaru"""
        return {
            'module_id': self.module_id,
            'name': self.name,
            'type': self.__class__.__name__,
            'active': self.is_active,
            'connected': self.is_connected,
            'being_count': await self.count_beings(),
            'created_at': self.created_at.isoformat(),
            'config': self._mask_sensitive_config()
        }
    
    async def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        return self._being_count
    
    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie wymiaru"""
        return {
            'healthy': self.is_connected and self.is_active,
            'connected': self.is_connected,
            'active': self.is_active,
            'last_check': datetime.now().isoformat()
        }
    
    def _mask_sensitive_config(self) -> Dict[str, Any]:
        """Maskuje wrażliwe dane w konfiguracji"""
        masked_config = self.config.copy()
        sensitive_keys = ['password', 'secret', 'key', 'token']
        
        for key in masked_config:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked_config[key] = '***'
        
        return masked_config
