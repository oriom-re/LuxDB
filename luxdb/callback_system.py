
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
from .callback_database_manager import CallbackDatabaseManager

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
                # Sprawdź czy jest aktywny event loop
                try:
                    loop = asyncio.get_running_loop()
                    # Jeśli jest aktywny loop, utwórz task
                    task = loop.create_task(self.callback(context))
                    return task
                except RuntimeError:
                    # Brak aktywnego loop - uruchom nowy
                    return asyncio.run(self.callback(context))
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
    
    def __init__(self, enable_database: bool = True):
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
        
        # Database manager dla persystencji
        self.database_enabled = enable_database
        self.db_manager = None
        if enable_database:
            self._init_database()
        
        logger.log_info("Inicjalizacja AstralCallbackManager")
    
    def _init_database(self):
        """Inicjalizuje manager bazy danych dla callbacków"""
        try:
            from .manager import DatabaseManager
            db_manager = DatabaseManager()
            self.db_manager = CallbackDatabaseManager(db_manager)
            logger.log_info("Inicjalizacja bazy danych callbacków zakończona")
        except Exception as e:
            logger.log_error("init_callback_database", e)
            self.database_enabled = False
    
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
            
            # Zapisz do bazy danych jeśli włączona
            if self.database_enabled and self.db_manager:
                try:
                    self.db_manager.register_callback(
                        registration_id=registration.registration_id,
                        event_name=event_name,
                        callback_function=getattr(callback, '__name__', str(callback)),
                        priority=priority,
                        is_async=registration.is_async,
                        once=once,
                        filters=filters,
                        namespace=namespace
                    )
                except Exception as e:
                    logger.log_error("register_callback_to_db", e)
            
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
        
        # Utwórz event w bazie danych jeśli włączona
        event_id = None
        if self.database_enabled and self.db_manager:
            try:
                event_id = self.db_manager.create_event(
                    event_name=event_name,
                    source=source,
                    data=data,
                    session_id=session_id,
                    user_id=user_id,
                    namespace=namespace,
                    **metadata
                )
            except Exception as e:
                logger.log_error("create_event_in_db", e)
        
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
                
                # Rozpocznij śledzenie wykonania w bazie danych
                execution_id = None
                if self.database_enabled and self.db_manager and event_id:
                    try:
                        # Znajdź odpowiedni task_id w bazie
                        pending_tasks = self.db_manager.get_pending_tasks(event_name, namespace)
                        matching_task = next((t for t in pending_tasks if t['registration_id'] == registration.registration_id), None)
                        
                        if matching_task:
                            execution_id = self.db_manager.start_execution(
                                task_id=matching_task['id'],
                                event_id=event_id,
                                context_data=context.to_dict()
                            )
                    except Exception as e:
                        logger.log_error("start_execution_tracking", e)
                
                try:
                    result = registration.execute(context)
                    
                    # Obsłuż wyniki asynchroniczne
                    if registration.is_async and asyncio.iscoroutine(result):
                        # Jeśli to coroutine, uruchom ją
                        try:
                            loop = asyncio.get_running_loop()
                            task = loop.create_task(result)
                            results.append(task)
                        except RuntimeError:
                            # Brak event loop - uruchom synchronicznie
                            result = asyncio.run(result)
                            results.append(result)
                    elif hasattr(result, '__await__'):
                        # Jeśli to task lub future
                        results.append(result)
                    else:
                        results.append(result)
                    
                    # Zakończ śledzenie wykonania w bazie danych
                    if execution_id and self.database_enabled and self.db_manager:
                        try:
                            self.db_manager.complete_execution(execution_id, result)
                        except Exception as e:
                            logger.log_error("complete_execution_tracking", e)
                    
                    if registration.is_async:
                        self.stats['async_executions'] += 1
                    
                    # Oznacz do usunięcia jeśli "once"
                    if registration.once:
                        callbacks_to_remove.append(registration)
                    
                except Exception as e:
                    # Zakończ śledzenie z błędem
                    if execution_id and self.database_enabled and self.db_manager:
                        try:
                            self.db_manager.complete_execution(execution_id, error=str(e))
                        except Exception as db_e:
                            logger.log_error("complete_execution_tracking_error", db_e)
                    
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
            
            stats = {
                **self.stats,
                'registered_callbacks': total_registered,
                'namespace_callbacks': total_namespace,
                'global_callbacks': len(self.global_callbacks),
                'namespaces': list(self.namespace_callbacks.keys()),
                'database_enabled': self.database_enabled
            }
            
            # Dodaj statystyki z bazy danych jeśli dostępne
            if self.database_enabled and self.db_manager:
                try:
                    db_stats = self.db_manager.generate_stats()
                    stats['database_stats'] = db_stats
                except Exception as e:
                    logger.log_error("get_database_stats", e)
                    stats['database_stats'] = {"error": str(e)}
            
            return stats
    
    def cleanup_weak_refs(self):
        """Czyści martwe weak references"""
        dead_refs = set()
        for ref in self.weak_refs:
            if ref() is None:
                dead_refs.add(ref)
        
        self.weak_refs -= dead_refs
        logger.log_info(f"Wyczyszczono {len(dead_refs)} martwych referencji")
    
    async def wait_for_async_results(self, results: List[Any]) -> List[Any]:
        """Oczekuje na wyniki asynchronicznych callbacków"""
        final_results = []
        
        for result in results:
            if asyncio.iscoroutine(result) or hasattr(result, '__await__'):
                try:
                    awaited_result = await result
                    final_results.append(awaited_result)
                except Exception as e:
                    final_results.append(AstralCallbackError(str(e)))
            else:
                final_results.append(result)
        
        return final_results
    
    async def stream_async_results(self, results: List[Any]):
        """Generator zwracający wyniki asynchronicznych callbacków w miarę ukończenia"""
        async_tasks = []
        sync_results = []
        
        # Rozdziel synchroniczne i asynchroniczne wyniki
        for i, result in enumerate(results):
            if asyncio.iscoroutine(result) or hasattr(result, '__await__'):
                async_tasks.append((i, result))
            else:
                sync_results.append((i, result))
                
        # Najpierw zwróć synchroniczne wyniki
        for index, result in sync_results:
            yield {'index': index, 'result': result, 'completed_at': datetime.now()}
        
        # Następnie zwracaj asynchroniczne w miarę ukończenia
        if async_tasks:
            # Utwórz tasks dla asynchronicznych callbacków
            pending = {}
            for index, task in async_tasks:
                if asyncio.iscoroutine(task):
                    # Jeśli to coroutine, utwórz task
                    pending[asyncio.create_task(task)] = index
                elif hasattr(task, '__await__'):
                    # Jeśli to już task/future, użyj bezpośrednio
                    pending[task] = index
            
            while pending:
                done, pending_set = await asyncio.wait(pending.keys(), return_when=asyncio.FIRST_COMPLETED)
                
                # Aktualizuj pending tasks
                pending = {task: index for task, index in pending.items() if task in pending_set}
                
                for task in done:
                    original_index = next(index for t, index in pending.items() if t == task) if task in pending else None
                    if original_index is None:
                        # Znajdź index dla ukończonego taska
                        for t, idx in async_tasks:
                            if hasattr(t, '__await__') and task.get_coro() == t:
                                original_index = idx
                                break
                    
                    try:
                        result = await task
                        yield {
                            'index': original_index, 
                            'result': result, 
                            'completed_at': datetime.now()
                        }
                    except Exception as e:
                        yield {
                            'index': original_index, 
                            'result': AstralCallbackError(str(e)), 
                            'completed_at': datetime.now()
                        }
    
    def get_async_results_with_callbacks(self, results: List[Any], 
                                        on_result_ready: Callable = None) -> List[Any]:
        """Zwraca wyniki z callbackiem dla każdego ukończonego zadania"""
        async_tasks = []
        final_results = [None] * len(results)
        
        def set_result(index: int, result: Any):
            final_results[index] = result
            if on_result_ready:
                on_result_ready(index, result)
        
        # Przetwórz wyniki
        for i, result in enumerate(results):
            if asyncio.iscoroutine(result) or hasattr(result, '__await__'):
                # Dla async - utwórz task z callbackiem
                async def handle_async_result(idx, async_result):
                    try:
                        if asyncio.iscoroutine(async_result):
                            completed_result = await async_result
                        else:
                            completed_result = await async_result
                        set_result(idx, completed_result)
                        return completed_result
                    except Exception as e:
                        error_result = AstralCallbackError(str(e))
                        set_result(idx, error_result)
                        return error_result
                
                # Uruchom w tle
                try:
                    loop = asyncio.get_running_loop()
                    task = loop.create_task(handle_async_result(i, result))
                    async_tasks.append(task)
                except RuntimeError:
                    # Brak event loop - uruchom synchronicznie
                    sync_result = asyncio.run(handle_async_result(i, result))
                    set_result(i, sync_result)
            else:
                # Dla sync - ustaw od razu
                set_result(i, result)
        
        return final_results

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
            return self.callback_manager.emit(event_name, data)

    
    def get_execution_history(self, event_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera historię wykonań callbacków z bazy danych"""
        if not self.database_enabled or not self.db_manager:
            return []
        
        try:
            return self.db_manager.get_execution_history(event_name, limit)
        except Exception as e:
            logger.log_error("get_execution_history", e)
            return []
    
    def cleanup_old_callbacks(self, days_old: int = 30):
        """Czyści stare dane callbacków z bazy danych"""
        if not self.database_enabled or not self.db_manager:
            return
        
        try:
            return self.db_manager.cleanup_old_data(days_old)
        except Exception as e:
            logger.log_error("cleanup_old_callbacks", e)
    
    def get_pending_executions(self) -> List[Dict[str, Any]]:
        """Pobiera oczekujące wykonania callbacków"""
        if not self.database_enabled or not self.db_manager:
            return []
        
        try:
            return self.db_manager.get_pending_tasks()
        except Exception as e:
            logger.log_error("get_pending_executions", e)
            return []
    
    def create_stats_snapshot(self, period_type: str = "hour"):
        """Tworzy snapshot statystyk callbacków"""
        if not self.database_enabled or not self.db_manager:
            return
        
        try:
            self.db_manager.create_stats_snapshot(period_type)
        except Exception as e:
            logger.log_error("create_stats_snapshot", e)
    
    def get_period_stats(self, period_type: str = "day", periods_back: int = 7) -> List[Dict[str, Any]]:
        """Pobiera statystyki dla ostatnich okresów"""
        if not self.database_enabled or not self.db_manager:
            return []
        
        try:
            return self.db_manager.get_stats_for_period(period_type, periods_back)
        except Exception as e:
            logger.log_error("get_period_stats", e)
            return []
        
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
