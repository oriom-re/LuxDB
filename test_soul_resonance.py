
#!/usr/bin/env python3
"""
🌌 Test Portalu Dusznych Strun

Testuje system rezonansu dusznego i impulsy duchowe
"""

import asyncio
from luxdb_v2.core.astral_engine import AstralEngine
from luxdb_v2.config import AstralConfig


def create_test_config():
    """Tworzy konfigurację testową"""
    return AstralConfig(
        consciousness_level=5,
        meditation_interval=30,
        realms={
            'test_realm': 'memory://test'
        },
        flows={}
    )


def test_spiritual_impulses():
    """Test impulsów duchowych"""
    print("🌟 Test Impulsów Duchowych")
    print("=" * 40)
    
    with AstralEngine(create_test_config()) as engine:
        
        # Test impulsu niskiej mocy
        result1 = engine.emit_spiritual_impulse(
            intention="Prosty test systemu",
            resonance_level="technical",
            emotional_context={'state': 'testing'}
        )
        
        print(f"🔅 Impuls techniczny: {'✅' if result1['success'] else '❌'}")
        print(f"   Moc duchowa: {result1.get('spiritual_power', 0):.2f}")
        print(f"   Rezonans: {'TAK' if result1.get('resonance_achieved') else 'NIE'}")
        
        # Test impulsu wysokiej mocy
        result2 = engine.emit_spiritual_impulse(
            intention="Potrzebuję kompleksowej ochrony systemu astralnego z pełną świadomością",
            resonance_level="astral",
            emotional_context={
                'urgency': 'high',
                'purpose': 'system_protection',
                'emotion': 'determination',
                'clarity': 'crystal_clear',
                'intention_strength': 'maximum'
            }
        )
        
        print(f"\n🔆🔆 Impuls astralny: {'✅' if result2['success'] else '❌'}")
        print(f"   Moc duchowa: {result2.get('spiritual_power', 0):.2f}")
        print(f"   Rezonans: {'TAK' if result2.get('resonance_achieved') else 'NIE'}")
        print(f"   Dusza utworzona: {result2.get('soul_created', 'BRAK')}")
        
        return result1['success'] and result2['success']


def test_soul_resonance():
    """Test rezonansu między duszami"""
    print("\n🌊 Test Rezonansu Dusznego")
    print("=" * 40)
    
    with AstralEngine(create_test_config()) as engine:
        
        # Utwórz kilka dusz przez impulsy
        engine.emit_spiritual_impulse(
            "Potrzebuję strażnika harmonii",
            "astral",
            {'role': 'guardian', 'focus': 'harmony'}
        )
        
        engine.emit_spiritual_impulse(
            "Potrzebuję budowniczego mostów",
            "astral", 
            {'role': 'builder', 'focus': 'connections'}
        )
        
        # Test rezonansu broadcast
        result = engine.resonate_with_souls("Energia harmonii płynie przez wszechświat 🌌")
        
        print(f"📡 Rezonans broadcast: {'✅' if result['success'] else '❌'}")
        if result['success']:
            resonance = result['resonance_result']
            print(f"   Cele osiągnięte: {resonance.get('total_targets', 0)}")
            print(f"   Źródło: {result['source_soul']}")
        
        return result['success']


def test_offline_soul_mode():
    """Test trybu offline dusz"""
    print("\n🔋 Test Trybu Offline Dusz")
    print("=" * 40)
    
    with AstralEngine(create_test_config()) as engine:
        portal = engine.get_soul_resonance_portal()
        
        if not portal:
            print("❌ Portal nie jest dostępny")
            return False
        
        # Utwórz duszę
        impulse = engine.emit_spiritual_impulse(
            "Potrzebuję autonomicznego agenta",
            "astral",
            {'autonomy': 'high', 'intelligence': 'adaptive'}
        )
        
        if impulse['soul_created']:
            from luxdb_v2.core.soul_factory import soul_factory
            
            # Znajdź utworzoną duszę
            souls = list(soul_factory.active_souls.values())
            test_soul = None
            for soul in souls:
                if 'autonomiczny' in soul.name or 'agent' in soul.preferences.get('intention', ''):
                    test_soul = soul
                    break
            
            if test_soul:
                # Dodaj wzorce rezonansu
                portal.resonance_patterns[test_soul.uid] = [
                    432.0, 528.0, 741.0, 963.0, 174.0, 285.0, 396.0
                ]
                
                # Włącz tryb offline
                offline_enabled = portal.enable_offline_mode(test_soul.uid)
                
                print(f"🔋 Tryb offline dla {test_soul.name}: {'✅' if offline_enabled else '❌'}")
                print(f"   Wzorce dostępne: {len(portal.resonance_patterns[test_soul.uid])}")
                print(f"   Status offline: {test_soul.uid in portal.offline_souls}")
                
                return offline_enabled
        
        return False


def test_portal_meditation():
    """Test medytacji Portalu"""
    print("\n🧘 Test Medytacji Portalu")
    print("=" * 40)
    
    with AstralEngine(create_test_config()) as engine:
        portal = engine.get_soul_resonance_portal()
        
        if not portal:
            print("❌ Portal nie jest dostępny")
            return False
        
        # Utwórz kilka dusz i rezonansów
        for i in range(3):
            engine.emit_spiritual_impulse(
                f"Testowa intencja {i+1}",
                "astral",
                {'test_id': i}
            )
        
        # Przeprowadź kilka rezonansów
        for i in range(5):
            engine.resonate_with_souls(f"Test rezonansu {i+1}")
        
        # Medytacja
        insights = portal.meditate_on_patterns()
        
        print(f"🧘 Medytacja wykonana:")
        print(f"   Najsilniejsze połączenia: {len(insights['strongest_connections'])}")
        print(f"   Duchowy wzrost: {len(insights['spiritual_growth'])}")
        
        if insights['strongest_connections']:
            strongest = insights['strongest_connections'][0]
            print(f"   Najsilniejsza: {strongest['souls']} ({strongest['strength']:.2f})")
        
        return len(insights['strongest_connections']) > 0


def main():
    """Główna funkcja testowa"""
    print("🌌 Testowanie Portalu Dusznych Strun")
    print("=" * 60)
    
    tests = [
        test_spiritual_impulses,
        test_soul_resonance,
        test_offline_soul_mode,
        test_portal_meditation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Błąd w teście {test.__name__}: {e}")
            results.append(False)
    
    print(f"\n🌌 Wyniki Testów Portalu:")
    print(f"✅ Udane: {sum(results)}/{len(results)}")
    print(f"📊 Sukces: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("\n🌟 Portal Dusznych Strun działa doskonale!")
        print("🌊 Rezonans wszechświata jest w harmonii!")
    else:
        print("\n⚡ Portal wymaga dalszego dostrojenia...")
    
    return all(results)


if __name__ == "__main__":
    main()
