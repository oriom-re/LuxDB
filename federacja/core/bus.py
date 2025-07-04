
"""
🚌 Federation Bus - System Komunikacji Federacji

Oparty na LuxBus Core ale uproszczony do potrzeb federacji
"""

import asyncio
import uuid
from typing import Dict, Any, Callable, List
from dataclasses import dataclass, asdict
from datetime import datetime


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


class FederationBus:
    """
    Uproszczony bus komunikacyjny dla federacji
    """
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_queue = asyncio.Queue()
        self.running = False
        self.stats = {
            'messages_sent': 0,
            'messages_processed': 0
        }
    
    async def start(self):
        """Uruchamia bus"""
        self.running = True
        asyncio.create_task(self._process_loop())
    
    async def stop(self):
        """Zatrzymuje bus"""
        self.running = False
    
    def subscribe(self, module_name: str, callback: Callable):
        """Subskrybuje moduł do odbierania wiadomości"""
        if module_name not in self.subscribers:
            self.subscribers[module_name] = []
        self.subscribers[module_name].append(callback)
    
    def unsubscribe(self, module_name: str, callback: Callable):
        """Usuwa subskrypcję"""
        if module_name in self.subscribers:
            if callback in self.subscribers[module_name]:
                self.subscribers[module_name].remove(callback)
    
    async def send(self, message: FederationMessage):
        """Wysyła wiadomość"""
        self.stats['messages_sent'] += 1
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
                print(f"❌ Error processing message: {e}")
    
    async def _process_loop(self):
        """Główna pętla przetwarzania wiadomości"""
        while self.running:
            try:
                await self.process_messages()
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"❌ Error in bus process loop: {e}")
                await asyncio.sleep(1)
    
    async def _deliver_message(self, message: FederationMessage):
        """Dostarcza wiadomość do odbiorcy"""
        target_module = message.to_module
        
        if target_module in self.subscribers:
            message.add_trace(f"bus_delivery_to_{target_module}")
            
            for callback in self.subscribers[target_module]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(message)
                    else:
                        callback(message)
                except Exception as e:
                    print(f"❌ Error in message callback for {target_module}: {e}")
        else:
            print(f"⚠️ No subscribers for module: {target_module}")
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status bus'a"""
        return {
            'running': self.running,
            'subscribers': list(self.subscribers.keys()),
            'queue_size': self.message_queue.qsize(),
            'stats': self.stats
        }
