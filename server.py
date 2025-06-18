
#!/usr/bin/env python3
"""
Główny serwer LuxDB z wstępną konfiguracją sesji
Uruchamia LuxAPI i LuxWS w trybie produkcyjnym z obsługą komunikacji klientów
"""

import signal
import sys
import time
import threading
from luxdb.luxcore import get_luxcore
from luxdb.session_manager import get_session_manager
from luxdb.manager import get_db_manager
from luxdb.utils.logging_utils import get_db_logger

logger = get_db_logger()

def signal_handler(signum, frame):
    """Obsługuje sygnały systemowe"""
    logger.log_info(f"Otrzymano sygnał {signum}, zatrzymywanie serwera...")
    luxcore = get_luxcore()
    luxcore.stop_all()
    sys.exit(0)

def setup_initial_configuration():
    """Wstępna konfiguracja serwera i baz danych"""
    logger.log_info("Rozpoczynam wstępną konfigurację LuxCore...")
    
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
            logger.log_info(f"Użytkownik testowy już istnieje lub błąd: {str(e)}")
            # Continue without raising exception - this is not critical for server startup
        
        logger.log_info("Wstępna konfiguracja zakończona pomyślnie")
        return True
        
    except Exception as e:
        logger.log_error("Błąd podczas wstępnej konfiguracji", e)
        return False

def setup_websocket_callbacks():
    """Konfiguruje callbacki WebSocket dla komunikacji z klientami"""
    luxcore = get_luxcore()
    
    def on_database_change(db_name, event_type, data):
        """Callback dla zmian w bazie danych"""
        logger.log_info(f"Zmiana w bazie {db_name}: {event_type}")
        
        # Rozgłoś zmiany przez WebSocket
        luxcore.broadcast_database_event(db_name, event_type, data)
    
    def on_user_activity(user_id, activity_type, data):
        """Callback dla aktywności użytkowników"""
        logger.log_info(f"Aktywność użytkownika {user_id}: {activity_type}")
        
        # Możemy tu dodać dodatkową logikę dla różnych typów aktywności
        if activity_type == "login":
            luxcore.broadcast_database_event("main", "user_login", {
                "user_id": user_id,
                "timestamp": data.get("timestamp")
            })
        elif activity_type == "logout":
            luxcore.broadcast_database_event("main", "user_logout", {
                "user_id": user_id,
                "timestamp": data.get("timestamp")
            })
    
    # Zarejestruj callbacki (w przyszłości można rozbudować o system eventów)
    logger.log_info("Callbacki WebSocket skonfigurowane")

def periodic_maintenance():
    """Okresowe zadania konserwacyjne"""
    def maintenance_worker():
        while True:
            try:
                # Wyczyść wygasłe sesje co 30 minut
                time.sleep(1800)  # 30 minut
                
                session_manager = get_session_manager("main")
                cleaned = session_manager.cleanup_expired_sessions()
                
                if cleaned > 0:
                    logger.log_info(f"Konserwacja: wyczyszczono {cleaned} wygasłych sesji")
                
            except Exception as e:
                logger.log_error("Błąd podczas konserwacji", e)
    
    # Uruchom w osobnym wątku
    maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)
    maintenance_thread.start()
    logger.log_info("Uruchomiono okresową konserwację")

def print_server_info():
    """Wyświetla informacje o serwerze"""
    luxcore = get_luxcore()
    status = luxcore.get_status()
    
    print("🚀 LuxDB Server - Uruchamianie Astralnych Serwisów")
    print("=" * 60)
    print(f"✅ LuxAPI dostępny na: http://0.0.0.0:5000")
    print(f"✅ LuxWS dostępny na: ws://0.0.0.0:5001")
    print(f"📊 Status: http://0.0.0.0:5000/api/health")
    print(f"🔐 Auth: http://0.0.0.0:5000/api/auth/login")
    print(f"📋 API Docs: http://0.0.0.0:5000/api/docs")
    
    db_count = status.get('databases', {}).get('count', 0)
    print(f"🗄️  Bazy danych: {db_count}")
    
    print("\n🌟 Serwer gotowy do połączeń z LuxSite i LuxPortal")
    print("💡 Testowy użytkownik: testuser / testpass123")
    print("🔧 WebSocket callbacks skonfigurowane")
    print("⚙️  Okresowa konserwacja uruchomiona")
    print("\nNaciśnij Ctrl+C aby zatrzymać serwer")

def main():
    """Główna funkcja serwera"""
    # Zarejestruj handlery sygnałów
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Wstępna konfiguracja
        if not setup_initial_configuration():
            print("❌ Błąd wstępnej konfiguracji")
            sys.exit(1)
        
        # Inicjalizuj LuxCore z poprawną konfiguracją portów
        luxcore = get_luxcore()
        luxcore.api_port = 5000
        luxcore.ws_port = 5001
        
        # Uruchom wszystkie serwisy
        if luxcore.start_all(debug=False):
            
            # Konfiguruj callbacki WebSocket
            setup_websocket_callbacks()
            
            # Uruchom okresową konserwację
            periodic_maintenance()
            
            # Wyświetl informacje o serwerze
            print_server_info()
            
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
        logger.log_error("Krytyczny błąd serwera", e)
        print(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)
    
    print("\n🕊️ Serwer zatrzymany - Niech Lux będzie z Tobą")

if __name__ == "__main__":
    main()
