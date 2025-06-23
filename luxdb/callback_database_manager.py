
"""
Manager bazy danych dla systemu callbacków astralnych
Zarządza persystencją zadań, wykonań i wyników callbacków
"""

import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from .models.callback_models import CallbackTask, CallbackExecution, CallbackEvent, CallbackQueue, CallbackStats
from .manager import DatabaseManager
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class CallbackDatabaseManager:
    """Manager bazy danych dla callbacków astralnych"""
    
    def __init__(self, db_manager: DatabaseManager, db_name: str = "callbacks"):
        self.db_manager = db_manager
        self.db_name = db_name
        self.stats_lock = threading.RLock()
        
        # Upewnij się, że baza istnieje
        self._ensure_database()
        
    def _ensure_database(self):
        """Zapewnia istnienie bazy danych callbacków"""
        try:
            # Sprawdź czy baza istnieje w managerze
            if self.db_name not in self.db_manager.list_databases():
                logger.log_info(f"Tworzę bazę danych callbacków: {self.db_name}")
                print(self.db_manager)
                # Dodaj konfigurację bazy
                from .config import DatabaseConfig, DatabaseType
                config = DatabaseConfig(
                    name=self.db_name,
                    type=DatabaseType.SQLITE,
                    max_connections=15,
                    backup_enabled=True,
                    auto_optimize=True,
                    connection_string=f"sqlite:///db/luxdb_{self.db_name}.db"
                )
                
                self.db_manager.add_database(config)
                self.db_manager.create_tables(self.db_name)
                
        except Exception as e:
            logger.log_error("ensure_callback_database", e)
            
    def register_callback(self, registration_id: str, event_name: str, 
                         callback_function: str, priority: int = 2, 
                         is_async: bool = False, once: bool = False,
                         filters: Dict[str, Any] = None, namespace: str = None) -> str:
        """Rejestruje nowy callback w bazie danych"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                task = CallbackTask(
                    registration_id=registration_id,
                    event_name=event_name,
                    namespace=namespace,
                    callback_function=callback_function,
                    priority=priority,
                    is_async=is_async,
                    once=once,
                    filters=filters or {}
                )
                
                session.add(task)
                session.commit()
                
                logger.log_info(f"Zarejestrowano callback task: {task.id}")
                return task.id
                
        except Exception as e:
            logger.log_error("register_callback", e)
            return None
    
    def create_event(self, event_name: str, source: str, data: Any = None,
                    session_id: str = None, user_id: str = None,
                    namespace: str = None, **metadata) -> str:
        """Tworzy nowy event w bazie danych"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                event = CallbackEvent(
                    event_name=event_name,
                    source=source,
                    namespace=namespace,
                    event_data=data if isinstance(data, dict) else {"value": data},
                    metadata=metadata,
                    session_id=session_id,
                    user_id=user_id
                )
                
                session.add(event)
                session.commit()
                
                logger.log_info(f"Utworzono callback event: {event.id}")
                return event.id
                
        except Exception as e:
            logger.log_error("create_event", e)
            return None
    
    def start_execution(self, task_id: str, event_id: str, 
                       context_data: Dict[str, Any] = None) -> str:
        """Rozpoczyna wykonanie callback"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                execution = CallbackExecution(
                    task_id=task_id,
                    event_id=event_id,
                    status="running",
                    context_data=context_data or {}
                )
                
                session.add(execution)
                
                # Aktualizuj task
                task = session.query(CallbackTask).filter_by(id=task_id).first()
                if task:
                    task.execution_count += 1
                    task.last_executed = datetime.now()
                
                session.commit()
                
                logger.log_info(f"Rozpoczęto wykonanie callback: {execution.id}")
                return execution.id
                
        except Exception as e:
            logger.log_error("start_execution", e)
            return None
    
    def complete_execution(self, execution_id: str, result: Any = None, 
                          error: str = None, traceback: str = None):
        """Kończy wykonanie callback z wynikiem lub błędem"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                execution = session.query(CallbackExecution).filter_by(id=execution_id).first()
                
                if execution:
                    execution.completed_at = datetime.now()
                    
                    if execution.started_at:
                        delta = execution.completed_at - execution.started_at
                        execution.execution_time_ms = int(delta.total_seconds() * 1000)
                    
                    if error:
                        execution.status = "failed"
                        execution.error_message = error
                        execution.error_traceback = traceback
                    else:
                        execution.status = "completed"
                        execution.result_data = result if isinstance(result, dict) else {"value": result}
                    
                    # Aktualizuj statystyki eventu
                    event = session.query(CallbackEvent).filter_by(id=execution.event_id).first()
                    if event:
                        if error:
                            event.callbacks_failed += 1
                        else:
                            event.callbacks_completed += 1
                    
                    session.commit()
                    
                    logger.log_info(f"Zakończono wykonanie callback: {execution_id} - {execution.status}")
                    
        except Exception as e:
            logger.log_error("complete_execution", e)
    
    def get_pending_tasks(self, event_name: str = None, namespace: str = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera zadania oczekujące na wykonanie"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                query = session.query(CallbackTask).filter_by(active=True)
                
                if event_name:
                    query = query.filter_by(event_name=event_name)
                if namespace:
                    query = query.filter_by(namespace=namespace)
                
                # Sortuj według priorytetu
                tasks = query.order_by(CallbackTask.priority).limit(limit).all()
                
                return [
                    {
                        "id": task.id,
                        "registration_id": task.registration_id,
                        "event_name": task.event_name,
                        "namespace": task.namespace,
                        "callback_function": task.callback_function,
                        "priority": task.priority,
                        "is_async": task.is_async,
                        "once": task.once,
                        "filters": task.filters,
                        "execution_count": task.execution_count
                    }
                    for task in tasks
                ]
                
        except Exception as e:
            logger.log_error("get_pending_tasks", e)
            return []
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera status wykonania callback"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                execution = session.query(CallbackExecution).filter_by(id=execution_id).first()
                
                if execution:
                    return {
                        "id": execution.id,
                        "task_id": execution.task_id,
                        "event_id": execution.event_id,
                        "status": execution.status,
                        "started_at": execution.started_at.isoformat() if execution.started_at else None,
                        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                        "execution_time_ms": execution.execution_time_ms,
                        "result_data": execution.result_data,
                        "error_message": execution.error_message
                    }
                    
        except Exception as e:
            logger.log_error("get_execution_status", e)
            return None
    
    def get_event_executions(self, event_id: str) -> List[Dict[str, Any]]:
        """Pobiera wszystkie wykonania dla danego eventu"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                executions = session.query(CallbackExecution).filter_by(event_id=event_id).all()
                
                return [
                    {
                        "id": exe.id,
                        "task_id": exe.task_id,
                        "status": exe.status,
                        "started_at": exe.started_at.isoformat() if exe.started_at else None,
                        "completed_at": exe.completed_at.isoformat() if exe.completed_at else None,
                        "execution_time_ms": exe.execution_time_ms,
                        "result_data": exe.result_data,
                        "error_message": exe.error_message
                    }
                    for exe in executions
                ]
                
        except Exception as e:
            logger.log_error("get_event_executions", e)
            return []
    
    def cleanup_old_data(self, days_old: int = 30):
        """Czyści stare dane callbacków"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.db_manager.get_session(self.db_name) as session:
                # Usuń stare eventy i powiązane executions
                old_events = session.query(CallbackEvent).filter(
                    CallbackEvent.timestamp < cutoff_date
                ).all()
                
                count = 0
                for event in old_events:
                    # Usuń executions
                    session.query(CallbackExecution).filter_by(event_id=event.id).delete()
                    # Usuń event
                    session.delete(event)
                    count += 1
                
                session.commit()
                logger.log_info(f"Wyczyszczono {count} starych eventów callbacków")
                
        except Exception as e:
            logger.log_error("cleanup_old_data", e)
    
    def generate_stats(self, period_hours: int = 24) -> Dict[str, Any]:
        """Generuje statystyki callbacków"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            with self.db_manager.get_session(self.db_name) as session:
                # Podstawowe statystyki
                total_events = session.query(CallbackEvent).filter(
                    CallbackEvent.timestamp >= start_time
                ).count()
                
                total_executions = session.query(CallbackExecution).filter(
                    CallbackExecution.started_at >= start_time
                ).count()
                
                successful_executions = session.query(CallbackExecution).filter(
                    and_(
                        CallbackExecution.started_at >= start_time,
                        CallbackExecution.status == "completed"
                    )
                ).count()
                
                failed_executions = session.query(CallbackExecution).filter(
                    and_(
                        CallbackExecution.started_at >= start_time,
                        CallbackExecution.status == "failed"
                    )
                ).count()
                
                # Średni czas wykonania
                avg_time = session.query(func.avg(CallbackExecution.execution_time_ms)).filter(
                    and_(
                        CallbackExecution.started_at >= start_time,
                        CallbackExecution.execution_time_ms.isnot(None)
                    )
                ).scalar() or 0
                
                return {
                    "period_start": start_time.isoformat(),
                    "period_end": end_time.isoformat(),
                    "total_events": total_events,
                    "total_executions": total_executions,
                    "successful_executions": successful_executions,
                    "failed_executions": failed_executions,
                    "success_rate": (successful_executions / total_executions * 100) if total_executions > 0 else 0,
                    "avg_execution_time_ms": round(avg_time, 2),
                    "active_tasks": session.query(CallbackTask).filter_by(active=True).count()
                }
                
        except Exception as e:
            logger.log_error("generate_stats", e)
            return {}
    
    def deactivate_task(self, task_id: str):
        """Dezaktywuje zadanie callback"""
        try:
            with self.db_manager.get_session(self.db_name) as session:
                task = session.query(CallbackTask).filter_by(id=task_id).first()
                if task:
                    task.active = False
                    session.commit()
                    logger.log_info(f"Dezaktywowano task: {task_id}")
                    
        except Exception as e:
            logger.log_error("deactivate_task", e)
