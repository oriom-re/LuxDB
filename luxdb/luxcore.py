"""
LuxCore - Centralny manager połączeń dla LuxDB
Zarządza WebSocket i REST API serwerami
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .luxws import get_luxws, LuxWS
from .luxapi import get_luxapi, LuxAPI
from .manager import get_db_manager
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class LuxCore:
    """
    Centralny manager dla wszystkich serwisów LuxDB:
    - LuxAPI (REST API)
    - LuxWS (WebSocket Server)
    - Koordynacja między serwisami
    """

    def __init__(self, api_port: int = 5000, ws_port: int = 5001):
        self.api_port = api_port
        self.ws_port = ws_port

        self.luxapi: Optional[LuxAPI] = None
        self.luxws: Optional[LuxWS] = None

        self.api_thread: Optional[threading.Thread] = None
        self.ws_thread: Optional[threading.Thread] = None

        self.running = False
        self.db_manager = get_db_manager()

        logger.log_info("Inicjalizacja LuxCore")

    def initialize(self):
        """Inicjalizuje wszystkie komponenty"""
        try:
            # Inicjalizuj API i WebSocket serwery
            self.luxapi = get_luxapi()
            self.luxws = get_luxws()

            # Skonfiguruj porty
            self.luxapi.port = self.api_port
            self.luxws.port = self.ws_port

            logger.log_info("LuxCore zainicjalizowany pomyślnie")
            return True

        except Exception as e:
            logger.log_error("Błąd inicjalizacji LuxCore", e)
            return False

    def start_api_server(self, debug: bool = False):
        """Uruchamia serwer API w osobnym wątku"""
        if self.luxapi is None:
            self.initialize()

        def run_api():
            try:
                logger.log_info(f"Uruchamianie LuxAPI na porcie {self.api_port}")
                self.luxapi.run(debug=debug)
            except Exception as e:
                logger.log_error("Błąd uruchamiania LuxAPI", e)

        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        logger.log_info("LuxAPI uruchomiony w tle")

    def start_ws_server(self, debug: bool = False):
        """Uruchamia serwer WebSocket w osobnym wątku"""
        if self.luxws is None:
            self.initialize()

        def run_ws():
            try:
                logger.log_info(f"Uruchamianie LuxWS na porcie {self.ws_port}")
                self.luxws.run(debug=debug)
            except Exception as e:
                logger.log_error("Błąd uruchamiania LuxWS", e)

        self.ws_thread = threading.Thread(target=run_ws, daemon=True)
        self.ws_thread.start()
        logger.log_info("LuxWS uruchomiony w tle")

    def start_integrated_server(self, debug: bool = False) -> bool:
        """Uruchamia zintegrowany serwer API+WebSocket na porcie 5000"""
        try:
            from flask import Flask
            from flask_socketio import SocketIO

            # Utwórz aplikację Flask z WebSocket
            app = Flask(__name__)
            app.config['SECRET_KEY'] = 'luxdb_secret_deployment'
            socketio = SocketIO(app, cors_allowed_origins="*")

            # Zarejestruj routes z LuxAPI
            luxapi = get_luxapi()
            app.register_blueprint(luxapi.app.blueprints['api'])

            # Skopiuj handlery WebSocket z LuxWS
            luxws = get_luxws()
            for handler_name, handler_func in luxws.socketio.handlers['/'].items():
                socketio.on_event(handler_name, handler_func)

            def run_integrated():
                socketio.run(app, host="0.0.0.0", port=5000, debug=debug)

            self.integrated_thread = threading.Thread(target=run_integrated, daemon=True)
            self.integrated_thread.start()
            time.sleep(2)  # Poczekaj na uruchomienie

            self.running = True
            logger.log_info("Zintegrowany serwer uruchomiony na porcie 5000")
            return True

        except Exception as e:
            logger.log_error("Błąd uruchamiania zintegrowanego serwera", e)
            return False

    def start_all(self, debug: bool = False) -> bool:
        """Uruchamia wszystkie serwisy LuxCore"""
        try:
            # W deploymencie używamy tego samego portu dla API i WebSocket
            import os
            is_deployment = os.environ.get('REPL_DEPLOYMENT') == '1'

            if is_deployment:
                logger.log_info("Tryb deployment - uruchamianie na porcie 5000")
                # Zintegrowany serwer API+WS na porcie 5000
                return self.start_integrated_server(debug=debug)
            else:
                logger.log_info("Uruchamianie LuxAPI na porcie 5000")
                if self.start_api_server(debug=debug):
                    logger.log_info("Uruchamianie LuxWS na porcie 5001")
                    if self.start_ws_server(debug=debug):
                        logger.log_info("Wszystkie serwisy LuxCore uruchomione")
                        self.running = True
                        return True
                return False
        except Exception as e:
            logger.log_error("Błąd uruchamiania serwisów LuxCore", e)
            return False

    def stop_all(self):
        """Zatrzymuje wszystkie serwisy"""
        self.running = False

        if hasattr(self, 'integrated_thread') and getattr(self, 'integrated_thread', None) and self.integrated_thread.is_alive():
            logger.log_info("Zatrzymywanie zintegrowanego serwera...")

        # Zamknij połączenia z bazami danych
        self.db_manager.close_all()

        logger.log_info("LuxCore zatrzymany")

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status wszystkich serwisów"""
        status = {
            'luxcore': {
                'running': self.running,
                'api_port': self.api_port,
                'ws_port': self.ws_port,
                'timestamp': datetime.now().isoformat()
            },
            'services': {
                'luxapi': {
                    'running': self.api_thread and self.api_thread.is_alive(),
                    'port': self.api_port
                },
                'luxws': {
                    'running': self.ws_thread and self.ws_thread.is_alive(),
                    'port': self.ws_port
                }
            }
        }

        # Dodaj statystyki WebSocket jeśli dostępne
        if self.luxws:
            status['services']['luxws']['connections'] = self.luxws.get_connection_stats()

        # Dodaj informacje o bazach danych
        status['databases'] = {
            'count': len(self.db_manager.list_databases()),
            'list': self.db_manager.list_databases()
        }

        return status

    def broadcast_database_event(self, db_name: str, event_type: str, data: Dict[str, Any]):
        """Rozgłasza wydarzenie bazy danych przez WebSocket"""
        if self.luxws and self.running:
            self.luxws.broadcast_database_change(db_name, event_type, data)

    def wait_for_shutdown(self):
        """Oczekuje na zakończenie wszystkich wątków"""
        try:
            if self.api_thread and self.api_thread.is_alive():
                self.api_thread.join()

            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join()

        except KeyboardInterrupt:
            logger.log_info("Otrzymano sygnał przerwania")
            self.stop_all()

# Singleton instance
_luxcore_instance = None

def get_luxcore() -> LuxCore:
    """Zwraca singleton instance LuxCore"""
    global _luxcore_instance
    if _luxcore_instance is None:
        _luxcore_instance = LuxCore()
    return _luxcore_instance