#!/usr/bin/env python3
"""
🤖 Test GPT Flow - Komunikacja z Astrą
"""

import requests
import json
import time

def test_server_availability(url_base):
    """Sprawdza czy serwer jest dostępny"""
    try:
        response = requests.get(f"{url_base}/astral/status", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_gpt_chat():
    """Testuje komunikację z Astrą przez GPT"""

    # Próbuj różne URL-e dla Replit
    possible_urls = [
        "http://127.0.0.1:5000",
        "http://localhost:5000", 
        "http://0.0.0.0:5000",
        "https://e1998e06-5fd9-4892-9dde-55862809e026-00-1tug2biuoyhvh.spock.replit.dev/"  # Publiczny URL Replit (automatycznie przekieruje na port 5000)
    ]

    url_base = None
    print("🤖 Testowanie komunikacji z Astrą przez GPT...")
    print("=" * 60)

    # Sprawdź który URL działa
    print("🔍 Sprawdzanie dostępności serwera...")
    for test_url in possible_urls:
        print(f"   Próbuję: {test_url}")
        if test_server_availability(test_url):
            url_base = test_url
            print(f"✅ Serwer dostępny na: {url_base}")
            break
        else:
            print(f"   ❌ Niedostępny")

    if not url_base:
        print("❌ Serwer nie jest dostępny na żadnym z portów")
        print("💡 Sprawdź czy Astra jest uruchomiona:")
        print("   - Status workflow 'Start Astra Pure'")
        print("   - Sprawdź logi serwera")
        print("   - Możliwe że serwer startuje - poczekaj chwilę")
        return

    gpt_url = f"{url_base}/gpt/chat"


    test_messages = [
        "Witaj Astro! Jak się dzisiaj czujesz?",
        "Pokaż mi status wszystkich wymiarów astralnych",
        "Stwórz nowego bytu o nazwie 'TestoweBłękitneŚwiatło'",
        "Znajdź wszystkie intencje związane z harmonią",
        "Wykonaj medytację systemu i powiedz mi co odkryłaś"
    ]

    success_count = 0
    total_tests = len(test_messages)

    for i, message in enumerate(test_messages, 1):
        print(f"\n💬 Test {i}/{total_tests}: {message}")

        try:
            response = requests.post(gpt_url, json={
                'message': message,
                'user_id': 'test_user'
            }, timeout=30)

            if response.status_code == 200:
                print(f"✅ Sukces: {response}")
                data = response.json()
                if data.get('success', False):
                    print(f"✨ Astra odpowiada: {data.get('astra_response', 'Brak odpowiedzi')[:200]}...")
                    if data.get('actions_executed', 0) > 0:
                        print(f"🎯 Wykonano {data['actions_executed']} akcji astralnych")
                    success_count += 1
                else:
                    print(f"⚠️ Błąd w odpowiedzi: {data.get('error', 'Nieznany błąd')}")
            else:
                print(f"❌ Błąd HTTP: {response.status_code}")
                if response.text:
                    print(f"   Szczegóły: {response.text[:200]}")

        except requests.exceptions.ConnectionError as e:
            print(f"❌ Błąd połączenia: Serwer niedostępny")
            print(f"   Szczegóły: {str(e)[:150]}...")
            break

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout: Astra potrzebuje więcej czasu na odpowiedź")

        except Exception as e:
            print(f"❌ Nieoczekiwany błąd: {type(e).__name__}: {str(e)[:150]}")

    print("\n" + "=" * 60)
    print(f"📊 Wyniki: {success_count}/{total_tests} testów zakończonych sukcesem")

    if success_count == 0:
        print("💡 Wskazówki:")
        print("   - Sprawdź czy GPT Flow ma skonfigurowany klucz OpenAI API")
        print("   - Sprawdź logi serwera pod kątem błędów")
        print("   - Upewnij się, że Astra jest w pełni przebudzona")

if __name__ == "__main__":
    test_gpt_chat()