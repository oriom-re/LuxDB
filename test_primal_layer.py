
#!/usr/bin/env python3
"""
🌑 Test warstwy 0 - Pre-Soul Core

Testuje funkcjonalność warstwy pierwotnej systemu
"""

import time
import sys
import os
from datetime import datetime

# Dodaj ścieżkę do LuxDB v2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from luxdb_v2.core.primal_bootstrap import execute_primal_bootstrap, PrimalConfig
from luxdb_v2.core.primal_core import PrimalCore, get_primal_core, initialize_primal_core


def print_test_header(title: str):
    """Wyświetla nagłówek testu"""
    print(f"\n{'='*60}")
    print(f"🌑 {title}")
    print('='*60)


def test_primal_bootstrap():
    """Test podstawowego bootstrap warstwy pierwotnej"""
    print_test_header("TEST 1: Primal Bootstrap")
    
    print("1. Wykonywanie bootstrap warstwy pierwotnej...")
    start_time = time.time()
    
    result = execute_primal_bootstrap()
    
    bootstrap_time = time.time() - start_time
    
    print(f"   ⏱️  Czas bootstrap: {bootstrap_time:.2f}s")
    print(f"   📊 Wynik: {'✅ SUKCES' if result['success'] else '❌ BŁĄD'}")
    
    if result['success']:
        print(f"   📂 Zmontowane wymiary: {len(result['mounted_realms'])}")
        print(f"   ✅ Ukończone fazy: {', '.join(result['phases_completed'])}")
        
        for realm_name, connection in result['mounted_realms'].items():
            print(f"     • {realm_name}: {connection}")
    else:
        print(f"   💥 Nieudane fazy: {', '.join(result['phases_failed'])}")
    
    return result['success']


def test_primal_core_lifecycle():
    """Test pełnego cyklu życia Primal Core"""
    print_test_header("TEST 2: Primal Core Lifecycle")
    
    print("1. Inicjalizacja Primal Core...")
    start_time = time.time()
    
    result = initialize_primal_core()
    
    if not result['success']:
        print(f"   ❌ Inicjalizacja nieudana: {result.get('error')}")
        return False
    
    core = get_primal_core()
    init_time = time.time() - start_time
    
    print(f"   ✅ Inicjalizacja udana w {init_time:.2f}s")
    print(f"   🎯 Stan: {core.state.value}")
    
    print("2. Sprawdzanie statusu...")
    status = core.get_status()
    
    print(f"   📊 Zmontowane wymiary: {status['mounted_realms']}")
    print(f"   🔍 Zasoby w monitoringu: {status['resource_monitor']['total_resources']}")
    print(f"   ⚡ Zasoby aktywne: {status['resource_monitor']['active_resources']}")
    
    print("3. Test monitoringu przez 3 sekundy...")
    time.sleep(3)
    
    # Sprawdź status po czasie
    status_after = core.get_status()
    print(f"   ⏱️  Uptime: {status_after['uptime_seconds']:.1f}s")
    
    print("4. Graceful shutdown...")
    shutdown_result = core.shutdown()
    
    if shutdown_result['success']:
        print(f"   ✅ Shutdown udany po {shutdown_result['shutdown_time']:.2f}s")
        return True
    else:
        print(f"   ❌ Shutdown nieudany: {shutdown_result.get('error')}")
        return False


def test_resource_monitoring():
    """Test systemu monitorowania zasobów"""
    print_test_header("TEST 3: Resource Monitoring")
    
    # Użyj świeżej instancji
    config = PrimalConfig()
    core = PrimalCore(config)
    
    print("1. Inicjalizacja i rejestracja zasobów...")
    init_result = core.initialize()
    
    if not init_result['success']:
        print(f"   ❌ Inicjalizacja nieudana")
        return False
    
    print("2. Sprawdzenie zasobów po inicjalizacji...")
    status = core.get_status()
    resources = status['resource_monitor']['resources']
    
    print(f"   📦 Zarejestrowanych zasobów: {len(resources)}")
    
    for name, info in resources.items():
        print(f"     • {name} ({info['type']}): {info['status']}")
    
    print("3. Test przez 2 sekundy...")
    time.sleep(2)
    
    # Sprawdź status po monitoringu
    final_status = core.get_status()
    final_resources = final_status['resource_monitor']['resources']
    
    active_count = len([r for r in final_resources.values() if r['status'] == 'active'])
    print(f"   ⚡ Zasoby aktywne po monitoringu: {active_count}/{len(final_resources)}")
    
    # Shutdown
    core.shutdown()
    
    return active_count > 0


def test_layer0_to_layer1_interface():
    """Test interfejsu między warstwą 0 a 1"""
    print_test_header("TEST 4: Interface Layer 0 → Layer 1")
    
    print("1. Inicjalizacja warstwy 0...")
    result = initialize_primal_core()
    
    if not result['success']:
        print("   ❌ Warstwa 0 nie została zainicjalizowana")
        return False
    
    core = get_primal_core()
    
    print("2. Test interfejsu dla warstwy 1...")
    
    # Test dostępu do wymiarów
    realm_interface = core.get_realm_interface('astral_prime')
    print(f"   🔗 Interface astral_prime: {realm_interface or 'None'}")
    
    consciousness_interface = core.get_realm_interface('consciousness')
    print(f"   🧠 Interface consciousness: {consciousness_interface or 'None'}")
    
    # Test callback dla warstwy 1
    layer1_notifications = []
    
    def layer1_callback(primal_status):
        layer1_notifications.append(primal_status)
        print(f"   📢 Callback warstwy 1: Stan={primal_status['state']}")
    
    core.register_layer1_callback(layer1_callback)
    
    print("3. Test operacyjności warstwy 0...")
    is_operational = core.is_operational()
    print(f"   ⚙️  Operacyjna: {'✅' if is_operational else '❌'}")
    
    # Test raportu bootstrap
    bootstrap_report = core.get_bootstrap_report()
    if bootstrap_report:
        print(f"   📊 Raport bootstrap dostępny: ✅")
        print(f"     • Bootstrap time: {bootstrap_report.get('bootstrap_time', 0):.2f}s")
    
    core.shutdown()
    
    success = (realm_interface is not None and 
               consciousness_interface is not None and 
               is_operational)
    
    return success


def run_all_tests():
    """Uruchamia wszystkie testy warstwy 0"""
    print("🌑 TESTY WARSTWY 0 - PRE-SOUL CORE")
    print("🌑 System bezduszny, ale sprawiedliwy jak BIOS")
    
    tests = [
        ("Primal Bootstrap", test_primal_bootstrap),
        ("Primal Core Lifecycle", test_primal_core_lifecycle),
        ("Resource Monitoring", test_resource_monitoring),
        ("Layer 0→1 Interface", test_layer0_to_layer1_interface)
    ]
    
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Uruchamianie: {test_name}")
            result = test_func()
            results.append((test_name, result))
            print(f"   {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"   💥 EXCEPTION: {e}")
            results.append((test_name, False))
    
    total_time = time.time() - start_time
    
    # Podsumowanie
    print(f"\n{'='*60}")
    print("🌑 PODSUMOWANIE TESTÓW WARSTWY PIERWOTNEJ")
    print('='*60)
    
    passed = len([r for r in results if r[1]])
    failed = len(results) - passed
    
    print(f"✅ Testy udane: {passed}")
    print(f"❌ Testy nieudane: {failed}")
    print(f"⏱️  Całkowity czas: {total_time:.2f}s")
    print(f"🎯 Sukces: {'✅ WSZYSTKIE TESTY PRZESZŁY' if failed == 0 else '❌ NIEKTÓRE TESTY NIEUDANE'}")
    
    if failed > 0:
        print("\n💥 Nieudane testy:")
        for test_name, result in results:
            if not result:
                print(f"   • {test_name}")
    
    print(f"\n🌑 Warstwa pierwotna {'✅ GOTOWA' if failed == 0 else '❌ WYMAGA NAPRAWY'}")


if __name__ == "__main__":
    run_all_tests()
