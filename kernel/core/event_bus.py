
"""
📡 Kernel EventBus - Wewnętrzny, izolowany EventBus Kernela

Komunikacja wewnętrzna Kernela, nie dostępna dla użytkownika
"""

import asyncio
from typing import Dict, List, Callable, Any
from datetime import datetime
from enum import Enum


class EventType(Enum):
    """Typy zdarzeń Kernela"""
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop" 
    COMPONENT_ERROR = "component_error"
    RESOURCE_WARNING = "resource_warning"
    HEALTH_CHECK = "health_check"
    UPDATE_AVAILABLE = "update_available"
    SAFE_MODE_ENTER = "safe_mode_enter"
    SAFE_MODE_EXIT = "safe_mode_exit"


class KernelEvent:
    """Zdarzenie Kernela"""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any], source: str = "kernel"):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.now()
        self.processed = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type.value,
            'data': self.data,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'processed': self.processed
        }


class KernelEventBus:
    """
    Wewnętrzny EventBus Kernela
    
    Izolowany od zewnętrznego świata - służy tylko komunikacji
    wewnętrznej między komponentami Kernela
    """
    
    def __init__(self, logger):
        self.logger = logger
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.running = False
        self.processed_events = 0
        
        self.logger.debug("📡 Kernel EventBus initialized")
    
    async def start(self):
        """Uruchamia EventBus"""
        self.running = True
        self.logger.info("📡 Kernel EventBus started")
        
        # Uruchom processor zdarzeń w tle
        asyncio.create_task(self._event_processor())
    
    async def stop(self):
        """Zatrzymuje EventBus"""
        self.running = False
        self.logger.info("📡 Kernel EventBus stopped")
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """Subskrybuje zdarzenie"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"📡 Subscribed to {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Usuwa subskrypcję"""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
            self.logger.debug(f"📡 Unsubscribed from {event_type.value}")
    
    async def emit(self, event_type: EventType, data: Dict[str, Any], source: str = "kernel"):
        """Emituje zdarzenie"""
        event = KernelEvent(event_type, data, source)
        await self.event_queue.put(event)
        
        self.logger.debug(f"📡 Event emitted: {event_type.value}")
    
    async def process_events(self):
        """Przetwarza zdarzenia z kolejki"""
        try:
            # Przetwórz maksymalnie 10 zdarzeń na raz
            for _ in range(10):
                if self.event_queue.empty():
                    break
                
                event = await asyncio.wait_for(self.event_queue.get(), timeout=0.1)
                await self._process_event(event)
                
        except asyncio.TimeoutError:
            pass  # Brak zdarzeń do przetworzenia
        except Exception as e:
            self.logger.error(f"❌ Error processing events: {e}")
    
    async def _event_processor(self):
        """Ciągły processor zdarzeń w tle"""
        while self.running:
            try:
                await self.process_events()
                await asyncio.sleep(0.01)  # Krótka przerwa
                
            except Exception as e:
                self.logger.error(f"❌ Event processor error: {e}")
                await asyncio.sleep(1)
    
    async def _process_event(self, event: KernelEvent):
        """Przetwarza pojedyncze zdarzenie"""
        try:
            if event.event_type in self.subscribers:
                # Wywołaj wszystkich subskrybentów
                for callback in self.subscribers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        self.logger.error(f"❌ Callback error for {event.event_type.value}: {e}")
            
            event.processed = True
            self.processed_events += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing event {event.event_type.value}: {e}")
    
    def is_healthy(self) -> bool:
        """Sprawdza zdrowie EventBus"""
        return self.running and self.event_queue.qsize() < 1000  # Nie za duża kolejka
    
    async def restart(self):
        """Restartuje EventBus"""
        self.logger.info("🔄 Restarting Kernel EventBus")
        await self.stop()
        await asyncio.sleep(0.1)
        await self.start()
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status EventBus"""
        return {
            'running': self.running,
            'queue_size': self.event_queue.qsize(),
            'processed_events': self.processed_events,
            'subscribers': {et.value: len(subs) for et, subs in self.subscribers.items()}
        }
