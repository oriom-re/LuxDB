
"""
LuxWS Server - Dedykowany serwer WebSocket dla LuxDB
Obsługuje połączenia przychodzące i dwukierunkową komunikację
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional, List
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from threading import Thread, Lock

from .manager import get_db_manager
from .session_manager import get_session_manager
from .utils.error_handlers import LuxDBError, handle_database_errors
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class LuxWSServer:
    """
    Dedykowany serwer WebSocket dla LuxDB z funkcjami:
    - Real-time synchronizacja danych
    - Powiadomienia o zmianach w bazie
    - Zarządzanie sesjami użytkowników
    - Pokoje dla różnych baz danych
    - Dwukierunkowa komunikacja z klientami
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5002):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'luxws_server_secret_key_change_in_production'
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*", 
            logger=True, 
            engineio_logger=True,
            ping_timeout=60,
            ping_interval=25
        )
        
        self.host = host
        self.port = port
        self.db_manager = get_db_manager()
        self.session_manager = get_session_manager()
        
        # Aktywne połączenia i pokoje
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.database_rooms: Dict[str, Set[str]] = {}
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}
        
        # Thread safety
        self.connections_lock = Lock()
        
        self._setup_event_handlers()
        self._setup_server_events()
    
    def _setup_event_handlers(self):
        """Konfiguruje handlery eventów WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            """Obsługuje nowe połączenie WebSocket"""
            client_id = request.sid
            client_ip = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            logger.log_info(f"Nowe połączenie WebSocket: {client_id} z {client_ip}")
            
            with self.connections_lock:
                # Inicjalizuj dane połączenia
                self.active_connections[client_id] = {
                    'connected_at': datetime.now(),
                    'authenticated': False,
                    'user_id': None,
                    'databases': set(),
                    'session_token': None,
                    'ip_address': client_ip,
                    'user_agent': user_agent,
                    'last_activity': datetime.now()
                }
                
                self.client_subscriptions[client_id] = set()
            
            emit('server_welcome', {
                'client_id': client_id,
                'server': 'LuxWS Server',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat(),
                'features': [
                    'real_time_sync',
                    'database_rooms',
                    'user_sessions',
                    'bidirectional_comm'
                ]
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Obsługuje rozłączenie WebSocket"""
            client_id = request.sid
            logger.log_info(f"Rozłączenie WebSocket: {client_id}")
            
            with self.connections_lock:
                # Usuń z pokoi i aktywnych połączeń
                if client_id in self.active_connections:
                    user_data = self.active_connections[client_id]
                    for db_name in user_data.get('databases', []):
                        if db_name in self.database_rooms:
                            self.database_rooms[db_name].discard(client_id)
                    
                    del self.active_connections[client_id]
                
                if client_id in self.client_subscriptions:
                    del self.client_subscriptions[client_id]
                
                if client_id in self.connected_clients:
                    del self.connected_clients[client_id]
        
        @self.socketio.on('client_authenticate')
        def handle_authenticate(data):
            """Uwierzytelnia klienta przez WebSocket"""
            client_id = request.sid
            session_token = data.get('session_token')
            client_type = data.get('client_type', 'web')
            
            if not session_token:
                emit('auth_error', {'message': 'Brak tokenu sesji'})
                return
            
            try:
                session_data = self.session_manager.validate_session(session_token)
                if session_data:
                    with self.connections_lock:
                        self.active_connections[client_id].update({
                            'authenticated': True,
                            'user_id': session_data['user_id'],
                            'session_token': session_token,
                            'client_type': client_type
                        })
                        
                        self.connected_clients[client_id] = {
                            'user_id': session_data['user_id'],
                            'client_type': client_type,
                            'authenticated_at': datetime.now()
                        }
                    
                    emit('auth_success', {
                        'user_id': session_data['user_id'],
                        'client_type': client_type,
                        'timestamp': datetime.now().isoformat(),
                        'available_databases': self.db_manager.list_databases()
                    })
                    
                    logger.log_info(f"Uwierzytelniono klienta {client_type} dla użytkownika {session_data['user_id']}")
                else:
                    emit('auth_error', {'message': 'Nieprawidłowy token sesji'})
            except Exception as e:
                logger.log_error("Błąd uwierzytelniania WebSocket", e)
                emit('auth_error', {'message': 'Błąd serwera podczas uwierzytelniania'})
        
        @self.socketio.on('join_database_room')
        def handle_join_database(data):
            """Dołącza klienta do pokoju bazy danych"""
            client_id = request.sid
            db_name = data.get('database')
            
            if not self._is_authenticated(client_id):
                emit('error', {'message': 'Wymagane uwierzytelnienie'})
                return
            
            if not db_name or db_name not in self.db_manager.list_databases():
                emit('error', {'message': f'Baza danych {db_name} nie istnieje'})
                return
            
            with self.connections_lock:
                # Dołącz do pokoju
                join_room(f"db_{db_name}")
                
                # Zaktualizuj dane połączenia
                self.active_connections[client_id]['databases'].add(db_name)
                self.client_subscriptions[client_id].add(f"db_{db_name}")
                
                if db_name not in self.database_rooms:
                    self.database_rooms[db_name] = set()
                self.database_rooms[db_name].add(client_id)
            
            emit('room_joined', {
                'database': db_name,
                'room': f"db_{db_name}",
                'timestamp': datetime.now().isoformat(),
                'room_members': len(self.database_rooms[db_name])
            })
            
            # Powiadom innych w pokoju o nowym członku
            emit('room_member_joined', {
                'database': db_name,
                'user_id': self.active_connections[client_id]['user_id'],
                'timestamp': datetime.now().isoformat()
            }, room=f"db_{db_name}", include_self=False)
            
            logger.log_info(f"Klient {client_id} dołączył do bazy {db_name}")
        
        @self.socketio.on('leave_database_room')
        def handle_leave_database(data):
            """Opuszcza pokój bazy danych"""
            client_id = request.sid
            db_name = data.get('database')
            
            if db_name and client_id in self.active_connections:
                with self.connections_lock:
                    leave_room(f"db_{db_name}")
                    self.active_connections[client_id]['databases'].discard(db_name)
                    self.client_subscriptions[client_id].discard(f"db_{db_name}")
                    
                    if db_name in self.database_rooms:
                        self.database_rooms[db_name].discard(client_id)
                
                emit('room_left', {
                    'database': db_name,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Powiadom innych w pokoju
                emit('room_member_left', {
                    'database': db_name,
                    'user_id': self.active_connections[client_id]['user_id'],
                    'timestamp': datetime.now().isoformat()
                }, room=f"db_{db_name}")
        
        @self.socketio.on('execute_database_query')
        def handle_query_database(data):
            """Wykonuje zapytanie do bazy danych przez WebSocket"""
            client_id = request.sid
            
            if not self._is_authenticated(client_id):
                emit('query_error', {'message': 'Wymagane uwierzytelnienie'})
                return
            
            db_name = data.get('database')
            query_type = data.get('type', 'select')
            query_data = data.get('data', {})
            query_id = data.get('query_id')  # Identyfikator zapytania dla klienta
            
            try:
                result = None
                
                if query_type == 'get_info':
                    result = self.db_manager.get_database_info(db_name)
                elif query_type == 'list_tables':
                    result = self.db_manager.get_tables_list(db_name)
                elif query_type == 'raw_sql':
                    sql = query_data.get('sql', '')
                    params = query_data.get('params', {})
                    result = self.db_manager.execute_raw_sql(db_name, sql, params)
                elif query_type == 'table_data':
                    table_name = query_data.get('table_name')
                    limit = query_data.get('limit', 100)
                    result = self.db_manager.get_table_data(db_name, table_name, limit)
                else:
                    emit('query_error', {
                        'query_id': query_id,
                        'error': 'Nieobsługiwany typ zapytania'
                    })
                    return
                
                emit('query_result', {
                    'query_id': query_id,
                    'database': db_name,
                    'type': query_type,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.log_error(f"Błąd zapytania WebSocket: {e}")
                emit('query_error', {
                    'query_id': query_id,
                    'database': db_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('subscribe_to_events')
        def handle_subscribe_events(data):
            """Subskrybuje zdarzenia"""
            client_id = request.sid
            event_types = data.get('events', [])
            
            if not self._is_authenticated(client_id):
                emit('error', {'message': 'Wymagane uwierzytelnienie'})
                return
            
            with self.connections_lock:
                for event_type in event_types:
                    self.client_subscriptions[client_id].add(event_type)
            
            emit('subscription_confirmed', {
                'events': list(self.client_subscriptions[client_id]),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('get_server_status')
        def handle_get_server_status():
            """Zwraca status serwera"""
            with self.connections_lock:
                databases = self.db_manager.list_databases()
                emit('server_status', {
                    'active_connections': len(self.active_connections),
                    'authenticated_clients': len(self.connected_clients),
                    'databases': databases,
                    'database_rooms': {db: len(clients) for db, clients in self.database_rooms.items()},
                    'server_uptime': (datetime.now() - datetime.now()).total_seconds(),
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('client_heartbeat')
        def handle_heartbeat(data):
            """Obsługuje heartbeat od klienta"""
            client_id = request.sid
            
            if client_id in self.active_connections:
                with self.connections_lock:
                    self.active_connections[client_id]['last_activity'] = datetime.now()
                
                emit('server_heartbeat', {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'alive'
                })
    
    def _setup_server_events(self):
        """Konfiguruje zdarzenia specyficzne dla serwera"""
        
        @self.socketio.on('broadcast_to_room')
        def handle_broadcast_to_room(data):
            """Rozgłasza wiadomość do pokoju (tylko dla administratorów)"""
            client_id = request.sid
            
            if not self._is_admin_user(client_id):
                emit('error', {'message': 'Brak uprawnień administratora'})
                return
            
            room_name = data.get('room')
            message = data.get('message')
            event_type = data.get('event_type', 'admin_broadcast')
            
            if room_name and message:
                self.socketio.emit(event_type, {
                    'message': message,
                    'from': 'server_admin',
                    'timestamp': datetime.now().isoformat()
                }, room=room_name)
                
                emit('broadcast_sent', {
                    'room': room_name,
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
    
    def _is_authenticated(self, client_id: str) -> bool:
        """Sprawdza czy klient jest uwierzytelniony"""
        return (client_id in self.active_connections and 
                self.active_connections[client_id]['authenticated'])
    
    def _is_admin_user(self, client_id: str) -> bool:
        """Sprawdza czy użytkownik ma uprawnienia administratora"""
        if not self._is_authenticated(client_id):
            return False
        
        # Tu można dodać logikę sprawdzania uprawnień
        # Na razie zwracamy False - wymaga implementacji systemu uprawnień
        return False
    
    def broadcast_database_change(self, db_name: str, event_type: str, data: Dict[str, Any]):
        """Rozgłasza zmiany w bazie danych do wszystkich klientów w pokoju"""
        if db_name in self.database_rooms and self.database_rooms[db_name]:
            self.socketio.emit('database_change', {
                'database': db_name,
                'event_type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }, room=f"db_{db_name}")
            
            logger.log_info(f"Rozgłoszono zmianę w bazie {db_name}: {event_type}")
    
    def broadcast_to_all_clients(self, event_type: str, data: Dict[str, Any]):
        """Rozgłasza wiadomość do wszystkich połączonych klientów"""
        self.socketio.emit(event_type, {
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.log_info(f"Rozgłoszono do wszystkich klientów: {event_type}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki połączeń"""
        with self.connections_lock:
            authenticated_count = sum(1 for conn in self.active_connections.values() 
                                    if conn['authenticated'])
            
            return {
                'total_connections': len(self.active_connections),
                'authenticated_connections': authenticated_count,
                'connected_clients': len(self.connected_clients),
                'database_rooms': len(self.database_rooms),
                'active_databases': list(self.database_rooms.keys()),
                'client_types': {client['client_type']: 1 for client in self.connected_clients.values()}
            }
    
    def cleanup_inactive_connections(self):
        """Czyści nieaktywne połączenia"""
        inactive_threshold = datetime.now() - timedelta(minutes=30)
        inactive_clients = []
        
        with self.connections_lock:
            for client_id, conn_data in self.active_connections.items():
                if conn_data['last_activity'] < inactive_threshold:
                    inactive_clients.append(client_id)
        
        for client_id in inactive_clients:
            logger.log_info(f"Usuwanie nieaktywnego klienta: {client_id}")
            self.socketio.disconnect(client_id)
    
    def run(self, debug: bool = False):
        """Uruchamia serwer WebSocket"""
        logger.log_info(f"Uruchamianie LuxWS Server na {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, debug=debug)

# Singleton instance
_luxws_server_instance = None

def get_luxws_server() -> LuxWSServer:
    """Zwraca singleton instance LuxWS Server"""
    global _luxws_server_instance
    if _luxws_server_instance is None:
        _luxws_server_instance = LuxWSServer()
    return _luxws_server_instance
