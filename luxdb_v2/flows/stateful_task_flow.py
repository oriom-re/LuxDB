
"""
🎯 StatefulTaskFlow - Przepływ Zadań z Kontrolą Stanu

Zarządza zadaniami opartymi na intencjach z pełną kontrolą stanu,
chunkami danych i real-time komunikacją przez WebSocket
"""

import uuid
import json
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from ..beings.intention_being import IntentionBeing, IntentionState


class TaskState(Enum):
    """Stany zadania"""
    RECEIVED = "received"           # Żądanie odebrane
    WORKING = "working"            # W trakcie przetwarzania
    CHUNKING = "chunking"          # Wysyłanie chunków
    COMPLETED = "completed"        # Zakończone
    CONFIRMED = "confirmed"        # Potwierdzone przez klienta
    ARCHIVED = "archived"          # Zarchiwizowane
    FAILED = "failed"              # Błąd


@dataclass
class DataChunk:
    """Chunk danych"""
    chunk_id: str
    sequence: int
    data: Any
    checksum: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'chunk_id': self.chunk_id,
            'sequence': self.sequence,
            'data': self.data,
            'checksum': self.checksum,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class StatefulTask:
    """Zadanie z kontrolą stanu"""
    task_id: str
    client_uid: str
    intention: IntentionBeing
    state: TaskState
    chunks: List[DataChunk] = field(default_factory=list)
    subscribers: Set[str] = field(default_factory=set)
    confirmed_chunks: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_chunk(self, data: Any) -> DataChunk:
        """Dodaje nowy chunk danych"""
        chunk = DataChunk(
            chunk_id=f"chunk_{len(self.chunks):04d}_{uuid.uuid4().hex[:8]}",
            sequence=len(self.chunks),
            data=data,
            checksum=self._calculate_checksum(data)
        )
        self.chunks.append(chunk)
        self.updated_at = datetime.now()
        return chunk
    
    def _calculate_checksum(self, data: Any) -> str:
        """Oblicza checksum dla danych"""
        import hashlib
        data_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def confirm_chunk(self, chunk_id: str) -> bool:
        """Potwierdza odbiór chunka"""
        if chunk_id in [c.chunk_id for c in self.chunks]:
            self.confirmed_chunks.add(chunk_id)
            return True
        return False
    
    def is_fully_confirmed(self) -> bool:
        """Sprawdza czy wszystkie chunki są potwierdzone"""
        all_chunk_ids = {c.chunk_id for c in self.chunks}
        return all_chunk_ids.issubset(self.confirmed_chunks)
    
    def get_missing_chunks(self) -> List[str]:
        """Zwraca listę niepotwierdzone chunków"""
        all_chunk_ids = {c.chunk_id for c in self.chunks}
        return list(all_chunk_ids - self.confirmed_chunks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje zadanie do słownika"""
        return {
            'task_id': self.task_id,
            'client_uid': self.client_uid,
            'state': self.state.value,
            'intention_id': self.intention.essence.soul_id,
            'intention_name': self.intention.essence.name,
            'chunks_count': len(self.chunks),
            'confirmed_chunks_count': len(self.confirmed_chunks),
            'fully_confirmed': self.is_fully_confirmed(),
            'missing_chunks': self.get_missing_chunks(),
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class StatefulTaskFlow:
    """
    Przepływ zadań z kontrolą stanu
    Zarządza intencjami jako zadaniami z real-time komunikacją
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.tasks: Dict[str, StatefulTask] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}
        
        self._running = False
        self.start_time = datetime.now()
        
        # Statystyki
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
    
    def start(self) -> bool:
        """Uruchamia przepływ zadań"""
        if self._running:
            return True
        
        self._running = True
        self.engine.logger.info("🎯 StatefulTaskFlow uruchomiony")
        return True
    
    def stop(self):
        """Zatrzymuje przepływ zadań"""
        self._running = False
        self.engine.logger.info("🎯 StatefulTaskFlow zatrzymany")
    
    async def create_task_from_request(self, client_uid: str, request_data: Dict[str, Any]) -> StatefulTask:
        """
        Tworzy nowe zadanie z żądania klienta
        
        Args:
            client_uid: UID klienta
            request_data: Dane żądania
            
        Returns:
            Nowe zadanie
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        # Tworzenie intencji dla zadania
        intention_data = {
            'nazwa': f"Task_{task_id}",
            'duchowa': {
                'opis_intencji': request_data.get('description', 'Zadanie utworzone z żądania klienta'),
                'kontekst': f'Żądanie klienta {client_uid}',
                'emocje': ['determinacja', 'focus'],
                'energia_duchowa': 100.0
            },
            'materialna': {
                'zadanie': request_data.get('task', 'Przetwarzanie żądania'),
                'wymagania': request_data.get('requirements', []),
                'oczekiwany_rezultat': request_data.get('expected_result', 'Pomyślne zakończenie'),
                'techniczne_detale': request_data.get('technical_details', {}),
                'resources_needed': request_data.get('resources', [])
            },
            'metainfo': {
                'zrodlo': 'stateful_task_flow',
                'tags': ['task', 'stateful', client_uid],
                'opiekun': client_uid
            }
        }
        
        # Utwórz intencję w wymiarze intentions
        intention_realm = self.engine.get_realm('intentions')
        intention = intention_realm.manifestation.manifest(intention_data)
        
        # Stwórz zadanie
        task = StatefulTask(
            task_id=task_id,
            client_uid=client_uid,
            intention=intention,
            state=TaskState.RECEIVED,
            metadata={
                'original_request': request_data,
                'client_info': {
                    'uid': client_uid,
                    'connected_at': datetime.now().isoformat()
                }
            }
        )
        
        self.tasks[task_id] = task
        self.total_tasks += 1
        
        # Dodaj klienta do subskrypcji
        if client_uid not in self.client_subscriptions:
            self.client_subscriptions[client_uid] = set()
        self.client_subscriptions[client_uid].add(task_id)
        task.subscribers.add(client_uid)
        
        self.engine.logger.info(f"🎯 Nowe zadanie utworzone: {task_id} dla klienta {client_uid}")
        
        # Wyślij potwierdzenie
        await self._broadcast_task_update(task, 'task_created', {
            'message': 'Zadanie utworzone i przypisane do intencji',
            'task_info': task.to_dict()
        })
        
        return task
    
    async def start_task_processing(self, task_id: str) -> bool:
        """
        Rozpoczyna przetwarzanie zadania
        
        Args:
            task_id: ID zadania
            
        Returns:
            True jeśli rozpoczęto pomyślnie
        """
        task = self.tasks.get(task_id)
        if not task or task.state != TaskState.RECEIVED:
            return False
        
        # Zmień stan na WORKING
        task.state = TaskState.WORKING
        task.updated_at = datetime.now()
        
        # Aktualizuj intencję
        task.intention.add_interaction('realizuj', {
            'started_by': 'stateful_task_flow',
            'processing_mode': 'chunked_streaming'
        }, 'system')
        
        # Powiadom klientów
        await self._broadcast_task_update(task, 'task_started', {
            'message': 'Przetwarzanie zadania rozpoczęte',
            'processing_info': {
                'mode': 'chunked_streaming',
                'estimated_chunks': 'unknown'
            }
        })
        
        self.engine.logger.info(f"🎯 Rozpoczęto przetwarzanie zadania: {task_id}")
        return True
    
    async def add_task_chunk(self, task_id: str, chunk_data: Any, chunk_metadata: Dict[str, Any] = None) -> Optional[DataChunk]:
        """
        Dodaje chunk danych do zadania
        
        Args:
            task_id: ID zadania
            chunk_data: Dane chunka
            chunk_metadata: Metadane chunka
            
        Returns:
            Dodany chunk lub None
        """
        task = self.tasks.get(task_id)
        if not task or task.state not in [TaskState.WORKING, TaskState.CHUNKING]:
            return None
        
        # Zmień stan na CHUNKING jeśli to pierwszy chunk
        if task.state == TaskState.WORKING:
            task.state = TaskState.CHUNKING
            task.updated_at = datetime.now()
        
        # Dodaj chunk
        chunk = task.add_chunk(chunk_data)
        
        # Powiadom klientów o nowym chunku
        await self._broadcast_task_update(task, 'chunk_available', {
            'chunk': chunk.to_dict(),
            'metadata': chunk_metadata or {},
            'task_progress': {
                'total_chunks': len(task.chunks),
                'confirmed_chunks': len(task.confirmed_chunks),
                'missing_chunks': task.get_missing_chunks()
            }
        })
        
        self.engine.logger.info(f"🎯 Dodano chunk {chunk.chunk_id} do zadania {task_id}")
        return chunk
    
    async def confirm_chunk_receipt(self, task_id: str, chunk_id: str, client_uid: str) -> bool:
        """
        Potwierdza odbiór chunka przez klienta
        
        Args:
            task_id: ID zadania
            chunk_id: ID chunka
            client_uid: UID klienta
            
        Returns:
            True jeśli potwierdzono pomyślnie
        """
        task = self.tasks.get(task_id)
        if not task or client_uid not in task.subscribers:
            return False
        
        # Potwierdź chunk
        confirmed = task.confirm_chunk(chunk_id)
        if not confirmed:
            return False
        
        task.updated_at = datetime.now()
        
        # Powiadom o potwierdzeniu
        await self._broadcast_task_update(task, 'chunk_confirmed', {
            'chunk_id': chunk_id,
            'confirmed_by': client_uid,
            'task_progress': {
                'total_chunks': len(task.chunks),
                'confirmed_chunks': len(task.confirmed_chunks),
                'missing_chunks': task.get_missing_chunks(),
                'fully_confirmed': task.is_fully_confirmed()
            }
        })
        
        self.engine.logger.info(f"🎯 Chunk {chunk_id} potwierdzony przez {client_uid}")
        
        # Sprawdź czy wszystkie chunki potwierdzone i zadanie można zakończyć
        if task.state == TaskState.CHUNKING and task.is_fully_confirmed():
            await self._auto_complete_task(task)
        
        return True
    
    async def complete_task(self, task_id: str, completion_data: Dict[str, Any] = None) -> bool:
        """
        Kończy zadanie
        
        Args:
            task_id: ID zadania
            completion_data: Dane zakończenia
            
        Returns:
            True jeśli zakończono pomyślnie
        """
        task = self.tasks.get(task_id)
        if not task or task.state not in [TaskState.WORKING, TaskState.CHUNKING]:
            return False
        
        # Zmień stan na COMPLETED
        task.state = TaskState.COMPLETED
        task.updated_at = datetime.now()
        
        # Zakończ intencję
        task.intention.complete_intention(completion_data or {
            'success_score': 1.0,
            'completion_type': 'automatic',
            'total_chunks': len(task.chunks)
        })
        
        # Powiadom o zakończeniu
        await self._broadcast_task_update(task, 'task_completed', {
            'message': 'Zadanie zakończone',
            'completion_data': completion_data or {},
            'final_stats': {
                'total_chunks': len(task.chunks),
                'confirmed_chunks': len(task.confirmed_chunks),
                'processing_time': (task.updated_at - task.created_at).total_seconds()
            }
        })
        
        self.completed_tasks += 1
        self.engine.logger.info(f"🎯 Zadanie zakończone: {task_id}")
        return True
    
    async def _auto_complete_task(self, task: StatefulTask):
        """Automatycznie kończy zadanie gdy wszystkie chunki potwierdzone"""
        await self.complete_task(task.task_id, {
            'success_score': 1.0,
            'completion_type': 'auto_complete_on_full_confirmation',
            'auto_completed': True
        })
    
    async def archive_task(self, task_id: str, client_uid: str) -> bool:
        """
        Archiwizuje zadanie po potwierdzeniu przez klienta
        
        Args:
            task_id: ID zadania
            client_uid: UID klienta
            
        Returns:
            True jeśli zarchiwizowano pomyślnie
        """
        task = self.tasks.get(task_id)
        if not task or task.state != TaskState.COMPLETED or client_uid not in task.subscribers:
            return False
        
        # Zmień stan na ARCHIVED
        task.state = TaskState.ARCHIVED
        task.updated_at = datetime.now()
        
        # Powiadom o archiwizacji
        await self._broadcast_task_update(task, 'task_archived', {
            'message': 'Zadanie zarchiwizowane',
            'archived_by': client_uid,
            'archive_time': task.updated_at.isoformat()
        })
        
        # Usuń z aktywnych zadań (opcjonalne - może zostać w pamięci)
        # del self.tasks[task_id]
        
        # Usuń subskrypcje
        if client_uid in self.client_subscriptions:
            self.client_subscriptions[client_uid].discard(task_id)
        
        self.engine.logger.info(f"🎯 Zadanie zarchiwizowane: {task_id}")
        return True
    
    async def get_missing_chunks(self, task_id: str, client_uid: str) -> Optional[List[DataChunk]]:
        """
        Zwraca brakujące chunki dla klienta
        
        Args:
            task_id: ID zadania
            client_uid: UID klienta
            
        Returns:
            Lista brakujących chunków
        """
        task = self.tasks.get(task_id)
        if not task or client_uid not in task.subscribers:
            return None
        
        missing_chunk_ids = task.get_missing_chunks()
        missing_chunks = [c for c in task.chunks if c.chunk_id in missing_chunk_ids]
        
        return missing_chunks
    
    async def _broadcast_task_update(self, task: StatefulTask, update_type: str, update_data: Dict[str, Any]):
        """
        Broadcastuje aktualizację zadania do subskrybentów
        
        Args:
            task: Zadanie
            update_type: Typ aktualizacji
            update_data: Dane aktualizacji
        """
        message = {
            'type': 'task_update',
            'update_type': update_type,
            'task_id': task.task_id,
            'task_state': task.state.value,
            'data': update_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Wyślij przez WebSocket jeśli dostępny
        if hasattr(self.engine, 'ws_flow') and self.engine.ws_flow:
            for subscriber in task.subscribers:
                await self._send_to_client(subscriber, message)
        
        # Wyślij również przez LuxBus
        if hasattr(self.engine, 'luxbus_core') and self.engine.luxbus_core:
            from ..core.luxbus_core import LuxPacket, PacketType
            
            packet = LuxPacket(
                uid=f"task_update_{uuid.uuid4().hex[:8]}",
                from_id="stateful_task_flow",
                to_id="broadcast",
                packet_type=PacketType.EVENT,
                data={
                    'event_type': 'task_update',
                    'subscribers': list(task.subscribers),
                    'message': message
                }
            )
            
            self.engine.luxbus_core.send_packet(packet)
    
    async def _send_to_client(self, client_uid: str, message: Dict[str, Any]):
        """Wysyła wiadomość do konkretnego klienta przez WebSocket"""
        if hasattr(self.engine, 'ws_flow') and self.engine.ws_flow:
            # Znajdź WebSocket klienta i wyślij
            for websocket in self.engine.ws_flow.clients:
                if hasattr(websocket, 'client_uid') and websocket.client_uid == client_uid:
                    try:
                        await websocket.send(json.dumps(message, ensure_ascii=False))
                    except Exception as e:
                        self.engine.logger.error(f"Błąd wysyłania do klienta {client_uid}: {e}")
    
    def get_task(self, task_id: str) -> Optional[StatefulTask]:
        """Pobiera zadanie po ID"""
        return self.tasks.get(task_id)
    
    def get_client_tasks(self, client_uid: str) -> List[StatefulTask]:
        """Pobiera wszystkie zadania klienta"""
        if client_uid not in self.client_subscriptions:
            return []
        
        task_ids = self.client_subscriptions[client_uid]
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu"""
        active_tasks = sum(1 for t in self.tasks.values() if t.state not in [TaskState.ARCHIVED])
        
        return {
            'type': 'stateful_task_flow',
            'running': self._running,
            'total_tasks': self.total_tasks,
            'active_tasks': active_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'success_rate': self.completed_tasks / max(1, self.total_tasks),
            'uptime': str(datetime.now() - self.start_time),
            'clients_count': len(self.client_subscriptions),
            'task_states': {
                state.value: sum(1 for t in self.tasks.values() if t.state == state)
                for state in TaskState
            }
        }
