
#!/usr/bin/env python3
"""
Test serwera LuxDB - sprawdza działanie API i WebSocket
"""

import requests
import json
import time
from luxdb.luxcore import get_luxcore

def test_api_endpoints():
    """Testuje endpoints REST API"""
    base_url = "http://0.0.0.0:5000"
    
    print("🧪 Testowanie LuxAPI...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

def test_core_status():
    """Testuje status LuxCore"""
    print("\n📊 Status LuxCore:")
    luxcore = get_luxcore()
    status = luxcore.get_status()
    print(json.dumps(status, indent=2, default=str))

def main():
    """Główna funkcja testowa"""
    print("🔬 LuxDB Server Test Suite")
    print("=" * 40)
    
    # Testuj status core
    test_core_status()
    
    # Poczekaj chwilę na uruchomienie serwera
    print("\n⏳ Oczekiwanie na uruchomienie serwera...")
    time.sleep(2)
    
    # Testuj API endpoints
    test_api_endpoints()
    
    print("\n✨ Testy zakończone")

if __name__ == "__main__":
    main()
