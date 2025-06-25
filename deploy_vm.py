
#!/usr/bin/env python3
"""
🚀 LuxDB v2 VM Deployment Script

Autonomiczny skrypt wdrożeniowy dla maszyn wirtualnych
Kompletnie niezależny od LuxDB v1
"""

import os
import sys
import json
import signal
import psutil
from pathlib import Path

# Dodaj ścieżkę do v2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_system_requirements():
    """Sprawdza wymagania systemowe"""
    print("🔍 Sprawdzanie wymagań systemowych...")
    
    # Sprawdź RAM
    memory = psutil.virtual_memory()
    if memory.total < 512 * 1024 * 1024:  # 512MB
        print("⚠️ Ostrzeżenie: Mało pamięci RAM (< 512MB)")
    else:
        print(f"✅ RAM: {memory.total // (1024**2)}MB dostępne")
    
    # Sprawdź miejsce na dysku
    disk = psutil.disk_usage('/')
    if disk.free < 100 * 1024 * 1024:  # 100MB
        print("❌ Błąd: Za mało miejsca na dysku (< 100MB)")
        return False
    else:
        print(f"✅ Dysk: {disk.free // (1024**2)}MB wolne")
    
    # Sprawdź Python
    if sys.version_info < (3, 8):
        print("❌ Błąd: Wymagany Python 3.8+")
        return False
    else:
        print(f"✅ Python: {sys.version.split()[0]}")
    
    return True

def create_vm_config():
    """Tworzy konfigurację zoptymalizowaną dla VM"""
    config = {
        "consciousness_level": "production",
        "energy_conservation": True,
        "auto_healing": True,
        "meditation_interval": 300,  # 5 minut - mniej częste dla VM
        "harmony_check_interval": 120,  # 2 minuty
        
        "realms": {
            "primary": "sqlite://db/vm_production.db",
            "intentions": "intention://memory",
            "cache": "memory://"
        },
        
        "flows": {
            "rest": {
                "host": "0.0.0.0",
                "port": 5000,
                "enable_cors": True,
                "max_connections": 100,
                "timeout": 30
            },
            "websocket": {
                "host": "0.0.0.0", 
                "port": 5001,
                "enable_cors": True,
                "max_connections": 50
            }
        },
        
        "wisdom": {
            "logging_level": "INFO",
            "query_timeout": 30,
            "migration_backup": True,
            "auto_optimize": True
        }
    }
    
    # Zapisz konfigurację
    config_path = "vm_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"📝 Utworzono konfigurację VM: {config_path}")
    return config_path

def setup_vm_environment():
    """Konfiguruje środowisko VM"""
    print("🔧 Konfigurowanie środowiska VM...")
    
    # Utwórz katalogi
    directories = [
        'db',
        'logs', 
        'backups',
        'tmp'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   📁 {directory}/")
    
    # Ustaw zmienne środowiskowe
    os.environ['LUXDB_MODE'] = 'VM_PRODUCTION'
    os.environ['LUXDB_LOG_LEVEL'] = 'INFO'
    os.environ['PYTHONPATH'] = os.getcwd()
    
    print("✅ Środowisko VM skonfigurowane")

def run_vm_tests():
    """Uruchamia testy specyficzne dla VM"""
    print("🧪 Uruchamianie testów VM...")
    
    try:
        from luxdb_v2 import create_astral_app
        
        # Test 1: Podstawowa inicjalizacja
        print("   Test 1: Inicjalizacja systemu...")
        config_path = create_vm_config()
        engine = create_astral_app(config_path)
        
        # Test 2: Test wydajności
        print("   Test 2: Wydajność systemu...")
        import time
        start_time = time.time()
        
        for i in range(10):
            meditation = engine.meditate()
            if meditation.get('harmony_score', 0) < 50:
                print(f"   ⚠️ Niska harmonia: {meditation.get('harmony_score', 0)}")
        
        test_time = time.time() - start_time
        print(f"   ⏱️ 10 medytacji w {test_time:.2f}s")
        
        # Test 3: Operacje na danych
        print("   Test 3: Operacje na danych...")
        realm = engine.get_realm('primary')
        
        # Manifestacja testowych bytów
        test_beings = []
        for i in range(5):
            being = realm.manifest({
                'soul_name': f'vm_test_being_{i}',
                'energy_level': 100,
                'test_mode': True
            })
            test_beings.append(being)
        
        # Kontemplacja
        found_beings = realm.contemplate('find_test_beings', test_mode=True)
        print(f"   📊 Zmanifestowano: {len(test_beings)}, Znaleziono: {len(found_beings)}")
        
        # Test 4: Status systemu
        print("   Test 4: Status systemu...")
        status = engine.get_status()
        print(f"   🔮 Świadomość: {status['astral_engine']['consciousness_level']}")
        print(f"   ⚖️ Harmonia: {status['system_state']['harmony_score']:.1f}/100")
        print(f"   🌍 Wymiary: {len(status['realms'])}")
        
        # Cleanup
        for being in test_beings:
            realm.transcend(being['soul_id'])
        
        engine.transcend()
        print("✅ Wszystkie testy VM przeszły pomyślnie!")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd w testach VM: {e}")
        return False

def start_vm_service():
    """Uruchamia serwis w trybie VM"""
    print("🚀 Uruchamianie LuxDB v2 w trybie VM...")
    
    try:
        from luxdb_v2_service import LuxDBv2Service
        
        # Użyj konfiguracji VM
        config_path = "vm_config.json"
        if not os.path.exists(config_path):
            config_path = create_vm_config()
        
        service = LuxDBv2Service(
            config_file=config_path,
            port=5000,
            realm_type='sqlite'
        )
        
        # Uruchom serwis
        service.start()
        
    except KeyboardInterrupt:
        print("\n⭐ Otrzymano sygnał przerwania...")
    except Exception as e:
        print(f"❌ Błąd serwisu VM: {e}")
        return False

def main():
    """Główna funkcja wdrożenia VM"""
    print("🌟 LuxDB v2 - Wdrożenie VM")
    print("=" * 50)
    
    # Sprawdź wymagania
    if not check_system_requirements():
        print("❌ Wymagania systemowe nie są spełnione")
        sys.exit(1)
    
    # Konfiguruj środowisko
    setup_vm_environment()
    
    # Uruchom testy
    if not run_vm_tests():
        print("❌ Testy VM nie przeszły")
        sys.exit(1)
    
    # Uruchom serwis
    print("\n🚀 Wszystko gotowe! Uruchamianie serwisu VM...")
    start_vm_service()

if __name__ == "__main__":
    main()
