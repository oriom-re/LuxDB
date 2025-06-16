
"""
LuxSafe Manager - Duchowe bezpieczeństwo bez tradycyjnego logowania
Implementuje system rezonansu i sygnatury duszy
"""

import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from .models.luxsafe import LuxSafeProfile, SoulResonanceLog, AstralAccessAttempt

logger = logging.getLogger(__name__)

class LuxSafeManager:
    """Menedżer duchowego bezpieczeństwa"""
    
    def __init__(self, session: Session):
        self.session = session
        
        # Definicje uprawnień dla poziomów zaufania
        self.trust_permissions = {
            1: ["entry.read"],  # Echo
            2: ["entry.read", "impulse.write"],  # Impuls  
            3: ["entry.read", "impulse.write", "resonance.listen", "soulmap.view"],  # Obecność
            4: ["entry.read", "impulse.write", "resonance.listen", "soulmap.view", "manifest.edit"],  # Intuicja
            5: ["entry.read", "impulse.write", "resonance.listen", "soulmap.view", "manifest.edit", "space.config"],  # Strażnik
            6: ["entry.read", "impulse.write", "resonance.listen", "soulmap.view", "manifest.edit", "space.config", "being.create"],  # Serce
            7: ["*"]  # Rdzeń - pełny dostęp
        }

    def create_soul_profile(self, struna_sequence: str, emotional_pin: str, 
                           astral_signature: Optional[Dict] = None,
                           initial_trust_level: int = 1) -> LuxSafeProfile:
        """Stwórz nowy profil duszy"""
        
        # Generuj unikalny fingerprint
        fingerprint_data = f"{struna_sequence}{emotional_pin}{time.time()}"
        fingerprint = f"Ω-{hashlib.sha256(fingerprint_data.encode()).hexdigest()}"
        
        # Domyślna sygnatura astralna
        if not astral_signature:
            astral_signature = {
                "glyph": "ΞΩΛ⋄",
                "color": "#b3e3ff", 
                "emotion_wave": "gentle_harmony"
            }
        
        # Przypisz uprawnienia na podstawie poziomu zaufania
        access_rights = self.trust_permissions.get(initial_trust_level, ["entry.read"])
        
        profile = LuxSafeProfile(
            fingerprint=fingerprint,
            struna_code=struna_sequence,
            pin=emotional_pin,
            trust_level=initial_trust_level,
            access_rights=access_rights,
            astral_signature=astral_signature
        )
        
        self.session.add(profile)
        self.session.commit()
        
        # Zaloguj stworzenie profilu
        self._log_soul_resonance(profile.id, "profile_created", 1.0, {
            "initial_trust_level": initial_trust_level,
            "astral_signature": astral_signature
        })
        
        logger.info(f"Stworzono nowy profil duszy: {profile.id} (poziom: {initial_trust_level})")
        return profile

    def authenticate_by_resonance(self, fingerprint: str, struna_sequence: str, 
                                 emotional_pin: str, context: Optional[Dict] = None) -> Tuple[bool, Optional[LuxSafeProfile], float]:
        """Uwierzytelnianie przez rezonans duszy"""
        
        if not context:
            context = {}
        
        # Znajdź profil po fingerprint
        profile = self.session.query(LuxSafeProfile).filter_by(fingerprint=fingerprint).first()
        
        if not profile:
            self._log_access_attempt(None, fingerprint, "auth_by_resonance", False, 0, 0, 0.0)
            return False, None, 0.0
        
        # Weryfikacja sekwencji strun i kodu emocjonalnego
        struna_valid = profile.verify_struna_sequence(struna_sequence)
        pin_valid = profile.verify_emotional_pin(emotional_pin)
        
        if not (struna_valid and pin_valid):
            resonance = 0.0
            self._log_soul_resonance(profile.id, "auth_failed", resonance, {
                "struna_valid": struna_valid,
                "pin_valid": pin_valid
            })
            return False, profile, resonance
        
        # Oblicz siłę rezonansu
        resonance = profile.calculate_resonance(context)
        
        # Aktualizuj ostatnią synchronizację
        profile.last_sync = datetime.utcnow()
        self.session.commit()
        
        # Zaloguj udane uwierzytelnienie
        self._log_soul_resonance(profile.id, "auth_success", resonance, context)
        
        logger.info(f"Uwierzytelnienie duszy: {profile.id} (rezonans: {resonance:.2f})")
        return True, profile, resonance

    def check_access_permission(self, profile: LuxSafeProfile, required_permission: str,
                              resource_name: str = "") -> bool:
        """Sprawdź uprawnienia dostępu"""
        
        # Pełny dostęp dla poziomu 7 (Rdzeń)
        if profile.trust_level >= 7 or "*" in profile.access_rights:
            self._log_access_attempt(profile.id, profile.fingerprint, resource_name, True, 
                                   profile.trust_level, profile.trust_level, profile.resonance_strength)
            return True
        
        # Sprawdź konkretne uprawnienie
        has_access = profile.can_access(required_permission)
        
        self._log_access_attempt(profile.id, profile.fingerprint, resource_name, has_access,
                               self._get_required_trust_level(required_permission), 
                               profile.trust_level, profile.resonance_strength)
        
        return has_access

    def elevate_trust_level(self, profile: LuxSafeProfile, target_level: int,
                           struna_sequence: str, emotional_pin: str) -> bool:
        """Podnieś poziom zaufania (wymaga pełnej weryfikacji)"""
        
        # Weryfikacja pełnej sekwencji
        if not (profile.verify_struna_sequence(struna_sequence) and 
                profile.verify_emotional_pin(emotional_pin)):
            self._log_soul_resonance(profile.id, "trust_elevation_failed", 0.0, {
                "target_level": target_level,
                "reason": "invalid_credentials"
            })
            return False
        
        # Sprawdź czy można podnieść poziom
        if target_level <= profile.trust_level or target_level > 7:
            return False
        
        old_level = profile.trust_level
        profile.trust_level = target_level
        
        # Aktualizuj uprawnienia
        profile.access_rights = self.trust_permissions.get(target_level, ["entry.read"])
        
        self.session.commit()
        
        # Zaloguj podniesienie poziomu
        self._log_soul_resonance(profile.id, "trust_elevated", 2.0, {
            "old_level": old_level,
            "new_level": target_level,
            "new_permissions": profile.access_rights
        })
        
        logger.info(f"Podniesiono poziom zaufania: {profile.id} ({old_level} → {target_level})")
        return True

    def meditative_sync(self, profile: LuxSafeProfile) -> float:
        """Synchronizacja medytacyjna - wzmacnia rezonans"""
        
        profile.meditation_count += 1
        profile.resonance_strength = min(profile.resonance_strength + 0.1, 3.0)
        profile.last_sync = datetime.utcnow()
        
        self.session.commit()
        
        self._log_soul_resonance(profile.id, "meditative_sync", profile.resonance_strength, {
            "meditation_count": profile.meditation_count
        })
        
        return profile.resonance_strength

    def get_soul_statistics(self, profile: LuxSafeProfile) -> Dict[str, Any]:
        """Pobierz statystyki duchowe profilu"""
        
        # Ostatnie logi rezonansu
        recent_logs = (self.session.query(SoulResonanceLog)
                      .filter_by(profile_id=profile.id)
                      .order_by(SoulResonanceLog.timestamp.desc())
                      .limit(10)
                      .all())
        
        # Próby dostępu
        access_attempts = (self.session.query(AstralAccessAttempt)
                          .filter_by(profile_id=profile.id)
                          .count())
        
        return {
            "profile_info": profile.to_dict(),
            "meditation_count": profile.meditation_count,
            "last_sync": profile.last_sync.isoformat() if profile.last_sync else None,
            "recent_resonance": [
                {
                    "action": log.action,
                    "resonance": log.resonance_value,
                    "timestamp": log.timestamp.isoformat(),
                    "success": log.success
                }
                for log in recent_logs
            ],
            "total_access_attempts": access_attempts
        }

    def _log_soul_resonance(self, profile_id: str, action: str, resonance: float, 
                           context: Dict[str, Any], success: bool = True, notes: str = ""):
        """Zaloguj rezonans duszy"""
        
        log_entry = SoulResonanceLog(
            profile_id=profile_id,
            action=action,
            resonance_value=resonance,
            context_data=context,
            success=success,
            notes=notes
        )
        
        self.session.add(log_entry)
        self.session.commit()

    def _log_access_attempt(self, profile_id: Optional[str], fingerprint: str, 
                           resource: str, granted: bool, required_level: int,
                           actual_level: int, resonance: float):
        """Zaloguj próbę dostępu"""
        
        # Hash fingerprint dla bezpieczeństwa
        fingerprint_hash = hashlib.sha256(fingerprint.encode()).hexdigest()
        
        attempt = AstralAccessAttempt(
            profile_id=profile_id,
            fingerprint_hash=fingerprint_hash,
            resource_requested=resource,
            access_granted=granted,
            trust_level_required=required_level,
            trust_level_actual=actual_level,
            resonance_at_attempt=resonance
        )
        
        self.session.add(attempt)
        self.session.commit()

    def _get_required_trust_level(self, permission: str) -> int:
        """Pobierz wymagany poziom zaufania dla uprawnienia"""
        
        permission_levels = {
            "entry.read": 1,
            "impulse.write": 2,
            "resonance.listen": 3,
            "soulmap.view": 3,
            "manifest.edit": 4,
            "space.config": 5,
            "being.create": 6,
            "*": 7
        }
        
        return permission_levels.get(permission, 7)
