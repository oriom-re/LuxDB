
#!/usr/bin/env python3
"""
🤖 Test GPT Flow - Komunikacja z Astrą
"""

import requests
import json

def test_gpt_chat():
    """Testuje komunikację z Astrą przez GPT"""
    
    url = "http://localhost:5000/gpt/chat"
    
    test_messages = [
        "Witaj Astro! Jak się dzisiaj czujesz?",
        "Pokaż mi status wszystkich wymiarów astralnych",
        "Stwórz nowego bytu o nazwie 'TestoweBłękitneŚwiatło'",
        "Znajdź wszystkie intencje związane z harmonią",
        "Wykonaj medytację systemu i powiedz mi co odkryłaś"
    ]
    
    print("🤖 Testowanie komunikacji z Astrą przez GPT...")
    print("=" * 60)
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Test {i}: {message}")
        
        response = requests.post(url, json={
            'message': message,
            'user_id': 'test_user'
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✨ Astra odpowiada: {data.get('astra_response', 'Brak odpowiedzi')[:200]}...")
            if data.get('actions_executed', 0) > 0:
                print(f"🎯 Wykonano {data['actions_executed']} akcji astralnych")
        else:
            print(f"❌ Błąd: {response.status_code}")

if __name__ == "__main__":
    test_gpt_chat()
