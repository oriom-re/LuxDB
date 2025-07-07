
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
