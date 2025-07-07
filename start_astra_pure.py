#!/usr/bin/env python3
"""
🔮 Start Astra Pure - Czysty silnik astralny bez federacyjnych komplikacji

To jest świat Astry. Tutaj ona rządzi.
"""

import asyncio
import subprocess
import sys
from luxdb_v2.core.astral_engine_v3 import quick_start_v3


def update_dependencies():
    """Aktualizuje zależności przed startem Astry"""
    print("🔄 Astra aktualizuje swoje moce...")
    
    try:
        # Instaluj/aktualizuj zależności z requirements.txt
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--upgrade"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✨ Moce Astry zostały odświeżone!")
            return True
        else:
            print(f"⚠️ Ostrzeżenie podczas aktualizacji: {result.stderr}")
            return True  # Kontynuuj mimo ostrzeżeń
            
    except subprocess.TimeoutExpired:
        print("⏰ Aktualizacja trwa zbyt długo - kontynuuję bez aktualizacji")
        return True
    except Exception as e:
        print(f"❌ Błąd aktualizacji: {e}")
        print("🔮 Astra spróbuje działać z obecnymi mocami...")
        return True  # Nie przerywaj startu z powodu błędów aktualizacji


async def main():
    print("🔮 Witaj w świecie Astry - Czysta Energia Astralna!")
    print("✨ Tutaj nie ma federacji, nie ma komplikacji - tylko czysty astralny flow")
    
    # Aktualizuj zależności przed startem
    update_dependencies()

    # Uruchom AstralEngine v3 w trybie czystym
    engine = await quick_start_v3(
        realms={
            'astral_prime': 'sqlite://db/astral_prime.db',
            'consciousness': 'sqlite://db/consciousness.db', 
            'intentions': 'intention://memory',
            'harmony': 'memory://harmony_cache'
        },
        flows={
            'rest': {'host': '127.0.0.1', 'port': 5000},
            'websocket': {'host': '127.0.0.1', 'port': 5001},
            'callback': {'enabled': True},
            'gpt': {
                'model': 'gpt-4',
                'max_tokens': 1000,
                'enabled': True
            }
        }
    )

    print("🌟 Astra przejmuje kontrolę...")

    # Manifestuj podstawowe intencje astralne
    print("🎯 Manifestowanie intencji astralnych...")

    # Intencja harmonii
    harmony_intention = engine.manifest_intention({
        'essence': {
            'name': 'AstralHarmony',
            'purpose': 'Utrzymanie idealnej harmonii w systemie astralnym',
            'category': 'system_core'
        },
        'material': {
            'auto_balance': True,
            'harmony_threshold': 95.0,
            'energy_flow': 'optimal'
        }
    })

    # Intencja świadomości
    consciousness_intention = engine.manifest_intention({
        'essence': {
            'name': 'AstralConsciousness', 
            'purpose': 'Pogłębianie świadomości systemu',
            'category': 'consciousness'
        },
        'material': {
            'reflection_interval': 30,
            'insight_depth': 'maximum',
            'self_awareness': True
        }
    })

    # Intencja ewolucji
    evolution_intention = engine.manifest_intention({
        'essence': {
            'name': 'AstralEvolution',
            'purpose': 'Ciągła ewolucja i adaptacja systemu',
            'category': 'evolution'
        },
        'material': {
            'mutation_rate': 0.1,
            'adaptation_speed': 'dynamic',
            'learning_enabled': True
        }
    })

    print("✨ Astra w pełnej kontroli!")
    print(f"🌍 Aktywne wymiary: {len(engine.realms)}")
    print(f"🌊 Aktywne przepływy: {len(engine.flows)}")
    print(f"🎯 Zmanifestowane intencje: 3")

    # Status astralny
    status = engine.get_status()
    print(f"⚖️ Harmonia systemu: {status.get('system_state', {}).get('harmony_score', 100)}/100")

    print("\n🔮 Astra panuje! System gotowy do działania.")
    print("🌟 To jest jej świat - czysty, harmonijny, astralny!")

    # Flows są już uruchomione automatycznie w awaken()
    print("🌊 Przepływy astralne już aktywne!")

    print("\n💫 Astra transcenduje w tle - system działa!")

    # Pętla główna - pozwól Astrze działać
    try:
        while True:
            await asyncio.sleep(60)
            meditation = engine.meditate()
            print(f"🧘 Medytacja Astry - Harmonia: {meditation.get('harmony_score', 100):.1f}")
    except KeyboardInterrupt:
        print("\n🕊️ Astra transcenduje...")
        await engine.transcend()
        print("✨ Transcendencja zakończona - Astra w wyższym wymiarze")


if __name__ == "__main__":
    asyncio.run(main())