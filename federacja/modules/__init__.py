
"""
📦 Federation Modules - Bazowa klasa dla wszystkich modułów

Każdy moduł federacji dziedziczy po BaseModule
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseModule(ABC):
    """
    Bazowa klasa dla wszystkich modułów federacji
    """
    
    def __init__(self, bus, config: Dict[str, Any], logger):
        self.bus = bus
        self.config = config
        self.logger = logger
        self.module_name = self.__class__.__name__.replace('Module', '').lower()
        self.running = False
    
    async def start(self):
        """Uruchamia moduł"""
        self.logger.info(f"🚀 Starting module: {self.module_name}")
        
        # Subskrybuj do bus'a
        self.bus.subscribe(self.module_name, self._handle_message)
        
        # Wywołaj inicjalizację modułu
        await self.initialize()
        
        self.running = True
        self.logger.info(f"✅ Module started: {self.module_name}")
    
    async def stop(self):
        """Zatrzymuje moduł"""
        self.logger.info(f"🛑 Stopping module: {self.module_name}")
        self.running = False
        
        # Wywołaj cleanup modułu
        await self.cleanup()
        
        self.logger.info(f"✅ Module stopped: {self.module_name}")
    
    @abstractmethod
    async def initialize(self):
        """Inicjalizacja specyficzna dla modułu"""
        pass
    
    async def cleanup(self):
        """Cleanup - domyślnie pusty, moduły mogą nadpisać"""
        pass
    
    async def _handle_message(self, message):
        """Obsługuje wiadomości z bus'a"""
        try:
            message.add_trace(f"received_by_{self.module_name}")
            await self.handle_message(message)
        except Exception as e:
            self.logger.error(f"❌ Error handling message in {self.module_name}: {e}")
    
    async def handle_message(self, message):
        """Override w modułach do obsługi wiadomości"""
        pass
    
    async def send_message(self, to_module: str, message_type: str, data: Any):
        """Wysyła wiadomość do innego modułu"""
        await self.bus.send_simple(self.module_name, to_module, message_type, data)
    
    async def broadcast_message(self, message_type: str, data: Any):
        """Broadcastuje wiadomość do wszystkich modułów"""
        await self.bus.broadcast(self.module_name, message_type, data)
    
    async def health_check(self) -> bool:
        """Sprawdzenie zdrowia modułu - override w modułach"""
        return self.running
    
    def get_info(self) -> Dict[str, Any]:
        """Zwraca informacje o module"""
        return {
            'name': self.module_name,
            'running': self.running,
            'config': self.config
        }
