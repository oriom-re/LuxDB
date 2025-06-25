
"""
🎯 IntentionFlow - Przepływ Komunikacji dla Systemu Intencji

Zarządza kanałami komunikacji, interakcjami i callbackami dla intencji
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
import threading
import queue
import uuid

from .callback_flow import CallbackFlow, CallbackNamespace, CallbackPriority
from ..beings.intention_being import IntentionBeing, IntentionState


class IntentionCommunicationChannel:
    """Kanał komunikacji dla konkretnej intencji"""
    
    def __init__(self, intention: IntentionBeing, flow_manager):
        self.intention = intention
        self.flow_manager = flow_manager
        self.channel_id = intention.get_communication_channel()
        
        self.subscribers: List[str] = []
        self.message_history: List[Dict[str, Any]] = []
        self.interaction_buttons = self._create_interaction_buttons()
        
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def _create_interaction_buttons(self) -> Dict[str, Dict[str, Any]]:
        """Tworzy przyciski interakcji dla intencji"""
        return {
            'wzmocnij': {
                'label': '💪 Wzmocnij',
                'description': 'Wzmacnia energię intencji',
                'enabled': True,
                'callback': self._handle_wzmocnij
            },
            'korektuj': {
                'label': '✏️ Zaproponuj korektę',
                'description': 'Sugeruje zmiany w intencji',
                'enabled': True,
                'callback': self._handle_korektuj
            },
            'realizuj': {
                'label': '🚀 Zainicjuj realizację',
                'description': 'Rozpoczyna materializację intencji',
                'enabled': self.intention.state in [IntentionState.CONTEMPLATED, IntentionState.APPROVED],
                'callback': self._handle_realizuj
            },
            'przypisz_opiekuna': {
                'label': '👤 Przypisz opiekuna',
                'description': 'Przypisuje opiekuna intencji',
                'enabled': True,
                'callback': self._handle_przypisz_opiekuna
            },
            'zatwierdz': {
                'label': '✅ Zatwierdź',
                'description': 'Zatwierdza intencję do realizacji',
                'enabled': self.intention.state == IntentionState.CONTEMPLATED,
                'callback': self._handle_zatwierdz
            }
        }
    
    def _handle_wzmocnij(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Obsługuje wzmocnienie intencji"""
        power = data.get('power', 10)
        return self.intention.add_interaction('wzmocnij', {'power': power}, user_id)
    
    def _handle_korektuj(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Obsługuje korektę intencji"""
        return self.intention.add_interaction('korektuj', data, user_id)
    
    def _handle_realizuj(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Obsługuje rozpoczęcie realizacji"""
        return self.intention.add_interaction('realizuj', data, user_id)
    
    def _handle_przypisz_opiekuna(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Obsługuje przypisanie opiekuna"""
        return self.intention.add_interaction('przypisz_opiekuna', data, user_id)
    
    def _handle_zatwierdz(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Obsługuje zatwierdzenie intencji"""
        return self.intention.approve_intention(user_id)
    
    def add_message(self, message_type: str, content: Any, sender_id: str = "system") -> Dict[str, Any]:
        """Dodaje wiadomość do kanału"""
        message = {
            'id': str(uuid.uuid4()),
            'type': message_type,
            'content': content,
            'sender_id': sender_id,
            'timestamp': datetime.now().isoformat(),
            'channel_id': self.channel_id
        }
        
        self.message_history.append(message)
        self.last_activity = datetime.now()
        
        # Ogranicz historię
        if len(self.message_history) > 100:
            self.message_history = self.message_history[-50:]
        
        return message
    
    def process_interaction(self, button_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Przetwarza interakcję przyciskiem"""
        if button_id not in self.interaction_buttons:
            return {'success': False, 'message': f'Nieznany przycisk: {button_id}'}
        
        button = self.interaction_buttons[button_id]
        
        if not button['enabled']:
            return {'success': False, 'message': f'Przycisk {button_id} jest nieaktywny'}
        
        try:
            result = button['callback'](data, user_id)
            
            # Dodaj wiadomość o interakcji
            self.add_message('interaction', {
                'button': button_id,
                'user_id': user_id,
                'data': data,
                'result': result
            }, user_id)
            
            # Aktualizuj stan przycisków
            self.interaction_buttons = self._create_interaction_buttons()
            
            return result
            
        except Exception as e:
            error_result = {'success': False, 'message': f'Błąd interakcji: {str(e)}'}
            self.add_message('error', error_result, user_id)
            return error_result
    
    def subscribe(self, user_id: str) -> bool:
        """Subskrybuje użytkownika do kanału"""
        if user_id not in self.subscribers:
            self.subscribers.append(user_id)
            self.add_message('system', f'Użytkownik {user_id} dołączył do kanału')
            return True
        return False
    
    def unsubscribe(self, user_id: str) -> bool:
        """Usuwa subskrypcję użytkownika"""
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            self.add_message('system', f'Użytkownik {user_id} opuścił kanał')
            return True
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status kanału"""
        return {
            'channel_id': self.channel_id,
            'intention_id': self.intention.essence.soul_id,
            'intention_name': self.intention.essence.name,
            'intention_state': self.intention.state.value,
            'subscribers_count': len(self.subscribers),
            'messages_count': len(self.message_history),
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'available_buttons': [
                {
                    'id': btn_id,
                    'label': btn['label'],
                    'description': btn['description'],
                    'enabled': btn['enabled']
                }
                for btn_id, btn in self.interaction_buttons.items()
            ]
        }


class IntentionFlow:
    """
    Przepływ komunikacji dla systemu intencji
    Zarządza kanałami, interakcjami i callbackami
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        
        # Kanały komunikacji
        self.communication_channels: Dict[str, IntentionCommunicationChannel] = {}
        
        # Namespace callbacków
        self.callback_namespace: Optional[CallbackNamespace] = None
        
        # Kolejka materializacji
        self.materialization_queue = queue.Queue()
        self._materialization_worker: Optional[threading.Thread] = None
        self._running = False
        
        # Statystyki
        self.total_interactions = 0
        self.successful_materializations = 0
        self.failed_materializations = 0
        
        self.start_time = datetime.now()
    
    def initialize(self):
        """Inicjalizuje przepływ intencji"""
        # Utwórz namespace callbacków jeśli callback_flow dostępny
        if hasattr(self.engine, 'callback_flow') and self.engine.callback_flow:
            self.callback_namespace = self.engine.callback_flow.create_namespace('intentions')
            self._setup_intention_callbacks()
        
        # Uruchom worker materializacji
        self._running = True
        self._materialization_worker = threading.Thread(target=self._materialization_worker_loop, daemon=True)
        self._materialization_worker.start()
        
        self.engine.logger.info("🎯 IntentionFlow zainicjalizowany")
    
    def _setup_intention_callbacks(self):
        """Konfiguruje callbacki dla intencji"""
        if not self.callback_namespace:
            return
        
        def on_intention_manifested(event):
            """Callback po manifestacji intencji"""
            intention_data = event.data
            intention_id = intention_data.get('intention_id')
            
            # Utwórz kanał komunikacji
            if intention_id:
                realm_name = intention_data.get('realm')
                if realm_name and hasattr(self.engine, 'realms'):
                    realm = self.engine.realms.get(realm_name)
                    if realm and hasattr(realm, 'get_intention_by_id'):
                        intention = realm.get_intention_by_id(intention_id)
                        if intention:
                            self.create_communication_channel(intention)
        
        def on_materialization_started(event):
            """Callback rozpoczęcia materializacji"""
            materialization_data = event.data
            self.queue_materialization(materialization_data)
        
        def on_intention_interaction(event):
            """Callback interakcji z intencją"""
            self.total_interactions += 1
            interaction_data = event.data
            
            # Powiadom subskrybentów kanału
            intention_id = interaction_data.get('intention_id')
            if intention_id:
                self.broadcast_to_intention_channel(intention_id, 'interaction', interaction_data)
        
        # Rejestruj callbacki
        self.callback_namespace.on('intention_manifested', on_intention_manifested, CallbackPriority.NORMAL)
        self.callback_namespace.on('materialization_started', on_materialization_started, CallbackPriority.HIGH)
        self.callback_namespace.on('intention_interaction', on_intention_interaction, CallbackPriority.NORMAL)
    
    def create_communication_channel(self, intention: IntentionBeing) -> IntentionCommunicationChannel:
        """
        Tworzy kanał komunikacji dla intencji
        
        Args:
            intention: Byt intencji
            
        Returns:
            Kanał komunikacji
        """
        channel = IntentionCommunicationChannel(intention, self)
        self.communication_channels[intention.essence.soul_id] = channel
        
        # Dodaj wiadomość powitalną
        channel.add_message('system', {
            'type': 'welcome',
            'intention_name': intention.essence.name,
            'intention_description': intention.duchowa.opis_intencji,
            'task': intention.materialna.zadanie,
            'current_state': intention.state.value
        })
        
        self.engine.logger.info(f"🎯 Kanał komunikacji utworzony dla intencji: {intention.essence.name}")
        return channel
    
    def get_communication_channel(self, intention_id: str) -> Optional[IntentionCommunicationChannel]:
        """Pobiera kanał komunikacji dla intencji"""
        return self.communication_channels.get(intention_id)
    
    def process_interaction(self, intention_id: str, button_id: str, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Przetwarza interakcję użytkownika z intencją
        
        Args:
            intention_id: ID intencji
            button_id: ID przycisku interakcji
            data: Dane interakcji
            user_id: ID użytkownika
            
        Returns:
            Wynik interakcji
        """
        channel = self.get_communication_channel(intention_id)
        if not channel:
            return {'success': False, 'message': 'Kanał komunikacji nie znaleziony'}
        
        result = channel.process_interaction(button_id, data, user_id)
        
        # Emituj wydarzenie
        if self.callback_namespace:
            self.callback_namespace.emit('intention_interaction_processed', {
                'intention_id': intention_id,
                'button_id': button_id,
                'user_id': user_id,
                'result': result
            })
        
        return result
    
    def queue_materialization(self, materialization_data: Dict[str, Any]):
        """Dodaje zadanie materializacji do kolejki"""
        materialization_task = {
            'id': str(uuid.uuid4()),
            'intention_id': materialization_data.get('intention_id'),
            'zadanie': materialization_data.get('zadanie'),
            'wymagania': materialization_data.get('wymagania', []),
            'deadline': materialization_data.get('deadline'),
            'queued_at': datetime.now().isoformat(),
            'status': 'queued'
        }
        
        self.materialization_queue.put(materialization_task)
        self.engine.logger.info(f"🚀 Zadanie materializacji dodane do kolejki: {materialization_task['id']}")
    
    def _materialization_worker_loop(self):
        """Pętla workera materializacji"""
        while self._running:
            try:
                # Pobierz zadanie z kolejki
                task = self.materialization_queue.get(timeout=1.0)
                
                # Przetworz zadanie
                success = self._process_materialization_task(task)
                
                if success:
                    self.successful_materializations += 1
                else:
                    self.failed_materializations += 1
                
                self.materialization_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                self.engine.logger.error(f"🚀 Błąd workera materializacji: {e}")
    
    def _process_materialization_task(self, task: Dict[str, Any]) -> bool:
        """Przetwarza zadanie materializacji"""
        try:
            intention_id = task['intention_id']
            
            # Symulacja przetwarzania zadania
            self.engine.logger.info(f"🚀 Przetwarzanie materializacji: {task['zadanie']}")
            
            # Powiadom kanał o rozpoczęciu
            self.broadcast_to_intention_channel(intention_id, 'materialization_started', {
                'task_id': task['id'],
                'zadanie': task['zadanie']
            })
            
            # Tu byłaby rzeczywista logika wykonania zadania
            # Na razie symulacja sukcesu
            import time
            time.sleep(1)  # Symulacja pracy
            
            # Powiadom o zakończeniu
            self.broadcast_to_intention_channel(intention_id, 'materialization_completed', {
                'task_id': task['id'],
                'success': True,
                'completed_at': datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            self.engine.logger.error(f"🚀 Błąd przetwarzania materializacji: {e}")
            
            # Powiadom o błędzie
            intention_id = task.get('intention_id')
            if intention_id:
                self.broadcast_to_intention_channel(intention_id, 'materialization_failed', {
                    'task_id': task['id'],
                    'error': str(e),
                    'failed_at': datetime.now().isoformat()
                })
            
            return False
    
    def broadcast_to_intention_channel(self, intention_id: str, message_type: str, content: Any):
        """Wysyła broadcast do kanału intencji"""
        channel = self.get_communication_channel(intention_id)
        if channel:
            channel.add_message(message_type, content, "system")
    
    def subscribe_to_intention(self, intention_id: str, user_id: str) -> Dict[str, Any]:
        """Subskrybuje użytkownika do kanału intencji"""
        channel = self.get_communication_channel(intention_id)
        if not channel:
            return {'success': False, 'message': 'Kanał nie znaleziony'}
        
        success = channel.subscribe(user_id)
        return {
            'success': success,
            'message': 'Subskrypcja dodana' if success else 'Już subskrybowany',
            'channel_id': channel.channel_id
        }
    
    def unsubscribe_from_intention(self, intention_id: str, user_id: str) -> Dict[str, Any]:
        """Usuwa subskrypcję użytkownika"""
        channel = self.get_communication_channel(intention_id)
        if not channel:
            return {'success': False, 'message': 'Kanał nie znaleziony'}
        
        success = channel.unsubscribe(user_id)
        return {
            'success': success,
            'message': 'Subskrypcja usunięta' if success else 'Nie był subskrybowany'
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu intencji"""
        return {
            'type': 'intention_flow',
            'running': self._running,
            'active_channels': len(self.communication_channels),
            'materialization_queue_size': self.materialization_queue.qsize(),
            'total_interactions': self.total_interactions,
            'successful_materializations': self.successful_materializations,
            'failed_materializations': self.failed_materializations,
            'success_rate': (self.successful_materializations / max(1, self.successful_materializations + self.failed_materializations)),
            'uptime': str(datetime.now() - self.start_time),
            'channels_summary': [
                {
                    'intention_id': channel.intention.essence.soul_id,
                    'intention_name': channel.intention.essence.name,
                    'state': channel.intention.state.value,
                    'subscribers': len(channel.subscribers),
                    'messages': len(channel.message_history)
                }
                for channel in self.communication_channels.values()
            ]
        }
    
    def stop(self):
        """Zatrzymuje przepływ intencji"""
        self._running = False
        
        # Poczekaj na zakończenie kolejki materializacji
        if not self.materialization_queue.empty():
            self.materialization_queue.join()
        
        self.engine.logger.info("🎯 IntentionFlow zatrzymany")
