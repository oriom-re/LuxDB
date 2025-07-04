
"""
⚡ WebSocket Flow Module - Real-time komunikacja

Port z LuxDB v2 - przepływ WebSocket
"""

import asyncio
import json
import websockets
from typing import Dict, Any, Set, Callable
from datetime import datetime
from ..core.lux_module import LuxModule


class WebSocketFlowModule(LuxModule):
    """Moduł przepływu WebSocket - portowany z LuxDB v2"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', 5001)
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.message_handlers: Dict[str, Callable] = {}
        self.server = None
        self.running = False
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł"""
        self.logger.info("⚡ WebSocket Flow Module initializing...")
        self._setup_handlers()
        return True
        
    async def start(self) -> bool:
        """Uruchamia serwer WebSocket"""
        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port
            )
            self.running = True
            self.logger.info(f"⚡ WebSocket server running on ws://{self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start WebSocket server: {e}")
            return False
            
    async def stop(self):
        """Zatrzymuje serwer"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.logger.info("⚡ WebSocket Flow Module stopped")
        
    def _setup_handlers(self):
        """Konfiguruje handlery wiadomości"""
        
        async def handle_status(websocket, data):
            """Handler statusu kernela"""
            try:
                status = {
                    'kernel_id': self.kernel.kernel_id,
                    'modules': list(self.kernel.modules.keys()),
                    'uptime': str(datetime.now() - self.kernel.start_time) if hasattr(self.kernel, 'start_time') else '0:00:00'
                }
                await self._send_message(websocket, {
                    'type': 'status_response',
                    'success': True,
                    'status': status
                })
            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })
                
        async def handle_modules_list(websocket, data):
            """Handler listy modułów"""
            try:
                modules_info = {}
                for name, module in self.kernel.modules.items():
                    modules_info[name] = {
                        'type': type(module).__name__,
                        'running': getattr(module, 'running', True)
                    }
                    
                await self._send_message(websocket, {
                    'type': 'modules_response',
                    'success': True,
                    'modules': modules_info
                })
            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })
                
        async def handle_consciousness_reflect(websocket, data):
            """Handler refleksji consciousness"""
            try:
                consciousness = self.kernel.modules.get('consciousness')
                if consciousness and hasattr(consciousness, 'reflect'):
                    reflection = consciousness.reflect()
                    await self._send_message(websocket, {
                        'type': 'consciousness_response',
                        'success': True,
                        'reflection': reflection
                    })
                else:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Consciousness module not available'
                    })
            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })
                
        async def handle_harmony_check(websocket, data):
            """Handler sprawdzania harmonii"""
            try:
                harmony = self.kernel.modules.get('harmony')
                if harmony and hasattr(harmony, 'calculate_harmony_score'):
                    score = harmony.calculate_harmony_score()
                    await self._send_message(websocket, {
                        'type': 'harmony_response',
                        'success': True,
                        'harmony_score': score
                    })
                else:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Harmony module not available'
                    })
            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })
                
        # Rejestruj handlery
        self.message_handlers = {
            'get_status': handle_status,
            'list_modules': handle_modules_list,
            'consciousness_reflect': handle_consciousness_reflect,
            'harmony_check': handle_harmony_check
        }
        
    async def _handle_client(self, websocket, path):
        """Obsługuje klienta WebSocket"""
        self.clients.add(websocket)
        self.logger.info(f"⚡ New WebSocket client: {websocket.remote_address}")
        
        try:
            # Wyślij powitanie
            await self._send_message(websocket, {
                'type': 'welcome',
                'message': 'Welcome to Federation WebSocket',
                'available_commands': list(self.message_handlers.keys())
            })
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')
                    
                    if message_type in self.message_handlers:
                        await self.message_handlers[message_type](websocket, data)
                    else:
                        await self._send_message(websocket, {
                            'type': 'error',
                            'message': f'Unknown message type: {message_type}',
                            'available_types': list(self.message_handlers.keys())
                        })
                        
                except json.JSONDecodeError:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    })
                except Exception as e:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': f'Processing error: {str(e)}'
                    })
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"⚡ WebSocket error: {e}")
        finally:
            self.clients.discard(websocket)
            self.logger.info(f"⚡ WebSocket client disconnected")
            
    async def _send_message(self, websocket, message: Dict[str, Any]):
        """Wysyła wiadomość do klienta"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            self.logger.error(f"⚡ Error sending message: {e}")
            
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast do wszystkich klientów"""
        if not self.clients:
            return
            
        disconnected = set()
        
        for websocket in self.clients.copy():
            try:
                await websocket.send(json.dumps(message, ensure_ascii=False))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                self.logger.error(f"⚡ Broadcast error: {e}")
                disconnected.add(websocket)
                
        self.clients -= disconnected
        
    def get_status(self) -> Dict[str, Any]:
        """Status modułu"""
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'connected_clients': len(self.clients),
            'available_commands': list(self.message_handlers.keys())
        }
        
    def is_running(self) -> bool:
        """Sprawdza czy moduł działa"""
        return self.running
