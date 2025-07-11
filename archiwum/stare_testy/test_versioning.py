#!/usr/bin/env python3
"""
Test wersjonowania - sprawdzenie czy "latest" wybiera najnowszą wersję
"""
import sys
import os
sys.path.insert(0, '/var/home/oriom/Dokumenty/Federacja/luxdb')

from lux_core.init import initialize_lux_core
from lux_core.routing import resolve_lux_uri, get_all_routes

def test_versioning():
    print("=== Test Wersjonowania Route ===\n")
    
    # Inicjalizacja
    initialize_lux_core()
    
    # Test 1: Sprawdź czy "latest" wybiera v2 (najnowszą)
    print("1. Test wyboru najnowszej wersji:")
    
    test_paths = [
        "system/resources/monitor", 
        "system/resources/detect",
        "system/bootstrap/env",
        "system/safety/check"
    ]
    
    for path in test_paths:
        try:
            func = resolve_lux_uri(path)  # bez @latest - powinno wybrać najnowszą
            print(f"   {path} -> Funkcja: {func}")
            
            # Sprawdź czy to v2 (dynamiczna) czy v1 (statyczna)
            if hasattr(func, '__module__') and 'layer0' in func.__module__:
                print(f"     ✓ Wybrano v2 (dynamiczna z layer0)")
            else:
                print(f"     ✓ Wybrano v1 (statyczna)")
            
        except Exception as e:
            print(f"   ✗ Błąd dla {path}: {e}")
    
    print("\n2. Test jawnego wyboru wersji:")
    
    # Test v1 vs v2
    for path in ["system/resources/monitor", "system/bootstrap/env"]:
        try:
            func_v1 = resolve_lux_uri(f"{path}@v1")
            func_v2 = resolve_lux_uri(f"{path}@v2")
            
            print(f"   {path}@v1 -> {func_v1}")
            print(f"   {path}@v2 -> {func_v2}")
            print(f"   Różne funkcje: {func_v1 != func_v2}")
            
        except Exception as e:
            print(f"   ✗ Błąd: {e}")
    
    print("\n3. Lista wszystkich dostępnych wersji:")
    all_routes = get_all_routes()
    
    # Grupuj po bazowej nazwie
    route_groups = {}
    for path in all_routes.keys():
        if '@' in path:
            base, version = path.split('@')
            if base not in route_groups:
                route_groups[base] = []
            route_groups[base].append(version)
    
    for base, versions in route_groups.items():
        versions.sort(key=lambda v: int(v[1:]) if v.startswith('v') else 0, reverse=True)
        print(f"   {base} -> wersje: {versions} (latest: {versions[0]})")
    
    print("\n=== Test zakończony ===")

if __name__ == "__main__":
    test_versioning()
