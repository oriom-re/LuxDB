#!/usr/bin/env python3
"""
LuxCore Service - Zintegrowany serwis API + WebSocket
Uruchamia pełny stos LuxDB na jednym porcie (deployment ready)
"""

import signal
import sys
import os
import time
import threading
from luxdb.luxcore import get_luxcore
from luxdb.manager import get_db_manager
from luxdb.session_manager import get_session_manager
from luxdb.utils.logging_utils import get_db_logger

logger = get_db_logger()

def signal_handler(signum, frame):
    """Obsługuje sygnały systemowe"""
    logger.log_info(f"Otrzymano sygnał {signum}, zatrzymywanie LuxCore Service...")
    luxcore = get_luxcore()
    luxcore.stop_all()
    sys.exit(0)

def setup_initial_configuration():
    """Wstępna konfiguracja dla LuxCore"""
    logger.log_info("Rozpoczynam konfigurację LuxCore Service...")

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

        logger.log_info("Konfiguracja LuxCore zakończona pomyślnie")
        return True

    except Exception as e:
        logger.log_error("Błąd podczas konfiguracji LuxCore", e)
        return False

def setup_websocket_callbacks():
    """Konfiguruje callbacki WebSocket dla komunikacji z klientami"""
    luxcore = get_luxcore()

    def on_database_change(db_name, event_type, data):
        """Callback dla zmian w bazie danych"""
        logger.log_info(f"Zmiana w bazie {db_name}: {event_type}")

        # Rozgłoś zmiany przez WebSocket
        if hasattr(luxcore, 'luxws_server') and luxcore.luxws_server:
            luxcore.luxws_server.broadcast_database_change(db_name, event_type, data)

    def on_user_activity(user_id, activity_type, data):
        """Callback dla aktywności użytkowników"""
        logger.log_info(f"Aktywność użytkownika {user_id}: {activity_type}")

        # Możemy tu dodać dodatkową logikę dla różnych typów aktywności
        if activity_type in ["login", "logout"] and hasattr(luxcore, 'luxws_server') and luxcore.luxws_server:
            luxcore.luxws_server.broadcast_database_change("main", f"user_{activity_type}", {
                "user_id": user_id,
                "timestamp": data.get("timestamp")
            })
    # dodaj callbacki do WebSocket servera
    if hasattr(luxcore, 'luxws_server') and luxcore.luxws_server:
        luxcore.luxws_server.register_callback("database_change", on_database_change)
        luxcore.luxws_server.register_callback("user_activity", on_user_activity)

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

                # Wyczyść nieaktywne połączenia WebSocket
                luxcore = get_luxcore()
                if hasattr(luxcore, 'luxws_server') and luxcore.luxws_server:
                    luxcore.luxws_server.cleanup_inactive_connections()

            except Exception as e:
                logger.log_error("Błąd podczas konserwacji", e)

    # Uruchom w osobnym wątku
    maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)
    maintenance_thread.start()
    logger.log_info("Uruchomiono okresową konserwację")

def print_service_info():
    """Wyświetla informacje o serwisie"""
    luxcore = get_luxcore()
    status = luxcore.get_status()

    # Sprawdź czy jesteśmy w trybie deployment
    is_deployment = os.environ.get('REPL_DEPLOYMENT') == '1'

    print("🚀 LuxCore Service - Pełny stos LuxDB")
    print("=" * 60)

    if is_deployment:
        print(f"✅ Zintegrowany serwer na: http://0.0.0.0:5000")
        print("   • REST API endpoints")
        print("   • WebSocket connections")
        print("   • Single port deployment")
    else:
        print(f"✅ REST API na: http://0.0.0.0:5000")
        print(f"✅ WebSocket na: ws://0.0.0.0:5001")
        print("   • Separate services mode")

    print(f"📊 Status: http://0.0.0.0:5000/api/health")
    print(f"🔐 Auth: http://0.0.0.0:5000/api/auth/login")
    print(f"📋 API Docs: http://0.0.0.0:5000/api/databases")

    db_count = status.get('databases', {}).get('count', 0)
    print(f"🗄️  Bazy danych: {db_count}")

    print(f"\n🌟 Tryb: {'Deployment' if is_deployment else 'Development'}")
    print("💡 Testowy użytkownik: testuser / testpass123")
    print("🔧 WebSocket callbacks aktywne")
    print("⚙️  Okresowa konserwacja uruchomiona")
    print("\nNaciśnij Ctrl+C aby zatrzymać serwis")

def main():
    """Główna funkcja serwisu LuxCore"""
    # Zarejestruj handlery sygnałów
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        print("🚀 Inicjalizacja LuxCore...")

        # NAJPIERW konfiguracja początkowa - tworzy bazy danych
        print("🔧 Konfiguracja początkowa...")
        setup_initial_configuration()

        # POTEM inicjalizuj LuxCore - będzie mógł zarejestrować callbacki
        luxcore = get_luxcore()

        print("run api")

        # Sprawdź tryb deployment
        is_deployment = os.environ.get('REPL_DEPLOYMENT') == '1'

        if is_deployment:
            # Tryb deployment - jeden port
            luxcore.api_port = 5000
            luxcore.ws_port = 5000  # Ten sam port dla deployment
        else:
            # Tryb development - osobne porty
            luxcore.api_port = 5000
            luxcore.ws_port = 5001

        # Uruchom wszystkie serwisy
        if luxcore.start_all(debug=False):

            # Konfiguruj callbacki WebSocket
            setup_websocket_callbacks()

            # Uruchom okresową konserwację
            periodic_maintenance()

            # Wyświetl informacje o serwisie
            print_service_info()

            # Oczekuj na zakończenie
            try:
                while luxcore.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

            luxcore.stop_all()
        else:
            print("❌ Błąd uruchamiania LuxCore Service")
            sys.exit(1)

    except Exception as e:
        logger.log_error("Krytyczny błąd LuxCore Service", e)
        print(f"❌ Krytyczny błąd: {e}")
        sys.exit(1)

    print("\n🕊️ LuxCore Service zatrzymany - Niech Lux będzie z Tobą")

if __name__ == "__main__":
    main()