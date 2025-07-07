
"""
🛡️ Security Config - Konfiguracja bezpieczeństwa Astry
"""

import os
from typing import Dict, Any, List

class AstralSecurityConfig:
    """Konfiguracja bezpieczeństwa systemu astralnego"""
    
    def __init__(self):
        self.security_mode = os.getenv('ASTRA_SECURITY_MODE', 'development')  # development, production, locked
        self.allowed_ips: List[str] = self._get_allowed_ips()
        self.require_auth = self.security_mode in ['production', 'locked']
        self.enable_rate_limiting = self.security_mode != 'development'
        self.max_requests_per_minute = int(os.getenv('ASTRA_RATE_LIMIT', '60'))
        
    def _get_allowed_ips(self) -> List[str]:
        """Pobiera listę dozwolonych IP"""
        allowed = os.getenv('ASTRA_ALLOWED_IPS', '')
        if allowed:
            return [ip.strip() for ip in allowed.split(',')]
        
        # Domyślne IP dla różnych trybów
        if self.security_mode == 'development':
            return ['127.0.0.1', '::1']  # tylko localhost
        elif self.security_mode == 'production':
            return []  # wymagaj explicit konfiguracji
        else:  # locked
            return ['127.0.0.1']  # tylko localhost
    
    def is_ip_allowed(self, ip: str) -> bool:
        """Sprawdza czy IP jest dozwolone"""
        if self.security_mode == 'development':
            return True  # w dev wszystko dozwolone
        
        if not self.allowed_ips:
            return True  # jeśli nie ma konfiguracji, pozwól
            
        return ip in self.allowed_ips
    
    def get_security_headers(self) -> Dict[str, str]:
        """Zwraca nagłówki bezpieczeństwa"""
        headers = {}
        
        if self.security_mode in ['production', 'locked']:
            headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'",
                'X-Astra-Security-Mode': self.security_mode
            })
        
        return headers

# Globalna konfiguracja
astral_security = AstralSecurityConfig()

def get_security_config():
    """Pobiera globalną konfigurację bezpieczeństwa"""
    return astral_security
