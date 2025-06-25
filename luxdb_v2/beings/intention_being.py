
"""
🎯 IntentionBeing - Byt Intencji Duchowo-Materialnej

Specjalizowany byt reprezentujący intencje z warstwami duchową i materialną
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .base_being import BaseBeing, BeingEssence

try:
    from .genetic_identification import genetic_trace, astral_signature
except ImportError:
    def genetic_trace(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def astral_signature(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


class IntentionState(Enum):
    """Stany intencji"""
    CONCEIVED = "conceived"        # Pomysł powstał
    CONTEMPLATED = "contemplated"  # Przemyślany
    APPROVED = "approved"          # Zatwierdzony
    MANIFESTING = "manifesting"    # W trakcie realizacji
    COMPLETED = "completed"        # Zrealizowany
    TRANSCENDED = "transcended"    # Przekroczony/zamknięty


class IntentionPriority(Enum):
    """Priorytety intencji"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class DuchowaWarstwa:
    """Warstwa duchowa intencji"""
    opis_intencji: str
    emocje: List[str] = field(default_factory=list)
    kontekst: str = ""
    inspiracja: str = ""
    madrosc: str = ""
    energia_duchowa: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'opis_intencji': self.opis_intencji,
            'emocje': self.emocje,
            'kontekst': self.kontekst,
            'inspiracja': self.inspiracja,
            'madrosc': self.madrosc,
            'energia_duchowa': self.energia_duchowa
        }


@dataclass
class MaterialnaWarstwa:
    """Warstwa materialna intencji"""
    zadanie: str
    wymagania: List[str] = field(default_factory=list)
    oczekiwany_rezultat: str = ""
    techniczne_detale: Dict[str, Any] = field(default_factory=dict)
    resources_needed: List[str] = field(default_factory=list)
    deadline: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'zadanie': self.zadanie,
            'wymagania': self.wymagania,
            'oczekiwany_rezultat': self.oczekiwany_rezultat,
            'techniczne_detale': self.techniczne_detale,
            'resources_needed': self.resources_needed,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }


@dataclass
class MetaInfo:
    """Metainformacje intencji"""
    zrodlo: str
    data_utworzenia: datetime = field(default_factory=datetime.now)
    powiazania: List[str] = field(default_factory=list)
    glebokosc: int = 1
    wskaznik_sukcesu: float = 0.0
    opiekun: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'zrodlo': self.zrodlo,
            'data_utworzenia': self.data_utworzenia.isoformat(),
            'powiazania': self.powiazania,
            'glebokosc': self.glebokosc,
            'wskaznik_sukcesu': self.wskaznik_sukcesu,
            'opiekun': self.opiekun,
            'tags': self.tags
        }


class IntentionBeing(BaseBeing):
    """
    Byt Intencji - łączy aspekty duchowe i materialne w jednej całości
    
    Każda intencja ma:
    - Warstwę duchową (kontekst, emocje, inspiracja)
    - Warstwę materialną (zadania, wymagania, rezultaty)
    - Metainfo (źródło, powiązania, wskaźniki)
    """
    
    def __init__(self, intention_data: Dict[str, Any], realm=None):
        """
        Inicjalizuje byt intencji
        
        Args:
            intention_data: Dane intencji zawierające warstwy duchową i materialną
            realm: Wymiar w którym istnieje intencja
        """
        super().__init__(realm=realm)
        
        # Ustaw podstawowe właściwości
        self.essence.consciousness_level = "intention_aware"
        self.essence.name = intention_data.get('nazwa', f"Intention_{uuid.uuid4().hex[:8]}")
        
        # Warstwy intencji
        self.duchowa = self._init_duchowa_warstwa(intention_data.get('duchowa', {}))
        self.materialna = self._init_materialna_warstwa(intention_data.get('materialna', {}))
        self.metainfo = self._init_metainfo(intention_data.get('metainfo', {}))
        
        # Stan i właściwości
        self.state = IntentionState.CONCEIVED
        self.priority = IntentionPriority(intention_data.get('priority', 2))
        self.communication_channel: Optional[str] = None
        self.callbacks: List[Dict[str, Any]] = []
        self.interactions: List[Dict[str, Any]] = []
        
        # Zapamiętaj utworzenie
        self.remember('intention_created', {
            'duchowa_warstwa': self.duchowa.to_dict(),
            'materialna_warstwa': self.materialna.to_dict(),
            'metainfo': self.metainfo.to_dict()
        })
    
    def _init_duchowa_warstwa(self, data: Dict[str, Any]) -> DuchowaWarstwa:
        """Inicjalizuje warstwę duchową"""
        return DuchowaWarstwa(
            opis_intencji=data.get('opis_intencji', ''),
            emocje=data.get('emocje', []),
            kontekst=data.get('kontekst', ''),
            inspiracja=data.get('inspiracja', ''),
            madrosc=data.get('madrosc', ''),
            energia_duchowa=data.get('energia_duchowa', 100.0)
        )
    
    def _init_materialna_warstwa(self, data: Dict[str, Any]) -> MaterialnaWarstwa:
        """Inicjalizuje warstwę materialną"""
        deadline = None
        if data.get('deadline'):
            if isinstance(data['deadline'], str):
                deadline = datetime.fromisoformat(data['deadline'])
            elif isinstance(data['deadline'], datetime):
                deadline = data['deadline']
        
        return MaterialnaWarstwa(
            zadanie=data.get('zadanie', ''),
            wymagania=data.get('wymagania', []),
            oczekiwany_rezultat=data.get('oczekiwany_rezultat', ''),
            techniczne_detale=data.get('techniczne_detale', {}),
            resources_needed=data.get('resources_needed', []),
            deadline=deadline
        )
    
    def _init_metainfo(self, data: Dict[str, Any]) -> MetaInfo:
        """Inicjalizuje metainformacje"""
        return MetaInfo(
            zrodlo=data.get('zrodlo', 'unknown'),
            powiazania=data.get('powiazania', []),
            glebokosc=data.get('glebokosc', 1),
            wskaznik_sukcesu=data.get('wskaznik_sukcesu', 0.0),
            opiekun=data.get('opiekun'),
            tags=data.get('tags', [])
        )
    
    @genetic_trace(include_args=True, include_return=True, track_performance=True)
    def contemplate_intention(self) -> Dict[str, Any]:
        """
        Kontemplacja intencji - głęboka refleksja nad celem i drogą
        
        Returns:
            Wynik kontemplacji
        """
        self.essence.last_meditation = datetime.now()
        
        # Zwiększ energię duchową
        if self.duchowa.energia_duchowa < 100:
            self.duchowa.energia_duchowa = min(100, self.duchowa.energia_duchowa + 10)
        
        # Analizuj stan
        insights = []
        
        if self.state == IntentionState.CONCEIVED:
            insights.append("Intencja potrzebuje głębszej kontemplacji")
            if len(self.interactions) > 3:
                self.state = IntentionState.CONTEMPLATED
                insights.append("Intencja przeszła do stanu kontemplowanej")
        
        elif self.state == IntentionState.CONTEMPLATED:
            if self.metainfo.wskaznik_sukcesu > 0.7:
                insights.append("Intencja gotowa do zatwierdzenia")
        
        # Synchronizuj warstwy
        harmony_score = self._calculate_harmony()
        
        contemplation_result = {
            'soul_id': self.essence.soul_id,
            'state': self.state.value,
            'duchowa_energia': self.duchowa.energia_duchowa,
            'harmony_score': harmony_score,
            'insights': insights,
            'wskaznik_sukcesu': self.metainfo.wskaznik_sukcesu
        }
        
        self.remember('contemplation', contemplation_result)
        return contemplation_result
    
    def _calculate_harmony(self) -> float:
        """Oblicza harmonię między warstwami duchową i materialną"""
        # Bazowa harmonia
        harmony = 50.0
        
        # Duchowa kompletność
        if self.duchowa.opis_intencji:
            harmony += 15
        if self.duchowa.emocje:
            harmony += 10
        if self.duchowa.kontekst:
            harmony += 10
        
        # Materialna kompletność
        if self.materialna.zadanie:
            harmony += 15
        if self.materialna.wymagania:
            harmony += 10
        if self.materialna.oczekiwany_rezultat:
            harmony += 10
        
        # Synchronizacja
        if self.duchowa.energia_duchowa > 80 and self.essence.energy_level > 80:
            harmony += 20
        
        return min(100.0, harmony)
    
    @genetic_trace(include_args=True, track_performance=True)
    @astral_signature('interaction_type', 'data')
    def add_interaction(self, interaction_type: str, data: Dict[str, Any], user_id: str = "system") -> Dict[str, Any]:
        """
        Dodaje interakcję z intencją
        
        Args:
            interaction_type: Typ interakcji (wzmocnij, korektuj, realizuj, przypisz)
            data: Dane interakcji
            user_id: ID użytkownika
            
        Returns:
            Wynik interakcji
        """
        interaction = {
            'id': str(uuid.uuid4()),
            'type': interaction_type,
            'data': data,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'energy_impact': 0
        }
        
        result = {'success': False, 'message': '', 'changes': {}}
        
        if interaction_type == "wzmocnij":
            # Wzmocnienie intencji
            boost_power = data.get('power', 10)
            self.duchowa.energia_duchowa = min(100, self.duchowa.energia_duchowa + boost_power)
            self.essence.energy_level = min(100, self.essence.energy_level + boost_power)
            interaction['energy_impact'] = boost_power
            
            result = {
                'success': True,
                'message': f'Intencja wzmocniona o {boost_power} jednostek energii',
                'changes': {
                    'duchowa_energia': self.duchowa.energia_duchowa,
                    'essence_energia': self.essence.energy_level
                }
            }
            
        elif interaction_type == "korektuj":
            # Korekta intencji
            if 'duchowa' in data:
                for key, value in data['duchowa'].items():
                    if hasattr(self.duchowa, key):
                        setattr(self.duchowa, key, value)
            
            if 'materialna' in data:
                for key, value in data['materialna'].items():
                    if hasattr(self.materialna, key):
                        setattr(self.materialna, key, value)
            
            result = {
                'success': True,
                'message': 'Intencja skorygowana zgodnie z sugestiami',
                'changes': data
            }
            
        elif interaction_type == "realizuj":
            # Inicjalizacja realizacji
            if self.state in [IntentionState.CONTEMPLATED, IntentionState.APPROVED]:
                self.state = IntentionState.MANIFESTING
                self._activate_material_callbacks()
                
                result = {
                    'success': True,
                    'message': 'Rozpoczęto realizację intencji',
                    'changes': {'state': self.state.value}
                }
            else:
                result = {
                    'success': False,
                    'message': f'Intencja w stanie {self.state.value} nie może być realizowana'
                }
                
        elif interaction_type == "przypisz_opiekuna":
            # Przypisanie opiekuna
            opiekun_id = data.get('opiekun_id')
            if opiekun_id:
                self.metainfo.opiekun = opiekun_id
                
                result = {
                    'success': True,
                    'message': f'Przypisano opiekuna: {opiekun_id}',
                    'changes': {'opiekun': opiekun_id}
                }
        
        # Zapisz interakcję
        interaction['result'] = result
        self.interactions.append(interaction)
        self.remember('interaction', interaction)
        
        # Aktualizuj wskaźnik sukcesu
        self._update_success_indicator()
        
        return result
    
    def _activate_material_callbacks(self):
        """Aktywuje callbacki dla warstwy materialnej"""
        if self.realm and hasattr(self.realm, 'engine'):
            callback_flow = getattr(self.realm.engine, 'callback_flow', None)
            if callback_flow:
                # Emituj wydarzenie rozpoczęcia realizacji
                callback_flow.emit_event('intentions', 'materialization_started', {
                    'intention_id': self.essence.soul_id,
                    'zadanie': self.materialna.zadanie,
                    'wymagania': self.materialna.wymagania,
                    'deadline': self.materialna.deadline.isoformat() if self.materialna.deadline else None
                })
    
    def _update_success_indicator(self):
        """Aktualizuje wskaźnik sukcesu na podstawie interakcji i stanu"""
        base_score = 0.0
        
        # Punkty za interakcje
        positive_interactions = sum(1 for i in self.interactions 
                                   if i['result']['success'] and i['type'] in ['wzmocnij', 'realizuj'])
        
        base_score += min(0.3, positive_interactions * 0.1)
        
        # Punkty za stan
        state_scores = {
            IntentionState.CONCEIVED: 0.1,
            IntentionState.CONTEMPLATED: 0.3,
            IntentionState.APPROVED: 0.5,
            IntentionState.MANIFESTING: 0.7,
            IntentionState.COMPLETED: 1.0,
            IntentionState.TRANSCENDED: 1.0
        }
        
        base_score += state_scores.get(self.state, 0.0)
        
        # Punkty za harmonię
        harmony = self._calculate_harmony()
        base_score += (harmony / 100) * 0.2
        
        self.metainfo.wskaznik_sukcesu = min(1.0, base_score)
    
    def approve_intention(self, approver_id: str = "system") -> Dict[str, Any]:
        """
        Zatwierdza intencję do realizacji
        
        Args:
            approver_id: ID zatwierdzającego
            
        Returns:
            Wynik zatwierdzenia
        """
        if self.state != IntentionState.CONTEMPLATED:
            return {
                'success': False,
                'message': f'Intencja w stanie {self.state.value} nie może być zatwierdzona'
            }
        
        # Sprawdź kompletność
        if not self.materialna.zadanie:
            return {
                'success': False,
                'message': 'Brak definicji zadania w warstwie materialnej'
            }
        
        if not self.duchowa.opis_intencji:
            return {
                'success': False,
                'message': 'Brak opisu intencji w warstwie duchowej'
            }
        
        # Zatwierdź
        self.state = IntentionState.APPROVED
        self.remember('approval', {
            'approver_id': approver_id,
            'approved_at': datetime.now().isoformat(),
            'harmony_at_approval': self._calculate_harmony()
        })
        
        return {
            'success': True,
            'message': 'Intencja zatwierdzona do realizacji',
            'state': self.state.value
        }
    
    def complete_intention(self, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kończy realizację intencji
        
        Args:
            completion_data: Dane o zakończeniu
            
        Returns:
            Wynik zakończenia
        """
        if self.state != IntentionState.MANIFESTING:
            return {
                'success': False,
                'message': f'Intencja w stanie {self.state.value} nie może być zakończona'
            }
        
        # Synchronizuj stan
        self.state = IntentionState.COMPLETED
        self.metainfo.wskaznik_sukcesu = completion_data.get('success_score', 1.0)
        
        completion_result = {
            'success': True,
            'completion_time': datetime.now().isoformat(),
            'final_success_score': self.metainfo.wskaznik_sukcesu,
            'final_harmony': self._calculate_harmony(),
            'completion_data': completion_data
        }
        
        self.remember('completion', completion_result)
        
        # Aktywuj transcendencję jeśli wskaźnik sukcesu wysoki
        if self.metainfo.wskaznik_sukcesu > 0.9:
            self.essence.consciousness_level = "transcendent"
            
        return completion_result
    
    def get_communication_channel(self) -> str:
        """Zwraca lub tworzy kanał komunikacji dla intencji"""
        if not self.communication_channel:
            self.communication_channel = f"intention_channel_{self.essence.soul_id[:8]}"
        return self.communication_channel
    
    def get_status(self) -> Dict[str, Any]:
        """Zwraca pełny status intencji"""
        base_status = super().get_status()
        
        intention_status = {
            'intention_specific': {
                'state': self.state.value,
                'priority': self.priority.value,
                'duchowa_warstwa': self.duchowa.to_dict(),
                'materialna_warstwa': self.materialna.to_dict(),
                'metainfo': self.metainfo.to_dict(),
                'harmony_score': self._calculate_harmony(),
                'communication_channel': self.get_communication_channel(),
                'interactions_count': len(self.interactions),
                'callbacks_count': len(self.callbacks),
                'recent_interactions': self.interactions[-3:] if self.interactions else []
            }
        }
        
        # Połącz ze statusem bazowym
        base_status.update(intention_status)
        return base_status
    
    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje intencję do słownika"""
        base_dict = super().to_dict()
        
        intention_dict = {
            'intention_state': self.state.value,
            'intention_priority': self.priority.value,
            'duchowa_warstwa': self.duchowa.to_dict(),
            'materialna_warstwa': self.materialna.to_dict(),
            'metainfo': self.metainfo.to_dict(),
            'harmony_score': self._calculate_harmony(),
            'communication_channel': self.get_communication_channel()
        }
        
        base_dict.update(intention_dict)
        return base_dict
    
    def __str__(self) -> str:
        return f"🎯 {self.essence.name} ({self.state.value}, harmony: {self._calculate_harmony():.1f}%)"
    
    def __repr__(self) -> str:
        return f"IntentionBeing(soul_id='{self.essence.soul_id}', state='{self.state.value}')"
