"""
🩹 SelfHealingFlow - Przepływ Samonaprawy

Zarządza procesem samonaprawy błędów reprezentowanych jako intencje.
Koordynuje działania między bytami specjalistycznymi a systemem GUI.
"""

import asyncio
import threading
import queue
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..beings.error_handler_being import ErrorHandlerBeing
from ..beings.pdf_generator_being import PDFGeneratorBeing
from .secure_code_flow import SecureCodeFlow
from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority


class SelfHealingFlow:
    """
    Przepływ samonaprawy - koordynuje działania healing bytów
    """

    def __init__(self, astral_engine):
        self.engine = astral_engine

        # Byty specjalistyczne
        self.error_handler: Optional[ErrorHandlerBeing] = None
        self.pdf_generator: Optional[PDFGeneratorBeing] = None
        self.specialist_beings: Dict[str, Any] = {}

        # Kolejki zadań
        self.healing_queue = queue.PriorityQueue()
        self.notification_queue = queue.Queue()

        # Workery
        self._healing_worker: Optional[threading.Thread] = None
        self._notification_worker: Optional[threading.Thread] = None
        self._running = False

        # Callback namespace
        self.callback_namespace: Optional[CallbackNamespace] = None

        # Statystyki
        self.healing_statistics = {
            'total_healing_attempts': 0,
            'successful_healings': 0,
            'failed_healings': 0,
            'specialist_activations': 0
        }

        self.start_time = datetime.now()

    def initialize(self):
        """Inicjalizuje przepływ samonaprawy"""

        # Utwórz byty specjalistyczne
        self._create_specialist_beings()

        # Utwórz namespace callbacków
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('self_healing')
            self._setup_healing_callbacks()

        # Uruchom workery
        self._running = True
        self._healing_worker = threading.Thread(target=self._healing_worker_loop, daemon=True)
        self._notification_worker = threading.Thread(target=self._notification_worker_loop, daemon=True)

        self._healing_worker.start()
        self._notification_worker.start()

        self.engine.logger.info("🩹 SelfHealingFlow zainicjalizowany")

    def start(self) -> bool:
        """Uruchamia przepływ samonaprawy"""
        if self._running:
            self.engine.logger.warning("SelfHealingFlow już działa")
            return True

        self.initialize()
        return True

    def _create_specialist_beings(self):
        """Tworzy byty specjalistyczne"""

        # Error Handler Being
        self.error_handler = ErrorHandlerBeing(realm=self._get_error_realm())
        self.specialist_beings['error_handler'] = self.error_handler

        # PDF Generator Being  
        self.pdf_generator = PDFGeneratorBeing(realm=self._get_default_realm())
        self.specialist_beings['pdf_generator'] = self.pdf_generator

        # System bezpiecznego generowania kodu
        self.secure_code_flow = SecureCodeFlow(self.engine)
        self.specialist_beings['secure_code_flow'] = self.secure_code_flow


        self.engine.logger.info("🤖 Byty specjalistyczne utworzone")

    def _get_error_realm(self):
        """Pobiera wymiar dla błędów lub tworzy memory realm"""
        if hasattr(self.engine, 'realms'):
            # Spróbuj użyć intentions realm
            return self.engine.realms.get('intentions', None)
        return None

    def _get_default_realm(self):
        """Pobiera domyślny wymiar"""
        if hasattr(self.engine, 'realms'):
            return self.engine.realms.get('astral_prime', None)
        return None

    def _setup_healing_callbacks(self):
        """Konfiguruje callbacki dla samonaprawy"""
        if not self.callback_namespace:
            return

        def on_error_captured(event):
            """Callback gdy błąd zostanie przechwycony"""
            error_data = event.data
            self._queue_healing_task(error_data.get('error_intention_id'), 'error_healing', 3)

        def on_specialist_needed(event):
            """Callback gdy potrzebny jest specjalista"""
            specialist_data = event.data
            specialist_type = specialist_data.get('specialist_type')
            task_data = specialist_data.get('task_data', {})

            self._activate_specialist(specialist_type, task_data)

        def on_gui_action(event):
            """Callback dla akcji z GUI"""
            action_data = event.data
            self._handle_gui_action(action_data)

        # Rejestruj callbacki
        self.callback_namespace.on('error_captured', on_error_captured, CallbackPriority.HIGH)
        self.callback_namespace.on('specialist_needed', on_specialist_needed, CallbackPriority.NORMAL)
        self.callback_namespace.on('gui_action', on_gui_action, CallbackPriority.NORMAL)

    def _queue_healing_task(self, intention_id: str, task_type: str, priority: int):
        """Dodaje zadanie naprawy do kolejki"""
        healing_task = {
            'id': intention_id,
            'type': task_type,
            'priority': priority,
            'queued_at': datetime.now(),
            'attempts': 0
        }

        # Kolejka priorytetowa (niższa liczba = wyższy priorytet)
        self.healing_queue.put((priority, datetime.now(), healing_task))

        self.engine.logger.info(f"🩹 Zadanie healing dodane do kolejki: {task_type}")

    def _healing_worker_loop(self):
        """Pętla workera naprawy"""
        while self._running:
            try:
                # Pobierz zadanie z kolejki (timeout 1s)
                priority, queued_time, task = self.healing_queue.get(timeout=1.0)

                # Przetworz zadanie
                success = self._process_healing_task(task)

                # Aktualizuj statystyki
                self.healing_statistics['total_healing_attempts'] += 1
                if success:
                    self.healing_statistics['successful_healings'] += 1
                else:
                    self.healing_statistics['failed_healings'] += 1

                self.healing_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🩹 Błąd w healing worker: {e}")

    def _process_healing_task(self, task: Dict[str, Any]) -> bool:
        """Przetwarza zadanie naprawy"""
        try:
            task_type = task['type']
            intention_id = task['id']

            if task_type == 'error_healing' and self.error_handler:
                # Znajdź intencję błędu
                if intention_id in self.error_handler.error_intentions:
                    error_intention = self.error_handler.error_intentions[intention_id]

                    # Spróbuj samonaprawy
                    repair_result = error_intention.attempt_self_repair()

                    # Powiadom GUI
                    self._notify_gui_healing_progress(intention_id, repair_result)

                    return repair_result.get('success', False)

            elif task_type == 'pdf_generation' and self.pdf_generator:
                # Zadanie generowania PDF delegowane do specjalisty
                return self._delegate_pdf_generation(task)

            return False

        except Exception as e:
            self.engine.logger.error(f"🩹 Błąd przetwarzania zadania healing: {e}")
            return False

    def _delegate_pdf_generation(self, task: Dict[str, Any]) -> bool:
        """Deleguje generowanie PDF do specjalisty"""
        try:
            if not self.pdf_generator:
                return False

            # Pobierz dane zadania
            generation_data = task.get('generation_data', {})
            text = generation_data.get('text', '')
            style = generation_data.get('style', 'manifest')
            title = generation_data.get('title')

            # Wykonaj generowanie
            result = self.pdf_generator.generate_from_text(text, style, title)

            # Powiadom o wyniku
            self._notify_gui_generation_result(task['id'], result)

            return result.get('document_info', {}).get('success', False)

        except Exception as e:
            self.engine.logger.error(f"📄 Błąd delegacji PDF: {e}")
            return False

    def _notify_gui_healing_progress(self, intention_id: str, repair_result: Dict[str, Any]):
        """Powiadamia GUI o postępie naprawy"""
        notification = {
            'type': 'healing_progress',
            'intention_id': intention_id,
            'repair_result': repair_result,
            'timestamp': datetime.now().isoformat()
        }

        self.notification_queue.put(notification)

    def _notify_gui_generation_result(self, task_id: str, result: Dict[str, Any]):
        """Powiadamia GUI o wyniku generowania"""
        notification = {
            'type': 'pdf_generation_result',
            'task_id': task_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }

        self.notification_queue.put(notification)

    def _notification_worker_loop(self):
        """Pętla workera powiadomień"""
        while self._running:
            try:
                # Pobierz powiadomienie
                notification = self.notification_queue.get(timeout=1.0)

                # Wyślij przez callback system
                if self.callback_namespace:
                    self.callback_namespace.emit('gui_notification', notification)

                self.notification_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🔔 Błąd w notification worker: {e}")

    def _activate_specialist(self, specialist_type: str, task_data: Dict[str, Any]):
        """Aktywuje specjalistę do zadania"""
        self.healing_statistics['specialist_activations'] += 1

        if specialist_type == 'pdf_generator':
            self._queue_healing_task(
                task_data.get('task_id', 'pdf_gen_' + datetime.now().strftime('%H%M%S')),
                'pdf_generation',
                2
            )

        elif specialist_type == 'error_handler':
            # Error handler już aktywny poprzez system przechwytywania
            pass

    def _handle_gui_action(self, action_data: Dict[str, Any]):
        """Obsługuje akcje z GUI"""
        action_type = action_data.get('action_type')

        if action_type == 'retry_healing':
            intention_id = action_data.get('intention_id')
            self._queue_healing_task(intention_id, 'error_healing', 2)

        elif action_type == 'generate_pdf':
            generation_data = action_data.get('generation_data', {})
            task_id = f"gui_pdf_{datetime.now().strftime('%H%M%S')}"

            task = {
                'id': task_id,
                'type': 'pdf_generation',
                'generation_data': generation_data,
                'priority': 2,
                'queued_at': datetime.now()
            }

            self.healing_queue.put((2, datetime.now(), task))

        elif action_type == 'escalate_error' and self.error_handler:
            intention_id = action_data.get('intention_id')
            self.error_handler.handle_gui_action(intention_id, 'escalate')

    def capture_error(self, exc_type, exc_value, exc_traceback, user_action: str = "") -> Optional[str]:
        """
        Publiczny interfejs do przechwytywania błędów

        Returns:
            ID intencji błędu jeśli utworzono
        """
        if not self.error_handler:
            return None

        try:
            error_intention = self.error_handler.capture_error(
                exc_type, exc_value, exc_traceback, user_action
            )
            return error_intention.essence.soul_id

        except Exception as e:
            self.engine.logger.error(f"🚨 Błąd przechwytywania błędu: {e}")
            return None

    def generate_pdf_from_text(self, text: str, style: str = "manifest", title: str = None) -> Dict[str, Any]:
        """
        Publiczny interfejs do generowania PDF
        """
        if not self.pdf_generator:
            return {'success': False, 'error': 'PDF Generator nie dostępny'}

        try:
            return self.pdf_generator.generate_from_text(text, style, title)

        except Exception as e:
            self.engine.logger.error(f"📄 Błąd generowania PDF: {e}")
            return {'success': False, 'error': str(e)}

    def get_error_dashboard_data(self) -> Dict[str, Any]:
        """Zwraca dane dla dashboard błędów w GUI"""
        if not self.error_handler:
            return {'errors': [], 'statistics': {}}

        return {
            'errors': self.error_handler.get_error_intentions_for_gui(),
            'statistics': self.healing_statistics,
            'error_handler_status': self.error_handler.get_status()
        }

    def get_pdf_dashboard_data(self) -> Dict[str, Any]:
        """Zwraca dane dla dashboard PDF w GUI"""
        if not self.pdf_generator:
            return {'documents': [], 'statistics': {}}

        return {
            'documents': self.pdf_generator.list_generated_documents(),
            'statistics': {
                'total_generated': self.pdf_generator.total_generated,
                'success_rate': (
                    self.pdf_generator.successful_generations / 
                    max(1, self.pdf_generator.total_generated)
                ),
                'average_time': self.pdf_generator.average_generation_time
            },
            'pdf_generator_status': self.pdf_generator.get_status()
        }

    def generate_repair_function(self, error_intention: 'IntentionBeing') -> Dict[str, Any]:
        """
        Generuje bezpieczną funkcję naprawczą dla błędu
        """
        try:
            repair_context = {
                'error_type': error_intention.materialna.wymagania[0] if error_intention.materialna.wymagania else 'unknown',
                'repair_needed': True,
                'security_level': 'standard'
            }

            # Użyj SecureCodeFlow do wygenerowania funkcji naprawczej
            result = self.secure_code_flow.generate_secure_function(error_intention, repair_context)

            if result.get('status') == 'generated':
                self.engine.logger.info(f"🔧 Funkcja naprawcza wygenerowana: {result['function_name']}")

                # Spróbuj wykonać funkcję naprawczą
                execution_result = self.secure_code_flow.execute_dimension_function(
                    result['function_id'],
                    args=[error_intention.materialna.techniczne_detale],
                    kwargs={'auto_repair': True}
                )

                return {
                    'repair_function_generated': True,
                    'function_id': result['function_id'],
                    'execution_result': execution_result,
                    'dimension_layer': result['dimension_layer']
                }

            return {'repair_function_generated': False, 'reason': result.get('reason', 'Unknown')}

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd generowania funkcji naprawczej: {e}")
            return {'repair_function_generated': False, 'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu samonaprawy"""
        return {
            'type': 'self_healing_flow',
            'running': self._running,
            'healing_queue_size': self.healing_queue.qsize(),
            'notification_queue_size': self.notification_queue.qsize(),
            'healing_statistics': self.healing_statistics,
            'specialist_beings': {
                name: being.get_status() if hasattr(being, 'get_status') else {'name': name}
                for name, being in self.specialist_beings.items()
            },
            'secure_code_system': self.secure_code_flow.get_status(),
            'uptime': str(datetime.now() - self.start_time),
            'error_handler_active': self.error_handler is not None,
            'pdf_generator_active': self.pdf_generator is not None
        }

    def stop(self):
        """Zatrzymuje przepływ samonaprawy"""
        self._running = False

        # Poczekaj na zakończenie kolejek
        if not self.healing_queue.empty():
            self.healing_queue.join()

        if not self.notification_queue.empty():
            self.notification_queue.join()

        self.engine.logger.info("🩹 SelfHealingFlow zatrzymany")

    def handle_await_expression_error(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Specjalizowana obsługa błędu 'dict can't be used in await expression'
        """
        try:
            # Identyfikuj lokalizację błędu
            error_location = error_context.get('traceback', '')
            function_name = error_context.get('function_name', 'unknown')

            # Wygeneruj intencję naprawy
            repair_intention = self.engine.manifest_intention({
                'duchowa': {
                    'opis_intencji': f'Napraw błąd await na dict w funkcji {function_name}',
                    'kontekst': 'TypeError: object dict can\'t be used in \'await\' expression',
                    'inspiracja': 'Przekształć synchroniczne wywołania w asynchroniczne',
                    'energia_duchowa': 90.0
                },
                'materialna': {
                    'zadanie': 'async_await_correction',
                    'wymagania': ['detect_sync_calls', 'wrap_in_coroutine', 'preserve_functionality'],
                    'oczekiwany_rezultat': 'Poprawne działanie asynchronicznej funkcji'
                },
                'metainfo': {
                    'zrodlo': 'self_healing_await_error',
                    'tags': ['async', 'await', 'type_error', 'auto_repair']
                }
            })

            # Wygeneruj funkcję naprawczą
            repair_result = self.generate_repair_function(repair_intention)

            if repair_result.get('repair_function_generated'):
                self.engine.logger.info(f"🔧 Funkcja naprawcza wygenerowana dla błędu await")

                # Wykonaj natychmiastową naprawę w pamięci
                self._apply_immediate_await_fix(error_context)

                return {
                    'status': 'repaired',
                    'repair_type': 'await_expression_fix',
                    'function_id': repair_result.get('function_id'),
                    'immediate_fix_applied': True
                }

            return {'status': 'repair_failed', 'reason': 'Could not generate repair function'}

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd obsługi await error: {e}")
            return {'status': 'error', 'error': str(e)}

    def _apply_immediate_await_fix(self, error_context: Dict[str, Any]):
        """
        Aplikuje natychmiastową naprawę błędu await w pamięci
        """
        try:
            # Znajdź problematyczne wywołania w aktywnych flow
            for flow_name, flow in self.engine.flows.items():
                if hasattr(flow, '_fix_await_expressions'):
                    flow._fix_await_expressions()

            # Napraw w bytach logicznych
            for being_name, being in self.specialist_beings.items():
                if hasattr(being, 'fix_async_calls'):
                    being.fix_async_calls()

            self.engine.logger.info("🩹 Natychmiastowa naprawa await zastosowana")

        except Exception as e:
            self.engine.logger.error(f"❌ Błąd natychmiastowej naprawy: {e}")