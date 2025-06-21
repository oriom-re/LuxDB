
#!/usr/bin/env python3
"""
LuxAPI Service - Standalone REST API service
Uruchamia tylko REST API na porcie 5000
"""

import signal
import sys
import os
import time
from luxdb.luxapi import get_luxapi
from luxdb.manager import get_db_manager
from luxdb.session_manager import get_session_manager
from luxdb.utils.logging_utils import get_db_logger

logger = get_db_logger()

def signal_handler(signum, frame):
    """Obsługuje sygnały systemowe"""
    logger.log_info(f"Otrzymano sygnał {signum}, zatrzymywanie LuxAPI Service...")
    sys.exit(0)

def setup_initial_configuration():
    """Wstępna konfiguracja dla LuxAPI"""
    logger.log_info("Rozpoczynam konfigurację LuxAPI Service...")
    
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
        
        # Przykładowy użytkownik testowy (tylko do rozwoju)
        try:
            test_user_id = session_manager.create_user(
                username="testuser",
                email="test@luxdb.dev",
                password="testpass123"
            )
            if test_user_id:
                logger.log_info(f"Utworzono użytkownika testowego (ID: {test_user_id})")
        except Exception as e:
            logger.log_info(f"Użytkownik testowy już istnieje: {str(e)}")
        
        logger.log_info("Konfiguracja LuxAPI zakończona pomyślnie")
        return True
        
    except Exception as e:
        logger.log_error("Błąd podczas konfiguracji LuxAPI", e)
        return False

def print_service_info():
    """Wyświetla informacje o serwisie"""
    print("🌟 LuxAPI Service - REST API dla LuxDB")
    print("=" * 50)
    print(f"✅ REST API dostępny na: http://0.0.0.0:5000")
    print(f"📊 Health Check: http://0.0.0.0:5000/api/health")
    print(f"🔐 Auth Login: http://0.0.0.0:5000/api/auth/login")
    print(f"📋 Databases: http://0.0.0.0:5000/api/databases")
    print(f"💡 Testowy użytkownik: testuser / testpass123")
    print("\nNaciśnij Ctrl+C aby zatrzymać serwis")

def main():
    """Główna funkcja serwisu LuxAPI"""
    # Zarejestruj handlery sygnałów
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wstępna konfiguracja
        if not setup_initial_configuration():
            print("❌ Błąd konfiguracji LuxAPI Service")
            sys.exit(1)
        
        # Inicjalizuj i uruchom LuxAPI
        luxapi = get_luxapi()
        luxapi.host = "0.0.0.0"
        luxapi.port = 5000
        
        # Wyświetl informacje o serwisie
        print_service_info()
        
        # Uruchom serwer
        logger.log_info("Uruchamianie LuxAPI Service...")
        luxapi.run(debug=False)
        
    except Exception as e:
        logger.log_error("Krytyczny błąd LuxAPI Service", e)
        print(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)
    
    print("\n🕊️ LuxAPI Service zatrzymany")

if __name__ == "__main__":
    main()
