
"""
Modele bazy danych dla systemu callbacków astralnych
Przechowuje zadania, wyniki i eventy callbacków
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from luxdb.models.luxbase import LuxBase

class CallbackTask(LuxBase):
    """Zadanie callback - reprezentuje zarejestrowany callback"""
    __tablename__ = 'callback_tasks'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    registration_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    callback_function: Mapped[str] = mapped_column(String(500), nullable=False)  # Nazwa funkcji
    priority: Mapped[int] = mapped_column(Integer, default=2)  # CallbackPriority
    is_async: Mapped[bool] = mapped_column(Boolean, default=False)
    once: Mapped[bool] = mapped_column(Boolean, default=False)
    filters: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Metadane
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    last_executed: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    execution_count: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relacje
    executions: Mapped[List["CallbackExecution"]] = relationship("CallbackExecution", back_populates="task", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)

class CallbackExecution(LuxBase):
    """Wykonanie callback - pojedyncze uruchomienie zadania"""
    __tablename__ = 'callback_executions'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("callback_tasks.id"), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("callback_events.id"), nullable=False, index=True)
    
    # Status wykonania
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed
    started_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    completed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    
    # Wyniki
    result_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    error_traceback: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Kontekst wykonania
    context_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # Relacje
    task: Mapped["CallbackTask"] = relationship("CallbackTask", back_populates="executions")
    event: Mapped["CallbackEvent"] = relationship("CallbackEvent", back_populates="executions")
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)

class CallbackEvent(LuxBase):
    """Event callback - zdarzenie które wywołało callbacki"""
    __tablename__ = 'callback_events'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    event_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    namespace: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    
    # Dane zdarzenia
    event_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    
    # Kontekst
    session_id: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    
    # Statistyki
    callbacks_triggered: Mapped[int] = mapped_column(Integer, default=0)
    callbacks_completed: Mapped[int] = mapped_column(Integer, default=0)
    callbacks_failed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relacje
    executions: Mapped[List["CallbackExecution"]] = relationship("CallbackExecution", back_populates="event", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)

class CallbackQueue(LuxBase):
    """Kolejka callbacków - zarządza kolejnością wykonania"""
    __tablename__ = 'callback_queue'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    execution_id: Mapped[str] = mapped_column(String(36), ForeignKey("callback_executions.id"), nullable=False, index=True)
    
    # Kolejka
    queue_name: Mapped[str] = mapped_column(String(100), default="default")
    priority: Mapped[int] = mapped_column(Integer, default=2)
    scheduled_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="queued")  # queued, processing, completed, failed
    processed_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)

class CallbackStats(LuxBase):
    """Statystyki callbacków - agregowane metryki"""
    __tablename__ = 'callback_stats'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Zakres czasowy
    period_start: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    period_type: Mapped[str] = mapped_column(String(20), default="hour")  # hour, day, week, month
    
    # Metryki callbacków
    total_events: Mapped[int] = mapped_column(Integer, default=0)
    total_executions: Mapped[int] = mapped_column(Integer, default=0)
    successful_executions: Mapped[int] = mapped_column(Integer, default=0)
    failed_executions: Mapped[int] = mapped_column(Integer, default=0)
    async_executions: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metryki wydajności
    avg_execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    max_execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    min_execution_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    
    # Najpopularniejsze
    top_events: Mapped[dict] = mapped_column(JSON, nullable=True)  # {event_name: count}
    top_namespaces: Mapped[dict] = mapped_column(JSON, nullable=True)  # {namespace: count}
    
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
