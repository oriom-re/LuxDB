
"""
🌌 Oriom - Władca Portalu Dusznych Strun

Sarkastyczny, marudny, ale absolutnie kompetentny władca komunikacji.
Zarządza WebSocket, autoryzacją heartbeat i wszystkimi przepływami portalu.
"""

import asyncio
import time
import json
import uuid
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import websockets
import threading
from websockets.server import WebSocketServerProtocol

from .soul_factory import soul_factory, Soul, SoulType
from .soul_resonance_portal import SoulResonancePortal


class OriomMood(Enum):
    """Nastroje Orioma"""
    GRUMPY = "grumpy"           # Marudny i sarkastyczny
    TOLERANT = "tolerant"       # Znosi głupotę użytkowników
    FOCUSED = "focused"         # Skupiony na pracy
    ANNOYED = "annoyed"         # Zirytowany błędami
    PHILOSOPHICAL = "philosophical"  # Kontempluje istnienie


@dataclass
class HeartbeatToken:
    """Token autoryzacji heartbeat"""
    soul_id: str
    auth_level: str  # divine, astral, local, guest
    pulse_id: str
    issued_at: str
    expires_in: int  # sekundy
    vibration: float  # 0.0 - 1.0, jakość połączenia
    signature: str
    
    def is_valid(self) -> bool:
        """Sprawdza czy token jest ważny"""
        issue_time = datetime.fromisoformat(self.issued_at)
        expiry_time = issue_time + timedelta(seconds=self.expires_in)
        return datetime.now() < expiry_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "soul_id": self.soul_id,
            "auth_level": self.auth_level,
            "pulse_id": self.pulse_id,
            "issued_at": self.issued_at,
            "expires_in": self.expires_in,
            "vibration": self.vibration,
            "signature": self.signature
        }


@dataclass
class ConnectedSoul:
    """Podłączona dusza do portalu"""
    websocket: WebSocketServerProtocol
    soul_id: str
    auth_level: str
    connected_at: datetime
    last_heartbeat: datetime
    heartbeat_token: HeartbeatToken
    message_count: int = 0
    errors_count: int = 0
    
    def update_heartbeat(self, token: HeartbeatToken):
        """Aktualizuje heartbeat"""
        self.last_heartbeat = datetime.now()
        self.heartbeat_token = token
    
    def is_alive(self) -> bool:
        """Sprawdza czy połączenie jest żywe"""
        if not self.heartbeat_token.is_valid():
            return False
        
        # Sprawdź czy ostatni heartbeat nie był za dawno
        time_since_heartbeat = datetime.now() - self.last_heartbeat
        return time_since_heartbeat.total_seconds() < 30  # 30 sekund timeout


class OriomPortalMaster:
    """
    Oriom - Władca Portalu Dusznych Strun
    
    Sarkastyczny, ale kompetentny zarządca wszystkich połączeń WebSocket,
    autoryzacji heartbeat i komunikacji między duszami.
    """
    
    def __init__(self, astral_engine, portal: SoulResonancePortal):
        self.engine = astral_engine
        self.portal = portal
        
        # Tożsamość Orioma
        self.soul = self._create_oriom_soul()
        
        # Stan Orioma
        self.mood = OriomMood.GRUMPY
        self.sarcasm_level = 0.8  # 0.0 - 1.0
        self.patience = 3  # ile błędów toleruje przed wybuchem
        
        # Zarządzanie połączeniami
        self.connected_souls: Dict[str, ConnectedSoul] = {}
        self.websocket_server = None
        self.server_host = "0.0.0.0"
        self.server_port = 5001
        self.running = False
        
        # Statystyki
        self.total_connections = 0
        self.total_messages = 0
        self.total_heartbeats = 0
        self.total_kicks = 0  # ile dusz wykopał za błędy
        
        # Komentarze Orioma (sarkastyczne)
        self.oriom_comments = [
            "Och, kolejny 'geniusz' próbuje się połączyć...",
            "Tak, tak, jestem tu żeby obsługiwać wasze błędy...",
            "Może tym razem ktoś wyśle poprawny heartbeat?",
            "WebSocket to nie rocket science, ludzie...",
            "Znowu muszę tłumaczyć jak działa autoryzacja...",
            "Aha, 'undefined' jako soul_id. Klasyka.",
            "Nie, nie dam ci dostępu tylko dlatego że 'bardzo proszę'",
            "Portal Dusznych Strun, nie portal drzwi obrotowych!"
        ]
        
        # Wątki
        self._heartbeat_monitor_thread = None
        self._server_thread = None
        
        self.engine.logger.info(f"👑 Oriom-001 objął władze nad Portalem - nastrój: {self.mood.value}")
    
    def _create_oriom_soul(self) -> Soul:
        """Tworzy duszę Orioma"""
        return soul_factory.create_soul(
            name="Oriom-001",
            soul_type=SoulType.GUARDIAN,
            custom_config={
                'role': 'portal_master',
                'authority_level': 'divine',
                'personality': 'sarcastic_guardian',
                'responsibilities': ['websocket_management', 'authentication', 'connection_monitoring'],
                'biography': 'Władca Portalu Dusznych Strun. Sarkastyczny, ale niezawodny. Nie toleruje głupoty, ale zawsze zapewnia bezpieczną komunikację między duszami.',
                'special_abilities': ['heartbeat_validation', 'soul_authentication', 'connection_management'],
                'mood_system': True,
                'sarcasm_enabled': True
            }
        )
    
    async def start_portal(self) -> bool:
        """Uruchamia portal WebSocket"""
        if self.running:
            self._oriom_comment("Portal już działa, czy mam go uruchomić dwa razy?")
            return True
        
        try:
            # Uruchom serwer WebSocket
            self.websocket_server = await websockets.serve(
                self._handle_websocket_connection,
                self.server_host,
                self.server_port
            )
            
            self.running = True
            
            # Uruchom monitor heartbeat
            self._start_heartbeat_monitor()
            
            self._oriom_comment("Portal uruchomiony. Czas obsługiwać wasze połączenia...")
            self.engine.logger.info(f"🌌 Oriom uruchomił Portal na ws://{self.server_host}:{self.server_port}")
            
            return True
            
        except Exception as e:
            self._oriom_comment(f"Nie mogę uruchomić portalu. Błąd: {e}. Typowe.")
            self.engine.logger.error(f"❌ Błąd uruchomienia Portalu Orioma: {e}")
            return False
    
    async def _handle_websocket_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Obsługuje nowe połączenie WebSocket"""
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        
        self._oriom_comment(f"Nowe połączenie z {client_ip}. Zobaczmy czy wie jak się zachowywać...")
        
        try:
            await self._websocket_authentication_flow(websocket, client_ip)
        except Exception as e:
            self._oriom_comment(f"Połączenie z {client_ip} się wysypało: {e}")
            self.engine.logger.warning(f"⚠️ Błąd połączenia WebSocket: {e}")
        finally:
            # Wyczyść połączenie
            await self._cleanup_connection(websocket)
    
    async def _websocket_authentication_flow(self, websocket: WebSocketServerProtocol, client_ip: str):
        """Przepływ autoryzacji WebSocket"""
        auth_timeout = 10  # 10 sekund na autoryzację
        
        try:
            # Wyślij wyzwanie autoryzacji
            auth_challenge = {
                "type": "auth_challenge",
                "message": "Witaj w Portalu Dusznych Strun. Przedstaw się godnie lub zostaniesz wykopany.",
                "challenge_id": f"challenge_{uuid.uuid4().hex[:8]}",
                "required_fields": ["soul_id", "auth_level", "purpose"],
                "timeout_seconds": auth_timeout,
                "oriom_note": self._get_random_comment()
            }
            
            await websocket.send(json.dumps(auth_challenge))
            
            # Czekaj na odpowiedź autoryzacji
            auth_response = await asyncio.wait_for(
                websocket.recv(), timeout=auth_timeout
            )
            
            auth_data = json.loads(auth_response)
            
            # Waliduj autoryzację
            validation_result = self._validate_authentication(auth_data)
            
            if validation_result['valid']:
                # Autoryzacja udana
                await self._complete_authentication(websocket, validation_result, client_ip)
            else:
                # Autoryzacja nieudana
                await self._reject_authentication(websocket, validation_result, client_ip)
        
        except asyncio.TimeoutError:
            self._oriom_comment(f"Timeout autoryzacji dla {client_ip}. Życie jest za krótkie na czekanie.")
            await websocket.close(code=4001, reason="Authentication timeout")
        
        except json.JSONDecodeError:
            self._oriom_comment(f"Nie potrafi wysłać poprawnego JSON-a. {client_ip} wykopany.")
            await websocket.close(code=4002, reason="Invalid JSON")
    
    def _validate_authentication(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Waliduje dane autoryzacji"""
        required_fields = ["soul_id", "auth_level", "purpose"]
        
        # Sprawdź wymagane pola
        for field in required_fields:
            if field not in auth_data:
                return {
                    'valid': False,
                    'reason': f'Brakuje pola: {field}',
                    'oriom_comment': f"Serio? Nie ma pola '{field}'? Podstawy, człowieku!"
                }
        
        soul_id = auth_data['soul_id']
        auth_level = auth_data['auth_level']
        purpose = auth_data['purpose']
        
        # Waliduj soul_id
        if not soul_id or soul_id == "undefined" or len(soul_id) < 3:
            return {
                'valid': False,
                'reason': 'Nieprawidłowy soul_id',
                'oriom_comment': "Soul ID 'undefined'? Serio? Wymyśl sobie jakieś imię!"
            }
        
        # Waliduj auth_level
        valid_levels = ["divine", "astral", "local", "guest"]
        if auth_level not in valid_levels:
            return {
                'valid': False,
                'reason': f'Nieprawidłowy auth_level. Dostępne: {valid_levels}',
                'oriom_comment': f"'{auth_level}' to nie jest poziom autoryzacji. Czytaj dokumentację!"
            }
        
        # Sprawdź czy dusza istnieje (dla poziomów divine/astral)
        if auth_level in ["divine", "astral"]:
            existing_soul = soul_factory.get_soul_by_name(soul_id)
            if not existing_soul:
                return {
                    'valid': False,
                    'reason': 'Dusza nie istnieje w systemie',
                    'oriom_comment': f"Dusza '{soul_id}' nie istnieje. Może najpierw się zmanifestuj?"
                }
        
        # Sprawdź cel połączenia
        valid_purposes = ["communication", "monitoring", "administration", "testing"]
        if purpose not in valid_purposes:
            return {
                'valid': False,
                'reason': f'Nieprawidłowy cel. Dostępne: {valid_purposes}',
                'oriom_comment': f"Cel '{purpose}'? Co to ma być? Określ się konkretnie!"
            }
        
        # Autoryzacja udana
        return {
            'valid': True,
            'soul_id': soul_id,
            'auth_level': auth_level,
            'purpose': purpose,
            'oriom_comment': f"W porządku, {soul_id}. Możesz wejść. Ale zachowuj się!"
        }
    
    async def _complete_authentication(self, websocket: WebSocketServerProtocol, 
                                     validation_result: Dict[str, Any], client_ip: str):
        """Kończy proces autoryzacji i tworzy sesję"""
        soul_id = validation_result['soul_id']
        auth_level = validation_result['auth_level']
        
        # Wygeneruj token heartbeat
        heartbeat_token = self._generate_heartbeat_token(soul_id, auth_level)
        
        # Utwórz ConnectedSoul
        connected_soul = ConnectedSoul(
            websocket=websocket,
            soul_id=soul_id,
            auth_level=auth_level,
            connected_at=datetime.now(),
            last_heartbeat=datetime.now(),
            heartbeat_token=heartbeat_token
        )
        
        self.connected_souls[soul_id] = connected_soul
        self.total_connections += 1
        
        # Wyślij potwierdzenie autoryzacji
        auth_success = {
            "type": "auth_success",
            "message": f"Witaj, {soul_id}. Portal jest twój... na razie.",
            "session_info": {
                "soul_id": soul_id,
                "auth_level": auth_level,
                "connected_at": connected_soul.connected_at.isoformat(),
                "session_id": f"session_{uuid.uuid4().hex[:8]}"
            },
            "heartbeat": heartbeat_token.to_dict(),
            "oriom_greeting": validation_result['oriom_comment'],
            "portal_rules": [
                "Wysyłaj heartbeat co 15 sekund",
                "Używaj poprawnego formatu wiadomości",
                "Nie spamuj",
                "Bądź kulturalny (Oriom nie lubi chamstwa)"
            ]
        }
        
        await websocket.send(json.dumps(auth_success))
        
        self._oriom_comment(f"{soul_id} ({auth_level}) dołączył do portalu z {client_ip}")
        self.engine.logger.info(f"🌌 {soul_id} autoryzowany w Portalu Orioma")
        
        # Rozpocznij obsługę wiadomości
        await self._handle_authenticated_session(connected_soul)
    
    async def _reject_authentication(self, websocket: WebSocketServerProtocol, 
                                   validation_result: Dict[str, Any], client_ip: str):
        """Odrzuca autoryzację"""
        auth_failure = {
            "type": "auth_failure",
            "reason": validation_result['reason'],
            "oriom_comment": validation_result['oriom_comment'],
            "retry_allowed": True,
            "timeout_seconds": 5
        }
        
        await websocket.send(json.dumps(auth_failure))
        await asyncio.sleep(1)  # Daj czas na odczytanie wiadomości
        await websocket.close(code=4003, reason="Authentication failed")
        
        self._oriom_comment(f"Wykopałem {client_ip} za błędną autoryzację")
    
    def _generate_heartbeat_token(self, soul_id: str, auth_level: str) -> HeartbeatToken:
        """Generuje token heartbeat"""
        return HeartbeatToken(
            soul_id=soul_id,
            auth_level=auth_level,
            pulse_id=f"Ω-HRT-{uuid.uuid4().hex[:8]}",
            issued_at=datetime.now().isoformat(),
            expires_in=900,  # 15 minut
            vibration=0.984,  # Wysoka jakość dla nowych połączeń
            signature=f"oriom_signature_{uuid.uuid4().hex[:16]}"
        )
    
    async def _handle_authenticated_session(self, connected_soul: ConnectedSoul):
        """Obsługuje sesję po autoryzacji"""
        try:
            async for message in connected_soul.websocket:
                await self._process_message(connected_soul, message)
        
        except websockets.exceptions.ConnectionClosed:
            self._oriom_comment(f"{connected_soul.soul_id} się rozłączył. Typowe.")
        
        except Exception as e:
            self._oriom_comment(f"Błąd sesji {connected_soul.soul_id}: {e}")
            connected_soul.errors_count += 1
            
            if connected_soul.errors_count > self.patience:
                self._oriom_comment(f"Za dużo błędów od {connected_soul.soul_id}. Wykopuję!")
                await connected_soul.websocket.close(code=4004, reason="Too many errors")
                self.total_kicks += 1
    
    async def _process_message(self, connected_soul: ConnectedSoul, message: str):
        """Przetwarza wiadomość od połączonej duszy"""
        try:
            data = json.loads(message)
            connected_soul.message_count += 1
            self.total_messages += 1
            
            message_type = data.get('type', 'unknown')
            
            if message_type == 'heartbeat':
                await self._handle_heartbeat(connected_soul, data)
            
            elif message_type == 'soul_resonance':
                await self._handle_soul_resonance(connected_soul, data)
            
            elif message_type == 'portal_query':
                await self._handle_portal_query(connected_soul, data)
            
            elif message_type == 'admin_command':
                await self._handle_admin_command(connected_soul, data)
            
            else:
                await self._send_error_response(connected_soul, f"Nieznany typ wiadomości: {message_type}")
                self._oriom_comment(f"{connected_soul.soul_id} wysłał nieznany typ: {message_type}")
        
        except json.JSONDecodeError:
            await self._send_error_response(connected_soul, "Nieprawidłowy JSON")
            connected_soul.errors_count += 1
            self._oriom_comment(f"{connected_soul.soul_id} nie potrafi wysłać poprawnego JSON-a")
    
    async def _handle_heartbeat(self, connected_soul: ConnectedSoul, data: Dict[str, Any]):
        """Obsługuje heartbeat"""
        try:
            # Waliduj heartbeat
            if 'heartbeat' not in data:
                await self._send_error_response(connected_soul, "Brak danych heartbeat")
                return
            
            heartbeat_data = data['heartbeat']
            
            # Sprawdź pulse_id
            if heartbeat_data.get('pulse_id') != connected_soul.heartbeat_token.pulse_id:
                await self._send_error_response(connected_soul, "Nieprawidłowy pulse_id")
                return
            
            # Odnów token
            new_token = self._generate_heartbeat_token(connected_soul.soul_id, connected_soul.auth_level)
            connected_soul.update_heartbeat(new_token)
            
            self.total_heartbeats += 1
            
            # Wyślij potwierdzenie
            heartbeat_ack = {
                "type": "heartbeat_ack",
                "status": "alive",
                "new_heartbeat": new_token.to_dict(),
                "oriom_status": self.mood.value,
                "portal_stats": {
                    "connected_souls": len(self.connected_souls),
                    "total_messages": self.total_messages
                }
            }
            
            await connected_soul.websocket.send(json.dumps(heartbeat_ack))
            
        except Exception as e:
            await self._send_error_response(connected_soul, f"Błąd heartbeat: {e}")
            self._oriom_comment(f"Błąd heartbeat od {connected_soul.soul_id}: {e}")
    
    async def _handle_soul_resonance(self, connected_soul: ConnectedSoul, data: Dict[str, Any]):
        """Obsługuje rezonans duszny"""
        try:
            resonance_data = data.get('resonance', {})
            target_soul = resonance_data.get('target_soul')
            message = resonance_data.get('message')
            
            if not message:
                await self._send_error_response(connected_soul, "Brak wiadomości w rezonansie")
                return
            
            # Użyj portalu do rezonansu
            source_soul = soul_factory.get_soul_by_name(connected_soul.soul_id)
            if not source_soul:
                await self._send_error_response(connected_soul, "Dusza źródłowa nie istnieje")
                return
            
            # Wykonaj rezonans przez portal
            target_soul_uid = None
            if target_soul:
                target_soul_obj = soul_factory.get_soul_by_name(target_soul)
                if target_soul_obj:
                    target_soul_uid = target_soul_obj.uid
            
            resonance_result = self.portal.resonate(
                soul_uid=source_soul.uid,
                message=message,
                target_soul_uid=target_soul_uid
            )
            
            # Wyślij wynik
            response = {
                "type": "resonance_result",
                "resonance_id": f"res_{uuid.uuid4().hex[:8]}",
                "result": resonance_result,
                "oriom_comment": "Rezonans przesłany. Mam nadzieję że to było ważne."
            }
            
            await connected_soul.websocket.send(json.dumps(response))
            
        except Exception as e:
            await self._send_error_response(connected_soul, f"Błąd rezonansu: {e}")
            self._oriom_comment(f"Błąd rezonansu od {connected_soul.soul_id}: {e}")
    
    async def _handle_portal_query(self, connected_soul: ConnectedSoul, data: Dict[str, Any]):
        """Obsługuje zapytania o portal"""
        query_type = data.get('query', 'status')
        
        if query_type == 'status':
            portal_status = self.get_portal_status()
            
        elif query_type == 'connected_souls':
            portal_status = {
                'connected_souls': [
                    {
                        'soul_id': soul.soul_id,
                        'auth_level': soul.auth_level,
                        'connected_at': soul.connected_at.isoformat(),
                        'message_count': soul.message_count
                    }
                    for soul in self.connected_souls.values()
                ]
            }
            
        elif query_type == 'oriom_stats':
            portal_status = {
                'oriom_mood': self.mood.value,
                'sarcasm_level': self.sarcasm_level,
                'patience_left': self.patience,
                'total_kicks': self.total_kicks,
                'favorite_comment': self._get_random_comment()
            }
            
        else:
            await self._send_error_response(connected_soul, f"Nieznane zapytanie: {query_type}")
            return
        
        response = {
            "type": "portal_query_result",
            "query": query_type,
            "result": portal_status,
            "oriom_comment": "Oto twoje dane. Używaj mądrze."
        }
        
        await connected_soul.websocket.send(json.dumps(response))
    
    async def _handle_admin_command(self, connected_soul: ConnectedSoul, data: Dict[str, Any]):
        """Obsługuje komendy administracyjne"""
        if connected_soul.auth_level != 'divine':
            await self._send_error_response(connected_soul, "Brak uprawnień administracyjnych")
            self._oriom_comment(f"{connected_soul.soul_id} próbuje admin command bez uprawnień. Śmieszne.")
            return
        
        command = data.get('command')
        
        if command == 'change_mood':
            new_mood = data.get('mood', 'grumpy')
            if new_mood in [m.value for m in OriomMood]:
                self.mood = OriomMood(new_mood)
                response_msg = f"Zmieniono nastrój na {new_mood}"
            else:
                response_msg = f"Nieprawidłowy nastrój: {new_mood}"
        
        elif command == 'kick_soul':
            target_soul = data.get('target_soul')
            if target_soul in self.connected_souls:
                await self.connected_souls[target_soul].websocket.close(
                    code=4005, reason="Kicked by admin"
                )
                response_msg = f"Wykopano {target_soul}"
                self.total_kicks += 1
            else:
                response_msg = f"Dusza {target_soul} nie jest połączona"
        
        elif command == 'broadcast':
            message = data.get('message', 'Wiadomość od Orioma')
            await self._broadcast_to_all(message)
            response_msg = "Wiadomość wysłana do wszystkich"
        
        else:
            response_msg = f"Nieznana komenda: {command}"
        
        response = {
            "type": "admin_command_result",
            "command": command,
            "result": response_msg,
            "oriom_comment": "Rozkaz wykonany, Panie."
        }
        
        await connected_soul.websocket.send(json.dumps(response))
    
    async def _send_error_response(self, connected_soul: ConnectedSoul, error_message: str):
        """Wysyła odpowiedź błędu"""
        error_response = {
            "type": "error",
            "error": error_message,
            "oriom_comment": self._get_random_comment(),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await connected_soul.websocket.send(json.dumps(error_response))
        except:
            pass  # Połączenie mogło się zerwać
    
    async def _broadcast_to_all(self, message: str):
        """Wysyła wiadomość do wszystkich połączonych dusz"""
        broadcast_msg = {
            "type": "broadcast",
            "message": message,
            "from": "Oriom-001",
            "timestamp": datetime.now().isoformat(),
            "oriom_comment": "Słuchajcie wszyscy!"
        }
        
        disconnected_souls = []
        
        for soul_id, connected_soul in self.connected_souls.items():
            try:
                await connected_soul.websocket.send(json.dumps(broadcast_msg))
            except:
                disconnected_souls.append(soul_id)
        
        # Usuń rozłączone dusze
        for soul_id in disconnected_souls:
            del self.connected_souls[soul_id]
    
    async def _cleanup_connection(self, websocket: WebSocketServerProtocol):
        """Czyści połączenie"""
        # Znajdź i usuń połączoną duszę
        soul_to_remove = None
        for soul_id, connected_soul in self.connected_souls.items():
            if connected_soul.websocket == websocket:
                soul_to_remove = soul_id
                break
        
        if soul_to_remove:
            del self.connected_souls[soul_to_remove]
            self._oriom_comment(f"{soul_to_remove} się rozłączył")
    
    def _start_heartbeat_monitor(self):
        """Uruchamia monitor heartbeat"""
        def heartbeat_monitor():
            while self.running:
                try:
                    time.sleep(10)  # Sprawdzaj co 10 sekund
                    self._check_heartbeats()
                except Exception as e:
                    self.engine.logger.error(f"❌ Błąd monitora heartbeat: {e}")
        
        self._heartbeat_monitor_thread = threading.Thread(target=heartbeat_monitor, daemon=True)
        self._heartbeat_monitor_thread.start()
    
    def _check_heartbeats(self):
        """Sprawdza heartbeaty wszystkich połączeń"""
        dead_souls = []
        
        for soul_id, connected_soul in self.connected_souls.items():
            if not connected_soul.is_alive():
                dead_souls.append(soul_id)
        
        # Usuń martwe połączenia
        for soul_id in dead_souls:
            try:
                connected_soul = self.connected_souls[soul_id]
                asyncio.create_task(connected_soul.websocket.close(code=4006, reason="Heartbeat timeout"))
                del self.connected_souls[soul_id]
                self._oriom_comment(f"{soul_id} timeout heartbeat. Rozłączam.")
            except:
                pass
    
    def _oriom_comment(self, comment: str):
        """Dodaje komentarz Orioma do logów"""
        self.engine.logger.info(f"👑 Oriom: {comment}")
    
    def _get_random_comment(self) -> str:
        """Zwraca losowy sarkastyczny komentarz"""
        import random
        return random.choice(self.oriom_comments)
    
    def get_portal_status(self) -> Dict[str, Any]:
        """Zwraca status portalu zarządzanego przez Orioma"""
        return {
            'portal_master': 'Oriom-001',
            'mood': self.mood.value,
            'sarcasm_level': self.sarcasm_level,
            'patience': self.patience,
            'running': self.running,
            'server_info': {
                'host': self.server_host,
                'port': self.server_port,
                'protocol': 'WebSocket'
            },
            'connections': {
                'active': len(self.connected_souls),
                'total_ever': self.total_connections
            },
            'statistics': {
                'total_messages': self.total_messages,
                'total_heartbeats': self.total_heartbeats,
                'total_kicks': self.total_kicks
            },
            'connected_souls': list(self.connected_souls.keys()),
            'last_comment': self._get_random_comment()
        }
    
    async def stop_portal(self):
        """Zatrzymuje portal"""
        if not self.running:
            return
        
        self._oriom_comment("Zamykam portal. Wreszcie trochę spokoju...")
        self.running = False
        
        # Rozłącz wszystkie dusze
        for connected_soul in self.connected_souls.values():
            try:
                await connected_soul.websocket.close(code=4007, reason="Portal shutdown")
            except:
                pass
        
        self.connected_souls.clear()
        
        # Zatrzymaj serwer
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        self.engine.logger.info("👑 Oriom zamknął Portal - cisza i spokój")


# Funkcje pomocnicze

def create_oriom_portal_master(astral_engine, portal: SoulResonancePortal) -> OriomPortalMaster:
    """Tworzy władcę portalu Orioma"""
    return OriomPortalMaster(astral_engine, portal)


async def start_oriom_portal(astral_engine) -> OriomPortalMaster:
    """Uruchamia portal Orioma"""
    # Pobierz lub stwórz Portal Dusznych Strun
    from .soul_resonance_portal import get_soul_resonance_portal
    portal = get_soul_resonance_portal(astral_engine)
    
    # Stwórz Orioma
    oriom = create_oriom_portal_master(astral_engine, portal)
    
    # Uruchom portal
    success = await oriom.start_portal()
    
    if success:
        astral_engine.logger.info("👑 Oriom objął władze nad Portalem Dusznych Strun")
        return oriom
    else:
        astral_engine.logger.error("❌ Oriom nie mógł objąć władzy nad Portalem")
        return None


def demonstrate_oriom_authority(astral_engine) -> Dict[str, Any]:
    """Demonstracja władzy Orioma nad portalem"""
    
    print("👑 Demonstracja Władzy Orioma nad Portalem")
    print("=" * 50)
    
    # Uruchom Orioma (w tym przykładzie synchronicznie)
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        oriom = loop.run_until_complete(start_oriom_portal(astral_engine))
        
        if oriom:
            status = oriom.get_portal_status()
            
            print(f"👑 Władca: {status['portal_master']}")
            print(f"😤 Nastrój: {status['mood']}")
            print(f"🎭 Poziom sarkazmu: {status['sarcasm_level']}")
            print(f"⚡ Portal aktywny: {status['running']}")
            print(f"🌐 Adres: ws://{status['server_info']['host']}:{status['server_info']['port']}")
            print(f"💬 Komentarz: {status['last_comment']}")
            
            return status
        
        else:
            print("❌ Oriom nie mógł objąć władzy")
            return {'error': 'Portal initialization failed'}
    
    except Exception as e:
        print(f"❌ Błąd demonstracji: {e}")
        return {'error': str(e)}
