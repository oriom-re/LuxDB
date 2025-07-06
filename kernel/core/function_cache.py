
"""
💾 Function Cache - Cache dla dynamicznych funkcji

LRU cache z timeout dla exec/marshal i innych funkcji
"""

import time
import marshal
import types
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict


class FunctionCache:
    """
    Cache dla funkcji z LRU i timeout
    
    Przechowuje skompilowane funkcje, kod bytecode
    i inne obiekty z automatycznym czyszczeniem
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.max_size = config.get('max_size', 1000)
        self.ttl_seconds = config.get('ttl_seconds', 3600)
        self.cleanup_interval = config.get('cleanup_interval', 300)
        
        # Cache storage
        self.cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        
        # Statystyki
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0,
            'last_cleanup': time.time()
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Pobiera wartość z cache"""
        current_time = time.time()
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Sprawdź TTL
            if current_time - entry['timestamp'] < self.ttl_seconds:
                # Przenieś na koniec (LRU)
                self.cache.move_to_end(key)
                self.stats['hits'] += 1
                return entry['value']
            else:
                # Wygasły - usuń
                del self.cache[key]
        
        self.stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any) -> bool:
        """Ustawia wartość w cache"""
        try:
            current_time = time.time()
            
            # Sprawdź czy nie przekraczamy rozmiaru
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # Dodaj do cache
            self.cache[key] = {
                'value': value,
                'timestamp': current_time,
                'access_count': 1
            }
            
            # Przenieś na koniec
            self.cache.move_to_end(key)
            
            # Okresowe czyszczenie
            if current_time - self.stats['last_cleanup'] > self.cleanup_interval:
                self._cleanup_expired()
            
            return True
            
        except Exception:
            return False
    
    def _evict_oldest(self):
        """Usuwa najstarszy element (LRU)"""
        if self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
    
    def _cleanup_expired(self):
        """Czyści wygasłe elementy"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if current_time - entry['timestamp'] >= self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.stats['cleanups'] += 1
        
        self.stats['last_cleanup'] = current_time
    
    def compile_and_cache(self, code: str, filename: str = '<cache>') -> Optional[types.CodeType]:
        """Kompiluje i cachuje kod"""
        cache_key = f"code_{hash(code)}"
        
        # Sprawdź cache
        cached = self.get(cache_key)
        if cached:
            return cached
        
        try:
            # Kompiluj
            compiled = compile(code, filename, 'exec')
            
            # Cache
            self.set(cache_key, compiled)
            
            return compiled
            
        except Exception:
            return None
    
    def marshal_and_cache(self, obj: Any, key: str) -> Optional[bytes]:
        """Serializuje obiekt przez marshal i cachuje"""
        cache_key = f"marshal_{key}"
        
        # Sprawdź cache
        cached = self.get(cache_key)
        if cached:
            return cached
        
        try:
            # Marshal
            marshaled = marshal.dumps(obj)
            
            # Cache
            self.set(cache_key, marshaled)
            
            return marshaled
            
        except Exception:
            return None
    
    def unmarshal_from_cache(self, key: str) -> Optional[Any]:
        """Deserializuje obiekt z cache"""
        cache_key = f"marshal_{key}"
        
        cached = self.get(cache_key)
        if cached:
            try:
                return marshal.loads(cached)
            except Exception:
                pass
        
        return None
    
    def clear(self):
        """Czyści cały cache"""
        self.cache.clear()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'cleanups': 0,
            'last_cleanup': time.time()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki cache"""
        hit_rate = 0.0
        total_requests = self.stats['hits'] + self.stats['misses']
        if total_requests > 0:
            hit_rate = self.stats['hits'] / total_requests
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_rate': hit_rate,
            'stats': self.stats.copy()
        }
