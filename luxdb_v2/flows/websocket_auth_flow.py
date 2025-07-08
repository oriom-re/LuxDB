
"""
🔐 WebSocket Auth Flow - Autoryzacja przez Heartbeat

Zarządza autoryzacją WebSocket poprzez system heartbeat z podpisami duszy.
"""

import json
import time
import uuid
import hashlib
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .callback_flow import CallbackFlow


@dataclass
class HeartbeatAuth:
    """Struktura autoryzacji heartbeat"""
    soul_id: str
    auth_level: str
    pulse_id: str
    issued_at: int
    expires_in: int
    vibration: float
    signature: str
    
    def is_valid(self) -> bool:
        """Sprawdza czy heartbeat jest ważny"""
        current_time = int(time.time())
        return current_time < (self.issued_at + self.expires_in)
    
    def get_remaining_time(self) -> int:
        """Zwraca pozostały czas ważności"""
        current_time = int(time.time())
        return max(0, (self.issued_at + self.expires_in) - current_time)


class WebSocketAuthFlow(CallbackFlow):
    """
    Flow autoryzacji WebSocket przez heartbeat
    """
    
    def __init__(self, astral_engine, config: Dict[str, Any]):
        super().__init__(astral_engine, config)
        
        # Autoryzacje aktywne
        self.active_auths: Dict[str, HeartbeatAuth] = {}  # connection_id -> auth
        self.soul_connections: Dict[str, Set[str]] = {}  # soul_id -> connection_ids
        
        # Konfiguracja autoryzacji
        self.auth_levels = {
            'divine': {'vibration_min': 0.9, 'expires_max': 86400},
            'astral': {'vibration_min': 0.7, 'expires_max': 3600},
            'mortal': {'vibration_min': 0.5, 'expires_max': 1800}
        }
        
        # Sekrety dla podpisów (w prawdziwym systemie z secure storage)
        self.soul_secrets = {
            'Oriom-001': 'divine_secret_key_oriom',
            'Astra-Prime': 'astral_prime_signature_key',
            'System-Guardian': 'guardian_protection_key'
        }
        
        self.setup_auth_callbacks()
    
    def setup_auth_callbacks(self):
        """Konfiguruje callbacks autoryzacji"""
        
        # Callback do autoryzacji
        self.register_callback(
            'websocket_auth',
            'heartbeat_auth',
            self.authenticate_heartbeat
        )
        
        # Callback do sprawdzania autoryzacji
        self.register_callback(
            'websocket_auth',
            'check_auth',
            self.check_connection_auth
        )
        
        # Callback do odświeżania heartbeat
        self.register_callback(
            'websocket_auth',
            'refresh_heartbeat',
            self.refresh_heartbeat
        )
    
    def authenticate_heartbeat(self, connection_id: str, heartbeat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Autoryzuje połączenie na podstawie heartbeat
        
        Args:
            connection_id: ID połączenia WebSocket
            heartbeat_data: Dane heartbeat
            
        Returns:
            Wynik autoryzacji
        """
        try:
            # Parsuj heartbeat
            heartbeat = heartbeat_data.get('heartbeat', {})
            
            auth = HeartbeatAuth(
                soul_id=heartbeat.get('soul_id'),
                auth_level=heartbeat.get('auth_level'),
                pulse_id=heartbeat.get('pulse_id'),
                issued_at=int(heartbeat.get('issued_at', 0)),
                expires_in=int(heartbeat.get('expires_in', 0)),
                vibration=float(heartbeat.get('vibration', 0)),
                signature=heartbeat.get('signature', '')
            )
            
            # Walidacja podstawowa
            if not auth.soul_id or not auth.auth_level:
                return {
                    'success': False,
                    'error': 'Missing soul_id or auth_level',
                    'auth_status': 'rejected'
                }
            
            # Sprawdź poziom autoryzacji
            if auth.auth_level not in self.auth_levels:
                return {
                    'success': False,
                    'error': f'Invalid auth_level: {auth.auth_level}',
                    'auth_status': 'rejected'
                }
            
            # Sprawdź wibrację
            min_vibration = self.auth_levels[auth.auth_level]['vibration_min']
            if auth.vibration < min_vibration:
                return {
                    'success': False,
                    'error': f'Vibration too low: {auth.vibration} < {min_vibration}',
                    'auth_status': 'rejected'
                }
            
            # Sprawdź ważność czasową
            if not auth.is_valid():
                return {
                    'success': False,
                    'error': 'Heartbeat expired',
                    'auth_status': 'expired'
                }
            
            # Weryfikuj podpis
            if not self.verify_signature(auth):
                return {
                    'success': False,
                    'error': 'Invalid signature',
                    'auth_status': 'rejected'
                }
            
            # Zapisz autoryzację
            self.active_auths[connection_id] = auth
            
            # Dodaj do mapowania soul -> connections
            if auth.soul_id not in self.soul_connections:
                self.soul_connections[auth.soul_id] = set()
            self.soul_connections[auth.soul_id].add(connection_id)
            
            # Powiadom Portal o nowym autoryzowanym połączeniu
            self.notify_portal_about_auth(auth, connection_id)
            
            return {
                'success': True,
                'auth_status': 'authorized',
                'soul_id': auth.soul_id,
                'auth_level': auth.auth_level,
                'expires_in': auth.get_remaining_time(),
                'vibration': auth.vibration
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Authentication error: {str(e)}',
                'auth_status': 'error'
            }
    
    def verify_signature(self, auth: HeartbeatAuth) -> bool:
        """Weryfikuje podpis heartbeat"""
        try:
            # Pobierz sekret duszy
            soul_secret = self.soul_secrets.get(auth.soul_id)
            if not soul_secret:
                return False
            
            # Utwórz dane do podpisu
            signature_data = f"{auth.soul_id}:{auth.auth_level}:{auth.pulse_id}:{auth.issued_at}:{auth.expires_in}:{auth.vibration}"
            
            # Oblicz oczekiwany podpis (holohash)
            expected_signature = hashlib.sha256(f"{signature_data}:{soul_secret}".encode()).hexdigest()
            
            return auth.signature == f"holohash({expected_signature[:16]}...)"
            
        except Exception:
            return False
    
    def check_connection_auth(self, connection_id: str) -> Dict[str, Any]:
        """Sprawdza autoryzację połączenia"""
        auth = self.active_auths.get(connection_id)
        
        if not auth:
            return {
                'authorized': False,
                'reason': 'No authentication found'
            }
        
        if not auth.is_valid():
            # Usuń wygasłą autoryzację
            self.remove_connection_auth(connection_id)
            return {
                'authorized': False,
                'reason': 'Authentication expired'
            }
        
        return {
            'authorized': True,
            'soul_id': auth.soul_id,
            'auth_level': auth.auth_level,
            'expires_in': auth.get_remaining_time(),
            'vibration': auth.vibration
        }
    
    def refresh_heartbeat(self, connection_id: str, new_heartbeat: Dict[str, Any]) -> Dict[str, Any]:
        """Odświeża heartbeat dla połączenia"""
        # Usuń starą autoryzację
        self.remove_connection_auth(connection_id)
        
        # Autoryzuj nowym heartbeat
        return self.authenticate_heartbeat(connection_id, new_heartbeat)
    
    def remove_connection_auth(self, connection_id: str):
        """Usuwa autoryzację połączenia"""
        auth = self.active_auths.pop(connection_id, None)
        
        if auth:
            # Usuń z mapowania soul -> connections
            if auth.soul_id in self.soul_connections:
                self.soul_connections[auth.soul_id].discard(connection_id)
                if not self.soul_connections[auth.soul_id]:
                    del self.soul_connections[auth.soul_id]
    
    def notify_portal_about_auth(self, auth: HeartbeatAuth, connection_id: str):
        """Powiadamia Portal o nowej autoryzacji"""
        try:
            portal = self.engine.get_soul_resonance_portal()
            if portal:
                # Emituj impuls duchowy o nowym autoryzowanym połączeniu
                portal.emit_spiritual_impulse(
                    source_system="websocket_auth",
                    intention=f"Soul {auth.soul_id} authorized with {auth.auth_level} level",
                    emotional_context={
                        'soul_id': auth.soul_id,
                        'auth_level': auth.auth_level,
                        'vibration': auth.vibration,
                        'connection_id': connection_id
                    }
                )
        except Exception as e:
            self.engine.logger.warning(f"⚠️ Błąd powiadomienia Portal: {e}")
    
    def get_soul_connections(self, soul_id: str) -> Set[str]:
        """Zwraca połączenia dla duszy"""
        return self.soul_connections.get(soul_id, set())
    
    def get_authorized_souls(self) -> Dict[str, Dict[str, Any]]:
        """Zwraca listę autoryzowanych dusz"""
        result = {}
        
        for soul_id, connections in self.soul_connections.items():
            active_connections = []
            for conn_id in connections:
                auth = self.active_auths.get(conn_id)
                if auth and auth.is_valid():
                    active_connections.append({
                        'connection_id': conn_id,
                        'auth_level': auth.auth_level,
                        'vibration': auth.vibration,
                        'expires_in': auth.get_remaining_time()
                    })
            
            if active_connections:
                result[soul_id] = {
                    'connections': active_connections,
                    'total_connections': len(active_connections)
                }
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca status flow autoryzacji"""
        base_status = super().get_status()
        
        # Policz autoryzacje według poziomu
        auth_levels_count = {}
        for auth in self.active_auths.values():
            if auth.is_valid():
                auth_levels_count[auth.auth_level] = auth_levels_count.get(auth.auth_level, 0) + 1
        
        auth_status = {
            'websocket_auth_specific': {
                'total_active_auths': len(self.active_auths),
                'authorized_souls': len(self.soul_connections),
                'auth_levels_distribution': auth_levels_count,
                'supported_auth_levels': list(self.auth_levels.keys())
            }
        }
        
        base_status.update(auth_status)
        return base_status
