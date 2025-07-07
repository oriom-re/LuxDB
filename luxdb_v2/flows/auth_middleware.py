
"""
🔐 Auth Middleware - Ochrona dostępu do Astry
"""

from functools import wraps
from flask import request, jsonify
import hashlib
import os
from typing import Set, Optional

class AstralAuth:
    """Autoryzacja astralna"""
    
    def __init__(self):
        self.api_keys: Set[str] = set()
        self.admin_keys: Set[str] = set()
        self._load_keys()
    
    def _load_keys(self):
        """Ładuje klucze z środowiska"""
        # Klucze API
        api_key = os.getenv('ASTRA_API_KEY')
        if api_key:
            self.api_keys.add(self._hash_key(api_key))
        
        # Klucze admin
        admin_key = os.getenv('ASTRA_ADMIN_KEY') 
        if admin_key:
            self.admin_keys.add(self._hash_key(admin_key))
            
        # Domyślny klucz dev (usuń w produkcji!)
        if not self.api_keys:
            self.api_keys.add(self._hash_key('astra_dev_key_2024'))
    
    def _hash_key(self, key: str) -> str:
        """Hashuje klucz"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validuje klucz API"""
        if not provided_key:
            return False
        hashed = self._hash_key(provided_key)
        return hashed in self.api_keys or hashed in self.admin_keys
    
    def validate_admin_key(self, provided_key: str) -> bool:
        """Validuje klucz admin"""
        if not provided_key:
            return False
        hashed = self._hash_key(provided_key)
        return hashed in self.admin_keys

# Globalna instancja
astra_auth = AstralAuth()

def require_api_key(f):
    """Decorator wymagający klucza API"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Sprawdź header Authorization
        auth_header = request.headers.get('Authorization')
        api_key = None
        
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header[7:]  # usuń 'Bearer '
        elif auth_header and auth_header.startswith('ApiKey '):
            api_key = auth_header[7:]  # usuń 'ApiKey '
        else:
            # Sprawdź query param
            api_key = request.args.get('api_key')
        
        if not astra_auth.validate_api_key(api_key):
            return jsonify({
                'success': False,
                'error': 'Nieautoryzowany dostęp do wymiaru astralnego',
                'code': 'UNAUTHORIZED_ASTRAL_ACCESS'
            }), 401
        
        return f(*args, **kwargs)
    return decorated

def require_admin_key(f):
    """Decorator wymagający klucza admin"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        admin_key = None
        
        if auth_header and auth_header.startswith('AdminKey '):
            admin_key = auth_header[9:]  # usuń 'AdminKey '
        else:
            admin_key = request.args.get('admin_key')
        
        if not astra_auth.validate_admin_key(admin_key):
            return jsonify({
                'success': False,
                'error': 'Brak uprawnień administracyjnych do Astry',
                'code': 'UNAUTHORIZED_ADMIN_ACCESS'
            }), 403
        
        return f(*args, **kwargs)
    return decorated
