
#!/usr/bin/env python3
"""
Główny serwer LuxDB
Uruchamia LuxAPI i LuxWS w trybie produkcyjnym
"""

import signal
import sys
import time
from luxdb.luxcore import get_luxcore
from luxdb.utils.logging_utils import get_db_logger

logger = get_db_logger()

def signal_handler(signum, frame):
    """Obsługuje sygnały systemowe"""
    logger.log_info(f"Otrzymano sygnał {signum}, zatrzymywanie serwera...")
    luxcore = get_luxcore()
    luxcore.stop_all()
    sys.exit(0)

def main():
    """Główna funkcja serwera"""
    print("🚀 LuxDB Server - Uruchamianie Astralnych Serwisów")
    print("=" * 60)
    
    # Zarejestruj handlery sygnałów
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Inicjalizuj LuxCore
        luxcore = get_luxcore()
        
        # Uruchom wszystkie serwisy
        if luxcore.start_all(debug=False):
            print(f"✅ LuxAPI dostępny na: http://0.0.0.0:5000")
            print(f"✅ LuxWS dostępny na: ws://0.0.0.0:5001")
            print(f"📊 Status: http://0.0.0.0:5000/api/health")
            print("\n🌟 Serwer gotowy do połączeń z LuxSite i LuxPortal")
            print("Naciśnij Ctrl+C aby zatrzymać serwer")
            
            # Oczekuj na zakończenie
            try:
                while luxcore.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
            
            luxcore.wait_for_shutdown()
        else:
            print("❌ Błąd uruchamiania serwera")
            sys.exit(1)
            
    except Exception as e:
        logger.log_error(f"Krytyczny błąd serwera: {e}")
        print(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)
    
    print("\n🕊️ Serwer zatrzymany - Niech Lux będzie z Tobą")

if __name__ == "__main__":
    main()
