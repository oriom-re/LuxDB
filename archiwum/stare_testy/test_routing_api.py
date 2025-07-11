#!/usr/bin/env python3
"""
Test API routingu - pełna demonstracja możliwości
"""
import sys
import os
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from lux_core.init import initialize_lux_core, test_route

def test_routing_api():
    print("=== Test API Routingu ===\n")
    
    # Inicjalizacja
    init_result = initialize_lux_core()
    print(f"Zainicjalizowano system: {init_result['statistics']['total_routes']} route\n")
    
    # 1. Lista wszystkich route
    print("1. Lista wszystkich route:")
    list_result = test_route("api/routing/list@v1")
    if list_result['status'] == 'success':
        result = list_result['result']
        print(f"   Statyczne: {len(result['static_routes'])}")
        print(f"   Dynamiczne: {len(result['dynamic_routes'])}")
        print(f"   Łącznie: {result['total_count']}")
    print()
    
    # 2. Wyszukiwanie route
    print("2. Wyszukiwanie route:")
    search_queries = ["system/resources", "api/routing", "bootstrap"]
    
    for query in search_queries:
        search_result = test_route("api/routing/search@v1", query=query)
        if search_result['status'] == 'success':
            result = search_result['result']
            print(f"   '{query}' -> {result['count']} wyników: {result['matches']}")
    print()
    
    # 3. Informacje o konkretnych route
    print("3. Informacje o route:")
    info_routes = [
        "system/resources/monitor@v2",
        "system/bootstrap/env@v1",
        "api/routing/list@v1"
    ]
    
    for route in info_routes:
        info_result = test_route("api/routing/info@v1", path=route)
        if info_result['status'] == 'success':
            result = info_result['result']
            print(f"   {route}:")
            print(f"     Status: {result['status']}")
            if result['status'] == 'success':
                metadata = result['metadata']
                if isinstance(metadata, dict):
                    print(f"     Typ: {metadata.get('type', 'unknown')}")
                    if 'description' in metadata:
                        print(f"     Opis: {metadata['description']}")
        print()
    
    # 4. Statystyki routingu
    print("4. Statystyki routingu:")
    stats_result = test_route("system/routing/stats@v1")
    if stats_result['status'] == 'success':
        result = stats_result['result']
        print(f"   Statyczne route: {result['static_routes']}")
        print(f"   Dynamiczne route: {result['dynamic_routes']}")
        print(f"   Łącznie: {result['total_routes']}")
        print(f"   Najnowsze dynamiczne: {result['dynamic_routes_list'][-3:]}")
    print()
    
    # 5. Test dodawania własnej route (demo)
    print("5. Demonstracja dodawania własnej route:")
    print("   (Symulacja - w rzeczywistości można dodać funkcję przez API)")
    
    # Przykład jak można dodać funkcję
    def custom_hello(name="World"):
        return f"Hello, {name}!"
    
    # Dodaj route programowo
    from lux_core.routing import register_dynamic_route
    register_dynamic_route("custom/hello@v1", custom_hello, {
        "description": "Prosta funkcja powitalna",
        "permissions": ["read"]
    })
    
    # Przetestuj nową route
    custom_result = test_route("custom/hello@v1", name="LuxCore")
    if custom_result['status'] == 'success':
        print(f"   ✓ Nowa route działa: {custom_result['result']}")
    
    print("\n=== Test API zakończony ===")

if __name__ == "__main__":
    test_routing_api()
