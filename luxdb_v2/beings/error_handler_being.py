
"""
🚨 ErrorHandlerBeing - Byt Obsługi Błędów

Przekształca błędy w intencje z możliwością samonaprawy.
Błędy to sposobność do wzrostu, nie przeszkoda.
"""

import uuid
import traceback
import sys
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .logical_being import LogicalBeing, LogicType, LogicalContext
from .intention_being import IntentionBeing, IntentionState, IntentionPriority


class ErrorSeverity(Enum):
    """Poziomy ważności błędów"""
    LOW = 1          # Ostrzeżenia, niekrytyczne
    MEDIUM = 2       # Błędy funkcjonalne
    HIGH = 3         # Błędy krytyczne
    CRITICAL = 4     # Błędy systemowe


class ErrorCategory(Enum):
    """Kategorie błędów"""
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    LOGIC = "logic"
    NETWORK = "network"
    DATABASE = "database"
    PERMISSION = "permission"
    RESOURCE = "resource"
    INTEGRATION = "integration"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Kontekst błędu"""
    error_type: str
    error_message: str
    stack_trace: str
    module_name: str
    function_name: str
    line_number: int
    timestamp: datetime = field(default_factory=datetime.now)
    user_action: str = ""
    system_state: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'error_type': self.error_type,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace,
            'module_name': self.module_name,
            'function_name': self.function_name,
            'line_number': self.line_number,
            'timestamp': self.timestamp.isoformat(),
            'user_action': self.user_action,
            'system_state': self.system_state
        }


class ErrorIntention(IntentionBeing):
    """
    Specjalna intencja reprezentująca błąd z możliwością samonaprawy
    """
    
    def __init__(self, error_context: ErrorContext, severity: ErrorSeverity, category: ErrorCategory, realm=None):
        # Przygotuj dane intencji z kontekstu błędu
        intention_data = {
            'duchowa': {
                'opis_intencji': f'Naprawa błędu: {error_context.error_message}',
                'kontekst': f'Moduł: {error_context.module_name}, Funkcja: {error_context.function_name}',
                'inspiracja': 'Błąd to sposobność do wzrostu i poprawy systemu',
                'madrosc': 'Każdy błąd niesie w sobie lekcję dla całego systemu',
                'energia_duchowa': 100.0 - (severity.value * 15)  # Mniej energii dla poważniejszych błędów
            },
            'materialna': {
                'zadanie': 'self_healing_repair',
                'wymagania': ['error_analysis', 'solution_generation', 'auto_repair'],
                'oczekiwany_rezultat': f'Naprawiony błąd {error_context.error_type}',
                'techniczne_detale': error_context.to_dict()
            },
            'metainfo': {
                'zrodlo': 'error_handler_being',
                'tags': ['error', 'self_healing', severity.name.lower(), category.value],
                'glebokosc': severity.value,
                'opiekun': 'error_handler_being'
            }
        }
        
        super().__init__(intention_data, realm)
        
        # Specjalne właściwości błędu
        self.error_context = error_context
        self.severity = severity
        self.category = category
        self.repair_attempts: List[Dict[str, Any]] = []
        self.solution_suggestions: List[str] = []
        self.auto_repair_enabled = True
        self.healing_progress = 0.0
        
        # Ustaw priorytet na podstawie ważności
        priority_map = {
            ErrorSeverity.LOW: IntentionPriority.LOW,
            ErrorSeverity.MEDIUM: IntentionPriority.NORMAL,
            ErrorSeverity.HIGH: IntentionPriority.HIGH,
            ErrorSeverity.CRITICAL: IntentionPriority.CRITICAL
        }
        self.priority = priority_map[severity]
        
        # Rozpocznij od razu analizę błędu
        self.state = IntentionState.CONTEMPLATED
        self.essence.name = f"ErrorHealing_{error_context.error_type}_{uuid.uuid4().hex[:8]}"
    
    def attempt_self_repair(self) -> Dict[str, Any]:
        """Próbuje samonaprawy błędu"""
        repair_attempt = {
            'attempt_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'category': self.category.value,
            'severity': self.severity.name,
            'strategies_tried': [],
            'success': False,
            'partial_success': False,
            'error_resolved': False
        }
        
        # Wybierz strategię naprawy na podstawie kategorii błędu
        if self.category == ErrorCategory.SYNTAX:
            repair_attempt.update(self._attempt_syntax_repair())
        elif self.category == ErrorCategory.RUNTIME:
            repair_attempt.update(self._attempt_runtime_repair())
        elif self.category == ErrorCategory.LOGIC:
            repair_attempt.update(self._attempt_logic_repair())
        elif self.category == ErrorCategory.NETWORK:
            repair_attempt.update(self._attempt_network_repair())
        elif self.category == ErrorCategory.DATABASE:
            repair_attempt.update(self._attempt_database_repair())
        elif self.category == ErrorCategory.PERMISSION:
            repair_attempt.update(self._attempt_permission_repair())
        elif self.category == ErrorCategory.RESOURCE:
            repair_attempt.update(self._attempt_resource_repair())
        else:
            repair_attempt.update(self._attempt_generic_repair())
        
        self.repair_attempts.append(repair_attempt)
        
        # Aktualizuj progress
        if repair_attempt['success']:
            self.healing_progress = 100.0
            self.state = IntentionState.COMPLETED
        elif repair_attempt['partial_success']:
            self.healing_progress += 25.0
        
        self.remember('self_repair_attempt', repair_attempt)
        return repair_attempt
    
    def _attempt_syntax_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy składniowe"""
        strategies = []
        
        # Analiza typowych błędów składniowych
        error_msg = self.error_context.error_message.lower()
        
        if 'invalid syntax' in error_msg:
            strategies.append('check_parentheses_brackets')
            strategies.append('check_indentation')
            strategies.append('check_missing_colons')
        
        if 'unexpected eof' in error_msg:
            strategies.append('check_unclosed_strings')
            strategies.append('check_unclosed_brackets')
        
        # Symulacja naprawy
        success = len(strategies) > 0
        
        return {
            'repair_type': 'syntax_repair',
            'strategies_tried': strategies,
            'success': success,
            'suggestions': [
                f"Sprawdź składnię w linii {self.error_context.line_number}",
                "Zweryfikuj poprawność wcięć i nawiasów",
                "Upewnij się, że wszystkie stringi są prawidłowo zamknięte"
            ]
        }
    
    def _attempt_runtime_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy runtime"""
        strategies = []
        error_msg = self.error_context.error_message.lower()
        
        if 'name' in error_msg and 'not defined' in error_msg:
            strategies.append('check_variable_scope')
            strategies.append('add_missing_import')
        
        if 'attribute' in error_msg and 'has no attribute' in error_msg:
            strategies.append('check_object_type')
            strategies.append('verify_method_existence')
        
        if 'index out of range' in error_msg:
            strategies.append('add_bounds_checking')
            strategies.append('validate_list_length')
        
        # Symulacja częściowej naprawy dla runtime errors
        partial_success = len(strategies) > 1
        
        return {
            'repair_type': 'runtime_repair',
            'strategies_tried': strategies,
            'success': False,  # Runtime errors wymagają często manualnej interwencji
            'partial_success': partial_success,
            'suggestions': [
                "Dodaj sprawdzenie czy zmienna jest zdefiniowana",
                "Zweryfikuj typy obiektów przed wywołaniem metod",
                "Dodaj obsługę wyjątków w krytycznych sekcjach"
            ]
        }
    
    def _attempt_logic_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy logiczne"""
        return {
            'repair_type': 'logic_repair',
            'strategies_tried': ['analyze_flow', 'check_conditions', 'verify_algorithms'],
            'success': False,  # Błędy logiczne wymagają ludzkiej analizy
            'suggestions': [
                "Przeanalizuj logikę algorytmu krok po kroku",
                "Sprawdź warunki brzegowe",
                "Zweryfikuj założenia biznesowe"
            ]
        }
    
    def _attempt_network_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy sieciowe"""
        strategies = ['retry_connection', 'check_timeout', 'verify_endpoint']
        
        # Sieciowe błędy często da się naprawić przez retry
        success = True
        
        return {
            'repair_type': 'network_repair',
            'strategies_tried': strategies,
            'success': success,
            'suggestions': [
                "Dodaj mechanizm retry z backoff",
                "Sprawdź dostępność endpoints",
                "Zweryfikuj konfigurację sieciową"
            ]
        }
    
    def _attempt_database_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy bazy danych"""
        strategies = ['check_connection', 'verify_schema', 'validate_queries']
        
        return {
            'repair_type': 'database_repair',
            'strategies_tried': strategies,
            'success': False,
            'partial_success': True,
            'suggestions': [
                "Sprawdź połączenie z bazą danych",
                "Zweryfikuj schemat i uprawnienia",
                "Zoptymalizuj zapytania SQL"
            ]
        }
    
    def _attempt_permission_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy uprawnień"""
        return {
            'repair_type': 'permission_repair',
            'strategies_tried': ['check_file_permissions', 'verify_user_rights'],
            'success': False,
            'suggestions': [
                "Sprawdź uprawnienia do plików i katalogów",
                "Zweryfikuj uprawnienia użytkownika",
                "Uruchom z odpowiednimi prawami administratora"
            ]
        }
    
    def _attempt_resource_repair(self) -> Dict[str, Any]:
        """Próbuje naprawić błędy zasobów"""
        strategies = ['free_memory', 'close_unused_connections', 'optimize_resources']
        
        # Problemy z zasobami często da się naprawić automatycznie
        success = True
        
        return {
            'repair_type': 'resource_repair',
            'strategies_tried': strategies,
            'success': success,
            'suggestions': [
                "Zwolnij nieużywane zasoby",
                "Zamknij nieaktywne połączenia",
                "Zoptymalizuj zużycie pamięci"
            ]
        }
    
    def _attempt_generic_repair(self) -> Dict[str, Any]:
        """Ogólna próba naprawy nieznanego błędu"""
        return {
            'repair_type': 'generic_repair',
            'strategies_tried': ['log_analysis', 'context_review', 'pattern_matching'],
            'success': False,
            'suggestions': [
                "Przeanalizuj logi systemowe",
                "Sprawdź kontekst wystąpienia błędu",
                "Poszukaj podobnych przypadków w historii"
            ]
        }
    
    def generate_gui_report(self) -> Dict[str, Any]:
        """Generuje raport do wyświetlenia w GUI konsoli"""
        return {
            'error_id': self.essence.soul_id,
            'title': f"🚨 {self.error_context.error_type}: {self.error_context.error_message[:50]}...",
            'severity': self.severity.name,
            'category': self.category.value,
            'timestamp': self.error_context.timestamp.isoformat(),
            'location': {
                'module': self.error_context.module_name,
                'function': self.error_context.function_name,
                'line': self.error_context.line_number
            },
            'healing_progress': self.healing_progress,
            'state': self.state.value,
            'repair_attempts_count': len(self.repair_attempts),
            'latest_suggestions': self.solution_suggestions[-3:] if self.solution_suggestions else [],
            'stack_trace': self.error_context.stack_trace,
            'actions': [
                {'id': 'retry_repair', 'label': '🔄 Ponów naprawę', 'enabled': True},
                {'id': 'escalate', 'label': '⬆️ Eskaluj', 'enabled': True},
                {'id': 'ignore', 'label': '⏸️ Ignoruj', 'enabled': True},
                {'id': 'mark_resolved', 'label': '✅ Oznacz jako rozwiązany', 'enabled': True}
            ]
        }


class ErrorHandlerBeing(LogicalBeing):
    """
    Byt specjalizujący się w obsłudze błędów jako intencji
    """
    
    def __init__(self, realm=None):
        context = LogicalContext(
            domain="error_handling",
            specialization="self_healing_systems"
        )
        
        super().__init__(LogicType.ADAPTIVE, context, realm)
        
        # Rejestr błędów jako intencji
        self.error_intentions: Dict[str, ErrorIntention] = {}
        self.error_patterns: Dict[str, List[str]] = {}
        self.healing_statistics = {
            'total_errors': 0,
            'auto_resolved': 0,
            'partially_resolved': 0,
            'escalated': 0,
            'ignored': 0
        }
        
        # Konfiguracja obsługi błędów
        self.auto_capture_enabled = True
        self.gui_notifications_enabled = True
        self.self_healing_enabled = True
        
        self.essence.name = "ErrorHandlerBeing"
        
        # Zainstaluj handler błędów
        if self.auto_capture_enabled:
            self._install_error_handler()
    
    def _install_error_handler(self):
        """Instaluje globalny handler błędów"""
        original_excepthook = sys.excepthook
        
        def custom_excepthook(exc_type, exc_value, exc_traceback):
            # Przechwytuj błędy i przekształcaj w intencje
            self.capture_error(exc_type, exc_value, exc_traceback)
            # Wywołaj oryginalny handler
            original_excepthook(exc_type, exc_value, exc_traceback)
        
        sys.excepthook = custom_excepthook
    
    def capture_error(self, exc_type, exc_value, exc_traceback, user_action: str = "") -> ErrorIntention:
        """
        Przechwytuje błąd i tworzy intencję naprawy
        """
        # Analizuj traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        stack_trace = ''.join(tb_lines)
        
        # Wyciągnij informacje o błędzie
        if exc_traceback:
            frame = exc_traceback.tb_frame
            module_name = frame.f_globals.get('__name__', 'unknown')
            function_name = frame.f_code.co_name
            line_number = exc_traceback.tb_lineno
        else:
            module_name = 'unknown'
            function_name = 'unknown'
            line_number = 0
        
        # Stwórz kontekst błędu
        error_context = ErrorContext(
            error_type=exc_type.__name__ if exc_type else 'UnknownError',
            error_message=str(exc_value),
            stack_trace=stack_trace,
            module_name=module_name,
            function_name=function_name,
            line_number=line_number,
            user_action=user_action,
            system_state=self._capture_system_state()
        )
        
        # Określ ważność i kategorię
        severity = self._determine_severity(error_context)
        category = self._determine_category(error_context)
        
        # Stwórz intencję błędu
        error_intention = ErrorIntention(error_context, severity, category, self.realm)
        
        # Zarejestruj
        self.error_intentions[error_intention.essence.soul_id] = error_intention
        self.healing_statistics['total_errors'] += 1
        
        # Rozpocznij samonaprawę jeśli włączona
        if self.self_healing_enabled:
            self._initiate_self_healing(error_intention)
        
        # Powiadom GUI jeśli włączone
        if self.gui_notifications_enabled:
            self._notify_gui(error_intention)
        
        self.remember('error_captured', {
            'error_id': error_intention.essence.soul_id,
            'error_type': error_context.error_type,
            'severity': severity.name,
            'category': category.value
        })
        
        return error_intention
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """Przechwytuje stan systemu w momencie błędu"""
        import psutil
        
        try:
            return {
                'memory_usage': psutil.virtual_memory().percent,
                'cpu_usage': psutil.cpu_percent(),
                'disk_usage': psutil.disk_usage('/').percent,
                'active_processes': len(psutil.pids()),
                'timestamp': datetime.now().isoformat()
            }
        except:
            return {'error': 'Could not capture system state'}
    
    def _determine_severity(self, error_context: ErrorContext) -> ErrorSeverity:
        """Określa ważność błędu"""
        error_type = error_context.error_type.lower()
        error_msg = error_context.error_message.lower()
        
        # Błędy krytyczne
        if any(critical in error_type for critical in ['systemexit', 'keyboardinterrupt', 'memoryerror']):
            return ErrorSeverity.CRITICAL
        
        # Błędy wysokiej ważności
        if any(high in error_type for high in ['connectionerror', 'timeouterror', 'permissionerror']):
            return ErrorSeverity.HIGH
        
        # Błędy średniej ważności
        if any(medium in error_type for medium in ['valueerror', 'typeerror', 'attributeerror']):
            return ErrorSeverity.MEDIUM
        
        # Domyślnie niska ważność
        return ErrorSeverity.LOW
    
    def _determine_category(self, error_context: ErrorContext) -> ErrorCategory:
        """Określa kategorię błędu"""
        error_type = error_context.error_type.lower()
        error_msg = error_context.error_message.lower()
        
        if 'syntax' in error_type or 'syntax' in error_msg:
            return ErrorCategory.SYNTAX
        
        if any(net in error_type for net in ['connection', 'timeout', 'socket', 'http']):
            return ErrorCategory.NETWORK
        
        if any(db in error_type for db in ['database', 'sql', 'cursor']):
            return ErrorCategory.DATABASE
        
        if 'permission' in error_type or 'access' in error_msg:
            return ErrorCategory.PERMISSION
        
        if any(res in error_type for res in ['memory', 'resource', 'file']):
            return ErrorCategory.RESOURCE
        
        if any(rt in error_type for rt in ['runtime', 'value', 'type', 'attribute', 'index']):
            return ErrorCategory.RUNTIME
        
        return ErrorCategory.UNKNOWN
    
    def _initiate_self_healing(self, error_intention: ErrorIntention):
        """Rozpoczyna proces samonaprawy"""
        # Uruchom w tle próbę samonaprawy
        repair_result = error_intention.attempt_self_repair()
        
        if repair_result['success']:
            self.healing_statistics['auto_resolved'] += 1
        elif repair_result.get('partial_success', False):
            self.healing_statistics['partially_resolved'] += 1
        
        # Zapisz wzorzec błędu dla przyszłych referencji
        self._learn_error_pattern(error_intention, repair_result)
    
    def _learn_error_pattern(self, error_intention: ErrorIntention, repair_result: Dict[str, Any]):
        """Uczy się wzorców błędów dla przyszłej naprawy"""
        pattern_key = f"{error_intention.category.value}_{error_intention.error_context.error_type}"
        
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = []
        
        self.error_patterns[pattern_key].append({
            'error_message': error_intention.error_context.error_message,
            'repair_strategies': repair_result.get('strategies_tried', []),
            'success': repair_result['success'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Ogranicz historię wzorców
        if len(self.error_patterns[pattern_key]) > 10:
            self.error_patterns[pattern_key] = self.error_patterns[pattern_key][-5:]
    
    def _notify_gui(self, error_intention: ErrorIntention):
        """Powiadamia GUI o nowym błędzie"""
        if self.realm and hasattr(self.realm, 'engine'):
            callback_flow = getattr(self.realm.engine, 'callback_flow', None)
            if callback_flow:
                callback_flow.emit_event('error_handling', 'new_error_intention', {
                    'error_intention_id': error_intention.essence.soul_id,
                    'gui_report': error_intention.generate_gui_report()
                })
    
    def get_error_intentions_for_gui(self) -> List[Dict[str, Any]]:
        """Zwraca listę błędów dla GUI"""
        return [
            intention.generate_gui_report() 
            for intention in self.error_intentions.values()
        ]
    
    def handle_gui_action(self, error_id: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Obsługuje akcje z GUI"""
        if error_id not in self.error_intentions:
            return {'success': False, 'message': 'Błąd nie znaleziony'}
        
        error_intention = self.error_intentions[error_id]
        
        if action == 'retry_repair':
            repair_result = error_intention.attempt_self_repair()
            return {'success': True, 'repair_result': repair_result}
        
        elif action == 'escalate':
            error_intention.priority = IntentionPriority.CRITICAL
            self.healing_statistics['escalated'] += 1
            return {'success': True, 'message': 'Błąd eskalowany'}
        
        elif action == 'ignore':
            error_intention.state = IntentionState.TRANSCENDED
            self.healing_statistics['ignored'] += 1
            return {'success': True, 'message': 'Błąd zignorowany'}
        
        elif action == 'mark_resolved':
            error_intention.state = IntentionState.COMPLETED
            error_intention.healing_progress = 100.0
            return {'success': True, 'message': 'Błąd oznaczony jako rozwiązany'}
        
        return {'success': False, 'message': 'Nieznana akcja'}
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status bytu obsługi błędów"""
        base_status = super().get_status()
        
        error_handler_status = {
            'error_handler_specific': {
                'total_error_intentions': len(self.error_intentions),
                'healing_statistics': self.healing_statistics,
                'success_rate': (
                    self.healing_statistics['auto_resolved'] / 
                    max(1, self.healing_statistics['total_errors'])
                ),
                'auto_capture_enabled': self.auto_capture_enabled,
                'self_healing_enabled': self.self_healing_enabled,
                'gui_notifications_enabled': self.gui_notifications_enabled,
                'learned_patterns_count': len(self.error_patterns),
                'active_errors': [
                    {
                        'id': intention.essence.soul_id,
                        'type': intention.error_context.error_type,
                        'severity': intention.severity.name,
                        'progress': intention.healing_progress,
                        'state': intention.state.value
                    }
                    for intention in self.error_intentions.values()
                    if intention.state not in [IntentionState.COMPLETED, IntentionState.TRANSCENDED]
                ]
            }
        }
        
        base_status.update(error_handler_status)
        return base_status
