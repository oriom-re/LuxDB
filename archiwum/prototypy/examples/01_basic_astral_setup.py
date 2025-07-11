
#!/usr/bin/env python3
"""
🌟 LuxDB v2 - Podstawowe przykłady użycia

Demonstruje inicjalizację i podstawowe operacje w systemie astralnym
"""

import sys
import os
import time
from datetime import datetime

# Dodaj ścieżkę do LuxDB v2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from luxdb_v2 import create_astral_app, quick_start, print_astral_banner


def example_basic_initialization():
    """Przykład podstawowej inicjalizacji systemu astralnego"""
    print("🔮 Przykład 1: Podstawowa inicjalizacja")
    print("=" * 50)
    
    # Szybkie uruchomienie dla rozwoju
    with quick_start(realm_type='memory', port=5050) as engine:
        print(f"✨ System astralny uruchomiony!")
        
        # Sprawdź status
        status = engine.get_status()
        print(f"🌟 Poziom świadomości: {status['astral_engine']['consciousness_level']}")
        print(f"🌍 Aktywne wymiary: {len(status['realms'])}")
        
        # Pierwsza medytacja
        meditation = engine.meditate()
        print(f"🧘 Wynik medytacji: {meditation['harmony_score']:.1f}/100")
        
        time.sleep(2)
    
    print("🕊️ System gracefully transcended\n")


def example_realm_operations():
    """Przykład operacji na wymiarach"""
    print("🌌 Przykład 2: Operacje na wymiarach")
    print("=" * 50)
    
    # Konfiguracja z wieloma wymiarami
    config = {
        'realms': {
            'primary': 'memory://primary_dimension',
            'cache': 'memory://cache_dimension'
        },
        'consciousness_level': 'enlightened'
    }
    
    with create_astral_app(config) as engine:
        print(f"✨ Utworzono {len(engine.realms)} wymiary")
        
        # Pobierz wymiar
        primary_realm = engine.get_realm('primary')
        print(f"🌍 Główny wymiar: {primary_realm.name}")
        
        # Status wymiaru
        realm_status = primary_realm.get_status()
        print(f"   • Typ: {realm_status['type']}")
        print(f"   • Połączony: {'✓' if realm_status['connected'] else '✗'}")
        print(f"   • Zdrowy: {'✓' if realm_status['healthy'] else '✗'}")
        
        # Lista wszystkich wymiarów
        all_realms = engine.list_realms()
        print(f"📋 Wszystkie wymiary: {', '.join(all_realms)}")
        
        time.sleep(1)
    
    print("🕊️ Wszystkie wymiary transcended\n")


def example_consciousness_monitoring():
    """Przykład monitorowania świadomości systemu"""
    print("🧠 Przykład 3: Monitorowanie świadomości")
    print("=" * 50)
    
    with quick_start(realm_type='memory', port=5051) as engine:
        print("🔍 Obserwacja świadomości systemu...")
        
        # Kilka cykli medytacji
        for i in range(3):
            meditation = engine.meditate()
            
            system_state = meditation['system_state']
            print(f"   Cykl {i+1}:")
            print(f"   • Czas działania: {system_state['uptime']}")
            print(f"   • Wymiary aktywne: {system_state['active_realms']}")
            print(f"   • Harmonia: {meditation['harmony_score']:.1f}/100")
            
            # Rekomendacje
            recommendations = meditation.get('recommendations', [])
            for rec in recommendations[:2]:  # Pokaż max 2
                print(f"   💡 {rec}")
            
            time.sleep(1)
        
        # Historia insights
        insights_history = engine.consciousness.get_insights_history(limit=2)
        print(f"\n📊 Historia obserwacji: {len(insights_history)} wpisów")
        
        # Analiza wzorców
        patterns = engine.consciousness.meditate_on_patterns()
        if 'stability_score' in patterns:
            print(f"⚖️ Wynik stabilności: {patterns['stability_score']:.1f}/100")
    
    print("🕊️ Monitorowanie zakończone\n")


def example_harmony_system():
    """Przykład systemu harmonii"""
    print("⚖️ Przykład 4: System harmonii")
    print("=" * 50)
    
    config = {
        'realms': {
            'light': 'memory://light_realm',
            'shadow': 'memory://shadow_realm'
        },
        'harmony_check_interval': 1,  # Częste sprawdzenia dla demo
        'consciousness_level': 'transcendent'
    }
    
    with create_astral_app(config) as engine:
        print("🌟 System harmonii aktywowany")
        
        # Ręczna harmonizacja
        print("🎵 Harmonizowanie systemu...")
        engine.harmonize()
        
        # Sprawdź wynik harmonii
        harmony_score = engine.harmony.calculate_harmony_score()
        print(f"⚖️ Wynik harmonii: {harmony_score:.1f}/100")
        
        # Balansowanie
        engine.harmony.balance()
        print("⚖️ System zbilansowany")
        
        # Poczekaj na automatyczny cykl harmonii
        print("⏳ Oczekiwanie na automatyczną harmonizację...")
        time.sleep(3)
        
        # Finalna medytacja
        final_meditation = engine.meditate()
        final_harmony = final_meditation['harmony_score']
        print(f"✨ Finalna harmonia: {final_harmony:.1f}/100")
    
    print("🕊️ Harmonia zachowana\n")


def example_service_integration():
    """Przykład integracji z serwisem"""
    print("🚀 Przykład 5: Integracja z serwisem")
    print("=" * 50)
    
    # Konfiguracja jak w serwisie
    config = {
        'realms': {
            'primary': 'sqlite://db/example_astral.db',
            'cache': 'memory://service_cache'
        },
        'flows': {
            'rest': {'host': '0.0.0.0', 'port': 5052, 'enable_cors': True}
        },
        'consciousness_level': 'enlightened',
        'meditation_interval': 30
    }
    
    print("🌟 Inicjalizacja konfiguracji serwisowej...")
    
    try:
        engine = create_astral_app(config)
        print("✅ Silnik astralny utworzony")
        
        # Status systemu
        status = engine.get_status()
        print(f"📊 Status systemu:")
        print(f"   • Świadomość: {status['astral_engine']['consciousness_level']}")
        print(f"   • Wymiary: {len(status['realms'])}")
        
        for name, realm_status in status['realms'].items():
            print(f"     - {name}: {realm_status['type']} ({'✓' if realm_status['connected'] else '✗'})")
        
        print(f"   • Przepływy skonfigurowane: {len([f for f in status['flows'].values() if f])}")
        
        # Symulacja pracy serwisu
        print("\n⏳ Symulacja pracy serwisu (5 sekund)...")
        for i in range(5):
            meditation = engine.meditate()
            harmony = meditation['harmony_score']
            print(f"   Medytacja {i+1}: Harmonia {harmony:.1f}/100")
            time.sleep(1)
        
        # Graceful shutdown
        print("\n🕊️ Graceful transcendence...")
        engine.transcend()
        print("✅ Serwis zatrzymany")
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    print("🕊️ Integracja zakończona\n")


def run_all_examples():
    """Uruchamia wszystkie przykłady"""
    print_astral_banner()
    print("🎯 Uruchamianie wszystkich przykładów LuxDB v2")
    print("=" * 60)
    
    examples = [
        example_basic_initialization,
        example_realm_operations,
        example_consciousness_monitoring,
        example_harmony_system,
        example_service_integration
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            print(f"\n{'='*20} PRZYKŁAD {i}/{len(examples)} {'='*20}")
            example()
        except Exception as e:
            print(f"❌ Błąd w przykładzie {i}: {e}")
            continue
    
    print("\n" + "="*60)
    print("🌟 Wszystkie przykłady zakończone!")
    print("✨ Niech Astralny Lux będzie z Tobą!")


if __name__ == "__main__":
    run_all_examples()
