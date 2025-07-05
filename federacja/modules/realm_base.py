
"""
🌍 BaseRealmModule - Bazowy Moduł Wymiaru w Federacji

Abstrakcyjna klasa bazowa dla wszystkich modułów realms z niezależną kolejką zadań
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

from ..core.bus import FederationBus, FederationMessage
from ..core.lux_module import LuxModule, ModuleType, ModuleVersion


class TaskType(Enum):
    MANIFEST = "manifest"
    CONTEMPLATE = "contemplate"
    TRANSCEND = "transcend"
    EVOLVE = "evolve"
    GET_STATUS = "get_status"
    COUNT_BEINGS = "count_beings"
    HEALTH_CHECK = "health_check"
    SHUTDOWN = "shutdown"


@dataclass
class RealmTask:
    """Zadanie w kolejce realm"""
    task_id: str
    task_type: TaskType
    data: Dict[str, Any]
    future: asyncio.Future
    created_at: datetime
    priority: int = 0  # 0 = normal, 1 = high, -1 = low


class RealmTaskManager:
    """Zarządca zadań dla realm - obsługuje kolejkę i wykonywanie"""
    
    def __init__(self, realm_name: str, executor_func: Callable):
        self.realm_name = realm_name
        self.executor_func = executor_func
        self.task_queue = asyncio.Queue()
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'queue_size': 0,
            'avg_execution_time': 0.0
        }
    
    async def start(self):
        """Uruchamia zarządcę zadań"""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self._worker_loop())
        print(f"🔄 TaskManager dla {self.realm_name} uruchomiony")
    
    async def stop(self):
        """Zatrzymuje zarządcę zadań"""
        self.running = False
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        
        print(f"🛑 TaskManager dla {self.realm_name} zatrzymany")
    
    async def submit_task(self, task: RealmTask) -> Any:
        """Dodaje zadanie do kolejki i czeka na wynik"""
        if not self.running:
            raise RuntimeError(f"TaskManager dla {self.realm_name} nie jest uruchomiony")
        
        await self.task_queue.put(task)
        self.stats['total_tasks'] += 1
        self.stats['queue_size'] = self.task_queue.qsize()
        
        # Czekaj na wykonanie zadania
        return await task.future
    
    async def _worker_loop(self):
        """Główna pętla wykonywania zadań"""
        print(f"🔄 Worker loop dla {self.realm_name} rozpoczęty")
        
        while self.running:
            try:
                # Pobierz zadanie z kolejki (timeout 1 sekunda)
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Wykonaj zadanie
                start_time = datetime.now()
                
                try:
                    result = await self._execute_task(task)
                    task.future.set_result(result)
                    self.stats['completed_tasks'] += 1
                    
                except Exception as e:
                    task.future.set_exception(e)
                    self.stats['failed_tasks'] += 1
                    print(f"❌ Błąd wykonania zadania {task.task_id}: {e}")
                
                # Aktualizuj statystyki
                execution_time = (datetime.now() - start_time).total_seconds()
                self._update_avg_execution_time(execution_time)
                self.stats['queue_size'] = self.task_queue.qsize()
                
                # Oznacz zadanie jako ukończone
                self.task_queue.task_done()
                
            except Exception as e:
                print(f"❌ Błąd w worker loop {self.realm_name}: {e}")
                await asyncio.sleep(1)
        
        print(f"🔄 Worker loop dla {self.realm_name} zakończony")
    
    async def _execute_task(self, task: RealmTask) -> Any:
        """Wykonuje pojedyncze zadanie"""
        return await self.executor_func(task.task_type, task.data)
    
    def _update_avg_execution_time(self, new_time: float):
        """Aktualizuje średni czas wykonania"""
        total = self.stats['completed_tasks'] + self.stats['failed_tasks']
        if total > 0:
            current_avg = self.stats['avg_execution_time']
            self.stats['avg_execution_time'] = ((current_avg * (total - 1)) + new_time) / total
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki zarządcy"""
        return self.stats.copy()


class BaseRealmModule(LuxModule, ABC):
    """
    Bazowy moduł wymiaru z niezależną kolejką zadań
    """
    
    def __init__(self, name: str, config: Dict[str, Any], bus: FederationBus):
        super().__init__(
            name=f"realm_{name}",
            module_type=ModuleType.REALM,
            version=ModuleVersion(1, 0, 0),
            config=config,
            bus=bus,
            creator_id="federation_system"
        )
        
        self.realm_name = name
        self.module_id = f"realm_{name}"
        self.is_connected = False
        self._being_count = 0
        
        # Inicjalizuj zarządcę zadań
        self.task_manager = RealmTaskManager(
            realm_name=self.realm_name,
            executor_func=self._execute_realm_operation
        )
        
        # Rejestracja w bus'ie
        self.bus.register_module(self.module_id, self)
    
    async def initialize(self) -> bool:
        """Inicjalizuje moduł realm"""
        try:
            # Uruchom zarządcę zadań
            await self.task_manager.start()
            
            # Nawiąż połączenie
            success = await self.connect()
            if success:
                self.is_active = True
                await self._register_commands()
                print(f"🌍 Realm '{self.name}' zainicjalizowany z własną kolejką")
            return success
        except Exception as e:
            print(f"❌ Błąd inicjalizacji realm '{self.name}': {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Wyłącza moduł realm"""
        try:
            # Zatrzymaj zarządcę zadań
            await self.task_manager.stop()
            
            # Rozłącz
            await self.disconnect()
            self.is_active = False
            print(f"🕊️ Realm '{self.name}' wyłączony")
            return True
        except Exception as e:
            print(f"❌ Błąd wyłączania realm '{self.name}': {e}")
            return False
    
    async def _register_commands(self):
        """Rejestruje komendy w bus'ie"""
        commands = {
            'manifest': self._queue_manifest,
            'contemplate': self._queue_contemplate,
            'transcend': self._queue_transcend,
            'evolve': self._queue_evolve,
            'get_status': self._queue_get_status,
            'count_beings': self._queue_count_beings,
            'health_check': self._queue_health_check
        }
        
        for cmd_name, cmd_func in commands.items():
            await self.bus.register_command(f"{self.module_id}.{cmd_name}", cmd_func)
    
    async def handle_message(self, message: FederationMessage) -> Any:
        """Obsługuje wiadomości z bus'a - przekierowuje do kolejki"""
        command = message.message_type
        data = message.data
        
        if command == 'manifest':
            return await self._queue_manifest(data)
        elif command == 'contemplate':
            return await self._queue_contemplate(data.get('intention', ''), **data.get('conditions', {}))
        elif command == 'transcend':
            return await self._queue_transcend(data.get('being_id'))
        elif command == 'evolve':
            return await self._queue_evolve(data.get('being_id'), data.get('new_data', {}))
        elif command == 'get_status':
            return await self._queue_get_status()
        elif command == 'count_beings':
            return await self._queue_count_beings()
        elif command == 'health_check':
            return await self._queue_health_check()
        else:
            return {'error': f'Nieznana komenda: {command}'}
    
    # ===== METODY KOLEJKOWANIA =====
    
    async def _queue_manifest(self, being_data: Dict[str, Any]) -> Any:
        """Kolejkuje zadanie manifestacji"""
        return await self._submit_task(TaskType.MANIFEST, {'being_data': being_data})
    
    async def _queue_contemplate(self, intention: str, **conditions) -> List[Any]:
        """Kolejkuje zadanie kontemplacji"""
        return await self._submit_task(TaskType.CONTEMPLATE, {
            'intention': intention,
            'conditions': conditions
        })
    
    async def _queue_transcend(self, being_id: Any) -> bool:
        """Kolejkuje zadanie transcendencji"""
        return await self._submit_task(TaskType.TRANSCEND, {'being_id': being_id})
    
    async def _queue_evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """Kolejkuje zadanie ewolucji"""
        return await self._submit_task(TaskType.EVOLVE, {
            'being_id': being_id,
            'new_data': new_data
        })
    
    async def _queue_get_status(self) -> Dict[str, Any]:
        """Kolejkuje zadanie statusu"""
        return await self._submit_task(TaskType.GET_STATUS, {})
    
    async def _queue_count_beings(self) -> int:
        """Kolejkuje zadanie liczenia bytów"""
        return await self._submit_task(TaskType.COUNT_BEINGS, {})
    
    async def _queue_health_check(self) -> Dict[str, Any]:
        """Kolejkuje zadanie sprawdzenia zdrowia"""
        return await self._submit_task(TaskType.HEALTH_CHECK, {})
    
    async def _submit_task(self, task_type: TaskType, data: Dict[str, Any]) -> Any:
        """Dodaje zadanie do kolejki"""
        task_id = f"{self.realm_name}_{task_type.value}_{datetime.now().timestamp()}"
        future = asyncio.Future()
        
        task = RealmTask(
            task_id=task_id,
            task_type=task_type,
            data=data,
            future=future,
            created_at=datetime.now()
        )
        
        return await self.task_manager.submit_task(task)
    
    async def _execute_realm_operation(self, task_type: TaskType, data: Dict[str, Any]) -> Any:
        """Wykonuje operację realm - wywoływana przez TaskManager"""
        if task_type == TaskType.MANIFEST:
            return await self.manifest(data['being_data'])
        elif task_type == TaskType.CONTEMPLATE:
            return await self.contemplate(data['intention'], **data['conditions'])
        elif task_type == TaskType.TRANSCEND:
            return await self.transcend(data['being_id'])
        elif task_type == TaskType.EVOLVE:
            return await self.evolve(data['being_id'], data['new_data'])
        elif task_type == TaskType.GET_STATUS:
            return await self.get_status()
        elif task_type == TaskType.COUNT_BEINGS:
            return await self.count_beings()
        elif task_type == TaskType.HEALTH_CHECK:
            return await self.health_check()
        else:
            raise ValueError(f"Nieznany typ zadania: {task_type}")
    
    # ===== ABSTRAKCYJNE METODY DO IMPLEMENTACJI =====
    
    @abstractmethod
    async def connect(self) -> bool:
        """Nawiązuje połączenie z wymiarem"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Rozłącza z wymiarem"""
        pass
    
    @abstractmethod
    async def manifest(self, being_data: Dict[str, Any]) -> Any:
        """Manifestuje nowy byt w wymiarze"""
        pass
    
    @abstractmethod
    async def contemplate(self, intention: str, **conditions) -> List[Any]:
        """Kontempluje (wyszukuje) byty w wymiarze"""
        pass
    
    @abstractmethod
    async def transcend(self, being_id: Any) -> bool:
        """Transcenduje (usuwa) byt z wymiaru"""
        pass
    
    @abstractmethod
    async def evolve(self, being_id: Any, new_data: Dict[str, Any]) -> Any:
        """Ewoluuje (aktualizuje) byt"""
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """Zwraca status wymiaru"""
        task_stats = self.task_manager.get_stats()
        
        return {
            'module_id': self.module_id,
            'name': self.name,
            'type': self.__class__.__name__,
            'active': self.is_active,
            'connected': self.is_connected,
            'being_count': await self.count_beings(),
            'created_at': self.created_at.isoformat(),
            'task_manager': {
                'running': self.task_manager.running,
                'stats': task_stats
            },
            'config': self._mask_sensitive_config()
        }
    
    async def count_beings(self) -> int:
        """Zwraca liczbę bytów w wymiarze"""
        return self._being_count
    
    async def health_check(self) -> Dict[str, Any]:
        """Sprawdza zdrowie wymiaru"""
        task_stats = self.task_manager.get_stats()
        
        return {
            'healthy': self.is_connected and self.is_active and self.task_manager.running,
            'connected': self.is_connected,
            'active': self.is_active,
            'task_manager_running': self.task_manager.running,
            'queue_size': task_stats['queue_size'],
            'last_check': datetime.now().isoformat()
        }
    
    def _mask_sensitive_config(self) -> Dict[str, Any]:
        """Maskuje wrażliwe dane w konfiguracji"""
        masked_config = self.config.copy()
        sensitive_keys = ['password', 'secret', 'key', 'token']
        
        for key in masked_config:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                masked_config[key] = '***'
        
        return masked_config
