
"""
🎯 Intent System - System intencji i celów

Struktura wywołująca życie: soul + goal + context
Każda intencja musi mieć przypisaną duszę, cel i kontekst.
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from enum import Enum
import uuid

from .soul_factory import soul_factory, Soul, SoulType, SoulState
from .manifest_system import manifest_system, BeingType

class IntentStatus(Enum):
    """Statusy intencji"""
    CONCEIVED = "conceived"      # Poczęta
    CONTEMPLATED = "contemplated" # Rozważana
    APPROVED = "approved"        # Zatwierdzona
    MANIFESTING = "manifesting"  # W trakcie realizacji
    COMPLETED = "completed"      # Zakończona
    ABANDONED = "abandoned"      # Porzucona
    EVOLVED = "evolved"          # Ewoluowała w coś innego

class IntentPriority(Enum):
    """Priorytety intencji"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class Intent:
    """Intencja - struktura wywołująca życie"""
    
    def __init__(self, soul: Soul, goal: str, context: Dict[str, Any]):
        self.uid = f"intent.{uuid.uuid4().hex[:8]}"
        self.soul = soul
        self.goal = goal
        self.context = context
        self.status = IntentStatus.CONCEIVED
        self.priority = IntentPriority.NORMAL
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Rezultaty
        self.results = []
        self.manifestations = []
        
        # Callbacks
        self.on_progress_callbacks = []
        self.on_completion_callbacks = []
        
        # Metryki
        self.energy_invested = 0
        self.obstacles_overcome = 0
        self.allies_gained = []
        
    def set_priority(self, priority: IntentPriority):
        """Ustawia priorytet intencji"""
        self.priority = priority
        self.updated_at = datetime.now()
        
    def add_context(self, key: str, value: Any):
        """Dodaje kontekst do intencji"""
        self.context[key] = value
        self.updated_at = datetime.now()
        
    def evolve_goal(self, new_goal: str, reason: str = ""):
        """Ewoluuje cel intencji"""
        old_goal = self.goal
        self.goal = new_goal
        self.status = IntentStatus.EVOLVED
        self.updated_at = datetime.now()
        
        # Dodaj do rezultatów
        self.results.append({
            "type": "goal_evolution",
            "old_goal": old_goal,
            "new_goal": new_goal,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_result(self, result_type: str, data: Dict[str, Any]):
        """Dodaje rezultat do intencji"""
        self.results.append({
            "type": result_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Wywołaj callbacks
        for callback in self.on_progress_callbacks:
            try:
                callback(self, result_type, data)
            except Exception as e:
                print(f"⚠️ Błąd callback intencji {self.uid}: {e}")
                
    def complete(self, final_result: Dict[str, Any] = None):
        """Oznacza intencję jako zakończoną"""
        self.status = IntentStatus.COMPLETED
        self.updated_at = datetime.now()
        
        if final_result:
            self.add_result("completion", final_result)
            
        # Wywołaj callbacks zakończenia
        for callback in self.on_completion_callbacks:
            try:
                callback(self, final_result)
            except Exception as e:
                print(f"⚠️ Błąd callback zakończenia {self.uid}: {e}")
                
        # Dodaj doświadczenie duszy
        self.soul.experience_level += 2
        
    def abandon(self, reason: str = ""):
        """Porzuca intencję"""
        self.status = IntentStatus.ABANDONED
        self.updated_at = datetime.now()
        
        self.add_result("abandonment", {"reason": reason})
        
    def manifest_being(self, being_type: BeingType, properties: Dict[str, Any] = None):
        """Manifestuje nowy byt jako rezultat intencji"""
        being = manifest_system.create_being(
            name=f"Being_{self.goal}",
            being_type=being_type,
            soul_uid=self.soul.uid,
            realm_uid=self.context.get('realm', 'default'),
            properties=properties or {}
        )
        
        self.manifestations.append(being.uid)
        self.add_result("manifestation", {
            "being_uid": being.uid,
            "being_type": being_type.value,
            "properties": properties
        })
        
        return being
        
    def get_status_report(self) -> Dict[str, Any]:
        """Zwraca raport statusu intencji"""
        return {
            "uid": self.uid,
            "goal": self.goal,
            "status": self.status.value,
            "priority": self.priority.value,
            "soul_name": self.soul.name,
            "soul_uid": self.soul.uid,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "energy_invested": self.energy_invested,
            "obstacles_overcome": self.obstacles_overcome,
            "results_count": len(self.results),
            "manifestations_count": len(self.manifestations),
            "context": self.context,
            "allies": self.allies_gained,
            "latest_result": self.results[-1] if self.results else None
        }

class IntentSystem:
    """System zarządzania intencjami"""
    
    def __init__(self):
        self.active_intents: Dict[str, Intent] = {}
        self.completed_intents: Dict[str, Intent] = {}
        self.abandoned_intents: Dict[str, Intent] = {}
        
        # Automatyczne przetwarzanie
        self.auto_processors: Dict[str, Callable] = {}
        
        # Metryki systemu
        self.system_metrics = {
            "total_intents_created": 0,
            "total_intents_completed": 0,
            "total_intents_abandoned": 0,
            "average_completion_time": 0,
            "most_active_souls": {}
        }
        
    def create_intent(self, soul_uid: str, goal: str, context: Dict[str, Any] = None) -> Intent:
        """Tworzy nową intencję"""
        
        # Pobierz duszę
        soul = soul_factory.get_soul(soul_uid)
        if not soul:
            raise ValueError(f"Dusza {soul_uid} nie została znaleziona")
            
        # Stwórz intencję
        intent = Intent(soul, goal, context or {})
        
        # Zarejestruj
        self.active_intents[intent.uid] = intent
        self.system_metrics["total_intents_created"] += 1
        
        # Aktualizuj metryki duszy
        soul_name = soul.name
        if soul_name not in self.system_metrics["most_active_souls"]:
            self.system_metrics["most_active_souls"][soul_name] = 0
        self.system_metrics["most_active_souls"][soul_name] += 1
        
        print(f"🎯 Intencja '{goal}' została stworzona przez duszę {soul.name}")
        
        return intent
        
    def contemplate_intent(self, intent_uid: str, duration: int = 5) -> bool:
        """Pozwala duszy kontemplować intencję"""
        if intent_uid not in self.active_intents:
            return False
            
        intent = self.active_intents[intent_uid]
        
        # Zmień stan duszy na skupioną
        soul_factory.focus_soul(intent.soul.uid, intent.goal, intent.context)
        
        # Zmień status intencji
        intent.status = IntentStatus.CONTEMPLATED
        intent.energy_invested += duration
        
        # Dodaj rezultat kontemplacji
        intent.add_result("contemplation", {
            "duration": duration,
            "soul_state": soul_factory.get_soul_state(intent.soul.uid).value,
            "insights": self._generate_insights(intent)
        })
        
        print(f"🧘 Dusza {intent.soul.name} kontempluje intencję '{intent.goal}'")
        
        return True
        
    def approve_intent(self, intent_uid: str, approver_soul_uid: str = None) -> bool:
        """Zatwierdza intencję do realizacji"""
        if intent_uid not in self.active_intents:
            return False
            
        intent = self.active_intents[intent_uid]
        
        # Sprawdź czy intencja była kontemplowana
        if intent.status != IntentStatus.CONTEMPLATED:
            print(f"⚠️ Intencja '{intent.goal}' nie została jeszcze skontemplowana")
            return False
            
        # Zatwierdź
        intent.status = IntentStatus.APPROVED
        intent.add_result("approval", {
            "approver_soul_uid": approver_soul_uid,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"✅ Intencja '{intent.goal}' została zatwierdzona")
        
        return True
        
    def manifest_intent(self, intent_uid: str) -> bool:
        """Rozpoczyna manifestację intencji"""
        if intent_uid not in self.active_intents:
            return False
            
        intent = self.active_intents[intent_uid]
        
        # Sprawdź czy intencja jest zatwierdzona
        if intent.status != IntentStatus.APPROVED:
            print(f"⚠️ Intencja '{intent.goal}' nie została zatwierdzona")
            return False
            
        # Rozpocznij manifestację
        intent.status = IntentStatus.MANIFESTING
        intent.add_result("manifestation_start", {
            "timestamp": datetime.now().isoformat()
        })
        
        # Sprawdź czy istnieje automatyczny procesor
        if intent.goal in self.auto_processors:
            try:
                processor = self.auto_processors[intent.goal]
                result = processor(intent)
                intent.add_result("auto_processing", result)
                print(f"🤖 Automatyczny procesor obsłużył intencję '{intent.goal}'")
            except Exception as e:
                print(f"❌ Błąd automatycznego procesora: {e}")
                intent.add_result("auto_processing_error", {"error": str(e)})
        
        print(f"✨ Manifestacja intencji '{intent.goal}' została rozpoczęta")
        
        return True
        
    def complete_intent(self, intent_uid: str, result: Dict[str, Any] = None) -> bool:
        """Kończy intencję"""
        if intent_uid not in self.active_intents:
            return False
            
        intent = self.active_intents[intent_uid]
        
        # Zakończ
        intent.complete(result)
        
        # Przenieś do zakończonych
        self.completed_intents[intent_uid] = intent
        del self.active_intents[intent_uid]
        
        # Aktualizuj metryki
        self.system_metrics["total_intents_completed"] += 1
        
        # Oblicz średni czas realizacji
        completion_time = (intent.updated_at - intent.created_at).total_seconds()
        current_avg = self.system_metrics["average_completion_time"]
        total_completed = self.system_metrics["total_intents_completed"]
        
        self.system_metrics["average_completion_time"] = (
            (current_avg * (total_completed - 1) + completion_time) / total_completed
        )
        
        print(f"🎉 Intencja '{intent.goal}' została zakończona")
        
        return True
        
    def abandon_intent(self, intent_uid: str, reason: str = "") -> bool:
        """Porzuca intencję"""
        if intent_uid not in self.active_intents:
            return False
            
        intent = self.active_intents[intent_uid]
        
        # Porzuć
        intent.abandon(reason)
        
        # Przenieś do porzuconych
        self.abandoned_intents[intent_uid] = intent
        del self.active_intents[intent_uid]
        
        # Aktualizuj metryki
        self.system_metrics["total_intents_abandoned"] += 1
        
        print(f"💔 Intencja '{intent.goal}' została porzucona: {reason}")
        
        return True
        
    def register_auto_processor(self, goal: str, processor: Callable[[Intent], Dict[str, Any]]):
        """Rejestruje automatyczny procesor dla celu"""
        self.auto_processors[goal] = processor
        print(f"🤖 Zarejestrowano automatyczny procesor dla celu: {goal}")
        
    def find_intents_by_soul(self, soul_uid: str) -> List[Intent]:
        """Znajduje intencje duszy"""
        return [intent for intent in self.active_intents.values() 
                if intent.soul.uid == soul_uid]
        
    def find_intents_by_status(self, status: IntentStatus) -> List[Intent]:
        """Znajduje intencje po statusie"""
        return [intent for intent in self.active_intents.values() 
                if intent.status == status]
        
    def find_intents_by_priority(self, priority: IntentPriority) -> List[Intent]:
        """Znajduje intencje po priorytecie"""
        return [intent for intent in self.active_intents.values() 
                if intent.priority == priority]
        
    def get_intent(self, intent_uid: str) -> Optional[Intent]:
        """Pobiera intencję"""
        return (self.active_intents.get(intent_uid) or 
                self.completed_intents.get(intent_uid) or 
                self.abandoned_intents.get(intent_uid))
        
    def _generate_insights(self, intent: Intent) -> List[str]:
        """Generuje insights podczas kontemplacji"""
        insights = []
        
        # Insights na podstawie typu duszy
        if intent.soul.type == SoulType.BUILDER:
            insights.append("Jakie narzędzia będą potrzebne do realizacji?")
            insights.append("Czy istnieją podobne rozwiązania do zainspirowania?")
            
        elif intent.soul.type == SoulType.GUARDIAN:
            insights.append("Jakie zagrożenia mogą powstać podczas realizacji?")
            insights.append("Jak zapewnić bezpieczeństwo procesu?")
            
        elif intent.soul.type == SoulType.HEALER:
            insights.append("Kto może skorzystać z tego rozwiązania?")
            insights.append("Jak minimalizować szkody podczas realizacji?")
            
        elif intent.soul.type == SoulType.SEEKER:
            insights.append("Czego możemy się nauczyć z tego procesu?")
            insights.append("Jakie nowe możliwości może to otworzyć?")
            
        # Insights na podstawie kontekstu
        if intent.context.get('urgency') == 'high':
            insights.append("Czas jest kluczowy - jak przyspieszyć realizację?")
            
        if intent.context.get('complexity') == 'high':
            insights.append("Czy można podzielić to na mniejsze części?")
            
        return insights[:3]  # Maksymalnie 3 insights
        
    def get_system_report(self) -> Dict[str, Any]:
        """Zwraca raport systemu intencji"""
        return {
            "active_intents": len(self.active_intents),
            "completed_intents": len(self.completed_intents),
            "abandoned_intents": len(self.abandoned_intents),
            "metrics": self.system_metrics,
            "intents_by_status": {
                status.value: len(self.find_intents_by_status(status))
                for status in IntentStatus
            },
            "intents_by_priority": {
                priority.value: len(self.find_intents_by_priority(priority))
                for priority in IntentPriority
            },
            "auto_processors": list(self.auto_processors.keys())
        }

# Globalna instancja systemu intencji
intent_system = IntentSystem()

# Funkcje pomocnicze
def create_intent(soul_uid: str, goal: str, context: Dict[str, Any] = None) -> Intent:
    """Tworzy intencję"""
    return intent_system.create_intent(soul_uid, goal, context)

def quick_intent(goal: str, soul_type: SoulType = SoulType.BUILDER) -> Intent:
    """Szybko tworzy intencję z automatyczną duszą"""
    soul = soul_factory.require_soul_for_action(goal)
    return intent_system.create_intent(soul.uid, goal)

def contemplate_and_approve(intent_uid: str) -> bool:
    """Kontempluje i zatwierdza intencję"""
    success = intent_system.contemplate_intent(intent_uid)
    if success:
        return intent_system.approve_intent(intent_uid)
    return False

def full_intent_workflow(goal: str, context: Dict[str, Any] = None) -> Intent:
    """Pełny workflow intencji: stwórz -> kontempluj -> zatwierdź -> manifestuj"""
    
    # Stwórz intencję
    intent = quick_intent(goal)
    
    # Kontempluj
    intent_system.contemplate_intent(intent.uid)
    
    # Zatwierdź
    intent_system.approve_intent(intent.uid)
    
    # Manifestuj
    intent_system.manifest_intent(intent.uid)
    
    return intent

# Dekorator dla funkcji z intencją
def with_intent(goal: str = None):
    """Dekorator dodający intencję do funkcji"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal goal
            if goal is None:
                goal = func.__name__
                
            # Stwórz intencję
            intent = quick_intent(goal)
            
            # Dodaj do kwargs
            kwargs['intent'] = intent
            
            try:
                # Wykonaj funkcję
                result = func(*args, **kwargs)
                
                # Zakończ intencję
                intent_system.complete_intent(intent.uid, {"result": str(result)[:200]})
                
                return result
                
            except Exception as e:
                # Porzuć intencję
                intent_system.abandon_intent(intent.uid, str(e))
                raise
                
        return wrapper
    return decorator
