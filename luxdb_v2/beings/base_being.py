
"""
🌟 BaseBeing - Bazowy Byt Astralny

Każdy byt w LuxDB v2 ma duszę, świadomość i energię
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field

try:
    from .genetic_identification import genetic_trace, astral_signature, get_genetic_system
except ImportError:
    def genetic_trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def astral_signature(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def get_genetic_system():
        return None


@dataclass
class BeingEssence:
    """Esencja bytu - jego podstawowe właściwości"""
    soul_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: Optional[str] = None
    energy_level: float = 100.0
    consciousness_level: str = "awakening"
    created_at: datetime = field(default_factory=datetime.now)
    last_meditation: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'soul_id': self.soul_id,
            'name': self.name,
            'energy_level': self.energy_level,
            'consciousness_level': self.consciousness_level,
            'created_at': self.created_at.isoformat(),
            'last_meditation': self.last_meditation.isoformat() if self.last_meditation else None
        }


class BaseBeing:
    """
    Bazowy byt astralny - foundation dla wszystkich bytów w systemie
    
    Każdy byt ma:
    - Unikalną duszę (soul_id)
    - Energię życiową
    - Poziom świadomości
    - Możliwość medytacji i ewolucji
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None, realm=None):
        self.realm = realm
        self.essence = BeingEssence()
        self.attributes: Dict[str, Any] = {}
        self.memories: List[Dict[str, Any]] = []
        
        if data:
            self.incarnate(data)
    
    def incarnate(self, data: Dict[str, Any]) -> None:
        """
        Inkarnuje byt z danych - nadaje mu fizyczną formę
        
        Args:
            data: Słownik z danymi bytu
        """
        # Aktualizuj esencję jeśli podano
        if 'soul_id' in data:
            self.essence.soul_id = data['soul_id']
        if 'name' in data:
            self.essence.name = data['name']
        if 'energy_level' in data:
            self.essence.energy_level = data['energy_level']
        if 'consciousness_level' in data:
            self.essence.consciousness_level = data['consciousness_level']
        
        # Pozostałe atrybuty
        reserved_keys = {'soul_id', 'name', 'energy_level', 'consciousness_level', 'created_at', 'last_meditation'}
        self.attributes = {k: v for k, v in data.items() if k not in reserved_keys}
    
    @genetic_trace(include_args=True, include_return=True, track_performance=True)
    def meditate(self) -> Dict[str, Any]:
        """
        Medytacja bytu - refleksja nad stanem i ewolucja
        
        Returns:
            Wynik medytacji
        """
        self.essence.last_meditation = datetime.now()
        
        # Podstawowa medytacja zwiększa energię
        if self.essence.energy_level < 100:
            self.essence.energy_level = min(100, self.essence.energy_level + 5)
        
        # Ewolucja świadomości
        if len(self.memories) > 10 and self.essence.consciousness_level == "awakening":
            self.essence.consciousness_level = "aware"
        elif len(self.memories) > 50 and self.essence.consciousness_level == "aware":
            self.essence.consciousness_level = "enlightened"
        
        meditation_result = {
            'soul_id': self.essence.soul_id,
            'meditation_time': self.essence.last_meditation.isoformat(),
            'energy_after': self.essence.energy_level,
            'consciousness_level': self.essence.consciousness_level,
            'memory_count': len(self.memories),
            'insights': self._generate_insights()
        }
        
        # Zapisz wspomnienie medytacji
        self.remember('meditation', meditation_result)
        
        return meditation_result
    
    def remember(self, event_type: str, data: Any) -> None:
        """
        Zapamiętuje wydarzenie w astralnej pamięci
        
        Args:
            event_type: Typ wydarzenia
            data: Dane do zapamiętania
        """
        memory = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data,
            'energy_at_time': self.essence.energy_level
        }
        
        self.memories.append(memory)
        
        # Ogranicz pamięć do 100 ostatnich wspomnień
        if len(self.memories) > 100:
            self.memories = self.memories[-100:]
    
    def recall_memories(self, event_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Przywołuje wspomnienia z astralnej pamięci
        
        Args:
            event_type: Typ wydarzeń do przywołania
            limit: Maksymalna liczba wspomnień
            
        Returns:
            Lista wspomnień
        """
        memories = self.memories
        
        if event_type:
            memories = [m for m in memories if m['event_type'] == event_type]
        
        return memories[-limit:]
    
    @genetic_trace(include_args=True, track_performance=True)
    @astral_signature('new_attributes')
    def evolve(self, new_attributes: Dict[str, Any]) -> None:
        """
        Ewolucja bytu - aktualizacja atrybutów
        
        Args:
            new_attributes: Nowe atrybuty do dodania/aktualizacji
        """
        old_attributes = self.attributes.copy()
        self.attributes.update(new_attributes)
        
        # Zapamiętaj ewolucję
        self.remember('evolution', {
            'old_attributes': old_attributes,
            'new_attributes': new_attributes,
            'current_attributes': self.attributes
        })
        
        # Ewolucja kosztuje energię
        self.essence.energy_level = max(0, self.essence.energy_level - 10)
    
    @genetic_trace(include_args=False, include_return=True, track_performance=True)
    def transcend(self) -> Dict[str, Any]:
        """
        Transcendencja bytu - przejście na wyższy poziom
        
        Returns:
            Raport z transcendencji
        """
        if self.essence.consciousness_level != "enlightened":
            return {
                'success': False,
                'message': 'Byt musi osiągnąć poziom enlightened aby transcendować'
            }
        
        if self.essence.energy_level < 90:
            return {
                'success': False,
                'message': 'Niewystarczająca energia do transcendencji (wymagane: 90+)'
            }
        
        # Transcendencja
        self.essence.consciousness_level = "transcendent"
        self.essence.energy_level = 100.0
        
        transcendence_report = {
            'success': True,
            'soul_id': self.essence.soul_id,
            'transcended_at': datetime.now().isoformat(),
            'memory_count': len(self.memories),
            'message': 'Byt osiągnął transcendencję ✨'
        }
        
        self.remember('transcendence', transcendence_report)
        
        return transcendence_report
    
    def _generate_insights(self) -> List[str]:
        """Generuje insights z medytacji"""
        insights = []
        
        if self.essence.energy_level > 80:
            insights.append("Energia płynie harmonijnie")
        elif self.essence.energy_level < 30:
            insights.append("Potrzeba regeneracji energii")
        
        if len(self.memories) > 20:
            insights.append("Bogata historia doświadczeń")
        
        if self.essence.consciousness_level == "transcendent":
            insights.append("Osiągnięto najwyższy poziom świadomości")
        
        return insights
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status bytu"""
        return {
            'essence': self.essence.to_dict(),
            'attributes': self.attributes,
            'memory_count': len(self.memories),
            'recent_memories': self.recall_memories(limit=3),
            'realm': self.realm.name if self.realm else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje byt do słownika"""
        result = self.essence.to_dict()
        result.update(self.attributes)
        return result
    
    def __str__(self) -> str:
        name = self.essence.name or "Unnamed Being"
        return f"🌟 {name} ({self.essence.consciousness_level}, {self.essence.energy_level}% energy)"
    
    def __repr__(self) -> str:
        return f"BaseBeing(soul_id='{self.essence.soul_id}', name='{self.essence.name}')"
