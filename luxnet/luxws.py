
"""
LuxWS - WebSocket Server dla LuxDB
Zapewnia stałe połączenie i real-time komunikację z klientami
"""

import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from threading import Thread

from .manager import get_db_manager
from .session_manager import get_session_manager
from .utils.error_handlers import LuxDBError, handle_database_errors
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class LuxWS:
    """
    WebSocket serwer dla LuxDB z funkcjami:
    - Real-time synchronizacja danych
    - Powiadomienia o zmianach w bazie
    - Zarządzanie sesjami użytkowników
    - Pokoje dla różnych baz danych
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5001):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'luxdb_secret_key_change_in_production'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", logger=True, engineio_logger=True)
        
        self.host = host
        self.port = port
        self.db_manager = get_db_manager()
        self.session_manager = get_session_manager()
        
        # Aktywne połączenia i pokoje
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.database_rooms: Dict[str, Set[str]] = {}
        
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Konfiguruje handlery eventów WebSocket"""
        
        @self.socketio.on('connect')
        def handle_connect(auth=None):
            """Obsługuje nowe połączenie WebSocket"""
            client_id = request.sid
            logger.log_info(f"Nowe połączenie WebSocket: {client_id}")
            
            # Inicjalizuj dane połączenia
            self.active_connections[client_id] = {
                'connected_at': datetime.now(),
                'authenticated': False,
                'user_id': None,
                'databases': set(),
                'session_token': None
            }
            
            emit('connection_established', {
                'client_id': client_id,
                'server': 'LuxWS',
                'version': '1.0.0',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Obsługuje rozłączenie WebSocket"""
            client_id = request.sid
            logger.log_info(f"Rozłączenie WebSocket: {client_id}")
            
            # Usuń z pokoi i aktywnych połączeń
            if client_id in self.active_connections:
                user_data = self.active_connections[client_id]
                for db_name in user_data.get('databases', []):
                    if db_name in self.database_rooms:
                        self.database_rooms[db_name].discard(client_id)
                
                del self.active_connections[client_id]
        
        @self.socketio.on('authenticate')
        def handle_authenticate(data):
            """Uwierzytelnia użytkownika przez WebSocket"""
            client_id = request.sid
            session_token = data.get('session_token')
            
            if not session_token:
                emit('auth_error', {'message': 'Brak tokenu sesji'})
                return
            
            try:
                session_data = self.session_manager.validate_session(session_token)
                if session_data:
                    self.active_connections[client_id].update({
                        'authenticated': True,
                        'user_id': session_data['user_id'],
                        'session_token': session_token
                    })
                    
                    emit('authenticated', {
                        'user_id': session_data['user_id'],
                        'timestamp': datetime.now().isoformat()
                    })
                    logger.log_info(f"Uwierzytelniono użytkownika {session_data['user_id']} na WebSocket")
                else:
                    emit('auth_error', {'message': 'Nieprawidłowy token sesji'})
            except Exception as e:
                logger.log_error("Błąd uwierzytelniania WebSocket", e)
                emit('auth_error', {'message': 'Błąd serwera podczas uwierzytelniania'})
        
        @self.socketio.on('join_database')
        def handle_join_database(data):
            """Dołącza użytkownika do pokoju bazy danych"""
            client_id = request.sid
            db_name = data.get('database')
            
            if not self._is_authenticated(client_id):
                emit('error', {'message': 'Wymagane uwierzytelnienie'})
                return
            
            if not db_name or db_name not in self.db_manager.list_databases():
                emit('error', {'message': f'Baza danych {db_name} nie istnieje'})
                return
            
            # Dołącz do pokoju
            join_room(f"db_{db_name}")
            
            # Zaktualizuj dane połączenia
            self.active_connections[client_id]['databases'].add(db_name)
            
            if db_name not in self.database_rooms:
                self.database_rooms[db_name] = set()
            self.database_rooms[db_name].add(client_id)
            
            emit('joined_database', {
                'database': db_name,
                'timestamp': datetime.now().isoformat()
            })
            
            logger.log_info(f"Użytkownik {self.active_connections[client_id]['user_id']} dołączył do bazy {db_name}")
        
        @self.socketio.on('leave_database')
        def handle_leave_database(data):
            """Opuszcza pokój bazy danych"""
            client_id = request.sid
            db_name = data.get('database')
            
            if db_name and client_id in self.active_connections:
                leave_room(f"db_{db_name}")
                self.active_connections[client_id]['databases'].discard(db_name)
                
                if db_name in self.database_rooms:
                    self.database_rooms[db_name].discard(client_id)
                
                emit('left_database', {
                    'database': db_name,
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('query_database')
        def handle_query_database(data):
            """Wykonuje zapytanie do bazy danych przez WebSocket"""
            client_id = request.sid
            
            if not self._is_authenticated(client_id):
                emit('error', {'message': 'Wymagane uwierzytelnienie'})
                return
            
            db_name = data.get('database')
            query_type = data.get('type', 'select')
            query_data = data.get('data', {})
            
            try:
                if query_type == 'get_info':
                    result = self.db_manager.get_database_info(db_name)
                elif query_type == 'raw_sql':
                    sql = query_data.get('sql', '')
                    params = query_data.get('params', {})
                    result = self.db_manager.execute_raw_sql(db_name, sql, params)
                else:
                    result = {'error': 'Nieobsługiwany typ zapytania'}
                
                emit('query_result', {
                    'database': db_name,
                    'type': query_type,
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.log_error(f"Błąd zapytania WebSocket: {e}")
                emit('query_error', {
                    'database': db_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        @self.socketio.on('get_server_status')
        def handle_get_server_status():
            """Zwraca status serwera"""
            databases = self.db_manager.list_databases()
            emit('server_status', {
                'active_connections': len(self.active_connections),
                'databases': databases,
                'database_rooms': {db: len(clients) for db, clients in self.database_rooms.items()},
                'timestamp': datetime.now().isoformat()
            })
    
    def _is_authenticated(self, client_id: str) -> bool:
        """Sprawdza czy klient jest uwierzytelniony"""
        return (client_id in self.active_connections and 
                self.active_connections[client_id]['authenticated'])
    
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
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Zwraca statystyki połączeń"""
        authenticated_count = sum(1 for conn in self.active_connections.values() 
                                if conn['authenticated'])
        
        return {
            'total_connections': len(self.active_connections),
            'authenticated_connections': authenticated_count,
            'database_rooms': len(self.database_rooms),
            'active_databases': list(self.database_rooms.keys())
        }
    
    def run(self, debug: bool = False):
        """Uruchamia serwer WebSocket"""
        logger.log_info(f"Uruchamianie LuxWS na {self.host}:{self.port}")
        self.socketio.run(self.app, host="0.0.0.0", port=self.port, debug=debug)

# Singleton instance
_luxws_instance = None

def get_luxws() -> LuxWS:
    """Zwraca singleton instance LuxWS"""
    global _luxws_instance
    if _luxws_instance is None:
        _luxws_instance = LuxWS()
    return _luxws_instance
