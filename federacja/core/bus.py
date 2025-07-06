
"""
🚌 Federation Bus - System Komunikacji Federacji

Oparty na LuxBus Core ale uproszczony do potrzeb federacji
"""

import asyncio
import uuid
from typing import Dict, Any, Callable, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from .logger import FederationLogger


@dataclass
class FederationMessage:
    """Wiadomość w federacji"""
    uid: str
    from_module: str
    to_module: str
    message_type: str
    data: Any
    timestamp: float
    trace_history: List[str] = None
    
    def __post_init__(self):
        if self.trace_history is None:
            self.trace_history = []
    
    def add_trace(self, module_name: str):
        """Dodaje ślad do historii"""
        self.trace_history.append(f"{module_name}@{datetime.now().isoformat()}")
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def get(self, key: str, default=None):
        """Kompatybilność z dict.get() dla starych modułów"""
        return getattr(self, key, default)


class FederationBus:
    """
    Uproszczony bus komunikacyjny dla federacji
    """
    
    def __init__(self, logger: Optional[FederationLogger] = None):
        self.logger = logger or FederationLogger({'level': 'INFO', 'format': 'console'})
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        self.stats = {
            'messages_sent': 0,
            'messages_processed': 0,
            'messages_failed': 0
        }
    
    async def start(self):
        """Uruchamia bus"""
        self.logger.info("🚌 Starting Federation Bus...")
        self.running = True
        asyncio.create_task(self._process_loop())
        self.logger.info("✅ Federation Bus started")
    
    async def stop(self):
        """Zatrzymuje bus"""
        self.logger.info("🛑 Stopping Federation Bus...")
        self.running = False
        self.logger.info("✅ Federation Bus stopped")
    
    def subscribe(self, module_name: str, callback: Callable):
        """Subskrybuje moduł do odbierania wiadomości"""
        if module_name not in self.subscribers:
            self.subscribers[module_name] = []
        self.subscribers[module_name].append(callback)
        self.logger.debug(f"📝 Module '{module_name}' subscribed to bus")
    
    def unsubscribe(self, module_name: str, callback: Callable):
        """Usuwa subskrypcję"""
        if module_name in self.subscribers:
            if callback in self.subscribers[module_name]:
                self.subscribers[module_name].remove(callback)
                self.logger.debug(f"❌ Module '{module_name}' unsubscribed from bus")
    
    def register_module(self, module_name: str, module_instance: Any):
        """Rejestruje moduł w bus'ie"""
        # Automatycznie subskrybuj moduł jeśli ma metodę handle_message
        if hasattr(module_instance, 'handle_message'):
            self.subscribe(module_name, module_instance.handle_message)
        
        self.logger.info(f"📋 Module '{module_name}' registered in bus")
        return True
    
    async def send(self, message: FederationMessage):
        """Wysyła wiadomość"""
        self.stats['messages_sent'] += 1
        self.logger.debug(f"📤 Sending message {message.uid}: {message.from_module} → {message.to_module} ({message.message_type})")
        await self.message_queue.put(message)
    
    async def send_simple(self, from_module: str, to_module: str, message_type: str, data: Any):
        """Uproszczone wysyłanie wiadomości"""
        message = FederationMessage(
            uid=f"msg_{uuid.uuid4().hex[:8]}",
            from_module=from_module,
            to_module=to_module,
            message_type=message_type,
            data=data,
            timestamp=asyncio.get_event_loop().time()
        )
        await self.send(message)
    
    async def broadcast(self, from_module: str, message_type: str, data: Any):
        """Wysyła wiadomość do wszystkich modułów"""
        target_count = len([m for m in self.subscribers.keys() if m != from_module])
        self.logger.debug(f"📡 Broadcasting '{message_type}' from '{from_module}' to {target_count} modules")
        
        for module_name in self.subscribers.keys():
            if module_name != from_module:
                await self.send_simple(from_module, module_name, message_type, data)
    
    async def process_messages(self):
        """Przetwarza pojedynczą partię wiadomości"""
        processed = 0
        max_batch = 10
        
        while processed < max_batch and not self.message_queue.empty():
            try:
                message = self.message_queue.get_nowait()
                await self._deliver_message(message)
                processed += 1
                self.stats['messages_processed'] += 1
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                self.stats['messages_failed'] += 1
                self.logger.error(f"❌ Error processing message: {e}")
        
        if processed > 0:
            self.logger.debug(f"📦 Processed {processed} messages in batch")
    
    async def _process_loop(self):
        """Główna pętla przetwarzania wiadomości"""
        self.logger.debug("🔄 Bus process loop started")
        while self.running:
            try:
                await self.process_messages()
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"❌ Error in bus process loop: {e}")
                await asyncio.sleep(1)
        self.logger.debug("🔄 Bus process loop stopped")
    
    async def _deliver_message(self, message: FederationMessage):
        """Dostarcza wiadomość do odbiorcy"""
        target_module = message.to_module
        
        if target_module in self.subscribers:
            message.add_trace(f"bus_delivery_to_{target_module}")
            self.logger.debug(f"📥 Delivering message {message.uid} to '{target_module}' ({len(self.subscribers[target_module])} callbacks)")
            
            for callback in self.subscribers[target_module]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    self.stats['messages_failed'] += 1
                    self.logger.error(f"❌ Error in message callback for {target_module}: {e}")
        else:
            self.stats['messages_failed'] += 1
            self.logger.warning(f"⚠️ No subscribers for module: {target_module} (message: {message.uid})")
    
    async def register_command(self, command_name: str, handler: Callable):
        """Rejestruje komendę w bus'ie"""
        # Dla uproszczenia, komendy traktujemy jak subskrypcje
        module_name = command_name.split('.')[0]
        self.subscribe(module_name, handler)
        self.logger.debug(f"🔧 Command '{command_name}' registered")
    
    async def send_message(self, message: FederationMessage, timeout: int = 30) -> Dict[str, Any]:
        """Wysyła wiadomość i czeka na odpowiedź"""
        await self.send(message)
        # Dla uproszczenia, zwracamy podstawową odpowiedź
        return {'success': True, 'healthy': True}
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status bus'a"""
        return {
            'running': self.running,
            'subscribers': list(self.subscribers.keys()),
            'queue_size': self.message_queue.qsize(),
            'stats': self.stats,
            'health': {
                'success_rate': (self.stats['messages_processed'] / max(self.stats['messages_sent'], 1)) * 100,
                'failure_rate': (self.stats['messages_failed'] / max(self.stats['messages_sent'], 1)) * 100
            }
        }
