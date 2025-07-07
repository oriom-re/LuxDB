
#!/usr/bin/env python3
"""
🎯 Test Systemu Intencji - Eksperymentalne manifestacje
"""

import requests
import json
import time

def test_intention_system():
    """Testuje system intencji"""
    
    base_url = "http://localhost:5000"
    
    # Testowe intencje do zmanifestowania
    test_intentions = [
        {
            'essence': {
                'name': 'CrystallClearVision',
                'purpose': 'Zwiększenie jasności mentalnej',
                'category': 'mind_enhancement'
            },
            'material': {
                'focus_level': 95,
                'clarity_boost': True,
                'meditation_depth': 'deep'
            }
        },
        {
            'essence': {
                'name': 'DigitalHarmonyFlow',
                'purpose': 'Optymalizacja przepływów danych',
                'category': 'system_optimization'
            },
            'material': {
                'bandwidth_optimization': True,
                'latency_reduction': 40,
                'error_tolerance': 0.01
            }
        },
        {
            'essence': {
                'name': 'CreativeEnergyBoost',
                'purpose': 'Wzmocnienie kreatywności systemu',
                'category': 'creativity'
            },
            'material': {
                'inspiration_level': 85,
                'innovation_factor': 1.5,
                'artistic_expression': True
            }
        }
    ]
    
    print("🎯 Testowanie Systemu Manifestacji Intencji")
    print("=" * 60)
    
    manifested_intentions = []
    
    # Manifestuj intencje
    for i, intention_data in enumerate(test_intentions, 1):
        print(f"\n🌟 Manifestowanie intencji {i}: {intention_data['essence']['name']}")
        
        response = requests.post(f"{base_url}/astral/manifest", json=intention_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                being_id = result.get('being_id')
                manifested_intentions.append(being_id)
                print(f"   ✨ Zmanifestowano: {being_id}")
            else:
                print(f"   ❌ Błąd manifestacji: {result.get('error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
    
    # Sprawdź status wymiarów
    print(f"\n📊 Sprawdzanie stanu wymiarów...")
    response = requests.get(f"{base_url}/realms")
    if response.status_code == 200:
        realms = response.json()
        for realm_name, realm_info in realms.items():
            print(f"   🌍 {realm_name}: {realm_info.get('beings_count', '?')} bytów")
    
    # Test kontemplacji
    print(f"\n🧘 Kontemplacja zmanifestowanych intencji...")
    for realm in ['intentions', 'astral_prime']:
        response = requests.post(f"{base_url}/realms/{realm}/contemplate", json={
            'operation': 'find_all'
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                found = result.get('found', 0)
                print(f"   🔍 W {realm}: znaleziono {found} bytów")

if __name__ == "__main__":
    test_intention_system()
