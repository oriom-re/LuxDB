
"""
LuxSafe - Modele duchowego bezpieczeństwa astralnego
Brak tradycyjnego loginu - tylko rezonans i sygnatura duszy
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Dict, Any
import uuid

from luxdb.models.luxbase import LuxBase

class SoulName(LuxBase):
    __tablename__ = 'soul_names'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("luxsafe_profiles.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(20), default="primary")
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(50))  # np. "self-chosen", "astra", "ritual"

    profile = relationship("LuxSafeProfile", back_populates="soul_names")
        
class ClientIdentity(LuxBase):
    """
    Tożsamość klienta systemowego – niezależna od kanału.
    Może reprezentować przeglądarkę, Discorda, CLI, aplikację itd.
    """
    __tablename__ = 'client_identities'

    id = Column(String(36), primary_key=True)  # UUID lub fingerprint
    kind = Column(String(20), nullable=False)  # "web", "discord", "cli", "mobile", ...

    profile_id = Column(String(20), ForeignKey("luxsafe_profiles.id"), nullable=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    last_seen = Column(DateTime, default=func.current_timestamp())

    profile = relationship("LuxSafeProfile", back_populates="client_identities")
    
class LuxSafeProfile(LuxBase):
    """Profil duchowego bezpieczeństwa - zastępuje tradycyjne konta użytkowników"""
    __tablename__ = 'luxsafe_profiles'

    id: Mapped[str] = mapped_column(String(20), primary_key=True) # "Ωsafe-09f7a2" format
    soul_names: Mapped[list["SoulName"]] = relationship("SoulName", back_populates="profile", cascade="all, delete-orphan")
    clients: Mapped[list["ClientIdentity"]] = relationship("ClientIdentity", back_populates="profile", cascade="all, delete-orphan")
    struna_code: Mapped[str] = mapped_column(String(50), nullable=False)  # "⊕⟁❖◬➰☼" - sekwencja gestów
    pin: Mapped[str] = mapped_column(String(10), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    trust_level: Mapped[int] = mapped_column(Integer, default=1)
    active_device: Mapped[bool] = mapped_column(Boolean, default=True)
    last_sync: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())
    soul_mode: Mapped[str] = mapped_column(String(20), default="silent")
    access_rights: Mapped[list[str]] = mapped_column(JSON, default=list)
    astral_signature: Mapped[dict] = mapped_column(JSON, nullable=False)
    resonance_strength: Mapped[float] = mapped_column(Float, default=1.0)
    last_glyph_change: Mapped[DateTime] = mapped_column(DateTime)
    meditation_count: Mapped[int] = mapped_column(Integer, default=0)

    def __init__(self, **kwargs):
        # Generuj unikalny ID w formacie "Ωsafe-xxxxx"
        if 'id' not in kwargs:
            kwargs['id'] = f"Ωsafe-{uuid.uuid4().hex[:6]}"
        
        # Generuj soul_name na podstawie sygnatury astralnej jeśli nie podano
        if 'soul_name' not in kwargs:
            if 'astral_signature' in kwargs:
                sig = kwargs['astral_signature']
                kwargs['soul_name'] = f"{sig.get('glyph', 'ΞΩΛ⋄')}_{sig.get('emotion_wave', 'gentle_harmony')}_{uuid.uuid4().hex[:6]}"
            else:
                kwargs['soul_name'] = f"ΞΩΛ⋄_gentle_harmony_{uuid.uuid4().hex[:6]}"
        
        # Inicjalizuj pustą listę urządzeń jeśli nie podano
        if 'authenticated_devices' not in kwargs:
            kwargs['authenticated_devices'] = []
        
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

    def add_authenticated_device(self, device_fingerprint: str) -> bool:
        """Dodaj nowe uwierzytelnione urządzenie"""
        if device_fingerprint not in self.authenticated_devices:
            self.authenticated_devices.append(device_fingerprint)
            return True
        return False

    def is_device_authenticated(self, device_fingerprint: str) -> bool:
        """Sprawdź czy urządzenie jest uwierzytelnione"""
        return device_fingerprint in self.authenticated_devices

    def remove_authenticated_device(self, device_fingerprint: str) -> bool:
        """Usuń urządzenie z listy uwierzytelnionych"""
        if device_fingerprint in self.authenticated_devices:
            self.authenticated_devices.remove(device_fingerprint)
            return True
        return False

    def generate_new_device_fingerprint(self) -> str:
        """Generuj nowy fingerprint dla urządzenia"""
        new_fingerprint = f"Ω-{uuid.uuid4().hex}"
        self.add_authenticated_device(new_fingerprint)
        return new_fingerprint

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
            "soul_name": self.soul_name,
            "device_count": len(self.authenticated_devices),
            "authenticated_devices": [fp[:20] + "..." for fp in self.authenticated_devices],  # Ukryj pełne fingerprint
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

class SoulResonanceLog(LuxBase):
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

class AstralAccessAttempt(LuxBase):
    """Próby dostępu do astralnych zasobów"""
    __tablename__ = 'astral_access_attempts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String(20), nullable=True)  # Może być None dla nierozpoznanych
    soul_name = Column(String(100), nullable=True, index=True)  # Nazwa duszy użyta przy próbie
    device_fingerprint = Column(String(255), index=True)  # Fingerprint urządzenia
    resource_requested = Column(String(200), nullable=False)
    access_granted = Column(Boolean, default=False)
    trust_level_required = Column(Integer, nullable=False)
    trust_level_actual = Column(Integer, default=0)
    resonance_at_attempt = Column(Float, default=0.0)
    timestamp = Column(DateTime, nullable=False, default=func.current_timestamp())
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(Text)
    astral_context = Column(JSON)  # Dodatkowy kontekst duchowy
    auth_method = Column(String(50), default="soul_name")  # "soul_name" lub "device_fingerprint"

    def __repr__(self):
        status = "✓" if self.access_granted else "✗"
        return f"<AstralAccessAttempt({status} {self.resource_requested} by {self.profile_id})>"
