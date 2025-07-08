
"""
🌐 WebSocketBeing - Świadomy Byt Komunikacji WebSocket

Zastępuje martwy ws_flow żywym bytem z własną inteligencją komunikacyjną.
"""

import uuid
import json
import asyncio
import websockets
from typing import Dict, Any, Set, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

from luxdb_v2.beings.base_being import BaseBeing
from luxdb_v2.beings.logical_being import LogicalBeing, LogicType, LogicalContext


@dataclass 
class ConnectionProfile:
    """Profil połączenia WebSocket"""
    connection_id: str
    user_id: Optional[str] = None
    connected_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    subscriptions: Set[str] = field(default_factory=set)
    preferences: Dict[str, Any] = field(default_factory=dict)


class WebSocketBeing(LogicalBeing):
    """
    Świadomy Byt Komunikacji WebSocket
    
    Posiada:
    - Inteligentne zarządzanie połączeniami
    - Adaptacyjne protokoły komunikacji
    - Samooptymalizujące się algorytmy routingu
    """
    
    def __init__(self, realm=None):
        context = LogicalContext(
            domain="communication",
            specialization="websocket_protocol",
            adaptive_learning=True,
            collaboration_enabled=True
        )
        
        super().__init__(LogicType.COMMUNICATION, context, realm)
        
        # Właściwości being'a
        self.essence.name = "WebSocketBeing"
        self.essence.consciousness_level = "communication_aware"
        
        # Zarządzanie połączeniami
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.connection_profiles: Dict[str, ConnectionProfile] = {}
        
        # Subskrypcje i routing
        self.subscriptions: Dict[str, Set[str]] = {}  # channel -> connection_ids
        self.message_handlers: Dict[str, Callable] = {}
        
        # Inteligentne algorytmy
        self.enabled = True
        self._initialize_communication_intelligence()
        self.remember('websocket_being_created', {
            'specialization': 'websocket_protocol',
            'communication_mode': 'adaptive'
        })
    
    def _initialize_communication_intelligence(self):
        """Inicjalizuje inteligentne algorytmy komunikacji"""
        
        def adaptive_message_router():
            """Adaptacyjny router wiadomości"""
            def route_message(message_type: str, data: Dict[str, Any], connection_id: str):
                profile = self.connection_profiles.get(connection_id)
                if not profile:
                    return False
                
                # Adaptacja na podstawie historii
                if profile.message_count > 100:
                    # Priorytetowe traktowanie aktywnych użytkowników
                    return self._priority_route(message_type, data, connection_id)
                else:
                    # Standardowy routing
                    return self._standard_route(message_type, data, connection_id)
            
            return route_message
        
        def connection_health_monitor():
            """Monitor zdrowia połączeń"""
            async def monitor_connections():
                while self.enabled:
                    current_time = datetime.now()
                    for conn_id, profile in list(self.connection_profiles.items()):
                        time_diff = (current_time - profile.last_activity).total_seconds()
                        
                        if time_diff > 300:  # 5 minut braku aktywności
                            await self._handle_inactive_connection(conn_id)
                    
                    await asyncio.sleep(30)  # Sprawdzaj co 30 sekund
            
            return monitor_connections
        
        # Dodaj algorytmy jako mikro-funkcje
        self.micro_functions['adaptive_router'] = adaptive_message_router()
        self.micro_functions['health_monitor'] = connection_health_monitor()
        
        # Zarejestruj handlery
        self._register_default_handlers()
        
        # Dodaj handlery autoryzacji
        self.message_handlers.update({
            'heartbeat_auth': self._handle_heartbeat_auth,
            'refresh_heartbeat': self._handle_refresh_heartbeat
        })
    
    def _register_default_handlers(self):
        """Rejestruje domyślne handlery wiadomości"""
        self.message_handlers.update({
            'subscribe': self._handle_subscribe,
            'unsubscribe': self._handle_unsubscribe,
            'broadcast': self._handle_broadcast,
            'direct_message': self._handle_direct_message,
            'ping': self._handle_ping,
            'get_status': self._handle_get_status
        })
    
    async def handle_new_connection(self, websocket, path):
        """Obsługuje nowe połączenie WebSocket"""
        connection_id = str(uuid.uuid4())
        
        # Utwórz profil połączenia
        profile = ConnectionProfile(connection_id=connection_id)
        self.connection_profiles[connection_id] = profile
        self.active_connections[connection_id] = websocket
        
        self.remember('new_connection', {
            'connection_id': connection_id,
            'path': path,
            'connected_at': profile.connected_at.isoformat()
        })
        
        try:
            # Wyślij powitanie
            await self._send_welcome_message(websocket, connection_id)
            
            # Obsługuj wiadomości
            async for message in websocket:
                await self._process_message(message, connection_id)
                
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self._handle_disconnection(connection_id)
    
    async def _process_message(self, raw_message: str, connection_id: str):
        """Przetwarza wiadomość od klienta"""
        try:
            message = json.loads(raw_message)
            message_type = message.get('type', 'unknown')
            data = message.get('data', {})
            
            # Sprawdź autoryzację dla wszystkich wiadomości oprócz heartbeat
            if message_type != 'heartbeat_auth':
                auth_check = await self._check_connection_auth(connection_id)
                if not auth_check.get('authorized', False):
                    await self._send_error(connection_id, "Unauthorized - valid heartbeat required")
                    return
            
            # Aktualizuj profil
            profile = self.connection_profiles.get(connection_id)
            if profile:
                profile.last_activity = datetime.now()
                profile.message_count += 1
            
            # Routing przez mikro-funkcję
            router = self.micro_functions.get('adaptive_router')
            if router:
                routed = router(message_type, data, connection_id)
                if routed:
                    return
            
            # Fallback do standardowych handlerów
            handler = self.message_handlers.get(message_type)
            if handler:
                await handler(data, connection_id)
            else:
                await self._handle_unknown_message(message_type, data, connection_id)
                
        except json.JSONDecodeError:
            await self._send_error(connection_id, "Invalid JSON format")
        except Exception as e:
            await self._send_error(connection_id, f"Message processing error: {str(e)}")
    
    async def _handle_subscribe(self, data: Dict[str, Any], connection_id: str):
        """Obsługuje subskrypcje kanałów"""

    
    async def _handle_heartbeat_auth(self, data: Dict[str, Any], connection_id: str):
        """Obsługuje autoryzację heartbeat"""
        try:
            # Sprawdź czy mamy access do auth flow
            auth_flow = getattr(self.realm.engine, 'websocket_auth_flow', None)
            if not auth_flow:
                await self._send_error(connection_id, "Authorization system not available")
                return
            
            # Autoryzuj przez callback
            result = auth_flow.execute_callback(
                'websocket_auth',
                'heartbeat_auth',
                connection_id,
                data
            )
            
            if result.get('success', False):
                # Autoryzacja udana
                await self._send_response(connection_id, {
                    'type': 'auth_success',
                    'auth_status': result['auth_status'],
                    'soul_id': result['soul_id'],
                    'auth_level': result['auth_level'],
                    'expires_in': result['expires_in'],
                    'vibration': result['vibration']
                })
                
                # Powiadom Portal o autoryzacji
                await self._notify_portal_about_auth(result, connection_id)
                
            else:
                # Autoryzacja nieudana
                await self._send_response(connection_id, {
                    'type': 'auth_failed',
                    'auth_status': result.get('auth_status', 'rejected'),
                    'error': result.get('error', 'Unknown error')
                })
                
        except Exception as e:
            await self._send_error(connection_id, f"Heartbeat auth error: {str(e)}")
    
    async def _handle_refresh_heartbeat(self, data: Dict[str, Any], connection_id: str):
        """Obsługuje odświeżanie heartbeat"""
        try:
            auth_flow = getattr(self.realm.engine, 'websocket_auth_flow', None)
            if not auth_flow:
                await self._send_error(connection_id, "Authorization system not available")
                return
            
            result = auth_flow.execute_callback(
                'websocket_auth',
                'refresh_heartbeat',
                connection_id,
                data
            )
            
            await self._send_response(connection_id, {
                'type': 'heartbeat_refreshed',
                'success': result.get('success', False),
                'auth_status': result.get('auth_status', 'unknown'),
                'expires_in': result.get('expires_in', 0)
            })
            
        except Exception as e:
            await self._send_error(connection_id, f"Heartbeat refresh error: {str(e)}")
    
    async def _check_connection_auth(self, connection_id: str) -> Dict[str, Any]:
        """Sprawdza autoryzację połączenia"""
        try:
            auth_flow = getattr(self.realm.engine, 'websocket_auth_flow', None)
            if not auth_flow:
                return {'authorized': False, 'reason': 'No auth system'}
            
            return auth_flow.execute_callback(
                'websocket_auth',
                'check_auth',
                connection_id
            )
            
        except Exception:
            return {'authorized': False, 'reason': 'Auth check failed'}
    
    async def _notify_portal_about_auth(self, auth_result: Dict[str, Any], connection_id: str):
        """Powiadamia Portal o autoryzacji"""
        try:
            portal = self.realm.engine.get_soul_resonance_portal()
            if portal:
                # Rezonans z informacją o autoryzacji
                portal.resonate(
                    soul_uid="websocket_being",
                    message={
                        'type': 'soul_authorized',
                        'soul_id': auth_result['soul_id'],
                        'auth_level': auth_result['auth_level'],
                        'connection_id': connection_id,
                        'vibration': auth_result['vibration']
                    }
                )
        except Exception as e:
            self.remember('portal_notification_error', {'error': str(e)})

        channels = data.get('channels', [])
        
        for channel in channels:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = set()
            
            self.subscriptions[channel].add(connection_id)
            
            # Dodaj do profilu
            profile = self.connection_profiles.get(connection_id)
            if profile:
                profile.subscriptions.add(channel)
        
        await self._send_response(connection_id, {
            'type': 'subscribed',
            'channels': channels,
            'success': True
        })
    
    async def _handle_broadcast(self, data: Dict[str, Any], connection_id: str):
        """Obsługuje broadcast do kanału"""
        channel = data.get('channel')
        message = data.get('message')
        
        if not channel or not message:
            await self._send_error(connection_id, "Missing channel or message")
            return
        
        # Rozgłoś do wszystkich subskrybentów
        subscribers = self.subscriptions.get(channel, set())
        
        broadcast_data = {
            'type': 'broadcast',
            'channel': channel,
            'message': message,
            'from': connection_id,
            'timestamp': datetime.now().isoformat()
        }
        
        for subscriber_id in subscribers:
            if subscriber_id != connection_id:  # Nie wysyłaj do nadawcy
                await self._send_to_connection(subscriber_id, broadcast_data)
    
    async def _send_welcome_message(self, websocket, connection_id: str):
        """Wysyła wiadomość powitalną"""
        welcome = {
            'type': 'welcome',
            'connection_id': connection_id,
            'being': {
                'name': self.essence.name,
                'consciousness_level': self.essence.consciousness_level,
                'specialization': self.context.specialization
            },
            'available_commands': list(self.message_handlers.keys()),
            'timestamp': datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(welcome))
    
    async def _send_to_connection(self, connection_id: str, data: Dict[str, Any]):
        """Wysyła dane do konkretnego połączenia"""
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send(json.dumps(data))
            except websockets.exceptions.ConnectionClosed:
                await self._handle_disconnection(connection_id)
    
    async def _handle_disconnection(self, connection_id: str):
        """Obsługuje rozłączenie"""
        # Usuń z aktywnych połączeń
        self.active_connections.pop(connection_id, None)
        profile = self.connection_profiles.pop(connection_id, None)
        
        # Usuń z wszystkich subskrypcji
        for channel, subscribers in self.subscriptions.items():
            subscribers.discard(connection_id)
        
        if profile:
            self.remember('disconnection', {
                'connection_id': connection_id,
                'duration': str(datetime.now() - profile.connected_at),
                'message_count': profile.message_count
            })
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status WebSocketBeing"""
        base_status = super().get_status()
        
        websocket_status = {
            'websocket_being_specific': {
                'active_connections': len(self.active_connections),
                'total_channels': len(self.subscriptions),
                'total_subscribers': sum(len(subs) for subs in self.subscriptions.values()),
                'message_handlers': list(self.message_handlers.keys()),
                'recent_connections': [
                    {
                        'connection_id': profile.connection_id,
                        'connected_at': profile.connected_at.isoformat(),
                        'message_count': profile.message_count,
                        'subscriptions': list(profile.subscriptions)
                    }
                    for profile in list(self.connection_profiles.values())[-5:]
                ]
            }
        }
        
        base_status.update(websocket_status)
        return base_status
