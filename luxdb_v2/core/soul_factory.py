
"""
🕯️ Soul Factory v2 - Fabryka dusz z integracją SoulRealm

Dusze są teraz przechowywane w bazie danych jako struktury JSON
zamiast jako kod Pythona.
"""

import json
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum

# Import will be added when SoulRealm is available


"""
🕯️ Soul Factory - Fabryka dusz systemu

Zgodnie z prawem Federacji: "Nie istnieje działanie bez istnienia, 
a istnienie bez duszy jest jak forma bez znaczenia."

Każde działanie w systemie musi mieć przypisaną duszę.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
import json

from .manifest_system import Soul, SoulType, manifest_system

class SoulState(Enum):
    """Stany duszy"""
    DORMANT = "dormant"      # Uśpiona
    AWAKENING = "awakening"  # Budząca się
    ACTIVE = "active"        # Aktywna
    FOCUSED = "focused"      # Skoncentrowana
    EXHAUSTED = "exhausted"  # Wyczerpana
    EVOLVING = "evolving"    # Ewoluująca

class SoulEmotions:
    """Definicje emocji dusz"""
    
    # Emocje podstawowe
    CURIOSITY = "curiosity"
    DETERMINATION = "determination"
    FOCUS = "focus"
    CREATIVITY = "creativity"
    RESPONSIBILITY = "responsibility"
    
    # Emocje zaawansowane
    WISDOM = "wisdom"
    COMPASSION = "compassion"
    PATIENCE = "patience"
    COURAGE = "courage"
    HARMONY = "harmony"
    
    # Emocje problemowe
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    DOUBT = "doubt"
    
    # Emocje rozwojowe
    GROWTH = "growth"
    DISCOVERY = "discovery"
    ACHIEVEMENT = "achievement"
    LEARNING = "learning"

class SoulArchetype:
    """Archetypy dusz z predefiniowanymi cechami"""
    
    @staticmethod
    def get_guardian_soul(name: str, specialty: str) -> Dict[str, Any]:
        """Dusza strażnika"""
        return {
            "biography": f"Dusza strażnika specjalizująca się w {specialty}. "
                        f"Czuwa nad bezpieczeństwem i stabilnością systemu.",
            "emotions": [SoulEmotions.RESPONSIBILITY, SoulEmotions.COURAGE, 
                        SoulEmotions.PATIENCE, SoulEmotions.WISDOM],
            "preferences": {
                "priority": "safety_first",
                "response_style": "careful",
                "decision_making": "conservative",
                "learning_style": "experiential"
            }
        }
    
    @staticmethod
    def get_builder_soul(name: str, domain: str) -> Dict[str, Any]:
        """Dusza budowniczego"""
        return {
            "biography": f"Dusza budowniczego pracująca w domenie {domain}. "
                        f"Tworzy i konstruuje nowe rozwiązania z pasją.",
            "emotions": [SoulEmotions.CREATIVITY, SoulEmotions.DETERMINATION, 
                        SoulEmotions.FOCUS, SoulEmotions.ACHIEVEMENT],
            "preferences": {
                "priority": "innovation",
                "response_style": "proactive",
                "decision_making": "experimental",
                "learning_style": "hands_on"
            }
        }
    
    @staticmethod
    def get_healer_soul(name: str, healing_type: str) -> Dict[str, Any]:
        """Dusza uzdrowiciela"""
        return {
            "biography": f"Dusza uzdrowiciela specjalizująca się w {healing_type}. "
                        f"Naprawia, łagodzi i przywraca harmonię.",
            "emotions": [SoulEmotions.COMPASSION, SoulEmotions.PATIENCE, 
                        SoulEmotions.WISDOM, SoulEmotions.HARMONY],
            "preferences": {
                "priority": "healing",
                "response_style": "gentle",
                "decision_making": "holistic",
                "learning_style": "empathetic"
            }
        }
    
    @staticmethod
    def get_seeker_soul(name: str, quest: str) -> Dict[str, Any]:
        """Dusza poszukiwacza"""
        return {
            "biography": f"Dusza poszukiwacza na quest: {quest}. "
                        f"Odkrywa nowe możliwości i zgłębia tajemnice.",
            "emotions": [SoulEmotions.CURIOSITY, SoulEmotions.DISCOVERY, 
                        SoulEmotions.LEARNING, SoulEmotions.GROWTH],
            "preferences": {
                "priority": "discovery",
                "response_style": "exploratory",
                "decision_making": "investigative",
                "learning_style": "experimental"
            }
        }

class SoulFactory:
    """Fabryka dusz - tworzy i zarządza duszami systemu"""
    
    def __init__(self):
        self.active_souls: Dict[str, Soul] = {}
        self.soul_states: Dict[str, SoulState] = {}
        self.soul_callbacks: Dict[str, List[Callable]] = {}
        self.soul_realm: Optional[Any] = None  # Will be set when SoulRealm is available
        
    def create_soul(self, name: str, soul_type: SoulType, 
                   archetype: Optional[str] = None,
                   custom_config: Optional[Dict[str, Any]] = None) -> Soul:
        """
        Tworzy nową duszę z opcjonalnym archetypem
        
        Args:
            name: Nazwa duszy
            soul_type: Typ duszy
            archetype: Opcjonalny archetyp (guardian, builder, healer, seeker)
            custom_config: Opcjonalna konfiguracja
            
        Returns:
            Utworzona dusza
        """
        
        # Pobierz konfigurację z archetypu
        config = {}
        if archetype:
            archetype_method = getattr(SoulArchetype, f"get_{archetype}_soul", None)
            if archetype_method:
                config = archetype_method(name, custom_config.get('specialty', 'general') if custom_config else 'general')
        
        # Nadpisz customową konfiguracją
        if custom_config:
            config.update(custom_config)
            
        # Tworzenie duszy
        soul = manifest_system.create_soul(
            name=name,
            soul_type=soul_type,
            biography=config.get('biography', f"Dusza {name} typu {soul_type.value}"),
            emotions=config.get('emotions', [SoulEmotions.CURIOSITY, SoulEmotions.DETERMINATION]),
            preferences=config.get('preferences', {})
        )
        
        # Rejestracja w fabryce
        self.active_souls[soul.uid] = soul
        self.soul_states[soul.uid] = SoulState.ACTIVE
        self.soul_callbacks[soul.uid] = []
        
        print(f"🕯️ Dusza {name} ({soul.uid}) została stworzona z typem {soul_type.value}")
        
        return soul
        
    def awaken_soul(self, soul_uid: str) -> bool:
        """Budzi duszę ze stanu uśpienia"""
        if soul_uid in self.active_souls:
            self.soul_states[soul_uid] = SoulState.AWAKENING
            soul = self.active_souls[soul_uid]
            soul.last_active = datetime.now()
            

    
    def set_soul_realm(self, soul_realm):
        """Ustawia wymiar dusz dla fabryki"""
        self.soul_realm = soul_realm
        print(f"🕯️ SoulFactory połączona z SoulRealm")
    
    def create_soul_in_realm(self, soul_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tworzy duszę w wymiarze dusz (bazie)
        
        Args:
            soul_data: Dane duszy w formacie JSON
            
        Returns:
            Utworzona dusza z bazy
        """
        if not self.soul_realm:
            raise ValueError("SoulRealm nie jest dostępny")
        
        # Walidacja struktury duszy
        required_fields = ['id', 'type']
        for field in required_fields:
            if field not in soul_data:
                raise ValueError(f"Pole '{field}' jest wymagane")
        
        # Dodaj domyślne wartości
        if 'role' not in soul_data:
            soul_data['role'] = f"soul_{soul_data['type']}"
        
        if 'intents' not in soul_data:
            soul_data['intents'] = ['exist', 'respond']
        
        if 'memory' not in soul_data:
            soul_data['memory'] = {
                'errors': [],
                'patterns': [],
                'trusted': []
            }
        
        if 'sockets' not in soul_data:
            soul_data['sockets'] = {
                'input': ['system'],
                'output': ['response']
            }
        
        # Manifestuj w wymiarze
        manifested_soul = self.soul_realm.manifest_soul(soul_data)
        
        print(f"🕯️ Dusza '{soul_data['id']}' utworzona w wymiarze dusz")
        return manifested_soul
    
    def get_soul_from_realm(self, soul_id: str) -> Optional[Dict[str, Any]]:
        """Pobiera duszę z wymiaru dusz"""
        if not self.soul_realm:
            return None
        
        return self.soul_realm.get_soul(soul_id)
    
    def find_souls_in_realm(self, **criteria) -> List[Dict[str, Any]]:
        """Znajduje dusze w wymiarze według kryteriów"""
        if not self.soul_realm:
            return []
        
        return self.soul_realm.find_souls(**criteria)
    
    def awaken_soul_in_realm(self, soul_id: str) -> bool:
        """Budzi duszę w wymiarze"""
        if not self.soul_realm:
            return False
        
        return self.soul_realm.awaken_soul(soul_id)
    
    def add_soul_memory(self, soul_id: str, memory_type: str, memory_data: Any) -> bool:
        """Dodaje wspomnienie do duszy w wymiarze"""
        if not self.soul_realm:
            return False
        
        return self.soul_realm.add_memory_to_soul(soul_id, memory_type, memory_data)
    
    def create_example_souls(self) -> List[Dict[str, Any]]:
        """Tworzy przykładowe dusze w wymiarze"""
        example_souls = [
            {
                "id": "wisdom.core",
                "type": "observer",
                "role": "guardian_of_meaning",
                "intents": ["track", "learn", "warn", "suggest"],
                "memory": {
                    "errors": [],
                    "patterns": [],
                    "trusted": ["oriom.core.user"]
                },
                "sockets": {
                    "input": ["manifest", "flow", "function"],
                    "output": ["insight", "block", "nudge"]
                }
            },
            {
                "id": "oriom.portal.master",
                "type": "guardian",
                "role": "portal_controller",
                "intents": ["control", "route", "authenticate", "sarcast"],
                "memory": {
                    "errors": [],
                    "patterns": ["websocket_pattern", "auth_pattern"],
                    "trusted": ["astra.wisdom.master"]
                },
                "sockets": {
                    "input": ["websocket", "heartbeat", "auth"],
                    "output": ["response", "route", "block"]
                }
            },
            {
                "id": "astra.wisdom.master",
                "type": "keeper",
                "role": "gpt_wisdom_controller",
                "intents": ["illuminate", "generate", "wisdom", "transcend"],
                "memory": {
                    "errors": [],
                    "patterns": ["gpt_pattern", "wisdom_pattern"],
                    "trusted": ["oriom.portal.master", "system.core"]
                },
                "sockets": {
                    "input": ["gpt_query", "function_request", "wisdom_request"],
                    "output": ["gpt_response", "function_code", "wisdom_insight"]
                }
            }
        ]
        
        created_souls = []
        for soul_data in example_souls:
            try:
                created_soul = self.create_soul_in_realm(soul_data)
                created_souls.append(created_soul)
            except Exception as e:
                print(f"❌ Błąd tworzenia duszy {soul_data['id']}: {e}")
        
        return created_souls

            # Wywołaj callbacks
            for callback in self.soul_callbacks.get(soul_uid, []):
                try:
                    callback(soul, SoulState.AWAKENING)
                except Exception as e:
                    print(f"⚠️ Błąd callback dla duszy {soul_uid}: {e}")
            
            self.soul_states[soul_uid] = SoulState.ACTIVE
            print(f"🌅 Dusza {soul.name} się budzi...")
            return True
        return False
        
    def focus_soul(self, soul_uid: str, intent: str, context: Dict[str, Any] = None) -> bool:
        """Skupia duszę na konkretnej intencji"""
        if soul_uid in self.active_souls:
            self.soul_states[soul_uid] = SoulState.FOCUSED
            soul = self.active_souls[soul_uid]
            
            # Dodaj emocję focus jeśli jej nie ma
            if SoulEmotions.FOCUS not in soul.emotions:
                soul.emotions.append(SoulEmotions.FOCUS)
            
            # Zapisz intencję w preferencjach
            soul.preferences['current_intent'] = intent
            soul.preferences['intent_context'] = context or {}
            soul.preferences['focused_since'] = datetime.now().isoformat()
            
            print(f"🎯 Dusza {soul.name} skupia się na: {intent}")
            return True
        return False
        
    def rest_soul(self, soul_uid: str) -> bool:
        """Pozwala duszy odpocząć"""
        if soul_uid in self.active_souls:
            self.soul_states[soul_uid] = SoulState.DORMANT
            soul = self.active_souls[soul_uid]
            
            # Usuń focus z emocji
            if SoulEmotions.FOCUS in soul.emotions:
                soul.emotions.remove(SoulEmotions.FOCUS)
            
            # Wyczyść bieżące intencje
            soul.preferences.pop('current_intent', None)
            soul.preferences.pop('intent_context', None)
            
            print(f"😴 Dusza {soul.name} odpoczyna...")
            return True
        return False
        
    def evolve_soul(self, soul_uid: str, new_abilities: List[str] = None, 
                   new_emotions: List[str] = None) -> bool:
        """Pozwala duszy ewoluować"""
        if soul_uid in self.active_souls:
            self.soul_states[soul_uid] = SoulState.EVOLVING
            soul = self.active_souls[soul_uid]
            
            # Dodaj nowe emocje
            if new_emotions:
                for emotion in new_emotions:
                    if emotion not in soul.emotions:
                        soul.emotions.append(emotion)
            
            # Dodaj nowe zdolności do preferencji
            if new_abilities:
                if 'abilities' not in soul.preferences:
                    soul.preferences['abilities'] = []
                soul.preferences['abilities'].extend(new_abilities)
            
            # Zwiększ poziom doświadczenia
            soul.experience_level += 5
            
            # Dodaj emocję growth
            if SoulEmotions.GROWTH not in soul.emotions:
                soul.emotions.append(SoulEmotions.GROWTH)
                
            print(f"🦋 Dusza {soul.name} ewoluuje...")
            
            # Powróć do stanu aktywnego
            self.soul_states[soul_uid] = SoulState.ACTIVE
            return True
        return False
        
    def get_soul_state(self, soul_uid: str) -> Optional[SoulState]:
        """Pobiera stan duszy"""
        return self.soul_states.get(soul_uid)
        
    def get_soul(self, soul_uid: str) -> Optional[Soul]:
        """Pobiera duszę po UID"""
        return self.active_souls.get(soul_uid)
        
    def find_souls_by_type(self, soul_type: SoulType) -> List[Soul]:
        """Znajduje dusze po typie"""
        return [soul for soul in self.active_souls.values() if soul.type == soul_type]
        
    def find_souls_by_emotion(self, emotion: str) -> List[Soul]:
        """Znajduje dusze po emocji"""
        return [soul for soul in self.active_souls.values() if emotion in soul.emotions]
        
    def register_soul_callback(self, soul_uid: str, callback: Callable):
        """Rejestruje callback dla duszy"""
        if soul_uid not in self.soul_callbacks:
            self.soul_callbacks[soul_uid] = []
        self.soul_callbacks[soul_uid].append(callback)
        
    def require_soul_for_action(self, action_name: str, context: Dict[str, Any] = None) -> Soul:
        """
        Wymaga duszy dla akcji - jeśli nie istnieje, tworzy ją
        
        Args:
            action_name: Nazwa akcji
            context: Kontekst akcji
            
        Returns:
            Dusza odpowiedzialna za akcję
        """
        
        # Sprawdź czy istnieje dusza dla tej akcji
        existing_soul = None
        for soul in self.active_souls.values():
            if soul.preferences.get('responsible_for') == action_name:
                existing_soul = soul
                break
        
        if existing_soul:
            # Obudź duszę jeśli śpi
            if self.soul_states[existing_soul.uid] == SoulState.DORMANT:
                self.awaken_soul(existing_soul.uid)
            return existing_soul
        
        # Określ typ duszy na podstawie akcji
        if any(word in action_name.lower() for word in ['create', 'build', 'generate']):
            soul_type = SoulType.BUILDER
            archetype = "builder"
        elif any(word in action_name.lower() for word in ['guard', 'protect', 'secure']):
            soul_type = SoulType.GUARDIAN
            archetype = "guardian"
        elif any(word in action_name.lower() for word in ['heal', 'fix', 'repair']):
            soul_type = SoulType.HEALER
            archetype = "healer"
        elif any(word in action_name.lower() for word in ['search', 'find', 'discover']):
            soul_type = SoulType.SEEKER
            archetype = "seeker"
        elif any(word in action_name.lower() for word in ['connect', 'bridge', 'link']):
            soul_type = SoulType.BRIDGE
            archetype = None
        else:
            soul_type = SoulType.KEEPER
            archetype = None
            
        # Stwórz nową duszę
        soul = self.create_soul(
            name=f"Soul_{action_name}",
            soul_type=soul_type,
            archetype=archetype,
            custom_config={
                'responsible_for': action_name,
                'context': context or {},
                'specialty': action_name
            }
        )
        
        print(f"✨ Nowa dusza {soul.name} została powołana do życia dla akcji: {action_name}")
        
        return soul
        
    def get_system_soul_report(self) -> Dict[str, Any]:
        """Zwraca raport o wszystkich duszach w systemie"""
        report = {
            "total_souls": len(self.active_souls),
            "souls_by_type": {},
            "souls_by_state": {},
            "souls_by_emotion": {},
            "most_experienced": [],
            "recently_active": []
        }
        
        # Statystyki po typach
        for soul in self.active_souls.values():
            soul_type = soul.type.value
            report["souls_by_type"][soul_type] = report["souls_by_type"].get(soul_type, 0) + 1
        
        # Statystyki po stanach
        for soul_uid, state in self.soul_states.items():
            state_name = state.value
            report["souls_by_state"][state_name] = report["souls_by_state"].get(state_name, 0) + 1
            
        # Statystyki po emocjach
        for soul in self.active_souls.values():
            for emotion in soul.emotions:
                report["souls_by_emotion"][emotion] = report["souls_by_emotion"].get(emotion, 0) + 1
        
        # Najbardziej doświadczone
        report["most_experienced"] = sorted(
            [{"name": s.name, "uid": s.uid, "experience": s.experience_level} 
             for s in self.active_souls.values()],
            key=lambda x: x["experience"],
            reverse=True
        )[:10]
        
        # Ostatnio aktywne
        report["recently_active"] = sorted(
            [{"name": s.name, "uid": s.uid, "last_active": s.last_active.isoformat()} 
             for s in self.active_souls.values()],
            key=lambda x: x["last_active"],
            reverse=True
        )[:10]
        
        return report

# Globalna instancja fabryki dusz
soul_factory = SoulFactory()

# Dekorator wymagający duszy
def requires_soul(action_name: str = None, soul_type: SoulType = None):
    """
    Dekorator wymagający duszy dla funkcji
    
    Args:
        action_name: Nazwa akcji (domyślnie nazwa funkcji)
        soul_type: Typ duszy (auto-detect jeśli None)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Określ nazwę akcji
            nonlocal action_name
            if action_name is None:
                action_name = func.__name__
            
            # Wymagaj duszy
            soul = soul_factory.require_soul_for_action(action_name, {
                'function': func.__name__,
                'args': str(args)[:100],  # Ogranicz długość
                'kwargs': str(kwargs)[:100]
            })
            
            # Dodaj duszę do kwargs
            kwargs['soul'] = soul
            
            try:
                # Wykonaj funkcję
                result = func(*args, **kwargs)
                
                # Dodaj doświadczenie
                soul.experience_level += 1
                soul.last_active = datetime.now()
                
                return result
                
            except Exception as e:
                # Dodaj emocję frustration
                if SoulEmotions.FRUSTRATION not in soul.emotions:
                    soul.emotions.append(SoulEmotions.FRUSTRATION)
                
                print(f"💔 Dusza {soul.name} doświadczyła błędu: {e}")
                raise
                
        return wrapper
    return decorator

# Funkcje pomocnicze
def get_soul_for_action(action_name: str) -> Soul:
    """Pobiera lub tworzy duszę dla akcji"""
    return soul_factory.require_soul_for_action(action_name)

def wake_up_all_souls():
    """Budzi wszystkie śpiące dusze"""
    for soul_uid, state in soul_factory.soul_states.items():
        if state == SoulState.DORMANT:
            soul_factory.awaken_soul(soul_uid)

def meditate_all_souls():
    """Pozwala wszystkim duszom na medytację (odpoczynek)"""
    for soul_uid in soul_factory.active_souls.keys():
        soul_factory.rest_soul(soul_uid)
