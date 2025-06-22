
"""
LuxWS Client - Dedykowany klient WebSocket dla LuxDB
Obsługuje połączenia wychodzące i dwukierunkową komunikację z serwerem
"""

import socketio
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Union
import queue
import uuid

from .utils.logging_utils import get_db_logger
from .utils.error_handlers import LuxDBError

logger = get_db_logger()

class LuxWSClient:
    """
    Dedykowany klient WebSocket dla LuxDB z funkcjami:
    - Automatyczne reconnect
    - Kolejkowanie wiadomości
    - Callback system
    - Heartbeat monitoring
    - Event subscriptions
    """
    
    def __init__(self, server_url: str = "http://0.0.0.0:5001", client_type: str = "api_client"):
        self.server_url = server_url
        self.client_type = client_type
        
        # Stan połączenia
        self.connected = False
        self.authenticated = False
        self.client_id = None
        self.session_token = None
        
        # Konfiguracja
        self.reconnect_attempts = 5
        self.reconnect_delay = 2.0
        self.heartbeat_interval = 30
        
        # Wewnętrzne struktury
        self.callbacks: Dict[str, List[Callable]] = {}
        self.subscriptions: List[str] = []
        self.pending_queries: Dict[str, Dict[str, Any]] = {}
        self.message_queue = queue.Queue()
        
        # Threading
        self.heartbeat_thread = None
        self.message_thread = None
        self.reconnect_thread = None
        
        # SocketIO client
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=self.reconnect_attempts,
            reconnection_delay=self.reconnect_delay
        )
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Konfiguruje handlery eventów WebSocket"""
        
        @self.sio.event
        def connect():
            logger.log_info("Połączono z LuxWS Server")
            self.connected = True
            self._trigger_callback('on_connect', {'timestamp': datetime.now().isoformat()})
        
        @self.sio.event
        def disconnect():
            logger.log_info("Rozłączono z LuxWS Server")
            self.connected = False
            self.authenticated = False
            self._trigger_callback('on_disconnect', {'timestamp': datetime.now().isoformat()})
        
        @self.sio.event
        def server_welcome(data):
            logger.log_info(f"Powitanie od serwera: {data}")
            self.client_id = data.get('client_id')
            self._trigger_callback('on_server_welcome', data)
        
        @self.sio.event
        def auth_success(data):
            logger.log_info("Uwierzytelnienie udane")
            self.authenticated = True
            self._trigger_callback('on_auth_success', data)
        
        @self.sio.event
        def auth_error(data):
            logger.log_error(f"Błąd uwierzytelniania: {data}")
            self.authenticated = False
            self._trigger_callback('on_auth_error', data)
        
        @self.sio.event
        def room_joined(data):
            logger.log_info(f"Dołączono do pokoju: {data}")
            self._trigger_callback('on_room_joined', data)
        
        @self.sio.event
        def room_left(data):
            logger.log_info(f"Opuszczono pokój: {data}")
            self._trigger_callback('on_room_left', data)
        
        @self.sio.event
        def room_member_joined(data):
            self._trigger_callback('on_room_member_joined', data)
        
        @self.sio.event
        def room_member_left(data):
            self._trigger_callback('on_room_member_left', data)
        
        @self.sio.event
        def database_change(data):
            logger.log_info(f"Zmiana w bazie: {data}")
            self._trigger_callback('on_database_change', data)
        
        @self.sio.event
        def query_result(data):
            query_id = data.get('query_id')
            if query_id in self.pending_queries:
                query_info = self.pending_queries.pop(query_id)
                callback = query_info.get('callback')
                if callback:
                    callback(data, None)
            
            self._trigger_callback('on_query_result', data)
        
        @self.sio.event
        def query_error(data):
            query_id = data.get('query_id')
            if query_id in self.pending_queries:
                query_info = self.pending_queries.pop(query_id)
                callback = query_info.get('callback')
                if callback:
                    callback(None, data.get('error'))
            
            self._trigger_callback('on_query_error', data)
        
        @self.sio.event
        def server_status(data):
            self._trigger_callback('on_server_status', data)
        
        @self.sio.event
        def server_heartbeat(data):
            self._trigger_callback('on_server_heartbeat', data)
        
        @self.sio.event
        def subscription_confirmed(data):
            logger.log_info(f"Subskrypcje potwierdzone: {data}")
            self._trigger_callback('on_subscription_confirmed', data)
        
        @self.sio.event
        def error(data):
            logger.log_error(f"Błąd serwera: {data}")
            self._trigger_callback('on_error', data)
    
    def on(self, event: str, callback: Callable):
        """Rejestruje callback dla zdarzenia"""
        if event not in self.callbacks:
            self.callbacks[event] = []
        self.callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, data: Any):
        """Wywołuje wszystkie callbacki dla zdarzenia"""
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.log_error(f"Błąd w callback {event}: {e}")
    
    def connect_to_server(self) -> bool:
        """Łączy się z serwerem WebSocket"""
        try:
            logger.log_info(f"Łączenie z {self.server_url}...")
            self.sio.connect(self.server_url)
            
            # Czekaj na połączenie
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                self._start_heartbeat()
                return True
            else:
                logger.log_error("Timeout podczas łączenia")
                return False
                
        except Exception as e:
            logger.log_error("Błąd połączenia WebSocket", e,
                           context={'server_url': self.server_url, 'client_type': self.client_type},
                           error_code='WS_CONNECTION_ERROR')
            return False
    
    def authenticate(self, session_token: str) -> bool:
        """Uwierzytelnia się na serwerze"""
        if not self.connected:
            logger.log_error("Brak połączenia z serwerem")
            return False
        
        self.session_token = session_token
        
        self.sio.emit('client_authenticate', {
            'session_token': session_token,
            'client_type': self.client_type
        })
        
        # Czekaj na uwierzytelnienie
        timeout = 10
        start_time = time.time()
        while not self.authenticated and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        return self.authenticated
    
    def join_database_room(self, db_name: str):
        """Dołącza do pokoju bazy danych"""
        if not self.authenticated:
            raise LuxDBError("Wymagane uwierzytelnienie")
        
        self.sio.emit('join_database_room', {
            'database': db_name
        })
    
    def leave_database_room(self, db_name: str):
        """Opuszcza pokój bazy danych"""
        if not self.authenticated:
            raise LuxDBError("Wymagane uwierzytelnienie")
        
        self.sio.emit('leave_database_room', {
            'database': db_name
        })
    
    def execute_query(self, db_name: str, query_type: str, query_data: Dict[str, Any], 
                     callback: Optional[Callable] = None) -> str:
        """Wykonuje zapytanie do bazy danych"""
        if not self.authenticated:
            raise LuxDBError("Wymagane uwierzytelnienie")
        
        query_id = str(uuid.uuid4())
        
        if callback:
            self.pending_queries[query_id] = {
                'callback': callback,
                'created_at': datetime.now(),
                'db_name': db_name,
                'type': query_type
            }
        
        self.sio.emit('execute_database_query', {
            'query_id': query_id,
            'database': db_name,
            'type': query_type,
            'data': query_data
        })
        
        return query_id
    
    def subscribe_to_events(self, events: List[str]):
        """Subskrybuje zdarzenia"""
        if not self.authenticated:
            raise LuxDBError("Wymagane uwierzytelnienie")
        
        self.subscriptions.extend(events)
        
        self.sio.emit('subscribe_to_events', {
            'events': events
        })
    
    def get_server_status(self):
        """Pobiera status serwera"""
        if not self.connected:
            raise LuxDBError("Brak połączenia z serwerem")
        
        self.sio.emit('get_server_status')
    
    def send_heartbeat(self):
        """Wysyła heartbeat do serwera"""
        if self.connected:
            self.sio.emit('client_heartbeat', {
                'client_type': self.client_type,
                'timestamp': datetime.now().isoformat()
            })
    
    def _start_heartbeat(self):
        """Uruchamia wątek heartbeat"""
        def heartbeat_worker():
            while self.connected:
                try:
                    self.send_heartbeat()
                    time.sleep(self.heartbeat_interval)
                except Exception as e:
                    logger.log_error("Błąd heartbeat WebSocket", e,
                                   context={'client_type': self.client_type},
                                   error_code='WS_HEARTBEAT_ERROR')
                    break
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
    
    def disconnect(self):
        """Rozłącza się z serwerem"""
        if self.connected:
            self.sio.disconnect()
        
        self.connected = False
        self.authenticated = False
        self.client_id = None
        self.session_token = None
    
    def wait_for_response(self, query_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Czeka na odpowiedź na zapytanie (synchroniczne)"""
        start_time = time.time()
        
        while query_id in self.pending_queries and (time.time() - start_time) < timeout:
            time.sleep(0.1)
        
        # Sprawdź czy zapytanie zostało przetworzone
        if query_id not in self.pending_queries:
            return True  # Callback został wywołany
        else:
            # Timeout - usuń zapytanie
            if query_id in self.pending_queries:
                del self.pending_queries[query_id]
            return None
    
    # Convenience methods
    def get_database_info(self, db_name: str, callback: Optional[Callable] = None) -> str:
        """Pobiera informacje o bazie danych"""
        return self.execute_query(db_name, 'get_info', {}, callback)
    
    def list_tables(self, db_name: str, callback: Optional[Callable] = None) -> str:
        """Pobiera listę tabel"""
        return self.execute_query(db_name, 'list_tables', {}, callback)
    
    def execute_sql(self, db_name: str, sql: str, params: Dict[str, Any] = None, 
                   callback: Optional[Callable] = None) -> str:
        """Wykonuje surowe zapytanie SQL"""
        return self.execute_query(db_name, 'raw_sql', {
            'sql': sql,
            'params': params or {}
        }, callback)
    
    def get_table_data(self, db_name: str, table_name: str, limit: int = 100, 
                      callback: Optional[Callable] = None) -> str:
        """Pobiera dane z tabeli"""
        return self.execute_query(db_name, 'table_data', {
            'table_name': table_name,
            'limit': limit
        }, callback)

# Factory functions
def create_client(server_url: str = "http://0.0.0.0:5001", client_type: str = "api_client") -> LuxWSClient:
    """Tworzy nowego klienta WebSocket"""
    return LuxWSClient(server_url, client_type)

def create_authenticated_client(server_url: str, session_token: str, 
                               client_type: str = "api_client") -> Optional[LuxWSClient]:
    """Tworzy i uwierzytelnia klienta WebSocket"""
    client = LuxWSClient(server_url, client_type)
    
    if client.connect_to_server():
        if client.authenticate(session_token):
            return client
        else:
            client.disconnect()
            return None
    else:
        return None
