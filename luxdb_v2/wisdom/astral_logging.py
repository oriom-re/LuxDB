
"""
📝 AstralLogger - Zaawansowany System Logowania Astralnego

Duchowe podejście do logowania z wielopoziomową świadomością i kontekstem
"""

import json
import logging
import sys
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading


class LogLevel(Enum):
    """Poziomy logowania astralnego"""
    TRANSCENDENT = 60  # Najwyższy poziom - transcendentne ereigngse
    ENLIGHTENED = 50   # Oświecone - krytyczne informacje  
    AWARE = 40         # Świadome - ostrzeżenia
    AWAKENING = 30     # Przebudzenie - informacje
    DORMANT = 20       # Uśpione - debug
    VOID = 10          # Pustynia - trace


@dataclass
class LogEntry:
    """Wpis do loga astralnego"""
    timestamp: datetime
    level: LogLevel
    message: str
    context: Dict[str, Any]
    source: str
    realm: Optional[str] = None
    being_id: Optional[str] = None
    energy_level: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.name,
            'message': self.message,
            'context': self.context,
            'source': self.source,
            'realm': self.realm,
            'being_id': self.being_id,
            'energy_level': self.energy_level
        }


class LogFormatter:
    """Formatuje wpisy loga w różnych stylach"""
    
    @staticmethod
    def format_console(entry: LogEntry) -> str:
        """Format dla konsoli z emotikonami"""
        level_icons = {
            LogLevel.TRANSCENDENT: "🌟",
            LogLevel.ENLIGHTENED: "💎", 
            LogLevel.AWARE: "⚠️",
            LogLevel.AWAKENING: "ℹ️",
            LogLevel.DORMANT: "🔍",
            LogLevel.VOID: "👻"
        }
        
        icon = level_icons.get(entry.level, "📝")
        timestamp = entry.timestamp.strftime("%H:%M:%S")
        
        context_str = ""
        if entry.realm:
            context_str += f"[{entry.realm}]"
        if entry.being_id:
            context_str += f"[{entry.being_id[:8]}]"
        
        return f"{icon} {timestamp} {context_str} {entry.message}"
    
    @staticmethod
    def format_json(entry: LogEntry) -> str:
        """Format JSON"""
        return json.dumps(entry.to_dict(), ensure_ascii=False)
    
    @staticmethod
    def format_detailed(entry: LogEntry) -> str:
        """Szczegółowy format"""
        lines = [
            f"🕐 {entry.timestamp.isoformat()}",
            f"📊 Level: {entry.level.name}",
            f"📝 Message: {entry.message}",
            f"🏷️ Source: {entry.source}"
        ]
        
        if entry.realm:
            lines.append(f"🌍 Realm: {entry.realm}")
        
        if entry.being_id:
            lines.append(f"👤 Being: {entry.being_id}")
        
        if entry.energy_level is not None:
            lines.append(f"⚡ Energy: {entry.energy_level}")
        
        if entry.context:
            lines.append(f"🔍 Context: {json.dumps(entry.context, ensure_ascii=False)}")
        
        return "\n".join(lines) + "\n" + "─" * 50


class LogHandler:
    """Bazowa klasa dla handlerów logów"""
    
    def __init__(self, formatter: LogFormatter = None):
        self.formatter = formatter or LogFormatter()
    
    def handle(self, entry: LogEntry):
        """Obsługuje wpis loga"""
        raise NotImplementedError


class ConsoleHandler(LogHandler):
    """Handler dla konsoli"""
    
    def handle(self, entry: LogEntry):
        print(self.formatter.format_console(entry))


class FileHandler(LogHandler):
    """Handler dla plików"""
    
    def __init__(self, filepath: str, formatter: LogFormatter = None, max_size_mb: int = 10):
        super().__init__(formatter)
        self.filepath = Path(filepath)
        self.max_size_mb = max_size_mb
        self._lock = threading.Lock()
        
        # Utwórz katalog jeśli nie istnieje
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
    
    def handle(self, entry: LogEntry):
        with self._lock:
            # Sprawdź rozmiar pliku
            if self.filepath.exists():
                size_mb = self.filepath.stat().st_size / (1024 * 1024)
                if size_mb > self.max_size_mb:
                    self._rotate_file()
            
            # Zapisz wpis
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(self.formatter.format_json(entry) + '\n')
    
    def _rotate_file(self):
        """Rotuje plik loga"""
        if self.filepath.exists():
            backup_path = self.filepath.with_suffix(f'.{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            self.filepath.rename(backup_path)


class MemoryHandler(LogHandler):
    """Handler przechowujący logi w pamięci"""
    
    def __init__(self, max_entries: int = 1000):
        super().__init__()
        self.max_entries = max_entries
        self.entries: List[LogEntry] = []
        self._lock = threading.Lock()
    
    def handle(self, entry: LogEntry):
        with self._lock:
            self.entries.append(entry)
            
            # Ogranicz liczbę wpisów
            if len(self.entries) > self.max_entries:
                self.entries = self.entries[-self.max_entries:]
    
    def get_entries(self, level: Optional[LogLevel] = None, limit: int = 100) -> List[LogEntry]:
        """Zwraca wpisy z pamięci"""
        with self._lock:
            entries = self.entries
            
            if level:
                entries = [e for e in entries if e.level == level]
            
            return entries[-limit:]
    
    def clear(self):
        """Czyści pamięć"""
        with self._lock:
            self.entries.clear()


class AstralLogger:
    """
    Główny logger astralny - zarządza całym systemem logowania
    """
    
    def __init__(self, name: str = "astral", min_level: LogLevel = LogLevel.AWAKENING):
        self.name = name
        self.min_level = min_level
        self.handlers: List[LogHandler] = []
        self.context: Dict[str, Any] = {}
        
        # Domyślne handlery
        self.console_handler = ConsoleHandler()
        self.memory_handler = MemoryHandler()
        
        self.add_handler(self.console_handler)
        self.add_handler(self.memory_handler)
        
        # Statystyki
        self.log_count = 0
        self.start_time = datetime.now()
    
    def add_handler(self, handler: LogHandler):
        """Dodaje handler"""
        self.handlers.append(handler)
    
    def remove_handler(self, handler: LogHandler):
        """Usuwa handler"""
        if handler in self.handlers:
            self.handlers.remove(handler)
    
    def set_context(self, **context):
        """Ustawia globalny kontekst"""
        self.context.update(context)
    
    def clear_context(self):
        """Czyści kontekst"""
        self.context.clear()
    
    def log(self, level: LogLevel, message: str, **context):
        """
        Główna metoda logowania
        
        Args:
            level: Poziom loga
            message: Wiadomość
            **context: Dodatkowy kontekst
        """
        if level.value < self.min_level.value:
            return
        
        # Połącz konteksty
        merged_context = {**self.context, **context}
        
        # Utwórz wpis
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            context=merged_context,
            source=self.name,
            realm=merged_context.get('realm'),
            being_id=merged_context.get('being_id'),
            energy_level=merged_context.get('energy_level')
        )
        
        # Przekaż do handlerów
        for handler in self.handlers:
            try:
                handler.handle(entry)
            except Exception as e:
                # Fallback - wyświetl w konsoli
                print(f"❌ Błąd handlera loga: {e}")
        
        self.log_count += 1
    
    # Metody wygody dla różnych poziomów
    def transcendent(self, message: str, **context):
        """Log transcendentny - najwyższy poziom"""
        self.log(LogLevel.TRANSCENDENT, message, **context)
    
    def enlightened(self, message: str, **context):
        """Log oświecony - krytyczne informacje"""
        self.log(LogLevel.ENLIGHTENED, message, **context)
    
    def aware(self, message: str, **context):
        """Log świadomy - ostrzeżenia"""
        self.log(LogLevel.AWARE, message, **context)
    
    def awakening(self, message: str, **context):
        """Log przebudzenia - informacje"""
        self.log(LogLevel.AWAKENING, message, **context)
    
    def dormant(self, message: str, **context):
        """Log uśpiony - debug"""
        self.log(LogLevel.DORMANT, message, **context)
    
    def void(self, message: str, **context):
        """Log pustyni - trace"""
        self.log(LogLevel.VOID, message, **context)
    
    # Aliasy dla kompatybilności
    def info(self, message: str, **context):
        self.awakening(message, **context)
    
    def warning(self, message: str, **context):
        self.aware(message, **context)
    
    def error(self, message: str, **context):
        self.enlightened(message, **context)
    
    def debug(self, message: str, **context):
        self.dormant(message, **context)
    
    def critical(self, message: str, **context):
        self.transcendent(message, **context)
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki logowania"""
        uptime = datetime.now() - self.start_time
        
        return {
            'logger_name': self.name,
            'min_level': self.min_level.name,
            'total_logs': self.log_count,
            'handlers_count': len(self.handlers),
            'uptime': str(uptime),
            'memory_entries': len(self.memory_handler.entries),
            'context': self.context
        }
    
    def get_recent_logs(self, level: Optional[LogLevel] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Zwraca ostatnie logi"""
        entries = self.memory_handler.get_entries(level, limit)
        return [entry.to_dict() for entry in entries]
    
    def export_logs(self, format: str = 'json', level: Optional[LogLevel] = None) -> str:
        """
        Eksportuje logi
        
        Args:
            format: Format eksportu (json, text)
            level: Filtr poziomów
            
        Returns:
            Dane w wybranym formacie
        """
        entries = self.memory_handler.get_entries(level, 1000)
        
        if format == 'json':
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'logger': self.name,
                'total_entries': len(entries),
                'entries': [entry.to_dict() for entry in entries]
            }
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format == 'text':
            lines = [f"🌟 Astral Log Export - {datetime.now().isoformat()}", "=" * 60]
            
            for entry in entries:
                lines.append(LogFormatter.format_detailed(entry))
            
            return '\n'.join(lines)
        
        else:
            return str(entries)
    
    def clear_logs(self):
        """Czyści logi z pamięci"""
        self.memory_handler.clear()
        self.log_count = 0
        self.start_time = datetime.now()
    
    def setup_file_logging(self, filepath: str, level: Optional[LogLevel] = None):
        """
        Konfiguruje logowanie do pliku
        
        Args:
            filepath: Ścieżka do pliku
            level: Minimalny poziom dla pliku
        """
        file_handler = FileHandler(filepath)
        self.add_handler(file_handler)
        
        if level:
            # Tymczasowo zmień poziom tylko dla tego handlera
            # W pełnej implementacji każdy handler miałby swój poziom
            pass
    
    def create_realm_logger(self, realm_name: str) -> 'AstralLogger':
        """
        Tworzy logger dla konkretnego wymiaru
        
        Args:
            realm_name: Nazwa wymiaru
            
        Returns:
            Nowy logger z kontekstem wymiaru
        """
        realm_logger = AstralLogger(f"{self.name}.{realm_name}", self.min_level)
        realm_logger.set_context(realm=realm_name)
        
        # Udostępnij handlery
        for handler in self.handlers:
            realm_logger.add_handler(handler)
        
        return realm_logger
    
    def create_being_logger(self, being_id: str, realm: Optional[str] = None) -> 'AstralLogger':
        """
        Tworzy logger dla konkretnego bytu
        
        Args:
            being_id: ID bytu
            realm: Opcjonalna nazwa wymiaru
            
        Returns:
            Nowy logger z kontekstem bytu
        """
        being_logger = AstralLogger(f"{self.name}.being", self.min_level)
        context = {'being_id': being_id}
        if realm:
            context['realm'] = realm
        
        being_logger.set_context(**context)
        
        # Udostępnij handlery
        for handler in self.handlers:
            being_logger.add_handler(handler)
        
        return being_logger


# Globalna instancja loggera
_global_logger = AstralLogger("luxdb_v2")


def get_astral_logger(name: Optional[str] = None) -> AstralLogger:
    """
    Pobiera logger astralny
    
    Args:
        name: Nazwa loggera (None = globalny)
        
    Returns:
        Logger astralny
    """
    if name:
        return AstralLogger(name)
    return _global_logger


def setup_global_logging(level: LogLevel = LogLevel.AWAKENING, file_path: Optional[str] = None):
    """
    Konfiguruje globalne logowanie
    
    Args:
        level: Minimalny poziom logowania
        file_path: Opcjonalna ścieżka do pliku loga
    """
    global _global_logger
    _global_logger.min_level = level
    
    if file_path:
        _global_logger.setup_file_logging(file_path)
