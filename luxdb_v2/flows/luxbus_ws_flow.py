
"""
🌐 LuxBus WebSocket Flow - Przepływ WebSocket zintegrowany z LuxBus

Zapewnia real-time komunikację z systemem astralnym przez LuxBus
"""

import asyncio
import websockets
import json
import uuid
from typing import Dict, Any, Set, Optional
from datetime import datetime

from ..core.luxbus_core import LuxBusCore, LuxPacket, PacketType


class LuxBusWebSocketFlow:
    """
    WebSocket Flow zintegrowany z LuxBus Core
    Wszystka komunikacja odbywa się przez system pakietów LuxBus
    """
    
    def __init__(self, astral_engine, config: Dict[str, Any]):
        self.engine = astral_engine
        self.config = config
        
        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', 5001)
        
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.client_subscriptions: Dict[str, Set[str]] = {}
        
        self._running = False
        self._server = None
        
        self.start_time: Optional[datetime] = None
        
        # Integracja z LuxBus
        self.luxbus: LuxBusCore = getattr(engine, 'luxbus', None)
        self.flow_id = f"ws_flow_{uuid.uuid4().hex[:8]}"
        
        if self.luxbus:
            self.luxbus.register_module(self.flow_id, self)
            self.setup_luxbus_handlers()
        
        print(f"🌐 LuxBus WebSocket Flow initialized: {self.flow_id}")
    
    def setup_luxbus_handlers(self):
        """Konfiguruje handlery LuxBus"""
        
        def handle_ws_command(packet: LuxPacket):
            """Obsługuje komendy WebSocket"""
            command_data = packet.data
            command = command_data.get('command')
            params = command_data.get('params', {})
            
            if command == 'broadcast':
                # Broadcast wiadomości do wszystkich klientów
                message = params.get('message')
                target_subscription = params.get('subscription')
                
                asyncio.create_task(self._broadcast_message(message, target_subscription))
            
            elif command == 'send_to_client':
                # Wyślij wiadomość do konkretnego klienta
                client_id = params.get('client_id')
                message = params.get('message')
                
                asyncio.create_task(self._send_to_client(client_id, message))
            
            elif command == 'get_clients':
                # Zwróć listę klientów
                clients_info = {
                    client_id: {
                        'connected_at': 'unknown',  # można dodać tracking
                        'subscriptions': list(self.client_subscriptions.get(client_id, set()))
                    }
                    for client_id in self.clients.keys()
                }
                
                response = LuxPacket(
                    uid=f"ws_clients_response_{packet.uid}",
                    from_id=self.flow_id,
                    to_id=packet.from_id,
                    packet_type=PacketType.RESPONSE,
                    data=clients_info
                )
                
                self.luxbus.send_packet(response)
        
        def handle_system_event(packet: LuxPacket):
            """Obsługuje eventy systemowe do rozgłoszenia"""
            event_data = packet.data
            
            # Wyślij event do wszystkich klientów jako wiadomość WebSocket
            ws_message = {
                'type': 'system_event',
                'event_type': event_data.get('event_type'),
                'data': event_data.get('data'),
                'timestamp': datetime.now().isoformat()
            }
            
            asyncio.create_task(self._broadcast_message(ws_message))
        
        # Subskrybuj komendy i eventy
        if self.luxbus:
            self.luxbus.subscribe_to_packets(self.flow_id, handle_ws_command)
            self.luxbus.subscribe_to_packets('broadcast', handle_system_event)
    
    async def _handle_client(self, websocket, path):
        """Obsługuje połączenie klienta WebSocket"""
        client_id = f"ws_client_{uuid.uuid4().hex[:8]}"
        
        self.clients[client_id] = websocket
        self.client_subscriptions[client_id] = set()
        
        # Dodaj klienta do LuxBus
        if self.luxbus:
            self.luxbus.add_ws_client(websocket)
        
        print(f"🔌 Nowy klient WebSocket: {client_id} from {websocket.remote_address}")
        
        try:
            # Wyślij powitanie
            welcome_message = {
                'type': 'welcome',
                'client_id': client_id,
                'message': 'Witaj w LuxBus WebSocket Flow',
                'luxbus_node': self.luxbus.node_id if self.luxbus else 'unknown',
                'available_commands': [
                    'luxbus_command',
                    'subscribe', 
                    'unsubscribe',
                    'get_status'
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(welcome_message))
            
            # Główna pętla obsługi wiadomości
            async for message in websocket:
                try:
                    await self._handle_client_message(client_id, message)
                except json.JSONDecodeError:
                    error_msg = {
                        'type': 'error',
                        'message': 'Nieprawidłowy format JSON'
                    }
                    await websocket.send(json.dumps(error_msg))
                except Exception as e:
                    error_msg = {
                        'type': 'error',
                        'message': f'Błąd przetwarzania: {str(e)}'
                    }
                    await websocket.send(json.dumps(error_msg))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"🔌 Błąd WebSocket dla {client_id}: {e}")
        finally:
            # Cleanup
            self.clients.pop(client_id, None)
            self.client_subscriptions.pop(client_id, None)
            
            if self.luxbus:
                self.luxbus.remove_ws_client(websocket)
            
            print(f"🔌 Klient WebSocket rozłączony: {client_id}")
    
    async def _handle_client_message(self, client_id: str, message: str):
        """Obsługuje wiadomość od klienta"""
        data = json.loads(message)
        message_type = data.get('type')
        
        client = self.clients[client_id]
        
        if message_type == 'luxbus_command':
            # Przekaż komendę do LuxBus
            target = data.get('target', 'system')
            command = data.get('command')
            params = data.get('params', {})
            
            if self.luxbus and command:
                packet = LuxPacket(
                    uid=f"ws_{uuid.uuid4().hex[:8]}",
                    from_id=client_id,
                    to_id=target,
                    packet_type=PacketType.COMMAND,
                    data={'command': command, 'params': params}
                )
                
                self.luxbus.send_packet(packet)
                
                # Odpowiedź potwierdzająca
                response = {
                    'type': 'command_sent',
                    'target': target,
                    'command': command,
                    'packet_id': packet.uid
                }
                
                await client.send(json.dumps(response))
        
        elif message_type == 'subscribe':
            # Subskrybuj kanał
            subscription = data.get('subscription')
            if subscription:
                self.client_subscriptions[client_id].add(subscription)
                
                response = {
                    'type': 'subscribed',
                    'subscription': subscription,
                    'message': f'Subskrybowano {subscription}'
                }
                
                await client.send(json.dumps(response))
        
        elif message_type == 'unsubscribe':
            # Usuń subskrypcję
            subscription = data.get('subscription')
            if subscription:
                self.client_subscriptions[client_id].discard(subscription)
                
                response = {
                    'type': 'unsubscribed',
                    'subscription': subscription,
                    'message': f'Usunięto subskrypcję {subscription}'
                }
                
                await client.send(json.dumps(response))
        
        elif message_type == 'get_status':
            # Zwróć status przepływu
            status = self.get_status()
            
            response = {
                'type': 'status_response',
                'status': status
            }
            
            await client.send(json.dumps(response))
        
        else:
            # Nieznany typ wiadomości
            error_msg = {
                'type': 'error',
                'message': f'Nieznany typ wiadomości: {message_type}',
                'available_types': ['luxbus_command', 'subscribe', 'unsubscribe', 'get_status']
            }
            
            await client.send(json.dumps(error_msg))
    
    async def _broadcast_message(self, message: Any, target_subscription: str = None):
        """Broadcast wiadomości do klientów"""
        if not self.clients:
            return
        
        message_json = json.dumps(message) if not isinstance(message, str) else message
        disconnected = []
        
        for client_id, client in self.clients.items():
            try:
                # Sprawdź subskrypcję
                if target_subscription:
                    if target_subscription not in self.client_subscriptions.get(client_id, set()):
                        continue
                
                await client.send(message_json)
                
            except websockets.exceptions.ConnectionClosed:
                disconnected.append(client_id)
            except Exception as e:
                print(f"🔌 Błąd broadcastu do {client_id}: {e}")
                disconnected.append(client_id)
        
        # Usuń rozłączone klienty
        for client_id in disconnected:
            self.clients.pop(client_id, None)
            self.client_subscriptions.pop(client_id, None)
    
    async def _send_to_client(self, client_id: str, message: Any):
        """Wysyła wiadomość do konkretnego klienta"""
        if client_id not in self.clients:
            return False
        
        try:
            client = self.clients[client_id]
            message_json = json.dumps(message) if not isinstance(message, str) else message
            await client.send(message_json)
            return True
            
        except Exception as e:
            print(f"🔌 Błąd wysyłania do {client_id}: {e}")
            # Usuń klienta jeśli błąd
            self.clients.pop(client_id, None)
            self.client_subscriptions.pop(client_id, None)
            return False
    
    def start(self, debug: bool = False):
        """Uruchamia przepływ WebSocket"""
        if self._running:
            print("WebSocket Flow już działa")
            return
        
        self.start_time = datetime.now()
        self._running = True
        
        async def start_server():
            try:
                self._server = await websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port
                )
                
                print(f"🌐 LuxBus WebSocket Flow aktywny na ws://{self.host}:{self.port}")
                
                # Poczekaj na zamknięcie
                await self._server.wait_closed()
                
            except Exception as e:
                print(f"❌ Błąd WebSocket Flow: {e}")
                self._running = False
        
        # Uruchom w tle
        asyncio.create_task(start_server())
    
    def stop(self):
        """Zatrzymuje przepływ WebSocket"""
        self._running = False
        
        if self._server:
            self._server.close()
        
        print("🌐 LuxBus WebSocket Flow zatrzymany")
    
    def is_running(self) -> bool:
        """Sprawdza czy przepływ działa"""
        return self._running
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu"""
        return {
            'type': 'luxbus_websocket_flow',
            'flow_id': self.flow_id,
            'running': self._running,
            'host': self.host,
            'port': self.port,
            'connected_clients': len(self.clients),
            'total_subscriptions': sum(len(subs) for subs in self.client_subscriptions.values()),
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
            'luxbus_integration': self.luxbus is not None,
            'luxbus_node': self.luxbus.node_id if self.luxbus else None
        }
    
    def get_info(self) -> Dict[str, Any]:
        """Informacje o module dla LuxBus"""
        return {
            'type': 'LuxBusWebSocketFlow',
            'capabilities': ['real_time_communication', 'luxbus_integration', 'client_subscriptions'],
            'status': 'running' if self._running else 'stopped'
        }
