
"""
Manager bazy danych dla systemu callbacków astralnych
Zarządza persystencją zadań, wykonań i statystyk callbacków
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import desc, func, and_, or_
from sqlalchemy.orm import Session

from .models.callback_models import CallbackTask, CallbackExecution, CallbackEvent, CallbackQueue, CallbackStats
from .utils.logging_utils import get_db_logger
from .utils.error_handlers import LuxDBError

logger = get_db_logger()

class CallbackDatabaseManager:
    """Manager bazy danych dla systemu callbacków"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.logger = logger
        
        # Upewnij się, że tabele są utworzone
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Upewnia się, że tabele callbacków istnieją"""
        try:
            # Import modeli żeby SQLAlchemy je znało
            from .models.callback_models import CallbackTask, CallbackExecution, CallbackEvent, CallbackQueue, CallbackStats
            
            # Utwórz tabele jeśli nie istnieją
            self.db_manager.create_all_tables()
            logger.log_info("Tabele callbacków są gotowe")
        except Exception as e:
            logger.log_error("ensure_callback_tables", e)
    
    def register_callback(self, registration_id: str, event_name: str, 
                         callback_function: str, priority: int = 2,
                         is_async: bool = False, once: bool = False,
                         filters: Dict[str, Any] = None, namespace: str = None) -> str:
        """Rejestruje callback w bazie danych"""
        try:
            # sprawdź istniejące bazy
            if not self.db_manager.check_database_exists("main"):
                raise LuxDBError("Baza danych 'main' nie istnieje")
            with self.db_manager.get_session("main") as session:
                task = CallbackTask(
                    registration_id=registration_id,
                    event_name=event_name,
                    callback_function=callback_function,
                    priority=priority,
                    is_async=is_async,
                    once=once,
                    filters=filters,
                    namespace=namespace,
                    active=True
                )
                
                session.add(task)
                session.commit()
                
                logger.log_info(f"Zarejestrowano callback w bazie: {registration_id}")
                return task.id
        except Exception as e:
            logger.log_error("register_callback", e)
            raise LuxDBError(f"Błąd rejestracji callback: {e}")
    
    def create_event(self, event_name: str, source: str, data: Any = None,
                    session_id: str = None, user_id: str = None, 
                    namespace: str = None, **metadata) -> str:
        """Tworzy event w bazie danych"""
        try:
            with self.db_manager.get_session("main") as session:
                event = CallbackEvent(
                    event_name=event_name,
                    source=source,
                    namespace=namespace,
                    event_data=data if isinstance(data, dict) else {"data": data},
                    meta_data=metadata,
                    session_id=session_id,
                    user_id=user_id
                )
                
                session.add(event)
                session.commit()
                
                logger.log_info(f"Utworzono event: {event_name} z {source}")
                return event.id
        except Exception as e:
            logger.log_error("create_event", e)
            raise LuxDBError(f"Błąd tworzenia eventu: {e}")
    
    def start_execution(self, task_id: str, event_id: str, 
                       context_data: Dict[str, Any] = None) -> str:
        """Rozpoczyna śledzenie wykonania callback"""
        try:
            with self.db_manager.get_session("main") as session:
                execution = CallbackExecution(
                    task_id=task_id,
                    event_id=event_id,
                    status="running",
                    context_data=context_data,
                    session_id=context_data.get('session_id') if context_data else None,
                    user_id=context_data.get('user_id') if context_data else None
                )
                
                session.add(execution)
                session.commit()
                
                return execution.id
        except Exception as e:
            logger.log_error("start_execution", e)
            raise LuxDBError(f"Błąd rozpoczęcia wykonania: {e}")
    
    def complete_execution(self, execution_id: str, result: Any = None, error: str = None):
        """Kończy śledzenie wykonania callback"""
        try:
            with self.db_manager.get_session("main") as session:
                execution = session.query(CallbackExecution).filter_by(id=execution_id).first()
                
                if execution:
                    execution.completed_at = datetime.now()
                    execution.execution_time_ms = int(
                        (execution.completed_at - execution.started_at).total_seconds() * 1000
                    )
                    
                    if error:
                        execution.status = "failed"
                        execution.error_message = str(error)
                    else:
                        execution.status = "completed"
                        if result is not None:
                            # Serializuj wynik do JSON
                            try:
                                execution.result_data = {"result": result} if not isinstance(result, dict) else result
                            except:
                                execution.result_data = {"result": str(result)}
                    
                    # Zaktualizuj licznik wykonań w zadaniu
                    task = session.query(CallbackTask).filter_by(id=execution.task_id).first()
                    if task:
                        task.execution_count += 1
                        task.last_executed = execution.completed_at
                        
                        # Jeśli to callback "once", dezaktywuj go
                        if task.once:
                            task.active = False
                    
                    session.commit()
        except Exception as e:
            logger.log_error("complete_execution", e)
    
    def get_pending_tasks(self, event_name: str = None, namespace: str = None) -> List[Dict[str, Any]]:
        """Pobiera oczekujące zadania callback"""
        try:
            with self.db_manager.get_session("main") as session:
                query = session.query(CallbackTask).filter_by(active=True)
                
                if event_name:
                    query = query.filter_by(event_name=event_name)
                if namespace:
                    query = query.filter_by(namespace=namespace)
                
                tasks = query.order_by(CallbackTask.priority, CallbackTask.created_at).all()
                
                return [
                    {
                        'id': task.id,
                        'registration_id': task.registration_id,
                        'event_name': task.event_name,
                        'namespace': task.namespace,
                        'callback_function': task.callback_function,
                        'priority': task.priority,
                        'is_async': task.is_async,
                        'once': task.once,
                        'filters': task.filters,
                        'execution_count': task.execution_count,
                        'last_executed': task.last_executed.isoformat() if task.last_executed else None
                    }
                    for task in tasks
                ]
        except Exception as e:
            logger.log_error("get_pending_tasks", e)
            return []
    
    def get_execution_history(self, event_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Pobiera historię wykonań callbacków"""
        try:
            with self.db_manager.get_session("main") as session:
                query = session.query(CallbackExecution)\
                    .join(CallbackTask)\
                    .join(CallbackEvent)
                
                if event_name:
                    query = query.filter(CallbackEvent.event_name == event_name)
                
                executions = query.order_by(desc(CallbackExecution.started_at))\
                    .limit(limit).all()
                
                return [
                    {
                        'id': exec.id,
                        'event_name': exec.event.event_name,
                        'callback_function': exec.task.callback_function,
                        'status': exec.status,
                        'started_at': exec.started_at.isoformat(),
                        'completed_at': exec.completed_at.isoformat() if exec.completed_at else None,
                        'execution_time_ms': exec.execution_time_ms,
                        'result': exec.result_data,
                        'error': exec.error_message,
                        'session_id': exec.session_id,
                        'user_id': exec.user_id
                    }
                    for exec in executions
                ]
        except Exception as e:
            logger.log_error("get_execution_history", e)
            return []
    
    def generate_stats(self) -> Dict[str, Any]:
        """Generuje statystyki callbacków z bazy danych"""
        try:
            with self.db_manager.get_session("main") as session:
                # Podstawowe statystyki
                total_events = session.query(func.count(CallbackEvent.id)).scalar()
                total_executions = session.query(func.count(CallbackExecution.id)).scalar()
                
                successful_executions = session.query(func.count(CallbackExecution.id))\
                    .filter_by(status="completed").scalar()
                
                failed_executions = session.query(func.count(CallbackExecution.id))\
                    .filter_by(status="failed").scalar()
                
                async_executions = session.query(func.count(CallbackExecution.id))\
                    .join(CallbackTask)\
                    .filter(CallbackTask.is_async == True).scalar()
                
                # Średni czas wykonania
                avg_time_result = session.query(func.avg(CallbackExecution.execution_time_ms))\
                    .filter(CallbackExecution.execution_time_ms.isnot(None)).scalar()
                
                avg_execution_time_ms = float(avg_time_result) if avg_time_result else 0.0
                
                # Najpopularniejsze eventy (ostatnie 24h)
                yesterday = datetime.now() - timedelta(days=1)
                top_events_query = session.query(
                    CallbackEvent.event_name,
                    func.count(CallbackEvent.id).label('count')
                ).filter(CallbackEvent.timestamp >= yesterday)\
                 .group_by(CallbackEvent.event_name)\
                 .order_by(desc('count'))\
                 .limit(10).all()
                
                top_events = {name: count for name, count in top_events_query}
                
                # Najpopularniejsze namespace
                top_namespaces_query = session.query(
                    CallbackEvent.namespace,
                    func.count(CallbackEvent.id).label('count')
                ).filter(and_(
                    CallbackEvent.timestamp >= yesterday,
                    CallbackEvent.namespace.isnot(None)
                )).group_by(CallbackEvent.namespace)\
                  .order_by(desc('count'))\
                  .limit(10).all()
                
                top_namespaces = {name: count for name, count in top_namespaces_query}
                
                # Aktywne zadania
                active_tasks = session.query(func.count(CallbackTask.id))\
                    .filter_by(active=True).scalar()
                
                # Wskaźnik sukcesu
                success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
                
                return {
                    'total_events': total_events,
                    'total_executions': total_executions,
                    'successful_executions': successful_executions,
                    'failed_executions': failed_executions,
                    'async_executions': async_executions,
                    'avg_execution_time_ms': avg_execution_time_ms,
                    'success_rate': success_rate,
                    'active_tasks': active_tasks,
                    'top_events': top_events,
                    'top_namespaces': top_namespaces,
                    'generated_at': datetime.now().isoformat()
                }
        except Exception as e:
            logger.log_error("generate_stats", e)
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def cleanup_old_data(self, days_old: int = 30):
        """Czyści stare dane callbacków"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with self.db_manager.get_session("main") as session:
                # Usuń stare wykonania
                old_executions = session.query(CallbackExecution)\
                    .filter(CallbackExecution.started_at < cutoff_date)
                
                execution_count = old_executions.count()
                old_executions.delete()
                
                # Usuń stare eventy (które nie mają więcej wykonań)
                old_events = session.query(CallbackEvent)\
                    .filter(CallbackEvent.timestamp < cutoff_date)\
                    .filter(~CallbackEvent.executions.any())
                
                event_count = old_events.count()
                old_events.delete()
                
                # Usuń nieaktywne zadania bez wykonań
                inactive_tasks = session.query(CallbackTask)\
                    .filter(and_(
                        CallbackTask.active == False,
                        CallbackTask.created_at < cutoff_date,
                        ~CallbackTask.executions.any()
                    ))
                
                task_count = inactive_tasks.count()
                inactive_tasks.delete()
                
                session.commit()
                
                logger.log_info(f"Wyczyszczono: {execution_count} wykonań, "
                              f"{event_count} eventów, {task_count} zadań")
                
                return {
                    'cleaned_executions': execution_count,
                    'cleaned_events': event_count,
                    'cleaned_tasks': task_count
                }
        except Exception as e:
            logger.log_error("cleanup_old_data", e)
            raise LuxDBError(f"Błąd czyszczenia danych: {e}")
    
    def create_stats_snapshot(self, period_type: str = "hour"):
        """Tworzy snapshot statystyk dla konkretnego okresu"""
        try:
            now = datetime.now()
            
            # Określ zakres czasowy
            if period_type == "hour":
                period_start = now.replace(minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(hours=1)
            elif period_type == "day":
                period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = period_start + timedelta(days=1)
            elif period_type == "week":
                days_since_monday = now.weekday()
                period_start = (now - timedelta(days=days_since_monday)).replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                period_end = period_start + timedelta(weeks=1)
            else:  # month
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if now.month == 12:
                    period_end = period_start.replace(year=now.year + 1, month=1)
                else:
                    period_end = period_start.replace(month=now.month + 1)
            
            # Zbierz statystyki dla okresu
            stats = self._calculate_period_stats(period_start, period_end)
            
            with self.db_manager.get_session() as session:
                # Sprawdź czy już istnieje snapshot dla tego okresu
                existing = session.query(CallbackStats).filter(and_(
                    CallbackStats.period_start == period_start,
                    CallbackStats.period_type == period_type
                )).first()
                
                if existing:
                    # Zaktualizuj istniejący
                    for key, value in stats.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Utwórz nowy
                    snapshot = CallbackStats(
                        period_start=period_start,
                        period_end=period_end,
                        period_type=period_type,
                        **stats
                    )
                    session.add(snapshot)
                
                session.commit()
                
        except Exception as e:
            logger.log_error("create_stats_snapshot", e)
    
    def _calculate_period_stats(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Oblicza statystyki dla konkretnego okresu"""
        try:
            with self.db_manager.get_session("main") as session:
                # Filtruj po okresie
                events_in_period = session.query(CallbackEvent)\
                    .filter(and_(
                        CallbackEvent.timestamp >= period_start,
                        CallbackEvent.timestamp < period_end
                    ))
                
                executions_in_period = session.query(CallbackExecution)\
                    .filter(and_(
                        CallbackExecution.started_at >= period_start,
                        CallbackExecution.started_at < period_end
                    ))
                
                total_events = events_in_period.count()
                total_executions = executions_in_period.count()
                
                successful_executions = executions_in_period\
                    .filter_by(status="completed").count()
                
                failed_executions = executions_in_period\
                    .filter_by(status="failed").count()
                
                async_executions = executions_in_period\
                    .join(CallbackTask)\
                    .filter(CallbackTask.is_async == True).count()
                
                # Czasy wykonania
                time_stats = executions_in_period\
                    .filter(CallbackExecution.execution_time_ms.isnot(None))\
                    .with_entities(
                        func.avg(CallbackExecution.execution_time_ms),
                        func.max(CallbackExecution.execution_time_ms),
                        func.min(CallbackExecution.execution_time_ms)
                    ).first()
                
                avg_time = float(time_stats[0]) if time_stats[0] else 0.0
                max_time = int(time_stats[1]) if time_stats[1] else 0
                min_time = int(time_stats[2]) if time_stats[2] else 0
                
                # Top eventy
                top_events_query = events_in_period\
                    .with_entities(
                        CallbackEvent.event_name,
                        func.count(CallbackEvent.id).label('count')
                    ).group_by(CallbackEvent.event_name)\
                     .order_by(desc('count'))\
                     .limit(10).all()
                
                top_events = {name: count for name, count in top_events_query}
                
                # Top namespace
                top_namespaces_query = events_in_period\
                    .filter(CallbackEvent.namespace.isnot(None))\
                    .with_entities(
                        CallbackEvent.namespace,
                        func.count(CallbackEvent.id).label('count')
                    ).group_by(CallbackEvent.namespace)\
                     .order_by(desc('count'))\
                     .limit(10).all()
                
                top_namespaces = {name: count for name, count in top_namespaces_query}
                
                return {
                    'total_events': total_events,
                    'total_executions': total_executions,
                    'successful_executions': successful_executions,
                    'failed_executions': failed_executions,
                    'async_executions': async_executions,
                    'avg_execution_time_ms': avg_time,
                    'max_execution_time_ms': max_time,
                    'min_execution_time_ms': min_time,
                    'top_events': top_events,
                    'top_namespaces': top_namespaces
                }
        except Exception as e:
            logger.log_error("_calculate_period_stats", e)
            return {}
    
    def get_stats_for_period(self, period_type: str = "day", 
                           periods_back: int = 7) -> List[Dict[str, Any]]:
        """Pobiera statystyki dla ostatnich okresów"""
        try:
            with self.db_manager.get_session("main") as session:
                stats = session.query(CallbackStats)\
                    .filter_by(period_type=period_type)\
                    .order_by(desc(CallbackStats.period_start))\
                    .limit(periods_back).all()
                
                return [
                    {
                        'period_start': stat.period_start.isoformat(),
                        'period_end': stat.period_end.isoformat(),
                        'period_type': stat.period_type,
                        'total_events': stat.total_events,
                        'total_executions': stat.total_executions,
                        'successful_executions': stat.successful_executions,
                        'failed_executions': stat.failed_executions,
                        'success_rate': (stat.successful_executions / stat.total_executions * 100) 
                                      if stat.total_executions > 0 else 0,
                        'avg_execution_time_ms': stat.avg_execution_time_ms,
                        'top_events': stat.top_events,
                        'top_namespaces': stat.top_namespaces
                    }
                    for stat in stats
                ]
        except Exception as e:
            logger.log_error("get_stats_for_period", e)
            return []
