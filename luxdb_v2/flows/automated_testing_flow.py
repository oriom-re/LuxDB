
"""
🧪 AutomatedTestingFlow - System automatycznego testowania słabości

Automatycznie testuje system w poszukiwaniu potencjalnych słabości,
błędów i punktów awaryjnych.
"""

import asyncio
import random
import threading
import queue
import importlib
import sys
import traceback
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

from ..beings.error_handler_being import ErrorHandlerBeing
from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class WeaknessProbe:
    """Sonda do wykrywania słabości systemu"""
    
    def __init__(self, name: str, description: str, test_function: Callable):
        self.name = name
        self.description = description
        self.test_function = test_function
        self.last_run = None
        self.success_count = 0
        self.failure_count = 0
        self.weakness_found_count = 0
    
    def execute(self, target_system: Any) -> Dict[str, Any]:
        """Wykonuje sondę testową"""
        try:
            self.last_run = datetime.now()
            result = self.test_function(target_system)
            
            if result.get('success', False):
                self.success_count += 1
            else:
                self.failure_count += 1
                
            if result.get('weakness_found', False):
                self.weakness_found_count += 1
                
            return result
            
        except Exception as e:
            self.failure_count += 1
            return {
                'success': False,
                'error': str(e),
                'traceback': traceback.format_exc(),
                'weakness_found': True,
                'weakness_type': 'exception_in_probe'
            }


class AutomatedTestingFlow:
    """
    System automatycznego testowania słabości
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Sondy testowe
        self.weakness_probes: Dict[str, WeaknessProbe] = {}
        self.active_tests = set()
        
        # Kolejki testów
        self.test_queue = queue.PriorityQueue()
        self.results_queue = queue.Queue()
        
        # Workery
        self._testing_worker: Optional[threading.Thread] = None
        self._results_worker: Optional[threading.Thread] = None
        self._scheduler_worker: Optional[threading.Thread] = None
        self._running = False
        
        # Callback namespace
        self.callback_namespace: Optional[CallbackNamespace] = None
        
        # Statystyki
        self.testing_statistics = {
            'total_tests_run': 0,
            'weaknesses_found': 0,
            'false_positives': 0,
            'system_crashes_prevented': 0,
            'improvement_suggestions': 0
        }
        
        # Znalezione słabości
        self.discovered_weaknesses: List[Dict[str, Any]] = []
        
        self.start_time = datetime.now()
        
        # Inicjalizuj sondy
        self._initialize_weakness_probes()
    
    def _initialize_weakness_probes(self):
        """Inicjalizuje sondy wykrywania słabości"""
        
        # Sonda testowania błędów await
        self.weakness_probes['await_error_probe'] = WeaknessProbe(
            name="Await Error Probe",
            description="Testuje błędy await na nieprawidłowych obiektach",
            test_function=self._test_await_errors
        )
        
        # Sonda testowania przeciążenia pamięci
        self.weakness_probes['memory_stress_probe'] = WeaknessProbe(
            name="Memory Stress Probe", 
            description="Testuje reakcję systemu na wysokie zużycie pamięci",
            test_function=self._test_memory_stress
        )
        
        # Sonda testowania błędów importu
        self.weakness_probes['import_error_probe'] = WeaknessProbe(
            name="Import Error Probe",
            description="Testuje błędy importu modułów",
            test_function=self._test_import_errors
        )
        
        # Sonda testowania błędów typu
        self.weakness_probes['type_error_probe'] = WeaknessProbe(
            name="Type Error Probe",
            description="Testuje błędy typów w krytycznych funkcjach",
            test_function=self._test_type_errors
        )
        
        # Sonda testowania błędów konkurrency
        self.weakness_probes['concurrency_probe'] = WeaknessProbe(
            name="Concurrency Probe",
            description="Testuje błędy związane z wielowątkowością",
            test_function=self._test_concurrency_issues
        )
        
        # Sonda testowania błędów konfiguracji
        self.weakness_probes['config_error_probe'] = WeaknessProbe(
            name="Configuration Error Probe",
            description="Testuje błędy związane z konfiguracją",
            test_function=self._test_configuration_errors
        )
    
    def _test_await_errors(self, target_system: Any) -> Dict[str, Any]:
        """Testuje błędy await"""
        try:
            # Symuluj typowe błędy await
            test_cases = [
                # Await na dict
                "await {'key': 'value'}",
                # Await na None
                "await None",
                # Await na funkcję synchroniczną
                "await len([1,2,3])"
            ]
            
            weaknesses_found = []
            
            for test_case in test_cases:
                try:
                    # Nie wykonujemy tego kodu, tylko testujemy czy system może go wykryć
                    weakness_found = self._check_if_system_handles_await_error(test_case)
                    if not weakness_found:
                        weaknesses_found.append({
                            'type': 'await_error_not_handled',
                            'test_case': test_case,
                            'description': f"System może nie obsługiwać: {test_case}"
                        })
                except Exception as e:
                    weaknesses_found.append({
                        'type': 'await_error_exception',
                        'test_case': test_case,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'weakness_found': len(weaknesses_found) > 0,
                'weaknesses': weaknesses_found,
                'test_type': 'await_errors'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'probe_execution_error'
            }
    
    def _check_if_system_handles_await_error(self, test_case: str) -> bool:
        """Sprawdza czy system ma mechanizmy obsługi błędów await"""
        # Sprawdź czy jest SelfHealingFlow
        if hasattr(self.engine, 'flows'):
            for flow_name, flow in self.engine.flows.items():
                if hasattr(flow, 'handle_await_expression_error'):
                    return True
        
        # Sprawdź czy jest ErrorHandlerBeing
        if hasattr(self.engine, 'beings'):
            for being in self.engine.beings.values():
                if isinstance(being, ErrorHandlerBeing):
                    return True
        
        return False
    
    def _test_memory_stress(self, target_system: Any) -> Dict[str, Any]:
        """Testuje reakcję na stress pamięciowy"""
        try:
            import psutil
            initial_memory = psutil.virtual_memory().percent
            
            # Symuluj lekki stress pamięciowy
            test_data = []
            for i in range(1000):
                test_data.append([random.randint(1, 1000) for _ in range(100)])
            
            current_memory = psutil.virtual_memory().percent
            memory_increase = current_memory - initial_memory
            
            # Wyczyść test data
            del test_data
            
            weakness_found = memory_increase > 10  # Wzrost > 10% może być problemem
            
            return {
                'success': True,
                'weakness_found': weakness_found,
                'memory_increase': memory_increase,
                'test_type': 'memory_stress',
                'warning': 'High memory usage detected' if weakness_found else None
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'psutil not available',
                'weakness_found': True,
                'weakness_type': 'missing_dependency'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'memory_test_error'
            }
    
    def _test_import_errors(self, target_system: Any) -> Dict[str, Any]:
        """Testuje błędy importu"""
        try:
            problematic_imports = [
                'nonexistent_module',
                'luxdb_v2.nonexistent_submodule',
                'os.nonexistent_function'
            ]
            
            weaknesses_found = []
            
            for import_name in problematic_imports:
                try:
                    # Próbuj importu - nie powinien się powieść
                    importlib.import_module(import_name)
                    weaknesses_found.append({
                        'type': 'unexpected_import_success',
                        'import_name': import_name,
                        'description': f"Importowanie {import_name} powiodło się nieoczekiwanie"
                    })
                except ImportError:
                    # To jest oczekiwane - brak słabości
                    pass
                except Exception as e:
                    weaknesses_found.append({
                        'type': 'import_error_not_handled',
                        'import_name': import_name,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'weakness_found': len(weaknesses_found) > 0,
                'weaknesses': weaknesses_found,
                'test_type': 'import_errors'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'import_test_error'
            }
    
    def _test_type_errors(self, target_system: Any) -> Dict[str, Any]:
        """Testuje błędy typów"""
        try:
            weaknesses_found = []
            
            # Testuj kluczowe metody systemu z błędnymi typami
            test_methods = [
                ('meditate', [None, "string", 123]),
                ('get_realm', [None, 123, []]),
                ('manifest_intention', [None, "string", 123])
            ]
            
            for method_name, wrong_args in test_methods:
                if hasattr(target_system, method_name):
                    method = getattr(target_system, method_name)
                    
                    for wrong_arg in wrong_args:
                        try:
                            # Nie wywołujemy metody, tylko sprawdzamy czy jest zabezpieczona
                            if not self._has_type_checking(method):
                                weaknesses_found.append({
                                    'type': 'missing_type_validation',
                                    'method_name': method_name,
                                    'description': f"Metoda {method_name} może nie mieć walidacji typów"
                                })
                                break
                        except Exception:
                            pass
            
            return {
                'success': True,
                'weakness_found': len(weaknesses_found) > 0,
                'weaknesses': weaknesses_found,
                'test_type': 'type_errors'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'type_test_error'
            }
    
    def _has_type_checking(self, method: Callable) -> bool:
        """Sprawdza czy metoda ma type checking"""
        try:
            import inspect
            signature = inspect.signature(method)
            
            # Sprawdź czy parametry mają adnotacje typów
            for param in signature.parameters.values():
                if param.annotation != inspect.Parameter.empty:
                    return True
            
            # Sprawdź zwracany typ
            if signature.return_annotation != inspect.Signature.empty:
                return True
            
            return False
        except Exception:
            return False
    
    def _test_concurrency_issues(self, target_system: Any) -> Dict[str, Any]:
        """Testuje problemy wielowątkowości"""
        try:
            import threading
            import time
            
            weaknesses_found = []
            results = []
            
            def test_concurrent_access():
                try:
                    # Próbuj równoczesnego dostępu do medytacji
                    if hasattr(target_system, 'meditate'):
                        result = target_system.meditate()
                        results.append(result)
                except Exception as e:
                    weaknesses_found.append({
                        'type': 'concurrency_error',
                        'method': 'meditate',
                        'error': str(e)
                    })
            
            # Uruchom kilka wątków równocześnie
            threads = []
            for i in range(3):
                thread = threading.Thread(target=test_concurrent_access)
                threads.append(thread)
                thread.start()
            
            # Poczekaj na zakończenie
            for thread in threads:
                thread.join(timeout=5.0)
            
            # Sprawdź czy wszystkie wątki zakończyły się poprawnie
            active_threads = sum(1 for t in threads if t.is_alive())
            if active_threads > 0:
                weaknesses_found.append({
                    'type': 'thread_hanging',
                    'active_threads': active_threads,
                    'description': 'Niektóre wątki nie zakończyły się w czasie'
                })
            
            return {
                'success': True,
                'weakness_found': len(weaknesses_found) > 0,
                'weaknesses': weaknesses_found,
                'test_type': 'concurrency_issues',
                'results_count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'concurrency_test_error'
            }
    
    def _test_configuration_errors(self, target_system: Any) -> Dict[str, Any]:
        """Testuje błędy konfiguracji"""
        try:
            weaknesses_found = []
            
            # Sprawdź dostęp do konfiguracji
            if hasattr(target_system, 'config'):
                config = target_system.config
                
                # Sprawdź wymagane pola konfiguracji
                required_fields = ['realms', 'flows', 'consciousness_level']
                for field in required_fields:
                    if not hasattr(config, field):
                        weaknesses_found.append({
                            'type': 'missing_config_field',
                            'field': field,
                            'description': f"Brak wymaganego pola konfiguracji: {field}"
                        })
                
                # Sprawdź puste konfiguracje
                if hasattr(config, 'realms') and not config.realms:
                    weaknesses_found.append({
                        'type': 'empty_realms_config',
                        'description': 'Konfiguracja realms jest pusta'
                    })
            else:
                weaknesses_found.append({
                    'type': 'missing_config',
                    'description': 'System nie ma dostępu do konfiguracji'
                })
            
            return {
                'success': True,
                'weakness_found': len(weaknesses_found) > 0,
                'weaknesses': weaknesses_found,
                'test_type': 'configuration_errors'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'config_test_error'
            }
    
    def initialize(self):
        """Inicjalizuje system testowania"""
        
        # Utwórz namespace callbacków
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('automated_testing')
            self._setup_testing_callbacks()
        
        # Uruchom workery
        self._running = True
        self._testing_worker = threading.Thread(target=self._testing_worker_loop, daemon=True)
        self._results_worker = threading.Thread(target=self._results_worker_loop, daemon=True)
        self._scheduler_worker = threading.Thread(target=self._scheduler_worker_loop, daemon=True)
        
        self._testing_worker.start()
        self._results_worker.start()
        self._scheduler_worker.start()
        
        self.engine.logger.info("🧪 AutomatedTestingFlow zainicjalizowany")
    
    def start(self) -> bool:
        """Uruchamia system testowania"""
        if self._running:
            self.engine.logger.warning("AutomatedTestingFlow już działa")
            return True
        
        self.initialize()
        return True
    
    def _testing_worker_loop(self):
        """Pętla workera testowania"""
        while self._running:
            try:
                # Pobierz test z kolejki
                priority, queued_time, test_task = self.test_queue.get(timeout=1.0)
                
                # Wykonaj test
                result = self._execute_test(test_task)
                
                # Dodaj wynik do kolejki wyników
                self.results_queue.put({
                    'test_task': test_task,
                    'result': result,
                    'executed_at': datetime.now()
                })
                
                self.testing_statistics['total_tests_run'] += 1
                self.test_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🧪 Błąd w testing worker: {e}")
    
    def _execute_test(self, test_task: Dict[str, Any]) -> Dict[str, Any]:
        """Wykonuje test"""
        try:
            probe_name = test_task['probe_name']
            target = test_task.get('target', self.engine)
            
            if probe_name in self.weakness_probes:
                probe = self.weakness_probes[probe_name]
                return probe.execute(target)
            else:
                return {
                    'success': False,
                    'error': f'Nieznana sonda: {probe_name}',
                    'weakness_found': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'weakness_found': True,
                'weakness_type': 'test_execution_error'
            }
    
    def _results_worker_loop(self):
        """Pętla workera wyników"""
        while self._running:
            try:
                # Pobierz wynik
                result_data = self.results_queue.get(timeout=1.0)
                
                # Przetwórz wynik
                self._process_test_result(result_data)
                
                self.results_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🧪 Błąd w results worker: {e}")
    
    def _process_test_result(self, result_data: Dict[str, Any]):
        """Przetwarza wynik testu"""
        try:
            result = result_data['result']
            test_task = result_data['test_task']
            
            if result.get('weakness_found', False):
                self.testing_statistics['weaknesses_found'] += 1
                
                # Dodaj do listy znalezionych słabości
                weakness_record = {
                    'probe_name': test_task['probe_name'],
                    'weakness_data': result,
                    'discovered_at': result_data['executed_at'].isoformat(),
                    'severity': self._assess_weakness_severity(result)
                }
                
                self.discovered_weaknesses.append(weakness_record)
                
                # Powiadom system o słabości
                if self.callback_namespace:
                    self.callback_namespace.emit('weakness_discovered', weakness_record)
                
                self.engine.logger.warning(f"⚠️ Wykryto słabość przez {test_task['probe_name']}: {result.get('weakness_type', 'unknown')}")
            
        except Exception as e:
            self.engine.logger.error(f"🧪 Błąd przetwarzania wyniku: {e}")
    
    def _assess_weakness_severity(self, result: Dict[str, Any]) -> str:
        """Ocenia wagę słabości"""
        weakness_type = result.get('weakness_type', '')
        
        critical_patterns = ['crash', 'exception', 'hanging', 'memory']
        high_patterns = ['error', 'missing', 'validation']
        
        if any(pattern in weakness_type.lower() for pattern in critical_patterns):
            return 'critical'
        elif any(pattern in weakness_type.lower() for pattern in high_patterns):
            return 'high'
        else:
            return 'medium'
    
    def _scheduler_worker_loop(self):
        """Pętla schedulera testów"""
        while self._running:
            try:
                # Uruchamiaj testy okresowo
                current_time = datetime.now()
                
                for probe_name, probe in self.weakness_probes.items():
                    # Sprawdź czy czas na kolejny test (co 5 minut)
                    if (probe.last_run is None or 
                        current_time - probe.last_run > timedelta(minutes=5)):
                        
                        # Dodaj test do kolejki
                        test_task = {
                            'probe_name': probe_name,
                            'target': self.engine,
                            'scheduled': True
                        }
                        
                        # Priorytet na podstawie ważności
                        priority = 3  # Średni priorytet dla scheduled testów
                        self.test_queue.put((priority, current_time, test_task))
                
                # Sprawdzaj co minutę
                for _ in range(60):
                    if not self._running:
                        break
                    threading.Event().wait(1)
                    
            except Exception as e:
                self.engine.logger.error(f"🧪 Błąd w scheduler: {e}")
                threading.Event().wait(5)
    
    def _setup_testing_callbacks(self):
        """Konfiguruje callbacki testowania"""
        if not self.callback_namespace:
            return
        
        def on_manual_test_request(event):
            """Callback na żądanie manualnego testu"""
            test_data = event.data
            self._queue_manual_test(test_data)
        
        def on_weakness_mitigation_needed(event):
            """Callback gdy potrzebna jest mitygacja słabości"""
            weakness_data = event.data
            self._queue_mitigation_test(weakness_data)
        
        # Rejestruj callbacki
        self.callback_namespace.on('manual_test_request', on_manual_test_request, CallbackPriority.NORMAL)
        self.callback_namespace.on('mitigation_needed', on_weakness_mitigation_needed, CallbackPriority.HIGH)
    
    def run_immediate_test(self, probe_name: str) -> Dict[str, Any]:
        """Uruchamia natychmiastowy test"""
        if probe_name not in self.weakness_probes:
            return {'error': f'Nieznana sonda: {probe_name}'}
        
        probe = self.weakness_probes[probe_name]
        result = probe.execute(self.engine)
        
        self.engine.logger.info(f"🧪 Wykonano natychmiastowy test: {probe_name}")
        return result
    
    def get_testing_dashboard_data(self) -> Dict[str, Any]:
        """Zwraca dane dla dashboard testowania"""
        return {
            'statistics': self.testing_statistics,
            'weakness_probes': {
                name: {
                    'description': probe.description,
                    'last_run': probe.last_run.isoformat() if probe.last_run else None,
                    'success_count': probe.success_count,
                    'failure_count': probe.failure_count,
                    'weakness_found_count': probe.weakness_found_count
                }
                for name, probe in self.weakness_probes.items()
            },
            'discovered_weaknesses': self.discovered_weaknesses[-20:],  # Ostatnie 20
            'queue_status': {
                'test_queue_size': self.test_queue.qsize(),
                'results_queue_size': self.results_queue.qsize()
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status systemu testowania"""
        return {
            'type': 'automated_testing_flow',
            'running': self._running,
            'test_queue_size': self.test_queue.qsize(),
            'results_queue_size': self.results_queue.qsize(),
            'probes_count': len(self.weakness_probes),
            'weaknesses_discovered': len(self.discovered_weaknesses),
            'statistics': self.testing_statistics,
            'uptime': str(datetime.now() - self.start_time)
        }
    
    def stop(self):
        """Zatrzymuje system testowania"""
        self._running = False
        
        # Poczekaj na zakończenie kolejek
        if not self.test_queue.empty():
            self.test_queue.join()
        if not self.results_queue.empty():
            self.results_queue.join()
        
        self.engine.logger.info("🧪 AutomatedTestingFlow zatrzymany")
