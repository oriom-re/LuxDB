
#!/usr/bin/env python3
"""
⚡ Szybki test LuxDB v2 - Podstawowe funkcje

Minimalistyczny test sprawdzający czy serwer odpowiada
"""

import requests
import time
import sys


def quick_rest_test(base_url="http://0.0.0.0:5000"):
    """Szybki test REST API"""
    print(f"🌐 Szybki test REST API: {base_url}")
    
    tests = [
        ("Status astralny", "/astral/status", "GET"),
        ("Lista wymiarów", "/realms", "GET"),
        ("Medytacja", "/astral/meditate", "POST")
    ]
    
    passed = 0
    total = len(tests)
    
    for name, endpoint, method in tests:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", timeout=5)
            
            success = 200 <= response.status_code < 300
            print(f"   {'✅' if success else '❌'} {name}: {response.status_code}")
            
            if success:
                passed += 1
                
        except Exception as e:
            print(f"   ❌ {name}: {str(e)}")
    
    print(f"\n📊 Wynik: {passed}/{total} testów przeszło ({passed/total*100:.1f}%)")
    return passed == total


def check_server_health(base_url="http://0.0.0.0:5000"):
    """Sprawdza czy serwer żyje"""
    try:
        response = requests.get(f"{base_url}/astral/status", timeout=3)
        return response.status_code == 200
    except:
        return False


def main():
    """Główna funkcja szybkiego testu"""
    print("⚡ LuxDB v2 - Szybki test")
    print("=" * 40)
    
    # Sprawdź argumenty
    base_url = "http://0.0.0.0:5000"
    if len(sys.argv) > 1:
        if sys.argv[1].startswith("http"):
            base_url = sys.argv[1]
        else:
            # Prawdopodobnie IP
            base_url = f"http://{sys.argv[1]}:5000"
    
    print(f"🎯 Target: {base_url}")
    
    # Sprawdź czy serwer odpowiada
    print("🔍 Sprawdzanie połączenia...")
    if not check_server_health(base_url):
        print("❌ Serwer nie odpowiada!")
        print("💡 Upewnij się, że LuxDB v2 Service jest uruchomiony")
        return
    
    print("✅ Serwer odpowiada!")
    
    # Uruchom szybkie testy
    success = quick_rest_test(base_url)
    
    if success:
        print("\n🎉 Wszystkie testy przeszły pomyślnie!")
    else:
        print("\n⚠️ Niektóre testy nie powiodły się")


if __name__ == "__main__":
    main()
