# lux_core/auto_discovery.py
"""
System auto-discovery dla dynamicznego ładowania i rejestracji route
"""
import os
import importlib
import pkgutil
from typing import List, Dict
from .decorators import DECORATED_ROUTES, lux_route
from .routing import resolve_lux_uri

def discover_and_load_modules(base_path: str = None):
    """
    Skanuje i ładuje wszystkie moduły w zadanej ścieżce, rejestrując funkcje z dekoratorami
    """
    if base_path is None:
        base_path = os.path.dirname(__file__)
    
    discovered_modules = []
    
    # Skanuj pakiet lux_core
    for importer, modname, ispkg in pkgutil.walk_packages([base_path], prefix="lux_core."):
        try:
            module = importlib.import_module(modname)
            discovered_modules.append(modname)
        except ImportError as e:
            print(f"Nie udało się załadować modułu {modname}: {e}")
    
    # Dodatkowo, spróbuj załadować moduły layer0 bezpośrednio
    layer0_modules = [
        "lux_core.layer0.bootstrap",
        "lux_core.layer0.safety_protocols", 
        "lux_core.layer0.system_resources",
        "lux_core.layer0.realm_mounter",
        "lux_core.layer0.layer0_interface",
        "lux_core.layer0.validation",
    ]
    
    for modname in layer0_modules:
        try:
            if modname not in discovered_modules:
                module = importlib.import_module(modname)
                discovered_modules.append(modname)
        except ImportError as e:
            print(f"Nie udało się załadować modułu layer0 {modname}: {e}")
    
    return discovered_modules

def scan_for_decorated_functions():
    """
    Skanuje wszystkie załadowane moduły w poszukiwaniu funkcji z dekoratorami @lux_route
    """
    return dict(DECORATED_ROUTES)

def auto_register_routes():
    """
    Automatycznie rejestruje wszystkie route z dekoratorów po załadowaniu modułów
    """
    discovered_modules = discover_and_load_modules()
    decorated_routes = scan_for_decorated_functions()
    
    return {
        "discovered_modules": discovered_modules,
        "registered_routes": list(decorated_routes.keys()),
        "total_routes": len(decorated_routes)
    }

def get_route_statistics():
    """
    Zwraca statystyki route (statyczne vs dynamiczne)
    """
    from .registry import LUX_ROUTING
    
    return {
        "static_routes": len(LUX_ROUTING),
        "dynamic_routes": len(DECORATED_ROUTES),
        "total_routes": len(LUX_ROUTING) + len(DECORATED_ROUTES),
        "static_routes_list": list(LUX_ROUTING.keys()),
        "dynamic_routes_list": list(DECORATED_ROUTES.keys())
    }

@lux_route("system/routing/discover@v1", description="Wykonaj auto-discovery i załaduj wszystkie moduły")
def perform_auto_discovery():
    """Route do uruchamiania auto-discovery przez routing"""
    return auto_register_routes()

@lux_route("system/routing/stats@v1", description="Zwróć statystyki wszystkich route")
def get_routing_stats():
    """Route do pobierania statystyk routingu"""
    return get_route_statistics()

@lux_route("system/introspection/live@v1", description="Wykonaj live introspection systemu")
def perform_live_introspection():
    """Route do uruchamiania live introspection przez routing"""
    # Statystyki routingu
    stats = get_route_statistics()

    # Zasoby systemowe
    monitor_func = resolve_lux_uri("system/resources/monitor@v2")
    resources = monitor_func()

    return {
        "stats": stats,
        "resources": resources
    }
