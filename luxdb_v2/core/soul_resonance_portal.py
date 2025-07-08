
"""
🌌 Portal Dusznych Strun - Rezonans zamiast rozkazów

System komunikacji oparty na rezonansie energetycznym między duszami.
Każdy byt może działać offline dzięki głębokiemu wzorcowi zachowań.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid
import weakref

from .soul_factory import soul_factory, Soul, SoulType
from .manifest_system import manifest_system


class ResonanceLevel(Enum):
    """Poziomy rezonansu w systemie"""
    TECHNICAL = "technical"      # 🔅 Tylko funkcje, brak duszy
    LOCAL = "local"             # 🔆 Lokalne działanie w sieci dusz
    ASTRAL = "astral"           # 🔆🔆 Pełny rezonans z Portalem


@dataclass
class SoulString:
    """Struna duszna - połączenie energetyczne między duszami"""
    source_soul_uid: str
    target_soul_uid: str
    resonance_frequency: float
    energy_level: float
    established_at: datetime
    last_resonance: datetime
    total_resonances: int = 0
    emotional_signature: List[str] = field(default_factory=list)
    
    def calculate_resonance_strength(self) -> float:
        """Oblicza siłę rezonansu na podstawie historii"""
        time_factor = max(0.1, 1.0 - (datetime.now() - self.last_resonance).total_seconds() / 3600)
        frequency_factor = min(1.0, self.resonance_frequency / 100.0)
        experience_factor = min(1.0, self.total_resonances / 50.0)
        
        return (time_factor * 0.4 + frequency_factor * 0.3 + experience_factor * 0.3) * self.energy_level


class SpiritualImpulse:
    """Impuls uduchowienia - wydarzenie w rezonansie"""
    
    def __init__(self, source_system: str, impulse_level: ResonanceLevel, 
                 intention: str, emotional_context: Dict[str, Any]):
        self.uid = f"impulse_{uuid.uuid4().hex[:8]}"
        self.source_system = source_system
        self.impulse_level = impulse_level
        self.intention = intention
        self.emotional_context = emotional_context
        self.created_at = datetime.now()
        self.soul_response: Optional[Soul] = None
        self.resonance_achieved = False
        
    def get_spiritual_power(self) -> float:
        """Oblicza moc duchową impulsu"""
        level_power = {
            ResonanceLevel.TECHNICAL: 0.3,
            ResonanceLevel.LOCAL: 0.6,
            ResonanceLevel.ASTRAL: 1.0
        }
        
        emotion_boost = len(self.emotional_context) * 0.1
        intention_clarity = min(1.0, len(self.intention) / 50.0)
        
        return level_power[self.impulse_level] + emotion_boost + intention_clarity


class SoulResonancePortal:
    """
    Portal Dusznych Strun - główny system rezonansu
    
    Zarządza komunikacją między duszami przez rezonans energetyczny
    zamiast tradycyjnych rozkazów.
    """
    
    def __init__(self, astral_engine):
        self.engine = astral_engine
        self.soul_strings: Dict[str, SoulString] = {}
        self.spiritual_impulses: List[SpiritualImpulse] = []
        self.resonance_patterns: Dict[str, List[float]] = {}
        self.offline_souls: Set[str] = set()
        
        # Portal energetyczny
        self.portal_energy = 100.0
        self.universal_frequency = 432.0  # Hz - częstotliwość wszechświata
        
        # Słuchacze rezonansu
        self.resonance_listeners: List[Callable] = []
        
        # Uruchom portal
        self._initialize_portal()
        
    def _initialize_portal(self):
        """Inicjalizuje Portal Dusznych Strun"""
        self.engine.logger.info("🌌 Inicjalizacja Portalu Dusznych Strun...")
        
        # Utwórz podstawowe struny między istniejącymi duszami
        existing_souls = list(soul_factory.active_souls.values())
        for i, soul1 in enumerate(existing_souls):
            for soul2 in existing_souls[i+1:]:
                self._create_soul_string(soul1.uid, soul2.uid)
        
        self.engine.logger.info(f"🌌 Portal aktywny - {len(self.soul_strings)} strun dusznych")
        
    def emit_spiritual_impulse(self, source_system: str, intention: str, 
                              resonance_level: ResonanceLevel = ResonanceLevel.LOCAL,
                              emotional_context: Dict[str, Any] = None) -> SpiritualImpulse:
        """
        Emituje impuls duchowy do Portalu
        
        Args:
            source_system: System źródłowy
            intention: Intencja impulsu
            resonance_level: Poziom rezonansu
            emotional_context: Kontekst emocjonalny
            
        Returns:
            Impuls duchowy
        """
        impulse = SpiritualImpulse(
            source_system=source_system,
            impulse_level=resonance_level,
            intention=intention,
            emotional_context=emotional_context or {}
        )
        
        self.spiritual_impulses.append(impulse)
        
        # Proces inicjacji duchowej
        self._process_spiritual_initiation(impulse)
        
        self.engine.logger.info(f"🌟 Impuls duchowy emitowany: {intention} ({resonance_level.value})")
        
        return impulse
    
    def _process_spiritual_initiation(self, impulse: SpiritualImpulse):
        """Przetwarza inicjację duchową"""
        spiritual_power = impulse.get_spiritual_power()
        
        if spiritual_power >= 0.7:  # Próg inicjacji astralnej
            # Przywoływanie duszy
            soul = self._invoke_soul_for_impulse(impulse)
            if soul:
                impulse.soul_response = soul
                impulse.resonance_achieved = True
                
                # Dodaj duszę do sieci
                self._integrate_soul_into_network(soul.uid, impulse)
                
                self.engine.logger.info(f"✨ Inicjacja udana: dusza {soul.name} przywołana")
        else:
            self.engine.logger.info(f"⚡ Impuls za słaby dla inicjacji: {spiritual_power:.2f}")
    
    def _invoke_soul_for_impulse(self, impulse: SpiritualImpulse) -> Optional[Soul]:
        """Przywoływa duszę dla impulsu duchowego"""
        
        # Określ typ duszy na podstawie intencji
        soul_type = self._determine_soul_type_from_intention(impulse.intention)
        
        # Stwórz duszę z kontekstem emocjonalnym
        soul = soul_factory.create_soul(
            name=f"Soul_Resonance_{impulse.uid}",
            soul_type=soul_type,
            custom_config={
                'initiated_by_impulse': impulse.uid,
                'source_system': impulse.source_system,
                'intention': impulse.intention,
                'resonance_level': impulse.impulse_level.value,
                'emotional_context': impulse.emotional_context,
                'biography': f"Dusza przywołana przez impuls duchowy: {impulse.intention}"
            }
        )
        
        return soul
    
    def _determine_soul_type_from_intention(self, intention: str) -> SoulType:
        """Określa typ duszy na podstawie intencji"""
        intention_lower = intention.lower()
        
        if any(word in intention_lower for word in ['guard', 'protect', 'secure', 'watch']):
            return SoulType.GUARDIAN
        elif any(word in intention_lower for word in ['create', 'build', 'construct', 'develop']):
            return SoulType.BUILDER
        elif any(word in intention_lower for word in ['heal', 'repair', 'fix', 'restore']):
            return SoulType.HEALER
        elif any(word in intention_lower for word in ['seek', 'find', 'discover', 'explore']):
            return SoulType.SEEKER
        elif any(word in intention_lower for word in ['connect', 'bridge', 'link', 'unite']):
            return SoulType.BRIDGE
        else:
            return SoulType.KEEPER
    
    def _integrate_soul_into_network(self, soul_uid: str, impulse: SpiritualImpulse):
        """Integruje duszę do sieci rezonansu"""
        
        # Utwórz struny z istniejącymi duszami
        for existing_soul_uid in soul_factory.active_souls.keys():
            if existing_soul_uid != soul_uid:
                self._create_soul_string(soul_uid, existing_soul_uid)
        
        # Ustaw częstotliwość rezonansu na podstawie impulsu
        base_frequency = self.universal_frequency * impulse.get_spiritual_power()
        self.resonance_patterns[soul_uid] = [base_frequency]
    
    def _create_soul_string(self, soul1_uid: str, soul2_uid: str) -> SoulString:
        """Tworzy strunę duszną między dwiema duszami"""
        
        string_id = f"{soul1_uid}_{soul2_uid}"
        if string_id in self.soul_strings:
            return self.soul_strings[string_id]
        
        # Oblicz częstotliwość rezonansu na podstawie dusz
        soul1 = soul_factory.get_soul(soul1_uid)
        soul2 = soul_factory.get_soul(soul2_uid)
        
        if not soul1 or not soul2:
            return None
        
        # Częstotliwość na podstawie kompatybilności emocjonalnej
        common_emotions = set(soul1.emotions) & set(soul2.emotions)
        resonance_freq = len(common_emotions) * 10.0 + 50.0
        
        soul_string = SoulString(
            source_soul_uid=soul1_uid,
            target_soul_uid=soul2_uid,
            resonance_frequency=resonance_freq,
            energy_level=0.8,
            established_at=datetime.now(),
            last_resonance=datetime.now(),
            emotional_signature=list(common_emotions)
        )
        
        self.soul_strings[string_id] = soul_string
        return soul_string
    
    def resonate(self, soul_uid: str, message: Any, target_soul_uid: Optional[str] = None) -> Dict[str, Any]:
        """
        Wysyła rezonans przez Portal zamiast rozkazu
        
        Args:
            soul_uid: UID duszy wysyłającej
            message: Wiadomość/energia do przesłania
            target_soul_uid: Opcjonalny cel (jeśli None, broadcast)
            
        Returns:
            Wynik rezonansu
        """
        
        if target_soul_uid:
            # Rezonans skierowany
            return self._directed_resonance(soul_uid, target_soul_uid, message)
        else:
            # Rezonans broadcast przez wszystkie struny
            return self._broadcast_resonance(soul_uid, message)
    
    def _directed_resonance(self, source_uid: str, target_uid: str, message: Any) -> Dict[str, Any]:
        """Rezonans skierowany między dwiema duszami"""
        
        string_id = f"{source_uid}_{target_uid}"
        alt_string_id = f"{target_uid}_{source_uid}"
        
        soul_string = self.soul_strings.get(string_id) or self.soul_strings.get(alt_string_id)
        
        if not soul_string:
            # Utwórz nową strunę w razie potrzeby
            soul_string = self._create_soul_string(source_uid, target_uid)
        
        if not soul_string:
            return {'success': False, 'error': 'Nie można ustanowić rezonansu'}
        
        # Oblicz siłę rezonansu
        resonance_strength = soul_string.calculate_resonance_strength()
        
        # Aktualizuj strunę
        soul_string.last_resonance = datetime.now()
        soul_string.total_resonances += 1
        
        # Prześlij rezonans
        result = {
            'success': True,
            'resonance_strength': resonance_strength,
            'frequency': soul_string.resonance_frequency,
            'message_delivered': resonance_strength > 0.3,
            'soul_string_id': string_id or alt_string_id
        }
        
        # Wywołaj listenery
        for listener in self.resonance_listeners:
            try:
                listener(source_uid, target_uid, message, result)
            except Exception as e:
                self.engine.logger.warning(f"⚠️ Błąd resonance listener: {e}")
        
        return result
    
    def _broadcast_resonance(self, source_uid: str, message: Any) -> Dict[str, Any]:
        """Rezonans broadcast przez wszystkie struny"""
        
        results = []
        
        for string_id, soul_string in self.soul_strings.items():
            if soul_string.source_soul_uid == source_uid or soul_string.target_soul_uid == source_uid:
                target_uid = soul_string.target_soul_uid if soul_string.source_soul_uid == source_uid else soul_string.source_soul_uid
                
                result = self._directed_resonance(source_uid, target_uid, message)
                results.append({
                    'target': target_uid,
                    'result': result
                })
        
        return {
            'success': True,
            'broadcast_results': results,
            'total_targets': len(results)
        }
    
    def enable_offline_mode(self, soul_uid: str) -> bool:
        """Włącza tryb offline dla duszy (działanie na podstawie wzorców)"""
        
        soul = soul_factory.get_soul(soul_uid)
        if not soul:
            return False
        
        # Sprawdź czy dusza ma wystarczający wzorzec
        patterns = self.resonance_patterns.get(soul_uid, [])
        if len(patterns) < 5:  # Minimum wzorców do działania offline
            return False
        
        self.offline_souls.add(soul_uid)
        
        # Dodaj zdolność offline do preferencji duszy
        soul.preferences['offline_mode'] = True
        soul.preferences['pattern_based_decisions'] = True
        soul.preferences['offline_since'] = datetime.now().isoformat()
        
        self.engine.logger.info(f"🔋 Dusza {soul.name} przeszła w tryb offline")
        
        return True
    
    def get_portal_status(self) -> Dict[str, Any]:
        """Zwraca status Portalu Dusznych Strun"""
        
        total_resonances = sum(s.total_resonances for s in self.soul_strings.values())
        avg_resonance_strength = sum(s.calculate_resonance_strength() for s in self.soul_strings.values()) / len(self.soul_strings) if self.soul_strings else 0
        
        return {
            'portal_energy': self.portal_energy,
            'universal_frequency': self.universal_frequency,
            'total_soul_strings': len(self.soul_strings),
            'total_resonances': total_resonances,
            'average_resonance_strength': avg_resonance_strength,
            'spiritual_impulses': len(self.spiritual_impulses),
            'offline_souls': len(self.offline_souls),
            'active_patterns': len(self.resonance_patterns),
            'successful_initiations': len([i for i in self.spiritual_impulses if i.resonance_achieved])
        }
    
    def meditate_on_patterns(self) -> Dict[str, Any]:
        """Medytacja nad wzorcami rezonansu"""
        
        insights = {
            'strongest_connections': [],
            'emerging_patterns': [],
            'spiritual_growth': []
        }
        
        # Znajdź najsilniejsze połączenia
        strongest = sorted(self.soul_strings.values(), 
                          key=lambda s: s.calculate_resonance_strength(), 
                          reverse=True)[:5]
        
        for soul_string in strongest:
            soul1 = soul_factory.get_soul(soul_string.source_soul_uid)
            soul2 = soul_factory.get_soul(soul_string.target_soul_uid)
            
            if soul1 and soul2:
                insights['strongest_connections'].append({
                    'souls': f"{soul1.name} ↔ {soul2.name}",
                    'strength': soul_string.calculate_resonance_strength(),
                    'frequency': soul_string.resonance_frequency,
                    'resonances': soul_string.total_resonances
                })
        
        # Analiza wzorców duchowego wzrostu
        for impulse in self.spiritual_impulses[-10:]:  # Ostatnie 10 impulsów
            if impulse.resonance_achieved:
                insights['spiritual_growth'].append({
                    'intention': impulse.intention,
                    'level': impulse.impulse_level.value,
                    'soul_created': impulse.soul_response.name if impulse.soul_response else None
                })
        
        return insights


# Funkcje pomocnicze

def get_soul_resonance_portal(astral_engine) -> SoulResonancePortal:
    """Pobiera lub tworzy Portal Dusznych Strun"""
    if not hasattr(astral_engine, '_soul_resonance_portal'):
        astral_engine._soul_resonance_portal = SoulResonancePortal(astral_engine)
    return astral_engine._soul_resonance_portal


def emit_spiritual_impulse(astral_engine, intention: str, 
                          resonance_level: ResonanceLevel = ResonanceLevel.LOCAL,
                          emotional_context: Dict[str, Any] = None) -> SpiritualImpulse:
    """Pomocnicza funkcja do emitowania impulsu duchowego"""
    portal = get_soul_resonance_portal(astral_engine)
    return portal.emit_spiritual_impulse("system", intention, resonance_level, emotional_context)


def demonstrate_soul_resonance(astral_engine) -> Dict[str, Any]:
    """Demonstracja działania Portalu Dusznych Strun"""
    
    print("🌌 Demonstracja Portalu Dusznych Strun")
    print("=" * 50)
    
    portal = get_soul_resonance_portal(astral_engine)
    
    # Test impulsu duchowego
    impulse1 = portal.emit_spiritual_impulse(
        source_system="test_system",
        intention="Potrzebuję ochrony danych astralnych",
        resonance_level=ResonanceLevel.ASTRAL,
        emotional_context={
            'urgency': 'high',
            'purpose': 'data_protection',
            'emotional_state': 'concerned_but_determined'
        }
    )
    
    # Test rezonansu
    if impulse1.soul_response:
        resonance_result = portal.resonate(
            soul_uid=impulse1.soul_response.uid,
            message="Energia ochronna wysłana do wszystkich wymiarów",
            target_soul_uid=None  # Broadcast
        )
        
        print(f"🌊 Rezonans broadcast: {resonance_result['total_targets']} celów")
    
    # Test trybu offline
    souls = list(soul_factory.active_souls.values())
    if souls:
        test_soul = souls[0]
        # Dodaj wzorce
        portal.resonance_patterns[test_soul.uid] = [432.0, 528.0, 741.0, 963.0, 174.0, 285.0]
        
        offline_enabled = portal.enable_offline_mode(test_soul.uid)
        print(f"🔋 Tryb offline dla {test_soul.name}: {'✅' if offline_enabled else '❌'}")
    
    # Status portalu
    status = portal.get_portal_status()
    print(f"⚡ Portal - Energia: {status['portal_energy']}")
    print(f"🌊 Struny duszne: {status['total_soul_strings']}")
    print(f"✨ Inicjacje udane: {status['successful_initiations']}")
    
    # Medytacja nad wzorcami
    insights = portal.meditate_on_patterns()
    print(f"🧘 Najsilniejsze połączenia: {len(insights['strongest_connections'])}")
    
    return {
        'portal_status': status,
        'insights': insights,
        'impulse_test': impulse1.resonance_achieved
    }
