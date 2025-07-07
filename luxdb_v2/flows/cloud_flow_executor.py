
"""
☁️ CloudFlowExecutor - Wykonawca Flow z Chmury

Wykonuje flow generowane dynamicznie z bazy danych.
Kod może być naprawiany przez RepairFlow.
"""

import asyncio
import threading
import queue
import hashlib
import tempfile
import os
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class CloudFlowExecutor:
    """
    Wykonawca flow z chmury - ładuje i wykonuje dynamiczne flow
    """

    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Załadowane flow z chmury
        self.cloud_flows: Dict[str, Dict[str, Any]] = {}
        
        # Kolejka zadań
        self.execution_queue = queue.PriorityQueue()
        
        # Worker
        self._execution_worker: Optional[threading.Thread] = None
        self._running = False
        
        # Callback namespace
        self.callback_namespace: Optional[CallbackNamespace] = None
        
        # Statystyki
        self.execution_statistics = {
            'flows_loaded': 0,
            'flows_executed': 0,
            'execution_errors': 0,
            'repairs_requested': 0
        }
        
        self.start_time = datetime.now()

    def initialize(self):
        """Inicjalizuje wykonawcę flow z chmury"""
        
        # Utwórz namespace callbacków
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('cloud_executor')
            self._setup_cloud_callbacks()
        
        # Uruchom worker
        self._running = True
        self._execution_worker = threading.Thread(target=self._execution_worker_loop, daemon=True)
        self._execution_worker.start()
        
        self.engine.logger.info("☁️ CloudFlowExecutor zainicjalizowany")

    def start(self) -> bool:
        """Uruchamia wykonawcę flow z chmury"""
        if self._running:
            self.engine.logger.warning("CloudFlowExecutor już działa")
            return True

        self.initialize()
        return True

    def _setup_cloud_callbacks(self):
        """Konfiguruje callbacki dla wykonawcy flow"""
        if not self.callback_namespace:
            return

        def on_flow_execution_error(event):
            """Callback gdy wystąpi błąd wykonania flow"""
            error_data = event.data
            flow_id = error_data.get('flow_id')
            
            # Zgłoś do RepairFlow
            if hasattr(self.engine, 'repair_flow'):
                self.engine.repair_flow.request_flow_repair(flow_id, error_data)
                self.execution_statistics['repairs_requested'] += 1

        def on_flow_repaired(event):
            """Callback gdy flow zostanie naprawiony"""
            repair_data = event.data
            flow_id = repair_data.get('flow_id')
            
            # Przeładuj naprawiony flow
            self._reload_cloud_flow(flow_id)

        # Rejestruj callbacki
        self.callback_namespace.on('flow_execution_error', on_flow_execution_error, CallbackPriority.HIGH)
        self.callback_namespace.on('flow_repaired', on_flow_repaired, CallbackPriority.NORMAL)

    def load_flow_from_cloud(self, flow_name: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Ładuje flow z bazy danych/chmury
        """
        try:
            # Sprawdź czy już załadowany
            if flow_name in self.cloud_flows and not force_reload:
                return {'success': True, 'message': 'Flow już załadowany', 'cached': True}

            # Pobierz flow z bazy
            flow_realm = self.engine.realms.get('astral_prime')
            if not flow_realm:
                return {'success': False, 'error': 'Brak dostępu do bazy flow'}

            # Znajdź flow w bazie
            flow_results = flow_realm.contemplate('find_cloud_flow', flow_name=flow_name)
            
            if not flow_results:
                return {'success': False, 'error': f'Flow {flow_name} nie znaleziony w chmurze'}

            flow_being = flow_results[0]
            flow_code = flow_being.materialna.flow_code
            flow_config = flow_being.materialna.flow_config
            
            # Kompiluj i załaduj flow
            compiled_flow = self._compile_cloud_flow(flow_name, flow_code, flow_config)
            
            if compiled_flow['success']:
                self.cloud_flows[flow_name] = {
                    'code': flow_code,
                    'config': flow_config,
                    'compiled': compiled_flow['flow_class'],
                    'instance': None,
                    'loaded_at': datetime.now(),
                    'hash': hashlib.sha256(flow_code.encode()).hexdigest()[:16]
                }
                
                self.execution_statistics['flows_loaded'] += 1
                self.engine.logger.info(f"☁️ Flow '{flow_name}' załadowany z chmury")
                
                return {'success': True, 'flow_hash': self.cloud_flows[flow_name]['hash']}
            else:
                return compiled_flow

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd ładowania flow z chmury: {e}")
            return {'success': False, 'error': str(e)}

    def _compile_cloud_flow(self, flow_name: str, flow_code: str, flow_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kompiluje kod flow z chmury
        """
        try:
            # Utwórz bezpieczny namespace dla wykonania
            flow_namespace = {
                '__builtins__': __builtins__,
                'engine': self.engine,
                'config': flow_config,
                'datetime': datetime,
                'asyncio': asyncio,
                'threading': threading,
                'Dict': Dict,
                'Any': Any,
                'Optional': Optional
            }
            
            # Wykonaj kod flow
            exec(flow_code, flow_namespace)
            
            # Znajdź klasę flow (powinna być nazwana jak flow_name + 'Flow')
            expected_class_name = f"{flow_name.title()}Flow"
            
            if expected_class_name in flow_namespace:
                flow_class = flow_namespace[expected_class_name]
                return {'success': True, 'flow_class': flow_class}
            else:
                # Spróbuj znaleźć pierwszą klasę kończącą się na 'Flow'
                for name, obj in flow_namespace.items():
                    if isinstance(obj, type) and name.endswith('Flow') and name != 'Flow':
                        return {'success': True, 'flow_class': obj}
                
                return {'success': False, 'error': f'Nie znaleziono klasy flow w kodzie'}

        except Exception as e:
            return {'success': False, 'error': f'Błąd kompilacji flow: {str(e)}'}

    def execute_cloud_flow(self, flow_name: str, action: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Wykonuje akcję na flow z chmury
        """
        params = params or {}
        
        try:
            # Sprawdź czy flow jest załadowany
            if flow_name not in self.cloud_flows:
                load_result = self.load_flow_from_cloud(flow_name)
                if not load_result['success']:
                    return load_result

            flow_data = self.cloud_flows[flow_name]
            
            # Utwórz instancję flow jeśli nie istnieje
            if flow_data['instance'] is None:
                flow_class = flow_data['compiled']
                flow_data['instance'] = flow_class(self.engine, flow_data['config'])
                
                # Zainicjalizuj flow
                if hasattr(flow_data['instance'], 'initialize'):
                    flow_data['instance'].initialize()

            # Wykonaj akcję
            flow_instance = flow_data['instance']
            
            if hasattr(flow_instance, action):
                method = getattr(flow_instance, action)
                result = method(**params)
                
                self.execution_statistics['flows_executed'] += 1
                
                return {
                    'success': True,
                    'result': result,
                    'flow_name': flow_name,
                    'action': action,
                    'execution_time': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': f'Flow {flow_name} nie ma akcji {action}'
                }

        except Exception as e:
            self.execution_statistics['execution_errors'] += 1
            
            # Zgłoś błąd do naprawy
            error_data = {
                'flow_id': flow_name,
                'action': action,
                'params': params,
                'error_message': str(e),
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.callback_namespace:
                self.callback_namespace.emit('flow_execution_error', error_data)
            
            self.engine.logger.error(f"❌ Błąd wykonania flow {flow_name}.{action}: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'flow_name': flow_name,
                'action': action,
                'repair_requested': True
            }

    def _execution_worker_loop(self):
        """Pętla workera wykonywania zadań"""
        while self._running:
            try:
                # Pobierz zadanie z kolejki (timeout 1s)
                priority, queued_time, task = self.execution_queue.get(timeout=1.0)
                
                # Wykonaj zadanie
                result = self.execute_cloud_flow(
                    task['flow_name'],
                    task['action'],
                    task.get('params', {})
                )
                
                # Powiadom o wyniku jeśli potrzeba
                if task.get('callback'):
                    task['callback'](result)
                
                self.execution_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"☁️ Błąd w execution worker: {e}")

    def queue_flow_execution(self, flow_name: str, action: str, params: Dict[str, Any] = None, 
                           priority: int = 2, callback: Optional[Callable] = None):
        """
        Dodaje wykonanie flow do kolejki
        """
        task = {
            'flow_name': flow_name,
            'action': action,
            'params': params or {},
            'callback': callback,
            'queued_at': datetime.now()
        }
        
        self.execution_queue.put((priority, datetime.now(), task))
        self.engine.logger.info(f"☁️ Zadanie {flow_name}.{action} dodane do kolejki")

    def _reload_cloud_flow(self, flow_name: str):
        """
        Przeładowuje naprawiony flow z chmury
        """
        try:
            # Usuń starą instancję
            if flow_name in self.cloud_flows:
                old_instance = self.cloud_flows[flow_name].get('instance')
                if old_instance and hasattr(old_instance, 'stop'):
                    old_instance.stop()
                del self.cloud_flows[flow_name]
            
            # Załaduj ponownie
            load_result = self.load_flow_from_cloud(flow_name, force_reload=True)
            
            if load_result['success']:
                self.engine.logger.info(f"☁️ Flow '{flow_name}' przeładowany po naprawie")
            else:
                self.engine.logger.error(f"❌ Błąd przeładowania flow '{flow_name}': {load_result.get('error')}")

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd przeładowania flow: {e}")

    def list_cloud_flows(self) -> Dict[str, Any]:
        """
        Zwraca listę dostępnych flow w chmurze
        """
        try:
            flow_realm = self.engine.realms.get('astral_prime')
            if not flow_realm:
                return {'success': False, 'error': 'Brak dostępu do bazy flow'}

            # Pobierz wszystkie flow z bazy
            all_flows = flow_realm.contemplate('list_cloud_flows')
            
            available_flows = []
            for flow_being in all_flows:
                flow_info = {
                    'name': flow_being.essence.name,
                    'description': flow_being.duchowa.opis_intencji,
                    'version': flow_being.materialna.version,
                    'loaded': flow_being.essence.name in self.cloud_flows,
                    'last_modified': flow_being.materialna.last_modified
                }
                available_flows.append(flow_info)
            
            return {
                'success': True,
                'flows': available_flows,
                'loaded_count': len(self.cloud_flows),
                'available_count': len(available_flows)
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status wykonawcy flow z chmury"""
        return {
            'type': 'cloud_flow_executor',
            'running': self._running,
            'loaded_flows': list(self.cloud_flows.keys()),
            'execution_queue_size': self.execution_queue.qsize(),
            'statistics': self.execution_statistics,
            'uptime': str(datetime.now() - self.start_time)
        }

    def stop(self):
        """Zatrzymuje wykonawcę flow z chmury"""
        self._running = False
        
        # Zatrzymaj wszystkie załadowane flow
        for flow_name, flow_data in self.cloud_flows.items():
            instance = flow_data.get('instance')
            if instance and hasattr(instance, 'stop'):
                try:
                    instance.stop()
                except Exception as e:
                    self.engine.logger.error(f"❌ Błąd zatrzymywania flow {flow_name}: {e}")
        
        # Poczekaj na zakończenie kolejki
        if not self.execution_queue.empty():
            self.execution_queue.join()
        
        self.engine.logger.info("☁️ CloudFlowExecutor zatrzymany")
