"""
⚡ WebSocketFlow - Przepływ Komunikacji WebSocket

Zapewnia real-time komunikację z systemem astralnym
"""

import json
import asyncio
import websockets
from typing import Dict, Any, Set, Optional, Callable
from datetime import datetime
import threading
import time


class WebSocketFlow:
    """
    Przepływ WebSocket - real-time komunikacja z systemem astralnym
    """

    def __init__(self, astral_engine, config: Dict[str, Any]):
        self.engine = astral_engine
        self.config = config

        self.host = config.get('host', '0.0.0.0')
        self.port = config.get('port', 5001)

        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.message_handlers: Dict[str, Callable] = {}

        self._running = False
        self._server = None
        self._thread: Optional[threading.Thread] = None

        self.message_count = 0
        self.start_time: Optional[datetime] = None

        self._setup_handlers()

    def _setup_handlers(self):
        """Konfiguruje handlery wiadomości"""

        async def handle_status(websocket, data):
            """Handler dla żądania statusu"""
            try:
                status = self.engine.get_status()
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

        async def handle_meditate(websocket, data):
            """Handler dla medytacji"""
            try:
                meditation_result = self.engine.meditate()

                # Wyślij do requestera
                await self._send_message(websocket, {
                    'type': 'meditation_response',
                    'success': True,
                    'meditation': meditation_result
                })

                # Broadcast do wszystkich klientów
                await self._broadcast({
                    'type': 'meditation_event',
                    'meditation': meditation_result,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })

        async def handle_subscribe_realm(websocket, data):
            """Handler dla subskrypcji zdarzeń wymiaru"""
            realm_name = data.get('realm_name')
            if not realm_name:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': 'Brak nazwy wymiaru'
                })
                return

            try:
                realm = self.engine.get_realm(realm_name)

                # Dodaj znacznik subskrypcji do websocketa
                if not hasattr(websocket, 'subscriptions'):
                    websocket.subscriptions = set()
                websocket.subscriptions.add(f'realm:{realm_name}')

                await self._send_message(websocket, {
                    'type': 'subscription_confirmed',
                    'realm': realm_name,
                    'message': f'Subskrybujesz wydarzenia wymiaru {realm_name}'
                })

            except ValueError as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })

        async def handle_manifest_being(websocket, data):
            """Handler dla manifestacji bytu"""
            realm_name = data.get('realm_name')
            being_data = data.get('being_data', {})

            if not realm_name:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': 'Brak nazwy wymiaru'
                })
                return

            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Wymiar nie obsługuje manifestacji'
                    })
                    return

                being = realm.manifestation.manifest(being_data)

                # Odpowiedź do requestera
                await self._send_message(websocket, {
                    'type': 'manifestation_response',
                    'success': True,
                    'being': being.get_status(),
                    'realm': realm_name
                })

                # Broadcast do subskrybentów wymiaru
                await self._broadcast_to_subscribers(f'realm:{realm_name}', {
                    'type': 'being_manifested',
                    'realm': realm_name,
                    'being': being.get_status(),
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })

        async def handle_contemplate(websocket, data):
            """Handler dla kontemplacji"""
            realm_name = data.get('realm_name')
            intention = data.get('intention', 'find_beings')
            criteria = data.get('criteria', {})

            if not realm_name:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': 'Brak nazwy wymiaru'
                })
                return

            try:
                realm = self.engine.get_realm(realm_name)

                if not hasattr(realm, 'manifestation'):
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Wymiar nie obsługuje kontemplacji'
                    })
                    return

                beings = realm.manifestation.contemplate(intention, criteria)
                beings_data = [being.get_status() for being in beings]

                await self._send_message(websocket, {
                    'type': 'contemplation_response',
                    'success': True,
                    'intention': intention,
                    'criteria': criteria,
                    'beings': beings_data,
                    'count': len(beings_data)
                })

            except Exception as e:
                await self._send_message(websocket, {
                    'type': 'error',
                    'message': str(e)
                })

        # Rejestruj handlery
        self.message_handlers = {
            'get_status': handle_status,
            'meditate': handle_meditate,
            'subscribe_realm': handle_subscribe_realm,
            'manifest_being': handle_manifest_being,
            'contemplate': handle_contemplate
        }

    async def _handle_client(self, websocket, path):
        """Obsługuje połączenie klienta"""
        self.clients.add(websocket)
        websocket.subscriptions = set()

        self.engine.logger.info(f"⚡ Nowy klient WebSocket: {websocket.remote_address}")

        try:
            # Wyślij powitanie
            await self._send_message(websocket, {
                'type': 'welcome',
                'message': 'Witaj w astralnym przepływie WebSocket',
                'available_commands': list(self.message_handlers.keys()),
                'timestamp': datetime.now().isoformat()
            })

            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')

                    if message_type in self.message_handlers:
                        await self.message_handlers[message_type](websocket, data)
                        self.message_count += 1
                    else:
                        await self._send_message(websocket, {
                            'type': 'error',
                            'message': f'Nieznany typ wiadomości: {message_type}',
                            'available_types': list(self.message_handlers.keys())
                        })

                except json.JSONDecodeError:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': 'Nieprawidłowy format JSON'
                    })
                except Exception as e:
                    await self._send_message(websocket, {
                        'type': 'error',
                        'message': f'Błąd przetwarzania: {str(e)}'
                    })

        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.engine.logger.error(f"⚡ Błąd WebSocket: {e}")
        finally:
            self.clients.discard(websocket)
            self.engine.logger.info(f"⚡ Klient WebSocket rozłączony: {websocket.remote_address}")

    async def _send_message(self, websocket, message: Dict[str, Any]):
        """Wysyła wiadomość do konkretnego klienta"""
        try:
            await websocket.send(json.dumps(message, ensure_ascii=False))
        except websockets.exceptions.ConnectionClosed:
            self.clients.discard(websocket)
        except Exception as e:
            self.engine.logger.error(f"⚡ Błąd wysyłania wiadomości: {e}")

    async def _broadcast(self, message: Dict[str, Any]):
        """Broadcast wiadomości do wszystkich klientów"""
        if not self.clients:
            return

        disconnected = set()

        for websocket in self.clients.copy():
            try:
                await websocket.send(json.dumps(message, ensure_ascii=False))
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(websocket)
            except Exception as e:
                self.engine.logger.error(f"⚡ Błąd broadcastu: {e}")
                disconnected.add(websocket)

        # Usuń rozłączone połączenia
        self.clients -= disconnected

    async def _broadcast_to_subscribers(self, subscription: str, message: Dict[str, Any]):
        """Broadcast do klientów z konkretną subskrypcją"""
        if not self.clients:
            return

        disconnected = set()

        for websocket in self.clients.copy():
            if hasattr(websocket, 'subscriptions') and subscription in websocket.subscriptions:
                try:
                    await websocket.send(json.dumps(message, ensure_ascii=False))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
                except Exception as e:
                    self.engine.logger.error(f"⚡ Błąd subskrypcji broadcast: {e}")
                    disconnected.add(websocket)

        # Usuń rozłączone połączenia
        self.clients -= disconnected

    def start(self, debug: bool = False) -> bool:
        """
        Uruchamia przepływ WebSocket

        Args:
            debug: Tryb debug

        Returns:
            True jeśli uruchomiono pomyślnie
        """
        if self._running:
            self.engine.logger.warning("WebSocketFlow już działa")
            return True

        self.start_time = datetime.now()
        self._running = True

        def run_server():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                self._server = websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port
                )

                loop.run_until_complete(self._server)
                loop.run_forever()

            except Exception as e:
                self.engine.logger.error(f"Błąd WebSocket Flow: {e}")
                self._running = False

        self._thread = threading.Thread(target=run_server, daemon=True)
        self._thread.start()

        # Poczekaj na uruchomienie
        time.sleep(1)

        self.engine.logger.info(f"⚡ WebSocket Flow aktywny na ws://{self.host}:{self.port}")
        return True

    def stop(self) -> None:
        """Zatrzymuje przepływ WebSocket"""
        self._running = False

        if self._server:
            self._server.close()

        self.engine.logger.info("⚡ WebSocket Flow zatrzymany")

    def is_running(self) -> bool:
        """Sprawdza czy przepływ działa"""
        return self._running

    def get_status(self) -> Dict[str, Any]:
        """Zwraca status przepływu"""
        return {
            'type': 'websocket_flow',
            'running': self._running,
            'host': self.host,
            'port': self.port,
            'connected_clients': len(self.clients),
            'messages_processed': self.message_count,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
            'available_commands': list(self.message_handlers.keys())
        }

    async def notify_being_event(self, realm_name: str, event_type: str, being_data: Dict[str, Any]):
        """Powiadamia klientów o wydarzeniu związanym z bytem"""
        await self._broadcast_to_subscribers(f'realm:{realm_name}', {
            'type': f'being_{event_type}',
            'realm': realm_name,
            'being': being_data,
            'timestamp': datetime.now().isoformat()
        })

    async def notify_system_event(self, event_type: str, data: Dict[str, Any]):
        """Powiadamia wszystkich klientów o wydarzeniu systemowym"""
        await self._broadcast({
            'type': f'system_{event_type}',
            'data': data,
            'timestamp': datetime.now().isoformat()
        })