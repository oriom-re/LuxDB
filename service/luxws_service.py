
#!/usr/bin/env python3
"""
LuxWS Service - Standalone WebSocket service
Uruchamia tylko WebSocket server na porcie 5001
"""

import signal
import sys
import os
import time
import threading
from datetime import timedelta, datetime
from luxdb.luxws_server import get_luxws_server
from luxdb.manager import get_db_manager
from luxdb.session_manager import get_session_manager
from luxdb.utils.logging_utils import get_db_logger

logger = get_db_logger()

def signal_handler(signum, frame):
    """Obsługuje sygnały systemowe"""
    logger.log_info(f"Otrzymano sygnał {signum}, zatrzymywanie LuxWS Service...")
    sys.exit(0)

def setup_initial_configuration():
    """Wstępna konfiguracja dla LuxWS"""
    logger.log_info("Rozpoczynam konfigurację LuxWS Service...")
    
    try:
        # Inicjalizuj menedżer baz danych
        db_manager = get_db_manager()
        
        # Upewnij się że główna baza istnieje
        if "main" not in db_manager.list_databases():
            logger.log_info("Tworzę główną bazę danych...")
            db_manager.create_database("main")
        
        # Inicjalizuj menedżer sesji
        session_manager = get_session_manager("main")
        
        # Wyczyść wygasłe sesje
        cleaned_sessions = session_manager.cleanup_expired_sessions()
        if cleaned_sessions > 0:
            logger.log_info(f"Wyczyszczono {cleaned_sessions} wygasłych sesji")
        
        logger.log_info("Konfiguracja LuxWS zakończona pomyślnie")
        return True
        
    except Exception as e:
        logger.log_error("Błąd podczas konfiguracji LuxWS", e)
        return False

def periodic_maintenance():
    """Okresowe zadania konserwacyjne dla WebSocket"""
    def maintenance_worker():
        while True:
            try:
                # Wyczyść nieaktywne połączenia co 15 minut
                time.sleep(900)  # 15 minut
                
                luxws = get_luxws_server()
                luxws.cleanup_inactive_connections()
                
                # Wyczyść wygasłe sesje co 30 minut
                if time.time() % 1800 < 900:  # Co drugie wywołanie (30 min)
                    session_manager = get_session_manager("main")
                    cleaned = session_manager.cleanup_expired_sessions()
                    if cleaned > 0:
                        logger.log_info(f"Konserwacja WS: wyczyszczono {cleaned} sesji")
                
            except Exception as e:
                logger.log_error("Błąd podczas konserwacji WS", e)
    
    # Uruchom w osobnym wątku
    maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)
    maintenance_thread.start()
    logger.log_info("Uruchomiono okresową konserwację WS")

def print_service_info():
    """Wyświetla informacje o serwisie"""
    luxws = get_luxws_server()
    stats = luxws.get_connection_stats()
    
    print("🔗 LuxWS Service - WebSocket Server dla LuxDB")
    print("=" * 50)
    print(f"✅ WebSocket dostępny na: ws://0.0.0.0:5001")
    print(f"📊 Aktywne połączenia: {stats.get('total_connections', 0)}")
    print(f"🔐 Uwierzytelnione: {stats.get('authenticated_connections', 0)}")
    print(f"🏠 Pokoje baz danych: {stats.get('database_rooms', 0)}")
    print(f"💾 Dostępne bazy: {', '.join(stats.get('active_databases', []))}")
    print("\nFunkcjonalności WebSocket:")
    print("  • Real-time synchronizacja danych")
    print("  • Pokoje dla różnych baz danych")
    print("  • Dwukierunkowa komunikacja")
    print("  • Automatyczne heartbeat")
    print("\nNaciśnij Ctrl+C aby zatrzymać serwis")

def main():
    """Główna funkcja serwisu LuxWS"""
    # Zarejestruj handlery sygnałów
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wstępna konfiguracja
        if not setup_initial_configuration():
            print("❌ Błąd konfiguracji LuxWS Service")
            sys.exit(1)
        
        # Inicjalizuj LuxWS Server
        luxws = get_luxws_server()
        luxws.host = "0.0.0.0"
        luxws.port = 5001
        
        # Uruchom okresową konserwację
        periodic_maintenance()
        
        # Wyświetl informacje o serwisie
        print_service_info()
        
        # Uruchom serwer WebSocket
        logger.log_info("Uruchamianie LuxWS Service...")
        luxws.run(debug=False)
        
    except Exception as e:
        logger.log_error("Krytyczny błąd LuxWS Service", e)
        print(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)
    
    print("\n🕊️ LuxWS Service zatrzymany")

if __name__ == "__main__":
    main()
