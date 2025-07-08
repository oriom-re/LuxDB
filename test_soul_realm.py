
#!/usr/bin/env python3
"""
🕯️ Test SoulRealm - Testuje nowy system dusz w bazie

Testuje:
- Tworzenie wymiaru dusz
- Manifestację dusz jako JSON
- Operacje na duszach (awakening, memory, etc.)
- Integrację z SoulFactory
"""

import asyncio
import os
import json
from datetime import datetime

# Import systemu
from luxdb_v2.core.astral_engine_v3 import AstralEngine
from luxdb_v2.core.soul_factory import soul_factory
from luxdb_v2.realms.soul_realm import SoulRealm


async def test_soul_realm():
    """Test pełnej funkcjonalności SoulRealm"""
    
    print("🕯️ === Test SoulRealm - Dusze w Bazie ===")
    print()
    
    # Inicjalizuj silnik
    engine = AstralEngine()
    await engine.initialize()
    
    # Stwórz wymiar dusz
    print("1. 🏗️ Tworzenie wymiaru dusz...")
    soul_realm = SoulRealm("souls", "sqlite:///db/souls.db", engine)
    connected = soul_realm.connect()
    
    if connected:
        print("✅ SoulRealm połączony pomyślnie")
        
        # Podłącz do fabryki dusz
        soul_factory.set_soul_realm(soul_realm)
        
    else:
        print("❌ Błąd połączenia z SoulRealm")
        return
    
    print()
    
    # Test 1: Tworzenie przykładowych dusz
    print("2. ✨ Manifestacja przykładowych dusz...")
    try:
        created_souls = soul_factory.create_example_souls()
        print(f"✅ Utworzono {len(created_souls)} dusz")
        
        for soul in created_souls:
            print(f"   🕯️ {soul['id']} ({soul['type']}) - {soul['role']}")
    
    except Exception as e:
        print(f"❌ Błąd tworzenia dusz: {e}")
        return
    
    print()
    
    # Test 2: Wyszukiwanie dusz
    print("3. 🔍 Wyszukiwanie dusz...")
    
    # Wszystkie dusze
    all_souls = soul_factory.find_souls_in_realm()
    print(f"📊 Łącznie dusz: {len(all_souls)}")
    
    # Dusze typu observer
    observers = soul_factory.find_souls_in_realm(soul_type="observer")
    print(f"👁️ Observerów: {len(observers)}")
    
    # Dusze z intencją "control"
    controllers = soul_factory.find_souls_in_realm(has_intent="control")
    print(f"🎮 Z intencją 'control': {len(controllers)}")
    
    print()
    
    # Test 3: Operacje na duszach
    print("4. 🎯 Operacje na duszach...")
    
    # Obudź duszę wisdom.core
    awakened = soul_factory.awaken_soul_in_realm("wisdom.core")
    if awakened:
        print("✅ Dusza wisdom.core obudzona")
    
    # Dodaj wspomnienie
    memory_added = soul_factory.add_soul_memory(
        "wisdom.core", 
        "patterns", 
        {"pattern": "test_pattern", "confidence": 0.95}
    )
    if memory_added:
        print("✅ Dodano wspomnienie do wisdom.core")
    
    # Pobierz zaktualizowaną duszę
    updated_soul = soul_factory.get_soul_from_realm("wisdom.core")
    if updated_soul:
        print(f"📋 Status duszy: {updated_soul['status']}")
        print(f"🧠 Wzorców w pamięci: {len(updated_soul['memory']['patterns'])}")
    
    print()
    
    # Test 4: Statystyki
    print("5. 📊 Statystyki wymiaru dusz...")
    stats = soul_realm.get_soul_stats()
    
    print(f"📈 Łącznie dusz: {stats['total_souls']}")
    print(f"⚡ Aktywnych: {stats['active_souls']}")
    print(f"😴 Śpiących: {stats['dormant_souls']}")
    print(f"🎯 Skupionych: {stats['focused_souls']}")
    print(f"🔋 Średnia energia: {stats['avg_energy']}")
    
    print()
    
    # Test 5: Przykład rozszerzonej duszy
    print("6. 🌟 Tworzenie zaawansowanej duszy...")
    
    advanced_soul_data = {
        "id": "chaos.conductor.prime",
        "type": "builder",
        "role": "reality_coordinator",
        "intents": ["orchestrate", "balance", "harmonize", "transcend"],
        "memory": {
            "errors": [],
            "patterns": [
                {"pattern": "chaos_emergence", "strength": 0.9},
                {"pattern": "harmony_restoration", "strength": 0.85}
            ],
            "trusted": ["astra.wisdom.master", "oriom.portal.master"],
            "achievements": [
                {"achievement": "first_paradox_resolution", "timestamp": datetime.now().isoformat()}
            ]
        },
        "sockets": {
            "input": ["chaos_signal", "harmony_request", "reality_shift"],
            "output": ["balance_adjustment", "paradox_resolution", "transcendence_guidance"]
        },
        "energy_level": 150.0,
        "status": "focused"
    }
    
    try:
        advanced_soul = soul_factory.create_soul_in_realm(advanced_soul_data)
        print(f"✅ Zaawansowana dusza utworzona: {advanced_soul['id']}")
        print(f"   🎯 Intencje: {', '.join(advanced_soul['intents'])}")
        print(f"   🔌 Wejścia: {', '.join(advanced_soul['sockets']['input'])}")
        print(f"   📡 Wyjścia: {', '.join(advanced_soul['sockets']['output'])}")
        
    except Exception as e:
        print(f"❌ Błąd tworzenia zaawansowanej duszy: {e}")
    
    print()
    
    # Test 6: Demonstracja komunikacji przez sockets
    print("7. 📡 Demonstracja komunikacji przez sockets...")
    
    # Znajdź dusze które mogą komunikować się ze sobą
    wisdom_soul = soul_factory.get_soul_from_realm("wisdom.core")
    chaos_soul = soul_factory.get_soul_from_realm("chaos.conductor.prime")
    
    if wisdom_soul and chaos_soul:
        # Sprawdź kompatybilność socketów
        wisdom_outputs = wisdom_soul['sockets']['output']
        chaos_inputs = chaos_soul['sockets']['input']
        
        compatible = any(output in chaos_inputs for output in wisdom_outputs)
        print(f"🔗 Kompatybilność socketów wisdom→chaos: {'✅' if compatible else '❌'}")
        
        # Symuluj komunikację
        if 'insight' in wisdom_outputs and 'harmony_request' in chaos_inputs:
            print("💫 Symulacja: wisdom.core wysyła 'insight' do chaos.conductor.prime")
            
            # Dodaj wzorzec komunikacji do pamięci
            soul_factory.add_soul_memory(
                "wisdom.core",
                "patterns",
                {
                    "communication": "insight_to_chaos",
                    "target": "chaos.conductor.prime",
                    "timestamp": datetime.now().isoformat()
                }
            )
            print("✅ Wzorzec komunikacji zapisany w pamięci")
    
    print()
    print("🕯️ === Test SoulRealm zakończony ===")
    
    # Finalne statystyki
    final_stats = soul_realm.get_soul_stats()
    print(f"📊 Finalne statystyki: {final_stats['total_souls']} dusz w wymiarze")


if __name__ == "__main__":
    asyncio.run(test_soul_realm())
