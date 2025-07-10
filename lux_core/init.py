# lux_core/init.py
"""
Inicjalizacja systemu lux_core z auto-discovery
"""
from .auto_discovery import auto_register_routes, get_route_statistics
from .routing import get_all_routes, resolve
from .logger import log_event

def initialize_lux_core():
    """
    Inicjalizuje cały system lux_core:
    1. Uruchamia auto-discovery
    2. Rejestruje wszystkie route
    3. Zwraca podsumowanie
    """
    log_event("system/init", "Inicjalizacja lux_core...")
    
    # Uruchom auto-discovery
    discovery_result = auto_register_routes()
    
    # Pobierz statystyki
    stats = get_route_statistics()
    
    # Pobierz wszystkie route
    all_routes = get_all_routes()
    
    log_event("system/init", f"Inicjalizacja zakończona. Załadowano {len(discovery_result['discovered_modules'])} modułów, zarejestrowano {stats['total_routes']} route.")
    
    return {
        "status": "initialized",
        "discovery": discovery_result,
        "statistics": stats,
        "available_routes": list(all_routes.keys())
    }

def get_system_info():
    """
    Zwraca pełne informacje o systemie lux_core
    """
    stats = get_route_statistics()
    all_routes = get_all_routes()
    
    return {
        "version": "2.0.0",
        "system_status": "active",
        "routing_stats": stats,
        "available_routes": {
            path: {
                "type": info["type"],
                "metadata": info["metadata"]
            }
            for path, info in all_routes.items()
        }
    }

# Funkcja do łatwego testowania
def test_route(route_path: str, *args, **kwargs):
    """
    Testuje konkretną route
    """
    try:
        func = resolve(f"lux://{route_path}")
        result = func(*args, **kwargs)
        return {
            "status": "success",
            "route": route_path,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "route": route_path,
            "error": str(e)
        }
