
"""
LuxDB Callback System - System callbacków dla komunikacji astralnej
Wspiera Socket.IO oraz komunikację wewnętrzną między bytami astralnymi
"""

import asyncio
import inspect
import threading
import weakref
from datetime import datetime
from typing import Dict, List, Callable, Any, Optional, Union, Set
from collections import defaultdict
from functools import wraps
import json
import uuid

from .utils.logging_utils import get_db_logger
from .utils.error_handlers import LuxDBError

logger = get_db_logger()

class AstralCallbackError(LuxDBError):
    """Błędy systemu callbacków astralnych"""
    pass

class CallbackPriority:
    """Priorytety wykonywania callbacków"""
    CRITICAL = 0    # Krytyczne - wykonywane jako pierwsze
    HIGH = 1        # Wysokie
    NORMAL = 2      # Normalne (domyślne)
    LOW = 3         # Niskie
    BACKGROUND = 4  # W tle - wykonywane jako ostatnie

class CallbackContext:
    """Kontekst wywołania callback"""
    
    def __init__(self, event_name: str, source: str, data: Any = None, 
                 session_id: str = None, user_id: str = None):
        self.event_name = event_name
        self.source = source
        self.data = data
        self.session_id = session_id
        self.user_id = user_id
        self.timestamp = datetime.now()
        self.callback_id = str(uuid.uuid4())
        self.metadata = {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje kontekst do słownika"""
        return {
            'event_name': self.event_name,
            'source': self.source,
            'data': self.data,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'callback_id': self.callback_id,
            'metadata': self.metadata
        }

class CallbackRegistration:
    """Rejestracja callback z metadanymi"""
    
    def __init__(self, callback: Callable, priority: int = CallbackPriority.NORMAL,
                 once: bool = False, filters: Dict[str, Any] = None,
                 async_callback: bool = None):
        self.callback = callback
        self.priority = priority
        self.once = once
        self.filters = filters or {}
        self.registration_time = datetime.now()
        self.call_count = 0
        self.last_called = None
        self.registration_id = str(uuid.uuid4())
        
        # Auto-detect async callback
        if async_callback is None:
            self.is_async = asyncio.iscoroutinefunction(callback)
        else:
            self.is_async = async_callback
    
    def should_execute(self, context: CallbackContext) -> bool:
        """Sprawdza czy callback powinien być wykonany"""
        if not self.filters:
            return True
            
        for filter_key, filter_value in self.filters.items():
            if hasattr(context, filter_key):
                context_value = getattr(context, filter_key)
                if context_value != filter_value:
                    return False
            elif filter_key in context.metadata:
                if context.metadata[filter_key] != filter_value:
                    return False
            else:
                return False
        
        return True
    
    def execute(self, context: CallbackContext) -> Any:
        """Wykonuje callback"""
        self.call_count += 1
        self.last_called = datetime.now()
        
        try:
            if self.is_async:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.callback(context))
                # return asyncio.create_task()
            else:
                return self.callback(context)
        except Exception as e:
            logger.log_error(f"Błąd wykonania callback {self.registration_id}", e,
                           context={'event': context.event_name, 'source': context.source})
            raise AstralCallbackError(f"Callback execution failed: {e}")

class AstralCallbackManager:
    """
    Manager callbacków astralnych - centralny system zarządzania
    callbackami dla Socket.IO i komunikacji wewnętrznej
    """
    
    def __init__(self):
        self.callbacks: Dict[str, List[CallbackRegistration]] = defaultdict(list)
        self.global_callbacks: List[CallbackRegistration] = []
        self.namespace_callbacks: Dict[str, Dict[str, List[CallbackRegistration]]] = defaultdict(
            lambda: defaultdict(list)
        )
        
        # Thread safety
        self.callback_lock = threading.RLock()
        
        # Weak references dla automatycznego czyszczenia
        self.weak_refs: Set[weakref.ref] = set()
        
        # Statistyki
        self.stats = {
            'total_callbacks': 0,
            'total_executions': 0,
            'failed_executions': 0,
            'async_executions': 0
        }
        
        # Event loop dla async callbacks
        self.loop = None
        self.loop_thread = None
        
        logger.log_info("Inicjalizacja AstralCallbackManager")
    
    def _ensure_event_loop(self):
        """Zapewnia istnienie event loop dla async callbacks"""
        if self.loop is None or self.loop.is_closed():
            def run_loop():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
            
            self.loop_thread = threading.Thread(target=run_loop, daemon=True)
            self.loop_thread.start()
            
            # Czekaj na inicjalizację loop
            while self.loop is None:
                threading.Event().wait(0.01)
    
    def on(self, event_name: str, callback: Callable, 
           priority: int = CallbackPriority.NORMAL, once: bool = False,
           filters: Dict[str, Any] = None, namespace: str = None) -> str:
        """
        Rejestruje callback dla zdarzenia
        
        Args:
            event_name: Nazwa zdarzenia
            callback: Funkcja callback
            priority: Priorytet wykonania
            once: Czy wykonać tylko raz
            filters: Filtry dla kontekstu
            namespace: Namespace (opcjonalne)
        
        Returns:
            ID rejestracji
        """
        with self.callback_lock:
            registration = CallbackRegistration(
                callback=callback,
                priority=priority,
                once=once,
                filters=filters
            )
            
            if namespace:
                self.namespace_callbacks[namespace][event_name].append(registration)
            else:
                self.callbacks[event_name].append(registration)
            
            # Sortuj według priorytetu
            callback_list = (self.namespace_callbacks[namespace][event_name] 
                           if namespace else self.callbacks[event_name])
            callback_list.sort(key=lambda x: x.priority)
            
            self.stats['total_callbacks'] += 1
            
            logger.log_info(f"Zarejestrowano callback dla '{event_name}' "
                          f"(priorytet: {priority}, namespace: {namespace})")
            
            return registration.registration_id
    
    def off(self, event_name: str = None, callback_id: str = None, 
            namespace: str = None) -> int:
        """
        Wyrejestrowuje callbacki
        
        Args:
            event_name: Nazwa zdarzenia (None = wszystkie)
            callback_id: ID konkretnego callback
            namespace: Namespace
        
        Returns:
            Liczba usuniętych callbacków
        """
        removed_count = 0
        
        with self.callback_lock:
            if namespace:
                if event_name:
                    if callback_id:
                        # Usuń konkretny callback
                        callbacks = self.namespace_callbacks[namespace][event_name]
                        self.namespace_callbacks[namespace][event_name] = [
                            cb for cb in callbacks if cb.registration_id != callback_id
                        ]
                        removed_count = len(callbacks) - len(self.namespace_callbacks[namespace][event_name])
                    else:
                        # Usuń wszystkie callbacki dla zdarzenia w namespace
                        removed_count = len(self.namespace_callbacks[namespace][event_name])
                        self.namespace_callbacks[namespace][event_name] = []
                else:
                    # Usuń cały namespace
                    for event_callbacks in self.namespace_callbacks[namespace].values():
                        removed_count += len(event_callbacks)
                    del self.namespace_callbacks[namespace]
            else:
                if event_name:
                    if callback_id:
                        # Usuń konkretny callback
                        callbacks = self.callbacks[event_name]
                        self.callbacks[event_name] = [
                            cb for cb in callbacks if cb.registration_id != callback_id
                        ]
                        removed_count = len(callbacks) - len(self.callbacks[event_name])
                    else:
                        # Usuń wszystkie callbacki dla zdarzenia
                        removed_count = len(self.callbacks[event_name])
                        self.callbacks[event_name] = []
                else:
                    # Usuń wszystkie callbacki
                    for event_callbacks in self.callbacks.values():
                        removed_count += len(event_callbacks)
                    self.callbacks.clear()
        
        self.stats['total_callbacks'] -= removed_count
        logger.log_info(f"Usunięto {removed_count} callbacków")
        return removed_count
    
    def emit(self, event_name: str, data: Any = None, source: str = "unknown",
             session_id: str = None, user_id: str = None, namespace: str = None,
             **metadata) -> List[Any]:
        """
        Emituje zdarzenie i wykonuje wszystkie pasujące callbacki
        
        Args:
            event_name: Nazwa zdarzenia
            data: Dane zdarzenia
            source: Źródło zdarzenia
            session_id: ID sesji
            user_id: ID użytkownika
            namespace: Namespace
            **metadata: Dodatkowe metadane
        
        Returns:
            Lista wyników wykonania callbacków
        """
        context = CallbackContext(
            event_name=event_name,
            source=source,
            data=data,
            session_id=session_id,
            user_id=user_id
        )
        context.metadata.update(metadata)
        
        results = []
        callbacks_to_remove = []
        
        with self.callback_lock:
            # Pobierz callbacki do wykonania
            callbacks_to_execute = []
            
            # Globalne callbacki
            callbacks_to_execute.extend(self.global_callbacks)
            
            # Callbacki dla konkretnego zdarzenia
            if event_name in self.callbacks:
                callbacks_to_execute.extend(self.callbacks[event_name])
            
            # Callbacki z namespace
            if namespace and namespace in self.namespace_callbacks:
                if event_name in self.namespace_callbacks[namespace]:
                    callbacks_to_execute.extend(
                        self.namespace_callbacks[namespace][event_name]
                    )
            
            # Wykonaj callbacki
            for registration in callbacks_to_execute:
                if not registration.should_execute(context):
                    continue
                
                try:
                    result = registration.execute(context)
                    results.append(result)
                    
                    if registration.is_async:
                        self.stats['async_executions'] += 1
                    
                    # Oznacz do usunięcia jeśli "once"
                    if registration.once:
                        callbacks_to_remove.append(registration)
                    
                except Exception as e:
                    self.stats['failed_executions'] += 1
                    logger.log_error(f"Błąd wykonania callback dla '{event_name}'", e)
                    results.append(AstralCallbackError(str(e)))
                
                self.stats['total_executions'] += 1
            
            # Usuń callbacki "once"
            for registration in callbacks_to_remove:
                self._remove_registration(registration, namespace)
        
        logger.log_info(f"Emitowano '{event_name}' - wykonano {len(results)} callbacków")
        return results
    
    def _remove_registration(self, registration: CallbackRegistration, 
                           namespace: str = None):
        """Usuwa konkretną rejestrację callback"""
        if namespace:
            for event_name, callback_list in self.namespace_callbacks[namespace].items():
                if registration in callback_list:
                    callback_list.remove(registration)
                    break
        else:
            for event_name, callback_list in self.callbacks.items():
                if registration in callback_list:
                    callback_list.remove(registration)
                    break
            
            if registration in self.global_callbacks:
                self.global_callbacks.remove(registration)
    
    def on_global(self, callback: Callable, priority: int = CallbackPriority.NORMAL) -> str:
        """Rejestruje globalny callback dla wszystkich zdarzeń"""
        with self.callback_lock:
            registration = CallbackRegistration(
                callback=callback,
                priority=priority
            )
            
            self.global_callbacks.append(registration)
            self.global_callbacks.sort(key=lambda x: x.priority)
            
            self.stats['total_callbacks'] += 1
            
            logger.log_info(f"Zarejestrowano globalny callback (priorytet: {priority})")
            return registration.registration_id
    
    def create_namespace(self, namespace: str) -> 'NamespaceManager':
        """Tworzy manager dla namespace"""
        return NamespaceManager(self, namespace)
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki callbacków"""
        with self.callback_lock:
            total_registered = sum(len(callbacks) for callbacks in self.callbacks.values())
            total_namespace = sum(
                sum(len(callbacks) for callbacks in ns_callbacks.values())
                for ns_callbacks in self.namespace_callbacks.values()
            )
            
            return {
                **self.stats,
                'registered_callbacks': total_registered,
                'namespace_callbacks': total_namespace,
                'global_callbacks': len(self.global_callbacks),
                'namespaces': list(self.namespace_callbacks.keys())
            }
    
    def cleanup_weak_refs(self):
        """Czyści martwe weak references"""
        dead_refs = set()
        for ref in self.weak_refs:
            if ref() is None:
                dead_refs.add(ref)
        
        self.weak_refs -= dead_refs
        logger.log_info(f"Wyczyszczono {len(dead_refs)} martwych referencji")

class NamespaceManager:
    """Manager callbacków dla konkretnego namespace"""
    
    def __init__(self, callback_manager: AstralCallbackManager, namespace: str):
        self.callback_manager = callback_manager
        self.namespace = namespace
    
    def on(self, event_name: str, callback: Callable, 
           priority: int = CallbackPriority.NORMAL, once: bool = False,
           filters: Dict[str, Any] = None) -> str:
        """Rejestruje callback w namespace"""
        return self.callback_manager.on(
            event_name=event_name,
            callback=callback,
            priority=priority,
            once=once,
            filters=filters,
            namespace=self.namespace
        )
    
    def off(self, event_name: str = None, callback_id: str = None) -> int:
        """Wyrejestrowuje callbacki z namespace"""
        return self.callback_manager.off(
            event_name=event_name,
            callback_id=callback_id,
            namespace=self.namespace
        )
    
    def emit(self, event_name: str, data: Any = None, source: str = "namespace",
             session_id: str = None, user_id: str = None, **metadata) -> List[Any]:
        """Emituje zdarzenie w namespace"""
        return self.callback_manager.emit(
            event_name=event_name,
            data=data,
            source=source,
            session_id=session_id,
            user_id=user_id,
            namespace=self.namespace,
            **metadata
        )

class SocketIOCallbackIntegration:
    """Integracja z Socket.IO dla automatycznego mapowania callbacków"""
    
    def __init__(self, callback_manager: AstralCallbackManager):
        self.callback_manager = callback_manager
        self.socketio_handlers = {}
    
    def register_socketio_event(self, socketio_instance, event_name: str, 
                               namespace: str = None):
        """Rejestruje automatyczne mapowanie zdarzenia Socket.IO na callback"""
        
        def socketio_handler(*args, **kwargs):
            # Konwertuj argumenty Socket.IO na format callback
            data = args[0] if args else kwargs
            
            # Pobierz informacje o sesji z Socket.IO
            session_id = getattr(socketio_instance, 'sid', None)
            
            # Emituj przez system callbacków
            return self.callback_manager.emit(
                event_name=event_name,
                data=data,
                source="socketio",
                session_id=session_id,
                namespace=namespace
            )
        
        # Zarejestruj w Socket.IO
        socketio_instance.on_event(event_name, socketio_handler, namespace=namespace)
        
        self.socketio_handlers[f"{namespace or 'default'}:{event_name}"] = socketio_handler
        
        logger.log_info(f"Zarejestrowano integrację Socket.IO dla '{event_name}' "
                       f"(namespace: {namespace})")

# Decoratory dla łatwego używania
def astral_callback(event_name: str, priority: int = CallbackPriority.NORMAL,
                   once: bool = False, filters: Dict[str, Any] = None,
                   namespace: str = None):
    """Decorator do rejestracji funkcji jako callback"""
    def decorator(func: Callable):
        # Pobierz globalny manager (będzie utworzony później)
        manager = get_astral_callback_manager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Zarejestruj callback
        manager.on(
            event_name=event_name,
            callback=wrapper,
            priority=priority,
            once=once,
            filters=filters,
            namespace=namespace
        )
        
        return wrapper
    return decorator

def global_astral_callback(priority: int = CallbackPriority.NORMAL):
    """Decorator do rejestracji globalnego callback"""
    def decorator(func: Callable):
        manager = get_astral_callback_manager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        manager.on_global(callback=wrapper, priority=priority)
        return wrapper
    return decorator

# Singleton instance
_astral_callback_manager = None

def get_astral_callback_manager() -> AstralCallbackManager:
    """Zwraca singleton instance managera callbacków astralnych"""
    global _astral_callback_manager
    if _astral_callback_manager is None:
        _astral_callback_manager = AstralCallbackManager()
    return _astral_callback_manager

def reset_astral_callback_manager():
    """Resetuje manager callbacków (do testów)"""
    global _astral_callback_manager
    _astral_callback_manager = None
