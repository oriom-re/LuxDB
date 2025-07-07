
#!/usr/bin/env python3
"""
🔍 Prosty test do debugowania problemów
"""

import sys
import os
import subprocess
import time

def test_imports():
    """Test importów"""
    print("🔍 Test importów...")
    try:
        from luxdb_v2 import AstralConfig
        print("✅ AstralConfig zaimportowany")
        
        from luxdb_v2.core.astral_engine_v3 import AstralEngineV3
        print("✅ AstralEngineV3 zaimportowany")
        
        from luxdb_v2.core.luxbus_core import LuxBusCore
        print("✅ LuxBusCore zaimportowany")
        
        return True
    except Exception as e:
        print(f"❌ Błąd importu: {e}")
        return False

def test_basic_creation():
    """Test podstawowego tworzenia obiektów"""
    print("\n🔍 Test tworzenia obiektów...")
    try:
        from luxdb_v2 import AstralConfig
        from luxdb_v2.core.astral_engine_v3 import AstralEngineV3
        
        config = AstralConfig()
        print("✅ AstralConfig utworzony")
        
        engine = AstralEngineV3(config)
        print("✅ AstralEngineV3 utworzony")
        
        return True
    except Exception as e:
        print(f"❌ Błąd tworzenia: {e}")
        return False

def test_start_script():
    """Test czy start_astra_pure.py istnieje"""
    print("\n🔍 Test start_astra_pure.py...")
    
    if os.path.exists("start_astra_pure.py"):
        print("✅ start_astra_pure.py istnieje")
        
        # Sprawdź czy można uruchomić
        try:
            result = subprocess.run([sys.executable, "-c", "import start_astra_pure"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ start_astra_pure.py można zaimportować")
                return True
            else:
                print(f"❌ Błąd importu start_astra_pure: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print("⏱️ Import start_astra_pure timeout")
            return False
        except Exception as e:
            print(f"❌ Błąd testu start_astra_pure: {e}")
            return False
    else:
        print("❌ start_astra_pure.py nie istnieje")
        return False

def main():
    """Główna funkcja testowa"""
    print("🧪 Prosty test diagnostyczny LuxDB v2")
    print("=" * 50)
    
    tests = [
        ("Testy importów", test_imports),
        ("Test tworzenia obiektów", test_basic_creation),
        ("Test start script", test_start_script),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Wyjątek w teście '{name}': {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 Wyniki: {passed} zaliczone, {failed} niezaliczone")
    
    if failed == 0:
        print("🎉 Wszystkie testy przeszły!")
        return True
    else:
        print("⚠️ Niektóre testy nie przeszły")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
