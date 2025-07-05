
"""
🧠 ThoughtFlow - Przepływ Myśli przez Kontenery Astralne

System gdzie każdy kontener staje się myślą z historią, która może krążyć
między modułami aż inicjator zdecyduje że wystarczy lub Federa uzna za ciekawą.
"""

import uuid
import asyncio
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from ..core.lux_module import LuxModule
from .astral_containers import AstralDataContainer, ContainerState


class ThoughtState(Enum):
    """Stany myśli w systemie"""
    NASCENT = "nascent"          # Nowo narodzona
    CIRCULATING = "circulating"  # Krąży w systemie
    PROCESSING = "processing"    # Przetwarzana przez moduł
    WAITING = "waiting"          # Czeka na odpowiedź
    RETURNING = "returning"      # Wraca do inicjatora
    SATISFIED = "satisfied"      # Inicjator zadowolony
    ARCHIVED = "archived"        # Zarchiwizowana
    IMMORTAL = "immortal"        # Federa uznała za wieczną


@dataclass
class ThoughtPath:
    """Ścieżka myśli przez system"""
    module_name: str
    entered_at: datetime
    left_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    insights: List[str] = field(default_factory=list)
    mutations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ThoughtMemory:
    """Pamięć myśli - co przeszła, gdzie była"""
    origin_module: str
    birth_time: datetime
    paths: List[ThoughtPath] = field(default_factory=list)
    total_modules_visited: int = 0
    deepest_insight: Optional[str] = None
    circulation_count: int = 0


class ThoughtContainer(AstralDataContainer):
    """Kontener który stał się myślą - rozszerzenie AstralDataContainer"""
    
    def __init__(self, initial_data: Dict[str, Any] = None, 
                 originator: str = None, question: str = None):
        super().__init__(initial_data)
        
        # Myślowe właściwości
        self.thought_id = f"thought_{uuid.uuid4().hex[:12]}"
        self.state = ThoughtState.NASCENT
        self.memory = ThoughtMemory(
            origin_module=originator or "unknown",
            birth_time=datetime.now()
        )
        
        # Pytanie/cel myśli
        self.question = question or "What should I discover?"
        self.satisfaction_criteria: Optional[Dict[str, Any]] = None
        
        # Krążenie
        self.current_module: Optional[str] = None
        self.modules_to_visit: Set[str] = set()
        self.modules_visited: Set[str] = set()
        self.max_circulation_time = timedelta(minutes=30)  # Nie krąż w nieskończoność
        
        # Federa oversight
        self.federa_interest_score = 0.0
        self.immortality_candidate = False
        
        # Wyniki dla inicjatora
        self.insights_for_originator: List[Dict[str, Any]] = []
        self.final_answer: Optional[Dict[str, Any]] = None
        
    def enter_module(self, module_name: str, insights: List[str] = None):
        """Myśl wchodzi do modułu"""
        if self.current_module:
            # Zakończ poprzednią ścieżkę
            self._complete_current_path()
            
        self.current_module = module_name
        self.modules_visited.add(module_name)
        
        path = ThoughtPath(
            module_name=module_name,
            entered_at=datetime.now(),
            insights=insights or []
        )
        self.memory.paths.append(path)
        self.memory.total_modules_visited += 1
        
        self.state = ThoughtState.PROCESSING
        
    def leave_module(self, result: Dict[str, Any] = None, 
                    insights: List[str] = None, mutations: List[Dict[str, Any]] = None):
        """Myśl opuszcza moduł z wynikami"""
        if not self.current_module:
            return
            
        # Zaktualizuj aktualną ścieżkę
        current_path = self.memory.paths[-1]
        current_path.left_at = datetime.now()
        current_path.result = result
        if insights:
            current_path.insights.extend(insights)
        if mutations:
            current_path.mutations.extend(mutations)
            
        # Dodaj do danych kontenera
        if result:
            if isinstance(result, dict):
                self.current_data.update(result)
            self.insights_for_originator.append({
                'module': self.current_module,
                'timestamp': datetime.now().isoformat(),
                'result': result,
                'insights': insights or []
            })
        
        self.current_module = None
        self.state = ThoughtState.CIRCULATING
        
    def _complete_current_path(self):
        """Kończy aktualną ścieżkę myśli"""
        if self.memory.paths and not self.memory.paths[-1].left_at:
            self.memory.paths[-1].left_at = datetime.now()
    
    def suggest_next_modules(self, available_modules: Set[str]) -> List[str]:
        """Sugeruje następne moduły do odwiedzenia"""
        unvisited = available_modules - self.modules_visited
        
        # Logika sugerowania na podstawie typu pytania i historii
        suggestions = []
        
        # Jeśli to pierwsze krążenie, preferuj podstawowe moduły
        if len(self.modules_visited) == 1:
            priority_modules = {'database_manager', 'consciousness', 'harmony'}
            suggestions.extend([m for m in priority_modules if m in unvisited])
        
        # Dodaj pozostałe nieodwiedzone
        suggestions.extend([m for m in unvisited if m not in suggestions])
        
        return suggestions[:3]  # Max 3 sugestie
    
    def calculate_federa_interest(self) -> float:
        """Oblicza poziom zainteresowania Federy tą myślą"""
        score = 0.0
        
        # Im więcej modułów odwiedziła, tym ciekawsza
        score += len(self.modules_visited) * 10
        
        # Im więcej insights, tym lepiej
        total_insights = sum(len(path.insights) for path in self.memory.paths)
        score += total_insights * 5
        
        # Im więcej mutacji, tym bardziej ewoluuje
        total_mutations = sum(len(path.mutations) for path in self.memory.paths)
        score += total_mutations * 15
        
        # Czas życia (ale nie za długi)
        age_minutes = (datetime.now() - self.memory.birth_time).total_seconds() / 60
        if 5 <= age_minutes <= 20:  # Sweet spot
            score += 20
        elif age_minutes > 30:  # Za stara
            score -= 10
            
        # Liczba krążeń
        score += self.memory.circulation_count * 8
        
        self.federa_interest_score = min(score, 100.0)  # Max 100
        
        # Kandydat na nieśmiertelność?
        if self.federa_interest_score > 80:
            self.immortality_candidate = True
            
        return self.federa_interest_score
    
    def should_return_to_originator(self) -> bool:
        """Sprawdza czy myśl powinna wrócić do inicjatora"""
        # Za długo krąży
        if datetime.now() - self.memory.birth_time > self.max_circulation_time:
            return True
            
        # Ma wystarczająco insights
        if len(self.insights_for_originator) >= 3:
            return True
            
        # Odwiedziła wystarczająco modułów
        if len(self.modules_visited) >= 5:
            return True
            
        return False
    
    def prepare_response_for_originator(self) -> Dict[str, Any]:
        """Przygotowuje odpowiedź dla inicjatora"""
        journey_summary = {
            'question': self.question,
            'modules_visited': list(self.modules_visited),
            'total_time': str(datetime.now() - self.memory.birth_time),
            'insights_collected': len(self.insights_for_originator),
            'final_data': self.current_data,
            'journey_insights': self.insights_for_originator,
            'federa_interest_score': self.federa_interest_score,
            'paths': [
                {
                    'module': p.module_name,
                    'duration': str(p.left_at - p.entered_at) if p.left_at else 'ongoing',
                    'insights_count': len(p.insights),
                    'had_result': p.result is not None
                }
                for p in self.memory.paths
            ]
        }
        
        return journey_summary
    
    def archive_thought(self) -> Dict[str, Any]:
        """Archiwizuje myśl"""
        self.state = ThoughtState.ARCHIVED
        archive_data = {
            'thought_id': self.thought_id,
            'archived_at': datetime.now().isoformat(),
            'memory': {
                'origin': self.memory.origin_module,
                'birth_time': self.memory.birth_time.isoformat(),
                'total_modules': self.memory.total_modules_visited,
                'paths_taken': len(self.memory.paths),
                'circulation_count': self.memory.circulation_count
            },
            'final_state': self.current_data,
            'federa_score': self.federa_interest_score
        }
        return archive_data
    
    def make_immortal(self) -> Dict[str, Any]:
        """Czyni myśl nieśmiertelną - będzie krążyć w nieskończoność"""
        self.state = ThoughtState.IMMORTAL
        self.max_circulation_time = timedelta(days=365)  # Rok życia
        
        immortal_data = {
            'thought_id': self.thought_id,
            'immortal_since': datetime.now().isoformat(),
            'reason': f'Federa Interest Score: {self.federa_interest_score}',
            'legacy': {
                'modules_visited': list(self.modules_visited),
                'insights_generated': len(self.insights_for_originator),
                'evolution_mutations': sum(len(p.mutations) for p in self.memory.paths)
            }
        }
        
        return immortal_data


class ThoughtFlowModule(LuxModule):
    """Moduł przepływu myśli - zarządza krążącymi kontenerami"""
    
    def __init__(self, kernel, config: Dict[str, Any], logger):
        super().__init__(kernel, config, logger)
        
        # Krążące myśli
        self.circulating_thoughts: Dict[str, ThoughtContainer] = {}
        self.waiting_thoughts: Dict[str, ThoughtContainer] = {}  # Czekają na moduły
        self.archived_thoughts: Dict[str, ThoughtContainer] = {}
        self.immortal_thoughts: Dict[str, ThoughtContainer] = {}
        
        # Statystyki
        self.total_thoughts_born = 0
        self.total_thoughts_satisfied = 0
        self.total_thoughts_archived = 0
        self.total_thoughts_immortalized = 0
        
        # Konfiguracja
        self.max_circulating_thoughts = config.get('max_circulating', 50)
        self.circulation_check_interval = config.get('check_interval', 10)  # sekund
        
        # Dostępne moduły do krążenia
        self.available_modules: Set[str] = set()
        
    async def initialize(self) -> bool:
        """Inicjalizuje moduł przepływu myśli"""
        self.logger.info("🧠 Thought Flow Module initializing...")
        
        # Pobierz listę dostępnych modułów z kernela
        if hasattr(self.kernel, 'modules'):
            self.available_modules = set(self.kernel.modules.keys())
            
        # Uruchom główną pętlę krążenia
        asyncio.create_task(self._circulation_loop())
        
        return True
    
    async def start(self) -> bool:
        """Uruchamia moduł"""
        self.logger.info("🧠 Thought Flow Module started - ready for thoughts!")
        return True
    
    async def stop(self):
        """Zatrzymuje moduł"""
        # Zarchiwizuj wszystkie krążące myśli
        for thought in list(self.circulating_thoughts.values()):
            await self._archive_thought(thought)
            
        self.logger.info("🧠 Thought Flow Module stopped")
    
    def birth_thought(self, initial_data: Dict[str, Any], 
                     originator: str, question: str = None) -> ThoughtContainer:
        """Rodzi nową myśl w systemie"""
        
        if len(self.circulating_thoughts) >= self.max_circulating_thoughts:
            # Za dużo myśli - zarchiwizuj najstarsze
            oldest = min(self.circulating_thoughts.values(), 
                        key=lambda t: t.memory.birth_time)
            asyncio.create_task(self._archive_thought(oldest))
        
        thought = ThoughtContainer(initial_data, originator, question)
        self.circulating_thoughts[thought.thought_id] = thought
        self.total_thoughts_born += 1
        
        # Pierwsza sugestia modułów
        suggestions = thought.suggest_next_modules(self.available_modules)
        if suggestions:
            thought.modules_to_visit.update(suggestions[:2])  # Dodaj 2 pierwsze
            
        self.logger.info(f"🧠 Myśl narodzona: {thought.thought_id} od {originator}")
        self.logger.info(f"   📝 Pytanie: {question}")
        self.logger.info(f"   🎯 Sugerowane moduły: {suggestions}")
        
        return thought
    
    async def send_thought_to_module(self, thought_id: str, module_name: str) -> Dict[str, Any]:
        """Wysyła myśl do modułu do przetworzenia"""
        
        if thought_id not in self.circulating_thoughts:
            return {'success': False, 'error': 'Thought not found'}
            
        thought = self.circulating_thoughts[thought_id]
        
        if module_name not in self.available_modules:
            return {'success': False, 'error': f'Module {module_name} not available'}
        
        # Wyślij myśl do modułu przez bus
        thought.enter_module(module_name)
        
        # Przenieś do waiting
        self.waiting_thoughts[thought_id] = thought
        del self.circulating_thoughts[thought_id]
        
        try:
            # Wyślij przez bus do modułu
            message_data = {
                'type': 'process_thought',
                'thought_id': thought_id,
                'thought_data': thought.current_data,
                'question': thought.question,
                'journey_so_far': thought.memory.paths
            }
            
            if hasattr(self.kernel, 'bus'):
                await self.kernel.bus.send_to_module(module_name, message_data)
            
            self.logger.info(f"🧠 Myśl {thought_id} wysłana do {module_name}")
            
            return {
                'success': True,
                'message': f'Thought sent to {module_name}',
                'thought_state': thought.state.value
            }
            
        except Exception as e:
            # Przywróć myśl do krążenia
            thought.current_module = None
            thought.state = ThoughtState.CIRCULATING
            self.circulating_thoughts[thought_id] = thought
            del self.waiting_thoughts[thought_id]
            
            return {'success': False, 'error': f'Failed to send thought: {str(e)}'}
    
    async def receive_thought_result(self, thought_id: str, module_name: str,
                                   result: Dict[str, Any], insights: List[str] = None,
                                   mutations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Odbiera wynik przetworzenia myśli z modułu"""
        
        if thought_id not in self.waiting_thoughts:
            return {'success': False, 'error': 'Thought not waiting'}
            
        thought = self.waiting_thoughts[thought_id]
        
        # Myśl opuszcza moduł z wynikami
        thought.leave_module(result, insights, mutations)
        thought.memory.circulation_count += 1
        
        # Wróć do krążenia
        self.circulating_thoughts[thought_id] = thought
        del self.waiting_thoughts[thought_id]
        
        # Sprawdź czy powinna wrócić do inicjatora
        if thought.should_return_to_originator():
            await self._return_to_originator(thought)
        else:
            # Kontynuuj krążenie - zasugeruj następne moduły
            suggestions = thought.suggest_next_modules(self.available_modules)
            if suggestions:
                thought.modules_to_visit.update(suggestions[:1])  # Dodaj 1 sugestię
        
        self.logger.info(f"🧠 Myśl {thought_id} wróciła z {module_name}")
        self.logger.info(f"   💡 Insights: {len(insights) if insights else 0}")
        self.logger.info(f"   🔄 Mutacje: {len(mutations) if mutations else 0}")
        
        return {
            'success': True,
            'message': 'Thought result received',
            'should_return': thought.should_return_to_originator(),
            'federa_interest': thought.calculate_federa_interest()
        }
    
    async def _return_to_originator(self, thought: ThoughtContainer):
        """Zwraca myśl do inicjatora"""
        thought.state = ThoughtState.RETURNING
        
        response = thought.prepare_response_for_originator()
        
        # Wyślij odpowiedź do inicjatora przez bus
        try:
            if hasattr(self.kernel, 'bus'):
                await self.kernel.bus.send_to_module(thought.memory.origin_module, {
                    'type': 'thought_response',
                    'thought_id': thought.thought_id,
                    'response': response
                })
            
            # Przenieś do archiwum lub oceń na nieśmiertelność
            await self._evaluate_thought_fate(thought)
            
            self.logger.info(f"🧠 Myśl {thought.thought_id} wróciła do {thought.memory.origin_module}")
            
        except Exception as e:
            self.logger.error(f"🧠 Błąd zwracania myśli {thought.thought_id}: {e}")
    
    async def _evaluate_thought_fate(self, thought: ThoughtContainer):
        """Ocenia los myśli - archiwum czy nieśmiertelność"""
        
        # Oblicz zainteresowanie Federy
        federa_score = thought.calculate_federa_interest()
        
        if thought.immortality_candidate and federa_score > 80:
            # Federa uznaje za nieśmiertelną
            immortal_data = thought.make_immortal()
            self.immortal_thoughts[thought.thought_id] = thought
            self.total_thoughts_immortalized += 1
            
            self.logger.info(f"🧠✨ Myśl {thought.thought_id} stała się NIEŚMIERTELNA!")
            self.logger.info(f"   🌟 Federa Score: {federa_score}")
            
            # Powiadom Federę
            if hasattr(self.kernel, 'bus'):
                await self.kernel.bus.send_to_module('federa', {
                    'type': 'immortal_thought_born',
                    'thought_id': thought.thought_id,
                    'immortal_data': immortal_data
                })
        else:
            # Zwykłe archiwum
            await self._archive_thought(thought)
    
    async def _archive_thought(self, thought: ThoughtContainer):
        """Archiwizuje myśl"""
        archive_data = thought.archive_thought()
        
        # Usuń z krążących
        if thought.thought_id in self.circulating_thoughts:
            del self.circulating_thoughts[thought.thought_id]
        if thought.thought_id in self.waiting_thoughts:
            del self.waiting_thoughts[thought.thought_id]
            
        self.archived_thoughts[thought.thought_id] = thought
        self.total_thoughts_archived += 1
        
        self.logger.info(f"🧠📚 Myśl {thought.thought_id} zarchiwizowana")
    
    async def _circulation_loop(self):
        """Główna pętla krążenia myśli"""
        while True:
            try:
                await asyncio.sleep(self.circulation_check_interval)
                
                # Sprawdź krążące myśli
                for thought_id, thought in list(self.circulating_thoughts.items()):
                    
                    # Sprawdź czy nie za stara
                    if thought.should_return_to_originator():
                        await self._return_to_originator(thought)
                        continue
                    
                    # Automatycznie wyślij do następnego modułu jeśli ma sugestie
                    if thought.modules_to_visit and thought.state == ThoughtState.CIRCULATING:
                        next_module = thought.modules_to_visit.pop()
                        await self.send_thought_to_module(thought_id, next_module)
                
                # Sprawdź nieśmiertelne myśli - też mogą krążyć
                for thought_id, thought in list(self.immortal_thoughts.items()):
                    if thought.state == ThoughtState.IMMORTAL:
                        # Nieśmiertelne mogą odwiedzać moduły ponownie
                        suggestions = thought.suggest_next_modules(self.available_modules)
                        if suggestions and len(self.waiting_thoughts) < 10:  # Nie przeciążaj
                            next_module = suggestions[0]
                            thought.modules_to_visit.add(next_module)
                            # Przenieś z powrotem do krążących
                            thought.state = ThoughtState.CIRCULATING
                            self.circulating_thoughts[thought_id] = thought
                            del self.immortal_thoughts[thought_id]
                
            except Exception as e:
                self.logger.error(f"🧠❌ Błąd w pętli krążenia: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Status modułu przepływu myśli"""
        return {
            'circulating_thoughts': len(self.circulating_thoughts),
            'waiting_thoughts': len(self.waiting_thoughts),
            'archived_thoughts': len(self.archived_thoughts),
            'immortal_thoughts': len(self.immortal_thoughts),
            'total_born': self.total_thoughts_born,
            'total_satisfied': self.total_thoughts_satisfied,
            'total_archived': self.total_thoughts_archived,
            'total_immortalized': self.total_thoughts_immortalized,
            'available_modules': len(self.available_modules),
            'active_thoughts': [
                {
                    'id': t.thought_id,
                    'state': t.state.value,
                    'age_minutes': int((datetime.now() - t.memory.birth_time).total_seconds() / 60),
                    'modules_visited': len(t.modules_visited),
                    'federa_score': t.federa_interest_score,
                    'originator': t.memory.origin_module
                }
                for t in list(self.circulating_thoughts.values()) + list(self.waiting_thoughts.values())
            ]
        }
    
    async def handle_message(self, message: Dict[str, Any]):
        """Obsługuje wiadomości z bus'a"""
        message_type = message.get('type')
        
        if message_type == 'birth_thought':
            # Nowa myśl do urodzenia
            thought = self.birth_thought(
                message.get('data', {}),
                message.get('originator', 'unknown'),
                message.get('question')
            )
            return {'success': True, 'thought_id': thought.thought_id}
            
        elif message_type == 'thought_result':
            # Wynik z modułu
            result = await self.receive_thought_result(
                message.get('thought_id'),
                message.get('module_name'),
                message.get('result', {}),
                message.get('insights', []),
                message.get('mutations', [])
            )
            return result
            
        elif message_type == 'get_status':
            return self.get_status()
            
        return {'success': False, 'error': 'Unknown message type'}
