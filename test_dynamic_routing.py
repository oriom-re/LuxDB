#!/usr/bin/env python3
"""
Test integracji dynamicznego routingu z głównym systemem
"""
import sys
import os
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from lux_core.init import initialize_lux_core, get_system_info, test_route
from lux_core.routing import get_all_routes, resolve
from lux_core.auto_discovery import get_route_statistics

def test_dynamic_routing():
    """Test pełnej integracji dynamicznego routingu"""
    print("=== Test Dynamicznego Routingu LuxCore ===\n")
    
    # 1. Inicjalizacja systemu
    print("1. Inicjalizacja systemu...")
    init_result = initialize_lux_core()
    print(f"   Status: {init_result['status']}")
    print(f"   Załadowane moduły: {len(init_result['discovery']['discovered_modules'])}")
    print(f"   Zarejestrowane route: {init_result['statistics']['total_routes']}")
    print(f"   - Statyczne: {init_result['statistics']['static_routes']}")
    print(f"   - Dynamiczne: {init_result['statistics']['dynamic_routes']}")
    print()
    
    # 2. Sprawdź wszystkie dostępne route
    print("2. Dostępne route:")
    all_routes = get_all_routes()
    for path, info in all_routes.items():
        route_type = info['type']
        metadata = info.get('metadata', {})
        description = metadata.get('description', 'Brak opisu')
        print(f"   {path} ({route_type}): {description}")
    print()
    
    # 3. Test route dynamicznych (v2)
    print("3. Test route dynamicznych (v2):")
    dynamic_routes_to_test = [
        "system/resources/monitor@v2",
        "system/resources/detect@v2", 
        "system/bootstrap/env@v2",
        "system/safety/check@v2"
    ]
    
    for route in dynamic_routes_to_test:
        print(f"   Testowanie: {route}")
        result = test_route(route)
        if result['status'] == 'success':
            print(f"   ✓ Sukces: {result['result']}")
        else:
            print(f"   ✗ Błąd: {result['error']}")
        print()
    
    # 4. Test route statycznych (v1)
    print("4. Test route statycznych (v1):")
    static_routes_to_test = [
        "system/resources/monitor@v1",
        "system/resources/detect@v1"
    ]
    
    for route in static_routes_to_test:
        print(f"   Testowanie: {route}")
        result = test_route(route)
        if result['status'] == 'success':
            print(f"   ✓ Sukces: {result['result']}")
        else:
            print(f"   ✗ Błąd: {result['error']}")
        print()
    
    # 5. Test route z auto-discovery
    print("5. Test route z auto-discovery:")
    discovery_routes = [
        "system/routing/discover@v1",
        "system/routing/stats@v1"
    ]
    
    for route in discovery_routes:
        print(f"   Testowanie: {route}")
        result = test_route(route)
        if result['status'] == 'success':
            print(f"   ✓ Sukces: {result['result']}")
        else:
            print(f"   ✗ Błąd: {result['error']}")
        print()
    
    # 6. Test wersjonowania (latest)
    print("6. Test wersjonowania (latest):")
    latest_routes = [
        "system/resources/monitor",  # powinno wybrać najnowszą wersję
        "system/resources/detect"
    ]
    
    for route in latest_routes:
        print(f"   Testowanie: {route} (latest)")
        result = test_route(route)
        if result['status'] == 'success':
            print(f"   ✓ Sukces: {result['result']}")
        else:
            print(f"   ✗ Błąd: {result['error']}")
        print()
    
    # 7. Podsumowanie
    print("7. Podsumowanie:")
    system_info = get_system_info()
    print(f"   Wersja systemu: {system_info['version']}")
    print(f"   Status: {system_info['system_status']}")
    print(f"   Łączna liczba route: {system_info['routing_stats']['total_routes']}")
    print()
    
    print("=== Test zakończony ===")

if __name__ == "__main__":
    test_dynamic_routing()
