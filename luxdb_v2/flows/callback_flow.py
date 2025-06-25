
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
        
        # Namespace diagnostyki
        diagnostic_ns = self.create_namespace('diagnostics')
        
        def on_container_error(event):
            """Handler błędów kontenerów - analizuje i generuje poprawki"""
            error_data = event.data
            container_id = error_data.get('container_id')
            function_name = error_data.get('function_name')
            error_message = error_data.get('error_message')
            
            self.engine.logger.info(f"🔬 Diagnostyka błędu kontenera {container_id} w funkcji {function_name}")
            
            # Pobierz kontener do analizy
            if hasattr(self.engine, 'container_manager'):
                container = self.engine.container_manager.get_container(container_id)
                if container:
                    # Generuj sugestię poprawki na podstawie błędu
                    fix_suggestion = self._analyze_error_and_suggest_fix(error_data, container)
                    
                    # Wyślij poprawkę z powrotem do kontenera
                    if fix_suggestion.get('success'):
                        self.emit_event('diagnostics', 'fix_ready', {
                            'container_id': container_id,
                            'function_name': function_name,
                            'fix_suggestion': fix_suggestion['fix'],
                            'diagnostic_confidence': fix_suggestion.get('confidence', 0.7)
                        })
                    else:
                        self.engine.logger.warning(f"⚠️ Nie udało się wygenerować poprawki dla {container_id}")
        
        def on_fix_ready(event):
            """Handler gotowej poprawki - aplikuje ją do funkcji"""
            fix_data = event.data
            container_id = fix_data.get('container_id')
            function_name = fix_data.get('function_name')
            fix_suggestion = fix_data.get('fix_suggestion')
            
            self.engine.logger.info(f"🔧 Aplikowanie poprawki dla funkcji {function_name} w kontenerze {container_id}")
            
            if hasattr(self.engine, 'container_manager'):
                container = self.engine.container_manager.get_container(container_id)
                if container:
                    # Zastosuj poprawkę
                    fix_result = self.engine.container_manager._apply_dynamic_function_fix(
                        function_name, container, fix_suggestion
                    )
                    
                    if fix_result['success']:
                        # Spróbuj ponownie wywołać funkcję
                        self.emit_event('diagnostics', 'retry_function', {
                            'container_id': container_id,
                            'function_name': function_name,
                            'fix_applied': True
                        })
                        
                        self.engine.logger.info(f"✅ Poprawka zastosowana pomyślnie dla {function_name}")
                    else:
                        self.engine.logger.error(f"❌ Nie udało się zastosować poprawki: {fix_result.get('error')}")
        
        def on_retry_function(event):
            """Handler ponownego wywołania funkcji po poprawce"""
            retry_data = event.data
            container_id = retry_data.get('container_id')
            function_name = retry_data.get('function_name')
            
            self.engine.logger.info(f"🔄 Ponowne wywołanie funkcji {function_name} dla kontenera {container_id}")
            
            # Tutaj mógłbyś automatycznie ponownie wywołać funkcję
            # ale zostawiam to jako opcjonalne - może lepiej pozwolić aplikacji decydować
        
        # Rejestruj callbacki diagnostyczne
        diagnostic_ns.on('container_error', on_container_error, CallbackPriority.HIGH)
        diagnostic_ns.on('fix_ready', on_fix_ready, CallbackPriority.HIGH)
        diagnostic_ns.on('retry_function', on_retry_function, CallbackPriority.NORMAL)
    
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
    
    def _analyze_error_and_suggest_fix(self, error_data: Dict[str, Any], container) -> Dict[str, Any]:
        """Analizuje błąd i generuje sugestię poprawki"""
        
        error_message = error_data.get('error_message', '')
        function_name = error_data.get('function_name')
        expected_params = error_data.get('expected_params', {})
        container_data = error_data.get('container_data', {})
        
        fix_suggestion = {
            'success': False,
            'fix': {},
            'confidence': 0.0
        }
        
        try:
            # Analiza typowych błędów
            if 'type' in error_message.lower() and 'expected' in error_message.lower():
                # Błąd typu - dodaj konwersję typów
                fix_suggestion = {
                    'success': True,
                    'fix': {
                        'fix_type': 'type_conversion',
                        'description': f'Funkcja {function_name} z automatyczną konwersją typów',
                        'parameters': self._generate_type_safe_params(expected_params, container_data),
                        'error_handling': {
                            'type_conversion': True,
                            'fallback_values': True
                        },
                        'validation_rules': {
                            'auto_convert_types': True,
                            'strict_validation': False
                        }
                    },
                    'confidence': 0.8
                }
            
            elif 'missing' in error_message.lower() or 'required' in error_message.lower():
                # Brakujący parametr - dodaj wartości domyślne
                fix_suggestion = {
                    'success': True,
                    'fix': {
                        'fix_type': 'missing_parameter_handling',
                        'description': f'Funkcja {function_name} z wartościami domyślnymi',
                        'parameters': self._generate_params_with_defaults(expected_params),
                        'error_handling': {
                            'default_values': True,
                            'optional_params': True
                        },
                        'validation_rules': {
                            'allow_missing_params': True,
                            'use_defaults': True
                        }
                    },
                    'confidence': 0.9
                }
            
            elif 'division by zero' in error_message.lower() or 'zerodivisionerror' in error_message.lower():
                # Błąd dzielenia przez zero
                fix_suggestion = {
                    'success': True,
                    'fix': {
                        'fix_type': 'division_safety',
                        'description': f'Funkcja {function_name} z zabezpieczeniem przed dzieleniem przez zero',
                        'parameters': expected_params,
                        'error_handling': {
                            'zero_division_check': True,
                            'fallback_result': 'infinity_or_none'
                        },
                        'validation_rules': {
                            'check_divisor': True
                        }
                    },
                    'confidence': 0.95
                }
            
            elif 'keyerror' in error_message.lower() or 'key' in error_message.lower():
                # Błąd brakującego klucza
                fix_suggestion = {
                    'success': True,
                    'fix': {
                        'fix_type': 'safe_key_access',
                        'description': f'Funkcja {function_name} z bezpiecznym dostępem do kluczy',
                        'parameters': expected_params,
                        'error_handling': {
                            'safe_dict_access': True,
                            'default_key_values': True
                        },
                        'validation_rules': {
                            'check_key_existence': True
                        }
                    },
                    'confidence': 0.85
                }
            
            else:
                # Ogólny błąd - dodaj try-catch wrapper
                fix_suggestion = {
                    'success': True,
                    'fix': {
                        'fix_type': 'general_error_handling',
                        'description': f'Funkcja {function_name} z ogólnym mechanizmem obsługi błędów',
                        'parameters': expected_params,
                        'error_handling': {
                            'try_catch_wrapper': True,
                            'graceful_degradation': True,
                            'error_logging': True
                        },
                        'validation_rules': {
                            'permissive_mode': True
                        }
                    },
                    'confidence': 0.6
                }
        
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd podczas analizy błędu: {e}")
        
        return fix_suggestion
    
    def _generate_type_safe_params(self, expected_params: Dict[str, Any], container_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generuje parametry z bezpieczną konwersją typów"""
        params = []
        
        for param_name, param_config in expected_params.items():
            param_type = param_config.get('type', 'Any')
            
            param_def = {
                'name': param_name,
                'type': param_type,
                'auto_convert': True,
                'description': f'Parametr {param_name} z automatyczną konwersją na {param_type}'
            }
            
            # Dodaj konwersję na podstawie typu
            if param_type == 'int':
                param_def['conversion_fallback'] = 0
            elif param_type == 'float':
                param_def['conversion_fallback'] = 0.0
            elif param_type == 'str':
                param_def['conversion_fallback'] = ''
            elif param_type == 'bool':
                param_def['conversion_fallback'] = False
            elif param_type == 'list':
                param_def['conversion_fallback'] = []
            elif param_type == 'dict':
                param_def['conversion_fallback'] = {}
            
            params.append(param_def)
        
        return params
    
    def _generate_params_with_defaults(self, expected_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generuje parametry z wartościami domyślnymi"""
        params = []
        
        for param_name, param_config in expected_params.items():
            param_type = param_config.get('type', 'Any')
            required = param_config.get('required', False)
            
            param_def = {
                'name': param_name,
                'type': param_type,
                'required': False,  # Zmień na opcjonalne
                'description': f'Parametr {param_name} z wartością domyślną'
            }
            
            # Dodaj wartość domyślną
            if param_type == 'int':
                param_def['default'] = 0
            elif param_type == 'float':
                param_def['default'] = 0.0
            elif param_type == 'str':
                param_def['default'] = ''
            elif param_type == 'bool':
                param_def['default'] = False
            elif param_type == 'list':
                param_def['default'] = []
            elif param_type == 'dict':
                param_def['default'] = {}
            else:
                param_def['default'] = None
            
            params.append(param_def)
        
        return params
