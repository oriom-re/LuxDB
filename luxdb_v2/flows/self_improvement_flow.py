
"""
🧬 SelfImprovementFlow - Główny coordinator systemu samodoskonalenia

Zarządza procesem kopiowania, analizy i przebudowy plików do wersji bytów.
Minimalizuje zależności od struktury podatnej na błędy.
"""

import asyncio
import os
import shutil
import hashlib
import threading
import queue
import ast
import inspect
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path

from ..beings.logical_being import LogicalBeing
from ..beings.error_handler_being import ErrorHandlerBeing
from .secure_code_flow import SecureCodeFlow
from .self_healing_flow import SelfHealingFlow
from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class CodeStabilityAnalyzer:
    """Analizuje stabilność kodu i identyfikuje bezpieczne funkcje"""
    
    def __init__(self):
        self.stability_metrics = {}
        self.error_patterns = {}
        self.function_reliability = {}
        
    def analyze_file_stability(self, file_path: str) -> Dict[str, Any]:
        """Analizuje stabilność pliku kodu"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
                
            # Parsuj AST
            tree = ast.parse(source_code)
            
            stability_report = {
                'file_path': file_path,
                'total_functions': 0,
                'stable_functions': [],
                'unstable_functions': [],
                'complexity_score': 0,
                'error_prone_patterns': [],
                'safety_score': 0.0
            }
            
            # Analizuj funkcje
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    stability_report['total_functions'] += 1
                    func_analysis = self._analyze_function_stability(node, source_code)
                    
                    if func_analysis['stability_score'] > 0.7:
                        stability_report['stable_functions'].append(func_analysis)
                    else:
                        stability_report['unstable_functions'].append(func_analysis)
                        
                    stability_report['complexity_score'] += func_analysis['complexity']
            
            # Oblicz ogólny wynik bezpieczeństwa
            total_funcs = max(1, stability_report['total_functions'])
            stable_count = len(stability_report['stable_functions'])
            stability_report['safety_score'] = stable_count / total_funcs
            
            return stability_report
            
        except Exception as e:
            return {
                'file_path': file_path,
                'error': str(e),
                'safety_score': 0.0
            }
    
    def _analyze_function_stability(self, func_node: ast.FunctionDef, source_code: str) -> Dict[str, Any]:
        """Analizuje stabilność pojedynczej funkcji"""
        
        # Metryki stabilności
        stability_factors = {
            'has_error_handling': 0,
            'complexity_low': 0,
            'uses_typing': 0,
            'has_docstring': 0,
            'avoids_global_state': 0,
            'predictable_returns': 0
        }
        
        # Sprawdź obsługę błędów
        for node in ast.walk(func_node):
            if isinstance(node, ast.Try):
                stability_factors['has_error_handling'] = 1
                break
        
        # Sprawdź złożoność
        complexity = self._calculate_cyclomatic_complexity(func_node)
        if complexity <= 5:
            stability_factors['complexity_low'] = 1
            
        # Sprawdź typing hints
        if func_node.returns or any(arg.annotation for arg in func_node.args.args):
            stability_factors['uses_typing'] = 1
            
        # Sprawdź docstring
        if (func_node.body and isinstance(func_node.body[0], ast.Expr) 
            and isinstance(func_node.body[0].value, ast.Constant)
            and isinstance(func_node.body[0].value.value, str)):
            stability_factors['has_docstring'] = 1
            
        # Sprawdź unikanie globalnego stanu
        has_global_access = False
        for node in ast.walk(func_node):
            if isinstance(node, ast.Global) or isinstance(node, ast.Nonlocal):
                has_global_access = True
                break
        if not has_global_access:
            stability_factors['avoids_global_state'] = 1
            
        # Sprawdź przewidywalność zwrotów
        return_count = sum(1 for node in ast.walk(func_node) if isinstance(node, ast.Return))
        if return_count <= 3:  # Maksymalnie 3 punkty wyjścia
            stability_factors['predictable_returns'] = 1
        
        stability_score = sum(stability_factors.values()) / len(stability_factors)
        
        return {
            'name': func_node.name,
            'line_start': func_node.lineno,
            'stability_score': stability_score,
            'complexity': complexity,
            'stability_factors': stability_factors,
            'safe_for_beings': stability_score > 0.6
        }
    
    def _calculate_cyclomatic_complexity(self, func_node: ast.FunctionDef) -> int:
        """Oblicza złożoność cyklomatyczną funkcji"""
        complexity = 1  # Bazowa złożoność
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
                
        return complexity


class FileToBeingConverter:
    """Konwertuje stabilne funkcje z plików do bytów logicznych"""
    
    def __init__(self, engine):
        self.engine = engine
        self.conversion_cache = {}
        self.being_templates = {}
        
    def convert_stable_functions_to_being(self, stability_report: Dict[str, Any]) -> Optional[LogicalBeing]:
        """Konwertuje stabilne funkcje do LogicalBeing"""
        
        stable_functions = stability_report.get('stable_functions', [])
        if not stable_functions:
            return None
            
        file_path = stability_report['file_path']
        being_name = f"StableBeing_{Path(file_path).stem}"
        
        # Utwórz kontekst bytu
        being_context = {
            'domain': self._extract_domain_from_path(file_path),
            'specialization': self._extract_specialization(stable_functions),
            'origin_file': file_path,
            'stability_score': stability_report['safety_score']
        }
        
        # Utwórz LogicalBeing
        logical_being = LogicalBeing(being_context, realm=self._get_beings_realm())
        
        # Dodaj stabilne funkcje jako mikro-funkcje
        for func_data in stable_functions:
            if func_data['safe_for_beings']:
                micro_function = self._create_micro_function_from_ast(func_data, file_path)
                if micro_function:
                    logical_being.micro_functions[func_data['name']] = micro_function
                    
        # Zapisz szablon bytu
        self.being_templates[being_name] = {
            'context': being_context,
            'functions': [f['name'] for f in stable_functions if f['safe_for_beings']],
            'created_at': datetime.now().isoformat(),
            'source_file': file_path
        }
        
        return logical_being
    
    def _extract_domain_from_path(self, file_path: str) -> str:
        """Wydobywa domenę z ścieżki pliku"""
        path_parts = Path(file_path).parts
        
        if 'flows' in path_parts:
            return 'flow_management'
        elif 'beings' in path_parts:
            return 'being_logic'
        elif 'realms' in path_parts:
            return 'data_management'
        elif 'wisdom' in path_parts:
            return 'system_intelligence'
        elif 'core' in path_parts:
            return 'core_functionality'
        else:
            return 'general_purpose'
    
    def _extract_specialization(self, stable_functions: List[Dict[str, Any]]) -> str:
        """Wydobywa specjalizację na podstawie nazw funkcji"""
        function_names = [f['name'] for f in stable_functions]
        
        # Analiza wzorców nazw
        if any('error' in name.lower() for name in function_names):
            return 'error_handling'
        elif any('process' in name.lower() for name in function_names):
            return 'data_processing'
        elif any('analyze' in name.lower() for name in function_names):
            return 'analysis'
        elif any('generate' in name.lower() for name in function_names):
            return 'generation'
        elif any('heal' in name.lower() or 'repair' in name.lower() for name in function_names):
            return 'system_healing'
        else:
            return 'general_operations'
    
    def _create_micro_function_from_ast(self, func_data: Dict[str, Any], file_path: str) -> Optional[Dict[str, Any]]:
        """Tworzy mikro-funkcję z danych AST"""
        try:
            # Wczytaj kod źródłowy
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Wydobądź kod funkcji (uproszczenie - potrzeba bardziej zaawansowanej analizy)
            func_name = func_data['name']
            start_line = func_data['line_start'] - 1
            
            # Znajdź koniec funkcji (bardzo podstawowa implementacja)
            func_lines = []
            indent_level = None
            
            for i, line in enumerate(lines[start_line:], start_line):
                if indent_level is None and line.strip().startswith('def '):
                    indent_level = len(line) - len(line.lstrip())
                    func_lines.append(line)
                elif indent_level is not None:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= indent_level and not line.strip().startswith('def '):
                        break
                    func_lines.append(line)
            
            func_code = ''.join(func_lines)
            
            return {
                'name': func_name,
                'code': func_code,
                'stability_score': func_data['stability_score'],
                'complexity': func_data['complexity'],
                'safe_execution': True,
                'origin_file': file_path,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd tworzenia mikro-funkcji {func_data['name']}: {e}")
            return None
    
    def _get_beings_realm(self):
        """Pobiera realm dla bytów"""
        if hasattr(self.engine, 'realms'):
            return self.engine.realms.get('astral_prime', None)
        return None


class SelfImprovementFlow:
    """
    Główny coordinator systemu samodoskonalenia
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Komponenty systemu
        self.stability_analyzer = CodeStabilityAnalyzer()
        self.file_converter = FileToBeingConverter(astral_engine)
        self.self_healing_flow: Optional[SelfHealingFlow] = None
        self.secure_code_flow: Optional[SecureCodeFlow] = None
        
        # System monitorowania
        self.monitored_files: Set[str] = set()
        self.file_checksums: Dict[str, str] = {}
        self.improvement_queue = queue.PriorityQueue()
        
        # Workery
        self._monitor_worker: Optional[threading.Thread] = None
        self._improvement_worker: Optional[threading.Thread] = None
        self._running = False
        
        # Callback namespace
        self.callback_namespace: Optional[CallbackNamespace] = None
        
        # Statystyki
        self.improvement_statistics = {
            'files_analyzed': 0,
            'stable_functions_found': 0,
            'beings_created': 0,
            'errors_prevented': 0,
            'system_improvements': 0
        }
        
        # Utworzone byty
        self.created_beings: Dict[str, LogicalBeing] = {}
        
        self.start_time = datetime.now()
    
    def initialize(self):
        """Inicjalizuje system samodoskonalenia"""
        
        # Połącz z innymi systemami
        self._connect_to_healing_systems()
        
        # Skonfiguruj monitorowanie plików
        self._setup_file_monitoring()
        
        # Utwórz namespace callbacków
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('self_improvement')
            self._setup_improvement_callbacks()
        
        # Uruchom workery
        self._running = True
        self._monitor_worker = threading.Thread(target=self._file_monitor_loop, daemon=True)
        self._improvement_worker = threading.Thread(target=self._improvement_worker_loop, daemon=True)
        
        self._monitor_worker.start()
        self._improvement_worker.start()
        
        self.engine.logger.info("🧬 SelfImprovementFlow zainicjalizowany")
    
    def start(self) -> bool:
        """Uruchamia system samodoskonalenia"""
        if self._running:
            self.engine.logger.warning("SelfImprovementFlow już działa")
            return True
        
        self.initialize()
        return True
    
    def _connect_to_healing_systems(self):
        """Łączy się z systemami healing"""
        # Znajdź SelfHealingFlow
        if hasattr(self.engine, 'flows'):
            for flow_name, flow in self.engine.flows.items():
                if isinstance(flow, SelfHealingFlow):
                    self.self_healing_flow = flow
                    break
        
        # Utwórz SecureCodeFlow jeśli nie istnieje
        if not self.secure_code_flow:
            self.secure_code_flow = SecureCodeFlow(self.engine)
    
    def _setup_file_monitoring(self):
        """Konfiguruje monitorowanie plików"""
        
        # Dodaj kluczowe pliki do monitorowania
        project_root = Path.cwd()
        
        patterns_to_monitor = [
            'luxdb_v2/**/*.py',
            '*.py'
        ]
        
        for pattern in patterns_to_monitor:
            for file_path in project_root.glob(pattern):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    self.add_file_to_monitoring(str(file_path))
    
    def add_file_to_monitoring(self, file_path: str):
        """Dodaje plik do monitorowania"""
        self.monitored_files.add(file_path)
        self.file_checksums[file_path] = self._calculate_file_checksum(file_path)
        
        self.engine.logger.debug(f"📁 Dodano do monitorowania: {file_path}")
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Oblicza checksum pliku"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _file_monitor_loop(self):
        """Pętla monitorowania zmian w plikach"""
        while self._running:
            try:
                # Sprawdź zmiany w monitorowanych plikach
                for file_path in list(self.monitored_files):
                    if os.path.exists(file_path):
                        current_checksum = self._calculate_file_checksum(file_path)
                        old_checksum = self.file_checksums.get(file_path, "")
                        
                        if current_checksum != old_checksum:
                            self.engine.logger.info(f"📝 Wykryto zmianę w pliku: {file_path}")
                            self._queue_file_analysis(file_path, 'file_changed')
                            self.file_checksums[file_path] = current_checksum
                
                # Sprawdź co 30 sekund
                for _ in range(30):
                    if not self._running:
                        break
                    threading.Event().wait(1)
                    
            except Exception as e:
                self.engine.logger.error(f"📁 Błąd w monitorowaniu plików: {e}")
                threading.Event().wait(5)
    
    def _queue_file_analysis(self, file_path: str, reason: str):
        """Dodaje plik do kolejki analizy"""
        analysis_task = {
            'type': 'analyze_file',
            'file_path': file_path,
            'reason': reason,
            'priority': 3,  # Średni priorytet
            'queued_at': datetime.now()
        }
        
        self.improvement_queue.put((3, datetime.now().timestamp(), analysis_task))
    
    def _improvement_worker_loop(self):
        """Pętla workera samodoskonalenia"""
        while self._running:
            try:
                # Pobierz zadanie z kolejki
                priority, queued_time, task = self.improvement_queue.get(timeout=1.0)
                
                # Przetwórz zadanie
                success = self._process_improvement_task(task)
                
                # Aktualizuj statystyki
                if success:
                    self.improvement_statistics['system_improvements'] += 1
                
                self.improvement_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🧬 Błąd w improvement worker: {e}")
    
    def _process_improvement_task(self, task: Dict[str, Any]) -> bool:
        """Przetwarza zadanie samodoskonalenia"""
        try:
            task_type = task['type']
            
            if task_type == 'analyze_file':
                return self._analyze_and_improve_file(task['file_path'])
            elif task_type == 'create_being':
                return self._create_being_from_analysis(task['analysis_data'])
            elif task_type == 'test_system_weakness':
                return self._test_system_for_weaknesses(task['test_data'])
            
            return False
            
        except Exception as e:
            self.engine.logger.error(f"🧬 Błąd przetwarzania zadania: {e}")
            return False
    
    def _analyze_and_improve_file(self, file_path: str) -> bool:
        """Analizuje plik i tworzy ulepszenia"""
        try:
            # Analizuj stabilność
            stability_report = self.stability_analyzer.analyze_file_stability(file_path)
            self.improvement_statistics['files_analyzed'] += 1
            
            if stability_report.get('error'):
                self.engine.logger.warning(f"⚠️ Błąd analizy pliku {file_path}: {stability_report['error']}")
                return False
            
            # Jeśli znaleziono stabilne funkcje, utwórz byt
            stable_count = len(stability_report.get('stable_functions', []))
            if stable_count > 0:
                self.improvement_statistics['stable_functions_found'] += stable_count
                
                # Utwórz LogicalBeing
                logical_being = self.file_converter.convert_stable_functions_to_being(stability_report)
                if logical_being:
                    being_name = f"StableBeing_{Path(file_path).stem}_{datetime.now().strftime('%H%M%S')}"
                    self.created_beings[being_name] = logical_being
                    self.improvement_statistics['beings_created'] += 1
                    
                    self.engine.logger.info(f"🤖 Utworzono byt: {being_name} z {stable_count} stabilnych funkcji")
                    
                    # Powiadom system o nowym bycie
                    if self.callback_namespace:
                        self.callback_namespace.emit('being_created', {
                            'being_name': being_name,
                            'source_file': file_path,
                            'stable_functions_count': stable_count,
                            'stability_score': stability_report['safety_score']
                        })
                    
                    return True
            
            return False
            
        except Exception as e:
            self.engine.logger.error(f"🧬 Błąd analizy pliku {file_path}: {e}")
            return False
    
    def _setup_improvement_callbacks(self):
        """Konfiguruje callbacki systemu samodoskonalenia"""
        if not self.callback_namespace:
            return
        
        def on_error_detected(event):
            """Callback gdy wykryto błąd"""
            error_data = event.data
            self._queue_error_analysis(error_data)
        
        def on_weakness_found(event):
            """Callback gdy znaleziono słabość"""
            weakness_data = event.data
            self._queue_weakness_mitigation(weakness_data)
        
        def on_improvement_request(event):
            """Callback na żądanie ulepszenia"""
            request_data = event.data
            self._handle_improvement_request(request_data)
        
        # Rejestruj callbacki
        self.callback_namespace.on('error_detected', on_error_detected, CallbackPriority.HIGH)
        self.callback_namespace.on('weakness_found', on_weakness_found, CallbackPriority.HIGH)
        self.callback_namespace.on('improvement_request', on_improvement_request, CallbackPriority.NORMAL)
    
    def _queue_error_analysis(self, error_data: Dict[str, Any]):
        """Dodaje błąd do analizy samodoskonalenia"""
        analysis_task = {
            'type': 'analyze_error',
            'error_data': error_data,
            'priority': 1,  # Wysoki priorytet
            'queued_at': datetime.now()
        }
        
        self.improvement_queue.put((1, datetime.now().timestamp(), analysis_task))
        self.improvement_statistics['errors_prevented'] += 1
    
    def trigger_comprehensive_analysis(self):
        """Uruchamia kompleksową analizę całego systemu"""
        self.engine.logger.info("🔍 Rozpoczynam kompleksową analizę systemu...")
        
        # Analizuj wszystkie monitorowane pliki
        for file_path in self.monitored_files:
            self._queue_file_analysis(file_path, 'comprehensive_analysis')
        
        # Dodaj zadanie testowania słabości
        weakness_test_task = {
            'type': 'test_system_weakness',
            'test_data': {'comprehensive': True},
            'priority': 2,
            'queued_at': datetime.now()
        }
        
        self.improvement_queue.put((2, datetime.now().timestamp(), weakness_test_task))
    
    def get_improvement_dashboard_data(self) -> Dict[str, Any]:
        """Zwraca dane dla dashboard samodoskonalenia"""
        return {
            'statistics': self.improvement_statistics,
            'created_beings': {
                name: {
                    'context': being.context,
                    'micro_functions_count': len(being.micro_functions),
                    'status': being.get_status() if hasattr(being, 'get_status') else {'active': True}
                }
                for name, being in self.created_beings.items()
            },
            'monitoring': {
                'monitored_files_count': len(self.monitored_files),
                'queue_size': self.improvement_queue.qsize(),
                'recent_files': list(self.monitored_files)[-10:]  # Ostatnie 10
            },
            'stability_analysis': {
                'analyzer_status': 'active',
                'converter_status': 'active'
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status systemu samodoskonalenia"""
        return {
            'type': 'self_improvement_flow',
            'running': self._running,
            'improvement_queue_size': self.improvement_queue.qsize(),
            'monitored_files_count': len(self.monitored_files),
            'created_beings_count': len(self.created_beings),
            'statistics': self.improvement_statistics,
            'uptime': str(datetime.now() - self.start_time),
            'components_status': {
                'stability_analyzer': 'active',
                'file_converter': 'active',
                'self_healing_connected': self.self_healing_flow is not None,
                'secure_code_connected': self.secure_code_flow is not None
            }
        }
    
    def stop(self):
        """Zatrzymuje system samodoskonalenia"""
        self._running = False
        
        # Poczekaj na zakończenie kolejki
        if not self.improvement_queue.empty():
            self.improvement_queue.join()
        
        self.engine.logger.info("🧬 SelfImprovementFlow zatrzymany")
