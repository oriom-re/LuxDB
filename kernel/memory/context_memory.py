
"""
🧠 Context Memory - Szybka, tymczasowa pamięć kontekstowa

Przechowuje dynamiczny kontekst i zmienne dla Kernela
"""

import time
import json
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import OrderedDict


class ContextMemory:
    """
    Szybka pamięć kontekstowa Kernela
    
    Przechowuje:
    - Zmienne kontekstowe
    - Dane sesji
    - Cache tymczasowy
    - Historię operacji
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Konfiguracja
        self.max_context_size = config.get('max_context_size', 10000)
        self.cleanup_threshold = config.get('cleanup_threshold', 8000)
        self.compression_enabled = config.get('compression_enabled', True)
        self.auto_cleanup_interval = config.get('auto_cleanup_interval', 300)
        
        # Pamięć kontekstowa
        self.context_data: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.session_data: Dict[str, Dict[str, Any]] = {}
        self.temporary_cache: Dict[str, Any] = {}
        
        # Metadane
        self.access_times: Dict[str, float] = {}
        self.creation_times: Dict[str, float] = {}
        self.access_counts: Dict[str, int] = {}
        
        # Statystyki
        self.stats = {
            'contexts_created': 0,
            'contexts_accessed': 0,
            'contexts_removed': 0,
            'cleanup_operations': 0,
            'last_cleanup': None
        }
        
        # Lock dla thread safety
        self._lock = threading.RLock()
        
        # Inicjalizacja
        self.initialized = False
    
    def initialize(self):
        """Inicjalizuje pamięć kontekstową"""
        with self._lock:
            if not self.initialized:
                self.initialized = True
                self._schedule_cleanup()
    
    def store_context(self, context_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Przechowuje kontekst"""
        try:
            with self._lock:
                current_time = time.time()
                
                # Sprawdź czy nie przekraczamy limitu
                if len(self.context_data) >= self.max_context_size:
                    self._cleanup_old_contexts()
                
                # Przygotuj dane kontekstu
                context_entry = {
                    'data': data,
                    'created_at': current_time,
                    'ttl': ttl,
                    'expires_at': current_time + ttl if ttl else None
                }
                
                # Dodaj do pamięci
                self.context_data[context_id] = context_entry
                self.access_times[context_id] = current_time
                self.creation_times[context_id] = current_time
                self.access_counts[context_id] = 1
                
                self.stats['contexts_created'] += 1
                
                return True
                
        except Exception as e:
            return False
    
    def get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera kontekst"""
        try:
            with self._lock:
                if context_id not in self.context_data:
                    return None
                
                context_entry = self.context_data[context_id]
                current_time = time.time()
                
                # Sprawdź TTL
                if context_entry.get('expires_at') and current_time > context_entry['expires_at']:
                    self.remove_context(context_id)
                    return None
                
                # Aktualizuj statystyki dostępu
                self.access_times[context_id] = current_time
                self.access_counts[context_id] = self.access_counts.get(context_id, 0) + 1
                self.stats['contexts_accessed'] += 1
                
                # Przenieś na koniec (LRU)
                self.context_data.move_to_end(context_id)
                
                return context_entry['data']
                
        except Exception as e:
            return None
    
    def remove_context(self, context_id: str) -> bool:
        """Usuwa kontekst"""
        try:
            with self._lock:
                if context_id in self.context_data:
                    del self.context_data[context_id]
                    self.access_times.pop(context_id, None)
                    self.creation_times.pop(context_id, None)
                    self.access_counts.pop(context_id, None)
                    
                    self.stats['contexts_removed'] += 1
                    return True
                return False
                
        except Exception as e:
            return False
    
    def update_context(self, context_id: str, updates: Dict[str, Any]) -> bool:
        """Aktualizuje kontekst"""
        try:
            with self._lock:
                if context_id not in self.context_data:
                    return False
                
                context_entry = self.context_data[context_id]
                context_entry['data'].update(updates)
                
                # Aktualizuj czas dostępu
                self.access_times[context_id] = time.time()
                self.access_counts[context_id] = self.access_counts.get(context_id, 0) + 1
                
                return True
                
        except Exception as e:
            return False
    
    def list_contexts(self) -> List[str]:
        """Zwraca listę kontekstów"""
        with self._lock:
            return list(self.context_data.keys())
    
    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Pobiera dane sesji"""
        with self._lock:
            return self.session_data.get(session_id, {})
    
    def set_session_data(self, session_id: str, data: Dict[str, Any]):
        """Ustawia dane sesji"""
        with self._lock:
            self.session_data[session_id] = data
    
    def clear_session(self, session_id: str):
        """Czyści sesję"""
        with self._lock:
            self.session_data.pop(session_id, None)
    
    def cache_temporary(self, key: str, value: Any, ttl: int = 300):
        """Przechowuje w tymczasowym cache"""
        with self._lock:
            self.temporary_cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl
            }
    
    def get_temporary(self, key: str) -> Optional[Any]:
        """Pobiera z tymczasowego cache"""
        with self._lock:
            if key in self.temporary_cache:
                entry = self.temporary_cache[key]
                if time.time() < entry['expires_at']:
                    return entry['value']
                else:
                    del self.temporary_cache[key]
            return None
    
    def _cleanup_old_contexts(self):
        """Czyści stare konteksty"""
        current_time = time.time()
        
        # Usuń wygasłe konteksty
        expired_contexts = []
        for context_id, context_entry in self.context_data.items():
            if context_entry.get('expires_at') and current_time > context_entry['expires_at']:
                expired_contexts.append(context_id)
        
        for context_id in expired_contexts:
            self.remove_context(context_id)
        
        # Jeśli nadal za dużo, usuń najstarsze (LRU)
        while len(self.context_data) > self.cleanup_threshold:
            oldest_context = next(iter(self.context_data))
            self.remove_context(oldest_context)
        
        # Wyczyść tymczasowy cache
        expired_temp_keys = []
        for key, entry in self.temporary_cache.items():
            if current_time > entry['expires_at']:
                expired_temp_keys.append(key)
        
        for key in expired_temp_keys:
            del self.temporary_cache[key]
        
        self.stats['cleanup_operations'] += 1
        self.stats['last_cleanup'] = datetime.now().isoformat()
    
    def _schedule_cleanup(self):
        """Planuje automatyczne czyszczenie"""
        def cleanup_loop():
            while self.initialized:
                time.sleep(self.auto_cleanup_interval)
                if len(self.context_data) > self.cleanup_threshold:
                    self._cleanup_old_contexts()
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
    
    def reset(self):
        """Resetuje pamięć kontekstową"""
        with self._lock:
            self.context_data.clear()
            self.session_data.clear()
            self.temporary_cache.clear()
            self.access_times.clear()
            self.creation_times.clear()
            self.access_counts.clear()
            
            self.stats = {
                'contexts_created': 0,
                'contexts_accessed': 0,
                'contexts_removed': 0,
                'cleanup_operations': 0,
                'last_cleanup': None
            }
    
    def is_healthy(self) -> bool:
        """Sprawdza zdrowie pamięci kontekstowej"""
        with self._lock:
            return (
                self.initialized and
                len(self.context_data) < self.max_context_size and
                len(self.temporary_cache) < 1000
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status pamięci kontekstowej"""
        with self._lock:
            return {
                'initialized': self.initialized,
                'contexts_count': len(self.context_data),
                'sessions_count': len(self.session_data),
                'temp_cache_count': len(self.temporary_cache),
                'stats': self.stats.copy(),
                'memory_usage': {
                    'contexts': len(self.context_data),
                    'max_contexts': self.max_context_size,
                    'cleanup_threshold': self.cleanup_threshold
                }
            }
