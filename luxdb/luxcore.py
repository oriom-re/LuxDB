"""
LuxCore - Centralny manager połączeń dla LuxDB
Zarządza WebSocket i REST API serwerami
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .luxws_server import get_luxws_server, LuxWSServer
from .luxapi import get_luxapi, LuxAPI
from .manager import get_db_manager
from .utils.logging_utils import get_db_logger
from .callback_system import get_astral_callback_manager, CallbackPriority

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
        self.luxws_server: Optional[LuxWSServer] = None

        self.api_thread: Optional[threading.Thread] = None
        self.ws_thread: Optional[threading.Thread] = None

        self.running = False
        self.db_manager = get_db_manager()

        # System callbacków astralnych
        self.callback_manager = get_astral_callback_manager()
        self.core_namespace = self.callback_manager.create_namespace("luxcore")

        logger.log_info("Inicjalizacja LuxCore")
        self._setup_core_callbacks()

    def initialize(self):
        """Inicjalizuje wszystkie komponenty"""
        try:
            # Inicjalizuj API i WebSocket serwery
            self.luxapi = get_luxapi()
            self.luxws_server = get_luxws_server()

            # Skonfiguruj porty
            self.luxapi.port = self.api_port
            self.luxws_server.port = self.ws_port

            logger.log_info("LuxCore zainicjalizowany pomyślnie")
            return True

        except Exception as e:
            logger.log_error("Błąd inicjalizacji LuxCore", e,
                           context={'api_port': self.api_port, 'ws_port': self.ws_port},
                           error_code='LUXCORE_INIT_ERROR')
            return False

    def start_api_server(self, debug: bool = False):
        """Uruchamia serwer API w osobnym wątku"""
        if self.luxapi is None:
            self.initialize()

        def run_api():
            print("run api")
            try:
                logger.log_info(f"Uruchamianie LuxAPI na porcie {self.api_port}")
                print('uruchomiony')
                self.luxapi.run(debug=debug)
            except Exception as e:
                print(e)
                logger.log_error("Błąd uruchamiania LuxAPI", e,
                               context={'port': self.api_port},
                               error_code='LUXAPI_START_ERROR')

        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        logger.log_info("LuxAPI uruchomiony w tle")

    def start_ws_server(self, debug: bool = False):
        """Uruchamia serwer WebSocket w osobnym wątku"""
        if self.luxws_server is None:
            self.initialize()

        def run_ws():
            try:
                logger.log_info(f"Uruchamianie LuxWS na porcie {self.ws_port}")
                self.luxws_server.run(debug=debug)
            except Exception as e:
                logger.log_error("Błąd uruchamiania LuxWS", e,
                               context={'port': self.ws_port},
                               error_code='LUXWS_START_ERROR')

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
            luxws = get_luxws_server()
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
            logger.log_error("Błąd uruchamiania zintegrowanego serwera", e,
                           context={'port': 5000, 'debug': debug},
                           error_code='INTEGRATED_SERVER_ERROR')
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
                # Uruchom serwisy w wątkach
                self.start_api_server(debug=debug)
                time.sleep(1)  # Krótka pauza na uruchomienie API

                logger.log_info("Uruchamianie LuxWS na porcie 5001")
                self.start_ws_server(debug=debug)
                time.sleep(1)  # Krótka pauza na uruchomienie WS

                # Sprawdź czy wątki są aktywne
                if (self.api_thread and self.api_thread.is_alive() and 
                    self.ws_thread and self.ws_thread.is_alive()):
                    logger.log_info("Wszystkie serwisy LuxCore uruchomione")
                    self.running = True
                    return True
                else:
                    logger.log_error("Błąd uruchamiania jednego lub więcej serwisów")
                    return False
        except Exception as e:
            logger.log_error("Błąd uruchamiania serwisów LuxCore", e,
                           context={'is_deployment': is_deployment, 'debug': debug},
                           error_code='LUXCORE_START_ALL_ERROR')
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
        if self.luxws_server:
            status['services']['luxws']['connections'] = self.luxws_server.get_connection_stats()

        # Dodaj informacje o bazach danych
        status['databases'] = {
            'count': len(self.db_manager.list_databases()),
            'list': self.db_manager.list_databases()
        }

        return status

    def broadcast_database_event(self, db_name: str, event_type: str, data: Dict[str, Any]):
        """Rozgłasza wydarzenie bazy danych przez WebSocket"""
        if self.luxws_server and self.running:
            self.luxws_server.broadcast_database_change(db_name, event_type, data)

        # Emituj również przez system callbacków astralnych
        self.emit_astral_event('database_change', {
            'database': db_name,
            'event_type': event_type,
            'data': data
        })

    def _setup_core_callbacks(self):
        """Konfiguruje callbacki astralne dla LuxCore"""

        def on_service_startup(context):
            """Callback dla startu serwisów"""
            service_data = context.data
            logger.log_info(f"Uruchomiono serwis: {service_data}")

            # Rozgłoś przez WebSocket jeśli dostępny
            if self.luxws_server:
                self.luxws_server.emit_astral_event('service_started', service_data)

        def on_service_shutdown(context):
            """Callback dla zatrzymania serwisów"""
            service_data = context.data
            logger.log_info(f"Zatrzymano serwis: {service_data}")

            if self.luxws_server:
                self.luxws_server.emit_astral_event('service_stopped', service_data)

        def on_database_operation(context):
            """Callback dla operacji na bazach danych"""
            operation_data = context.data
            logger.log_info(f"Operacja na bazie: {operation_data}")

            # Automatycznie rozgłoś przez WebSocket
            if self.luxws_server and operation_data.get('broadcast', True):
                self.broadcast_database_event(
                    operation_data.get('database'),
                    operation_data.get('operation'),
                    operation_data.get('result', {})
                )

        def on_astral_realm_sync(context):
            """Callback dla synchronizacji między realami astralnymi"""
            sync_data = context.data
            logger.log_info(f"Synchronizacja realm: {sync_data}")

            # Koordynuj synchronizację między serwisami
            if self.luxws_server:
                self.luxws_server.emit_astral_event('realm_sync', sync_data)

        # Rejestruj callbacki w namespace core
        self.core_namespace.on('service_startup', on_service_startup,
                              priority=CallbackPriority.HIGH)
        self.core_namespace.on('service_shutdown', on_service_shutdown,
                              priority=CallbackPriority.HIGH)
        self.core_namespace.on('database_operation', on_database_operation,
                              priority=CallbackPriority.NORMAL)
        self.core_namespace.on('astral_realm_sync', on_astral_realm_sync,
                              priority=CallbackPriority.CRITICAL)

        logger.log_info("Skonfigurowano callbacki astralne dla LuxCore")

    def emit_astral_event(self, event_name: str, data: Any, **metadata):
        """Emituje zdarzenie astralne przez system callbacków"""
        return self.core_namespace.emit(
            event_name=event_name,
            data=data,
            source="luxcore",
            **metadata
        )

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
```

```python
"""
LuxCore - Centralny manager połączeń dla LuxDB
Zarządza WebSocket i REST API serwerami
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime
import time

from .luxws_server import get_luxws_server, LuxWSServer
from .luxapi import get_luxapi, LuxAPI
from .manager import get_db_manager
from .utils.logging_utils import get_db_logger
from .callback_system import get_astral_callback_manager, CallbackPriority

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
        self.luxws_server: Optional[LuxWSServer] = None

        self.api_thread: Optional[threading.Thread] = None
        self.ws_thread: Optional[threading.Thread] = None

        self.running = False
        self.db_manager = get_db_manager()

        # System callbacków astralnych
        self.callback_manager = get_astral_callback_manager()
        self.core_namespace = self.callback_manager.create_namespace("luxcore")

        logger.log_info("Inicjalizacja LuxCore")
        self._setup_core_callbacks()

    def initialize(self):
        """Inicjalizuje wszystkie komponenty"""
        try:
            # Inicjalizuj API i WebSocket serwery
            self.luxapi = get_luxapi()
            self.luxws_server = get_luxws_server()

            # Skonfiguruj porty
            self.luxapi.port = self.api_port
            self.luxws_server.port = self.ws_port

            logger.log_info("LuxCore zainicjalizowany pomyślnie")
            return True

        except Exception as e:
            logger.log_error("Błąd inicjalizacji LuxCore", e,
                           context={'api_port': self.api_port, 'ws_port': self.ws_port},
                           error_code='LUXCORE_INIT_ERROR')
            return False

    def start_api_server(self, debug: bool = False):
        """Uruchamia serwer API w osobnym wątku"""
        if self.luxapi is None:
            self.initialize()

        def run_api():
            print("run api")
            try:
                logger.log_info(f"Uruchamianie LuxAPI na porcie {self.api_port}")
                print('uruchomiony')
                self.luxapi.run(debug=debug)
            except Exception as e:
                print(e)
                logger.log_error("Błąd uruchamiania LuxAPI", e,
                               context={'port': self.api_port},
                               error_code='LUXAPI_START_ERROR')

        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        logger.log_info("LuxAPI uruchomiony w tle")

    def start_ws_server(self, debug: bool = False):
        """Uruchamia serwer WebSocket w osobnym wątku"""
        if self.luxws_server is None:
            self.initialize()

        def run_ws():
            try:
                logger.log_info(f"Uruchamianie LuxWS na porcie {self.ws_port}")
                self.luxws_server.run(debug=debug)
            except Exception as e:
                logger.log_error("Błąd uruchamiania LuxWS", e,
                               context={'port': self.ws_port},
                               error_code='LUXWS_START_ERROR')

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
            luxws = get_luxws_server()
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
            logger.log_error("Błąd uruchamiania zintegrowanego serwera", e,
                           context={'port': 5000, 'debug': debug},
                           error_code='INTEGRATED_SERVER_ERROR')
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
                # Uruchom serwisy w wątkach
                self.start_api_server(debug=debug)
                time.sleep(1)  # Krótka pauza na uruchomienie API

                logger.log_info("Uruchamianie LuxWS na porcie 5001")
                self.start_ws_server(debug=debug)
                time.sleep(1)  # Krótka pauza na uruchomienie WS

                # Sprawdź czy wątki są aktywne
                if (self.api_thread and self.api_thread.is_alive() and 
                    self.ws_thread and self.ws_thread.is_alive()):
                    logger.log_info("Wszystkie serwisy LuxCore uruchomione")
                    self.running = True
                    return True
                else:
                    logger.log_error("Błąd uruchamiania jednego lub więcej serwisów")
                    return False
        except Exception as e:
            logger.log_error("Błąd uruchamiania serwisów LuxCore", e,
                           context={'is_deployment': is_deployment, 'debug': debug},
                           error_code='LUXCORE_START_ALL_ERROR')
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
        if self.luxws_server:
            status['services']['luxws']['connections'] = self.luxws_server.get_connection_stats()

        # Dodaj informacje o bazach danych
        status['databases'] = {
            'count': len(self.db_manager.list_databases()),
            'list': self.db_manager.list_databases()
        }

        return status

    def broadcast_database_event(self, db_name: str, event_type: str, data: Dict[str, Any]):
        """Rozgłasza wydarzenie bazy danych przez WebSocket"""
        if self.luxws_server and self.running:
            self.luxws_server.broadcast_database_change(db_name, event_type, data)

        # Emituj również przez system callbacków astralnych
        self.emit_astral_event('database_change', {
            'database': db_name,
            'event_type': event_type,
            'data': data
        })

    def _setup_core_callbacks(self):
        """Konfiguruje callbacki astralne dla LuxCore"""

        def on_service_startup(context):
            """Callback dla startu serwisów"""
            service_data = context.data
            logger.log_info(f"Uruchomiono serwis: {service_data}")

            # Rozgłoś przez WebSocket jeśli dostępny
            if self.luxws_server:
                self.luxws_server.emit_astral_event('service_started', service_data)

        def on_service_shutdown(context):
            """Callback dla zatrzymania serwisów"""
            service_data = context.data
            logger.log_info(f"Zatrzymano serwis: {service_data}")

            if self.luxws_server:
                self.luxws_server.emit_astral_event('service_stopped', service_data)

        def on_database_operation(context):
            """Callback dla operacji na bazach danych"""
            operation_data = context.data
            logger.log_info(f"Operacja na bazie: {operation_data}")

            # Automatycznie rozgłoś przez WebSocket
            if self.luxws_server and operation_data.get('broadcast', True):
                self.broadcast_database_event(
                    operation_data.get('database'),
                    operation_data.get('operation'),
                    operation_data.get('result', {})
                )

        def on_astral_realm_sync(context):
            """Callback dla synchronizacji między realami astralnymi"""
            sync_data = context.data
            logger.log_info(f"Synchronizacja realm: {sync_data}")

            # Koordynuj synchronizację między serwisami
            if self.luxws_server:
                self.luxws_server.emit_astral_event('realm_sync', sync_data)

        # Rejestruj callbacki w namespace core
        self.core_namespace.on('service_startup', on_service_startup,
                              priority=CallbackPriority.HIGH)
        self.core_namespace.on('service_shutdown', on_service_shutdown,
                              priority=CallbackPriority.HIGH)
        self.core_namespace.on('database_operation', on_database_operation,
                              priority=CallbackPriority.NORMAL)
        self.core_namespace.on('astral_realm_sync', on_astral_realm_sync,
                              priority=CallbackPriority.CRITICAL)

        logger.log_info("Skonfigurowano callbacki astralne dla LuxCore")

    def emit_astral_event(self, event_name: str, data: Any, **metadata):
        """Emituje zdarzenie astralne przez system callbacków"""
        return self.core_namespace.emit(
            event_name=event_name,
            data=data,
            source="luxcore",
            **metadata
        )

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
```