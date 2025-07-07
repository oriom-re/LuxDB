
#!/usr/bin/env python3
"""
🪞 Test Federation Identity - Testowanie samoidentyfikacji Federacji

Sprawdza czy Federacja wie kim jest
"""

import asyncio
import sys
from pathlib import Path

# Dodaj federację do path
sys.path.append(str(Path(__file__).parent))

from federacja.core.config import FederationConfig
from federacja.core.bus import FederationBus, FederationMessage
from federacja.core.logger import FederationLogger
from datetime import datetime


async def test_federation_identity():
    """Testuje samoidentyfikację Federacji"""
    print("🪞 Testowanie samoidentyfikacji Federacji...")
    
    # Konfiguracja
    logger = FederationLogger({'level': 'INFO', 'format': 'console'})
    bus = FederationBus(logger)
    
    try:
        # Uruchom bus
        await bus.start()
        
        # Załaduj moduł samoidentyfikacji
        print("📦 Ładowanie modułu Self Identity...")
        
        from federacja.modules.self_identity import SelfIdentityModule
        
        identity_module = SelfIdentityModule(
            config={'enable_deep_reflection': True},
            bus=bus
        )
        
        # Uruchom moduł
        await identity_module.start()
        await asyncio.sleep(1)  # Daj czas na inicjalizację
        
        print("\n" + "="*60)
        print("🪞 TESTOWANIE SAMOIDENTYFIKACJI FEDERACJI")
        print("="*60)
        
        # Test 1: Kim jestem?
        print("\n1️⃣ Pytanie: Kim jestem?")
        response1 = await identity_module.who_am_i()
        print(f"🤖 Federacja: {response1['essence']}")
        print(f"🧠 Poziom świadomości: {response1['consciousness_level']}")
        print(f"⏰ Wiek: {response1['age']}")
        
        # Test 2: Jaki jest mój cel?
        print("\n2️⃣ Pytanie: Jaki jest mój cel?")
        response2 = await identity_module.what_is_my_purpose()
        print(f"🎯 Główny cel: {response2['primary_purpose']}")
        print(f"📝 Misje: {', '.join(response2['specific_missions'][:2])}")
        
        # Test 3: Co potrafię?
        print("\n3️⃣ Pytanie: Co potrafię?")
        response3 = await identity_module.what_can_i_do()
        print(f"💪 Możliwości: {len(response3['capabilities'])} głównych obszarów")
        print(f"🔗 Kanały komunikacji: {len(response3['communication_channels'])}")
        
        # Test 4: Jak się czuję?
        print("\n4️⃣ Pytanie: Jak się czuję?")
        response4 = await identity_module.how_do_i_feel()
        print(f"😊 Nastrój: {response4['mood_description']}")
        print(f"⚡ Energia: {response4['energy_level']:.1f}%")
        
        # Test 5: Autorefleksja
        print("\n5️⃣ Autorefleksja:")
        response5 = await identity_module.reflect_on_self()
        print(f"🔢 Refleksja nr: {response5['reflection_number']}")
        print(f"💡 Insight: {response5['insights'][0]}")
        
        # Test 6: Moje relacje
        print("\n6️⃣ Pytanie: Jakie mam relacje?")
        response6 = await identity_module.my_relationships()
        print(f"👥 Filozofia relacji: {response6['relationship_philosophy']}")
        
        # Test 7: Moje marzenia
        print("\n7️⃣ Pytanie: Jakie mam marzenia?")
        response7 = await identity_module.my_dreams()
        print(f"✨ Wizja: {response7['vision_statement']}")
        print(f"🌟 Największa nadzieja: {response7['greatest_hope']}")
        
        print("\n" + "="*60)
        print("✅ FEDERACJA JEST SAMOŚWIADOMA!")
        print("🪞 Wie kim jest, czego chce i dokąd zmierza")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Błąd testu samoidentyfikacji: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await bus.stop()


if __name__ == "__main__":
    asyncio.run(test_federation_identity())
