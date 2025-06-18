
"""
Menedżer sesji użytkowników dla LuxDB
Zarządza sesjami, autoryzacją i stanem użytkowników
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from contextlib import contextmanager

from .manager import get_db_manager
from .models import User, UserSession
from .utils.error_handlers import LuxDBError, handle_database_errors
from .utils.logging_utils import get_db_logger

logger = get_db_logger()

class SessionError(LuxDBError):
    """Błąd sesji użytkownika"""
    pass

class AuthenticationError(SessionError):
    """Błąd uwierzytelniania"""
    pass

class SessionManager:
    """
    Menedżer sesji użytkowników z funkcjami:
    - Uwierzytelnianie użytkowników
    - Zarządzanie sesjami (create, validate, destroy)
    - Automatyczne wygasanie sesji
    - Śledzenie aktywności użytkowników
    """
    
    def __init__(self, db_name: str = "main", session_timeout_hours: int = 24):
        self.db_manager = get_db_manager()
        self.db_name = db_name
        self.session_timeout = timedelta(hours=session_timeout_hours)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Upewnij się, że baza istnieje
        if db_name not in self.db_manager.list_databases():
            self.db_manager.create_database(db_name)
    
    @handle_database_errors("hash_password")
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hashuje hasło z solą"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        pwd_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
        return pwd_hash.hex(), salt
    
    @handle_database_errors("verify_password")
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Weryfikuje hasło"""
        calculated_hash, _ = self._hash_password(password, salt)
        return secrets.compare_digest(calculated_hash, password_hash)
    
    @handle_database_errors("generate_session_token")
    def _generate_session_token(self) -> str:
        """Generuje bezpieczny token sesji"""
        return secrets.token_urlsafe(32)
    
    @handle_database_errors("create_user")
    def create_user(self, username: str, email: str, password: str, 
                   extra_data: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Tworzy nowego użytkownika
        
        Args:
            username: Nazwa użytkownika
            email: Email użytkownika
            password: Hasło w postaci jawnej
            extra_data: Dodatkowe dane użytkownika
            
        Returns:
            ID utworzonego użytkownika lub None w przypadku błędu
        """
        password_hash, salt = self._hash_password(password)
        
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": datetime.now()
        }
        
        if extra_data:
            user_data.update(extra_data)
        
        with self.db_manager.get_session(self.db_name) as session:
            # Sprawdź czy użytkownik już istnieje
            existing = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing:
                logger.log_info(f"User {username} already exists, skipping creation")
                return existing.id
            
            user = self.db_manager.insert_data(session, self.db_name, User, user_data)
            if user:
                return user.id
            return None
    
    @handle_database_errors("authenticate_user")
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Uwierzytelnia użytkownika
        
        Args:
            username: Nazwa użytkownika lub email
            password: Hasło
            
        Returns:
            Dane użytkownika jeśli uwierzytelnienie powiodło się
        """
        with self.db_manager.get_session(self.db_name) as session:
            user = session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                raise AuthenticationError("Nieprawidłowa nazwa użytkownika lub hasło")
            
            if not user.is_active:
                raise AuthenticationError("Konto użytkownika jest nieaktywne")
            
            if not self._verify_password(password, user.password_hash, user.salt):
                raise AuthenticationError("Nieprawidłowa nazwa użytkownika lub hasło")
            
            # Aktualizuj ostatnie logowanie
            user.last_login_at = datetime.now()
            session.commit()
            
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login_at": user.last_login_at
            }
    
    @handle_database_errors("create_session")
    def create_session(self, user_id: int, ip_address: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> str:
        """
        Tworzy nową sesję dla użytkownika
        
        Args:
            user_id: ID użytkownika
            ip_address: Adres IP użytkownika
            user_agent: User Agent przeglądarki
            
        Returns:
            Token sesji
        """
        session_token = self._generate_session_token()
        expires_at = datetime.now() + self.session_timeout
        
        session_data = {
            "user_id": user_id,
            "session_token": session_token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.now(),
            "expires_at": expires_at,
            "is_active": True
        }
        
        with self.db_manager.get_session(self.db_name) as session:
            user_session = self.db_manager.insert_data(session, self.db_name, UserSession, session_data)
            
            if user_session:
                # Dodaj do cache aktywnych sesji
                self.active_sessions[session_token] = {
                    "user_id": user_id,
                    "created_at": datetime.now(),
                    "expires_at": expires_at,
                    "last_activity": datetime.now()
                }
                
                return session_token
            
            raise SessionError("Nie udało się utworzyć sesji")
    
    @handle_database_errors("validate_session")
    def validate_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Waliduje sesję użytkownika
        
        Args:
            session_token: Token sesji
            
        Returns:
            Dane sesji jeśli jest ważna
        """
        # Sprawdź cache
        if session_token in self.active_sessions:
            cached_session = self.active_sessions[session_token]
            if datetime.now() < cached_session["expires_at"]:
                # Aktualizuj ostatnią aktywność
                cached_session["last_activity"] = datetime.now()
                return cached_session
            else:
                # Sesja wygasła - usuń z cache
                del self.active_sessions[session_token]
        
        # Sprawdź w bazie danych
        with self.db_manager.get_session(self.db_name) as session:
            user_session = session.query(UserSession).filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not user_session:
                return None
            
            # Sprawdź czy sesja nie wygasła
            if datetime.now() > user_session.expires_at:
                user_session.is_active = False
                session.commit()
                return None
            
            # Aktualizuj ostatnią aktywność
            user_session.last_activity_at = datetime.now()
            session.commit()
            
            session_data = {
                "user_id": user_session.user_id,
                "created_at": user_session.created_at,
                "expires_at": user_session.expires_at,
                "last_activity": user_session.last_activity_at
            }
            
            # Dodaj do cache
            self.active_sessions[session_token] = session_data
            
            return session_data
    
    @handle_database_errors("destroy_session")
    def destroy_session(self, session_token: str) -> bool:
        """
        Niszczy sesję użytkownika (wylogowanie)
        
        Args:
            session_token: Token sesji
            
        Returns:
            True jeśli sesja została zniszczona
        """
        # Usuń z cache
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
        
        # Dezaktywuj w bazie danych
        with self.db_manager.get_session(self.db_name) as session:
            user_session = session.query(UserSession).filter_by(
                session_token=session_token
            ).first()
            
            if user_session:
                user_session.is_active = False
                user_session.destroyed_at = datetime.now()
                session.commit()
                return True
            
            return False
    
    @handle_database_errors("get_user_sessions")
    def get_user_sessions(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Pobiera sesje użytkownika
        
        Args:
            user_id: ID użytkownika
            active_only: Czy tylko aktywne sesje
            
        Returns:
            Lista sesji użytkownika
        """
        with self.db_manager.get_session(self.db_name) as session:
            query = session.query(UserSession).filter_by(user_id=user_id)
            
            if active_only:
                query = query.filter_by(is_active=True)
            
            sessions = query.all()
            
            return [
                {
                    "session_token": s.session_token,
                    "ip_address": s.ip_address,
                    "user_agent": s.user_agent,
                    "created_at": s.created_at,
                    "expires_at": s.expires_at,
                    "last_activity_at": s.last_activity_at,
                    "is_active": s.is_active
                }
                for s in sessions
            ]
    
    @handle_database_errors("cleanup_expired_sessions")
    def cleanup_expired_sessions(self) -> int:
        """
        Czyści wygasłe sesje
        
        Returns:
            Liczba usuniętych sesji
        """
        now = datetime.now()
        
        # Czyść cache
        expired_tokens = [
            token for token, data in self.active_sessions.items()
            if now > data["expires_at"]
        ]
        
        for token in expired_tokens:
            del self.active_sessions[token]
        
        # Czyść bazę danych
        with self.db_manager.get_session(self.db_name) as session:
            expired_sessions = session.query(UserSession).filter(
                (UserSession.expires_at < now) | 
                (UserSession.is_active == False)
            ).all()
            
            count = len(expired_sessions)
            
            for user_session in expired_sessions:
                session.delete(user_session)
            
            session.commit()
            
            return count
    
    @contextmanager
    def user_context(self, session_token: str):
        """
        Context manager dla operacji w kontekście użytkownika
        
        Args:
            session_token: Token sesji
            
        Yields:
            Dane użytkownika jeśli sesja jest ważna
            
        Raises:
            AuthenticationError: Jeśli sesja jest nieważna
        """
        session_data = self.validate_session(session_token)
        
        if not session_data:
            raise AuthenticationError("Nieważna lub wygasła sesja")
        
        with self.db_manager.get_session(self.db_name) as db_session:
            user = db_session.query(User).filter_by(id=session_data["user_id"]).first()
            
            if not user or not user.is_active:
                raise AuthenticationError("Użytkownik nieaktywny")
            
            yield {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "session_data": session_data
            }

# Singleton instance
_session_manager = None

def get_session_manager(db_name: str = "main") -> SessionManager:
    """Zwraca singleton instance menedżera sesji"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager(db_name)
    return _session_manager
