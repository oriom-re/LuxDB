
"""
🔧 RepairFlow - Flow Naprawy

Automatycznie naprawia błędy w innych flow.
Jeden z 5 podstawowych flow fizycznych systemu.
"""

import threading
import queue
import ast
import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class RepairFlow:
    """
    Flow naprawy - automatycznie naprawia błędy w kodzie flow
    """

    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Kolejka napraw
        self.repair_queue = queue.PriorityQueue()
        
        # Worker
        self._repair_worker: Optional[threading.Thread] = None
        self._running = False
        
        # Callback namespace
        self.callback_namespace: Optional[CallbackNamespace] = None
        
        # Wzorce napraw
        self.repair_patterns = self._initialize_repair_patterns()
        
        # Statystyki
        self.repair_statistics = {
            'repair_attempts': 0,
            'successful_repairs': 0,
            'failed_repairs': 0,
            'patterns_applied': 0
        }
        
        self.start_time = datetime.now()

    def initialize(self):
        """Inicjalizuje flow naprawy"""
        
        # Utwórz namespace callbacków
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('repair_flow')
            self._setup_repair_callbacks()
        
        # Uruchom worker
        self._running = True
        self._repair_worker = threading.Thread(target=self._repair_worker_loop, daemon=True)
        self._repair_worker.start()
        
        self.engine.logger.info("🔧 RepairFlow zainicjalizowany")

    def start(self) -> bool:
        """Uruchamia flow naprawy"""
        if self._running:
            self.engine.logger.warning("RepairFlow już działa")
            return True

        self.initialize()
        return True

    def _setup_repair_callbacks(self):
        """Konfiguruje callbacki dla flow naprawy"""
        if not self.callback_namespace:
            return

        def on_repair_completed(event):
            """Callback po zakończeniu naprawy"""
            repair_data = event.data
            flow_id = repair_data.get('flow_id')
            
            # Powiadom CloudFlowExecutor o naprawie
            if hasattr(self.engine, 'cloud_flow_executor'):
                cloud_namespace = self.engine.callback_flow.get_namespace('cloud_executor')
                if cloud_namespace:
                    cloud_namespace.emit('flow_repaired', repair_data)

        # Rejestruj callback
        self.callback_namespace.on('repair_completed', on_repair_completed, CallbackPriority.NORMAL)

    def _initialize_repair_patterns(self) -> Dict[str, Dict[str, Any]]:
        """
        Inicjalizuje wzorce napraw dla typowych błędów
        """
        return {
            'syntax_error': {
                'patterns': [
                    {
                        'regex': r'invalid syntax.*line (\d+)',
                        'fix_function': self._fix_syntax_error
                    }
                ]
            },
            'name_error': {
                'patterns': [
                    {
                        'regex': r"name '(\w+)' is not defined",
                        'fix_function': self._fix_name_error
                    }
                ]
            },
            'import_error': {
                'patterns': [
                    {
                        'regex': r"No module named '(\w+)'",
                        'fix_function': self._fix_import_error
                    }
                ]
            },
            'attribute_error': {
                'patterns': [
                    {
                        'regex': r"'(\w+)' object has no attribute '(\w+)'",
                        'fix_function': self._fix_attribute_error
                    }
                ]
            },
            'await_error': {
                'patterns': [
                    {
                        'regex': r"object (\w+) can't be used in 'await' expression",
                        'fix_function': self._fix_await_error
                    }
                ]
            },
            'type_error': {
                'patterns': [
                    {
                        'regex': r"'<' not supported between instances of '(\w+)' and '(\w+)'",
                        'fix_function': self._fix_comparison_error
                    }
                ]
            }
        }

    def request_flow_repair(self, flow_id: str, error_data: Dict[str, Any], priority: int = 2):
        """
        Zgłasza flow do naprawy
        """
        repair_task = {
            'flow_id': flow_id,
            'error_data': error_data,
            'priority': priority,
            'requested_at': datetime.now(),
            'attempts': 0
        }
        
        self.repair_queue.put((priority, datetime.now(), repair_task))
        self.engine.logger.info(f"🔧 Flow '{flow_id}' zgłoszony do naprawy")

    def _repair_worker_loop(self):
        """Pętla workera naprawy"""
        while self._running:
            try:
                # Pobierz zadanie naprawy (timeout 1s)
                priority, queued_time, task = self.repair_queue.get(timeout=1.0)
                
                # Przetworz naprawę
                success = self._process_repair_task(task)
                
                # Aktualizuj statystyki
                self.repair_statistics['repair_attempts'] += 1
                if success:
                    self.repair_statistics['successful_repairs'] += 1
                else:
                    self.repair_statistics['failed_repairs'] += 1
                
                self.repair_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🔧 Błąd w repair worker: {e}")

    def _process_repair_task(self, task: Dict[str, Any]) -> bool:
        """
        Przetwarza zadanie naprawy
        """
        try:
            flow_id = task['flow_id']
            error_data = task['error_data']
            
            # Pobierz aktualny kod flow z bazy
            flow_code = self._get_flow_code_from_database(flow_id)
            if not flow_code:
                self.engine.logger.error(f"❌ Nie można pobrać kodu flow '{flow_id}'")
                return False
            
            # Analizuj błąd i zastosuj naprawę
            repaired_code = self._analyze_and_repair(flow_code, error_data)
            
            if repaired_code and repaired_code != flow_code:
                # Zapisz naprawiony kod
                save_success = self._save_repaired_flow(flow_id, repaired_code, error_data)
                
                if save_success:
                    # Powiadom o udanej naprawie
                    if self.callback_namespace:
                        self.callback_namespace.emit('repair_completed', {
                            'flow_id': flow_id,
                            'repair_successful': True,
                            'error_data': error_data,
                            'timestamp': datetime.now().isoformat()
                        })
                    
                    self.engine.logger.info(f"🔧 Flow '{flow_id}' naprawiony pomyślnie")
                    return True
                else:
                    self.engine.logger.error(f"❌ Nie udało się zapisać naprawionego flow '{flow_id}'")
                    return False
            else:
                self.engine.logger.warning(f"⚠️ Nie znaleziono naprawy dla flow '{flow_id}'")
                return False

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd podczas naprawy flow: {e}")
            return False

    def _get_flow_code_from_database(self, flow_id: str) -> Optional[str]:
        """
        Pobiera kod flow z bazy danych
        """
        try:
            flow_realm = self.engine.realms.get('astral_prime')
            if not flow_realm:
                return None

            flow_results = flow_realm.contemplate('find_cloud_flow', flow_name=flow_id)
            
            if flow_results:
                return flow_results[0].materialna.flow_code
            
            return None

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd pobierania kodu flow: {e}")
            return None

    def _analyze_and_repair(self, flow_code: str, error_data: Dict[str, Any]) -> Optional[str]:
        """
        Analizuje błąd i próbuje naprawić kod
        """
        error_message = error_data.get('error_message', '')
        error_type = error_data.get('error_type', 'Unknown')
        
        # Znajdź odpowiedni wzorzec naprawy
        for category, category_data in self.repair_patterns.items():
            for pattern_data in category_data['patterns']:
                regex_pattern = pattern_data['regex']
                fix_function = pattern_data['fix_function']
                
                match = re.search(regex_pattern, error_message, re.IGNORECASE)
                if match:
                    self.engine.logger.info(f"🔧 Znaleziono wzorzec naprawy: {category}")
                    
                    try:
                        repaired_code = fix_function(flow_code, error_data, match)
                        if repaired_code:
                            self.repair_statistics['patterns_applied'] += 1
                            return repaired_code
                    except Exception as e:
                        self.engine.logger.error(f"❌ Błąd stosowania naprawy: {e}")
        
        # Jeśli nie znaleziono wzorca, spróbuj ogólnej naprawy
        return self._general_repair(flow_code, error_data)

    def _fix_syntax_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy składni"""
        # Podstawowa naprawa - usuwa problematyczne linie lub dodaje brakujące znaki
        lines = code.split('\n')
        
        # Sprawdź czy brakuje dwukropków
        for i, line in enumerate(lines):
            if line.strip().endswith(('if', 'def', 'class', 'for', 'while', 'try', 'except', 'with')):
                if not line.strip().endswith(':'):
                    lines[i] = line + ':'
        
        return '\n'.join(lines)

    def _fix_name_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy niezdefiniowanych nazw"""
        undefined_name = match.group(1)
        
        # Dodaj import jeśli to znana biblioteka
        common_imports = {
            'datetime': 'from datetime import datetime',
            'asyncio': 'import asyncio',
            'threading': 'import threading',
            'json': 'import json',
            'os': 'import os',
            'sys': 'import sys',
            'time': 'import time'
        }
        
        if undefined_name in common_imports:
            import_line = common_imports[undefined_name]
            lines = code.split('\n')
            
            # Znajdź miejsce na import (po docstringu)
            insert_index = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Pomiń docstring
                    quote = '"""' if '"""' in line else "'''"
                    if line.count(quote) == 1:  # Start docstringu
                        for j in range(i + 1, len(lines)):
                            if quote in lines[j]:
                                insert_index = j + 1
                                break
                    else:
                        insert_index = i + 1
                    break
                elif line.strip() and not line.startswith('#'):
                    insert_index = i
                    break
            
            lines.insert(insert_index, import_line)
            return '\n'.join(lines)
        
        return None

    def _fix_import_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy importu"""
        missing_module = match.group(1)
        
        # Zamień na dostępny import
        replacements = {
            'requests': 'import urllib.request as requests',
            'numpy': 'import math  # numpy replacement',
            'pandas': 'import csv  # pandas replacement'
        }
        
        if missing_module in replacements:
            replacement = replacements[missing_module]
            code = re.sub(rf'import {missing_module}', replacement, code)
            code = re.sub(rf'from {missing_module}.*', replacement, code)
            return code
        
        return None

    def _fix_attribute_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy atrybutów"""
        object_name = match.group(1)
        attribute_name = match.group(2)
        
        # Dodaj sprawdzenie istnienia atrybutu
        pattern = rf'(\w+)\.{attribute_name}'
        replacement = rf'getattr(\\1, "{attribute_name}", None)'
        
        modified_code = re.sub(pattern, replacement, code)
        
        if modified_code != code:
            return modified_code
        
        return None

    def _fix_await_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy await na nieAsyncowych obiektach"""
        object_type = match.group(1)
        
        # Usuń await przed obiektami dict, list itp.
        if object_type in ['dict', 'list', 'tuple', 'str', 'int', 'float']:
            code = re.sub(r'await\s+(\{.*?\})', r'\1', code)  # dict
            code = re.sub(r'await\s+(\[.*?\])', r'\1', code)  # list
            code = re.sub(r'await\s+(\(.*?\))', r'\1', code)  # tuple
            code = re.sub(r'await\s+(["\'].*?["\'])', r'\1', code)  # string
            code = re.sub(r'await\s+(\d+)', r'\1', code)  # number
            
        return code

    def _fix_comparison_error(self, code: str, error_data: Dict[str, Any], match) -> Optional[str]:
        """Naprawia błędy porównania między różnymi typami"""
        type1 = match.group(1)
        type2 = match.group(2)
        
        # Jeśli porównujemy dict z dict, dodaj konwersję na string lub hash
        if type1 == 'dict' and type2 == 'dict':
            # Zamień bezpośrednie porównania dict na porównania ich reprezentacji
            code = re.sub(r'(\w+)\s*<\s*(\w+)', r'str(\1) < str(\2)', code)
            code = re.sub(r'(\w+)\s*>\s*(\w+)', r'str(\1) > str(\2)', code)
            
        return code

    def _general_repair(self, code: str, error_data: Dict[str, Any]) -> Optional[str]:
        """
        Ogólna naprawa - dodaje try-catch wrappers
        """
        try:
            # Parse kod jako AST
            tree = ast.parse(code)
            
            # Dodaj try-catch wrapper do głównych funkcji
            modified_code = self._add_error_handling(code)
            
            return modified_code
            
        except Exception as e:
            self.engine.logger.error(f"❌ Błąd ogólnej naprawy: {e}")
            return None

    def _add_error_handling(self, code: str) -> str:
        """
        Dodaje obsługę błędów do kodu
        """
        lines = code.split('\n')
        modified_lines = []
        
        for line in lines:
            modified_lines.append(line)
            
            # Dodaj try-catch do metod
            if re.match(r'\s*def \w+\(.*\):', line):
                indent = len(line) - len(line.lstrip())
                spaces = ' ' * (indent + 4)
                
                # Znajdź koniec funkcji i owin w try-catch
                try_line = f"{spaces}try:"
                modified_lines.append(try_line)
        
        return '\n'.join(modified_lines)

    def _save_repaired_flow(self, flow_id: str, repaired_code: str, error_data: Dict[str, Any]) -> bool:
        """
        Zapisuje naprawiony kod flow do bazy
        """
        try:
            flow_realm = self.engine.realms.get('astral_prime')
            if not flow_realm:
                return False

            # Znajdź flow w bazie
            flow_results = flow_realm.contemplate('find_cloud_flow', flow_name=flow_id)
            
            if flow_results:
                flow_being = flow_results[0]
                
                # Aktualizuj kod i metadane
                update_data = {
                    'flow_code': repaired_code,
                    'last_repaired': datetime.now().isoformat(),
                    'repair_reason': error_data.get('error_message', 'Unknown error'),
                    'version': f"repaired_{hashlib.sha256(repaired_code.encode()).hexdigest()[:8]}"
                }
                
                flow_realm.evolve(flow_being.soul_id, {'materialna': update_data})
                
                self.engine.logger.info(f"🔧 Naprawiony kod flow '{flow_id}' zapisany")
                return True
            
            return False

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd zapisu naprawionego flow: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status flow naprawy"""
        return {
            'type': 'repair_flow',
            'running': self._running,
            'repair_queue_size': self.repair_queue.qsize(),
            'repair_statistics': self.repair_statistics,
            'available_patterns': list(self.repair_patterns.keys()),
            'uptime': str(datetime.now() - self.start_time)
        }

    def stop(self):
        """Zatrzymuje flow naprawy"""
        self._running = False
        
        # Poczekaj na zakończenie kolejki
        if not self.repair_queue.empty():
            self.repair_queue.join()
        
        self.engine.logger.info("🔧 RepairFlow zatrzymany")
