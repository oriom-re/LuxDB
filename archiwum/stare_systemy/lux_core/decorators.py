# lux_core/decorators.py
"""
System dekoratorów do automatycznej rejestracji funkcji w routingu
"""
import functools
from typing import Dict, Callable, Optional, List

# Globalny rejestr funkcji z dekoratorami
DECORATED_ROUTES: Dict[str, Dict] = {}

def lux_route(path: str, 
              description: Optional[str] = None,
              permissions: Optional[List[str]] = None,
              cache_ttl: Optional[int] = None):
    """
    Dekorator do automatycznej rejestracji funkcji w routingu
    
    Args:
        path: Ścieżka lux:// (np. "system/resources/detect@v2")
        description: Opis funkcji
        permissions: Lista wymaganych uprawnień
        cache_ttl: Czas cache'owania w sekundach
    """
    def decorator(func):
        DECORATED_ROUTES[path] = {
            "function": func,
            "description": description,
            "permissions": permissions or [],
            "cache_ttl": cache_ttl,
            "module": func.__module__,
            "name": func.__name__
        }
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def discover_routes():
    """Skanuje moduły i buduje routing z dekoratorów"""
    return {path: info["function"] for path, info in DECORATED_ROUTES.items()}

def get_route_info(path: str):
    """Zwraca pełne informacje o route"""
    return DECORATED_ROUTES.get(path)

def list_all_routes():
    """Lista wszystkich zarejestrowanych route z metadanymi"""
    return DECORATED_ROUTES
