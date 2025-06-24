
"""
🔄 CallbackFlow - Przepływ Astralnych Callbacków

Zarządza wewnętrznymi callbackami i reakcjami systemu na wydarzenia
"""

import asyncio
from typing import Dict, Any, List, Callable, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import time


class CallbackPriority(Enum):
    """Priorytety callbacków"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CallbackEvent:
    """Wydarzenie callback"""
    event_type: str
    data: Any
    priority: CallbackPriority
    timestamp: datetime
    source: str
    callback_id: str


class CallbackNamespace:
    """Namespace dla callbacków"""
    
    def __init__(self, name: str):
        self.name = name
        self.callbacks: Dict[str, List[Callable]] = {}
        self.event_history: List[CallbackEvent] = []
    
    def on(self, event_type: str, callback: Callable, priority: CallbackPriority = CallbackPriority.NORMAL):
        """Rejestruje callback"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        
        self.callbacks[event_type].append({
            'callback': callback,
            'priority': priority,
            'registered_at': datetime.now()
        })
        
        # Sortuj po priorytecie
        self.callbacks[event_type].sort(key=lambda x: x['priority'].value, reverse=True)
    
    def off(self, event_type: str, callback: Callable):
        """Usuwa callback"""
        if event_type in self.callbacks:
            self.callbacks[event_type] = [
                cb for cb in self.callbacks[event_type] 
                if cb['callback'] != callback
            ]
    
    def emit(self, event_type: str, data: Any = None, source: str = "unknown") -> List[Any]:
        """Emituje wydarzenie"""
        if event_type not in self.callbacks:
            return []
        
        # Zapisz w historii
        event = CallbackEvent(
            event_type=event_type,
            data=data,
            priority=CallbackPriority.NORMAL,
            timestamp=datetime.now(),
            source=source,
            callback_id=f"{self.name}:{event_type}:{int(time.time())}"
        )
        
        self.event_history.append(event)
        
        # Ogranicz historię
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]
        
        results = []
        
        for cb_info in self.callbacks[event_type]:
            try:
                result = cb_info['callback'](event)
                results.append(result)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        return results
    
    def get_event_history(self, event_type: Optional[str] = None, limit: int = 10) -> List[CallbackEvent]:
        """Zwraca historię wydarzeń"""
        history = self.event_history
        
        if event_type:
            history = [e for e in history if e.event_type == event_type]
        
        return history[-limit:]


class CallbackFlow:
    """
    Przepływ callbacków - zarządza wewnętrznymi reakcjami systemu
    """
    
    def __init__(self, astral_engine, config: Dict[str, Any]):
        self.engine = astral_engine
        self.config = config
        
        self.namespaces: Dict[str, CallbackNamespace] = {}
        self.event_queue = queue.Queue()
        
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        
        self.processed_events = 0
        self.start_time: Optional[datetime] = None
        
        self._setup_core_callbacks()
    
    def _setup_core_callbacks(self):
        """Konfiguruje podstawowe callbacki systemu"""
        
        # Namespace systemowy
        system_ns = self.create_namespace('system')
        
        def on_meditation_completed(event):
            """Callback po medytacji"""
            meditation_data = event.data
            self.engine.logger.info(f"🧘 Medytacja zakończona: {meditation_data.get('harmony_score', 0):.1f}/100")
            
            # Jeśli harmonia niska, sugeruj harmonizację
            if meditation_data.get('harmony_score', 100) < 70:
                self.emit_event('system', 'harmony_warning', {
                    'score': meditation_data.get('harmony_score'),
                    'recommendation': 'Rozważ harmonizację systemu'
                })
        
        def on_harmony_warning(event):
            """Callback dla ostrzeżeń harmonii"""
            warning_data = event.data
            self.engine.logger.warning(f"⚠️ Ostrzeżenie harmonii: {warning_data.get('recommendation')}")
        
        def on_being_manifested(event):
            """Callback po manifestacji bytu"""
            being_data = event.data
            self.engine.logger.info(f"✨ Nowy byt zmanifestowany: {being_data.get('soul_id')}")
            
            # Powiadom WebSocket jeśli aktywny
            if self.engine.ws_flow and hasattr(self.engine.ws_flow, 'notify_being_event'):
                asyncio.create_task(
                    self.engine.ws_flow.notify_being_event(
                        being_data.get('realm', 'unknown'),
                        'manifested',
                        being_data
                    )
                )
        
        def on_realm_connected(event):
            """Callback po połączeniu z wymiarem"""
            realm_data = event.data
            self.engine.logger.info(f"🌍 Wymiar połączony: {realm_data.get('name')}")
        
        def on_system_error(event):
            """Callback dla błędów systemowych"""
            error_data = event.data
            self.engine.logger.error(f"❌ Błąd systemu: {error_data.get('message')}")
            
            # Próba auto-naprawy
            if error_data.get('auto_heal', False):
                self.emit_event('system', 'auto_heal_requested', error_data)
        
        # Rejestruj callbacki
        system_ns.on('meditation_completed', on_meditation_completed, CallbackPriority.NORMAL)
        system_ns.on('harmony_warning', on_harmony_warning, CallbackPriority.HIGH)
        system_ns.on('being_manifested', on_being_manifested, CallbackPriority.NORMAL)
        system_ns.on('realm_connected', on_realm_connected, CallbackPriority.NORMAL)
        system_ns.on('system_error', on_system_error, CallbackPriority.CRITICAL)
    
    def create_namespace(self, name: str) -> CallbackNamespace:
        """
        Tworzy nowy namespace dla callbacków
        
        Args:
            name: Nazwa namespace
            
        Returns:
            Nowy namespace
        """
        if name in self.namespaces:
            return self.namespaces[name]
        
        namespace = CallbackNamespace(name)
        self.namespaces[name] = namespace
        
        self.engine.logger.info(f"🔄 Utworzono namespace callbacków: {name}")
        return namespace
    
    def get_namespace(self, name: str) -> Optional[CallbackNamespace]:
        """
        Pobiera namespace po nazwie
        
        Args:
            name: Nazwa namespace
            
        Returns:
            Namespace lub None
        """
        return self.namespaces.get(name)
    
    def emit_event(self, namespace: str, event_type: str, data: Any = None, source: str = "callback_flow") -> List[Any]:
        """
        Emituje wydarzenie w namespace
        
        Args:
            namespace: Nazwa namespace
            event_type: Typ wydarzenia
            data: Dane wydarzenia
            source: Źródło wydarzenia
            
        Returns:
            Lista wyników callbacków
        """
        ns = self.get_namespace(namespace)
        if not ns:
            self.engine.logger.warning(f"Namespace '{namespace}' nie istnieje")
            return []
        
        results = ns.emit(event_type, data, source)
        self.processed_events += 1
        
        return results
    
    def emit_event_async(self, namespace: str, event_type: str, data: Any = None, source: str = "callback_flow"):
        """
        Emituje wydarzenie asynchronicznie (przez kolejkę)
        
        Args:
            namespace: Nazwa namespace  
            event_type: Typ wydarzenia
            data: Dane wydarzenia
            source: Źródło wydarzenia
        """
        event = {
            'namespace': namespace,
            'event_type': event_type,
            'data': data,
            'source': source,
            'timestamp': datetime.now()
        }
        
        self.event_queue.put(event)
    
    def _worker_loop(self):
        """Pętla workera do przetwarzania asynchronicznych wydarzeń"""
        while self._running:
            try:
                # Pobierz wydarzenie z kolejki (timeout 1 sekunda)
                event = self.event_queue.get(timeout=1.0)
                
                # Przetworz wydarzenie
                self.emit_event(
                    event['namespace'],
                    event['event_type'],
                    event['data'],
                    event['source']
                )
                
                self.event_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🔄 Błąd workera callbacków: {e}")
    
    def start(self) -> None:
        """Uruchamia przepływ callbacków"""
        if self._running:
            self.engine.logger.warning("CallbackFlow już działa")
            return
        
        self.start_time = datetime.now()
        self._running = True
        
        # Uruchom worker thread
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        
        self.engine.logger.info("🔄 Callback Flow aktywowany")
    
    def stop(self) -> None:
        """Zatrzymuje przepływ callbacków"""
        self._running = False
        
        # Poczekaj na zakończenie kolejki
        if not self.event_queue.empty():
            self.event_queue.join()
        
        self.engine.logger.info("🔄 Callback Flow zatrzymany")
    
    def is_running(self) -> bool:
        """Sprawdza czy przepływ działa"""
        return self._running
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu"""
        total_callbacks = sum(
            len(callbacks) 
            for ns in self.namespaces.values() 
            for callbacks in ns.callbacks.values()
        )
        
        return {
            'type': 'callback_flow',
            'running': self._running,
            'namespaces': list(self.namespaces.keys()),
            'total_callbacks': total_callbacks,
            'processed_events': self.processed_events,
            'queue_size': self.event_queue.qsize(),
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00'
        }
    
    def get_namespace_stats(self, namespace: str) -> Dict[str, Any]:
        """Zwraca statystyki namespace"""
        ns = self.get_namespace(namespace)
        if not ns:
            return {'error': 'Namespace nie istnieje'}
        
        total_callbacks = sum(len(callbacks) for callbacks in ns.callbacks.values())
        
        return {
            'namespace': namespace,
            'event_types': list(ns.callbacks.keys()),
            'total_callbacks': total_callbacks,
            'event_history_count': len(ns.event_history),
            'recent_events': [
                {
                    'event_type': e.event_type,
                    'timestamp': e.timestamp.isoformat(),
                    'source': e.source
                }
                for e in ns.get_event_history(limit=5)
            ]
        }
    
    def clear_history(self, namespace: Optional[str] = None) -> int:
        """
        Czyści historię wydarzeń
        
        Args:
            namespace: Nazwa namespace (None = wszystkie)
            
        Returns:
            Liczba usuniętych wydarzeń
        """
        total_cleared = 0
        
        if namespace:
            ns = self.get_namespace(namespace)
            if ns:
                cleared = len(ns.event_history)
                ns.event_history.clear()
                total_cleared = cleared
        else:
            for ns in self.namespaces.values():
                total_cleared += len(ns.event_history)
                ns.event_history.clear()
        
        return total_cleared
