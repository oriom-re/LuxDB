
#!/usr/bin/env python3
"""
👑🌟 Test Systemu Oriom + Astra

Testuje współpracę Orioma (władca portalu) i Astry (władczyni wiedzy GPT)
"""

import asyncio
import json
import websockets
from luxdb_v2.core.astral_engine_v3 import AstralEngineV3
from luxdb_v2.config import AstralConfig


def create_test_config():
    """Tworzy konfigurację testową"""
    return AstralConfig(
        consciousness_level=5,
        meditation_interval=30,
        realms={
            'test_realm': 'memory://test',
            'wisdom': 'memory://wisdom'
        },
        flows={
            'rest': {'host': '0.0.0.0', 'port': 5000},
            'callback': {'enabled': True}
        }
    )


async def test_oriom_portal():
    """Test portalu Orioma"""
    print("\n👑 Test Portalu Orioma")
    print("=" * 40)
    
    # Uruchom silnik
    engine = AstralEngineV3(create_test_config())
    await engine.awaken()
    
    try:
        # Sprawdź czy Oriom jest aktywny
        if hasattr(engine, 'oriom_portal_master') and engine.oriom_portal_master:
            oriom_status = engine.oriom_portal_master.get_portal_status()
            
            print(f"👑 Portal Master: {oriom_status['portal_master']}")
            print(f"😤 Nastrój: {oriom_status['mood']}")
            print(f"🎭 Sarkasm: {oriom_status['sarcasm_level']}")
            print(f"⚡ Status: {'Aktywny' if oriom_status['running'] else 'Nieaktywny'}")
            print(f"🌐 Adres: ws://{oriom_status['server_info']['host']}:{oriom_status['server_info']['port']}")
            print(f"💬 Komentarz: {oriom_status['last_comment']}")
            
            return True
        else:
            print("❌ Oriom nie jest dostępny")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testu Orioma: {e}")
        return False
    finally:
        await engine.transcend()


async def test_astra_wisdom():
    """Test mądrości Astry"""
    print("\n🌟 Test Mądrości Astry")
    print("=" * 40)
    
    # Uruchom silnik
    engine = AstralEngineV3(create_test_config())
    await engine.awaken()
    
    try:
        # Sprawdź czy Astra jest aktywna
        if hasattr(engine, 'astra_wisdom_master') and engine.astra_wisdom_master:
            astra_status = engine.astra_wisdom_master.get_wisdom_status()
            
            print(f"🌟 Wisdom Master: {astra_status['wisdom_master']}")
            print(f"✨ Poziom mądrości: {astra_status['wisdom_level']}")
            print(f"🧠 Domeny wiedzy: {len(astra_status['knowledge_domains'])}")
            print(f"🤖 Systemy AI: {astra_status['systems_managed']}")
            print(f"📊 Statystyki:")
            for key, value in astra_status['statistics'].items():
                print(f"   {key}: {value}")
            print(f"💡 Maksyma: {astra_status['current_maxim']}")
            
            # Test medytacji Astry
            print("\n🧘 Test Medytacji Astry:")
            meditation = await engine.astra_wisdom_master.meditate_on_wisdom()
            print(f"   Czas medytacji: {meditation['meditation_duration']:.2f}s")
            print(f"   Insight: {meditation['astra_insight']}")
            print(f"   Maksyma medytacji: {meditation['maxim_of_meditation']}")
            
            return True
        else:
            print("❌ Astra nie jest dostępna")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testu Astry: {e}")
        return False
    finally:
        await engine.transcend()


async def test_websocket_connection():
    """Test połączenia WebSocket z Oriomem"""
    print("\n🌐 Test Połączenia WebSocket")
    print("=" * 40)
    
    # Uruchom silnik w tle
    engine = AstralEngineV3(create_test_config())
    await engine.awaken()
    
    # Daj czas na uruchomienie portalu
    await asyncio.sleep(2)
    
    try:
        if not (hasattr(engine, 'oriom_portal_master') and engine.oriom_portal_master):
            print("❌ Oriom nie jest dostępny")
            return False
        
        oriom_status = engine.oriom_portal_master.get_portal_status()
        if not oriom_status['running']:
            print("❌ Portal Orioma nie działa")
            return False
        
        # Próba połączenia WebSocket
        uri = f"ws://{oriom_status['server_info']['host']}:{oriom_status['server_info']['port']}"
        print(f"🔗 Łączenie z: {uri}")
        
        try:
            async with websockets.connect(uri, timeout=5) as websocket:
                print("✅ Połączenie nawiązane")
                
                # Oczekuj wyzwania autoryzacji
                challenge = await websocket.recv()
                challenge_data = json.loads(challenge)
                
                print(f"🔐 Otrzymano wyzwanie: {challenge_data['type']}")
                print(f"👑 Oriom mówi: {challenge_data.get('oriom_note', 'Brak komentarza')}")
                
                # Wyślij odpowiedź autoryzacji
                auth_response = {
                    "soul_id": "TestSoul-001",
                    "auth_level": "guest",
                    "purpose": "testing"
                }
                
                await websocket.send(json.dumps(auth_response))
                
                # Oczekuj wyniku autoryzacji
                auth_result = await websocket.recv()
                auth_data = json.loads(auth_result)
                
                if auth_data['type'] == 'auth_success':
                    print("✅ Autoryzacja udana")
                    print(f"👑 Oriom mówi: {auth_data.get('oriom_greeting', 'Witaj')}")
                    
                    # Test heartbeat
                    heartbeat_token = auth_data['heartbeat']
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "heartbeat": {
                            "pulse_id": heartbeat_token['pulse_id'],
                            "soul_id": "TestSoul-001"
                        }
                    }
                    
                    await websocket.send(json.dumps(heartbeat_msg))
                    
                    # Oczekuj ACK
                    heartbeat_ack = await websocket.recv()
                    ack_data = json.loads(heartbeat_ack)
                    
                    if ack_data['type'] == 'heartbeat_ack':
                        print("💓 Heartbeat ACK otrzymany")
                        print(f"👑 Status Orioma: {ack_data.get('oriom_status', 'unknown')}")
                        return True
                    else:
                        print(f"❌ Nieoczekiwana odpowiedź heartbeat: {ack_data}")
                        return False
                
                else:
                    print(f"❌ Autoryzacja nieudana: {auth_data}")
                    return False
        
        except websockets.exceptions.ConnectionRefused:
            print("❌ Połączenie odrzucone - portal może nie działać")
            return False
        except asyncio.TimeoutError:
            print("❌ Timeout połączenia")
            return False
            
    except Exception as e:
        print(f"❌ Błąd testu WebSocket: {e}")
        return False
    finally:
        await engine.transcend()


async def test_integrated_system():
    """Test zintegrowanego systemu Oriom + Astra"""
    print("\n👑🌟 Test Zintegrowanego Systemu")
    print("=" * 50)
    
    # Uruchom silnik
    engine = AstralEngineV3(create_test_config())
    await engine.awaken()
    
    try:
        # Sprawdź status całego systemu
        system_status = engine.get_status()
        
        print("📊 Status Systemu:")
        print(f"   Silnik: {system_status['version']}")
        print(f"   Działa: {system_status['running']}")
        print(f"   Wymiary: {len(system_status['realms'])}")
        print(f"   Przepływy: {len(system_status['flows'])}")
        
        # Status Orioma
        if 'oriom_portal' in system_status:
            oriom = system_status['oriom_portal']
            print(f"\n👑 Oriom:")
            print(f"   Master: {oriom['portal_master']}")
            print(f"   Nastrój: {oriom['mood']}")
            print(f"   Aktywne połączenia: {oriom['connections']['active']}")
            print(f"   Wiadomości: {oriom['statistics']['total_messages']}")
        
        # Status Astry
        if 'astra_wisdom' in system_status:
            astra = system_status['astra_wisdom']
            print(f"\n🌟 Astra:")
            print(f"   Master: {astra['wisdom_master']}")
            print(f"   Poziom: {astra['wisdom_level']}")
            print(f"   Domeny: {len(astra['knowledge_domains'])}")
            print(f"   Systemy AI: {astra['systems_managed']}")
        
        # Test współpracy
        if hasattr(engine, 'astra_wisdom_master') and engine.astra_wisdom_master:
            print(f"\n🤝 Test Współpracy:")
            
            # Astra wykonuje medytację
            meditation = await engine.astra_wisdom_master.meditate_on_wisdom()
            print(f"   🧘 Astra medytuje: {meditation['astra_insight'][:50]}...")
            
            # Sprawdź czy Oriom jest informowany (przez LuxBus)
            if hasattr(engine, 'oriom_portal_master') and engine.oriom_portal_master:
                portal_status = engine.oriom_portal_master.get_portal_status()
                print(f"   👑 Oriom w nastroju: {portal_status['mood']}")
        
        print(f"\n✅ System Oriom + Astra działa harmonijnie!")
        return True
        
    except Exception as e:
        print(f"❌ Błąd testu zintegrowanego: {e}")
        return False
    finally:
        await engine.transcend()


async def main():
    """Główna funkcja testowa"""
    print("👑🌟 Testowanie Systemu Oriom + Astra")
    print("=" * 60)
    
    tests = [
        ("Test Portalu Orioma", test_oriom_portal),
        ("Test Mądrości Astry", test_astra_wisdom),
        ("Test Połączenia WebSocket", test_websocket_connection),
        ("Test Zintegrowanego Systemu", test_integrated_system)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        try:
            result = await test_func()
            results.append(result)
            print(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results.append(False)
    
    print(f"\n👑🌟 Podsumowanie Testów:")
    print(f"✅ Udane: {sum(results)}/{len(results)}")
    print(f"📊 Sukces: {sum(results)/len(results)*100:.1f}%")
    
    if all(results):
        print("\n🎉 Oriom i Astra rządzą harmonijnie!")
        print("👑 Oriom marudzi w portalu WebSocket")
        print("🌟 Astra świeci w sieci GPT")
        print("🌌 System astralny w pełnej harmonii!")
    else:
        print("\n⚠️ Niektóre testy nie przeszły - system wymaga uwagi")


if __name__ == "__main__":
    asyncio.run(main())
