
"""
LuxCore - Centralny manager połączeń dla LuxDB
Zarządza WebSocket i REST API serwerami
"""

import threading
from typing import Optional, Dict, Any
from datetime import datetime

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
    
    def start_all(self, debug: bool = False):
        """Uruchamia wszystkie serwisy"""
        if not self.initialize():
            return False
        
        self.running = True
        
        # Uruchom API serwer
        self.start_api_server(debug)
        
        # Uruchom WebSocket serwer  
        self.start_ws_server(debug)
        
        logger.log_info("Wszystkie serwisy LuxCore uruchomione")
        return True
    
    def stop_all(self):
        """Zatrzymuje wszystkie serwisy"""
        self.running = False
        
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
