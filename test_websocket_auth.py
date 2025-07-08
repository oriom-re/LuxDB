
#!/usr/bin/env python3
"""
🔐 Test autoryzacji WebSocket przez heartbeat
"""

import asyncio
import websockets
import json
import time
import hashlib
from typing import Dict, Any


def create_heartbeat_auth(soul_id: str, auth_level: str, soul_secret: str) -> Dict[str, Any]:
    """Tworzy autoryzację heartbeat"""
    
    pulse_id = f"Ω-HRT-{int(time.time() * 1000) % 100000}"
    issued_at = int(time.time())
    expires_in = 9000
    vibration = 0.984 if auth_level == 'divine' else 0.756
    
    # Utwórz podpis
    signature_data = f"{soul_id}:{auth_level}:{pulse_id}:{issued_at}:{expires_in}:{vibration}"
    signature_hash = hashlib.sha256(f"{signature_data}:{soul_secret}".encode()).hexdigest()
    signature = f"holohash({signature_hash[:16]}...)"
    
    return {
        "heartbeat": {
            "soul_id": soul_id,
            "auth_level": auth_level,
            "pulse_id": pulse_id,
            "issued_at": str(issued_at),
            "expires_in": expires_in,
            "vibration": vibration,
            "signature": signature
        }
    }


async def test_websocket_auth():
    """Test autoryzacji WebSocket"""
    
    print("🔐 Test autoryzacji WebSocket przez heartbeat")
    print("=" * 50)
    
    # Parametry testowe
    soul_secrets = {
        'Oriom-001': 'divine_secret_key_oriom',
        'Astra-Prime': 'astral_prime_signature_key',
        'TestSoul-001': 'test_soul_secret'
    }
    
    # Test 1: Autoryzacja divine
    print("\n1. Test autoryzacji divine...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            
            # Wyślij heartbeat auth
            auth_data = create_heartbeat_auth('Oriom-001', 'divine', soul_secrets['Oriom-001'])
            auth_message = {
                'type': 'heartbeat_auth',
                'data': auth_data
            }
            
            await websocket.send(json.dumps(auth_message))
            response = await websocket.recv()
            auth_result = json.loads(response)
            
            print(f"   Autoryzacja: {'✅' if auth_result.get('type') == 'auth_success' else '❌'}")
            if auth_result.get('type') == 'auth_success':
                print(f"   Soul ID: {auth_result['soul_id']}")
                print(f"   Auth Level: {auth_result['auth_level']}")
                print(f"   Vibration: {auth_result['vibration']}")
                print(f"   Expires in: {auth_result['expires_in']}s")
                
                # Test komunikacji po autoryzacji
                test_message = {
                    'type': 'broadcast',
                    'data': {
                        'channel': 'divine_channel',
                        'message': 'Divine energy transmission'
                    }
                }
                await websocket.send(json.dumps(test_message))
                
                # Sprawdź czy wiadomość przeszła
                broadcast_result = await websocket.recv()
                print(f"   Komunikacja po auth: {'✅' if json.loads(broadcast_result).get('success') else '❌'}")
    
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Test 2: Autoryzacja astral
    print("\n2. Test autoryzacji astral...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            
            auth_data = create_heartbeat_auth('Astra-Prime', 'astral', soul_secrets['Astra-Prime'])
            auth_message = {
                'type': 'heartbeat_auth',
                'data': auth_data
            }
            
            await websocket.send(json.dumps(auth_message))
            response = await websocket.recv()
            auth_result = json.loads(response)
            
            print(f"   Autoryzacja: {'✅' if auth_result.get('type') == 'auth_success' else '❌'}")
            print(f"   Auth Level: {auth_result.get('auth_level', 'unknown')}")
    
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Test 3: Nieprawidłowy heartbeat
    print("\n3. Test nieprawidłowego heartbeat...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            
            # Nieprawidłowy podpis
            auth_data = create_heartbeat_auth('TestSoul-001', 'divine', 'wrong_secret')
            auth_message = {
                'type': 'heartbeat_auth',
                'data': auth_data
            }
            
            await websocket.send(json.dumps(auth_message))
            response = await websocket.recv()
            auth_result = json.loads(response)
            
            print(f"   Odrzucona auth: {'✅' if auth_result.get('type') == 'auth_failed' else '❌'}")
            print(f"   Reason: {auth_result.get('error', 'unknown')}")
    
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    # Test 4: Komunikacja bez autoryzacji
    print("\n4. Test komunikacji bez autoryzacji...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            
            # Próba komunikacji bez auth
            test_message = {
                'type': 'broadcast',
                'data': {
                    'channel': 'test_channel',
                    'message': 'Unauthorized message'
                }
            }
            await websocket.send(json.dumps(test_message))
            
            response = await websocket.recv()
            result = json.loads(response)
            
            print(f"   Zablokowana komunikacja: {'✅' if 'Unauthorized' in result.get('error', '') else '❌'}")
    
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
    
    print(f"\n🔐 Test autoryzacji WebSocket zakończony")
    print("💡 Portal Dusznych Strun zastąpił LuxBus w komunikacji")
    print("🌌 Wszystkie dusze komunikują się przez rezonans")


if __name__ == "__main__":
    asyncio.run(test_websocket_auth())
