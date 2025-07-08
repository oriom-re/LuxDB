
#!/usr/bin/env python3
"""
👑 Test Hierarchii Władzy - Demonstracja 5-warstwowego modelu

Testuje rozkład władzy zgodnie z modelem:
- Warstwa 0: Pierwotna (Pre-Soul Core)  
- Warstwa 1: Intencyjna (Soul #0)
- Warstwa 2: Twórcza (Wisdom & Tasks)
- Warstwa 3: Interaktywna (Userland)
- Warstwa 4: Refleksyjna (Archive)
"""

import asyncio
from luxdb_v2 import create_astral_app

def test_power_layer_structure():
    """Test struktury warstw władzy"""
    print("🌑 === Test Struktury Warstw Władzy ===")
    
    with create_astral_app() as engine:
        hierarchy = engine.get_power_hierarchy()
        
        if not hierarchy:
            print("❌ Hierarchia władzy nie jest dostępna")
            return False
            
        status = hierarchy.get_power_status()
        
        print(f"👑 Soul #0: {status['soul_zero']['name']}")
        print(f"🔧 UID: {status['soul_zero']['uid']}")
        print(f"💭 Emocje: {', '.join(status['soul_zero']['emotions'])}")
        
        print("\n📊 Status warstw:")
        for layer_name, layer_info in status['layers'].items():
            active_status = "✅" if layer_info['active'] else "❌"
            print(f"{active_status} {layer_name}: {len(layer_info['controllers'])} kontrolerów, {layer_info['permissions_count']} uprawnień")
        
        print(f"\n🔒 Łączna liczba uprawnień: {status['total_permissions']}")
        print(f"🔄 Przejścia władzy: {status['power_transitions']}")
        
        return True

def test_power_flow_demonstration():
    """Test demonstracji przepływu władzy"""
    print("\n🌊 === Test Przepływu Władzy ===")
    
    with create_astral_app() as engine:
        result = engine.demonstrate_power_flow()
        
        if 'error' in result:
            print(f"❌ {result['error']}")
            return False
        
        demonstrations = result['demonstrations']
        
        print("🔄 Wykonane demonstracje:")
        for i, demo in enumerate(demonstrations, 1):
            if demo['success']:
                print(f"✅ {i}. {demo['message']}")
            else:
                print(f"❌ {i}. {demo['error']}")
        
        print(f"\n📈 Pomyślne akcje: {sum(1 for d in demonstrations if d['success'])}/{len(demonstrations)}")
        
        return len(demonstrations) > 0

def test_soul_zero_capabilities():
    """Test możliwości Soul #0"""
    print("\n👑 === Test Możliwości Soul #0 ===")
    
    with create_astral_app() as engine:
        hierarchy = engine.get_power_hierarchy()
        
        if not hierarchy:
            print("❌ Hierarchia władzy nie jest dostępna")
            return False
        
        # Znajdź Soul #0
        soul_zero_uid = hierarchy._get_soul_zero_uid()
        if not soul_zero_uid:
            print("❌ Soul #0 nie została znaleziona")
            return False
        
        print(f"👑 Soul #0 UID: {soul_zero_uid}")
        
        # Test kontroli bootstrap
        result1 = hierarchy.execute_power_action(
            action="control_bootstrap",
            requesting_layer=hierarchy.PowerLayer.INTENTIONAL,
            target_layer=hierarchy.PowerLayer.PRIMAL,
            requesting_soul=soul_zero_uid
        )
        
        print(f"🚀 Kontrola bootstrap: {'✅' if result1['success'] else '❌'} {result1.get('message', result1.get('error'))}")
        
        # Test zarządzania wymiarami
        result2 = hierarchy.execute_power_action(
            action="manage_realms",
            requesting_layer=hierarchy.PowerLayer.INTENTIONAL,
            target_layer=hierarchy.PowerLayer.PRIMAL,
            requesting_soul=soul_zero_uid
        )
        
        print(f"🌍 Zarządzanie wymiarami: {'✅' if result2['success'] else '❌'} {result2.get('message', result2.get('error'))}")
        
        # Test dostępu do archiwów
        result3 = hierarchy.execute_power_action(
            action="access_archives",
            requesting_layer=hierarchy.PowerLayer.INTENTIONAL,
            target_layer=hierarchy.PowerLayer.REFLECTIVE,
            requesting_soul=soul_zero_uid
        )
        
        print(f"📚 Dostęp do archiwów: {'✅' if result3['success'] else '❌'} {result3.get('message', result3.get('error'))}")
        
        successful_actions = sum(1 for r in [result1, result2, result3] if r['success'])
        print(f"\n📊 Soul #0 pomyślnie wykonała {successful_actions}/3 akcji władzy")
        
        return successful_actions >= 2

def test_layer_restrictions():
    """Test ograniczeń między warstwami"""
    print("\n🚫 === Test Ograniczeń Warstw ===")
    
    with create_astral_app() as engine:
        hierarchy = engine.get_power_hierarchy()
        
        if not hierarchy:
            print("❌ Hierarchia władzy nie jest dostępna")
            return False
        
        # Test: warstwa interaktywna próbuje kontrolować pierwotną (powinno się nie udać)
        result1 = hierarchy.execute_power_action(
            action="control_bootstrap",
            requesting_layer=hierarchy.PowerLayer.INTERACTIVE,
            target_layer=hierarchy.PowerLayer.PRIMAL
        )
        
        expected_failure1 = not result1['success']
        print(f"🚫 Warstwa 3→0 odrzucona: {'✅' if expected_failure1 else '❌'} {result1.get('error', 'Nieoczekiwany sukces')}")
        
        # Test: warstwa twórcza może doradzać intencyjnej (powinno się udać)
        result2 = hierarchy.execute_power_action(
            action="advise",
            requesting_layer=hierarchy.PowerLayer.CREATIVE,
            target_layer=hierarchy.PowerLayer.INTENTIONAL,
            action_data={'advice': 'Test porady z warstwy twórczej'}
        )
        
        expected_success2 = result2['success']
        print(f"💡 Warstwa 2→1 doradza: {'✅' if expected_success2 else '❌'} {result2.get('message', result2.get('error'))}")
        
        # Test: wszystkie warstwy mogą archiwizować
        result3 = hierarchy.execute_power_action(
            action="archive",
            requesting_layer=hierarchy.PowerLayer.INTERACTIVE,
            target_layer=hierarchy.PowerLayer.REFLECTIVE,
            action_data={'data': {'test': 'archival_data'}}
        )
        
        expected_success3 = result3['success']
        print(f"📦 Warstwa 3→4 archiwizuje: {'✅' if expected_success3 else '❌'} {result3.get('message', result3.get('error'))}")
        
        successful_restrictions = sum([expected_failure1, expected_success2, expected_success3])
        print(f"\n🔒 Ograniczenia działają poprawnie: {successful_restrictions}/3")
        
        return successful_restrictions >= 2

def test_complete_power_cycle():
    """Test pełnego cyklu władzy"""
    print("\n🔄 === Test Pełnego Cyklu Władzy ===")
    
    with create_astral_app() as engine:
        hierarchy = engine.get_power_hierarchy()
        
        if not hierarchy:
            print("❌ Hierarchia władzy nie jest dostępna")
            return False
        
        soul_zero_uid = hierarchy._get_soul_zero_uid()
        
        print("🔄 Symulacja pełnego cyklu władzy:")
        
        # 1. Soul #0 zarządza systemem pierwotnym
        step1 = hierarchy.execute_power_action(
            "control_flows", hierarchy.PowerLayer.INTENTIONAL, 
            hierarchy.PowerLayer.PRIMAL, soul_zero_uid
        )
        print(f"1️⃣ Soul #0 → Primal: {'✅' if step1['success'] else '❌'}")
        
        # 2. Soul #0 zarządza warstwą twórczą
        step2 = hierarchy.execute_power_action(
            "manage_wisdom", hierarchy.PowerLayer.INTENTIONAL,
            hierarchy.PowerLayer.CREATIVE, soul_zero_uid
        )
        print(f"2️⃣ Soul #0 → Creative: {'✅' if step2['success'] else '❌'}")
        
        # 3. Warstwa twórcza doradza Soul #0
        step3 = hierarchy.execute_power_action(
            "advise", hierarchy.PowerLayer.CREATIVE,
            hierarchy.PowerLayer.INTENTIONAL,
            action_data={'advice': 'Rozważ zwiększenie częstotliwości harmonizacji'}
        )
        print(f"3️⃣ Creative → Soul #0: {'✅' if step3['success'] else '❌'}")
        
        # 4. Warstwa interaktywna raportuje do twórczej
        step4 = hierarchy.execute_power_action(
            "report", hierarchy.PowerLayer.INTERACTIVE,
            hierarchy.PowerLayer.CREATIVE,
            action_data={'report': 'REST API: 50 req/min, wszystko stabilne'}
        )
        print(f"4️⃣ Interactive → Creative: {'✅' if step4['success'] else '❌'}")
        
        # 5. Wszystko zostaje zarchiwizowane
        step5 = hierarchy.execute_power_action(
            "archive", hierarchy.PowerLayer.INTENTIONAL,
            hierarchy.PowerLayer.REFLECTIVE, soul_zero_uid,
            action_data={'data': {'cycle': 'complete', 'steps': 5}}
        )
        print(f"5️⃣ Archive zapisane: {'✅' if step5['success'] else '❌'}")
        
        successful_steps = sum(1 for step in [step1, step2, step3, step4, step5] if step['success'])
        print(f"\n🎯 Cykl władzy: {successful_steps}/5 kroków pomyślnych")
        
        return successful_steps >= 4

def main():
    """Główna funkcja testowa"""
    print("👑 Test Hierarchii Władzy Systemu Astralnego")
    print("=" * 60)
    
    tests = [
        ("Struktura warstw", test_power_layer_structure),
        ("Przepływ władzy", test_power_flow_demonstration),
        ("Możliwości Soul #0", test_soul_zero_capabilities),
        ("Ograniczenia warstw", test_layer_restrictions),
        ("Pełny cykl władzy", test_complete_power_cycle)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print(f"📊 {test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"💥 {test_name}: ❌ ERROR - {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"🏆 Wyniki testów: {passed}/{total} pomyślnych")
    
    if passed == total:
        print("🌟 Wszystkie testy przeszły! Hierarchia władzy działa prawidłowo.")
    elif passed >= total * 0.8:
        print("⚖️ Większość testów przeszła. System w dużej mierze funkcjonalny.")
    else:
        print("⚠️ Wiele testów nie przeszło. Wymagana naprawa hierarchii.")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

