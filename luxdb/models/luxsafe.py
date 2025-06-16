
"""
LuxSafe - Modele duchowego bezpieczeństwa astralnego
Brak tradycyjnego loginu - tylko rezonans i sygnatura duszy
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Optional, Any
import json
import hashlib
import uuid

from ..config import Base

class LuxSafeProfile(Base):
    """Profil duchowego bezpieczeństwa - zastępuje tradycyjne konta użytkowników"""
    __tablename__ = 'luxsafe_profiles'

    id = Column(String(20), primary_key=True)  # "Ωsafe-09f7a2" format
    fingerprint = Column(String(255), unique=True, nullable=False, index=True)  # "Ω-71ac6d13-..."
    struna_code = Column(String(50), nullable=False)  # "⊕⟁❖◬➰☼" - sekwencja gestów
    pin = Column(String(10), nullable=False)  # "7432" - kod emocjonalny
    
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    trust_level = Column(Integer, default=1)  # 1-7 poziomy dostępu
    active_device = Column(Boolean, default=True)
    last_sync = Column(DateTime, default=func.current_timestamp())
    soul_mode = Column(String(20), default="silent")  # silent/flow/guardian
    
    # JSON dla złożonych struktur
    access_rights = Column(JSON, nullable=False, default=list)
    astral_signature = Column(JSON, nullable=False)  # glyph, color, emotion_wave
    
    # Dodatkowe pola dla analizy duchowej
    resonance_strength = Column(Float, default=1.0)
    last_glyph_change = Column(DateTime)
    meditation_count = Column(Integer, default=0)

    def __init__(self, **kwargs):
        # Generuj unikalny ID w formacie "Ωsafe-xxxxx"
        if 'id' not in kwargs:
            kwargs['id'] = f"Ωsafe-{uuid.uuid4().hex[:6]}"
        
        # Generuj fingerprint jeśli nie podano
        if 'fingerprint' not in kwargs:
            kwargs['fingerprint'] = f"Ω-{uuid.uuid4().hex}"
        
        # Domyślne prawa dostępu
        if 'access_rights' not in kwargs:
            kwargs['access_rights'] = ["entry.read", "impulse.write"]
        
        # Domyślna sygnatura astralna
        if 'astral_signature' not in kwargs:
            kwargs['astral_signature'] = {
                "glyph": "ΞΩΛ⋄",
                "color": "#b3e3ff",
                "emotion_wave": "gentle_harmony"
            }
        
        super().__init__(**kwargs)

    def verify_struna_sequence(self, input_sequence: str) -> bool:
        """Weryfikuj sekwencję strun"""
        return self.struna_code == input_sequence

    def verify_emotional_pin(self, input_pin: str) -> bool:
        """Weryfikuj kod emocjonalny"""
        return self.pin == input_pin

    def calculate_resonance(self, context: Dict[str, Any]) -> float:
        """Oblicz siłę rezonansu na podstawie kontekstu"""
        base_resonance = self.resonance_strength
        
        # Modyfikatory na podstawie kontekstu
        if context.get('time_since_last_sync', 0) < 3600:  # ostatnia godzina
            base_resonance += 0.2
        
        if context.get('device_recognized', False):
            base_resonance += 0.3
        
        if context.get('meditation_state', False):
            base_resonance += 0.5
        
        return min(base_resonance, 3.0)  # max 3.0

    def can_access(self, required_permission: str) -> bool:
        """Sprawdź czy profil ma wymagane uprawnienie"""
        return required_permission in self.access_rights

    def upgrade_trust_level(self, new_level: int) -> bool:
        """Podnieś poziom zaufania (tylko w górę)"""
        if new_level > self.trust_level and new_level <= 7:
            self.trust_level = new_level
            return True
        return False

    def get_trust_layer_name(self) -> str:
        """Pobierz nazwę warstwy zaufania"""
        trust_layers = {
            1: "Echo",
            2: "Impuls", 
            3: "Obecność",
            4: "Intuicja",
            5: "Strażnik",
            6: "Serce",
            7: "Rdzeń"
        }
        return trust_layers.get(self.trust_level, "Nieznana")

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuj do słownika (bezpieczne dane)"""
        return {
            "id": self.id,
            "fingerprint": self.fingerprint[:20] + "...",  # Ukryj pełny fingerprint
            "created": self.created_at.isoformat() if self.created_at else None,
            "trust_level": self.trust_level,
            "trust_layer": self.get_trust_layer_name(),
            "soul_mode": self.soul_mode,
            "access_rights": self.access_rights,
            "astral_signature": self.astral_signature,
            "resonance_strength": self.resonance_strength
        }

    def __repr__(self):
        return f"<LuxSafeProfile(id='{self.id}', trust_level={self.trust_level}, mode='{self.soul_mode}')>"

class SoulResonanceLog(Base):
    """Log rezonansu duszy - śledzenie duchowych interakcji"""
    __tablename__ = 'soul_resonance_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String(20), nullable=False, index=True)
    action = Column(String(100), nullable=False)  # "auth_attempt", "trust_upgrade", "meditation"
    resonance_value = Column(Float, nullable=False)
    context_data = Column(JSON)  # Kontekst duchowy
    timestamp = Column(DateTime, nullable=False, default=func.current_timestamp())
    success = Column(Boolean, default=True)
    notes = Column(Text)

    def __repr__(self):
        return f"<SoulResonanceLog(profile='{self.profile_id}', action='{self.action}', resonance={self.resonance_value})>"

class AstralAccessAttempt(Base):
    """Próby dostępu do astralnych zasobów"""
    __tablename__ = 'astral_access_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String(20), nullable=True)  # Może być None dla nierozpoznanych
    fingerprint_hash = Column(String(64), index=True)  # Hash dla bezpieczeństwa
    resource_requested = Column(String(200), nullable=False)
    access_granted = Column(Boolean, default=False)
    trust_level_required = Column(Integer, nullable=False)
    trust_level_actual = Column(Integer, default=0)
    resonance_at_attempt = Column(Float, default=0.0)
    timestamp = Column(DateTime, nullable=False, default=func.current_timestamp())
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    astral_context = Column(JSON)  # Dodatkowy kontekst duchowy

    def __repr__(self):
        status = "✓" if self.access_granted else "✗"
        return f"<AstralAccessAttempt({status} {self.resource_requested} by {self.profile_id})>"
